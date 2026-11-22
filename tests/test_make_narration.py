"""make_narration.py 테스트. 실행: python -m pytest tests (모델 없이 돈다)."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import types
import wave
from collections.abc import Callable
from pathlib import Path

import numpy as np
import pytest

MODULE_PATH = (
    Path(__file__).resolve().parents[1] / ".claude/skills/reels/templates/make_narration.py"
)
SAMPLE_RATE = 1000
AUDIO_RATE = 16000
LOUD = 0.5
NOISE = 0.001


def _load_module() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("make_narration", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["make_narration"] = module
    spec.loader.exec_module(module)
    return module


mn = _load_module()

requires_ffmpeg = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg가 필요합니다")


def make_clip(before: int, speech: int, after: int, floor: float = 0.0) -> np.ndarray:
    """앞 무음 + 말소리 + 뒤 무음(샘플 수)으로 된 가짜 음성."""
    parts = (np.full(before, floor), np.full(speech, LOUD), np.full(after, floor))
    return np.concatenate(parts).astype(np.float32)


def read_wav(path: Path) -> np.ndarray:
    """16비트 WAV를 -1~1 범위 배열로 읽는다."""
    with wave.open(str(path), "rb") as wav_file:
        frames = wav_file.readframes(wav_file.getnframes())
    return np.frombuffer(frames, dtype="<i2").astype(np.float32) / 32768


def fake_synth(sample_rate: int) -> Callable[[str], np.ndarray]:
    """글자 수에 비례하는 길이의 사인파를 돌려주는 가짜 합성기."""

    def synth(text: str) -> np.ndarray:
        speech = np.sin(np.arange(int(sample_rate * 0.05 * len(text))) * 0.2) * LOUD
        quiet_before = np.zeros(int(sample_rate * 0.1))
        quiet_after = np.zeros(int(sample_rate * 0.2))
        return np.concatenate((quiet_before, speech, quiet_after)).astype(np.float32)

    return synth


@pytest.mark.unit
def test_read_script_lines_drops_blank_lines_and_whitespace() -> None:
    text = "첫 문장입니다.\r\n\r\n  둘째 문장입니다.  \n"

    lines = mn.read_script_lines(text)

    assert lines == ("첫 문장입니다.", "둘째 문장입니다.")


@pytest.mark.unit
def test_read_script_lines_raises_when_script_is_empty() -> None:
    with pytest.raises(mn.NarrationError):
        mn.read_script_lines(" \n\n")


@pytest.mark.unit
def test_clean_text_removes_unsupported_characters_and_extra_spaces() -> None:
    cleaned = mn.clean_text("대추차  ★한\t잔", unsupported=("★",))

    assert cleaned == "대추차 한 잔"


@pytest.mark.unit
def test_speech_bounds_returns_first_and_last_loud_sample() -> None:
    samples = make_clip(100, 300, 200)

    assert mn.speech_bounds(samples) == (100, 400)


@pytest.mark.unit
def test_speech_bounds_ignores_noise_below_threshold() -> None:
    samples = make_clip(100, 300, 200, floor=NOISE)

    assert mn.speech_bounds(samples) == (100, 400)


@pytest.mark.unit
def test_speech_bounds_raises_when_audio_is_silent() -> None:
    with pytest.raises(mn.NarrationError):
        mn.speech_bounds(np.zeros(500, dtype=np.float32))


@pytest.mark.unit
def test_cut_clip_keeps_margin_of_original_audio() -> None:
    clip = mn.cut_clip(make_clip(100, 300, 200), SAMPLE_RATE, margin_seconds=0.08)

    assert len(clip.samples) == 80 + 300 + 80
    assert (clip.lead_margin, clip.tail_margin) == (80, 80)


@pytest.mark.unit
def test_cut_clip_uses_available_audio_when_silence_is_shorter_than_margin() -> None:
    clip = mn.cut_clip(make_clip(20, 300, 10), SAMPLE_RATE, margin_seconds=0.08)

    assert len(clip.samples) == 20 + 300 + 10
    assert (clip.lead_margin, clip.tail_margin) == (20, 10)


@pytest.mark.unit
def test_cut_clip_fades_margin_edges_without_touching_speech() -> None:
    clip = mn.cut_clip(make_clip(100, 300, 200, floor=NOISE), SAMPLE_RATE, margin_seconds=0.08)

    assert clip.samples[0] == 0
    assert clip.samples[-1] == 0
    assert np.all(clip.samples[10:80] == np.float32(NOISE))
    assert np.all(clip.samples[80:380] == np.float32(LOUD))


@pytest.mark.unit
def test_cut_clip_does_not_fade_speech_when_there_is_no_margin() -> None:
    clip = mn.cut_clip(make_clip(0, 300, 0), SAMPLE_RATE, margin_seconds=0.08)

    assert np.all(clip.samples == np.float32(LOUD))


@pytest.mark.unit
def test_assemble_places_speech_with_fixed_lead_gap_and_tail() -> None:
    clips = (
        mn.cut_clip(make_clip(100, 300, 200, floor=NOISE), SAMPLE_RATE, 0.08),
        mn.cut_clip(make_clip(50, 500, 50, floor=NOISE), SAMPLE_RATE, 0.08),
    )

    timeline = mn.assemble(clips, SAMPLE_RATE, mn.Spacing())

    assert timeline.sections == (mn.Section("s1", 0.3, 0.6), mn.Section("s2", 1.2, 1.7))
    assert timeline.total == 2.5
    assert len(timeline.samples) == 2500
    assert np.all(timeline.samples[300:600] == np.float32(LOUD))
    assert np.all(timeline.samples[1200:1700] == np.float32(LOUD))
    assert np.all(timeline.samples[:220] == 0)
    assert np.all(timeline.samples[230:300] == np.float32(NOISE))
    assert np.all(timeline.samples[680:1150] == 0)
    assert np.all(timeline.samples[1750:] == 0)


@pytest.mark.unit
def test_assemble_raises_without_clips() -> None:
    with pytest.raises(mn.NarrationError):
        mn.assemble((), SAMPLE_RATE, mn.Spacing())


@pytest.mark.unit
def test_spacing_rejects_gap_shorter_than_two_margins() -> None:
    with pytest.raises(ValueError):
        mn.Spacing(gap=0.1, margin=0.08)


@pytest.mark.unit
def test_voice_settings_default_to_mac_mini_app_values() -> None:
    settings = mn.VoiceSettings()

    assert (settings.voice, settings.speed, settings.steps, settings.pause, settings.lang) == (
        "M1",
        1.05,
        8,
        0.3,
        "ko",
    )


@pytest.mark.unit
def test_voice_settings_rejects_unknown_voice() -> None:
    with pytest.raises(ValueError):
        mn.VoiceSettings(voice="Z9")


@pytest.mark.unit
@pytest.mark.parametrize("field, value", [("speed", 5.0), ("steps", 99), ("pause", -1.0)])
def test_voice_settings_rejects_values_out_of_range(field: str, value: float) -> None:
    with pytest.raises(ValueError):
        mn.VoiceSettings(**{field: value})


@pytest.mark.unit
def test_write_wav_saves_mono_16bit_and_clips_peaks(tmp_path: Path) -> None:
    path = tmp_path / "out.wav"
    samples = np.array([0.0, 0.5, 2.0, -2.0], dtype=np.float32)

    mn.write_wav(path, samples, 8000)

    with wave.open(str(path)) as wav_file:
        params = (wav_file.getframerate(), wav_file.getnchannels(), wav_file.getsampwidth())
        frames = np.frombuffer(wav_file.readframes(4), dtype="<i2")
    assert params == (8000, 1, 2)
    assert frames[0] == 0
    assert abs(int(frames[1]) - 16384) <= 1
    assert (frames[2], frames[3]) == (32767, -32767)


@pytest.mark.unit
def test_wav_duration_reads_length_in_seconds(tmp_path: Path) -> None:
    path = tmp_path / "one_second.wav"
    mn.write_wav(path, np.zeros(8000, dtype=np.float32), 8000)

    assert mn.wav_duration(path) == 1.0


@pytest.mark.unit
def test_timings_payload_matches_build_composition_format() -> None:
    clips = (mn.cut_clip(make_clip(100, 300, 200), SAMPLE_RATE, 0.08),)
    timeline = mn.assemble(clips, SAMPLE_RATE, mn.Spacing())

    payload = mn.timings_payload(timeline, mn.VoiceSettings())

    assert payload["total"] == 1.4
    assert payload["sections"] == [{"id": "s1", "start": 0.3, "end": 0.6}]
    assert payload["voice"] == "M1"
    assert json.loads(json.dumps(payload, ensure_ascii=False)) == payload


@pytest.mark.unit
def test_loudnorm_raises_when_ffmpeg_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(mn.shutil, "which", lambda name: None)

    with pytest.raises(mn.NarrationError, match="ffmpeg"):
        mn.loudnorm(tmp_path / "in.wav", tmp_path / "out.wav", AUDIO_RATE)


@pytest.mark.integration
@requires_ffmpeg
def test_loudnorm_raises_when_ffmpeg_fails(tmp_path: Path) -> None:
    with pytest.raises(mn.NarrationError):
        mn.loudnorm(tmp_path / "missing.wav", tmp_path / "out.wav", AUDIO_RATE)


@pytest.mark.integration
@requires_ffmpeg
def test_build_narration_writes_audio_and_timings(tmp_path: Path) -> None:
    lines = ("첫 문장입니다.", "둘째 문장은 조금 더 깁니다.")

    summary = mn.build_narration(lines, fake_synth(AUDIO_RATE), AUDIO_RATE, tmp_path)

    timings = json.loads((tmp_path / "narration_timings.json").read_text(encoding="utf-8"))
    sections = timings["sections"]
    assert (tmp_path / "s1_M1.wav").exists() and (tmp_path / "s2_M1.wav").exists()
    assert [section["id"] for section in sections] == ["s1", "s2"]
    assert sections[0]["start"] == 0.3
    assert round(sections[1]["start"] - sections[0]["end"], 3) == 0.6
    assert round(timings["total"] - sections[1]["end"], 3) == 0.8
    assert abs(mn.wav_duration(tmp_path / "narration_norm.wav") - timings["total"]) < 0.02
    assert summary["total"] == timings["total"]
    assert summary["narration"] == str(tmp_path / "narration_norm.wav")


@pytest.mark.unit
def test_load_synthesizer_explains_install_when_supertonic_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(sys.modules, "supertonic", None)

    with pytest.raises(mn.NarrationError, match="requirements-voice.txt"):
        mn.load_synthesizer(mn.VoiceSettings())


@pytest.mark.unit
def test_load_synthesizer_calls_supertonic_with_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: dict[str, object] = {}

    class FakeProcessor:
        def validate_text(self, text: str) -> tuple[bool, list[str]]:
            bad = sorted(ch for ch in set(text) if ch == "★")
            return (not bad, bad)

    class FakeTTS:
        sample_rate = 44100

        def __init__(self, model: str, auto_download: bool) -> None:
            calls["init"] = (model, auto_download)
            self.model = types.SimpleNamespace(text_processor=FakeProcessor())

        def get_voice_style(self, voice_name: str) -> str:
            calls["voice"] = voice_name
            return "style"

        def synthesize(self, **kwargs: object) -> tuple[np.ndarray, np.ndarray]:
            calls["synthesize"] = kwargs
            return np.full((1, 10), LOUD, dtype=np.float64), np.array([10 / 44100])

    monkeypatch.setitem(sys.modules, "supertonic", types.SimpleNamespace(TTS=FakeTTS))

    synth, sample_rate = mn.load_synthesizer(mn.VoiceSettings())
    samples = synth("대추차 ★한 잔")

    assert sample_rate == 44100
    assert samples.shape == (10,) and samples.dtype == np.float32
    assert calls["init"] == ("supertonic-3", True)
    assert calls["voice"] == "M1"
    assert calls["synthesize"] == {
        "text": "대추차 한 잔",
        "voice_style": "style",
        "total_steps": 8,
        "speed": 1.05,
        "silence_duration": 0.3,
        "lang": "ko",
    }


@pytest.mark.unit
def test_load_synthesizer_explains_download_when_model_fails_to_load(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class BrokenTTS:
        def __init__(self, model: str, auto_download: bool) -> None:
            raise OSError("network down")

    monkeypatch.setitem(sys.modules, "supertonic", types.SimpleNamespace(TTS=BrokenTTS))

    with pytest.raises(mn.NarrationError, match="huggingface.co"):
        mn.load_synthesizer(mn.VoiceSettings())


@pytest.mark.integration
@requires_ffmpeg
def test_main_writes_narration_into_project_audio_folder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    script = tmp_path / "script.txt"
    script.write_text("첫 문장입니다.\n둘째 문장입니다.\n", encoding="utf-8")
    project = tmp_path / "project"
    monkeypatch.setattr(
        mn, "load_synthesizer", lambda settings: (fake_synth(AUDIO_RATE), AUDIO_RATE)
    )

    exit_code = mn.main([str(project), "--script", str(script)])

    summary = json.loads(capsys.readouterr().out)
    audio_dir = project / "assets" / "audio"
    assert exit_code == 0
    assert summary["narration"] == str(audio_dir / "narration_norm.wav")
    assert (audio_dir / "narration_timings.json").exists()
    assert summary["sections"] == 2


@pytest.mark.unit
def test_main_returns_error_when_script_is_missing(tmp_path: Path) -> None:
    exit_code = mn.main([str(tmp_path), "--script", str(tmp_path / "none.txt")])

    assert exit_code == 1


@pytest.mark.unit
def test_main_returns_error_when_speed_is_out_of_range(tmp_path: Path) -> None:
    script = tmp_path / "script.txt"
    script.write_text("첫 문장입니다.\n", encoding="utf-8")

    exit_code = mn.main([str(tmp_path), "--script", str(script), "--speed", "5"])

    assert exit_code == 1


@pytest.mark.unit
def test_main_rejects_unknown_voice(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        mn.main([str(tmp_path), "--script", "script.txt", "--voice", "Z9"])


@pytest.mark.unit
def test_main_returns_error_when_output_audio_is_unreadable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def broken_run(args: object) -> dict[str, object]:
        raise wave.Error("bad wav")

    monkeypatch.setattr(mn, "run", broken_run)

    exit_code = mn.main([str(tmp_path), "--script", "script.txt"])

    assert exit_code == 1


@pytest.mark.unit
def test_assemble_keeps_clips_apart_when_gap_equals_two_margins() -> None:
    clips = (
        mn.cut_clip(make_clip(100, 300, 200, floor=NOISE), SAMPLE_RATE, 0.08),
        mn.cut_clip(make_clip(100, 200, 200, floor=NOISE), SAMPLE_RATE, 0.08),
    )

    timeline = mn.assemble(clips, SAMPLE_RATE, mn.Spacing(gap=0.16, margin=0.08))

    assert timeline.sections == (mn.Section("s1", 0.3, 0.6), mn.Section("s2", 0.76, 0.96))
    assert np.all(timeline.samples[300:600] == np.float32(LOUD))
    assert np.all(timeline.samples[760:960] == np.float32(LOUD))
    assert np.all(np.abs(timeline.samples[600:760]) <= np.float32(NOISE))


@pytest.mark.unit
def test_assemble_handles_takes_without_surrounding_silence() -> None:
    clips = tuple(mn.cut_clip(make_clip(0, 100, 0), SAMPLE_RATE, 0.08) for _ in range(2))

    timeline = mn.assemble(clips, SAMPLE_RATE, mn.Spacing())

    assert timeline.sections == (mn.Section("s1", 0.3, 0.4), mn.Section("s2", 1.0, 1.1))
    assert timeline.total == 1.9
    assert np.all(timeline.samples[300:400] == np.float32(LOUD))
    assert np.all(timeline.samples[400:1000] == 0)


@pytest.mark.integration
@requires_ffmpeg
def test_build_narration_keeps_speech_at_the_section_times(tmp_path: Path) -> None:
    lines = ("첫 문장입니다.", "둘째 문장은 조금 더 깁니다.")

    mn.build_narration(lines, fake_synth(AUDIO_RATE), AUDIO_RATE, tmp_path)

    timings = json.loads((tmp_path / "narration_timings.json").read_text(encoding="utf-8"))
    start, end = mn.speech_bounds(read_wav(tmp_path / "narration_norm.wav"))
    assert abs(start / AUDIO_RATE - timings["sections"][0]["start"]) < 0.005
    assert abs(end / AUDIO_RATE - timings["sections"][-1]["end"]) < 0.005


@pytest.mark.integration
@requires_ffmpeg
def test_build_narration_leaves_no_outputs_when_length_drifts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "narration_timings.json").write_text("{}", encoding="utf-8")
    (tmp_path / "narration_norm.wav").write_bytes(b"old")
    monkeypatch.setattr(mn, "wav_duration", lambda path: 999.0)

    with pytest.raises(mn.NarrationError, match="길이"):
        mn.build_narration(("첫 문장입니다.",), fake_synth(AUDIO_RATE), AUDIO_RATE, tmp_path)

    assert not (tmp_path / "narration_norm.wav").exists()
    assert not (tmp_path / "narration_timings.json").exists()


@pytest.mark.unit
def test_build_narration_names_the_sentence_when_synthesis_fails(tmp_path: Path) -> None:
    def broken(text: str) -> np.ndarray:
        raise RuntimeError("onnx failed")

    with pytest.raises(mn.NarrationError, match="1번째 문장"):
        mn.build_narration(("첫 문장입니다.",), broken, AUDIO_RATE, tmp_path)


@pytest.mark.unit
def test_build_narration_names_the_sentence_when_take_is_silent(tmp_path: Path) -> None:
    def silent(text: str) -> np.ndarray:
        return np.zeros(100, dtype=np.float32)

    with pytest.raises(mn.NarrationError, match="1번째 문장"):
        mn.build_narration(("첫 문장입니다.",), silent, AUDIO_RATE, tmp_path)
