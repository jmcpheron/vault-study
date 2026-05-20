---
title: What this project believes
---

# What this project believes

Five things. We try to live by them in the code, in the diagrams,
and in the prose. If any page on this site contradicts one, file an
issue — we'd rather fix it than be wrong about it.

## Parametric beats screenshot

Every dimension in this project lives in **one Python file**
([`src/vaultkit/params.py`](https://github.com/jmcpheron/vault-study/blob/main/src/vaultkit/params.py)).
Change `PIN_DIAMETER_MM` from 10 to 12 and the whole site rebuilds:
the SVG schematics shift, the OpenSCAD animations re-render, the
explainer pages quote the new number, the drift test makes sure
nothing in `specs.md` got missed. Screenshots lie about what a
project actually is at any given moment; parameters don't.

## Hands-on beats documentation

A slider that drives twelve gears teaches the mechanism in three
seconds. Three paragraphs about gear ratios teach it in three
minutes — and only to readers who finish them. So our hero is
[the interactive demo](interactive.html), not the prose. The prose
is for after you've grabbed the slider.

## Two variants, one mechanism

Adam Savage's machined vault and our FDM-printable redesign share
the same 120-tooth ring, twelve 24-tooth spurs, twelve pins, and a
combination-lock-as-gatekeeper. They differ in everything else —
cast iron vs PETG, side-bored cylinders vs hex-stock anti-rotation,
0.020-inch machined fits vs slicer-tested clearances. The
[mechanism stays the same](mechanics.html); the
[manufacturing language](faithful-vs-fdm.html) changes.

## The discrepancies are the lessons

When the gear math derives a 24 mm spur radius and Adam measured a
36 mm one, we don't pick a side and quietly delete the other. The
[interactive page](interactive.html) has a checkbox that flips
between them, and the math behind both gets its own page. The
disagreement is more interesting than either resolution. We learn
the most from the things that don't quite line up.

## Credit Adam

The mechanism design, the 120-tooth ring, the 5:1 ratio, the
combination-lock-as-gatekeeper coupling — that's all
[Adam Savage](https://www.tested.com/)'s work on the Tested YouTube
channel. This site is an independent CAD reinterpretation for
educational and hobby purposes. The **geometry** is CC BY-SA 4.0
(share-alike); the **code** that processes it is MIT. Both are
linked from the [repo](https://github.com/jmcpheron/vault-study).
We try to link to Adam's videos every time we cite him. He's the
reason this project exists.

---

The contributor-facing style guide lives at
[`STYLE.md`](https://github.com/jmcpheron/vault-study/blob/main/STYLE.md).
It's where the editorial rules behind these principles get spelled
out for anyone writing code or prose for this repo.
