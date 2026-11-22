"""Build the HyperFrames (2번 프레임) version of the winter-bath reel.

Same script, narration, music, cut timings, captions and ad disclosure as the
Remotion render; only the rendering framework and motion differ.
"""
import json
import sys
from pathlib import Path

P = Path(sys.argv[1])
WS = P / "hyperframes"
comp = json.loads((P / "artifacts/composition.json").read_text())
timings = json.loads((P / "assets/audio/narration_timings.json").read_text())

W, H, FPS = 1080, 1920, 30
TOTAL = 34.5
EPS = 0.02  # keep same-track clips from touching

BG, FG, ACCENT, WARN, INFO = "#0F1B26", "#F4F7FA", "#FF8A3D", "#FF5A5F", "#5AB0FF"


def f(v):
    return f"{float(v):.3f}".rstrip("0").rstrip(".")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


cuts = {c["id"]: c for c in comp["cuts"]}
clips, tweens = [], []


def scene(cid, inner, extra_class=""):
    c = cuts[cid]
    start, end = c["in_seconds"], c["out_seconds"]
    dur = end - start - (EPS if end < TOTAL else 0)
    clips.append(
        f'<section id="{cid}" class="clip scene {extra_class}" data-start="{f(start)}" '
        f'data-duration="{f(dur)}" data-track-index="1">{inner}</section>'
    )
    # generic exit: fade the scene's content out over the last 0.22s
    if end < TOTAL:
        tweens.append(
            f'tl.to("#{cid} .stage", {{opacity: 0, y: -30, duration: 0.22, ease: "power2.in"}}, {f(end - 0.24)});'
        )
    return start, end


def counter_keys(el_id, start, dur, a, b, fmt="{:,}", ease_pow=3):
    """Seek-safe count-up: one tl.set per frame (no onUpdate state)."""
    n = max(2, int(round(dur * FPS)))
    out = []
    last = None
    for i in range(n + 1):
        x = i / n
        e = 1 - (1 - x) ** ease_pow
        v = int(round(a + (b - a) * e))
        if v == last:
            continue
        last = v
        out.append(
            f'tl.set("#{el_id}", {{textContent: "{fmt.format(v)}"}}, {f(start + i / FPS)});'
        )
    return out


# ---------------------------------------------------------------- c1 hero
s, e = scene("c1", f"""
<div class="stage hero">
  <div class="pill" id="c1-pill">겨울 목욕</div>
  <svg class="clock" id="c1-clock" viewBox="0 0 200 200" width="260" height="260">
    <circle cx="100" cy="100" r="88" fill="none" stroke="{ACCENT}" stroke-width="10"/>
    <g id="c1-hand-wrap"><rect id="c1-hand" x="95" y="30" width="10" height="74" rx="5" fill="{FG}"/></g>
    <circle cx="100" cy="100" r="9" fill="{ACCENT}"/>
  </svg>
  <h1 class="hero-title"><span class="w" id="c1-w1">온도보다</span> <span class="w" id="c1-w2">무서운 건</span></h1>
  <div class="hero-big" id="c1-big">시간</div>
</div>""")
tweens += [
    f'tl.from("#c1-pill", {{y: -40, opacity: 0, duration: 0.45, ease: "power3.out"}}, {f(s + 0.05)});',
    f'tl.from("#c1-clock", {{scale: 0.6, opacity: 0, duration: 0.5, ease: "back.out(1.8)"}}, {f(s + 0.15)});',
    f'tl.fromTo("#c1-hand", {{rotation: 0}}, {{rotation: 540, duration: {f(e - s)}, ease: "none", transformOrigin: "50% 95%"}}, {f(s)});',
    f'tl.from("#c1-w1", {{y: 60, opacity: 0, duration: 0.45, ease: "power3.out"}}, {f(s + 0.35)});',
    f'tl.from("#c1-w2", {{y: 60, opacity: 0, duration: 0.45, ease: "power3.out"}}, {f(s + 0.7)});',
    f'tl.from("#c1-big", {{scale: 2.2, opacity: 0, duration: 0.55, ease: "expo.out"}}, {f(s + 1.55)});',
]


def callout(cid, kind, title, text, icon):
    color = WARN if kind == "warning" else INFO
    s, e = scene(cid, f"""
<div class="stage callout">
  <div class="label" style="color:{color}" id="{cid}-label"><span class="icon" style="background:{color}">{icon}</span>{esc(title)}</div>
  <div class="bar" id="{cid}-bar" style="background:{color}"></div>
  <p class="body" id="{cid}-body">{esc(text)}</p>
</div>""")
    tweens.extend([
        f'tl.from("#{cid}-label", {{x: -80, opacity: 0, duration: 0.4, ease: "power3.out"}}, {f(s + 0.05)});',
        f'tl.from("#{cid}-bar", {{scaleX: 0, duration: 0.5, ease: "power2.out", transformOrigin: "0% 50%"}}, {f(s + 0.2)});',
        f'tl.from("#{cid}-body", {{y: 50, opacity: 0, duration: 0.5, ease: "power3.out"}}, {f(s + 0.35)});',
    ])
    return s, e


# ---------------------------------------------------------------- c2 myth (+ strike)
s, e = callout("c2", "warning", "흔한 오해", "뜨거운 물에 오래 담가야 피로가 풀린다?", "!")
clips[-1] = clips[-1].replace(
    '<p class="body" id="c2-body">뜨거운 물에 오래 담가야 피로가 풀린다?</p>',
    '<div class="body" id="c2-body">'
    '<div class="sline"><span class="stext">뜨거운 물에 오래 담가야</span><div class="strike" id="c2-strike1"></div></div>'
    '<div class="sline"><span class="stext">피로가 풀린다?</span><div class="strike" id="c2-strike2"></div></div>'
    '</div>',
).replace("</div>\n</div>", "</div><div class=\"stamp\" id=\"c2-stamp\">오해</div>\n</div>")
tweens += [
    f'tl.from("#c2-strike1", {{scaleX: 0, duration: 0.35, ease: "power2.inOut", transformOrigin: "0% 50%"}}, {f(e - 1.35)});',
    f'tl.from("#c2-strike2", {{scaleX: 0, duration: 0.3, ease: "power2.inOut", transformOrigin: "0% 50%"}}, {f(e - 1.05)});',
    f'tl.to("#c2-body", {{opacity: 0.55, duration: 0.3}}, {f(e - 1.35)});',
    f'tl.from("#c2-stamp", {{scale: 2.4, rotation: -18, opacity: 0, duration: 0.35, ease: "back.out(2)"}}, {f(e - 0.95)});',
]

# ---------------------------------------------------------------- c3 info
callout("c3", "info", "일본 소비자청", "뜨거운 탕에 오래 있는 것, 겨울 욕조 사고의 원인", "i")


# ---------------------------------------------------------------- c4 stat 7,776
def stat(cid, num_html, sub, extra=""):
    s, e = scene(cid, f"""
<div class="stage stat">
  {extra}
  <div class="stat-num" id="{cid}-num">{num_html}</div>
  <div class="stat-rule" id="{cid}-rule"></div>
  <div class="stat-sub" id="{cid}-sub">{"".join(f'<div>{esc(x)}</div>' for x in sub.split("|"))}</div>
</div>""")
    tweens.extend([
        f'tl.from("#{cid}-num", {{scale: 0.7, opacity: 0, duration: 0.45, ease: "back.out(1.6)"}}, {f(s + 0.05)});',
        f'tl.from("#{cid}-rule", {{scaleX: 0, duration: 0.5, ease: "power2.out"}}, {f(s + 0.3)});',
        f'tl.from("#{cid}-sub", {{y: 30, opacity: 0, duration: 0.45, ease: "power3.out"}}, {f(s + 0.45)});',
    ])
    return s, e


s, e = stat("c4", '<span id="c4-count">0</span><span class="unit">명</span>',
            "2024년 일본 욕조 익사자|65세 이상 약 95%")
tweens += counter_keys("c4-count", s + 0.1, 1.3, 0, 7776)

# ---------------------------------------------------------------- c5 body temp (thermometer)
s, e = callout("c5", "warning", "오래 있을수록", "체온이 올라 의식이 흐려질 수 있습니다", "!")
clips[-1] = clips[-1].replace("</p>\n</div>", f"""</p>
  <div class="thermo" id="c5-thermo"><div class="thermo-tube"><div class="thermo-fill" id="c5-fill"></div></div><div class="thermo-bulb" id="c5-bulb"></div></div>
</div>""")
tweens += [
    f'tl.from("#c5-thermo", {{opacity: 0, y: 40, duration: 0.4, ease: "power2.out"}}, {f(s + 0.5)});',
    f'tl.fromTo("#c5-fill", {{scaleY: 0.25, backgroundColor: "{ACCENT}"}}, {{scaleY: 0.95, backgroundColor: "{WARN}", duration: 2.4, ease: "power1.inOut", transformOrigin: "50% 100%"}}, {f(s + 0.7)});',
    f'tl.fromTo("#c5-bulb", {{backgroundColor: "{ACCENT}"}}, {{backgroundColor: "{WARN}", duration: 2.4, ease: "power1.inOut"}}, {f(s + 0.7)});',
]

# ---------------------------------------------------------------- c6 blood pressure drop
s, e = callout("c6", "warning", "일어설 때", "혈압이 뚝 떨어져 쓰러질 수 있습니다", "!")
clips[-1] = clips[-1].replace("</p>\n</div>", f"""</p>
  <div class="drop"><svg id="c6-arrow" viewBox="0 0 120 200" width="150" height="250"><rect x="45" y="0" width="30" height="120" rx="8" fill="{WARN}"/><polygon points="10,110 110,110 60,190" fill="{WARN}"/></svg></div>
</div>""")
tweens += [
    f'tl.fromTo("#c6-arrow", {{y: -160, opacity: 0}}, {{y: 0, opacity: 1, duration: 0.7, ease: "bounce.out"}}, {f(s + 0.8)});',
]

# ---------------------------------------------------------------- c7 41°C
s, e = stat("c7", '<span id="c7-count">0</span><span class="unit">℃ 이하</span>', "물 온도",
            extra='<div class="tag" id="c7-tag">기억하세요 ①</div>')
tweens += counter_keys("c7-count", s + 0.1, 0.9, 0, 41, fmt="{}")
tweens.append(f'tl.from("#c7-tag", {{y: -30, opacity: 0, duration: 0.35, ease: "power2.out"}}, {f(s)});')

# ---------------------------------------------------------------- c8 10분 (clock)
s, e = stat("c8", '<span id="c8-count">0</span><span class="unit">분 이내</span>', "담그는 시간",
            extra=f'<div class="tag" id="c8-tag">기억하세요 ②</div>')
tweens += counter_keys("c8-count", s + 0.1, 0.6, 0, 10, fmt="{}")
tweens.append(f'tl.from("#c8-tag", {{y: -30, opacity: 0, duration: 0.35, ease: "power2.out"}}, {f(s)});')

# ---------------------------------------------------------------- c9 warm the bathroom
s, e = scene("c9", f"""
<div class="stage textcard">
  <div class="tag" id="c9-tag">기억하세요 ③</div>
  <div class="check" id="c9-check"><svg viewBox="0 0 100 100" width="150" height="150"><circle cx="50" cy="50" r="46" fill="{ACCENT}"/><polyline points="28,52 44,68 74,36" fill="none" stroke="{BG}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
  <p class="big-line" id="c9-l1">들어가기 전,</p>
  <p class="big-line accent" id="c9-l2">욕실부터 데우기</p>
</div>""")
tweens += [
    f'tl.from("#c9-tag", {{y: -30, opacity: 0, duration: 0.35, ease: "power2.out"}}, {f(s)});',
    f'tl.from("#c9-check", {{scale: 0, rotation: -90, duration: 0.5, ease: "back.out(2)"}}, {f(s + 0.1)});',
    f'tl.from("#c9-l1", {{y: 40, opacity: 0, duration: 0.4, ease: "power3.out"}}, {f(s + 0.3)});',
    f'tl.from("#c9-l2", {{y: 40, opacity: 0, duration: 0.4, ease: "power3.out"}}, {f(s + 0.55)});',
]

# ---------------------------------------------------------------- c10 end card + disclosure
c10 = cuts["c10"]
s, e = scene("c10", f"""
<div class="stage endcard">
  <p class="end-title" id="c10-title">{esc(c10['title'])}</p>
  <div class="end-arrow" id="c10-arrow"><svg viewBox="0 0 100 100" width="120" height="120"><polyline points="20,35 50,65 80,35" fill="none" stroke="{ACCENT}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
  <p class="disclosure" id="c10-disc">{esc(c10['text'])}</p>
</div>""")
bounces = int((e - s - 1.0) // 0.9) - 1
tweens += [
    f'tl.from("#c10-title", {{y: 50, opacity: 0, duration: 0.5, ease: "power3.out"}}, {f(s + 0.05)});',
    f'tl.from("#c10-disc", {{opacity: 0, duration: 0.6, ease: "power1.out"}}, {f(s + 0.4)});',
    f'tl.fromTo("#c10-arrow", {{y: 0}}, {{y: 26, duration: 0.45, ease: "sine.inOut", yoyo: true, repeat: {max(1, bounces * 2 - 1)}}}, {f(s + 0.6)});',
]

# ---------------------------------------------------------------- captions (track 5)
words = comp["captions"]
sections = timings["sections"]


def section_of(w):
    t = w["startMs"] / 1000
    for i, sec in enumerate(sections):
        if sec["start"] - 0.05 <= t <= sec["end"] + 0.05:
            return i
    return -1


pages, cur, cur_sec = [], [], None
for w in words:
    sec = section_of(w)
    if cur and (sec != cur_sec or len(cur) == 3):
        pages.append(cur)
        cur = []
    cur.append(w)
    cur_sec = sec
if cur:
    pages.append(cur)

for pi, page in enumerate(pages):
    start = page[0]["startMs"] / 1000
    end = page[-1]["endMs"] / 1000
    nxt = pages[pi + 1][0]["startMs"] / 1000 if pi + 1 < len(pages) else None
    # keep a page up through short gaps inside a sentence, never overlapping the next page
    if nxt is not None and nxt - end < 0.35:
        end = nxt - EPS
    spans = " ".join(
        f'<span class="cw" id="cap{pi}-{wi}">{esc(w["word"])}</span>' for wi, w in enumerate(page)
    )
    clips.append(
        f'<div id="cap{pi}" class="clip caption" data-start="{f(start)}" data-duration="{f(end - start)}" '
        f'data-track-index="5"><div class="cap-box" id="cap{pi}-box">{spans}</div></div>'
    )
    tweens.append(f'tl.from("#cap{pi}-box", {{y: 24, opacity: 0, duration: 0.16, ease: "power2.out"}}, {f(start)});')
    for wi, w in enumerate(page):
        ws_, we_ = w["startMs"] / 1000, w["endMs"] / 1000
        tweens.append(f'tl.to("#cap{pi}-{wi}", {{color: "{ACCENT}", scale: 1.08, duration: 0.08}}, {f(ws_)});')
        tweens.append(f'tl.to("#cap{pi}-{wi}", {{color: "{FG}", scale: 1, duration: 0.08}}, {f(max(ws_ + 0.09, we_ - 0.04))});')

# ---------------------------------------------------------------- background + progress
bg_clip = (
    f'<div id="bg" class="clip" data-start="0" data-duration="{f(TOTAL)}" data-track-index="0">'
    '<div class="bg-fill"></div><div class="glow g1" id="glow1"></div><div class="glow g2" id="glow2"></div>'
    '<div class="progress"><div class="progress-fill" id="progress-fill"></div></div></div>'
)
glow_cycles = int(TOTAL // 6)
tweens = [
    f'tl.fromTo("#glow1", {{y: 0, scale: 1}}, {{y: -120, scale: 1.15, duration: 3, ease: "sine.inOut", yoyo: true, repeat: {glow_cycles * 2 - 1}}}, 0);',
    f'tl.fromTo("#glow2", {{y: 0, scale: 1.1}}, {{y: 100, scale: 0.95, duration: 3, ease: "sine.inOut", yoyo: true, repeat: {glow_cycles * 2 - 1}}}, 0);',
    f'tl.fromTo("#progress-fill", {{scaleX: 0}}, {{scaleX: 1, duration: {f(TOTAL)}, ease: "none"}}, 0);',
    # music fade in / out (runtime probes volume keyframes)
    f'tl.fromTo("#bgm", {{volume: 0}}, {{volume: 0.07, duration: 1.5, ease: "none"}}, 0);',
    f'tl.to("#bgm", {{volume: 0, duration: 2.5, ease: "none"}}, {f(TOTAL - 2.5)});',
] + tweens

audio = (
    f'<audio id="nar" src="assets/narration_norm.wav" data-start="0" data-duration="{f(timings["total"])}" '
    f'data-track-index="10" data-volume="1"></audio>'
    f'<audio id="bgm" src="assets/bgm.mp3" data-start="0" data-duration="{f(TOTAL)}" '
    f'data-track-index="11" data-volume="0.07"></audio>'
)

CSS = f"""
@font-face {{ font-family:"HF Noto KR"; src:url("fonts/NotoSansKR-Regular.woff2") format("woff2"); font-weight:400; font-style:normal; }}
@font-face {{ font-family:"HF Noto KR"; src:url("fonts/NotoSansKR-Bold.woff2") format("woff2"); font-weight:700 900; font-style:normal; }}
:root {{ --bg:{BG}; --fg:{FG}; --accent:{ACCENT}; --warn:{WARN}; --info:{INFO}; }}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg);
  font-family:"HF Noto KR",sans-serif; word-break:keep-all; }}
#root {{ position:relative; width:{W}px; height:{H}px; overflow:hidden; }}
.clip {{ position:absolute; inset:0; }}
.bg-fill {{ position:absolute; inset:0; background:radial-gradient(120% 80% at 50% 0%, #1B3042 0%, var(--bg) 60%); }}
.glow {{ position:absolute; width:760px; height:760px; border-radius:50%; opacity:0.22; }}
.g1 {{ left:-260px; top:220px; background:radial-gradient(circle, var(--accent) 0%, rgba(255,138,61,0) 70%); }}
.g2 {{ right:-300px; top:980px; background:radial-gradient(circle, var(--info) 0%, rgba(90,176,255,0) 70%); }}
.progress {{ position:absolute; left:80px; right:80px; top:120px; height:8px; border-radius:4px; background:rgba(244,247,250,0.14); }}
.progress-fill {{ display:block; width:100%; height:100%; border-radius:4px; background:var(--accent); transform-origin:0% 50%; }}
.scene {{ display:flex; align-items:center; justify-content:center; padding:180px 90px 500px; }}
.stage {{ width:100%; display:flex; flex-direction:column; align-items:center; text-align:center; }}
.pill {{ display:inline-block; padding:14px 40px; border-radius:999px; background:var(--accent); color:var(--bg); font-size:48px; font-weight:700; }}
.clock {{ display:block; margin:70px 0 50px; }}
.hero-title {{ margin:0; font-size:88px; font-weight:700; line-height:1.25; }}
.hero-title .w {{ display:inline-block; }}
.hero-big {{ display:block; margin-top:10px; font-size:260px; font-weight:900; line-height:1.05; color:var(--accent); }}
.callout {{ align-items:flex-start; text-align:left; }}
.label {{ display:flex; align-items:center; gap:22px; font-size:56px; font-weight:700; }}
.icon {{ display:inline-flex; width:74px; height:74px; border-radius:50%; align-items:center; justify-content:center; color:var(--bg); font-size:50px; font-weight:900; }}
.bar {{ display:block; width:100%; height:8px; border-radius:4px; margin:36px 0 44px; }}
.body {{ margin:0; font-size:76px; font-weight:700; line-height:1.35; max-width:900px; }}
.sline {{ position:relative; display:block; width:fit-content; }}
.stext {{ display:inline; }}
.strike {{ position:absolute; left:-10px; right:-10px; top:52%; height:12px; border-radius:6px; background:var(--warn); }}
.stamp {{ display:inline-block; margin-top:60px; padding:12px 44px; border:8px solid var(--warn); border-radius:20px; color:var(--warn); font-size:80px; font-weight:900; }}
.thermo {{ display:flex; flex-direction:column; align-items:center; margin:70px auto 0; }}
.thermo-tube {{ width:70px; height:360px; border-radius:35px; background:rgba(244,247,250,0.15); overflow:hidden; display:flex; align-items:flex-end; }}
.thermo-fill {{ display:block; width:100%; height:100%; border-radius:35px; }}
.thermo-bulb {{ width:130px; height:130px; border-radius:50%; margin-top:-28px; }}
.drop {{ display:flex; justify-content:center; width:100%; margin-top:80px; }}

.tag {{ display:inline-block; padding:10px 34px; border-radius:999px; border:4px solid var(--accent); color:var(--accent); font-size:44px; font-weight:700; margin-bottom:60px; }}
.stat-num {{ font-size:230px; font-weight:900; line-height:1; color:var(--accent); white-space:nowrap; }}
.stat-num .unit {{ font-size:110px; margin-left:12px; color:var(--fg); }}
.stat-rule {{ display:block; width:240px; height:10px; border-radius:5px; background:var(--accent); margin:56px 0 44px; }}
.stat-sub {{ font-size:58px; font-weight:700; line-height:1.35; max-width:880px; }}

.check {{ margin:10px 0 60px; }}
.big-line {{ margin:0; font-size:100px; font-weight:900; line-height:1.25; }}
.big-line.accent {{ color:var(--accent); }}

.end-title {{ margin:0; font-size:84px; font-weight:900; line-height:1.3; max-width:880px; }}
.end-arrow {{ margin:40px 0 60px; }}
.disclosure {{ margin:0; padding:36px 44px; border-radius:24px; background:rgba(244,247,250,0.08); font-size:42px; font-weight:400; line-height:1.55; max-width:900px; color:var(--fg); }}
.caption {{ display:flex; align-items:flex-end; justify-content:center; padding:0 70px 260px; }}
.cap-box {{ display:block; max-width:940px; padding:18px 34px; border-radius:22px; background:rgba(6,12,18,0.78); text-align:center; line-height:1.3; font-size:64px; font-weight:900; }}
.cw {{ display:inline-block; font-size:64px; font-weight:900; color:var(--fg); }}
"""

html = f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width={W}, height={H}" />
  <title>겨울 목욕, 온도보다 무서운 건 시간 (HyperFrames)</title>
  <script src="vendor/gsap.min.js"></script>
  <style>{CSS}</style>
</head>
<body>
  <div id="root" data-composition-id="main" data-width="{W}" data-height="{H}" data-duration="{f(TOTAL)}" data-fps="{FPS}">
    {bg_clip}
    {chr(10).join(clips)}
    {audio}
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    {chr(10).join('    ' + t for t in tweens)}
    window.__timelines["main"] = tl;
  </script>
</body>
</html>
"""
(WS / "index.html").write_text(html, encoding="utf-8")
print("pages", len(pages), "clips", len(clips), "tweens", len(tweens))
