"""basic1_hyperframes.py(기본1 형식) 테스트. 사진·음성·글꼴 없이 설정 검사와 HTML 조립만 본다."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

TEMPLATES = Path(__file__).resolve().parents[1] / ".claude/skills/reels/templates"
spec = importlib.util.spec_from_file_location("basic1_hyperframes", TEMPLATES / "basic1_hyperframes.py")
b1 = importlib.util.module_from_spec(spec)
sys.modules["basic1_hyperframes"] = b1
spec.loader.exec_module(b1)

pytestmark = pytest.mark.unit


def scene(n: int, **extra) -> dict:
    return {"photo": f"assets/p{n}.jpg", "author": f"작가{n}", "lines": [f"{n}번 첫 줄", f"{n}번 둘째 줄"], **extra}


CFG = {
    "bar": "아이폰18",
    "title": "제목 <테스트>",
    "scenes": [
        scene(1),
        scene(2, pop={"text": "최대 40%", "at": 0.5}, split={"photo": "assets/q.jpg", "author": "작가Q"}),
        scene(3, contain=True),
    ],
    "recap": [{"photo": "assets/p1.jpg", "author": "작가1", "from": 0.2, "to": 0.8}],
}
TIMINGS = {"total": 9.0, "sections": [
    {"id": "s1", "start": 0.3, "end": 2.5},
    {"id": "s2", "start": 3.1, "end": 5.5},
    {"id": "s3", "start": 6.1, "end": 8.2},
]}


def test_boundaries_start_at_zero_and_end_after_last_line() -> None:
    assert b1.boundaries(TIMINGS, 3) == [0.0, 2.8, 5.8, 8.7]


def test_boundaries_reject_scene_count_mismatch() -> None:
    with pytest.raises(ValueError):
        b1.boundaries(TIMINGS, 2)


def test_check_config_requires_two_caption_lines() -> None:
    bad = {**CFG, "scenes": [{**scene(1), "lines": ["한 줄만"]}]}
    with pytest.raises(ValueError):
        b1.check_config(bad)


def test_build_html_has_layout_ment_ad_and_escapes_title() -> None:
    page = b1.build_html(b1.check_config(CFG), b1.boundaries(TIMINGS, 3))
    assert "겅태상점으로 오세요" in page
    assert b1.AD_NOTE in page
    assert "제목 &lt;테스트&gt;" in page
    assert 'data-duration="8.7"' in page
    assert 'id="img2b"' in page  # 2장면 뒤 절반 사진
    assert 'id="hl2"' in page and "최대 40%" in page
    assert 'id="img3bg"' in page  # contain 장면은 흐린 배경
    assert 'id="rc1"' in page  # 마지막 장면 다시 보기


def test_build_html_can_drop_ad_note() -> None:
    page = b1.build_html(b1.check_config({**CFG, "ad_note": False}), b1.boundaries(TIMINGS, 3))
    assert b1.AD_NOTE not in page
