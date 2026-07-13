---
title: "Exploding the vault: animated views from the STEP file"
date: 2026-06-17 09:00:00 -0700
excerpt: >
  The FDM variant, pulled apart along its assembly axis: one body
  plate, one ring gear, twelve spur-and-rack sets. The exploded view
  is generated straight from the STEP export, so it can never drift
  from the actual model.
---

# Exploding the vault: animated views from the STEP file

The FDM variant, pulled apart along its assembly axis: one body
plate, one ring gear, twelve spur-and-rack sets. The exploded view
is generated straight from the STEP export, so it can never drift
from the actual model.

<p style="text-align:center; margin: 1.5em 0;">
  <picture>
    <source srcset="{{ '/assets/generated/mechanism-exploded-fdm.webp' | relative_url }}" type="image/webp">
    <img src="{{ '/assets/generated/mechanism-exploded-fdm.gif' | relative_url }}"
         alt="Exploded-view animation of the FDM vault mechanism: the ring gear and twelve spur-and-rack sets lift away from the body plate and reassemble."
         width="560" style="max-width:100%; height:auto;">
  </picture>
</p>

What the explosion makes obvious that the assembled view hides:

- **The part count is honest.** One plate, one ring, and twelve
  copies of the same three-part satellite. If you can print one
  spur-and-rack set that works, you can print the whole door.
- **The assembly order is forced.** The ring gear has to land in
  the central cavity before any satellite goes in, because the
  racks trap it radially. The animation is accidentally an
  assembly manual.
- **Everything stacks along one axis.** That's the FDM redesign
  doing its job — every part lies flat on the build plate, and the
  whole mechanism assembles by dropping parts straight down.

## The mechanism in motion

The companion animation sweeps the cam through its throw — the
same 15° that the [pin-travel math]({{ '/pin-travel/' | relative_url }})
converts to 7.85 mm of pin extension:

<p style="text-align:center; margin: 1.5em 0;">
  <picture>
    <source srcset="{{ '/assets/generated/mechanism-cam-sweep-fdm.webp' | relative_url }}" type="image/webp">
    <img src="{{ '/assets/generated/mechanism-cam-sweep-fdm.gif' | relative_url }}"
         alt="Cam-sweep animation of the FDM vault mechanism: the ring gear oscillates and twelve pins extend and retract in unison."
         width="560" style="max-width:100%; height:auto;">
  </picture>
</p>

## Faithful vs FDM, one frame each

Side by side, the two variants' current states — the faithful puck
still blocky, the FDM plate further along:

<p style="text-align:center; margin: 1.5em 0;">
  <img src="{{ '/assets/generated/faithful-iso.png' | relative_url }}"
       alt="Isometric render of the faithful variant: a solid puck with side-bored pin holes."
       width="360" style="max-width:48%; height:auto;">
  <img src="{{ '/assets/generated/fdm-vault-iso.png' | relative_url }}"
       alt="Isometric render of the FDM variant: a thin plate with twelve radial bays."
       width="360" style="max-width:48%; height:auto;">
</p>

The [faithful vs FDM]({{ '/faithful-vs-fdm/' | relative_url }})
page holds the full STEP-level diff — bounding boxes, entity
histograms, and why the FDM file is the more developed of the two.

How these are made, in one paragraph: the STEP export from Onshape
gets pulled apart into named parts, each part is tessellated to
STL, and an OpenSCAD template animates the stack — all driven by
the repo's Python tooling (the
[README](https://github.com/jmcpheron/vault-study#readme) has the
pipeline). The point of the plumbing is that none of these images
are drawn by hand; re-export the STEP and every view regenerates.
