---
videomd: 1
part: timeline
shots: 8
tokens: 630
---

# Timeline

One shot per line: `#<n> start-end (s) | key value | …`. A key ending in `~` is the tools' inference; keys without it are visible on screen or measured directly.
`story` job in the story and the point · `seen` what is on screen · `act` acting (emotion, strength, face) · `camera` camera move · `overlay` overlays · `made~` how it was made (inferred) · `material~` where the material came from (inferred) · `remake` remake route · `flag` needs a second look
Full detail for a shot is in `video/shots/<n>.md` (e.g. `video/shots/07.md`).

```videomd-timeline
#01 0.0-3.7 | camera static | overlay subtitle, text, title, layout template | made~ 3D render 99% | material~ rendered by the creator | remake AI generation / 3D render · G1
#02 3.7-4.6 | camera static | overlay layout template | made~ screen recording / screenshot 52% · runner-up code / template render 43% | material~ the user's real material: UI screenshot | remake screen recording · Part 1 | flag low confidence
#03 4.6-7.7 | camera static | overlay layout template | made~ screen recording / screenshot 35% · runner-up static hold 32% | material~ the user's real material: UI screenshot;… | remake screen recording · Part 1 | flag low confidence
#04 7.7-11.1 | camera static | overlay layout template | made~ screen recording / screenshot 51% · runner-up code / template render 43% | material~ the user's real material: UI screenshot | remake screen recording · Part 1 | flag low confidence
#05 11.1-13.1 | camera static | overlay subtitle, text, title, layout template, styled text | made~ still image + pan/zoom 53% · runner-up code / template render 10% | material~ rendered by the creator; real or not, to… | remake local ffmpeg move | flag low confidence
#06 13.1-15.3 | camera static | overlay layout template | made~ screen recording / screenshot 35% · runner-up static hold 31% | material~ the user's real material: UI screenshot | remake screen recording · Part 2 | flag low confidence
#07 15.3-18.9 | camera static | overlay layout template | made~ screen recording / screenshot 36% · runner-up code / template render 30% | material~ the user's real material: UI screenshot | remake screen recording · Part 2 | flag low confidence
#08 18.9-23.0 | camera static | overlay layout template | made~ screen recording / screenshot 36% · runner-up code / template render 30% | material~ the user's real material: UI screenshot | remake screen recording · Part 2 | flag low confidence
```
