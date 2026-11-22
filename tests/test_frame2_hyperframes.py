"""frame2_hyperframes.py 자막 강조 확대율 테스트. 실행: python -m pytest tests"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / ".claude/skills/reels/templates/frame2_hyperframes.py"
VIDEO = ROOT / "videos/2026-11-22_jujube-tea-sugar"
LONG_WORD = "국제암연구기관이"


def _load_module() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("frame2_hyperframes", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["frame2_hyperframes"] = module
    spec.loader.exec_module(module)
    return module


hf = _load_module()


@pytest.mark.unit
def test_caption_pop_scale_keeps_full_pop_for_short_words() -> None:
    assert hf.caption_pop_scale("대추차") == 1.08


@pytest.mark.unit
def test_caption_pop_scale_shrinks_long_words_so_gaps_stay_visible() -> None:
    scale = hf.caption_pop_scale(LONG_WORD)

    grow_per_side = (scale - 1) * hf.caption_width_px(LONG_WORD) / 2
    assert scale < 1.04
    assert grow_per_side <= 7.5


@pytest.mark.unit
def test_caption_width_counts_latin_and_digits_as_narrower() -> None:
    assert hf.caption_width_px("10그램") == 2 * 34 + 2 * 58


@pytest.mark.unit
def test_caption_pop_scale_handles_empty_word() -> None:
    assert hf.caption_pop_scale("") == 1.08


def _comp(style: str | None) -> dict:
    cuts = [
        {"id": "c1", "type": "hero_title", "text": "효능보다 먼저 볼 건 설탕", "in_seconds": 0, "out_seconds": 3,
         "hf": {"photo": "assets/images/c1.webp"}},
        {"id": "c2", "type": "stat_card", "stat": "30g", "subtitle": "세 잔", "in_seconds": 3, "out_seconds": 7,
         "hf": {"gauge": {"value": 30, "max": 50, "max_label": "하루 권고 50g", "mark": 25, "mark_label": "절반"},
                "photo": "assets/images/c2.webp"}},
        {"id": "c3", "type": "text_card", "text": "뜨거우면, 한 김 식혀서", "in_seconds": 7, "out_seconds": 10,
         "hf": {"icon": "cup"}},
        {"id": "c4", "type": "callout", "title": "끝", "text": "판매 발생 시 수수료를 제공받습니다.",
         "in_seconds": 10, "out_seconds": 12, "hf": {"photo": "assets/images/c4.webp"}},
    ]
    comp = {"cuts": cuts, "captions": [], "audio": {}}
    if style:
        comp["hf_style"] = style
    return comp


def _build(style: str | None) -> str:
    return hf.Builder(_comp(style), {"total": 12, "sections": []}).build()


@pytest.mark.unit
def test_text_style_is_default_and_adds_no_photos_drawings_or_particles() -> None:
    html = _build(None)

    assert 'class="photo"' not in html
    assert 'id="fx"' not in html
    assert 'class="gauge"' not in html
    assert 'class="cup"' not in html
    assert 'id="c3-check"' in html  # text 방식의 cup은 check로


@pytest.mark.unit
def test_motion_style_adds_particles_camera_push_gauge_and_cup_but_no_photo() -> None:
    html = _build("motion")

    assert 'id="fx"' in html and html.count('class="dot"') == hf.PARTICLES
    assert f'scale: {hf.CAMERA_PUSH}' in html
    assert 'tl.fromTo("#c2-gfill", {scaleX: 0}, {scaleX: 0.6,' in html
    assert 'style="left:50%"' in html  # 절반 표시
    assert 'id="c3-cup"' in html and 'id="c3-check"' not in html
    assert 'class="photo"' not in html


@pytest.mark.unit
def test_photo_style_puts_slow_zoom_photos_on_cuts_but_not_on_endcard() -> None:
    html = _build("photo")

    assert 'src="assets/photos/c1.webp"' in html
    assert 'src="assets/photos/c2.webp"' in html
    assert 'id="c4-photo"' not in html  # 마지막 컷 = 끝 화면은 글자만
    assert re.search(r'tl\.fromTo\("#c1-img", \{scale: 1\.02, x: -24\}, \{scale: 1\.14, x: 24,', html)
    assert re.search(r'tl\.fromTo\("#c2-img", \{scale: 1\.02, x: 24\}, \{scale: 1\.14, x: -24,', html)


@pytest.mark.unit
def test_every_repeat_is_finite_for_deterministic_render() -> None:
    html = _build("photo")

    repeats = [int(n) for n in re.findall(r"repeat: (-?\d+)", html)]
    assert repeats and min(repeats) >= 0


@pytest.mark.unit
def test_unknown_style_is_rejected_with_choices() -> None:
    with pytest.raises(ValueError, match="text, motion, photo"):
        _build("fancy")


@pytest.mark.unit
def test_gauge_rejects_zero_max() -> None:
    comp = _comp("motion")
    comp["cuts"][1]["hf"]["gauge"]["max"] = 0

    with pytest.raises(ValueError, match="gauge.max"):
        hf.Builder(comp, {"total": 12, "sections": []}).build()


@pytest.mark.unit
def test_copy_photos_stops_with_list_of_missing_files(tmp_path: Path) -> None:
    comp = _comp("photo")

    with pytest.raises(SystemExit, match="c1: .*c1.webp"):
        hf.copy_photos(comp, tmp_path, tmp_path / "ws")


@pytest.mark.integration
def test_builder_writes_per_word_scale_into_caption_tweens() -> None:
    comp = json.loads((VIDEO / "artifacts/composition_hf.json").read_text(encoding="utf-8"))
    timings = json.loads((VIDEO / "audio/narration_timings.json").read_text(encoding="utf-8"))

    html = hf.Builder(comp, timings).build()

    words = dict(re.findall(r'<span class="cw" id="(cap\d+-\d+)">([^<]*)</span>', html))
    scales = {
        match.group(1): float(match.group(2))
        for match in re.finditer(r'tl\.to\("#(cap\d+-\d+)", \{color: "#FF8A3D", scale: ([0-9.]+)', html)
    }
    assert len(words) == len(scales) == len(comp["captions"])
    assert all(scales[key] == hf.caption_pop_scale(word) for key, word in words.items())
    assert scales[next(key for key, word in words.items() if word == LONG_WORD)] == 1.03
