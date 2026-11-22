# reels 폴더

1. 이 폴더를 `~/Downloads/reels`에 둔다.
2. 맥미니에서 Claude Code를 이 폴더에서 연다 (Claude 데스크톱 앱에서 이 폴더 선택, 또는 터미널에서 `cd ~/Downloads/reels && claude`).
   클라우드 세션에서 쓰려면 Claude 앱 설정 > Claude Code > Remote Control에 이 폴더를 추가한다.
3. "reels [주제]"라고 말하면 `reels` 스킬이 조사 → 대본 → im-not-ai 윤문 → 7790 남성1 음성 → 렌더 → mp4까지 진행한다.

- `videos/` — 완성된 영상별 폴더 (2026-11-22 겨울 목욕). 그 전 영상은 루트의 `2026-11-20-kitchen-scale/`
- `docs/reels-hub.html` — 아티팩트 "릴스"의 원본
- 연결: 노션 "릴스", 아티팩트 "릴스", 슬랙 `#reels` — 링크는 `CLAUDE.md`
- `docs/intent/` — 확정된 작업 의도 기록
- `videos/*/artifacts/*.json`의 파일 경로는 만들 때 쓴 클라우드 세션 경로라 이 컴퓨터에서는 그대로 열리지 않는다. 내용 참고용이다.

필요한 것 (처음 한 번): Node.js 22 이상, ffmpeg, Python 3, git. im-not-ai 스킬(humanize-korean).

음악(Pixabay) 원본 파일은 넣지 않았다. 출처는 각 영상의 `sources.md`에 있다.
