---
videomd: 1
name: ref
description: '“ref”. Made with (inferred): screen recording / screenshot 75%, 3D render 16%, still image + pan/zoom 9%'
source:
  file: ref.mp4
  sha256: 60c7793f7784b8f002da7d50b10d4eba4792442d8cda885ad4a38906e2523c21
  duration: 23.033
  size: 1440x2560
  fps: 30.0
  aspect: '9:16'
shots: 8
lang: en
made_mix:
  screen_capture: 0.7525
  cg_3d: 0.1606
  still_motion: 0.0868
confidence: 0.503
readers:
- tools
open_questions: 12
generator:
  name: rea-video
  version: 0.1.0
---

# ref.mp4

**Verdict** (inferred): Mixed production: screen recording / screenshot 75% + 3D render 16% + still image + pan/zoom 9%; overlays: styled text, text labels, layout template, subtitles, title (composited in code / an editor); real material used: UI screenshot (17.3s); audio: voice + 6 sound effects; packaging: 13 subtitle lines, styled text ×2, title ×2, text labels ×2, 4 sound effects land on text / sticker pops
**Made with** (inferred, by duration): screen recording / screenshot 75%, 3D render 16%, still image + pan/zoom 9%
**Remake**: 1 3D render shot → 1 generation unit, 1 MiniMax H3 / H3 Max call; code render / screen capture 6 shots → 1 code project (2 parts); still-image move / static frame 1 shot → rebuilt locally
**Real material to collect**: 6 shots (75% of the duration), list in `video/remake.md`

## Next steps

- No VLM ran: if you can see images, review first: `rea-video review <this dir>` → fill `review_answers.json` → `rea-video apply-review <this dir>`
- Remake: Capsule Cinema does the generation, assembly and checks. `rea-video remake <this dir>` hands over to it, does what can be done automatically and keeps the original elsewhere; `remake/status.md` says per shot what is left. Add incoming clips to `remake/mine.json` and run it again
- AI shots: prompts are in the generation units of `video/remake.md`; for automatic generation use Capsule Cinema: `scripts/remake_reference.py prepare <this dir>`, then `run <jobs.json> --dry-run` (paid: ask the user first)

## Open questions

- The VLM did not run (No VLM; live action / AI / 3D are told apart from pixel statistics only, so confidence is limited. An agent that can see images: run rea-vi…
- Shot #2 (3.7–4.6s): screen recording / screenshot at only 52% confidence, runner-up code / template render
- Shot #3 (4.6–7.7s): screen recording / screenshot at only 35% confidence, runner-up static hold
- Shot #3 (4.6–7.7s): photo / image: real material or generated, to confirm
- Shot #4 (7.7–11.1s): screen recording / screenshot at only 51% confidence, runner-up code / template render
- Shot #5 (11.1–13.1s): still image + pan/zoom at only 53% confidence, runner-up code / template render
- Shot #5 (11.1–13.1s): photo / image: real material or generated, to confirm
- Shot #6 (13.1–15.3s): screen recording / screenshot at only 35% confidence, runner-up static hold
- 4 more, see the `flag` lines in `video/timeline.md`

## Map

Read this page first; for detail, open only the file you need. Each line is `path | ~tokens | what is in it · when to read it`; paths are relative to this directory.

```videomd-map
video/timeline.md | 644 | Timeline: one line per shot · what a stretch says, which shots need review, how a shot was made
video/moments.md | 74 | Special moments · reveals, twists, climaxes, goofs: times, key frames, clips
video/content.md | 87 | Content and structure · what it says, the narrative line, structure, the script
video/cast.md | 32 | Cast, scenes and props · reference images for characters, first-frame prompts
video/sound.md | 364 | Sound · voice, music, sound effects, beats and sources
video/rhythm.md | 211 | Rhythm and key frames · when cuts and transitions happen, shot lengths, the change curve, key frames of each shot
video/look.md | 446 | Camera, lighting and editing · for filmed shots: framing, camera, lighting, kit
video/packaging.md | 1025 | Packaging · subtitles, styled text, stickers, picture-in-picture: timing and style
video/remake.md | 3067 | Remake plan · generation units, shoots, code builds, real material to collect, acting and emotion
video/shots/*.md | 486 | Per-shot detail, tokens per file on average · checking one shot: what is seen, the inference and its basis, prompts, frames
breakdown.json | 47304 | Full raw data · for programs; a model rarely needs it
shots/ | - | contact sheet, first and last frame of each shot · checking by eye
storyboard.jpg | - | storyboard of the whole video · the whole video at a glance
stems/ | - | voice, music and effects stems · listening, remaking the sound
sfx/ | - | a clip of each sound effect · finding matching effects
packaging/ | - | subtitle files, packaging timeline, sticker frames · remaking subtitles and packaging
frames/ | - | picture scenes: full-size frames, the drawn layer cut out and sampled, measurements · remaking rendered pictures
audio.png | - | waveform and beat chart · seeing the rhythm
```

## How to read

- One shot per line: `#<n> start-end (s) | key value | …`. A key ending in `~` is the tools' inference; keys without it are visible on screen or measured directly.
- `story` job in the story and the point · `seen` what is on screen · `act` acting (emotion, strength, face) · `camera` camera move · `overlay` overlays · `made~` how it was made (inferred) · `material~` where the material came from (inferred) · `remake` remake route · `flag` needs a second look
- Full detail for a shot is in `video/shots/<n>.md` (e.g. `video/shots/07.md`).
- What is “seen” can be checked against the frames; what is “inferred” is the tools' and image readers' judgement, with the basis in each shot file. When they disagree, trust the frames.
