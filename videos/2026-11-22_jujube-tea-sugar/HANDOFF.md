# 인수인계 — 겨울 대추차 릴스 (2번 프레임)

클라우드 세션에서 2026-11-22에 넘김. 맥미니 `~/Downloads/reels`에서 이어서 만든다.

## 지금까지 된 것

- 소재: 사용자 블로그 https://blog.naver.com/kst104/224485952422
- 조사 → 대본 → 윤문 완료. 사용자 확인 ①(대본) ②(윤문) 받음 (2026-11-22).
- 렌더 틀: **2번 프레임(HyperFrames)** — 사용자 지정.
- 장면 계획 `artifacts/scene_plan_hf.json`을 무음 임시 음성으로 2번 틀에 넣어 시험했다: lint·validate·inspect 오류 0, 장면 10개 글자 넘침 없음(클라우드, 리눅스).

| 파일 | 내용 |
|---|---|
| `script.txt` | 확정 대본 6줄(한 줄 = 한 문장 음성) |
| `sources.md` | 줄별 출처, 미확인 항목 |
| `artifacts/research_brief.json`, `proposal_packet.json`, `decision_log.json` | OpenMontage 조사·제안(자동 승인)·결정 기록 |
| `artifacts/scene_plan_hf.json` | 컷 10개 문구와 2번 틀 효과(`hf`). 시각은 음성 뒤에 채움 |
| `artifacts/build_composition.py` | 장면 계획 + 음성 시각 → `composition.json` |

## 사용자가 맥미니에서 할 일

1. 깃허브 PR을 병합한다(이 폴더가 main에 있어야 한다).
2. 터미널에서:
   ```bash
   cd ~/Downloads/reels
   git pull
   ```
3. 음성 프로그램(localhost:7790)을 켠다.
4. 이 폴더에서 Claude Code를 열고 이렇게 말한다:
   > videos/2026-11-22_jujube-tea-sugar/HANDOFF.md 보고 대추차 릴스 이어서 해줘

## Claude가 할 일 (reels 스킬 순서대로)

1. **준비** (스킬 0절): OpenMontage 설치 확인, `pip install fonttools brotli`, `npx hyperframes doctor --json`.
2. **프로젝트**: `init_project('jujube-tea-sugar-shorts', title='겨울 대추차, 효능보다 먼저 볼 건 설탕', pipeline_type='animated-explainer')` 뒤 이 폴더의 `artifacts/*.json` 세 개를 `projects/jujube-tea-sugar-shorts/artifacts/`로 복사하고 research·proposal checkpoint를 쓴다. script checkpoint는 `script.txt` 6줄, "사용자 확인 ①② 완료(2026-11-22)"로 기록한다.
3. **음성** (스킬 4절): 7790 API를 먼저 확인한다(추측 호출 금지). 확인한 호출법은 스킬 4절에 적자고 사용자에게 제안한다. `script.txt` 줄마다 남성1(M1) 음성을 만들고, 문장 사이 0.6초, loudnorm → `assets/audio/narration_norm.wav`, 문장 6개 구간을 `assets/audio/narration_timings.json`(`total`, `sections[s1..s6]`)으로 저장한다.
   - 3번 줄은 윤문으로 쉼표가 빠져 한 호흡이 길다. 숨이 차게 들리면 "50그램 미만이니," 쉼표를 되살려 그 줄만 다시 만들고 사용자에게 알린다.
4. **음악**: `pixabay_music`(query "calm ambient piano", `min_duration` 45) → `assets/music/bgm.mp3`.
5. **composition**:
   ```bash
   python videos/2026-11-22_jujube-tea-sugar/artifacts/build_composition.py OpenMontage/projects/jujube-tea-sugar-shorts
   ```
6. **2번 렌더** (스킬 5-2절): `frame2_hyperframes.py` → lint → validate → inspect → snapshot(장면마다 한 장 직접 보기) → render.
   - 맥에서 2번 틀을 처음 돌린다. 글꼴(Apple SD Gothic Neo) 경로와 렌더 시간을 확인해 스킬 "아직 확인하지 않은 부분"을 갱신하자고 제안한다.
7. **정리·확인 ③** (스킬 6절): 이 폴더에 `jujube-tea-sugar_final.mp4`, `audio/`, `artifacts/composition_hf.json`(=composition.json), `artifacts/hyperframes/index.html`. `sources.md`의 음악 칸을 채운다.
8. **상품 추천 ④** (스킬 7절): 블로그에는 이미 "들꽃잠 배 찜질팩 온열 팥 멀티형" 쇼핑 커넥트 링크(https://naver.me/Faeu91oI)가 걸려 있다. 주간 구매 순위 후보와 함께 이 상품도 보여 주고 사용자가 고르게 한다.
9. **링크·캡션·게시 ⑤** (스킬 8~9절), 네 곳(깃허브·노션·아티팩트·슬랙) 기록.
