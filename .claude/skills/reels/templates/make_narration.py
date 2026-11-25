"""script.txt → 문장별 음성 → narration_norm.wav + narration_timings.json.

맥미니 "한국어 음성 생성기"(localhost:7790)와 같은 모델·목소리(Supertonic 3, 남성1 = M1)를
서버 없이 직접 불러 쓴다. 맥미니든 클라우드든 같은 명령으로 음성이 나온다.

- 대본 한 줄 = 음성 한 구간(s1, s2, ...). 줄마다 따로 만들어 `s<N>_<목소리>.wav`로 남긴다.
- 말소리 앞뒤 무음을 잘라(여유 0.08초) 앞 0.3초, 문장 사이 0.6초, 끝 0.8초로 다시 놓는다.
- loudnorm(I=-16:TP=-1.5:LRA=11)으로 음량을 맞춰 `narration_norm.wav`로 저장한다.
- 문장별 말소리 시작·끝(초)을 `narration_timings.json`(`total`, `sections`)에 적는다.

사용:
  pip install -r requirements-voice.txt          # 처음 한 번
  python make_narration.py <projects/<id>> --script <script.txt>
      [--voice M1] [--speed 1.05] [--steps 8] [--pause 0.3]
  python make_narration.py <projects/<id>> --script <script.txt> --engine typecast \
      --voice tc_<목소리 ID> [--speed 1.0]      # 타입캐스트 API(유료, typecast_voice.py)

결과는 <project>/assets/audio/ 에 생긴다. 첫 실행 때 모델(약 385MB)을
huggingface.co(Supertone/supertonic-3)에서 ~/.cache/supertonic3 로 내려받는다.
필요: Python 3.9+, FFmpeg.
"""

from __future__ import annotations

import argparse
import itertools
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import wave
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

logger = logging.getLogger("make_narration")

MODEL_NAME = "supertonic-3"
MODEL_SOURCE = "huggingface.co(Supertone/supertonic-3)"
VOICES = ("F1", "F2", "F3", "F4", "F5", "M1", "M2", "M3", "M4", "M5")
ENGINES = ("supertonic", "typecast")
DEFAULT_SPEED = {"supertonic": 1.05, "typecast": 1.0}
TYPECAST_SPEED_RANGE = (0.5, 2.0)
TYPECAST_FILE_TAG = "TC"
SPEED_RANGE = (0.7, 2.0)
STEPS_RANGE = (5, 12)
PAUSE_RANGE = (0.0, 2.0)
SILENCE_THRESHOLD_DB = -35.0
EDGE_FADE_SECONDS = 0.01
LOUDNORM_FILTER = "loudnorm=I=-16:TP=-1.5:LRA=11"
DURATION_TOLERANCE_SECONDS = 0.02
PCM16_PEAK = 32767
FFMPEG_TIMEOUT_SECONDS = 300
NARRATION_NAME = "narration_norm.wav"
TIMINGS_NAME = "narration_timings.json"
INSTALL_HINT = "pip install -r .claude/skills/reels/templates/requirements-voice.txt"

Synthesizer = Callable[[str], np.ndarray]


class NarrationError(Exception):
    """사용자에게 그대로 보여 줄 수 있는 실패."""


def _check_range(name: str, value: float, bounds: tuple[float, float]) -> None:
    low, high = bounds
    if not low <= value <= high:
        raise ValueError(f"{name} 값은 {low}~{high} 사이여야 합니다: {value}")


@dataclass(frozen=True)
class VoiceSettings:
    """음성 설정. 기본값은 맥미니 음성 생성기 화면의 기본값과 같다."""

    voice: str = "M1"
    speed: float = 1.05
    steps: int = 8
    pause: float = 0.3
    lang: str = "ko"
    engine: str = "supertonic"

    def __post_init__(self) -> None:
        if self.engine not in ENGINES:
            raise ValueError(f"engine은 {', '.join(ENGINES)} 중 하나여야 합니다: {self.engine}")
        if self.engine == "typecast":
            if not self.voice.startswith(("tc_", "uc_")):
                raise ValueError(f"타입캐스트 목소리 ID는 tc_ 또는 uc_로 시작합니다: {self.voice}")
            _check_range("speed", self.speed, TYPECAST_SPEED_RANGE)
            return
        if self.voice not in VOICES:
            raise ValueError(f"목소리는 {', '.join(VOICES)} 중 하나여야 합니다: {self.voice}")
        _check_range("speed", self.speed, SPEED_RANGE)
        _check_range("steps", self.steps, STEPS_RANGE)
        _check_range("pause", self.pause, PAUSE_RANGE)


    @property
    def file_tag(self) -> str:
        """줄별 원본 파일 이름 꼬리(s1_M1.wav, 타입캐스트는 s1_TC.wav)."""
        return TYPECAST_FILE_TAG if self.engine == "typecast" else self.voice

    @property
    def model_label(self) -> str:
        return "typecast ssfm-v31" if self.engine == "typecast" else MODEL_NAME


@dataclass(frozen=True)
class Spacing:
    """말소리 사이 간격(초). margin은 말소리 앞뒤로 남기는 원본 음성 길이."""

    lead: float = 0.3
    gap: float = 0.6
    tail: float = 0.8
    margin: float = 0.08

    def __post_init__(self) -> None:
        if self.margin < 0:
            raise ValueError("margin은 0 이상이어야 합니다.")
        if min(self.lead, self.tail) < self.margin or self.gap < 2 * self.margin:
            raise ValueError("lead·tail은 margin 이상, gap은 margin의 두 배 이상이어야 합니다.")


@dataclass(frozen=True, eq=False)
class Clip:
    """말소리 한 구간. samples에는 앞뒤 여유(lead_margin, tail_margin 샘플)가 들어 있다."""

    samples: np.ndarray
    lead_margin: int
    tail_margin: int


@dataclass(frozen=True)
class Section:
    id: str
    start: float
    end: float


@dataclass(frozen=True, eq=False)
class Timeline:
    samples: np.ndarray
    sections: tuple[Section, ...]
    total: float


def read_script_lines(text: str) -> tuple[str, ...]:
    """빈 줄을 뺀 대본 줄. 한 줄이 음성 한 구간이 된다."""
    lines = tuple(line.strip() for line in text.splitlines() if line.strip())
    if not lines:
        raise NarrationError("대본에 읽을 문장이 없습니다.")
    return lines


def clean_text(text: str, unsupported: Sequence[str]) -> str:
    """모델이 읽지 못하는 문자를 빼고 공백을 하나로 줄인다."""
    blocked = set(unsupported)
    kept = "".join(ch for ch in text if ch not in blocked)
    return re.sub(r"[ \t]+", " ", kept).strip()


def speech_bounds(
    samples: np.ndarray, threshold_db: float = SILENCE_THRESHOLD_DB
) -> tuple[int, int]:
    """말소리가 시작하는 샘플과 끝난 다음 샘플."""
    threshold = 10 ** (threshold_db / 20)
    loud = np.flatnonzero(np.abs(samples) >= threshold)
    if loud.size == 0:
        raise NarrationError("음성에서 말소리를 찾지 못했습니다(전체가 무음).")
    return int(loud[0]), int(loud[-1]) + 1


def _fade_edges(samples: np.ndarray, fade_in: int, fade_out: int) -> np.ndarray:
    """잘린 자리에서 딱 소리가 나지 않게 양 끝을 0으로 줄인다."""
    body = len(samples) - fade_in - fade_out
    gain = np.concatenate(
        (
            np.arange(fade_in) / max(fade_in, 1),
            np.ones(body),
            np.arange(fade_out)[::-1] / max(fade_out, 1),
        )
    )
    return (samples * gain).astype(np.float32)


def cut_clip(
    samples: np.ndarray,
    sample_rate: int,
    margin_seconds: float,
    threshold_db: float = SILENCE_THRESHOLD_DB,
) -> Clip:
    """말소리와 그 앞뒤 여유만 남긴다. 여유 구간 끝만 줄이고 말소리는 건드리지 않는다."""
    start, end = speech_bounds(samples, threshold_db)
    margin = round(margin_seconds * sample_rate)
    fade = round(EDGE_FADE_SECONDS * sample_rate)
    lead = min(margin, start)
    tail = min(margin, len(samples) - end)
    kept = samples[start - lead : end + tail]
    return Clip(_fade_edges(kept, min(fade, lead), min(fade, tail)), lead, tail)


def _speech_length(clip: Clip) -> int:
    return len(clip.samples) - clip.lead_margin - clip.tail_margin


def assemble(clips: Sequence[Clip], sample_rate: int, spacing: Spacing) -> Timeline:
    """말소리를 앞 lead, 사이 gap, 끝 tail 간격으로 한 줄에 놓는다."""
    if not clips:
        raise NarrationError("이어 붙일 음성이 없습니다.")
    lead, gap, tail = (
        round(seconds * sample_rate) for seconds in (spacing.lead, spacing.gap, spacing.tail)
    )
    lengths = tuple(_speech_length(clip) for clip in clips)
    starts = tuple(
        itertools.accumulate(lengths[:-1], lambda start, length: start + length + gap, initial=lead)
    )
    ends = tuple(start + length for start, length in zip(starts, lengths))
    track = np.zeros(ends[-1] + tail, dtype=np.float32)
    for start, clip in zip(starts, clips):
        begin = start - clip.lead_margin
        track[begin : begin + len(clip.samples)] = clip.samples
    sections = tuple(
        Section(f"s{index}", round(start / sample_rate, 3), round(end / sample_rate, 3))
        for index, (start, end) in enumerate(zip(starts, ends), start=1)
    )
    return Timeline(track, sections, round(len(track) / sample_rate, 3))


def write_wav(path: Path, samples: np.ndarray, sample_rate: int) -> None:
    """모노 16비트 WAV로 저장한다."""
    pcm = np.rint(np.clip(samples, -1.0, 1.0) * PCM16_PEAK).astype("<i2")
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm.tobytes())


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav_file:
        return wav_file.getnframes() / wav_file.getframerate()


def loudnorm(source: Path, target: Path, sample_rate: int) -> None:
    """ffmpeg loudnorm으로 음량을 맞춘다."""
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise NarrationError("ffmpeg를 찾지 못했습니다. ffmpeg를 설치한 뒤 다시 실행하세요.")
    # 절대 경로로 넘겨 "-"로 시작하는 폴더 이름이 ffmpeg 옵션으로 읽히지 않게 한다.
    command = (
        ffmpeg, "-y", "-loglevel", "error", "-i", str(source.resolve()),
        "-af", LOUDNORM_FILTER, "-ar", str(sample_rate), "-ac", "1",
        "-c:a", "pcm_s16le", str(target.resolve()),
    )  # fmt: skip
    try:
        subprocess.run(
            command, check=True, capture_output=True, text=True, timeout=FFMPEG_TIMEOUT_SECONDS
        )
    except subprocess.CalledProcessError as error:
        raise NarrationError(f"ffmpeg 음량 맞춤에 실패했습니다: {error.stderr.strip()}") from error
    except subprocess.TimeoutExpired as error:
        raise NarrationError("ffmpeg 음량 맞춤이 제한 시간 안에 끝나지 않았습니다.") from error


def timings_payload(timeline: Timeline, settings: VoiceSettings) -> dict[str, object]:
    """build_composition.py가 읽는 형식(total, sections[id, start, end])."""
    return {
        "source": f"{settings.model_label} {settings.voice} (make_narration.py)",
        **asdict(settings),
        "total": timeline.total,
        "sections": [asdict(section) for section in timeline.sections],
    }


def _synthesize_line(index: int, line: str, synth: Synthesizer) -> np.ndarray:
    try:
        return synth(line)
    except NarrationError as error:
        raise NarrationError(f"{index}번째 문장: {error}") from error
    except Exception as error:  # 음성 라이브러리 예외 종류가 정해져 있지 않아 넓게 받아 다시 던진다
        raise NarrationError(f"{index}번째 문장 음성 생성에 실패했습니다: {error}") from error


def _cut_line(index: int, take: np.ndarray, sample_rate: int, margin: float) -> Clip:
    try:
        return cut_clip(take, sample_rate, margin)
    except NarrationError as error:
        raise NarrationError(f"{index}번째 문장: {error}") from error


def _save_normalized(timeline: Timeline, target: Path, sample_rate: int) -> None:
    """임시 폴더에서 음량을 맞추고, 길이가 맞을 때만 결과 자리에 놓는다."""
    with tempfile.TemporaryDirectory(dir=target.parent) as work_dir:
        edited = Path(work_dir) / "narration_edit.wav"
        normalized = Path(work_dir) / target.name
        write_wav(edited, timeline.samples, sample_rate)
        loudnorm(edited, normalized, sample_rate)
        drift = abs(wav_duration(normalized) - timeline.total)
        if drift > DURATION_TOLERANCE_SECONDS:
            raise NarrationError(
                f"음량을 맞춘 뒤 길이가 {drift:.3f}초 달라져 자막 시각이 어긋납니다."
            )
        os.replace(normalized, target)


def build_narration(
    lines: Sequence[str],
    synth: Synthesizer,
    sample_rate: int,
    out_dir: Path,
    settings: VoiceSettings = VoiceSettings(),
    spacing: Spacing = Spacing(),
) -> dict[str, object]:
    """줄마다 음성을 만들어 원본을 남기고, 간격·음량을 맞춘 음성과 구간 파일을 쓴다."""
    out_dir.mkdir(parents=True, exist_ok=True)
    narration, timings = out_dir / NARRATION_NAME, out_dir / TIMINGS_NAME
    for previous in (narration, timings):
        previous.unlink(missing_ok=True)  # 중간에 실패해도 예전 음성·구간 파일과 섞이지 않게 한다
    originals = tuple(
        out_dir / f"s{index}_{settings.file_tag}.wav" for index in range(1, len(lines) + 1)
    )
    takes = []
    for index, (line, original) in enumerate(zip(lines, originals), start=1):
        logger.info("s%d 만드는 중 (%d자)", index, len(line))
        take = _synthesize_line(index, line, synth)
        write_wav(original, take, sample_rate)
        takes.append(take)
    clips = tuple(
        _cut_line(index, take, sample_rate, spacing.margin)
        for index, take in enumerate(takes, start=1)
    )
    timeline = assemble(clips, sample_rate, spacing)
    _save_normalized(timeline, narration, sample_rate)
    payload = timings_payload(timeline, settings)
    timings.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    return {
        "narration": str(narration),
        "timings": str(timings),
        "total": timeline.total,
        "sections": len(timeline.sections),
        "voice": settings.voice,
        "originals": [str(path) for path in originals],
    }


def load_synthesizer(settings: VoiceSettings) -> tuple[Synthesizer, int]:
    """Supertonic 3 모델을 불러 (문장 → 음성 배열) 함수와 샘플레이트를 돌려준다."""
    try:
        from supertonic import TTS
    except ImportError as error:
        raise NarrationError(
            f"supertonic이 설치돼 있지 않습니다. 먼저 실행하세요: {INSTALL_HINT}"
        ) from error
    try:
        tts = TTS(model=MODEL_NAME, auto_download=True)
        style = tts.get_voice_style(voice_name=settings.voice)
    except (
        Exception
    ) as error:  # 라이브러리·내려받기 예외 종류가 정해져 있지 않아 넓게 받아 다시 던진다
        raise NarrationError(
            f"음성 모델을 불러오지 못했습니다. 첫 실행은 {MODEL_SOURCE}에서 약 385MB를 "
            f"내려받습니다. 접속이 되는지 확인하세요: {error}"
        ) from error

    def synth(text: str) -> np.ndarray:
        _, unsupported = tts.model.text_processor.validate_text(text)
        if unsupported:
            logger.warning("읽지 못하는 문자를 빼고 만듭니다: %s", " ".join(unsupported))
        readable = clean_text(text, unsupported)
        if not readable:
            raise NarrationError(f"읽을 수 있는 글자가 없습니다: {text!r}")
        wav, _ = tts.synthesize(
            text=readable,
            voice_style=style,
            total_steps=settings.steps,
            speed=settings.speed,
            silence_duration=settings.pause,
            lang=settings.lang,
        )
        return np.asarray(wav, dtype=np.float32).reshape(-1)

    return synth, int(tts.sample_rate)


def load_typecast_synthesizer(
    settings: VoiceSettings, lines: Sequence[str]
) -> tuple[Synthesizer, int]:
    """타입캐스트 API로 줄마다 음성을 만드는 함수(typecast_voice.py)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import typecast_voice

    try:
        api_key = typecast_voice.find_api_key()
        tc_settings = typecast_voice.TypecastSettings(voice_id=settings.voice, tempo=settings.speed)
    except typecast_voice.NarrationError as error:
        raise NarrationError(str(error)) from None
    synth = typecast_voice.make_synthesizer(tc_settings, tuple(lines), api_key)
    return synth, typecast_voice.SAMPLE_RATE


def _voice_arg(value: str) -> str:
    if value in VOICES or value.startswith(("tc_", "uc_")):
        return value
    raise argparse.ArgumentTypeError(
        f"목소리는 {', '.join(VOICES)} 또는 타입캐스트 ID(tc_…/uc_…)여야 합니다: {value}"
    )


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    defaults = VoiceSettings()
    parser = argparse.ArgumentParser(
        description="대본을 음성으로 만든다(기본 Supertonic 3 남성1 M1, --engine typecast면 타입캐스트)."
    )
    parser.add_argument("project", type=Path, help="OpenMontage/projects/<id> 폴더")
    parser.add_argument("--script", type=Path, required=True, help="한 줄에 한 문장씩 적은 대본")
    parser.add_argument("--engine", choices=ENGINES, default=defaults.engine)
    parser.add_argument(
        "--voice", type=_voice_arg, default=None, help="M1 등, 타입캐스트면 tc_… 목소리 ID"
    )
    parser.add_argument(
        "--speed", type=float, default=None, help="기본 Supertonic 1.05, 타입캐스트 1.0"
    )
    parser.add_argument("--steps", type=int, default=defaults.steps)
    parser.add_argument(
        "--pause", type=float, default=defaults.pause, help="한 줄 안 문장 사이 쉼(초)"
    )
    return parser.parse_args(argv)


def run(args: argparse.Namespace) -> dict[str, object]:
    if args.engine == "typecast" and args.voice is None:
        raise NarrationError("타입캐스트는 --voice에 목소리 ID(tc_…)를 적어야 합니다.")
    settings = VoiceSettings(
        voice=args.voice or VoiceSettings().voice,
        speed=DEFAULT_SPEED[args.engine] if args.speed is None else args.speed,
        steps=args.steps,
        pause=args.pause,
        engine=args.engine,
    )
    if not args.script.is_file():
        raise NarrationError(f"대본 파일이 없습니다: {args.script}")
    lines = read_script_lines(args.script.read_text(encoding="utf-8"))
    if settings.engine == "typecast":
        synth, sample_rate = load_typecast_synthesizer(settings, lines)
    else:
        synth, sample_rate = load_synthesizer(settings)
    return build_narration(lines, synth, sample_rate, args.project / "assets" / "audio", settings)


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = parse_args(argv)
    try:
        summary = run(args)
    except (NarrationError, ValueError, OSError, wave.Error, EOFError) as error:
        logger.error("음성을 만들지 못했습니다: %s", error)
        return 1
    sys.stdout.write(json.dumps(summary, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
