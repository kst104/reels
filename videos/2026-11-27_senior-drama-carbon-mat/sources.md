# 출처와 제작 기록: 시니어 드라마 「보일러는 니 맘대로」

## 제작 요청 프롬프트 (원문)

- 2026-11-27 `/yugyosu-senior-drama-shorts` "시니어 드라마 만들어줘"
- 질문 답: 홍보 상품 "한일의료기 탄소매트" / 장르 "참교육" / 길이 "30초 (2장면)" / 만드는 방법 "대사 나오는 영상 AI"
- "타입캐스트 api는 사용해도 돼"
- "아니 스크립트는 네가 짜서 줘야해"
- "이미지를 먼저 보여주고, 첫장면만 먼저 뽑아줘. 다 만들지말고"

## 제작전분석소 보고서

- 없음. 이 영상은 제작전분석소 브리프 없이 시니어 드라마 스킬로 바로 시작했다.

## 상품 확인에 쓴 곳 (2026-11-27 조회)

- 상점 후보 표: `docs/shop-sync.md` 2절 7번 "한일의료기 탄소매트 전기매트 1인용, 69,000원, 디지털/가전 약 3위(11.20 기준)". 상품 주소는 그 표에서도 미확인.
- 블로그 후기 https://m.blog.naver.com/alison_kk/224423376412 : 상품명 "한일의료기 탄소매트 전기매트 온열매트 전자파없는 전기장판 캠핑 침대 1인용 싱글 프리즘", 69,000원, 세탁 가능. 색·조절기·상자 설명 없음. "전자파 없음"의 근거 없음. 글 속 링크 naver.me/Gnt9RIKh → 브랜드 커넥트 제휴 주소(channelProductNo=12554272168).
- 블로그 후기 https://m.blog.naver.com/todaysdiary-u_u/224432336790 : "30년전통 한일의료기 탄소열선 전기요" 페이지를 가리킴. 베이지색, 다이얼 조절기, EMF 인증이라고 적음. 위 상품과 같은 페이지인지 확인하지 못함.
- 스마트스토어 상품 페이지(products/12554272168)는 로그인 화면으로 넘어가 열지 못함.

## 이미지

- 허깅페이스 Space mcp-tools/Z-Image-Turbo로 생성 (C1 시드 877041, C2 432975, L1 651050). 실존 인물·장소가 아니다.

## 음성

- `make_scene1_voice.py`: 저장소 공용 `.claude/skills/reels/templates/typecast_voice.py`를 불러 타입캐스트 ssfm-v31로 B1 대사 두 줄을 만든다. 목소리 ID는 아직 정하지 않았다(`--list`로 후보 확인).
- 목소리 목록 API(GET /v3/voices, gender·age 필터): https://typecast.ai/docs/llms.txt, https://typecast.ai/docs/api-reference/voices/list-voices
- 이 클라우드 세션에는 TYPECAST_API_KEY가 없어 실제 음성은 만들지 않았다.
