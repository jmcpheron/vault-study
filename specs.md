# Vault — specifications

Single source of truth for every dimension, count, and material call-out in
the Adam-Savage-faithful design. Every row is tagged with the source video
it came from (`[part-N]`), so when Adam revises a number in a later video
the trail stays clear.

Numbers here are the **canonical** values for the faithful variant. They
are mirrored into [`src/vaultkit/params.py`](src/vaultkit/params.py) by
hand; the drift test in [`tests/test_no_drift.py`](tests/test_no_drift.py)
fails if the two get out of sync. The FDM variant inherits these defaults
and deviates where noted in [`cad/fdm/deviations.md`](cad/fdm/deviations.md).

When a value is superseded, the old row is kept (struck through, marked
`superseded in [part-N]`) and the new row sits below it (marked `live`).
The history is the lesson — parametric design exists *because* numbers
move. The drift test only checks `live` rows.

Sources legend:

- `[part-1]` — Ring gear machining
  (https://www.youtube.com/watch?v=SiL8IzJSnyU)
- `[part-2]` — Locking pins, racks, main door body
- `[part-3]` — Vault door (heavy puck), frame, hinge
- `[part-4]` — Concentricity, rack refinement, pin-diameter revision
- `[part-5]` — Combination lock

---

## Global gear math

| Parameter | Value | Source |
| --- | --- | --- |
| Gear module | 0.5 mm | [part-1] |
| Scale (relative to a real vault door) | 1/12 | [part-1] |

The module is the parameter that must match across every gear that meshes,
so it is the single most important number in the file. A real vault door
uses 24 spur gears (24 teeth each) around a 288-tooth ring gear; Adam
halves the math for his 1/12-scale build.

## Ring gear

| Parameter | Value | Source |
| --- | --- | --- |
| Teeth | 120 | [part-1] |
| Outer diameter | 2.401 in (≈ 2.4 in) | [part-1] |
| Inner diameter (slip-fit on acrylic boss) | 2.003 in | [part-2] |
| Depth of gear cut (OD to root of tooth) | 0.044 in | [part-1] |
| Material (Adam's build, FYI only) | 416 stainless | [part-1] |

## Spur gears

| Parameter | Value | Source |
| --- | --- | --- |
| Count | 12 | [part-1] |
| Teeth (each) | 24 | [part-1] |
| Bolt-circle diameter (BCD) | 72 mm | [part-2] |
| Bolt-circle hole spacing | 30° (12 holes evenly around) | [part-1] |
| Axle | Shoulder bolt, 0.1 mm smaller than gear bore (slip-fit) | [part-2] |

Adam's mill dividing plate has 24 holes (15° spacing); he fills every
other one for the 12-pin door. In CAD: a 12-point circular pattern on a
72 mm BCD.

## Locking pins

| Parameter | Value | Source | Status |
| --- | --- | --- | --- |
| Count | 12 (one per spur gear) | [part-1] | live |
| Diameter | ~~12 mm~~ | [part-1], [part-2] | superseded in [part-4] |
| Diameter | **10 mm** | [part-4] | live |
| Length | 30 mm | [part-2] | live |
| Base thread | M6 (rack screws into pin base) | [part-2] | live |

The 12 mm → 10 mm revision is the textbook reason this repo is
parametric: change `PIN_DIAMETER_MM` in `params.py` and the radial
bores in the acrylic hub, the cast-iron puck, and the FDM-variant
hex stock all follow.

## Racks (drive the pins)

| Parameter | Value | Source |
| --- | --- | --- |
| Stock | 8 mm × 8 mm square | [part-2] |
| Module (matches ring + spur) | 0.5 mm | [part-2] |
| Threaded end | Turned down to 6 mm shaft, M6 thread | [part-2] |
| Clearance cut | Curved relief on back face (clears ring gear) | [part-2], [part-4] |
| Quantity machined | 14 (need 12; "always make more than you need") | [part-4] |

The threaded stud must be concentric to the 8 × 8 stock to within
~0.0125" or the pins bind on the door bores. Adam fixes this with an
8 mm square 5C collet + spindle lock + tailstock die — see [part-4].

## Main door body (acrylic hub)

The clear-acrylic puck that houses the mechanism and lets the gears
be visible.

| Parameter | Value | Source |
| --- | --- | --- |
| Outer diameter | 6 in | [part-2] |
| Thickness (stock) | 1.25 in | [part-2] |
| Material | Cast acrylic (not extruded — extruded melts on the lathe) | [part-2] |
| Ring-gear slip-fit boss diameter | 2.003 in | [part-2] |
| Radial pin bores | 12 × 12 mm dia | [part-2] |

Note: the radial pin bores were sized to the original 12 mm pins; on
a follow-on revision they need to drop to 10 mm to match the
[locking-pin revision in part-4](#locking-pins). Track that change
here when it lands.

## Heavy door puck (cast iron outer)

| Parameter | Value | Source | Status |
| --- | --- | --- | --- |
| Material | ~~Steel~~ | [part-3] | superseded mid-[part-3] |
| Material | **Cast iron** | [part-3] | live |
| Target weight (real-life) | 15–20 lb | [part-3] | live |
| Outer diameter (fits frame hole) | 6 in | [part-3] | live |
| Front-face thickness (solid) | 0.5 in | [part-3] | live |
| Edge taper (nominal) | ~10° (built as three stepped angles) | [part-3] | live |
| Closure depth into frame | 0.75 in (limited by hinge clearance) | [part-3] | live |

The tapered edge is what makes a vault door "thunk" home into the
frame. Adam estimates ~10° but breaks it into three slightly
different stepped angles — exact values TBD.

## Door frame

| Parameter | Value | Source |
| --- | --- | --- |
| Material | 1/2 in 6061 aluminum plate | [part-3] |
| Overall size | 10–12 in square | [part-3] |
| Door opening (centered) | 6 in dia | [part-3] |
| Door-to-frame clearance | 0.020 in (20 thou) | [part-3] |

## Hinge

| Parameter | Value | Source |
| --- | --- | --- |
| Thrust-bearing OD | 3/8 in | [part-3] |
| Center pin | 1/8 in | [part-3] |
| Fasteners | 28 × M2 screws | [part-3] |
| Hinge-hole inner column (X from door center) | 0.245 in | [part-3] |
| Hinge-hole column spacing | 0.508 in | [part-3] |
| Hinge-hole outer column (X = inner + spacing) | 0.753 in | [part-3] |
| Hinge-hole Y span (± from center) | 0.9125 in | [part-3] |

Adam's Plan B if the M2s fail under load: M6. CAD stays with M2.

## Combination lock

| Parameter | Value | Source |
| --- | --- | --- |
| Cage envelope | 0.75 in × 0.5 in | [part-5] |
| Cage material | 0.025 in (25 thou) brass sheet (~0.5 mm) | [part-5] |
| Combination wheels | 3 | [part-5] |
| Wheel diameter | 0.450 in | [part-5] |
| Wheel features (each) | Spindle hole + drive tab + locking slot | [part-5] |
| Front-dial spindle | 1/8 in brass rod | [part-5] |
| Front-dial divisions | 36 (10° each) | [part-5] |
| Front-dial tick lengths | 3 (short / medium / long, every 1/5/10) | [part-5] |

Bell-crank linkage couples the drop-arm to the ring gear: when the
three wheels' locking slots align, the arm drops, the bell crank
unlocks the ring gear, the user throws the lever, all 12 pins extend.

## Derived values

These fall out of the canonical numbers above. The kernel computes
them in [`gears.py`](src/vaultkit/gears.py) so prose can read them
without hard-coding.

| Parameter | Value | Derivation |
| --- | --- | --- |
| Drive ratio (ring : spur) | 5 : 1 | 120 / 24 |
| Teeth between adjacent spur-gear axes | 10 | 120 / 12 (timing math, [part-2]) |
| Ring-gear pitch diameter | 60 mm | module × teeth = 0.5 × 120 |
| Spur-gear pitch diameter | 12 mm | module × teeth = 0.5 × 24 |
| Spur-gear axis radius (from door center) | 36 mm | (ring PD + spur PD) / 2 |

The 36 mm spur-axis radius derived from gear math should match the
72 mm BCD measured by Adam (= 2 × 36). It does — and that
agreement is one of the things the [drift test](tests/test_no_drift.py)
silently confirms.
