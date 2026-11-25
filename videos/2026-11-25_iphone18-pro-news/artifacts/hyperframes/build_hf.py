"""아이폰18 프로 쇼츠: 원본(뉴스 카드형) 틀로 HyperFrames index.html을 만든다."""
import importlib.util, json, shutil, subprocess
from pathlib import Path
from PIL import Image, ImageEnhance

HERE = Path(__file__).parent
HF = HERE / "hf"
SRC = HERE / "assets/images/src"
TPL = Path("/Users/seungtaepc/Downloads/reels/.claude/skills/reels/templates/frame2_hyperframes.py")
TITLE = "아이폰18 프로, 뭐가 달라졌나?"
CHANNEL = "아이폰18"
MENT = "프로필 링크에서 확인하세요"
END_HOLD = 1.4

SCENES = [  # (사진, 초점, 작가, 자막 두 줄, 이동 방향)
    ("w11", "50% 40%", "茅野ふたば", ("아이폰18 프로가", "일반 아이폰18 없이 먼저 나왔다"), 1),
    ("w08", "50% 50%", "Olgierd Rudak", ("애플 발표와 리뷰를", "짧게 정리하면 이렇다"), -1),
    ("w06", "40% 30%", "Kyu3a", ("다이내믹 아일랜드가", "처음으로 작아졌다"), 1),
    ("w05", "45% 45%", "Kyu3a", ("아이폰 최초로 조리개를", "바꾸는 카메라가 들어갔다"), -1),
    ("w03", "50% 30%", "Farragutful", ("칩은 A20 프로, 애플은 전작보다", "최대 40% 빠르다고 한다"), 1),
    ("w10", "50% 45%", "Olgierd Rudak", ("대신 미국 가격은 1199달러로", "100달러 올랐다"), -1),
    ("w09", "55% 75%", "Olgierd Rudak", ("리뷰는 카메라를 칭찬했지만, 17 프로에서", "바꿀 이유는 약하다는 평도 있다"), 1),
    ("w07", "50% 50%", "Kyu3a", ("과연 올해", "갈아탈 만한 아이폰일까?"), -1),
]


def boundaries():
    t = json.loads((HERE / "assets/audio/narration_timings.json").read_text())
    starts = [0.0] + [round(s["start"] - 0.3, 3) for s in t["sections"][1:]]
    return starts + [round(t["total"] + END_HOLD, 3)]


def prepare_media():
    (HF / "assets/img").mkdir(parents=True, exist_ok=True)
    (HF / "assets/audio").mkdir(parents=True, exist_ok=True)
    for name, *_ in SCENES:  # 변형: 긴 변 1600으로 줄이고 대비·채도를 살짝 올린다
        im = Image.open(SRC / f"{name}.jpg").convert("RGB")
        im.thumbnail((1600, 1600))
        im = ImageEnhance.Contrast(im).enhance(1.08)
        im = ImageEnhance.Color(im).enhance(1.12)
        im.save(HF / f"assets/img/{name}.jpg", quality=90)
    shutil.copyfile(HERE / "assets/audio/narration_norm.wav", HF / "assets/audio/narration.wav")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                    "sine=frequency=1400:duration=0.07", "-af",
                    "afade=t=out:st=0.01:d=0.06,volume=0.35", HF / "assets/audio/pop.wav"], check=True)


def html(b):
    scenes, caps, pops, tweens = [], [], [], []
    for i, (name, focus, author, (l1, l2), d) in enumerate(SCENES, 1):
        s, e = b[i - 1], b[i]
        dur = round(e - s, 3)
        scenes.append(f'''      <div id="img{i}" class="clip panel" data-start="{s}" data-duration="{dur}" data-track-index="1">
        <img id="ph{i}" src="assets/img/{name}.jpg" style="object-position:{focus}" alt="" />
      </div>
      <p id="cr{i}" class="clip credit" data-start="{s}" data-duration="{dur}" data-track-index="2">사진: {author} · Wikimedia Commons · CC BY-SA 4.0</p>''')
        caps.append(f'''      <div id="cap{i}" class="clip cap" data-start="{s}" data-duration="{dur}" data-track-index="3"><div id="capin{i}"><p>{l1}</p><p>{l2}</p></div></div>''')
        if i > 1:
            pops.append(f'      <audio id="pop{i}" class="clip" src="assets/audio/pop.wav" data-start="{s}" data-duration="0.1" data-track-index="5"></audio>')
        tweens.append(f'tl.fromTo("#ph{i}", {{scale: 1.0, xPercent: {-1.5 * d}}}, {{scale: 1.09, xPercent: {1.5 * d}, duration: {dur}, ease: "none"}}, {s});')
    tweens.append('tl.fromTo("#capin1", {scale: 0.86, opacity: 0}, {scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2)"}, 0);')
    total = b[-1]
    return f'''<!doctype html>
<html lang="ko" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "KR"; src: url("assets/fonts/KR-Regular.woff2") format("woff2"); font-weight: 400; }}
      @font-face {{ font-family: "KR"; src: url("assets/fonts/KR-Bold.woff2") format("woff2"); font-weight: 700 900; }}
      :root {{ --ground: #ffffff; --ink: #111111; --bar: #ff7a1a; --muted: #8a8a8a; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: var(--ground); }}
      #root {{ position: relative; width: 1080px; height: 1920px; background: var(--ground); font-family: "KR", sans-serif; color: var(--ink); word-break: keep-all; }}
      #bar {{ position: absolute; left: 0; top: 0; width: 1080px; height: 330px; background: var(--bar); display: flex; align-items: center; justify-content: center; color: #fff; font-size: 132px; font-weight: 900; letter-spacing: -0.02em; }}
      #title {{ position: absolute; left: 40px; right: 40px; top: 330px; height: 307px; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 66px; font-weight: 900; letter-spacing: -0.03em; }}
      #rule {{ position: absolute; left: 0; width: 1080px; top: 637px; height: 3px; background: #d8d8d8; }}
      .panel {{ position: absolute; left: 0; top: 640px; width: 1080px; height: 640px; overflow: hidden; background: #000; }}
      .panel img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
      .credit {{ position: absolute; right: 24px; top: 1290px; font-size: 24px; font-weight: 400; color: var(--muted); }}
      .cap {{ position: absolute; left: 50px; right: 50px; top: 1340px; height: 300px; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 60px; font-weight: 700; line-height: 1.5; }}
      #ment {{ position: absolute; left: 50%; top: 1680px; transform: translateX(-50%); white-space: nowrap; padding: 22px 54px; border-radius: 999px; background: var(--bar); color: #fff; font-size: 50px; font-weight: 900; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920" data-composition-variables='[{{"id":"channel","type":"string","label":"채널 이름","default":"{CHANNEL}"}},{{"id":"title","type":"string","label":"제목","default":"{TITLE}"}},{{"id":"ment","type":"string","label":"고정 멘트","default":"{MENT}"}}]'>
      <div id="bar" class="clip" data-start="0" data-duration="{total}" data-track-index="0"><span data-var-text="channel">{CHANNEL}</span></div>
      <h1 id="title" class="clip" data-start="0" data-duration="{total}" data-track-index="0" data-var-text="title">{TITLE}</h1>
      <div id="rule" class="clip" data-start="0" data-duration="{total}" data-track-index="0"></div>
      <p id="ment" class="clip" data-start="0" data-duration="{total}" data-track-index="0" data-var-text="ment">{MENT}</p>
{chr(10).join(scenes)}
{chr(10).join(caps)}
      <audio id="narration" class="clip" src="assets/audio/narration.wav" data-start="0" data-duration="{total}" data-track-index="4"></audio>
{chr(10).join(pops)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {(chr(10) + "      ").join(tweens)}
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
'''


def main():
    b = boundaries()
    prepare_media()
    page = html(b)
    (HF / "index.html").write_text(page)
    spec = importlib.util.spec_from_file_location("f2", TPL)
    f2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(f2)
    (HF / "assets/fonts").mkdir(parents=True, exist_ok=True)
    f2.subset_fonts(page, HF / "assets/fonts", None, None)
    print("scenes", b)


main()
