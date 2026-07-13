---
title: Mechanics overview
---

# Mechanics overview

<p style="text-align:center; margin: 1em 0;">
  <picture>
    <source srcset="{{ '/assets/generated/mechanism-exploded-fdm.webp' | relative_url }}" type="image/webp">
    <img src="{{ '/assets/generated/mechanism-exploded-fdm.gif' | relative_url }}"
         alt="The vault mechanism in an exploded view: ring gear, twelve spur gears, twelve racks, twelve locking pins, hub plate, and base, fanning out radially from their assembled positions and returning."
         width="520"
         style="max-width:100%; height:auto; border-radius:10px; box-shadow:0 6px 20px rgba(0,0,0,0.08);">
  </picture>
</p>

The vault is a **one-knob lock**. We turn the dial, twelve pins shoot
outward into the frame in unison, and that's the whole thing. Under
the hood it's a chain of three motions, each multiplying the last:

1. **Combination lock → bell crank → ring gear.** Three watchmaker-scale
   wheels in a brass cage form the lock. Dial the right combination,
   a drop arm falls through three aligned slots, a bell crank pivots,
   and the giant **120-tooth ring gear** at the centre of the door is
   released. See [the combination lock]({{ '/combination-lock/' | relative_url }}).
2. **Ring gear → twelve spur gears.** The ring's 120 internal teeth
   mesh with twelve identical **24-tooth spur gears** spaced 30°
   apart. One turn of the ring spins every spur five times. The
   tooth-count ratio is 120 : 24 = 5 : 1; the
   [gearing-math page]({{ '/gearing-math/' | relative_url }}) walks through where the 5
   comes from.
3. **Spur gears → racks → pins.** Each spur drives a square **8 mm × 8 mm
   rack** with module-0.5 teeth on one face. The rack carries a
   **10 mm locking pin** threaded onto its end. As the spur rotates,
   the rack — and the pin attached to it — translates radially
   outward, through a bore in the door body, and into a matching bore
   in the frame.

With all twelve pins extended, the door is locked: each pin couples
it to the surrounding frame. Unlock the bell crank, throw the lever
in reverse, every pin retracts at once, and the door swings open. One
input, twelve coordinated motions — the whole point of the gear
chain.

The chain is **timed**: ring teeth (120) divided by pin count (12)
is 10. There are exactly ten ring teeth between adjacent spur axes.
The arithmetic isn't optional. If 120 ÷ 12 weren't a whole number,
the spurs couldn't all sit in matching phase relative to the ring's
tooth pattern, and the racks would push their pins to subtly
different depths. Adam emphasises this in
[part-2 of the build series]({{ '/sources/' | relative_url }}); the kernel enforces it in
[`vaultkit.gears.teeth_between_satellites`](https://github.com/jmcpheron/vault-study/blob/main/src/vaultkit/gears.py).

## The 12-spur crowding question

The animated diagram above places the twelve spur centres at the
**gear-math-derived radius** of 24 mm from the door centre — the
distance at which the spurs' teeth actually mesh with the ring's. At
that radius, twelve spurs of 12 mm diameter each are nearly
touching (their centres are 12.57 mm apart on the bolt circle, against
spur diameters of 12 mm — 0.57 mm of physical clearance). Adam's
build-video measurements report a 72 mm bolt-circle (36 mm radius),
where the spurs are much further apart — but at 36 mm, the spur teeth
would never reach the ring at all.

There's a real CAD discrepancy here, called out in
[`specs.md`](https://github.com/jmcpheron/vault-study/blob/main/specs.md#derived-values).
The [interactive page]({{ '/interactive/' | relative_url }}) lets you flip between the
two layouts and see the difference.

## See also

- [Gearing math]({{ '/gearing-math/' | relative_url }}) — module, tooth counts, where 5 : 1 comes from.
- [Interactive builder]({{ '/interactive/' | relative_url }}) — drag the slider, watch the pins extend.
- [Why twelve pins?]({{ '/why-twelve-pins/' | relative_url }}) — the divisor argument and base-12 elegance.
- [The combination lock]({{ '/combination-lock/' | relative_url }}) — the gatekeeper at the start of the chain.
- [Faithful vs FDM]({{ '/faithful-vs-fdm/' | relative_url }}) — what changes when you redesign for 3D printers.
