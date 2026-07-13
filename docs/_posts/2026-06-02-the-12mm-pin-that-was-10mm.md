---
title: "The 12 mm pin that turned out to be 10 mm"
date: 2026-06-02 09:00:00 -0700
excerpt: >
  In part 2 of the build series, Adam's drawing calls for 12 mm locking
  pins. In part 4, he picks one up and calls it 10 mm. A canonical
  number changed mid-series — which is exactly the situation parametric
  CAD is built for.
---

# The 12 mm pin that turned out to be 10 mm

In [part 2 of the build series](https://www.tested.com/), Adam's
technical drawing calls for 12 mm locking pins. In part 4, he picks
one up on camera and calls it 10 mm. A canonical number changed
mid-series — which is exactly the situation parametric CAD is built
for.

Our [`specs.md`](https://github.com/jmcpheron/vault-study/blob/main/specs.md)
keeps both rows: the 12 mm value struck through and marked
superseded, the 10 mm value tagged `[part-4]`. We could have
silently edited the number, but the strikethrough *is* the lesson.
Dimensions sourced from a video series are measurements of a moving
target, and the honest record shows its revisions.

The mechanical ripple is the interesting part. The pin diameter
drives the twelve radial bores in the acrylic hub, the twelve bores
in the cast-iron puck, and (in our FDM variant) the hex-stock
cross-section that replaces the cylinder. In Onshape that's one
variable — change `#PIN_DIAMETER_MM` and the model re-derives. In
the repo it's one constant, `PIN_DIAMETER_MM` in
[`params.py`](https://github.com/jmcpheron/vault-study/blob/main/src/vaultkit/params.py),
and a drift test fails CI if `specs.md` and the code ever disagree.
One number, one diff, every dependent dimension follows:

<p style="text-align:center; margin: 1.5em 0;">
  <img src="{{ '/assets/generated/technical-top-view.svg' | relative_url }}"
       alt="Top-down technical drawing of the mechanism with the Ø10 pin callout — the revised diameter, not the original 12 mm."
       width="640" style="max-width:100%; height:auto;">
</p>

Part 4 is also where Adam pays for the physical version of this
change. The racks screw into the pins on threaded studs he first
cut by hand with a die, and hand-cut threads came out about 0.0125"
off-center. Screwed together, the racks sat sideways and the pins
bound in their bores. His fix is a lovely piece of shop discipline:
an 8 mm square 5C collet to hold the stock dead-center, a depth
stop so every rack protrudes identically, and the die held in the
lathe's tailstock so the thread can only go on straight. He also
machines **14 racks for 12 slots** — "always make more than you
need," because assumptions kill.

We get all of that for free with a circular pattern, which is worth
being honest about: the CAD version of this project skips the
hardest parts. What we keep is the arithmetic — and the reminder
that a 0.0125" error was enough to jam the mechanism. That number
comes back in a later post, where we run the same stack-up math
forward for the printed version.
