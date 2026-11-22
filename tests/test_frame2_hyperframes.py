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
