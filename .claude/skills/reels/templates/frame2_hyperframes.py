"""2번 프레임(HyperFrames) 틀 — reels 스킬용 (2026-11-22).

1번 프레임(Remotion)과 같은 composition.json(컷·자막·오디오)을 받아
HyperFrames 작업 폴더(index.html + 음성·음악·GSAP·한글 글꼴)를 만든다.
렌더는 이 스크립트가 하지 않는다. 만든 뒤 작업 폴더에서
`npx hyperframes lint / validate / inspect / snapshot / render`를 돌린다.

사용:
  python frame2_hyperframes.py <OpenMontage/projects/<id>> \
      [--composition <json>] [--out <작업폴더>] \
      [--font-regular <ttf/otf/ttc> --font-bold <ttf/otf/ttc>] [--gsap <gsap.min.js>]

composition.json 컷마다 넣을 수 있는 선택 필드 "hf" (1번 프레임에는 넣지 않는다):
  hero_title : {"emphasis": "시간", "icon": "clock"}      emphasis 기본값 = text의 마지막 낱말
  callout    : {"fx": "strike"|"thermo"|"arrow_down", "stamp": "오해", "lines": ["1줄", "2줄"]}
  stat_card  : {"tag": "기억하세요 ①"}                    stat 앞 숫자는 0부터 올라간다
  text_card  : {"tag": "기억하세요 ③", "icon": "check"|"none"}
마지막 컷은 항상 끝 화면(title + 아래 화살표 + text 상자)으로 그린다. text에 광고 표기를 넣는다.

필요: Python 3, fontTools + brotli (pip install fonttools brotli), Node 22+, FFmpeg, Chrome.
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

W, H, FPS = 1080, 1920, 30
EPS = 0.02  # 같은 트랙의 클립이 맞닿지 않게
BG, FG, ACCENT, WARN, INFO = "#0F1B26", "#F4F7FA", "#FF8A3D", "#FF5A5F", "#5AB0FF"

FONT_CANDIDATES = [  # (regular, bold, 글꼴 이름)
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
     "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", "Noto Sans CJK KR"),
    ("/System/Library/Fonts/AppleSDGothicNeo.ttc",
     "/System/Library/Fonts/AppleSDGothicNeo.ttc", "Apple SD Gothic Neo"),  # 맥: 2026-11-22 확인
]


def f(v):
    return f"{float(v):.3f}".rstrip("0").rstrip(".")


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


CAPTION_POP_MAX = 1.08  # 강조되는 자막 낱말을 키우는 최대 배율
CAPTION_POP_GROW_PX = 14  # 낱말이 커지며 양옆으로 넓어지는 폭의 합 한도(낱말 사이 빈칸 약 22px보다 작게)
CAPTION_HANGUL_PX, CAPTION_LATIN_PX = 58, 34  # 64px 굵은 글꼴의 글자 폭(실측: 한글 8자 = 465px)


def caption_width_px(word: str) -> int:
    return sum(CAPTION_HANGUL_PX if ord(ch) > 0x2E80 else CAPTION_LATIN_PX for ch in word)


def caption_pop_scale(word: str) -> float:
    """강조 낱말 확대율. 긴 낱말은 옆 빈칸을 덮어 띄어쓰기가 사라져 보이지 않게 덜 키운다."""
    width = caption_width_px(word)
    if width <= 0:
        return CAPTION_POP_MAX
    return round(min(CAPTION_POP_MAX, 1 + CAPTION_POP_GROW_PX / width), 3)


class Builder:
    def __init__(self, comp, timings):
        self.comp = comp
        self.timings = timings
        self.cuts = comp["cuts"]
        self.total = max(float(c["out_seconds"]) for c in self.cuts)
        self.words = comp.get("captions", [])
        self.clips, self.tweens = [], []

    # ------------------------------------------------------------ helpers
    def scene(self, c, inner):
        cid, s, e = c["id"], float(c["in_seconds"]), float(c["out_seconds"])
        dur = e - s - (EPS if e < self.total else 0)
        self.clips.append(
            f'<section id="{cid}" class="clip scene" data-start="{f(s)}" '
            f'data-duration="{f(dur)}" data-track-index="1">{inner}</section>')
        if e < self.total:
            self.tw(f'tl.to("#{cid} .stage", {{opacity: 0, y: -30, duration: 0.22, ease: "power2.in"}}, {f(e - 0.24)});')
        return s, e

    def tw(self, t):
        self.tweens.append(t)

    def counter(self, el_id, start, dur, a, b, fmt):
        n = max(2, int(round(dur * FPS)))
        last = None
        for i in range(n + 1):
            x = i / n
            v = int(round(a + (b - a) * (1 - (1 - x) ** 3)))
            if v == last:
                continue
            last = v
            self.tw(f'tl.set("#{el_id}", {{textContent: "{fmt.format(v)}"}}, {f(start + i / FPS)});')

    def word_time(self, needle, s, e, default):
        for w in self.words:
            t = w["startMs"] / 1000
            if s - 0.1 <= t <= e and needle in w["word"]:
                return t
        return default

    @staticmethod
    def split_two(text):
        words = text.split()
        if len(words) < 3:
            return [text]
        mid = len(text) / 2
        best = None
        for i in range(1, len(words)):
            pos = len(" ".join(words[:i]))
            if best is None or abs(pos - mid) < abs(best[1] - mid):
                best = (i, pos)
        return [" ".join(words[:best[0]]), " ".join(words[best[0]:])]

    # ------------------------------------------------------------ scenes
    def hero(self, c):
        hf, cid = c.get("hf", {}), c["id"]
        text = c.get("text", "")
        emph = hf.get("emphasis") or (text.split()[-1] if text.split() else "")
        rest = text[: text.rfind(emph)].strip() if emph and text.endswith(emph) else text
        icon = ""
        if hf.get("icon") == "clock":
            icon = (f'<svg class="clock" id="{cid}-clock" viewBox="0 0 200 200" width="260" height="260">'
                    f'<circle cx="100" cy="100" r="88" fill="none" stroke="{ACCENT}" stroke-width="10"/>'
                    f'<rect id="{cid}-hand" x="95" y="30" width="10" height="74" rx="5" fill="{FG}"/>'
                    f'<circle cx="100" cy="100" r="9" fill="{ACCENT}"/></svg>')
        words = rest.split()
        spans = " ".join(f'<span class="w" id="{cid}-w{i}">{esc(w)}</span>' for i, w in enumerate(words))
        pill = f'<div class="pill" id="{cid}-pill">{esc(c["heroSubtitle"])}</div>' if c.get("heroSubtitle") else ""
        big = f'<div class="hero-big" id="{cid}-big">{esc(emph)}</div>' if emph and emph != text else ""
        s, e = self.scene(c, f'<div class="stage hero">{pill}{icon}<h1 class="hero-title">{spans}</h1>{big}</div>')
        if pill:
            self.tw(f'tl.from("#{cid}-pill", {{y: -40, opacity: 0, duration: 0.45, ease: "power3.out"}}, {f(s + 0.05)});')
        if icon:
            self.tw(f'tl.from("#{cid}-clock", {{scale: 0.6, opacity: 0, duration: 0.5, ease: "back.out(1.8)"}}, {f(s + 0.15)});')
            self.tw(f'tl.fromTo("#{cid}-hand", {{rotation: 0}}, {{rotation: 540, duration: {f(e - s)}, ease: "none", transformOrigin: "50% 95%"}}, {f(s)});')
        for i in range(len(words)):
            self.tw(f'tl.from("#{cid}-w{i}", {{y: 60, opacity: 0, duration: 0.45, ease: "power3.out"}}, {f(s + 0.35 + 0.3 * i)});')
        if big:
            t = self.word_time(emph, s, e, s + 1.2) - 0.1
            self.tw(f'tl.from("#{cid}-big", {{scale: 2.2, opacity: 0, duration: 0.55, ease: "expo.out"}}, {f(max(s + 0.4, t))});')

    def callout(self, c):
        hf, cid = c.get("hf", {}), c["id"]
        color = WARN if c.get("callout_type") == "warning" else INFO
        mark = "!" if color == WARN else "i"
        fx = hf.get("fx")
        lines = []
        if fx == "strike":
            lines = hf.get("lines") or self.split_two(c.get("text", ""))
            body = (f'<div class="body" id="{cid}-body">' + "".join(
                f'<div class="sline"><span class="stext">{esc(l)}</span><div class="strike" id="{cid}-strike{i}"></div></div>'
                for i, l in enumerate(lines)) + "</div>")
            if hf.get("stamp"):
                body += f'<div class="stamp" id="{cid}-stamp">{esc(hf["stamp"])}</div>'
        else:
            body = f'<p class="body" id="{cid}-body">{esc(c.get("text", ""))}</p>'
        extra = ""
        if fx == "thermo":
            extra = (f'<div class="thermo" id="{cid}-thermo"><div class="thermo-tube"><div class="thermo-fill" id="{cid}-fill"></div></div>'
                     f'<div class="thermo-bulb" id="{cid}-bulb"></div></div>')
        elif fx == "arrow_down":
            extra = (f'<div class="drop"><svg id="{cid}-arrow" viewBox="0 0 120 200" width="150" height="250">'
                     f'<rect x="45" y="0" width="30" height="120" rx="8" fill="{WARN}"/><polygon points="10,110 110,110 60,190" fill="{WARN}"/></svg></div>')
        s, e = self.scene(c, f'<div class="stage callout"><div class="label" style="color:{color}" id="{cid}-label">'
                             f'<span class="icon" style="background:{color}">{mark}</span>{esc(c.get("title", ""))}</div>'
                             f'<div class="bar" id="{cid}-bar" style="background:{color}"></div>{body}{extra}</div>')
        self.tw(f'tl.from("#{cid}-label", {{x: -80, opacity: 0, duration: 0.4, ease: "power3.out"}}, {f(s + 0.05)});')
        self.tw(f'tl.from("#{cid}-bar", {{scaleX: 0, duration: 0.5, ease: "power2.out", transformOrigin: "0% 50%"}}, {f(s + 0.2)});')
        self.tw(f'tl.from("#{cid}-body", {{y: 50, opacity: 0, duration: 0.5, ease: "power3.out"}}, {f(s + 0.35)});')
        if fx == "strike":
            for i in range(len(lines)):
                self.tw(f'tl.from("#{cid}-strike{i}", {{scaleX: 0, duration: 0.32, ease: "power2.inOut", transformOrigin: "0% 50%"}}, {f(e - 1.35 + 0.3 * i)});')
            self.tw(f'tl.to("#{cid}-body", {{opacity: 0.55, duration: 0.3}}, {f(e - 1.35)});')
            if hf.get("stamp"):
                self.tw(f'tl.from("#{cid}-stamp", {{scale: 2.4, rotation: -18, opacity: 0, duration: 0.35, ease: "back.out(2)"}}, {f(e - 0.95)});')
        elif fx == "thermo":
            d = max(1.0, e - s - 1.3)
            self.tw(f'tl.from("#{cid}-thermo", {{opacity: 0, y: 40, duration: 0.4, ease: "power2.out"}}, {f(s + 0.5)});')
            self.tw(f'tl.fromTo("#{cid}-fill", {{scaleY: 0.25, backgroundColor: "{ACCENT}"}}, {{scaleY: 0.95, backgroundColor: "{WARN}", duration: {f(d)}, ease: "power1.inOut", transformOrigin: "50% 100%"}}, {f(s + 0.7)});')
            self.tw(f'tl.fromTo("#{cid}-bulb", {{backgroundColor: "{ACCENT}"}}, {{backgroundColor: "{WARN}", duration: {f(d)}, ease: "power1.inOut"}}, {f(s + 0.7)});')
        elif fx == "arrow_down":
            self.tw(f'tl.fromTo("#{cid}-arrow", {{y: -160, opacity: 0}}, {{y: 0, opacity: 1, duration: 0.7, ease: "bounce.out"}}, {f(s + 0.8)});')

    def stat(self, c):
        hf, cid = c.get("hf", {}), c["id"]
        stat = c.get("stat", "")
        m = re.match(r"^\s*([\d][\d,]*)(.*)$", stat)
        tag = f'<div class="tag" id="{cid}-tag">{esc(hf["tag"])}</div>' if hf.get("tag") else ""
        if m:
            num_html = f'<span id="{cid}-count">0</span><span class="unit">{esc(m.group(2).strip())}</span>'
        else:
            num_html = esc(stat)
        sub_lines = re.split(r"\s*\|\s*|\s+·\s+", c.get("subtitle", "")) if c.get("subtitle") else []
        sub = "".join(f"<div>{esc(x)}</div>" for x in sub_lines)
        s, e = self.scene(c, f'<div class="stage stat">{tag}<div class="stat-num" id="{cid}-num">{num_html}</div>'
                             f'<div class="stat-rule" id="{cid}-rule"></div><div class="stat-sub" id="{cid}-sub">{sub}</div></div>')
        if tag:
            self.tw(f'tl.from("#{cid}-tag", {{y: -30, opacity: 0, duration: 0.35, ease: "power2.out"}}, {f(s)});')
        self.tw(f'tl.from("#{cid}-num", {{scale: 0.7, opacity: 0, duration: 0.45, ease: "back.out(1.6)"}}, {f(s + 0.05)});')
        self.tw(f'tl.from("#{cid}-rule", {{scaleX: 0, duration: 0.5, ease: "power2.out"}}, {f(s + 0.3)});')
        self.tw(f'tl.from("#{cid}-sub", {{y: 30, opacity: 0, duration: 0.45, ease: "power3.out"}}, {f(s + 0.45)});')
        if m:
            raw = m.group(1)
            val = int(raw.replace(",", ""))
            dur = 1.3 if val >= 1000 else 0.9 if val >= 20 else 0.6
            self.counter(f"{cid}-count", s + 0.1, min(dur, e - s - 0.5), 0, val, "{:,}" if "," in raw else "{}")

    def textcard(self, c):
        hf, cid = c.get("hf", {}), c["id"]
        text = c.get("text", "")
        parts = text.split(", ", 1)
        lines = [parts[0] + ",", parts[1]] if len(parts) == 2 else [text]
        tag = f'<div class="tag" id="{cid}-tag">{esc(hf["tag"])}</div>' if hf.get("tag") else ""
        check = "" if hf.get("icon") == "none" else (
            f'<div class="check" id="{cid}-check"><svg viewBox="0 0 100 100" width="150" height="150"><circle cx="50" cy="50" r="46" fill="{ACCENT}"/>'
            f'<polyline points="28,52 44,68 74,36" fill="none" stroke="{BG}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/></svg></div>')
        ps = "".join(f'<p class="big-line{" accent" if i == len(lines) - 1 else ""}" id="{cid}-l{i}">{esc(l)}</p>' for i, l in enumerate(lines))
        s, e = self.scene(c, f'<div class="stage textcard">{tag}{check}{ps}</div>')
        if tag:
            self.tw(f'tl.from("#{cid}-tag", {{y: -30, opacity: 0, duration: 0.35, ease: "power2.out"}}, {f(s)});')
        if check:
            self.tw(f'tl.from("#{cid}-check", {{scale: 0, rotation: -90, duration: 0.5, ease: "back.out(2)"}}, {f(s + 0.1)});')
        for i in range(len(lines)):
            self.tw(f'tl.from("#{cid}-l{i}", {{y: 40, opacity: 0, duration: 0.4, ease: "power3.out"}}, {f(s + 0.3 + 0.25 * i)});')

    def endcard(self, c):
        cid = c["id"]
        title = c.get("title") or c.get("text", "")
        text = c.get("text", "") if c.get("title") else c.get("subtitle", "")
        if "수수료" not in text:
            print("경고: 마지막 컷 text에 광고 표기(수수료 문구)가 없습니다.", file=sys.stderr)
        s, e = self.scene(c, f'<div class="stage endcard"><p class="end-title" id="{cid}-title">{esc(title)}</p>'
                             f'<div class="end-arrow" id="{cid}-arrow"><svg viewBox="0 0 100 100" width="120" height="120">'
                             f'<polyline points="20,35 50,65 80,35" fill="none" stroke="{ACCENT}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/></svg></div>'
                             f'<p class="disclosure" id="{cid}-disc">{esc(text)}</p></div>')
        bounces = max(1, int((e - s - 1.0) // 0.9) - 1)
        self.tw(f'tl.from("#{cid}-title", {{y: 50, opacity: 0, duration: 0.5, ease: "power3.out"}}, {f(s + 0.05)});')
        self.tw(f'tl.from("#{cid}-disc", {{opacity: 0, duration: 0.6, ease: "power1.out"}}, {f(s + 0.4)});')
        self.tw(f'tl.fromTo("#{cid}-arrow", {{y: 0}}, {{y: 26, duration: 0.45, ease: "sine.inOut", yoyo: true, repeat: {max(1, bounces * 2 - 1)}}}, {f(s + 0.6)});')

    # ------------------------------------------------------------ captions
    def captions(self):
        sections = self.timings.get("sections", [])

        def sec_of(w):
            t = w["startMs"] / 1000
            for i, sec in enumerate(sections):
                if sec["start"] - 0.05 <= t <= sec["end"] + 0.05:
                    return i
            return -1

        per_page = int(self.comp.get("captionStyle", {}).get("wordsPerPage", 3))
        pages, cur, cur_sec = [], [], None
        for w in self.words:
            sec = sec_of(w)
            if cur and (sec != cur_sec or len(cur) == per_page):
                pages.append(cur)
                cur = []
            cur.append(w)
            cur_sec = sec
        if cur:
            pages.append(cur)
        for pi, page in enumerate(pages):
            start, end = page[0]["startMs"] / 1000, page[-1]["endMs"] / 1000
            if pi + 1 < len(pages):
                nxt = pages[pi + 1][0]["startMs"] / 1000
                if nxt - end < 0.35:
                    end = nxt - EPS
            spans = " ".join(f'<span class="cw" id="cap{pi}-{wi}">{esc(w["word"])}</span>' for wi, w in enumerate(page))
            self.clips.append(f'<div id="cap{pi}" class="clip caption" data-start="{f(start)}" data-duration="{f(end - start)}" '
                              f'data-track-index="5"><div class="cap-box" id="cap{pi}-box">{spans}</div></div>')
            self.tw(f'tl.from("#cap{pi}-box", {{y: 24, opacity: 0, duration: 0.16, ease: "power2.out"}}, {f(start)});')
            for wi, w in enumerate(page):
                a, b = w["startMs"] / 1000, w["endMs"] / 1000
                self.tw(f'tl.to("#cap{pi}-{wi}", {{color: "{ACCENT}", scale: {caption_pop_scale(w["word"])}, duration: 0.08}}, {f(a)});')
                self.tw(f'tl.to("#cap{pi}-{wi}", {{color: "{FG}", scale: 1, duration: 0.08}}, {f(max(a + 0.09, b - 0.04))});')

    # ------------------------------------------------------------ assemble
    def build(self):
        for i, c in enumerate(self.cuts):
            if i == len(self.cuts) - 1:
                self.endcard(c)
            elif c.get("type") == "hero_title":
                self.hero(c)
            elif c.get("type") == "callout":
                self.callout(c)
            elif c.get("type") == "stat_card":
                self.stat(c)
            else:
                self.textcard(c)
        self.captions()
        music = self.comp.get("audio", {}).get("music") or {}
        vol = float(music.get("volume", 0.07))
        fin, fout = float(music.get("fadeInSeconds", 1.5)), float(music.get("fadeOutSeconds", 2.5))
        cycles = max(1, int(self.total // 6))
        head = [
            f'tl.fromTo("#glow1", {{y: 0, scale: 1}}, {{y: -120, scale: 1.15, duration: 3, ease: "sine.inOut", yoyo: true, repeat: {cycles * 2 - 1}}}, 0);',
            f'tl.fromTo("#glow2", {{y: 0, scale: 1.1}}, {{y: 100, scale: 0.95, duration: 3, ease: "sine.inOut", yoyo: true, repeat: {cycles * 2 - 1}}}, 0);',
            f'tl.fromTo("#progress-fill", {{scaleX: 0}}, {{scaleX: 1, duration: {f(self.total)}, ease: "none"}}, 0);',
        ]
        if music:
            head += [f'tl.fromTo("#bgm", {{volume: 0}}, {{volume: {f(vol)}, duration: {f(fin)}, ease: "none"}}, 0);',
                     f'tl.to("#bgm", {{volume: 0, duration: {f(fout)}, ease: "none"}}, {f(self.total - fout)});']
        tweens = head + self.tweens
        bg = (f'<div id="bg" class="clip" data-start="0" data-duration="{f(self.total)}" data-track-index="0">'
              '<div class="bg-fill"></div><div class="glow g1" id="glow1"></div><div class="glow g2" id="glow2"></div>'
              '<div class="progress"><div class="progress-fill" id="progress-fill"></div></div></div>')
        audio = (f'<audio id="nar" src="assets/narration.wav" data-start="0" data-duration="{f(self.timings["total"])}" '
                 f'data-track-index="10" data-volume="1"></audio>')
        if music:
            audio += (f'<audio id="bgm" src="assets/bgm.mp3" data-start="0" data-duration="{f(self.total)}" '
                      f'data-track-index="11" data-volume="{f(vol)}"></audio>')
        title = next((c.get("text") for c in self.cuts if c.get("type") == "hero_title"), "reels")
        return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width={W}, height={H}" />
  <title>{esc(title)} (2번 프레임)</title>
  <script src="vendor/gsap.min.js"></script>
  <style>{CSS}</style>
</head>
<body>
  <div id="root" data-composition-id="main" data-width="{W}" data-height="{H}" data-duration="{f(self.total)}" data-fps="{FPS}">
    {bg}
    {chr(10).join(self.clips)}
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


CSS = f"""
@font-face {{ font-family:"HF KR"; src:url("fonts/KR-Regular.woff2") format("woff2"); font-weight:400; font-style:normal; }}
@font-face {{ font-family:"HF KR"; src:url("fonts/KR-Bold.woff2") format("woff2"); font-weight:700 900; font-style:normal; }}
:root {{ --bg:{BG}; --fg:{FG}; --accent:{ACCENT}; --warn:{WARN}; --info:{INFO}; }}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg); font-family:"HF KR",sans-serif; word-break:keep-all; }}
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


def find_gsap(explicit):
    if explicit:
        return Path(explicit)
    pat = os.path.expanduser("~/.npm/_npx/*/node_modules/hyperframes/dist/vendor/npm/gsap@*/dist/gsap.min.js")
    hits = sorted(glob.glob(pat))
    if not hits:  # npx 캐시가 비었으면 한 번 받아 온다
        subprocess.run(["npx", "--yes", "hyperframes", "--version"], capture_output=True, text=True, timeout=300)
        hits = sorted(glob.glob(pat))
    if not hits:
        sys.exit("GSAP을 찾지 못했습니다. --gsap 로 gsap.min.js 경로를 지정하세요.")
    return Path(hits[-1])


def subset_fonts(html, out_dir, reg_path, bold_path):
    from fontTools import subset
    from fontTools.ttLib import TTCollection, TTFont

    def load(path, bold, family):
        if str(path).lower().endswith(".ttc"):
            for font in TTCollection(path).fonts:
                full = font["name"].getDebugName(4) or ""
                if family and family not in full:
                    continue
                tail = full.replace(family, "").strip() if family else full
                if (bold and tail == "Bold") or (not bold and tail in ("", "Regular")):
                    return font
            sys.exit(f"{path}에서 {family} {'Bold' if bold else 'Regular'}를 찾지 못했습니다.")
        return TTFont(path)

    family = None
    if not reg_path:
        for r, b, fam in FONT_CANDIDATES:
            if Path(r).exists() and Path(b).exists():
                reg_path, bold_path, family = r, b, fam
                break
        else:
            sys.exit("한글 글꼴을 찾지 못했습니다. --font-regular / --font-bold 로 지정하세요.")
    body = re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S)
    chars = set(re.sub(r"<[^>]+>", " ", body)) | set("0123456789,.·?!%℃①②③④⑤ ")
    for weight, path, bold in (("Regular", reg_path, False), ("Bold", bold_path, True)):
        font = load(path, bold, family)
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = ["*"]
        sub = subset.Subsetter(opts)
        sub.populate(text="".join(chars))
        sub.subset(font)
        subset.save_font(font, str(out_dir / f"KR-{weight}.woff2"), opts)
    return reg_path, bold_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--composition")
    ap.add_argument("--out")
    ap.add_argument("--font-regular")
    ap.add_argument("--font-bold")
    ap.add_argument("--gsap")
    a = ap.parse_args()
    P = Path(a.project).resolve()
    comp = json.loads(Path(a.composition or P / "artifacts/composition.json").read_text(encoding="utf-8"))
    timings = json.loads((P / "assets/audio/narration_timings.json").read_text(encoding="utf-8"))
    ws = Path(a.out or P / "hyperframes").resolve()
    for d in ("assets", "vendor", "fonts"):
        (ws / d).mkdir(parents=True, exist_ok=True)
    nar = comp.get("audio", {}).get("narration", {}).get("src") or str(P / "assets/audio/narration_norm.wav")
    shutil.copyfile(nar, ws / "assets/narration.wav")
    music = comp.get("audio", {}).get("music", {}).get("src")
    if music:
        shutil.copyfile(music, ws / "assets/bgm.mp3")
    shutil.copyfile(find_gsap(a.gsap), ws / "vendor/gsap.min.js")
    html = Builder(comp, timings).build()
    (ws / "index.html").write_text(html, encoding="utf-8")
    r, b = subset_fonts(html, ws / "fonts", a.font_regular, a.font_bold)
    print(json.dumps({"workspace": str(ws), "duration": max(float(c["out_seconds"]) for c in comp["cuts"]),
                      "cuts": len(comp["cuts"]), "fonts": [r, b]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
