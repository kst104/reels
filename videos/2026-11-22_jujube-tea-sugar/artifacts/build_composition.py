"""scene_plan_hf.json + 음성 시각(narration_timings.json) + script.txt → composition.json.

2번 프레임 틀(.claude/skills/reels/templates/frame2_hyperframes.py)의 입력을 만든다.
- 컷 시각: 같은 문장 컷이 여럿이면 split_after 어절이 끝나는 곳에서 나눈다.
  문장 첫 컷은 그 문장 시작 0.3초 전, 첫 컷은 0초, 마지막 컷은 내레이션 끝 + 3초까지.
- 자막: 어절 단위. 문장 구간은 실측 시각, 문장 안 어절은 글자 수 비례(스킬 5절과 같은 방식).

사용:
  python build_composition.py <OpenMontage/projects/<id>>
    [--plan scene_plan_hf.json] [--script script.txt] [--music assets/music/bgm.mp3]
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--plan", default=str(HERE / "scene_plan_hf.json"))
    ap.add_argument("--script", default=str(HERE.parent / "script.txt"))
    ap.add_argument("--music", default=None)
    a = ap.parse_args()
    P = Path(a.project).resolve()
    plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    lines = [l for l in Path(a.script).read_text(encoding="utf-8").strip().split("\n") if l.strip()]
    tim = json.loads((P / "assets/audio/narration_timings.json").read_text(encoding="utf-8"))
    secs = tim["sections"]
    if len(secs) != len(lines):
        raise SystemExit(f"문장 수가 다릅니다: script {len(lines)}줄, timings {len(secs)}구간")

    caps = []
    for si, (sec, line) in enumerate(zip(secs, lines)):
        words = line.split()
        total = sum(len(w) for w in words)
        cur = sec["start"]
        for w in words:
            d = (sec["end"] - sec["start"]) * len(w) / total
            caps.append({"word": w, "startMs": int(round(cur * 1000)), "endMs": int(round((cur + d) * 1000)), "_s": si + 1})
            cur += d

    cuts = [dict(c) for c in plan["cuts"]]
    by_sent = {}
    for c in cuts:
        by_sent.setdefault(c["sentence"], []).append(c)
    n = len(secs)
    for s, group in by_sent.items():
        sec = secs[s - 1]
        start = 0.0 if s == 1 else sec["start"] - 0.3
        words = [w for w in caps if w["_s"] == s]
        for c in group:
            c["in_seconds"] = round(start, 3)
            if "split_after" in c:
                hit = [w for w in words if w["word"] == c["split_after"]]
                if not hit:
                    raise SystemExit(f"{c['id']}: '{c['split_after']}' 어절을 {s}번 문장에서 찾지 못했습니다")
                end = hit[0]["endMs"] / 1000 + 0.05
            else:
                end = secs[s]["start"] - 0.3 if s < n else tim["total"] + 3.0
            c["out_seconds"] = round(end, 3)
            start = end
    for c in cuts:
        c.pop("sentence", None)
        c.pop("split_after", None)
    for w in caps:
        w.pop("_s")

    music = plan.get("audio", {}).get("music", {})
    music_src = Path(a.music) if a.music else P / "assets/music/bgm.mp3"
    comp = {
        "renderer_family": "explainer-teacher",
        "cuts": cuts,
        "captions": caps,
        "captionStyle": plan.get("captionStyle", {"wordsPerPage": 3, "fontSize": 64, "bottomOffset": 260}),
        "captionProps": {"fontFamily": "Noto Sans CJK KR, Apple SD Gothic Neo, sans-serif", "wordSeparator": " "},
        "audio": {
            "narration": {"src": str(P / "assets/audio/narration_norm.wav"), "volume": 1.0},
            "music": {"src": str(music_src), "volume": music.get("volume", 0.07),
                      "fadeInSeconds": music.get("fadeInSeconds", 1.5), "fadeOutSeconds": music.get("fadeOutSeconds", 2.5)},
        },
    }
    if not music_src.exists():
        print(f"경고: 음악 파일이 없습니다({music_src}). 음악 없이 만들려면 audio.music을 지우세요.")
    out = P / "artifacts/composition.json"
    out.write_text(json.dumps(comp, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"out": str(out), "duration": max(c["out_seconds"] for c in cuts),
                      "cuts": [(c["id"], c["in_seconds"], c["out_seconds"]) for c in cuts],
                      "captions": len(caps)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
