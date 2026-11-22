# 출처 — 겨울 대추차, 효능보다 먼저 볼 건 설탕 (2026-11-22)

- 소재: 사용자 블로그 「"대추차 한 잔 마시고 왔어요"... 응급실 의사가 겨울 식탁에서 설탕부터 보는 이유」(2026-11-21) https://blog.naver.com/kst104/224485952422
- 렌더 틀: **2번 프레임(HyperFrames)**

| 줄 | 내용 | 출처 |
|---|---|---|
| 2 | 시판 대추차 스틱 한 봉 당류 10그램쯤 | 담터 대추차 15g 1포 영양표시(열량 60kcal, 당류 10g, 1일 기준치 10%). 표시 내용을 옮긴 사이트 3곳이 일치: https://onlyknowledge.tistory.com/939 , https://geniet.co.kr/calorie-calculator/food-detail/153835 , fatsecret.kr. 제조사 원문은 미확인 |
| 3 | 하루 기준 50그램 미만, 세 잔이면 절반을 넘김 | WHO Healthy diet: 유리당은 총열량 10% 미만, 2,000kcal 기준 50g(약 12티스푼). https://www.who.int/news-room/fact-sheets/detail/healthy-diet — 세 잔 30g은 50g의 60% |
| 4 | 65도 넘는 뜨거운 음료는 식도암 발암 추정 요인 | IARC 보도자료 244(Monographs Vol.116): 65도 넘는 매우 뜨거운 음료는 2A군(인체 발암 추정). https://www.iarc.who.int/wp-content/uploads/2018/07/pr244_E.pdf |
| 5 | 하루 한 잔·식후에·설탕 없이 직접 끓이기 | 블로그 저자 권고. 공식 기준 아님 |
| 5 | 한 김 식혀서 | 위 IARC 65도 기준에 맞춘 안내 |

## 미확인
- 담터 대추차 당류 10g의 제조사 원문(2차 사이트 3곳 일치)
- 블로그의 "한 봉지 15g 안팎", "큰 컵 20g 이상"은 대표 제품(10g)과 달라 대본에 쓰지 않음
- 광고 표기 문구: 2차 자료 기준. 네이버 공식 안내를 확인할 것

## 음악
Pixabay "Ambient Piano" (leberch), 검색어 "calm ambient piano" — Pixabay Content License (상업 사용 가능, 출처 표기 불필요). 음악 파일은 저장소에 넣지 않았다.

## 제작 기록 (맥미니, 2026-11-22)
- 음성: 맥미니 localhost:7790 `POST /api/tts` {"voice":"M1","lang":"ko","speed":1.05,"steps":8,"pause":0.3,"format":"wav"} → `GET /audio/<file>`. 문장 6개를 따로 만들어 앞뒤 무음을 자르고 앞 0.3초·문장 사이 0.6초·끝 0.8초로 이음, loudnorm(-16 LUFS). 내레이션 37.6초 (`artifacts/build_narration.py`)
- 영상: `jujube-tea-sugar_final.mp4` 1080x1920, 30fps, 40.6초(끝 화면 3초 포함), 평균 음량 -17.5dB
- 자막 수정(같은 날 재렌더): 강조되는 낱말이 1.08배로 커지면서 옆 빈칸을 덮어 "음료는국제암연구기관이"·"요인으로분류했습니다."·"생각하시죠?시판"처럼 붙어 보였다. 이 영상의 `artifacts/hyperframes/index.html`에서만 긴 낱말의 확대율을 줄였다(8자 1.03배 ~ 3자 이하 1.08배 그대로, 43개 낱말은 변화 없음). 틀(`frame2_hyperframes.py`)은 고치지 않았다 — 수정 제안 중. 재렌더 뒤 lint·validate·inspect 오류 0, 장면 10개와 자막 전후 비교를 직접 확인
- 렌더: 2번 프레임(HyperFrames CLI 0.9.80, GSAP 3.15.0). lint 오류 0(구조 권장 경고만), validate·inspect 오류 0(배경 빛 무늬 panel_out_of_canvas는 의도). 렌더 28.4초
- 글꼴: Noto Sans CJK KR(SIL OFL 1.1)을 쓰인 글자만 남겨 woff2로 사용. 맥의 Apple SD Gothic Neo는 Aside 샌드박스에서 읽을 수 없어 쓰지 않음. 글꼴 파일은 저장소에 넣지 않았다.

## 사진 방식 시험본 (맥미니, 2026-11-23)
- 파일: `jujube-tea-sugar_photo.mp4` 1080x1920, 30fps, 40.6초. 화면 방식 **사진**(`artifacts/composition_hf_photo.json`, `hf_style: "photo"`). 인스타그램에는 올리지 않았다(게시된 영상은 `jujube-tea-sugar_final.mp4`)
- 사진 8장(`artifacts/images/c1~c8.webp`)은 **AI로 만든 사진**이다: Hugging Face `mcp-tools/Z-Image-Turbo`, 864x1536, steps 8, seed c1=11, c2=21, c3=31, c4=41, c5=51, c6=61, c7=71, c8=81. 9번째 장면은 무료 사용량이 끝나 c1 사진을 다른 부분으로 잘라 다시 썼다. 사진은 장면을 돕는 그림이며 근거 자료가 아니다
- 막대 도표: 10g·50g·30g을 WHO 하루 권고 50g 대비로 그림(위 출처와 같음). 30g 장면의 "절반" 표시는 25g
- 렌더: 2번 틀(HyperFrames CLI 0.9.80), 글꼴 Apple SD Gothic Neo. lint·validate·inspect 오류 0, 렌더 37초. 저장소에는 CRF 23으로 다시 압축한 7.7MB 파일을 넣었다(원본 25MB)
