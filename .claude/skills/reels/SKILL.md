---
name: reels
description: 주제 하나만 받아 네이버 쇼핑 커넥트 링크를 붙일 세로형 쇼츠·릴스(약 35초)를 OpenMontage로 만드는 스킬. 작업은 항상 ~/Downloads/reels 폴더에서 한다. 조사 → 고정 A형식 대본 → im-not-ai 윤문 → 맥미니 localhost:7790 "남성1"(M1) 음성 → Remotion 기본 틀 렌더(1080x1920, 한글 자막, Pixabay 음악) → 출처 목록과 mp4를 reels/videos/에 정리. 트리거 — "reels", "/reels", "릴스 만들어줘", "쇼츠 만들어줘", "쇼핑 커넥트 영상", "[주제]로 릴스".
argument-hint: "[영상 주제] (선택: 붙일 상품)"
---

# reels — 쇼핑 커넥트용 쇼츠·릴스 제작 (v2, 2026-11-22)

## 이미 확정된 것 (매번 다시 묻지 않는다)

사용자가 2026-11-22 인터뷰로 확정한 기본값이다. 이 스킬을 쓰면 Why와 완료 기준은 아래로 정해진 것으로 본다.

- **작업 폴더:** `~/Downloads/reels` (이하 `REELS`). 릴스 작업은 이 폴더 안에서만 한다. 사용자가 고정한 규칙이다.
- **Why:** 네이버 쇼핑 커넥트용 영상을 매번 같은 방식으로 빠르게 만들기 위해서
- **완료 기준:** 사용자 목소리가 들어간 세로 mp4 1개 + 대본에 쓴 정보의 출처 목록, `REELS/videos/YYYY-MM-DD_<주제>/`에 정리
- **도구:** OpenMontage (github.com/OpenMontageInc/OpenMontage), 파이프라인 `animated-explainer`, `REELS/OpenMontage/`에 설치
- **렌더링:** Remotion, 기본 틀(templated), 1080x1920 세로(`profile: tiktok`), 한글 자막을 화면에 굽는다
- **음악:** Pixabay 무료 음악 (상업 사용 가능, 출처 표기 불필요)
- **음성:** 맥미니 `localhost:7790` 음성 서버, "남성1"(파일명 접미사 `M1`). 음성은 스킬이 직접 만든다. 사용자에게 따로 만들어 올리라고 하지 않는다(사용자가 불편하다고 명시함).
- **대본 형식:** 아래 "A형식" 고정. 콘셉트 3안을 제안하지 않는다.
- **사용자 확인을 받는 곳:** ① 대본 초안 ② 윤문 결과 ③ 완성 영상. 그 밖의 OpenMontage 승인 단계(제안서·장면 계획 등)는 위 기본값으로 사용자가 미리 승인한 것으로 기록한다.

받아야 하는 입력은 **주제**뿐이다. 붙일 상품이 정해져 있으면 함께 받고, 없으면 영상 끝은 "설명란 링크 확인"으로 둔다.

## A형식 (고정)

문장 6개 안팎. 첫 편 실측: 공백 제외 186자 → 원본 음성 36.7초, 문장 사이 무음을 0.6초로 줄여 32.2초, 끝 화면 포함 영상 35.6초. 이 비율(약 5.7자/초)로 분량을 잡는다.

| 구간 | 내용 |
|---|---|
| 첫 문장 | 오해를 깨는 한 줄. "○○보다 무서운 건 △△입니다." 같은 꼴, 20자 안팎 |
| 오해 | 사람들이 흔히 믿는 것 한 가지 |
| 원인 | 왜 위험하거나 틀렸는지. 출처 있는 사실 1~2개. **문장마다 마침표로 끝낸다**(쉼표로 끝나는 문장은 문장별 음성 생성 때 어색하게 끊긴다) |
| 수칙 | 숫자로 된 수칙 2~3개 (예: "41도 이하", "10분 이내") |
| 마무리 | "자세한 건 설명란 링크에서 확인하세요." |

마지막 화면에는 광고 표기를 글자로 넣는다: "이 영상은 네이버 쇼핑 커넥트 활동의 일환으로, 판매 발생 시 수수료를 제공받습니다." 이 문구는 2차 자료에서 확인한 표현이니, 네이버 공식 안내가 바뀌었는지 가끔 확인한다. 건강 주제면 "지병이 있거나 고령이면 의사와 상담하세요." 같은 안내도 함께 넣는다.

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
5. 사전 점검: `.venv/bin/python -c "from tools.tool_registry import registry; import json; registry.discover(); print(json.dumps(registry.provider_menu_summary()['composition_runtimes']))"` → `remotion`이 `false`면 멈추고 알린다.
6. 음성 서버 확인: `curl -s -o /dev/null -w "%{http_code}" http://localhost:7790/`. 응답이 없으면 사용자에게 음성 프로그램을 켜 달라고 한다.
7. 프로젝트 생성: `init_project('<id>', title='<한글 제목>', pipeline_type='animated-explainer')`. 중간 산출물은 `OpenMontage/projects/<id>/`, 최종 정리는 `REELS/videos/`.

### 1. 조사 (research)

- `skills/pipelines/explainer/research-director.md`를 읽고 `research_brief`를 만든다(스키마 검증 → checkpoint).
- 출처 우선순위: 한국 정부(질병관리청 등) → 국내 학회·대학병원 → 해외 공식 기관·논문 → 출처를 밝힌 언론. 블로그·출처 없는 기사는 근거로 쓰지 않는다.
- 확인되지 않는 내용은 넣지 않거나 "미확인"으로 표시한다. 반론이 있으면 단정하지 않는다. 해외 통계는 나라를 밝힌다.
- 조사를 별도 에이전트에 맡겨도 된다. 원문 인용과 URL을 받아 온다.

### 2. 제안 (proposal) — 자동 승인

- 콘셉트는 A형식 1안. 스키마가 3안을 요구하면 같은 형식의 첫 문장 변형으로 채우고 1안을 선택한다.
- `render_runtime: remotion`, `composition_mode: templated`, `renderer_family: explainer-teacher`, `music_source.source_type: bring_your_own`(provider `pixabay_music`).
- decision_log: Remotion과 HyperFrames를 모두 `options_considered`에 넣고 HyperFrames는 "사용자 확정 기본값(reels 스킬)"으로 rejected.
- `approval.status: "approved"`, `user_notes: "reels 스킬 상시 승인(2026-11-22)"`.

### 3. 대본 (script) — 확인 ①②

1. `script-director.md`를 읽고 A형식 초안을 쓴다. 문장마다 근거 출처를 옆에 단다. 화면에만 나올 숫자·문구도 함께 보여준다.
2. 사용자 확인 전에는 다음으로 가지 않는다.
3. 확정 대본을 `humanize-korean`으로 윤문한다(내용·숫자·출처 표기 불변, 줄 수 유지). 작업 폴더는 `OpenMontage/projects/<id>/humanize/` 아래에 둔다(저장소 최상위에 `_workspace/`를 만들지 않는다). 바뀐 문장만 전후로 보여주고 확인받는다.
4. `script` 아티팩트 저장 → checkpoint.

### 4. 음성 (직접 생성)

- `localhost:7790`을 호출해 문장마다 "남성1"(M1) 음성을 만든다. 파일은 `projects/<id>/assets/audio/`.
- **API는 아직 확인 전이다.** 처음 쓸 때 `curl -s localhost:7790/`, `/docs`, `/openapi.json` 등으로 엔드포인트와 M1 지정 방법을 확인하고, 이 절에 정확한 호출법을 적어 넣자고 사용자에게 제안한다. 추측으로 호출하지 않는다.
- 클라우드 세션에서 작업 중이면: 맥미니의 이 폴더가 Remote Control로 연결돼 있을 때만 맥미니에서 호출할 수 있다. 연결이 안 되면 무엇이 막혔는지 알리고, 사용자에게 맥미니에서 이 폴더로 작업하자고 제안한다.
- 한 파일로 받았다면 `ffmpeg silencedetect=noise=-35dB:d=0.35`로 1.3초 이상 무음을 찾아 문장 경계를 잡는다.
- 문장 사이 무음은 0.6초로 줄이고(앞 0.3초, 끝 0.8초, 각 문장 앞뒤 0.08초 여유), `loudnorm=I=-16:TP=-1.5:LRA=11`로 음량을 맞춘다. 문장별 시작·끝 시각을 `narration_timings.json`으로 저장한다.

### 5. 장면·소재·편집·합성

- 단계마다 `skills/pipelines/explainer/<stage>-director.md`를 먼저 읽는다. scene_plan·asset_manifest·edit_decisions는 스키마 검증 후 checkpoint(자동 승인)한다.
- edit_decisions 스키마는 컷에 문구 필드를 허용하지 않는다. 그래서 Remotion에 넘길 props는 `artifacts/composition.json`에 따로 만들고 `video_compose`의 `remotion_render`에 `composition_data`로 넘긴다.
- 장면(첫 편에서 확인한 설정):
  - 색: 배경 `#0F1B26`, 글자 `#F4F7FA`, 강조 `#FF8A3D`, 경고 `#FF5A5F`
  - 첫 장면 `hero_title`(text, heroSubtitle)
  - 설명·경고 `callout`(title, text, `fontSize: 58`, `titleFontSize: 46`). 기본 32는 세로 화면에서 너무 작다.
  - 숫자 `stat_card`(stat, subtitle)
  - 짧은 문장 `text_card`(text). **text_card는 subtitle을 화면에 표시하지 않는다.** 그래서 마지막 장면(광고 표기)은 `callout`(title "자세한 건 설명란 링크에서", text 광고 표기+안내, `fontSize: 40`, `titleFontSize: 56`)으로 만든다.
  - `progress_bar`는 0~100 값과 퍼센트가 화면에 보인다. 실제 데이터가 없으면 쓰지 않는다(근거 없는 숫자 금지).
  - 컴포넌트 컷의 `source`는 `""`로 둔다(값이 있으면 검증기가 파일을 찾다 실패한다).
- 음악: `pixabay_music`(query 예: "calm ambient piano", `min_duration` 40, `output_path`를 반드시 `projects/<id>/assets/music/`로). 403이 나도 도구가 재시도하면 통과한 적이 있다. 볼륨 0.07, fadeIn 1.5초, fadeOut 2.5초.
- 자막: `captions`에 어절 단위 `{word, startMs, endMs}`. 문장 구간은 실측 시각, 문장 안 어절은 글자 수 비례로 나눈다. `captionStyle: {wordsPerPage: 3, fontSize: 64, bottomOffset: 260}`, `captionProps: {fontFamily: "Noto Sans CJK KR, Apple SD Gothic Neo, sans-serif", wordSeparator: " "}`.
- 마지막 장면은 내레이션이 끝난 뒤 약 3초 더 보여 준다.
- 렌더 전 `CompositionValidator`가 `valid: True`여야 한다.
- 렌더: `video_compose.execute({'operation':'remotion_render','composition_data':comp,'output_path':'projects/<id>/renders/final.mp4','profile':'tiktok','proposal_packet':pp})`. 약 4~5분.
  - Remotion이 브라우저를 받으려다 `remotion.media` 접속에 실패하면, 설치된 Chrome headless shell을 `remotion_browser_executable`로 지정한다.
  - Linux 클라우드에서는 한글 글꼴이 없을 수 있다: `apt-get install -y fonts-noto-cjk`. 맥은 기본 한글 글꼴로 대체된다.

### 6. 확인과 정리 — 확인 ③

- `ffprobe`로 1080x1920·길이를 확인하고, `volumedetect` 평균이 -24dB보다 작으면 음량을 다시 맞춘다.
- 장면마다 프레임을 한 장씩 뽑아 직접 본다: 한글 깨짐, 글자 크기, 광고 표기 노출 여부.
- `REELS/videos/YYYY-MM-DD_<주제>/`에 정리: `<주제>_final.mp4`, `script.txt`, `sources.md`(문장별 출처·미확인·음악 라이선스), `audio/`(원본·편집 음성, 음악, timings), `artifacts/`(json 전부).
- 사용자에게 mp4와 출처를 보여주고 확인받는다.
- OpenMontage 저장소에 변경이 남지 않았는지 `git status`로 확인한다(`projects/`는 git에서 무시된다).

## 연결된 곳과 갱신 규칙

- 원본은 깃허브 `kst104/reels`. 노션 "릴스"(https://app.notion.com/p/420cac3237508175b737c2f68ae4e034), 아티팩트 "릴스"(https://claude.ai/artifact/CUs4fAxQX4zuLcb3CznmK2, 원본 `docs/reels-hub.html`), 슬랙 `#reels`(C0CKTUB04FP)가 연결돼 있다.
- 이 스킬이나 작업 규칙을 바꾸면 네 곳을 함께 갱신한다: 깃허브 커밋 → 아티팩트 재게시 → 노션 갱신 → 슬랙에 바뀐 점과 의견 요청.
- 영상을 하나 끝내면 `videos/`에 정리하고 깃허브에 올린 뒤, 노션·아티팩트 영상 목록에 추가하고 슬랙에 알린다. 음악 원본 파일은 저장소에 넣지 않는다.

## 막혔을 때

① 무엇을 시도했고 ② 무엇이 실패했고 ③ 원인이 접속·권한·도구 버그·품질 중 무엇이며 ④ 다음 선택지와 ⑤ 추천안을 알린다. 사용자 승인 전에는 대체 경로로 진행하지 않는다.

## 주의

- 건강·의학 주제는 진단·치료를 대신하지 않는다는 뜻이 드러나게 쓰고, 과장하지 않는다.
- Remotion은 회사 규모에 따라 유료 라이선스가 필요할 수 있다. 개인 사용이 아니게 되면 remotion.dev/license를 확인한다.
- OpenMontage의 라이선스는 AGPL-3.0이다. 코드를 고쳐 배포하거나 서비스로 제공할 계획이 생기면 라이선스 조건을 따로 확인한다.

## 아직 확인하지 않은 부분

- 맥미니 `localhost:7790` 음성 서버의 API와 "남성1"(M1) 지정 방법 → 다음 영상에서 확인하고 4절을 갱신한다.
- 문장 안 어절 자막 타이밍은 추정치다(문장 경계는 실측). 음성 인식 도구가 생기면 단어 단위로 맞춘다.
