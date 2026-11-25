---
videomd: 1
part: remake
tokens: 3056
---

## Remake plan

### Step by step

This is a screen tutorial / software demo. Do the steps in this order; the detail for each is in the matching subsection below.

1. **Write the content**: one picture of your own for each of the 8 shots in the shot list
2. **Collect material**: the real material in the picture (UI screenshot) needs the original files, listed under “What to prepare”
3. **Voice**: where the original voice comes from is to confirm; record it yourself or use TTS
4. **Edit**: follow the order and lengths in the shot list; the original has 8 shots at 2.9s each
5. **Subtitles and styled text**: import `packaging/subtitles.srt` and replace the words; timing and style under “Packaging layer”
6. **Put it together and compare**: hand the shots you made to the agent; it places them on the original timeline, keeps the original where yours are missing, and renders a side-by-side comparison with the original

**1 3D render shot → 1 generation unit, 1 MiniMax H3 / H3 Max call; code render / screen capture 6 shots → 1 code project (2 parts); still-image move / static frame 1 shot → rebuilt locally**

### Generation units

| Part | Shots | Time | Length | Prepare |
|---|---|---|---|---|
| G1 | #1 | 0.0–3.7s | 3.7s | reference images |

**Why it is split this way**

- Grouping: consecutive shots share a call where they fit, ≤10s per call, ≤4 shots; a long stretch is cut at a scene change first
- Inputs: the model also takes reference video, but its default plan is used here: one source frame per shot (subtitles erased) fixes composition, swapped-in things get their own images
- Audio: the model can generate action sound effects and ambience along with the picture; the voice was recorded by a person: record it separately and mix it in rather than having the video model speak, so copy and timing stay editable
- Packaging: the title, subtitle on the generated shots is post-production packaging: keep it out of the prompts (erased from source references) and lay it back on from the packaging timeline after generation

**G1 · shots #1 · 3.7s**

- reference images: source frames of shots #1 (subtitles erased)

Draft prompt (in MiniMax H3 / H3 Max's layout; check it and put the final into remake/prompts.json before generating):

```text
integrated_multimodal_description: Generate the shots below in order in one go, hard cuts between them; each shot takes composition, size and camera from its source frame image. Vertical 9:16; soft frontal light, cool tones, background clearly blurred.
[Shot 1] (no description: write one in the image review) (composition: <Picture 1>). SFX: ding
overall_soundscape: Distinct action sounds: ding.
non_diegetic_music: N/A
```

**Prompt guides for MiniMax H3 / H3 Max**

- https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md
- https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md
- https://platform.minimax.io/docs/api-reference/video-generation-v2-create
- https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide.md

### Code composition

Rebuild it as one project in an HTML video framework (such as HyperFrames or Remotion): cuts, transitions and each shot's key frames from "Rhythm and key frames", layout, colours and elements from the scenes below. Text and UI are 100% controllable, changing copy is a data change, and an AI coding assistant can write the project.

`rea-video code-remake <breakdown folder>` only makes a quick draft: it renders `code/remake.mp4` from each scene's sampled points / cut-out, motion and background glow and scores it. Particles, point clouds and data visualisations on a dark ground come close; an illustrated character's acting and morph transitions do not.

- Part 1: shots #2–#4 (3.7–11.1s); #2–#4 use real screen recordings
- Part 2: shots #6–#8 (13.1–23.0s); #6–#8 use real screen recordings

Remake assets (all in the report folder; hand them over together with the data below to whoever writes the code, or to an LLM):
- `shots/shot_XXX_first.jpg` / `_last.jpg`: first / last frame of each shot at full size, for layout, type size and margins
- `shots/shot_XXX_strip.jpg`: key frames about every 0.5 s, to follow the animation
- `shots/shot_XXX_elements.jpg` and `_el_NN.jpg` / `_st_NN.jpg` / `_ly_NN.jpg`: full-size crop of every element once settled, numbered as in the motion timeline; redraw shapes from them, cut out icons, logos and illustrations that cannot be redrawn
- `packaging/overlays.ass`, `packaging/timeline.json`: timing, position and colour of the text

How to build the pictures (by the measured picture type):
- kinetic type: Word-by-word spring() entrances (offset + scale + opacity), highlight boxes on key words; match font, size and leading from the frame

| Shot | Time | Build | Picture | Camera | Colours | On-screen text |
|---|---|---|---|---|---|---|
| #2 | 3.7–4.6s | kinetic type | (to fill from the images: what the elements form and how they move) | static | ground #fcfcfc · #01857b #242627 #d0d4d5 #6f7071 · drawn #2d2d2d #118578 #020202 #8c8c8c | SAMMOBILE / 폰무위키 / 삼성이만드는베첼리스스마르폰? / 삼성이만드는베젤리스스마르폰? |
| #3 | 4.6–7.7s | kinetic type | (to fill from the images: what the elements form and how they move) | static | ground #fafbfc · #a3b7db #4a5577 #03867c #7581a4 · drawn #2f3a6e #5c6bb3 #0b0d15 #118578 | 폰무위키 / 삼성이만드는베젤리스스마르폰? |
| #4 | 7.7–11.1s | kinetic type | (to fill from the images: what the elements form and how they move) | static | ground #fcfcfc · #0c0d0f #777779 #5b5c60 #01857b · drawn #fbfcfc #050506 #161314 | 폰무위키 / 삼성이만드는베젤리스스마르폰? / 삼성이만드는베젤리스스마크폰? |
| #6 | 13.1–15.3s | kinetic type | (to fill from the images: what the elements form and how they move) | static | ground #fafcfc · #4e8f1d #71acbf #2e847a #b5cbc4 · drawn #4a7b1e #0d0e09 #118578 #6b9bb0 | 우리는모두삼성 / 폰무위키 / 삼성이만드는베젤리스스마르폰? |
| #7 | 15.3–18.9s | kinetic type | (to fill from the images: what the elements form and how they move) | static | ground #f7fbfc · #6b839a #0a1529 #283550 #4d5e70 · drawn #fdfdfd #0d182a #546475 #108278 | 폰무위키 / 삼성이만드는베젤리스스마트폰? |
| #8 | 18.9–23.0s | kinetic type | (to fill from the images: what the elements form and how they move) | static | ground #fcfcfc · #716179 #9d919e #4a3c59 #c8bdc0 · drawn #05020e #35234b #725f73 #118578 | 폰무위키 / 삼성이만드는베젤리스스마르폰? |

Per-shot motion timeline (measured: positions in % of frame width / height, colours sampled once the element settles; read together with the key-frame strip)

**Motion #2 3.7–4.6s · 0 events**

- Ground #fcfcfc; other main colours #01857b #242627 #d0d4d5 #6f7071; drawn layer #2d2d2d #118578 #020202 #8c8c8c
Element crops (numbers match the motion list below; L = the continuously moving layer mid-shot and at the end, S = elements that never move), full-size files in `shots/`:

- S1. never moves: shape / text block · x 0%–100%, y 0%–9% · #108578 · text “폰무위키” · [crop](shots/shot_002_st_01.jpg)
- S2. never moves: horizontal line · x 3%–97%, y 12%–17% · #000000 · text “삼성이만드는베첼리스스마르폰? / 삼성이만드는베젤리스스마르폰?” · [crop](shots/shot_002_st_02.jpg)
- S3. never moves: horizontal line · x 0%–100%, y 20%–21% · #dedede · [crop](shots/shot_002_st_03.jpg)
- S4. never moves: shape / text block · x 0%–44%, y 45%–55% · #292929 · [crop](shots/shot_002_st_04.jpg)
- S5. never moves: shape / text block · x 44%–59%, y 45%–55% · #292929 · text “SAMMOBILE” · [crop](shots/shot_002_st_05.jpg)
- S6. never moves: shape / text block · x 71%–80%, y 45%–55% · #292929 · [crop](shots/shot_002_st_06.jpg)
- S7. never moves: shape / text block · x 84%–100%, y 45%–55% · #292929 · [crop](shots/shot_002_st_07.jpg)
- S8. never moves: shape / text block · x 29%–70%, y 74%–78% · #000000 · text “샘모바일에 따르면 / 삼성이 테두리가 거의 안 보이는 / 올스크린 디스플레이를 개발하고 있음” · [crop](shots/shot_002_st_08.jpg)

**Motion #3 4.6–7.7s · 0 events**

- Ground #fafbfc; other main colours #a3b7db #4a5577 #03867c #7581a4; drawn layer #2f3a6e #5c6bb3 #0b0d15 #118578
- No element motion measured (still picture or only slight changes)

**Motion #4 7.7–11.1s · 1 events**

- Ground #fcfcfc; other main colours #0c0d0f #777779 #5b5c60 #01857b; drawn layer #fbfcfc #050506 #161314
Element crops (numbers match the motion list below; L = the continuously moving layer mid-shot and at the end, S = elements that never move), full-size files in `shots/`:

1. 8.00–8.07s · bottom (x 20%–78%, y 78%–81%) · changes, instant · #939393 · text “4면 전체로 확장할 계획인데 / 애플보다 먼저 제품을 출시할 수도 있다는거다” · [crop](shots/shot_004_el_01.jpg)

**Motion #6 13.1–15.3s · 0 events**

- Ground #fafcfc; other main colours #4e8f1d #71acbf #2e847a #b5cbc4; drawn layer #4a7b1e #0d0e09 #118578 #6b9bb0
Element crops (numbers match the motion list below; L = the continuously moving layer mid-shot and at the end, S = elements that never move), full-size files in `shots/`:

- S1. never moves: shape / text block · x 0%–100%, y 0%–9% · #108578 · text “폰무위키” · [crop](shots/shot_006_st_01.jpg)
- S2. never moves: horizontal line · x 3%–97%, y 12%–17% · #000000 · text “삼성이만드는베젤리스스마르폰?” · [crop](shots/shot_006_st_02.jpg)
- S3. never moves: shape / text block · x 0%–100%, y 24%–66% · #448c16 · text “포랫몬스터 / 우리는모두삼성 / 포랫몬스” · [crop](shots/shot_006_st_03.jpg)
- S4. never moves: horizontal line · x 6%–93%, y 72%–75% · #010101 · text “재있는 점은 디스플레이 공급사인 삼성이” · [crop](shots/shot_006_st_04.jpg)
- S5. never moves: horizontal line · x 1%–99%, y 78%–81% · #000000 · text “애플보다 먼저 제품을 출시할 수도 있다는거다” · [crop](shots/shot_006_st_05.jpg)

**Motion #7 15.3–18.9s · 0 events**

- Ground #f7fbfc; other main colours #6b839a #0a1529 #283550 #4d5e70; drawn layer #fdfdfd #0d182a #546475 #108278
- No element motion measured (still picture or only slight changes)

**Motion #8 18.9–23.0s · 0 events**

- Ground #fcfcfc; other main colours #716179 #9d919e #4a3c59 #c8bdc0; drawn layer #05020e #35234b #725f73 #118578
Element crops (numbers match the motion list below; L = the continuously moving layer mid-shot and at the end, S = elements that never move), full-size files in `shots/`:

- S1. never moves: shape / text block · x 0%–100%, y 0%–9% · #108578 · text “폰무위키” · [crop](shots/shot_008_st_01.jpg)
- S2. never moves: horizontal line · x 3%–97%, y 12%–17% · #000000 · text “삼성이만드는베젤리스스마르폰?” · [crop](shots/shot_008_st_02.jpg)
- S3. never moves: horizontal line · x 0%–100%, y 20%–21% · #dedede · [crop](shots/shot_008_st_03.jpg)
- S4. never moves: shape / text block · x 0%–100%, y 24%–65% · #23133d · [crop](shots/shot_008_st_04.jpg)
- S5. never moves: horizontal line · x 14%–84%, y 72%–75% · #020202 · text “과연 2027년 스마트폰 시장에서” · [crop](shots/shot_008_st_05.jpg)
- S6. never moves: horizontal line · x 3%–97%, y 78%–81% · #000000 · text “누가 먼저 완벽한 제로 베젤을 구현해낼라나” · [crop](shots/shot_008_st_06.jpg)

### Local rebuild

- #5 still image + pan/zoom 2.0s: one image + the measured zoom / pan parameters, rendered straight from ffmpeg

### Real material in the picture (the original files are needed)

6 shots, 17.33s (75%) contain real material (screen recordings, screenshots, photos, embedded video); a model cannot stand in for them:

- **UI screenshot** (whole frame): shots #2–#4, #6–#8, 17.3s in all
