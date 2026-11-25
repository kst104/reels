"""기본1 형식 결과(hf/index.html)의 장면 사진을 힉스필드 영상으로 바꾼다.

스킬 틀(basic1_hyperframes.py)은 사진만 받으므로, 이 프로젝트에서만 틀이 만든
HTML을 고친다. basic1.json 장면의 "video" 값이 있는 장면만 바꾼다.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
HF = PROJECT / "hf"


def swap(page: str, n: int, video_name: str) -> str:
    block = re.compile(
        rf'(<div id="img{n}" class="clip panel" data-start="([\d.]+)" data-duration="([\d.]+)"[^>]*>\s*)'
        rf'<img id="img{n}ph" src="[^"]+" style="([^"]*)" alt="" />'
    )
    match = block.search(page)
    if not match:
        raise ValueError(f"{n}번 장면 사진 자리를 찾지 못했습니다.")
    start, dur, style = match.group(2), match.group(3), match.group(4)
    style = ("position:absolute;left:0;top:0;width:100%;height:100%;display:block;"
             + style.replace("object-fit:contain", "object-fit:cover"))
    video = (f'<video id="img{n}ph" class="clip" src="assets/video/{video_name}" style="{style}" '
             f'data-start="{start}" data-duration="{dur}" data-track-index="11" muted playsinline></video>')
    # 영상만 시간을 갖게 하고, 감싸는 상자는 시간 없이 투명하게 둔다(lint: video_nested_in_timed_element).
    wrapper = f'<div id="img{n}" class="panel" style="background:transparent">\n        '
    return page[:match.start()] + wrapper + video + page[match.end():]


def main() -> int:
    cfg = json.loads((PROJECT / "basic1.json").read_text())
    page = (HF / "index.html").read_text()
    (HF / "assets/video").mkdir(parents=True, exist_ok=True)
    try:
        for n, scene in enumerate(cfg["scenes"], 1):
            if not scene.get("video"):
                continue
            src = PROJECT / scene["video"]
            if not src.is_file():
                raise FileNotFoundError(f"영상이 없습니다: {src}")
            shutil.copyfile(src, HF / "assets/video" / src.name)
            page = swap(page, n, src.name)
    except (OSError, ValueError) as error:
        print(f"영상으로 바꾸지 못했습니다: {error}", file=sys.stderr)
        return 1
    (HF / "index.html").write_text(page)
    print("영상으로 바꾼 장면:", [n for n, s in enumerate(cfg["scenes"], 1) if s.get("video")])
    return 0


if __name__ == "__main__":
    sys.exit(main())
