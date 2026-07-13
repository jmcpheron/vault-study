---
title: Sources
---

# Sources

The vault project is a study of **Adam Savage's** miniature
bank-vault-door build, shown on the
[Tested YouTube channel](https://www.tested.com/). The videos are
the original work; this site is commentary.

## The build series

| Part | Topic | Tag in [`specs.md`](https://github.com/jmcpheron/vault-study/blob/main/specs.md) |
| --- | --- | --- |
| 1 | [Ring gear machining](https://www.youtube.com/watch?v=SiL8IzJSnyU) | `[part-1]` |
| 2 | Locking pins, racks, main door body | `[part-2]` |
| 3 | Vault door (heavy puck), frame, hinge | `[part-3]` |
| 4 | Concentricity, rack refinement, pin-diameter revision | `[part-4]` |
| 5 | Combination lock | `[part-5]` |

_(Direct URLs for parts 2–5 — to be added.)_

## How sources cascade into the repo

```
Adam's video        →  specs.md                 (canonical, source-tagged)
   mirrored         →  src/vaultkit/params.py   (code-readable)
   tested           →  tests/test_no_drift.py   (drift check)
   explained        →  docs/*.md                (this site + the blog posts)
```

Every number on every page should trace back through that chain to
a `[part-N]` tag in `specs.md` to a timestamp in one of Adam's
videos.

## Attribution

The mechanism design — 12 pins, 120/24 gear math, combination-lock
gatekeeper, rack-and-pinion linear motion, the geometry of the
hinge — is Adam's. This repo is an independent CAD reinterpretation
for educational and hobby purposes, licensed CC BY-SA 4.0 (see
[`LICENSE-3D-FILES`](https://github.com/jmcpheron/vault-study/blob/main/LICENSE-3D-FILES)).
