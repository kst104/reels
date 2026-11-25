# 아이폰18 프로 쇼핑 쇼츠 — 출처 (2026-11-25)

제작 요청 원문: "오늘 쇼핑쇼츠인 아이폰18프로를 힉스필드를 이용해서 소구점 ( 구매가의 댓글에서 산이유와 만족포인트)을 찾아 대본을 먼저 짜주고, 힉스필드로 제작할께 (720p)" → 대본 확인 "이대로 제작".
근거가 된 제작전분석소 보고서: 없음(사용자가 제작소에 직접 요청). 소구점 표는 script_draft.md.

## 문장별 근거
1. 질문(근거 없음)
2. 바꾼 이유 1위 배터리·발열 — 클리앙 https://www.clien.net/service/board/cm_iphonien/19263561 (13프로 노후화·교체 5회)
3. 퇴근까지 배터리 넉넉 — 연합뉴스 3주 사용기 요약 https://wikidocs.net/blog/@wondergrid/33206/ , 클리앙 https://www.clien.net/service/board/cm_iphonien/19276726
4. 동영상 최대 34시간 — 애플 사양 https://www.apple.com/kr/iphone-18-pro/specs/
5. 아이폰 최초 가변 조리개 — 애플 사양(ƒ/1.48~ƒ/4.0), 위키독스 사용기
6. 빛 갈라짐 후기 — 클리앙 https://www.clien.net/service/board/cm_iphonien/19269434 ("조리개 버튼만 눌렀더니 이런 효과")
7. 15분 최대 50% — 애플 사양(60W 이상 AVS 어댑터, 별매)
8. 세 가지 만족 — 위 후기 종합
9. 질문(근거 없음)

## 화면
- 틀: 2번(HyperFrames) 기본1 형식. 장면 사진 자리를 힉스필드 영상으로 바꿈(artifacts/swap_video.py, 이 프로젝트에서만).
- 영상: 힉스필드 Seedance 2.5, 720p, 1:1, 5초, 소리 없음(artifacts/gen_clips.sh). 1~5·7~9번은 위키미디어 공용 사진을 첫 화면으로 쓴 AI 움직임, 6번은 글자 프롬프트로 만든 AI 영상(실제 촬영 아님). 7·8번 처음 결과는 폰을 돌리며 원본에 없는 면을 지어내 버리고, 8번은 w01로 다시 만듦.
- 원본 사진(CC BY-SA 4.0, https://commons.wikimedia.org/wiki/<파일 이름>): w01 Silver Apple iPhone 18 Pro (2026-11-13) — Olgierd Rudak / w02 Apple iPhone 18 Pro (2026-11-13) 2 — Olgierd Rudak / w03 IPhone 18 Pro - black 01 — Farragutful / w05 Back Camera of iPhone 18 Pro Max — Kyu3a / w06 Dynamic Island of iPhone 18 Pro Max — Kyu3a / w08 Apple iPhone 18 Pro box (2026-11-12) — Olgierd Rudak / w09 IPhone 18 Pro photography Ostrów Tumski Wrocław Poland (2026-11-15) 1 — Olgierd Rudak / w10 Apple iPhone 18 Pro & Apple iPhone 17 Pro (2026-11-13) — Olgierd Rudak
- 음성: 타입캐스트 "영규"(tc_61130cd072f7b1a0c044b7f5). 음량 -16.2 LUFS. 길이 37.5초.
- 힉스필드 크레딧: 5초 영상 1개 35, 쓴 영상 10개 = 350(1210 → 860). 실패한 3번은 차감되지 않음.
