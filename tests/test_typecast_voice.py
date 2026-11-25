"""typecast_voice.py 테스트. 실제 타입캐스트에 접속하지 않는다(가짜 응답을 넣는다)."""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import types
import urllib.error
import wave
from pathlib import Path

import numpy as np
import pytest

TEMPLATES = Path(__file__).resolve().parents[1] / ".claude/skills/reels/templates"


def _load(name: str) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, TEMPLATES / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


tv = _load("typecast_voice")

pytestmark = pytest.mark.unit


def wav_bytes(samples: np.ndarray, rate: int = 44100) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(rate)
        wav_file.writeframes((samples * 32767).astype("<i2").tobytes())
    return buffer.getvalue()


class FakeResponse(io.BytesIO):
    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


class FakeOpener:
    """요청을 기록하고, 정해 둔 응답(바이트 또는 HTTP 오류 코드)을 차례로 돌려준다."""

    def __init__(self, replies: list[bytes | int]) -> None:
        self.replies = list(replies)
        self.requests: list[tuple[str, dict[str, str], dict[str, object]]] = []

    def __call__(self, request: object, timeout: float) -> FakeResponse:
        headers = {key.lower(): value for key, value in request.header_items()}
        self.requests.append((request.full_url, headers, json.loads(request.data)))
        reply = self.replies.pop(0)
        if isinstance(reply, int):
            raise urllib.error.HTTPError(request.full_url, reply, "err", {}, io.BytesIO(b"{}"))
        return FakeResponse(reply)


SETTINGS = tv.TypecastSettings(voice_id="tc_test", tempo=1.1)


def test_decode_wav_returns_float_samples_and_rate() -> None:
    samples, rate = tv.decode_wav(wav_bytes(np.array([0.0, 0.5, -0.5], dtype=np.float32)))
    assert rate == 44100
    assert samples.dtype == np.float32
    assert np.allclose(samples, [0.0, 0.5, -0.5], atol=1e-3)


def test_decode_wav_rejects_stereo() -> None:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(44100)
        wav_file.writeframes(b"\x00\x00\x00\x00")
    with pytest.raises(tv.NarrationError):
        tv.decode_wav(buffer.getvalue())


def test_request_body_uses_smart_emotion_with_neighbor_lines() -> None:
    body = tv.request_body("둘째 줄", SETTINGS, previous="첫 줄", following="셋째 줄")
    assert body["voice_id"] == "tc_test"
    assert body["model"] == "ssfm-v31"
    assert body["language"] == "kor"
    assert body["prompt"] == {
        "emotion_type": "smart",
        "previous_text": "첫 줄",
        "next_text": "셋째 줄",
    }
    assert body["output"] == {"audio_format": "wav", "audio_tempo": 1.1}


def test_request_body_omits_missing_neighbors() -> None:
    body = tv.request_body("한 줄", SETTINGS, previous=None, following=None)
    assert body["prompt"] == {"emotion_type": "smart"}


def test_settings_reject_bad_values() -> None:
    with pytest.raises(ValueError):
        tv.TypecastSettings(voice_id="M1")
    with pytest.raises(ValueError):
        tv.TypecastSettings(voice_id="tc_x", tempo=3.0)


def test_synthesizer_sends_key_and_attribution_and_returns_samples() -> None:
    opener = FakeOpener([wav_bytes(np.full(10, 0.25, dtype=np.float32))])
    synth = tv.make_synthesizer(SETTINGS, ("가", "나"), api_key="secret", opener=opener)
    samples = synth("가")
    url, headers, body = opener.requests[0]
    assert url == "https://api.typecast.ai/v1/text-to-speech"
    assert headers["x-api-key"] == "secret"
    assert "generated_by=claude-code" in headers["user-agent"]
    assert body["prompt"]["next_text"] == "나"
    assert np.allclose(samples, 0.25, atol=1e-3)


def test_synthesizer_retries_rate_limit_then_succeeds() -> None:
    opener = FakeOpener([429, wav_bytes(np.zeros(4, dtype=np.float32))])
    synth = tv.make_synthesizer(
        SETTINGS, ("가",), api_key="k", opener=opener, sleep=lambda _: None
    )
    synth("가")
    assert len(opener.requests) == 2


@pytest.mark.parametrize(
    ("status", "hint"), [(401, "키"), (402, "크레딧"), (404, "목소리"), (403, "키")]
)
def test_synthesizer_explains_fatal_errors_without_key(status: int, hint: str) -> None:
    opener = FakeOpener([status])
    synth = tv.make_synthesizer(SETTINGS, ("가",), api_key="secret-key", opener=opener)
    with pytest.raises(tv.NarrationError) as caught:
        synth("가")
    assert hint in str(caught.value)
    assert "secret-key" not in str(caught.value)


def test_synthesizer_rejects_sample_rate_change() -> None:
    opener = FakeOpener([wav_bytes(np.zeros(4, dtype=np.float32), rate=32000)])
    synth = tv.make_synthesizer(SETTINGS, ("가",), api_key="k", opener=opener)
    with pytest.raises(tv.NarrationError):
        synth("가")


def test_find_api_key_prefers_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TYPECAST_API_KEY", "  from-env\n")
    assert tv.find_api_key(keychain=lambda: "from-keychain") == "from-env"


def test_find_api_key_falls_back_to_keychain(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TYPECAST_API_KEY", raising=False)
    assert tv.find_api_key(keychain=lambda: "from-keychain\n") == "from-keychain"


def test_find_api_key_explains_how_to_register(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TYPECAST_API_KEY", raising=False)
    with pytest.raises(tv.NarrationError) as caught:
        tv.find_api_key(keychain=lambda: None)
    assert "security add-generic-password" in str(caught.value)
