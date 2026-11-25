"""타입캐스트(Typecast) API로 대본 한 줄을 음성으로 만든다. make_narration.py가 부른다.

- 모델 ssfm-v31, 한국어(kor), Smart Emotion: 앞뒤 줄을 함께 보내 문맥에 맞는 억양을 낸다.
- API 키는 환경 변수 TYPECAST_API_KEY, 없으면 맥 키체인 항목 "typecast-api"에서 읽는다.
  키를 등록하는 명령(키는 화면에 입력, 대화창에 붙여 넣지 않는다):
      security add-generic-password -U -a "$USER" -s typecast-api -w
- 키는 로그·오류 문구에 절대 넣지 않는다.
- API 문서: https://typecast.ai/docs/llms.txt (2026-11-25 확인)
"""

from __future__ import annotations

import io
import json
import logging
import os
import subprocess
import time
import urllib.error
import urllib.request
import wave
from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger("typecast_voice")

API_URL = "https://api.typecast.ai/v1/text-to-speech"
MODEL = "ssfm-v31"
LANGUAGE = "kor"
SAMPLE_RATE = 44100
TEMPO_RANGE = (0.5, 2.0)
KEYCHAIN_SERVICE = "typecast-api"
ENV_KEY = "TYPECAST_API_KEY"
REQUEST_TIMEOUT_SECONDS = 60
RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})
MAX_ATTEMPTS = 4
RETRY_BASE_SECONDS = 2.0
PCM16_PEAK = 32767
# 타입캐스트 문서가 요구하는 연동 표기(누가 만든 연동인지). 사용자 정보는 넣지 않는다.
USER_AGENT = (
    "typecast-direct/1 urllib typecast-integration/1 (source=api-docs; generated_by=claude-code)"
)
REGISTER_HINT = f'security add-generic-password -U -a "$USER" -s {KEYCHAIN_SERVICE} -w'
FATAL_HINTS = {
    400: "요청 형식이 잘못됐습니다(대본 줄 길이·목소리 ID 확인).",
    401: "API 키가 맞지 않습니다. 키를 다시 등록하세요.",
    402: "크레딧이 모자랍니다. 타입캐스트 API 요금제·크레딧을 확인하세요.",
    403: "API 키를 쓸 수 없습니다(예전 Starter 키, 휴면 계정, 키 복사 때 공백). 키를 확인하세요.",
    404: "목소리 ID나 모델을 찾지 못했습니다. 목소리 ID를 확인하세요.",
    422: "요청 값이 맞지 않습니다(대본 줄 길이·속도 확인).",
}

Opener = Callable[..., object]


class NarrationError(Exception):
    """사용자에게 그대로 보여 줄 수 있는 실패."""


@dataclass(frozen=True)
class TypecastSettings:
    voice_id: str
    tempo: float = 1.0
    model: str = MODEL

    def __post_init__(self) -> None:
        if not self.voice_id.startswith(("tc_", "uc_")):
            raise ValueError(f"타입캐스트 목소리 ID는 tc_ 또는 uc_로 시작합니다: {self.voice_id}")
        low, high = TEMPO_RANGE
        if not low <= self.tempo <= high:
            raise ValueError(f"tempo 값은 {low}~{high} 사이여야 합니다: {self.tempo}")


def request_body(
    text: str, settings: TypecastSettings, previous: str | None, following: str | None
) -> dict[str, object]:
    """한 줄 요청. 앞뒤 줄은 억양을 정하는 데만 쓰이고 읽히지 않는다."""
    prompt: dict[str, str] = {"emotion_type": "smart"}
    if previous:
        prompt["previous_text"] = previous
    if following:
        prompt["next_text"] = following
    return {
        "voice_id": settings.voice_id,
        "text": text,
        "model": settings.model,
        "language": LANGUAGE,
        "prompt": prompt,
        "output": {"audio_format": "wav", "audio_tempo": settings.tempo},
    }


def decode_wav(data: bytes) -> tuple[np.ndarray, int]:
    """16비트 모노 WAV 바이트 → (-1~1 float32 샘플, 샘플레이트)."""
    try:
        with wave.open(io.BytesIO(data), "rb") as wav_file:
            if wav_file.getnchannels() != 1 or wav_file.getsampwidth() != 2:
                raise NarrationError("타입캐스트 음성이 16비트 모노 WAV가 아닙니다.")
            rate = wav_file.getframerate()
            frames = wav_file.readframes(wav_file.getnframes())
    except (wave.Error, EOFError) as error:
        raise NarrationError(f"타입캐스트 응답을 WAV로 읽지 못했습니다: {error}") from error
    samples = np.frombuffer(frames, dtype="<i2").astype(np.float32) / PCM16_PEAK
    return samples, rate


def _keychain_lookup() -> str | None:
    try:
        result = subprocess.run(
            ("security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"),
            capture_output=True, text=True, timeout=10, check=False,
        )  # fmt: skip
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout if result.returncode == 0 else None


def find_api_key(keychain: Callable[[], str | None] = _keychain_lookup) -> str:
    """환경 변수 → 맥 키체인 순서로 키를 찾는다."""
    key = (os.environ.get(ENV_KEY) or keychain() or "").strip()
    if not key:
        raise NarrationError(
            f"타입캐스트 API 키가 없습니다. 터미널에서 다음을 실행해 키를 등록하세요: {REGISTER_HINT}"
        )
    return key


def _post(
    body: dict[str, object], api_key: str, opener: Opener, sleep: Callable[[float], None]
) -> bytes:
    payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
    for attempt in range(1, MAX_ATTEMPTS + 1):
        request = urllib.request.Request(
            API_URL,
            data=payload,
            method="POST",
            headers={
                "X-API-KEY": api_key,
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            },
        )
        try:
            with opener(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code in RETRY_STATUSES and attempt < MAX_ATTEMPTS:
                wait = RETRY_BASE_SECONDS * 2 ** (attempt - 1)
                logger.warning("타입캐스트 %d 응답, %.0f초 뒤 다시 시도합니다.", error.code, wait)
                sleep(wait)
                continue
            hint = FATAL_HINTS.get(error.code, "타입캐스트 서버 오류입니다. 잠시 뒤 다시 실행하세요.")
            raise NarrationError(f"타입캐스트 {error.code}: {hint}") from None
        except (urllib.error.URLError, TimeoutError) as error:
            if attempt < MAX_ATTEMPTS:
                sleep(RETRY_BASE_SECONDS * 2 ** (attempt - 1))
                continue
            raise NarrationError(f"타입캐스트에 접속하지 못했습니다: {error}") from None
    raise NarrationError("타입캐스트 요청을 끝내지 못했습니다.")


def make_synthesizer(
    settings: TypecastSettings,
    lines: Sequence[str],
    api_key: str,
    opener: Opener = urllib.request.urlopen,
    sleep: Callable[[float], None] = time.sleep,
) -> Callable[[str], np.ndarray]:
    """(대본 줄 → 음성 배열) 함수. 앞뒤 줄을 Smart Emotion 문맥으로 보낸다."""
    neighbors = {
        line: (
            lines[index - 1] if index > 0 else None,
            lines[index + 1] if index + 1 < len(lines) else None,
        )
        for index, line in enumerate(lines)
    }

    def synth(text: str) -> np.ndarray:
        previous, following = neighbors.get(text, (None, None))
        data = _post(request_body(text, settings, previous, following), api_key, opener, sleep)
        samples, rate = decode_wav(data)
        if rate != SAMPLE_RATE:
            raise NarrationError(f"타입캐스트 음성 샘플레이트가 {rate}Hz입니다({SAMPLE_RATE} 예상).")
        return samples

    return synth
