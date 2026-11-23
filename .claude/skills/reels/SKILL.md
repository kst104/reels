---
name: reels
description: 주제 하나만 받아 네이버 쇼핑 커넥트 링크를 붙일 세로형 쇼츠·릴스(약 35초)를 OpenMontage로 만드는 스킬. 작업은 항상 ~/Downloads/reels 폴더에서 한다. 조사 → 고정 A형식 대본 → im-not-ai 윤문 → 저장소 스크립트로 "남성1"(M1) 음성 직접 생성(Supertonic 3, 맥미니·클라우드 공통) → 사용자가 지정한 틀과 화면 방식으로 렌더(1번 Remotion 기본 틀 / 2번 HyperFrames 틀, 화면 방식 글자·움직임·사진, 1080x1920, 한글 자막, Pixabay 음악) → 출처 목록과 mp4를 reels/videos/에 정리. 트리거 — "reels", "/reels", "릴스 만들어줘", "쇼츠 만들어줘", "쇼핑 커넥트 영상", "[주제]로 릴스".
argument-hint: "[영상 주제] [1번|2번 프레임] [글자|움직임|사진] (선택: 붙일 상품)"
---

# reels — 쇼핑 커넥트용 쇼츠·릴스 제작 (v8, 2026-11-23: 끝 멘트 "소개한 제품은 프로필 링크에서", 프로필 링크 = 겅태의 상점, 상품은 상점 등록 후 소개)

## 이미 확정된 것 (매번 다시 묻지 않는다)

사용자가 2026-11-22 인터뷰로 확정한 기본값이다. 이 스킬을 쓰면 Why와 완료 기준은 아래로 정해진 것으로 본다.

- **작업 폴더:** `~/Downloads/reels` (이하 `REELS`). 릴스 작업은 이 폴더 안에서만 한다. 사용자가 고정한 규칙이다.
- **Why:** 네이버 쇼핑 커넥트용 영상을 매번 같은 방식으로 빠르게 만들기 위해서
- **완료 기준:** 사용자 목소리가 들어간 세로 mp4 1개 + 대본에 쓴 정보의 출처 목록, `REELS/videos/YYYY-MM-DD_<주제>/`에 정리
- **도구:** OpenMontage (github.com/OpenMontageInc/OpenMontage), 파이프라인 `animated-explainer`, `REELS/OpenMontage/`에 설치
- **프레임(렌더링 틀):** 사용자가 영상마다 지정한다(2026-11-22 확정).
  - **1번 = Remotion 기본 틀**(OpenMontage `remotion_render`, templated)
  - **2번 = HyperFrames 틀**(이 스킬의 `templates/frame2_hyperframes.py`)
  - 둘 다 1080x1920 세로, 한글 자막을 화면에 굽는다. 대본·음성·음악·자막·광고 표기는 같고 화면 움직임만 다르다.
  - 지정이 없으면 대본 확인 ① 때 한 번 묻는다. 임의로 고르지 않는다.
- **화면 방식:** 제작 의뢰를 받으면 영상마다 묻는다(2026-11-23 사용자 지정). 의뢰에 없으면 대본 확인 ① 때 프레임과 함께 묻고, 임의로 고르지 않는다.
  - **글자** = 글자 위주. 장면이 들어올 때만 움직인다(2026-11-22까지의 방식)
  - **움직임** = 글자 + 떠오르는 입자 배경, 장면마다 천천히 다가가는 카메라, 그림(김 나는 찻잔, 권고량 막대 도표)
  - **사진** = 움직임 + 장면마다 사진을 어둡게 깔고 천천히 확대·이동. 사진은 AI로 만든다(5-2절)
  - 움직임·사진은 2번 틀에만 있다. 1번(Remotion)을 고른 뒤 움직임·사진을 원하면 2번으로 바꿀지 묻는다.
- **음악:** Pixabay 무료 음악 (상업 사용 가능, 출처 표기 불필요)
- **음성:** Supertonic 3 "남성1"(파일명 접미사 `M1`). 이 스킬의 `templates/make_narration.py`로 직접 만든다. 맥미니 음성 프로그램(`localhost:7790`)과 같은 모델·목소리이고 서버 없이 돌아가므로, 맥미니든 클라우드든 한 세션에서 끝까지 만든다. 음성 때문에 맥미니로 넘기지 않는다(2026-11-22 사용자 지정). 사용자에게 따로 만들어 올리라고 하지 않는다(사용자가 불편하다고 명시함).
- **대본 형식:** 아래 "A형식" 고정. 콘셉트 3안을 제안하지 않는다.
- **사용자 확인을 받는 곳:** ① 대본 초안 ② 윤문 결과 ③ 완성 영상 ④ 추천 상품 ⑤ 게시 캡션. 그 밖의 OpenMontage 승인 단계(제안서·장면 계획 등)는 위 기본값으로 사용자가 미리 승인한 것으로 기록한다.

릴스 3곳 흐름(2026-11-23 사용자 지정): 제작전분석소(`~/Downloads/reels-analysis`) → 이 스킬(릴스제작소) → 제작후분석소(`~/Downloads/reels/post`) → 피드백 → 제작전분석소. 주제는 제작전분석소의 `reports/`와 `제작연결.md` 브리프에서 받는다. 시장·경쟁 분석과 게시 후 성과 분석은 하지 않는다. `post/` 폴더에는 쓰지 않는다. 자세한 경계는 `CLAUDE.md`와 `post/PIPELINE.md`.

받아야 하는 입력은 **주제**, **프레임 번호(1번/2번)**, **화면 방식(글자/움직임/사진)**이다. 붙일 상품이 정해져 있으면 함께 받고, 없으면 영상 끝은 "소개한 제품은 프로필 링크에서 확인"으로 둔다.

## A형식 (고정)

문장 6개 안팎. 첫 편 실측: 공백 제외 186자 → 원본 음성 36.7초, 문장 사이 무음을 0.6초로 줄여 32.2초, 끝 화면 포함 영상 35.6초. 이 비율(약 5.7자/초)로 분량을 잡는다.

| 구간 | 내용 |
|---|---|
| 첫 문장 | 오해를 깨는 한 줄. "○○보다 무서운 건 △△입니다." 같은 꼴, 20자 안팎 |
| 오해 | 사람들이 흔히 믿는 것 한 가지 |
| 원인 | 왜 위험하거나 틀렸는지. 출처 있는 사실 1~2개. **문장마다 마침표로 끝낸다**(쉼표로 끝나는 문장은 문장별 음성 생성 때 어색하게 끊긴다) |
| 수칙 | 숫자로 된 수칙 2~3개 (예: "41도 이하", "10분 이내") |
| 마무리 | "소개한 제품은 프로필 링크에서 확인하세요." (2026-11-23 변경: 인스타그램은 캡션 링크가 눌리지 않고 프로필 링크만 눌린다. 프로필 링크는 크리에이터샵 겅태의 상점 https://cshop.naver.com/geongtae_shop) |

마지막 화면에는 광고 표기를 글자로 넣는다: "이 영상은 네이버 쇼핑 커넥트 활동의 일환으로, 판매 발생 시 수수료를 제공받습니다." 이 문구는 2차 자료에서 확인한 표현이니, 네이버 공식 안내가 바뀌었는지 가끔 확인한다. 2번 틀은 이 문장('수수료'가 든 문장)을 끝 화면 **오른쪽 아래에 작게**(30px) 그린다(2026-11-23 사용자 지정). 게시 캡션에는 사용자 지정 문구 "이 포스팅은 네이버 쇼핑커넥트 활동의 일환으로, 판매 발생 시 수수료를 제공받습니다."를 글자 그대로 넣는다(9절). 건강 주제면 "지병이 있거나 고령이면 의사와 상담하세요." 같은 안내도 함께 넣는다.

참고 예시: `REELS/videos/2026-11-22_winter-hot-bath/` (script.txt, sources.md, artifacts/composition.json)

## 진행 순서

### 0. 준비

1. 현재 폴더가 `REELS`인지 확인한다. 아니면 사용자에게 알리고 `REELS`에서 작업한다.
2. `REELS/OpenMontage`가 없으면 설치한다(약 3분, 사용자에게 먼저 알린다):
   ```bash
   cd ~/Downloads/reels
   git clone --depth 1 https://github.com/OpenMontageInc/OpenMontage.git
   cd OpenMontage && make setup
   git checkout -- remotion-composer/package-lock.json   # setup이 바꾼 lockfile을 되돌려 저장소를 깨끗하게 둔다
   ```
   필요: Node.js 22 이상, ffmpeg, Python 3, git.
3. OpenMontage의 `CLAUDE.md`가 `AGENT_GUIDE.md`를 먼저 읽으라고 요구한다. 읽고 따르되, 이 스킬의 확정 기본값과 충돌하는 부분(콘셉트 3안, 렌더링 엔진 재선택, 단계별 승인)은 사용자의 확정 결정을 따르고 decision_log에 남긴다.
4. im-not-ai(`humanize-korean` 스킬)가 있는지 확인한다. 없으면 사용자에게 알리고 윤문 단계를 진행하지 않는다.
5. 사전 점검: `.venv/bin/python -c "from tools.tool_registry import registry; import json; registry.discover(); print(json.dumps(registry.provider_menu_summary()['composition_runtimes']))"`
   - 1번이면 `remotion`이 `false`일 때 멈추고 알린다.
   - 2번이면 `hyperframes`가 `true`인지 보고, `npx hyperframes doctor --json`에서 Node.js·FFmpeg·Chrome 항목이 `ok`인지 확인한다. 글꼴 처리에 `pip install fonttools brotli`가 필요하다.
6. 음성 준비(OpenMontage 폴더에서): `.venv/bin/python -m pip install -r ../.claude/skills/reels/templates/requirements-voice.txt`. 음성 모델(약 385MB)은 4절에서 처음 음성을 만들 때 내려받는다. 맥미니 음성 프로그램(7790)은 켜져 있지 않아도 된다.
7. 프로젝트 생성: `init_project('<id>', title='<한글 제목>', pipeline_type='animated-explainer')`. 중간 산출물은 `OpenMontage/projects/<id>/`, 최종 정리는 `REELS/videos/`.

### 1. 조사 (research)

- `skills/pipelines/explainer/research-director.md`를 읽고 `research_brief`를 만든다(스키마 검증 → checkpoint).
- 출처 우선순위: 한국 정부(질병관리청 등) → 국내 학회·대학병원 → 해외 공식 기관·논문 → 출처를 밝힌 언론. 블로그·출처 없는 기사는 근거로 쓰지 않는다.
- 확인되지 않는 내용은 넣지 않거나 "미확인"으로 표시한다. 반론이 있으면 단정하지 않는다. 해외 통계는 나라를 밝힌다.
- 조사를 별도 에이전트에 맡겨도 된다. 원문 인용과 URL을 받아 온다.

### 2. 제안 (proposal) — 자동 승인

- 콘셉트는 A형식 1안. 스키마가 3안을 요구하면 같은 형식의 첫 문장 변형으로 채우고 1안을 선택한다.
- `render_runtime`: 1번이면 `remotion`, 2번이면 `hyperframes`. `composition_mode: templated`, `renderer_family: explainer-teacher`, `music_source.source_type: bring_your_own`(provider `pixabay_music`).
- decision_log `render_runtime_selection`: Remotion과 HyperFrames를 모두 `options_considered`에 넣고, 고른 쪽은 "사용자 지정 N번 프레임"으로 적는다.
- `approval.status: "approved"`, `user_notes: "reels 스킬 상시 승인(2026-11-22)"`.

### 3. 대본 (script) — 확인 ①②

1. `script-director.md`를 읽고 A형식 초안을 쓴다. 문장마다 근거 출처를 옆에 단다. 화면에만 나올 숫자·문구도 함께 보여준다.
2. 사용자 확인 전에는 다음으로 가지 않는다.
3. 확정 대본을 `humanize-korean`으로 윤문한다(내용·숫자·출처 표기 불변, 줄 수 유지). 작업 폴더는 `OpenMontage/projects/<id>/humanize/` 아래에 둔다(저장소 최상위에 `_workspace/`를 만들지 않는다). 바뀐 문장만 전후로 보여주고 확인받는다.
4. `script` 아티팩트 저장 → checkpoint.

### 4. 음성 (직접 생성)

- 저장소의 스크립트 하나로 만든다. 맥미니와 클라우드에서 명령이 같다(2026-11-22 사용자 지정: 음성 때문에 맥미니로 넘기지 않는다):
  ```bash
  cd <REELS>/OpenMontage
  .venv/bin/python ../.claude/skills/reels/templates/make_narration.py projects/<id> --script <확정 대본 script.txt>
  ```
- 대본은 한 줄에 한 문장이고, 한 줄이 음성 한 구간이 된다. 결과는 `projects/<id>/assets/audio/`에 생긴다: 줄별 원본 `s1_M1.wav`…, 간격과 음량을 맞춘 `narration_norm.wav`, 문장별 시작·끝 `narration_timings.json`(`total`, `sections[s1..]`).
- 스크립트가 하는 일: Supertonic 3 "남성1"(M1), 속도 1.05·품질 8·줄 안 쉼 0.3초(맥미니 음성 프로그램 화면의 기본값)로 줄마다 음성을 만든다 → 말소리 앞뒤 무음을 자르고(여유 0.08초) 앞 0.3초, 문장 사이 0.6초, 끝 0.8초로 놓는다 → `loudnorm=I=-16:TP=-1.5:LRA=11`로 음량을 맞춘다.
- 첫 실행 때 모델(약 385MB)을 huggingface.co(`Supertone/supertonic-3`)에서 `~/.cache/supertonic3`로 내려받는다. 모델은 파일 하나가 245MB라 깃허브 저장소에 넣지 않았다. 내려받기가 막히면 스크립트가 이유를 알려 주니, 다른 목소리로 바꾸지 말고 "막혔을 때"대로 알린다.
- 숨이 차게 들리는 줄이 있으면 대본 줄을 고쳐 스크립트를 다시 돌리고 사용자에게 알린다(전체가 10초 남짓이라 한 줄만 따로 만들 필요가 없다).
- 맥미니 확인(2026-11-22): 같은 대본으로 맥미니 음성 프로그램(`localhost:7790`)과 줄별 길이가 샘플 수까지 같았다. 파형은 만들 때마다 조금씩 달라 똑같지는 않다. 대추차 대본 6줄에 12초, 결과 음량 -16.6 LUFS.
- 참고(스킬은 쓰지 않는다) — 맥미니 음성 프로그램 호출법: `POST http://localhost:7790/api/tts`에 JSON `{"text", "voice": "M1", "lang": "ko", "speed": 1.05, "steps": 8, "pause": 0.3, "format": "wav"}` → `{"file", "seconds", ...}`, 파일은 `GET /audio/<file>`.
- 사용자가 음성 파일을 직접 준 경우에만: 한 파일이면 `ffmpeg silencedetect=noise=-35dB:d=0.35`로 1.3초 이상 무음을 찾아 문장 경계를 잡고, 위와 같은 간격·음량으로 맞춘다.
- 스크립트 테스트: 저장소 최상위에서 `OpenMontage/.venv/bin/python -m pytest tests`(모델 없이 돈다. `pip install pytest`가 필요하다).

### 5. 장면·소재·편집·합성

- 단계마다 `skills/pipelines/explainer/<stage>-director.md`를 먼저 읽는다. scene_plan·asset_manifest·edit_decisions는 스키마 검증 후 checkpoint(자동 승인)한다.
- edit_decisions 스키마는 컷에 문구 필드를 허용하지 않는다. 그래서 Remotion에 넘길 props는 `artifacts/composition.json`에 따로 만들고 `video_compose`의 `remotion_render`에 `composition_data`로 넘긴다.
- 장면(첫 편에서 확인한 설정):
  - 색: 배경 `#0F1B26`, 글자 `#F4F7FA`, 강조 `#FF8A3D`, 경고 `#FF5A5F`
  - 첫 장면 `hero_title`(text, heroSubtitle)
  - 설명·경고 `callout`(title, text, `fontSize: 58`, `titleFontSize: 46`). 기본 32는 세로 화면에서 너무 작다.
  - 숫자 `stat_card`(stat, subtitle)
  - 짧은 문장 `text_card`(text). **text_card는 subtitle을 화면에 표시하지 않는다.** 그래서 마지막 장면(광고 표기)은 `callout`(title "소개한 제품은 프로필 링크에서", text 광고 표기+안내, `fontSize: 40`, `titleFontSize: 56`)으로 만든다.
  - `progress_bar`는 0~100 값과 퍼센트가 화면에 보인다. 실제 데이터가 없으면 쓰지 않는다(근거 없는 숫자 금지).
  - 컴포넌트 컷의 `source`는 `""`로 둔다(값이 있으면 검증기가 파일을 찾다 실패한다).
- 음악: `pixabay_music`(query 예: "calm ambient piano", `min_duration` 40, `output_path`를 반드시 `projects/<id>/assets/music/`로). 403이 나도 도구가 재시도하면 통과한 적이 있다. 볼륨 0.07, fadeIn 1.5초, fadeOut 2.5초.
- 자막: `captions`에 어절 단위 `{word, startMs, endMs}`. 문장 구간은 실측 시각, 문장 안 어절은 글자 수 비례로 나눈다. `captionStyle: {wordsPerPage: 3, fontSize: 64, bottomOffset: 260}`, `captionProps: {fontFamily: "Noto Sans CJK KR, Apple SD Gothic Neo, sans-serif", wordSeparator: " "}`.
- 마지막 장면은 내레이션이 끝난 뒤 약 3초 더 보여 준다.
- 렌더 전 `CompositionValidator`가 `valid: True`여야 한다.

#### 5-1. 1번 프레임(Remotion) 렌더

- 렌더: `video_compose.execute({'operation':'remotion_render','composition_data':comp,'output_path':'projects/<id>/renders/final.mp4','profile':'tiktok','proposal_packet':pp})`. 약 4~5분.
  - Remotion이 브라우저를 받으려다 `remotion.media` 접속에 실패하면, 설치된 Chrome headless shell을 `remotion_browser_executable`로 지정한다.
  - Linux 클라우드에서는 한글 글꼴이 없을 수 있다: `apt-get install -y fonts-noto-cjk`. 맥은 기본 한글 글꼴로 대체된다.

#### 5-2. 2번 프레임(HyperFrames) 렌더

- composition.json은 1번과 같은 형식으로 만든다(컷·자막·오디오). 2번일 때만 컷에 선택 필드 `hf`를 넣는다(1번 Remotion에는 넣지 않는다):

  | 컷 | `hf` | 화면 |
  |---|---|---|
  | `hero_title` | `{"emphasis": "시간", "icon": "clock"}` | 강조 낱말을 크게, 그 낱말을 말할 때 튀어나옴. 시계 바늘 회전 |
  | `callout` | `{"fx": "strike", "stamp": "오해", "lines": ["1줄", "2줄"]}` | 줄마다 취소선 + 도장 |
  | `callout` | `{"fx": "thermo"}` / `{"fx": "arrow_down"}` | 온도계가 차오름 / 아래 화살표가 떨어짐 |
  | `stat_card` | `{"tag": "기억하세요 ①"}` | 숫자가 0부터 올라감(`stat` 앞 숫자). subtitle의 ` · `는 줄바꿈 |
  | `text_card` | `{"tag": "기억하세요 ③", "icon": "check"}` | 체크 표시, `, ` 뒤를 강조색 줄로 |
  | `hero_title`·`stat_card`·`text_card` | `{"icon": "cup"}` | 김이 피어오르는 찻잔 그림(움직임·사진 방식만. 글자 방식에서는 체크 표시) |
  | `stat_card` | `{"gauge": {"value": 30, "max": 50, "max_label": "하루 권고 50g", "mark": 25, "mark_label": "절반"}}` | 기준 대비 막대가 차오름. 절반을 넘으면 빨간색(움직임·사진 방식만). 근거 있는 숫자만 쓴다 |
  | 모든 컷 | `{"photo": "assets/images/c1.webp", "photo_focus": "50% 40%"}` | 사진을 어둡게 깔고 천천히 확대·이동(사진 방식만, 끝 화면 제외). 경로는 프로젝트 폴더 기준 |

  화면 방식은 composition.json 맨 위 `"hf_style"`에 `"text"`(글자, 기본값) / `"motion"`(움직임) / `"photo"`(사진)로 적는다.
  마지막 컷은 항상 끝 화면(title + 아래 화살표 + text 상자)으로 그린다. text 가운데 '수수료'가 든 문장(광고 표기)은 상자에서 빼 오른쪽 아래에 작게 그리고, 나머지(건강 안내 등)만 상자에 둔다. text에 광고 표기가 없으면 틀이 경고한다. 예시: 글자 `REELS/videos/2026-11-22_winter-hot-bath/artifacts/hyperframes/composition_hf.json`, 사진 `REELS/videos/2026-11-22_jujube-tea-sugar/artifacts/composition_hf_photo.json`
- 사진 방식의 사진 만들기(2026-11-23 대추차 시험본에서 확인):
  - Hugging Face 커넥터의 `gr1_z_image_turbo_generate`(Z-Image Turbo)로 장면마다 1장, `resolution: "864x1536 ( 9:16 )"`, `random_seed: false`와 seed를 적어 다시 만들 수 있게 한다.
  - 프롬프트는 영어로 "Realistic photograph, <장면 내용>, vertical composition, no text, no logos". 실제 상표·사람 얼굴은 넣지 않는다.
  - 결과 webp를 `projects/<id>/assets/images/c<번호>.webp`로 복사한다. 무료 사용량이 하루 8장쯤에서 끝났다. 모자라면 다른 장면 사진을 `photo_focus`를 바꿔 다시 쓴다.
  - 사진은 장면 내용을 돕는 그림일 뿐 근거가 아니다. 사진 속 장면을 사실처럼 말하지 않는다.
- 작업 폴더 만들기: `python <REELS>/.claude/skills/reels/templates/frame2_hyperframes.py projects/<id>` → `projects/<id>/hyperframes/`(index.html, 음성·음악 복사, GSAP, 쓰인 글자만 남긴 한글 글꼴 woff2).
- 작업 폴더에서 차례로 확인한다. 앞 단계에서 오류가 나면 렌더하지 않는다:
  1. `npx hyperframes lint --json` → 오류 0. `nested_structure_needs_subcomposition` 같은 구조 권장 경고는 무시해도 된다.
  2. `npx hyperframes validate --json` → 오류 0
  3. `npx hyperframes inspect --json` → 오류 0. 배경 빛 무늬의 `panel_out_of_canvas` 정보는 의도된 것이다.
  4. `npx hyperframes snapshot --at <장면마다 한 시각>` → `.hyperframes/artifacts/snapshots/`의 contact-sheet를 직접 본다(한글, 자막 띄어쓰기, 효과 위치).
  5. `npx hyperframes render --output ../renders/final.mp4 --fps 30 --quality high --strict`(첫 편 1분 37초)
- 글꼴은 `@font-face`로 파일을 선언해야 렌더에 쓰인다(안 하면 lint 오류). 틀이 리눅스는 Noto Sans CJK KR, 맥은 Apple SD Gothic Neo(`/System/Library/Fonts/AppleSDGothicNeo.ttc`, 2026-11-22 맥미니 확인, 렌더 23초)를 찾아 쓴다. 못 찾으면 `--font-regular`, `--font-bold`로 지정한다. 글꼴에 따라 글자 폭이 달라 줄바꿈 위치가 바뀔 수 있으니 snapshot에서 확인한다.
- 자막에서 강조되는 낱말은 길이에 맞춰 1.03~1.08배로 커진다(`caption_pop_scale`). 긴 낱말이 1.08배로 커지면 옆 빈칸을 덮어 띄어쓰기가 사라져 보여서 2026-11-22에 고쳤다. 틀 테스트: `python -m pytest tests/test_frame2_hyperframes.py`.
- 사진 방식 실측(대추차 40.6초, 맥미니): 렌더 37초. 렌더 그대로는 25MB(글자 방식 8MB)라, `videos/`에 넣기 전에 `ffmpeg -i final.mp4 -c:v libx264 -preset slow -crf 23 -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 128k <주제>_final.mp4`로 줄인다(7.7MB, 화질 차이 거의 없음). 크롬 업로드 도구가 한 번에 10MB까지만 올린다.
- 첫 편 실측: 평균 음량 -17.4dB(1번은 -20.5dB). 6절 음량 기준을 똑같이 적용한다.

### 6. 확인과 정리 — 확인 ③

- `ffprobe`로 1080x1920·길이를 확인하고, `volumedetect` 평균이 -24dB보다 작으면 음량을 다시 맞춘다.
- 장면마다 프레임을 한 장씩 뽑아 직접 본다: 한글 깨짐, 글자 크기, 광고 표기 노출 여부.
- `REELS/videos/YYYY-MM-DD_<주제>/`에 정리(프레임과 상관없이 같은 이름): `<주제>_final.mp4`, `script.txt`, `sources.md`(문장별 출처·미확인·음악 라이선스), `audio/`(원본·편집 음성, 음악, timings), `artifacts/`(json 전부, 2번이면 `artifacts/hyperframes/`에 index.html과 composition_hf.json). `sources.md`에 쓴 프레임(1번/2번)과 화면 방식, **근거가 된 제작전분석소 보고서 링크**(예: `reels-analysis/reports/<파일>.md`, `제작연결.md`의 해당 줄)와 **제작 요청 프롬프트**(사용자의 주제 요청 원문, 마지막에 확정한 것까지)를 적는다. 사진 방식이면 사진을 `artifacts/images/`에 두고, `sources.md`에 AI로 만든 사진이라는 것과 도구·seed를 적는다. 2번의 글꼴 파일은 저장소에 넣지 않는다.
- 사용자에게 mp4와 출처를 보여주고 확인받는다.
- OpenMontage 저장소에 변경이 남지 않았는지 `git status`로 확인한다(`projects/`는 git에서 무시된다).

### 7. 상품 추천 — 확인 ④ (2026-11-22 추가)

- 고르는 기준(2026-11-23 사용자 지정): **쇼핑 커넥트에 등록돼 링크가 나오는 상품이 1순위, 주간 판매 순위가 2순위.** 영상 내용과 맞는 상품을 최근 1주 판매 순위 순서로 3~7개 후보 목록으로 보여 주고, 사용자가 브랜드 커넥트에서 위에서부터 찾아 링크가 나오는 상품을 쓴다(가습기 편: 4위 윤남텍은 없어 70위 에어메이드로).
- 후보는 **제작 의뢰의 마지막 프롬프트(사용자가 마지막으로 정한 주제·상품 요청)에 맞는 것**을 고른다. 맞는 상품이 쇼핑 커넥트에 없거나 내용과 잘 맞지 않으면 임의로 다른 상품을 넣지 말고 사용자에게 묻는다(2026-11-23 사용자 지정). 링크를 받으면 그 상품이 마지막 프롬프트와 맞는지 다시 확인하고, 어긋나면 게시 전에 묻는다.
- 자료: 네이버+ 스토어 베스트 구매 순위(네이버플러스 스토어 구매 데이터 기반). 주소 형식 `https://snxbest.naver.com/product/best/buy?categoryId=<대분류ID>&sortType=PRODUCT_BUY&periodType=WEEKLY&ageType=ALL` (디지털/가전 = 50000003). 목록은 화면에서 그려지므로 `firecrawl_scrape`의 query(freeform)로 목록을 받고, 고를 후보의 상품명·가격은 directQuote로 원문 확인한다. 순위 숫자는 요약 추출값이라 "약"으로 말한다.
- 추천할 때 근거(카테고리, 주간, 기준일, 순위)를 함께 보여준다. 쇼핑 커넥트 등록 여부와 수수료율은 브랜드 커넥트에 로그인해야 보이므로 "미확인"으로 적는다.

### 8. 쇼핑 커넥트 링크

- 링크는 사용자가 네이버 브랜드 커넥트에서 발급해 붙여 준다(로그인이 필요해 클라우드 세션에서는 발급할 수 없다). 맥미니의 Claude in Chrome으로도 발급할 수 없다(2026-11-22 확인: 브랜드 커넥트 사이트가 브라우저 도구에서 열리지 않는다). 추천 상품의 링크를 받지 못하면 사용자가 이미 가진 링크의 상품(대안)으로 바꿀지 묻는다.
- naver.me 링크는 `brandconnect.naver.com/affiliates/...?channelProductNo=<상품번호>`로 연결된다. 상품 페이지는 로그인 화면으로 막혀 상품명을 확인하지 못할 수 있다. 그때는 캡션에 상품명을 단정하지 않고 사용자가 부른 이름을 쓴다.
- 캡션 속 링크는 인스타그램에서 눌리지 않는다. 프로필 링크는 크리에이터샵 "겅태의 상점"(https://cshop.naver.com/geongtae_shop)으로 고정돼 있다(2026-11-23 사용자 지정). 영상마다 프로필 링크를 바꾸지 않는다. 프로필은 인스타그램 앱에서만 고칠 수 있다(웹 설정 화면은 "링크 수정은 모바일에서만 가능"이라 막혀 있고 Windsor.ai로도 못 고친다).
- **링크는 상품·게시물마다 따로**(2026-11-23 사용자 지정): 이 릴스에 쓸 쇼핑 커넥트 링크는 이 게시물 전용으로 새로 발급받는다(다른 릴스·블로그에 쓴 링크를 다시 쓰지 않는다). 받은 링크를 `caption.md`와 `docs/shop-sync.md` 링크 표에 같이 적는다.
- **릴스 상품은 컬렉션에**(2026-11-23 사용자 지정): 게시하면 소개한 상품이 들어갈 상점 컬렉션을 `docs/shop-sync.md` 0-1절에 정하고(맞는 게 없으면 새 컬렉션), 사용자에게 상점 등록과 컬렉션 지정을 같이 요청한다.
- **콘텐츠와 상점 동기화**(2026-11-23 사용자 지정): 릴스·유튜브·블로그의 모든 콘텐츠가 상점 상품과 이어지게 `docs/shop-sync.md` 대응표(콘텐츠 → 상품 → 상점 상태)를 고친다. 게시하면 "넣을 것"에, 콘텐츠를 지우면 그 상품만 쓰던 경우 "뺄 것"에 올리고 사용자에게 상점 반영을 요청한다.
- **상점 등록 먼저**(2026-11-23 사용자 지정): 소개할 쇼핑 커넥트 상품은 게시 전에 겅태의 상점에 등록돼 있어야 한다. 등록은 사용자가 브랜드 커넥트에서 한다(로그인 필요). 게시 직전에 `firecrawl_scrape`로 https://cshop.naver.com/geongtae_shop을 읽어 그 상품(상품명 또는 `channelProductNo`)이 보이는지 확인한다(크롬 도구로는 열리지 않는다). 없으면 게시하지 말고 사용자에게 등록을 요청한다.

### 9. 인스타그램 게시 — 확인 ⑤

- mp4를 먼저 깃허브 `main`에 올린다. 영상 주소는 `https://raw.githubusercontent.com/kst104/reels/main/videos/<폴더>/<파일>.mp4`(공개 저장소).
- 캡션 틀: 첫 문장 → 원인 2줄 → 수칙 → "<용도> <상품 호칭>: <링크>" → 바로 아래 광고 표기 "이 포스팅은 네이버 쇼핑커넥트 활동의 일환으로, 판매 발생 시 수수료를 제공받습니다."(글자 그대로, 2026-11-23 사용자 지정) → 출처 → 의료 안내 → 해시태그(사용자가 더 넣으면 따른다).
- 사용자가 캡션을 확인하면 Windsor.ai `instagram` 커넥터의 `create_video_post`로 게시한다(계정 kst1_04, `thumb_offset: 1500`, `share_to_feed: true`).
- 게시 뒤 `get_data`(fields: media_id, media_permalink, media_product_type, timestamp, date_preset `last_1dT`)로 주소를 확인한다. Windsor.ai 체험(TRIAL) 요금제에서는 `force_refresh`를 쓸 수 없다.
- 영상 폴더에 `caption.md`(게시 주소, 상품 링크, 추천 근거, 캡션, **실제 게시한 해시태그 그대로**)를 남기고, 노션·아티팩트 영상 목록에 게시 링크를 적고, 슬랙 `#reels`에 알린다.

## 연결된 곳과 갱신 규칙

- 원본은 깃허브 `kst104/reels`. 노션 "릴스"(https://app.notion.com/p/420cac3237508175b737c2f68ae4e034), 아티팩트 "릴스"(https://claude.ai/artifact/CUs4fAxQX4zuLcb3CznmK2, 원본 `docs/reels-hub.html`), 슬랙 `#reels`(C0CKTUB04FP)가 연결돼 있다.
- 이 스킬이나 작업 규칙을 바꾸면 네 곳을 함께 갱신한다: 깃허브 커밋 → 아티팩트 재게시 → 노션 갱신 → 슬랙에 바뀐 점과 의견 요청.
- 영상을 하나 끝내면 `videos/`에 정리하고 깃허브에 올린 뒤, 노션·아티팩트 영상 목록에 추가하고 슬랙에 알린다. 음악 원본 파일은 저장소에 넣지 않는다.

## 막혔을 때

① 무엇을 시도했고 ② 무엇이 실패했고 ③ 원인이 접속·권한·도구 버그·품질 중 무엇이며 ④ 다음 선택지와 ⑤ 추천안을 알린다. 사용자 승인 전에는 대체 경로로 진행하지 않는다.

## 주의

- 건강·의학 주제는 진단·치료를 대신하지 않는다는 뜻이 드러나게 쓰고, 과장하지 않는다.
- Remotion은 회사 규모에 따라 유료 라이선스가 필요할 수 있다. 개인 사용이 아니게 되면 remotion.dev/license를 확인한다.
- HyperFrames는 Apache 2.0이다.
- OpenMontage의 라이선스는 AGPL-3.0이다. 코드를 고쳐 배포하거나 서비스로 제공할 계획이 생기면 라이선스 조건을 따로 확인한다.

## 아직 확인하지 않은 부분

- 클라우드 세션에서 `make_narration.py`가 음성 모델을 내려받는지(huggingface.co 접속) → 다음 클라우드 영상에서 확인한다. 맥미니에서는 2026-11-22에 확인했다(모델이 이미 받아져 있던 상태).
- 1번 틀(Remotion)은 맥미니에 설치만 했고 렌더는 아직 돌려 보지 않았다. 2번 틀은 클라우드와 맥미니 양쪽에서 확인했다(2026-11-22).
- 사진 방식은 맥미니에서만 렌더해 봤다(2026-11-23). 사진 방식으로 인스타그램에 올린 적은 아직 없다. 실제 같은 AI 사진에 인스타그램 "AI 정보" 표시를 붙여야 하는지는 확인하지 않았다 → 처음 게시할 때 확인한다.
- 문장 안 어절 자막 타이밍은 추정치다(문장 경계는 실측). 음성 인식 도구가 생기면 단어 단위로 맞춘다.
