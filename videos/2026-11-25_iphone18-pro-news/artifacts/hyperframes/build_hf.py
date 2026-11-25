"""아이폰18 프로 쇼츠: 원본(뉴스 카드형) 틀로 HyperFrames index.html을 만든다."""
import importlib.util, json, shutil, subprocess
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter

HERE = Path(__file__).parent
HF = HERE / "hf"
SRC = HERE / "assets/images/src"
TPL = Path("/Users/seungtaepc/Downloads/reels/.claude/skills/reels/templates/frame2_hyperframes.py")
TITLE = "아이폰18 프로, 뭐가 달라졌나?"
CHANNEL = "아이폰18"
MENT = "프로필 링크에서 확인하세요"
END_TAIL = 0.5  # 마지막 말 끝 + 0.5초에서 끊는다(제작후분석소 검수 ①-2)
CONTAIN = {"w06"}  # 넓게 잘라 위아래를 검게 둔다(섬과 상태 표시줄이 함께 보이게)
CROPS = {"w05": (0.0, 0.18, 1.0, 1.0), "w06": (0.16, 0.02, 0.84, 0.40)}  # (왼, 위, 오른, 아래) 비율. ①-4 글자 잘림, ①-5 일본어 위젯
POPS = {4: ("가변 조리개", 0.9), 5: ("최대 40%", 2.6), 6: ("1199달러", 1.6)}  # 장면: (강조 글자, 장면 시작 뒤 초) ①-6
SPLIT = {7: ("w01", "50% 50%", "Olgierd Rudak")}  # 장면: 뒤 절반에 쓸 두 번째 사진 (제작후분석소 3-4)
PUNCH_MIN = 3.5  # 이보다 긴 장면은 가운데서 한 번 더 다가간다 ①-7

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
    return starts + [round(t["sections"][-1]["end"] + END_TAIL, 3)]


def prepare_media():
    (HF / "assets/img").mkdir(parents=True, exist_ok=True)
    (HF / "assets/audio").mkdir(parents=True, exist_ok=True)
    names = [n for n, *_ in SCENES] + [v[0] for v in SPLIT.values()]
    for name in names:  # 변형: 긴 변 1600으로 줄이고 대비·채도를 살짝 올린다
        im = Image.open(SRC / f"{name}.jpg").convert("RGB")
        if name in CROPS:
            l, t, r, b = CROPS[name]
            im = im.crop((int(l * im.width), int(t * im.height), int(r * im.width), int(b * im.height)))
        im.thumbnail((1600, 1600))
        im = ImageEnhance.Contrast(im).enhance(1.08)
        im = ImageEnhance.Color(im).enhance(1.12)
        im.save(HF / f"assets/img/{name}.jpg", quality=90)
        if name in CONTAIN:
            bg = im.resize((540, int(540 * im.height / im.width))).filter(ImageFilter.GaussianBlur(18))
            ImageEnhance.Brightness(bg).enhance(0.55).save(HF / f"assets/img/{name}_bg.jpg", quality=85)
    shutil.copyfile(HERE / "assets/audio/narration_norm.wav", HF / "assets/audio/narration.wav")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                    "sine=frequency=1400:duration=0.07", "-af",
                    "afade=t=out:st=0.01:d=0.06,volume=0.35", HF / "assets/audio/pop.wav"], check=True)


def html(b):
    scenes, caps, pops, tweens = [], [], [], []
    for i, (name, focus, author, (l1, l2), d) in enumerate(SCENES, 1):
        s, e = b[i - 1], b[i]
        dur = round(e - s, 3)
        parts = [(name, focus, author, s, e, "")]
        if i in SPLIT:
            mid = round(s + dur / 2, 3)
            n2, f2, a2 = SPLIT[i]
            parts = [(name, focus, author, s, mid, ""), (n2, f2, a2, mid, e, "b")]
        for pn, pf, pa, ps, pe, sfx in parts:
            pd = round(pe - ps, 3)
            bg = f'<img id="bg{i}{sfx}" class="bg" src="assets/img/{pn}_bg.jpg" alt="" />' if pn in CONTAIN else ""
            fit = "contain" if pn in CONTAIN else "cover"
            scenes.append(f'''      <div id="img{i}{sfx}" class="clip panel" data-start="{ps}" data-duration="{pd}" data-track-index="1">
        {bg}<img id="ph{i}{sfx}" src="assets/img/{pn}.jpg" style="object-position:{pf};object-fit:{fit}" alt="" />
      </div>
      <p id="cr{i}{sfx}" class="clip credit" data-start="{ps}" data-duration="{pd}" data-track-index="2">사진: {pa} · Wikimedia Commons · CC BY-SA 4.0</p>''')
            if sfx:
                pops.append(f'      <audio id="pop{i}b" class="clip" src="assets/audio/pop.wav" data-start="{ps}" data-duration="0.1" data-track-index="5"></audio>')
                tweens.append(f'tl.fromTo("#ph{i}b", {{scale: 1.0, xPercent: {1.5 * d}}}, {{scale: 1.09, xPercent: {-1.5 * d}, duration: {pd}, ease: "none"}}, {ps});')
        caps.append(f'''      <div id="cap{i}" class="clip cap" data-start="{s}" data-duration="{dur}" data-track-index="3"><div id="capin{i}"><p>{l1}</p><p>{l2}</p></div></div>''')
        if i > 1:
            pops.append(f'      <audio id="pop{i}" class="clip" src="assets/audio/pop.wav" data-start="{s}" data-duration="0.1" data-track-index="5"></audio>')
        if i in SPLIT:
            tweens.append(f'tl.fromTo("#ph{i}", {{scale: 1.0, xPercent: {-1.5 * d}}}, {{scale: 1.09, xPercent: {1.5 * d}, duration: {round(dur / 2, 3)}, ease: "none"}}, {s});')
        elif dur > PUNCH_MIN:
            half = round(dur / 2, 3)
            tweens.append(f'tl.fromTo("#ph{i}", {{scale: 1.0, xPercent: {-1.5 * d}, yPercent: 0}}, {{scale: 1.05, xPercent: 0, duration: {half}, ease: "none"}}, {s});')
            tweens.append(f'tl.to("#ph{i}", {{scale: 1.16, xPercent: {2 * d}, yPercent: -3, duration: 0.3, ease: "power2.out"}}, {round(s + half, 3)});')
            tweens.append(f'tl.to("#ph{i}", {{scale: 1.2, duration: {round(dur - half - 0.3, 3)}, ease: "none"}}, {round(s + half + 0.3, 3)});')
        else:
            tweens.append(f'tl.fromTo("#ph{i}", {{scale: 1.0, xPercent: {-1.5 * d}}}, {{scale: 1.09, xPercent: {1.5 * d}, duration: {dur}, ease: "none"}}, {s});')
        if i in POPS:
            word, at = POPS[i]
            t0 = round(s + at, 3)
            scenes.append(f'      <div id="hl{i}" class="clip hl" data-start="{t0}" data-duration="{round(e - t0, 3)}" data-track-index="6"><span id="hlin{i}">{word}</span></div>')
            pops.append(f'      <audio id="hpop{i}" class="clip" src="assets/audio/pop.wav" data-start="{t0}" data-duration="0.1" data-track-index="7"></audio>')
            tweens.append(f'tl.fromTo("#hlin{i}", {{scale: 0.3, rotation: -14}}, {{scale: 1, rotation: -6, duration: 0.3, ease: "back.out(2.4)"}}, {t0});')
    tweens.append('tl.fromTo("#capin1", {scale: 0.94}, {scale: 1, duration: 0.25, ease: "back.out(2)"}, 0);')  # 0초부터 보인다(①-1)
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
      #bar {{ position: absolute; left: 0; top: 0; width: 1080px; height: 120px; background: var(--bar); display: flex; align-items: center; justify-content: center; color: #fff; font-size: 84px; font-weight: 900; letter-spacing: -0.02em; }}
      #title {{ position: absolute; left: 40px; right: 40px; top: 120px; height: 357px; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 66px; font-weight: 900; letter-spacing: -0.03em; }}
      #rule {{ position: absolute; left: 0; width: 1080px; top: 477px; height: 3px; background: #d8d8d8; }}
      .panel {{ position: absolute; left: 0; top: 480px; width: 1080px; height: 960px; overflow: hidden; background: #000; }}
      .panel img {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; display: block; }}
      .credit {{ position: absolute; right: 20px; top: 1398px; z-index: 4; font-size: 24px; font-weight: 400; color: #fff; text-shadow: 0 1px 4px rgba(0,0,0,.9); }}
      .cap {{ position: absolute; left: 50px; right: 50px; top: 1440px; height: 360px; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 60px; font-weight: 700; line-height: 1.5; }}
      .hl {{ position: absolute; left: 50px; top: 1250px; z-index: 5; }}
      .hl span {{ display: inline-block; padding: 14px 34px; border-radius: 16px; background: #1e63ff; color: #fff; font-size: 64px; font-weight: 900; box-shadow: 0 8px 24px rgba(0,0,0,.35); }}
      #ment {{ position: absolute; left: 0; top: 1800px; width: 1080px; height: 120px; display: flex; align-items: center; justify-content: center; background: var(--bar); color: #fff; font-size: 54px; font-weight: 900; }}
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
