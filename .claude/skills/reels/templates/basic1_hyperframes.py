"""기본1 형식(뉴스 카드형 쇼츠)을 HyperFrames 작업 폴더로 만든다. 2026-11-25 사용자 지정.

화면(1080x1920). 맨 아래 320px는 인스타·유튜브의 아이디·캡션·음악 줄 자리라 비워 둔다(2026-11-25 사용자: "겹치지않게 글씨위치 조정해줘").
쓰는 높이 1600px를 기준으로:
- 위(256px): 주황 띠(64px, 주제 낱말) : 고정 제목(192px) = 1:3
- 가운데(1088px): 장면 사진. 잘라 쓰고 대비·채도를 살짝 올리고 천천히 확대·이동한다. 작가·라이선스·광고 표기는 왼쪽 아래
  (오른쪽 세로 버튼 줄과 겹치지 않게)
- 아래(256px): 자막(192px) : 주황 띠 "겅태상점으로 오세요"(64px) = 3:1. 위아래 띠는 2026-11-25에 400px → 320px → 256px로 두 번 20%씩 줄였다("가운데 영상이 너무 좁아", "좀더 20%줄여줘"). 자막은 양옆 120px 여백
- 제목·자막 글꼴은 부드러운 Jua(Google Fonts, OFL), 띠 글꼴은 Apple SD Gothic Neo(또는 Noto Sans CJK)
- 파란 강조 글자(기울어져 튀어나옴) + 팝 효과음, 장면이 바뀔 때도 팝 효과음
- 마지막 장면: 앞에서 말한 장점 사진을 다시 짧게 보여 주고(recap), 오른쪽 아래에 광고 표기

사용법(OpenMontage 폴더에서):
    .venv/bin/python ../.claude/skills/reels/templates/basic1_hyperframes.py projects/<id>
필요: projects/<id>/basic1.json, assets/audio/narration_norm.wav, assets/audio/narration_timings.json
(make_narration.py 결과), basic1.json이 가리키는 사진. 결과는 projects/<id>/hf/.
예시 설정: videos/2026-11-25_iphone18-pro-news/artifacts/hyperframes/basic1.json
"""

from __future__ import annotations

import argparse
import html as htmllib
import importlib.util
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
JUA_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/jua/Jua-Regular.ttf"
JUA_CACHE = Path.home() / ".cache/reels-fonts/Jua-Regular.ttf"
AD_NOTE = "이 영상은 네이버 쇼핑 커넥트 활동의 일환으로, 판매 발생 시 수수료를 제공받습니다."
DEFAULT_MENT = "겅태상점으로 오세요"
END_TAIL = 0.5  # 마지막 말 끝 + 0.5초에서 끊는다
PUNCH_MIN = 3.5  # 이보다 긴 장면은 가운데서 한 번 더 다가간다
BAR_COLOR = "#ff7a1a"
POP_COLOR = "#1e63ff"


def esc(text: str) -> str:
    return htmllib.escape(str(text), quote=True)


def check_config(cfg: dict) -> dict:
    for key in ("bar", "title", "scenes"):
        if not cfg.get(key):
            raise ValueError(f"basic1.json에 '{key}'가 없습니다.")
    for n, sc in enumerate(cfg["scenes"], 1):
        if len(sc.get("lines", [])) != 2:
            raise ValueError(f"{n}번 장면: 자막 lines는 두 줄이어야 합니다.")
        if not sc.get("photo") or not sc.get("author"):
            raise ValueError(f"{n}번 장면: photo와 author가 필요합니다.")
    return cfg


def boundaries(timings: dict, scene_count: int, end_tail: float = END_TAIL) -> list[float]:
    """장면 경계: 문장 시작 0.3초 전, 첫 장면은 0초, 끝은 마지막 말 끝 + end_tail."""
    sections = timings["sections"]
    if len(sections) != scene_count:
        raise ValueError(f"대본 줄 수({len(sections)})와 장면 수({scene_count})가 다릅니다.")
    starts = [0.0] + [round(s["start"] - 0.3, 3) for s in sections[1:]]
    return starts + [round(sections[-1]["end"] + end_tail, 3)]


def img_id(photo: str) -> str:
    return Path(photo).stem


def credit(item: dict) -> str:
    source = item.get("source", "Wikimedia Commons")
    lic = item.get("license", "CC BY-SA 4.0")
    return f'사진: {esc(item["author"])} · {esc(source)} · {esc(lic)}'


def all_photos(cfg: dict) -> list[dict]:
    items = list(cfg["scenes"]) + [sc["split"] for sc in cfg["scenes"] if sc.get("split")]
    return items + list(cfg.get("recap", []))


def prepare_media(cfg: dict, project: Path, hf: Path) -> None:
    from PIL import Image, ImageEnhance, ImageFilter

    (hf / "assets/img").mkdir(parents=True, exist_ok=True)
    (hf / "assets/audio").mkdir(parents=True, exist_ok=True)
    done: set[str] = set()
    for item in all_photos(cfg):
        name = img_id(item["photo"])
        if name in done:
            continue
        done.add(name)
        src = project / item["photo"]
        if not src.is_file():
            raise FileNotFoundError(f"사진이 없습니다: {src}")
        im = Image.open(src).convert("RGB")
        if item.get("crop"):
            l, t, r, b = item["crop"]
            im = im.crop((int(l * im.width), int(t * im.height), int(r * im.width), int(b * im.height)))
        im.thumbnail((1600, 1600))
        im = ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.08)).enhance(1.12)
        im.save(hf / f"assets/img/{name}.jpg", quality=90)
        if item.get("contain"):
            bg = im.resize((540, int(540 * im.height / im.width))).filter(ImageFilter.GaussianBlur(18))
            ImageEnhance.Brightness(bg).enhance(0.55).save(hf / f"assets/img/{name}_bg.jpg", quality=85)
    shutil.copyfile(project / "assets/audio/narration_norm.wav", hf / "assets/audio/narration.wav")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                    "sine=frequency=1400:duration=0.07", "-af",
                    "afade=t=out:st=0.01:d=0.06,volume=0.35", str(hf / "assets/audio/pop.wav")], check=True)


def photo_block(div_id: str, cls: str, item: dict, start: float, dur: float, track: int) -> str:
    name = img_id(item["photo"])
    fit = "contain" if item.get("contain") else "cover"
    bg = f'<img id="{div_id}bg" class="bg" src="assets/img/{name}_bg.jpg" alt="" />' if item.get("contain") else ""
    focus = item.get("focus", "50% 50%")
    return (f'      <div id="{div_id}" class="clip panel{cls}" data-start="{start}" data-duration="{dur}" data-track-index="{track}">\n'
            f'        {bg}<img id="{div_id}ph" src="assets/img/{name}.jpg" style="object-position:{focus};object-fit:{fit}" alt="" />\n'
            f'      </div>')


def credit_line(p_id: str, cls: str, item: dict, start: float, dur: float, track: int) -> str:
    return (f'      <p id="{p_id}" class="clip credit{cls}" data-start="{start}" data-duration="{dur}" '
            f'data-track-index="{track}">{credit(item)}</p>')


def pan(sel: str, d: int, s: float, dur: float) -> str:
    return (f'tl.fromTo("{sel}", {{scale: 1.0, xPercent: {-1.5 * d}}}, '
            f'{{scale: 1.09, xPercent: {1.5 * d}, duration: {dur}, ease: "none"}}, {s});')


def punch(sel: str, d: int, s: float, dur: float) -> list[str]:
    """3.5초 넘는 장면: 가운데서 한 번 더 다가간다."""
    half = round(dur / 2, 3)
    return [
        f'tl.fromTo("{sel}", {{scale: 1.0, xPercent: {-1.5 * d}}}, {{scale: 1.05, xPercent: 0, duration: {half}, ease: "none"}}, {s});',
        f'tl.to("{sel}", {{scale: 1.16, xPercent: {2 * d}, yPercent: -3, duration: 0.3, ease: "power2.out"}}, {round(s + half, 3)});',
        f'tl.to("{sel}", {{scale: 1.2, duration: {round(dur - half - 0.3, 3)}, ease: "none"}}, {round(s + half + 0.3, 3)});',
    ]


def audio_clip(a_id: str, start: float, track: int) -> str:
    return (f'      <audio id="{a_id}" class="clip" src="assets/audio/pop.wav" data-start="{start}" '
            f'data-duration="0.1" data-track-index="{track}"></audio>')


def scene_parts(i: int, sc: dict, s: float, e: float, recap_end: float | None):
    """장면 하나의 사진·작가·자막·효과음·움직임."""
    blocks, sounds, tweens = [], [], []
    dur = round(e - s, 3)
    d = sc.get("dir", 1 if i % 2 else -1)
    halves = [(sc, s, e, "")]
    if sc.get("split"):
        mid = round(s + dur / 2, 3)
        halves = [(sc, s, mid, ""), (sc["split"], mid, e, "b")]
    for item, ps, pe, sfx in halves:
        cs = round(ps + recap_end, 3) if recap_end is not None else ps  # 다시 보기 동안은 그 사진 작가를 보인다
        blocks.append(photo_block(f"img{i}{sfx}", "", item, ps, round(pe - ps, 3), 1))
        blocks.append(credit_line(f"cr{i}{sfx}", "", item, cs, round(pe - cs, 3), 2))
        if sfx:
            sounds.append(audio_clip(f"pop{i}b", ps, 5))
            tweens.append(pan(f"#img{i}bph", -d, ps, round(pe - ps, 3)))
    if sc.get("split"):
        tweens.append(pan(f"#img{i}ph", d, s, round(dur / 2, 3)))
    elif dur > PUNCH_MIN:
        tweens += punch(f"#img{i}ph", d, s, dur)
    else:
        tweens.append(pan(f"#img{i}ph", d, s, dur))
    l1, l2 = sc["lines"]
    blocks.append(f'      <div id="cap{i}" class="clip cap" data-start="{s}" data-duration="{dur}" data-track-index="3">'
                  f'<div id="capin{i}"><p>{esc(l1)}</p><p>{esc(l2)}</p></div></div>')
    if i > 1:
        sounds.append(audio_clip(f"pop{i}", s, 5))
    if sc.get("pop"):
        t0 = round(s + float(sc["pop"].get("at", 0.9)), 3)
        blocks.append(f'      <div id="hl{i}" class="clip hl" data-start="{t0}" data-duration="{round(e - t0, 3)}" '
                      f'data-track-index="6"><span id="hlin{i}">{esc(sc["pop"]["text"])}</span></div>')
        sounds.append(audio_clip(f"hpop{i}", t0, 7))
        tweens.append(f'tl.fromTo("#hlin{i}", {{scale: 0.3, rotation: -14}}, '
                      f'{{scale: 1, rotation: -6, duration: 0.3, ease: "back.out(2.4)"}}, {t0});')
    return blocks, sounds, tweens


def recap_parts(recap: list[dict], last_start: float):
    blocks, sounds, tweens = [], [], []
    for k, item in enumerate(recap, 1):
        t0, d0 = round(last_start + item["from"], 3), round(item["to"] - item["from"], 3)
        blocks.append(photo_block(f"rc{k}", " recap", item, t0, d0, 8))
        blocks.append(credit_line(f"rcr{k}", " recap-cr", item, t0, d0, 9))
        sounds.append(audio_clip(f"rpop{k}", t0, 10))
        tweens.append(f'tl.fromTo("#rc{k}ph", {{scale: 1.12}}, {{scale: 1.0, duration: {d0}, ease: "power2.out"}}, {t0});')
    return blocks, sounds, tweens


CSS = """      @font-face { font-family: "KR"; src: url("assets/fonts/KR-Regular.woff2") format("woff2"); font-weight: 400; }
      @font-face { font-family: "KR"; src: url("assets/fonts/KR-Bold.woff2") format("woff2"); font-weight: 700 900; }
      @font-face { font-family: "Soft"; src: url("assets/fonts/Jua.woff2") format("woff2"); font-weight: 400; }
      :root { --ground: #ffffff; --ink: #111111; --bar: BAR_COLOR; --pop: POP_COLOR; }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1080px; height: 1920px; overflow: hidden; background: var(--ground); }
      #root { position: relative; width: 1080px; height: 1920px; background: var(--ground); font-family: "KR", sans-serif; color: var(--ink); word-break: keep-all; }
      #bar { position: absolute; left: 0; top: 0; width: 1080px; height: 64px; background: var(--bar); display: flex; align-items: center; justify-content: center; color: #fff; font-size: 50px; font-weight: 900; letter-spacing: -0.02em; }
      #title { position: absolute; left: 40px; right: 40px; top: 64px; height: 189px; display: flex; align-items: center; justify-content: center; text-align: center; font-family: "Soft", "KR", sans-serif; font-size: 54px; font-weight: 400; letter-spacing: -0.03em; }
      #rule { position: absolute; left: 0; width: 1080px; top: 253px; height: 3px; background: #d8d8d8; }
      .panel { position: absolute; left: 0; top: 256px; width: 1080px; height: 1088px; overflow: hidden; background: #000; }
      .panel img { position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; display: block; }
      .credit { position: absolute; left: 20px; top: 1300px; z-index: 4; max-width: 1040px; font-size: 24px; font-weight: 400; line-height: 1.3; color: #fff; padding: 3px 10px; border-radius: 6px; background: rgba(0,0,0,.55); }
      .cap { position: absolute; left: 120px; right: 120px; top: 1344px; height: 192px; display: flex; align-items: center; justify-content: center; text-align: center; font-family: "Soft", "KR", sans-serif; font-size: 42px; font-weight: 400; line-height: 1.35; }
      .recap { z-index: 3; }
      .recap-cr { z-index: 6; }
      .ad { position: absolute; left: 20px; top: 1216px; z-index: 7; max-width: 640px; text-align: left; font-size: 22px; font-weight: 400; line-height: 1.4; color: #fff; padding: 6px 12px; border-radius: 8px; background: rgba(0,0,0,.62); }
      .hl { position: absolute; left: 40px; top: 1154px; z-index: 5; }
      .hl span { display: inline-block; padding: 14px 34px; border-radius: 16px; background: var(--pop); color: #fff; font-size: 64px; font-weight: 900; box-shadow: 0 8px 24px rgba(0,0,0,.35); }
      #safe { position: absolute; left: 0; top: 1600px; width: 1080px; height: 320px; background: var(--ground); }
      #ment { position: absolute; left: 0; top: 1536px; width: 1080px; height: 64px; display: flex; align-items: center; justify-content: center; background: var(--bar); color: #fff; font-size: 36px; font-weight: 900; }"""


def build_html(cfg: dict, b: list[float]) -> str:
    scenes, recap = cfg["scenes"], cfg.get("recap", [])
    blocks, sounds, tweens = [], [], []
    for i, sc in enumerate(scenes, 1):
        rec_end = recap[-1]["to"] if (i == len(scenes) and recap) else None
        bl, so, tw = scene_parts(i, sc, b[i - 1], b[i], rec_end)
        blocks += bl; sounds += so; tweens += tw
    bl, so, tw = recap_parts(recap, b[len(scenes) - 1])
    blocks += bl; sounds += so; tweens += tw
    if cfg.get("ad_note", True):
        ad0 = b[len(scenes) - 1]
        blocks.append(f'      <p id="ad" class="clip ad" data-start="{ad0}" data-duration="{round(b[-1] - ad0, 3)}" '
                      f'data-track-index="11">{AD_NOTE}</p>')
    tweens.append('tl.fromTo("#capin1", {scale: 0.94}, {scale: 1, duration: 0.25, ease: "back.out(2)"}, 0);')
    total = b[-1]
    ment = cfg.get("ment", DEFAULT_MENT)
    variables = json.dumps([
        {"id": "channel", "type": "string", "label": "위 띠", "default": cfg["bar"]},
        {"id": "title", "type": "string", "label": "제목", "default": cfg["title"]},
        {"id": "ment", "type": "string", "label": "아래 띠", "default": ment},
    ], ensure_ascii=False)
    css = CSS.replace("BAR_COLOR", cfg.get("bar_color", BAR_COLOR)).replace("POP_COLOR", cfg.get("pop_color", POP_COLOR))
    nl = "\n"
    return f'''<!doctype html>
<html lang="ko" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
{css}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920" data-composition-variables='{esc(variables)}'>
      <div id="bar" class="clip" data-start="0" data-duration="{total}" data-track-index="0"><span data-var-text="channel">{esc(cfg["bar"])}</span></div>
      <h1 id="title" class="clip" data-start="0" data-duration="{total}" data-track-index="0" data-var-text="title">{esc(cfg["title"])}</h1>
      <div id="rule" class="clip" data-start="0" data-duration="{total}" data-track-index="0"></div>
      <p id="ment" class="clip" data-start="0" data-duration="{total}" data-track-index="0" data-var-text="ment">{esc(ment)}</p>
{nl.join(blocks)}
      <audio id="narration" class="clip" src="assets/audio/narration.wav" data-start="0" data-duration="{total}" data-track-index="4"></audio>
{nl.join(sounds)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {(nl + "      ").join(tweens)}
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
'''


def jua_font() -> Path:
    if not JUA_CACHE.is_file():
        JUA_CACHE.parent.mkdir(parents=True, exist_ok=True)
        print(f"Jua 글꼴을 내려받습니다(Google Fonts, OFL): {JUA_URL}")
        urllib.request.urlretrieve(JUA_URL, JUA_CACHE)
    return JUA_CACHE


def subset_fonts(page: str, hf: Path) -> None:
    from fontTools import subset

    fonts = hf / "assets/fonts"
    fonts.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location("frame2_hyperframes", HERE / "frame2_hyperframes.py")
    f2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(f2)
    f2.subset_fonts(page, fonts, None, None)
    opts = subset.Options()
    opts.flavor = "woff2"
    font = subset.load_font(str(jua_font()), opts)
    sub = subset.Subsetter(opts)
    sub.populate(text=page)
    sub.subset(font)
    subset.save_font(font, str(fonts / "Jua.woff2"), opts)


def ensure_workspace(hf: Path) -> None:
    if (hf / "hyperframes.json").is_file():
        return
    cmd = ["hyperframes", "init", hf.name, "--skip-skills", "--non-interactive", "--resolution", "portrait"]
    subprocess.run(cmd, cwd=hf.parent, check=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="기본1 형식 HyperFrames 작업 폴더 만들기")
    ap.add_argument("project", type=Path, help="OpenMontage 프로젝트 폴더(projects/<id>)")
    args = ap.parse_args(argv)
    project = args.project.resolve()
    try:
        cfg = check_config(json.loads((project / "basic1.json").read_text()))
        timings = json.loads((project / "assets/audio/narration_timings.json").read_text())
        b = boundaries(timings, len(cfg["scenes"]), float(cfg.get("end_tail", END_TAIL)))
        hf = project / "hf"
        ensure_workspace(hf)
        prepare_media(cfg, project, hf)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"기본1 형식을 만들지 못했습니다: {error}", file=sys.stderr)
        return 1
    page = build_html(cfg, b)
    (hf / "index.html").write_text(page)
    subset_fonts(page, hf)
    print(json.dumps({"workspace": str(hf), "scenes": b, "total": b[-1]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
