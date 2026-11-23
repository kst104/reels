# 출처 — 가습기 물, 정수기 물이 더 안전할까 (2026-11-23)

- 기획: 릴스분석소 W47 유튜브 쇼핑 쇼츠 8위 "가습기의 진실"(꿀팁노트, https://www.youtube.com/shorts/iIss_e7-u2Q) 구조를 참고. 그 영상의 건강 주장(수돗물 염소의 세균 억제, 12시간, 평당 40ml)은 공식 근거를 찾지 못해 대본에서 뺐다.
- 렌더 틀: **2번 프레임(HyperFrames)**, 화면 방식 **사진**

| 줄 | 내용 | 출처 |
|---|---|---|
| 1~2 | 정수기 물이 더 안전할까 / 수돗물이냐 정수기 물이냐 고민 | 질문 문장(사실 주장 아님) |
| 3 | 미국 환경보호청은 오히려 증류수를 권함 | US EPA Indoor Air Facts No. 8 "Use bottled water labeled 'distilled.'" https://www.epa.gov/sites/default/files/2014-08/documents/humidifier_factsheet.pdf (원 발행연도 미확인). 같은 취지: US CPSC Publication 5046 "Use distilled or demineralized water" https://www.cpsc.gov/s3fs-public/5046.pdf |
| 4 | 초음파식은 수돗물에서 미세입자가 가장 많이 나왔다는 국내 연구 | 윤충식 외, 한국공중보건학회지 2019;56(1) (서울대 보건환경연구소·국립환경과학원), doi 10.17262/KJPH.2019.06.56.1.33 — 입자·중금속 수돗물 > 정수기 물 > 증류수. 세균 비교는 하지 않음 |
| 5 | 하루 지난 물은 버리고 새 물로 | 질병관리본부·보건복지부 2011-11-04 "하루가 지난 물은 새 물로 교체한다" https://www.korea.kr/news/healthView.do?newsId=148721624 |
| 6 | 이틀마다 닦고, 주 1회 중성세제로 씻어 3회 이상 헹굼 | 같은 자료(질병관리본부 2011) |
| 6 | 살균제는 절대 넣지 말 것 | 질병관리본부 2011 "가습기 살균제 사용 중단을 강력 권고" https://www.korea.kr/news/policyNewsView.do?newsId=148721617 |
| 7 | 실내 습도 40~50% | 질병관리청 국가건강정보포털 '겨울철 한파대비 건강수칙' https://health.kdca.go.kr/healthinfo/biz/health/gnrlzHealthInfo/gnrlzHealthInfo/gnrlzHealthInfoView.do?cntnts_sn=2048 |

## 미확인·상충
- "정수기 물에서 세균이 더 빨리 번식한다"는 한국 정부기관·한국소비자원 시험은 찾지 못했다. KBS 팩트체크K(2020-09-30)도 "체계적으로 연구된 바는 없습니다"라고 했다. 그래서 "어떤 물이 더 안전하다"고 단정하지 않았다.
- 적정 습도: 질병관리청 40~50%, 미국 CPSC 30~50%, EPA 50% 이하. 블로그에 흔한 "40~60%(정부 권고)"는 정부 원문 미확인.
- "평당 40ml" 가습량은 정부 근거 없음. 공기청정협회 단체표준 KARSE B 0050:2010의 아파트 필요 가습량 14.1 mL/h·㎡(1평 약 47mL/h)가 가장 가까운 기준(업계 표준).
- 광고 표기 문구: 2차 자료 기준. 네이버 공식 안내를 확인할 것.

## 음악
Pixabay "Ambient Piano" (leberch), 검색어 "calm ambient piano" — Pixabay Content License (상업 사용 가능, 출처 표기 불필요). 음악 파일은 저장소에 넣지 않았다.

## 사진 (AI)
- 7장(`artifacts/images/c1~c7.webp`)은 **AI로 만든 사진**이다. Hugging Face 무료 사용량이 끝나 **이 맥미니 안에서** 만들었다: Open Generative AI의 sd.cpp 엔진(Metal) + Z-Image Turbo Q4_K, 720x1280, steps 8, cfg 1.0, euler/simple, seed c1=101 … c7=107. 프롬프트는 `artifacts/gen_photos.sh`. 한 장에 4~6분.
- c7(살균제 주의) 컷은 c6 사진을 다른 부분으로 잘라 다시 썼다. 사진은 장면을 돕는 그림이며 근거 자료가 아니다.

## 제작 기록 (맥미니, 2026-11-23)
- 음성: `make_narration.py`(Supertonic 3 M1), 7줄, 내레이션 35.5초
- 윤문: humanize-korean v2.4 light 경로, 7줄 중 2줄 수정, 게이트 수렴
- 영상: `humidifier-water_final.mp4` 1080x1920, 30fps, 38.6초(끝 화면 3초 포함), 평균 음량 -17.4dB, CRF 23 압축 7.2MB
- 렌더: 2번 프레임(HyperFrames CLI), lint·validate·inspect 오류 0(대비 경고 1건은 장면이 사라지는 순간의 태그). 렌더 28초
