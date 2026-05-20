# Vault build — specifications

Single source of truth for every dimension, count, and material call-out.
Each entry tagged with the source it came from (e.g. `[video-01]`), so when
Adam revises a number in a later video the trail stays clear.

Sources legend:
- `[video-01]` — Adam machining the ring gear from a stainless cylinder
  (https://www.youtube.com/watch?v=SiL8IzJSnyU)

---

## Global gear math

| Parameter | Value | Source |
| --- | --- | --- |
| Gear module | 0.5 mm | [video-01] |
| Scale (relative to a real vault door) | 1/12 | [video-01] |

The module is the parameter that has to match across every gear that meshes,
so it is the single most important number in the file.

## Real-world reference (for context, not for modeling)

Real vault doors: 24 spur gears (24 teeth each) around a 288-tooth ring gear.
Adam's miniature halves this — see below. `[video-01]`

## Ring gear

| Parameter | Value | Source |
| --- | --- | --- |
| Teeth | 120 | [video-01] |
| Outer diameter | 2.401 in (≈ 2.4 in) | [video-01] |
| Depth of gear cut (OD to root of tooth) | 0.044 in | [video-01] |
| Material (Adam's build, FYI only) | 416 stainless | [video-01] |

## Spur gears

| Parameter | Value | Source |
| --- | --- | --- |
| Count | 12 | [video-01] |
| Teeth (each) | 24 | [video-01] |
| Bolt-circle hole spacing | 30° (12 holes evenly around) | [video-01] |

Adam's mill dividing plate has 24 holes (15° spacing), but he only fills every
other one for the 12-pin door.

## Locking pins

| Parameter | Value | Source |
| --- | --- | --- |
| Count | 12 (one per spur gear) | [video-01] |
| Diameter | 12 mm | [video-01] |
| Drive mechanism | Straight rack on bottom face, driven by spur gear | [video-01] |

## Derived values

| Parameter | Value | Notes |
| --- | --- | --- |
| Drive ratio (ring : spur) | 5 : 1 | 120 / 24. Onshape's Gear Relation tool will compute this automatically from tooth counts. |
