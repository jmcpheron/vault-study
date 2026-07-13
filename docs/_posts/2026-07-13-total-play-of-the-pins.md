---
title: "How much do the pins actually rattle? A tolerance stack-up"
date: 2026-07-13 00:00:00 +0000
excerpt: >
  A printed Ø10 pin in a Ø10.4 bore has 0.2 mm of radial slop — but how
  much can the pin tip really move, and how far can the locked door
  shift before the pins catch it? We ran the stack-up, faithful vs FDM.
---

# How much do the pins actually rattle? A tolerance stack-up

A printed Ø10 pin in a Ø10.4 bore has 0.2 mm of radial slop — but
how much can the pin tip really move, and how far can the locked
door shift before the pins catch it? We ran the stack-up for both
variants, and every number below comes out of the repo's math
kernel, not out of our heads.

<p style="text-align:center; margin: 1.5em 0;">
  <img src="{{ '/assets/generated/pin-play-diagram.svg' | relative_url }}"
       alt="Cross-section technical drawing of one Ø10 locking pin extended through a Ø10.4 door bore into the frame receiver, showing the 0.2 mm radial clearance, the 0.508 mm door-frame gap, and the 1.03° maximum tilt, with clearances exaggerated 10× for visibility."
       width="640" style="max-width:100%; height:auto;">
</p>

## The fits

The faithful variant's pins ride in machined, reamed bores — Adam's
slip fit. We model that clearance as zero (a real slip fit is a few
hundredths of a millimetre; we don't have his reamer chart, so zero
plus a hedge is more honest than a guessed decimal). The FDM
variant can't play that game: printed bores need real clearance or
the pin fuses to the door. The planned bore from
[`cad/fdm/deviations.md`](https://github.com/jmcpheron/vault-study/blob/main/cad/fdm/deviations.md)
is **10.4 mm for the 10 mm pin** — 0.4 mm diametral, 0.2 mm radial,
still TBD until we tune it on an actual print.

## The stack-up

At the standard 15° lever throw (7.85 mm of pin extension — see
[pin travel]({{ '/pin-travel/' | relative_url }})):

| | faithful | FDM |
| --- | ---: | ---: |
| Bore diameter | 10.000 mm | 10.400 mm |
| Diametral clearance | 0.000 mm | 0.400 mm |
| Radial clearance | 0.000 mm | 0.200 mm |
| Tilt at rest (30 mm guided) | 0.000° | 0.764° |
| Tilt extended (22.1 mm guided) | 0.000° | 1.035° |
| Lateral play at the pin tip | 0.000 mm | 0.351 mm |
| Locked-door play | 0.000 mm | 0.400 mm |
| Door-frame gap | 0.508 mm | 0.508 mm |

Three things in that table are worth unpacking.

**Tilt grows as the pin extends.** A pin can cock inside its bore
until it touches both walls: `atan(clearance / guided length)`. At
rest the full 30 mm of pin is guided and the FDM pin can tilt
0.764°. Extended 7.85 mm, only 22.1 mm remains in the bore and the
tilt grows to 1.035°. Project that tilt over the overhanging tip —
7.85 mm of extension plus the 0.508 mm door-frame gap — add the
0.2 mm of pure sideways float, and the FDM pin tip can wander
**0.351 mm** before anything stops it.

**The pins catch the door before the frame does.** Locked, each
pin bridges the door bore and the frame receiver. The door can
shift by the sum of the two radial clearances — 0.4 mm for the FDM
variant (assuming the receivers get the same fit as the door
bores) — before pins bear on both walls. That's *less* than the
0.508 mm door-frame gap, so in the printed vault the locking pins,
not the door rim, are what you feel when you shake the locked
door. In the faithful variant both numbers at the pin are zero,
and the 0.020" rim gap is the only play there is.

**Adam already ran this math in reverse.** In part 4, his
hand-threaded rack studs came out 0.0125" (0.318 mm) off-center —
comfortably inside our FDM clearance budget, but his bores had no
budget. In a near-zero-clearance slip fit, 0.318 mm of stud offset
is the whole stack-up spent on one error, and his pins bound
exactly the way the table predicts. Tight fits don't forgive;
that's what the 5C collet was for
(the [previous post]({{ '/2026/06/02/the-12mm-pin-that-was-10mm/' | relative_url }})
has that story).

## What we're not counting yet

Gear backlash. Every gear mesh has a dead-band, and a
rack-and-pinion passes it straight through to pin travel, 1:1. We
don't have a measured backlash figure for module-0.5 gears —
machined or printed — so it appears in the kernel as an input with
no default, not as a made-up constant. When the first FDM gears
come off the printer, we'll measure it, it becomes a `params.py`
number, and this table grows a row.

---

*The table is computed by
[`src/vaultkit/play.py`](https://github.com/jmcpheron/vault-study/blob/main/src/vaultkit/play.py)
from the canonical dimensions in
[`specs.md`](https://github.com/jmcpheron/vault-study/blob/main/specs.md) —
run `vaultkit play` to reproduce it. The diagram above is generated
from the same constants. See also
[faithful vs FDM]({{ '/faithful-vs-fdm/' | relative_url }}) for the
two variants' broader diff.*
