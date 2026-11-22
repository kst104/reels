# reels 폴더

1. 이 폴더를 `~/Downloads/reels`에 둔다.
2. Claude Code를 이 폴더에서 연다. 맥미니(Claude 데스크톱 앱에서 이 폴더 선택, 또는 터미널에서 `cd ~/Downloads/reels && claude`)에서도, 이 저장소를 연 클라우드 세션에서도 같은 순서로 만든다.
3. "reels [주제]"라고 말하면 `reels` 스킬이 조사 → 대본 → im-not-ai 윤문 → 남성1 음성(`make_narration.py`) → 렌더 → mp4까지 한 세션에서 진행한다. 음성 때문에 맥미니로 넘기지 않는다.

- `videos/` — 완성된 영상별 폴더 (2026-11-22 겨울 목욕). 그 전 영상은 루트의 `2026-11-20-kitchen-scale/`
- `docs/reels-hub.html` — 아티팩트 "릴스"의 원본
- 연결: 노션 "릴스", 아티팩트 "릴스", 슬랙 `#reels` — 링크는 `CLAUDE.md`
- `docs/intent/` — 확정된 작업 의도 기록
- `.claude/skills/reels/templates/make_narration.py` — 음성 스크립트(Supertonic 3 남성1). 테스트는 `tests/` (`python -m pytest tests`)
- `videos/*/artifacts/*.json`의 파일 경로는 만들 때 쓴 클라우드 세션 경로라 이 컴퓨터에서는 그대로 열리지 않는다. 내용 참고용이다.

필요한 것 (처음 한 번): Node.js 22 이상, ffmpeg, Python 3, git. im-not-ai 스킬(humanize-korean). 음성 라이브러리는 스킬이 `requirements-voice.txt`로 설치하고, 음성 모델(약 385MB)은 처음 음성을 만들 때 huggingface.co에서 내려받는다.

음악(Pixabay) 원본 파일은 넣지 않았다. 출처는 각 영상의 `sources.md`에 있다.
