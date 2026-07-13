---
title: "Half a millimetre per degree: the pin-travel math"
date: 2026-05-20 09:00:00 -0700
excerpt: >
  Turn the ring gear one degree and every pin extends 0.524 mm. The
  whole chain — lever to ring to spur to rack to pin — reduces to one
  identity and one ratio, and we drew the technical drawings to prove it.
---

# Half a millimetre per degree: the pin-travel math

Turn the ring gear one degree and every pin extends 0.524 mm. The
whole chain — lever to ring to spur to rack to pin — reduces to one
identity and one ratio, and this post walks both.

<p style="text-align:center; margin: 1.5em 0;">
  <img src="{{ '/assets/generated/technical-top-view.svg' | relative_url }}"
       alt="Top-down technical drawing of the vault mechanism: ring gear pitch diameter Ø60, spur bolt-circle Ø72, pin diameter Ø10, 120 ring teeth, 24-tooth spurs at 30° spacing."
       width="640" style="max-width:100%; height:auto;">
</p>

The identity is the rack-and-pinion one: unroll a spur gear's pitch
circle into a straight line and a rotation of θ radians becomes a
linear travel of exactly `θ · r`. No approximation — an unrolled
circle is the definition of a radian.

The ratio comes from the tooth counts. The 120-tooth ring gear
drives twelve 24-tooth spurs, so each spur turns 120/24 = 5 times
per ring revolution. Chain the two together with the spur's 6 mm
pitch radius (module 0.5 × 24 teeth / 2) and:

```
pin_travel = θ_ring · 5 · 6 mm  ≈  0.524 mm per ring degree
```

At the 15° lever throw we use everywhere on this site, that's
**7.85 mm of pin extension** — enough to bury a pin well past the
0.020" door-frame gap and into its receiver.

## Where the drawing earns its keep

<p style="text-align:center; margin: 1.5em 0;">
  <img src="{{ '/assets/generated/rack-pinion-closeup.svg' | relative_url }}"
       alt="Close-up technical drawing of one spur gear meshing with one rack: 6 mm pitch radius, 1.57 mm tooth pitch, pitch point marked, rack-disengagement limit flagged."
       width="640" style="max-width:100%; height:auto;">
</p>

The close-up also shows the limit: the rack has a finite toothed
section, and past about 12 mm of travel — a 22.9° ring throw — the
spur runs out of rack. That's not a number we invented; it falls
out of `θ · r` run backwards from the rack length.

<p style="text-align:center; margin: 1.5em 0;">
  <img src="{{ '/assets/generated/pin-travel-diagram.svg' | relative_url }}"
       alt="Technical drawing of one pin at rest and after a 15° ring throw, extended 7.85 mm through the door body into the frame receiver."
       width="640" style="max-width:100%; height:auto;">
</p>

The full derivation — with a slider you can drag and the table of
travel per lever angle — lives on the evergreen
[pin travel]({{ '/pin-travel/' | relative_url }}) page; the
[gearing math]({{ '/gearing-math/' | relative_url }}) page covers
where the 5:1 comes from. This post is the story; those pages are
the math.
