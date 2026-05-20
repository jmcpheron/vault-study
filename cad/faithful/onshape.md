# Onshape working notes — faithful variant

CAD-tool-specific guidance for the faithful build. [`../../specs.md`](../../specs.md)
is for *what* to model; this file is for *how* to model it in Onshape.

Absorbed and expanded from `vault-notes-from-youtube/onshape-notes.md`
plus the per-video "Tips for Modeling this in Onshape" sections in
parts 1–5.

## Variables at the top of the Part Studio

Every parameter in [`../../src/vaultkit/params.py`](../../src/vaultkit/params.py)
should also be defined as an Onshape variable at the top of the
Part Studio, using the same name (in Onshape's `#snake_case` form).
The Onshape variables are the editing surface; `params.py` is the
diffable record. They are kept in sync **by hand** until automation
lands.

Example: `#PIN_DIAMETER_MM = 10 mm` drives every radial bore in
both the acrylic hub and the cast-iron puck. Change the variable,
the whole model re-derives.

## FeatureScripts

Don't hand-draw involute gear teeth — the standard custom-feature
library has a **Spur Gear** generator. Add it via "Add custom
features" in any Part Studio.

| Gear | Settings |
| --- | --- |
| Spur gear (qty 12) | Module 0.5, 24 teeth |
| Ring gear | Module 0.5, 120 teeth, **Internal Gear** option |

The 2.4-in outer-diameter target on the ring gear should fall out
of the math once module and tooth count are right; verify against
[`../../specs.md`](../../specs.md) after generating.

## Assembly: getting them to mesh

1. **Revolute Mate** each spur gear and the ring gear to the
   acrylic hub so each rotates about its axis.
2. **Gear Relation** between the ring gear and *one* spur gear.
   Onshape derives the 5:1 ratio from the tooth counts automatically.
3. For the locking pins, **Slider Mate** the pin radially through
   the hub, then **Rack and Pinion Relation** between the spur's
   Revolute Mate and the pin's Slider Mate. Drive the ring gear
   and watch the pin extend.
4. **Circular Assembly Pattern** the perfectly-mated single
   spur+pin assembly 12 times around 360° at 30° intervals. This
   is the CAD answer to Adam's "all 12 racks must be machined
   identically" problem — Onshape mathematically guarantees it.

## Sub-assemblies (recommended)

Build one (spur + rack + pin) as its own Assembly tab, fully mated,
fully timed. Insert that sub-assembly 12 times into the main vault
assembly. Keeps the mate tree clean.

## Door swing kinematics

Once the heavy puck, frame, and hinge are modelled (see
[`../../specs.md`](../../specs.md) → Hinge section), Revolute Mate the
door to the hinge pin and **drag the door open with the mouse**.
Use Onshape's **Interference Detection** to check whether the back
edge of the puck clips the aluminum frame at any angle. This is the
issue Adam discovered only after machining — CAD catches it for
free.

## Combination lock as a sub-assembly

Build the 0.75 in × 0.5 in cage as a completely separate Assembly
tab. Get the three 0.450 in wheels, the cage, and the 1/8 in
spindle perfectly aligned, then insert that sub-assembly into the
main vault. Use **Tangent Mates** or limit constraints to simulate
the drive-tab "drag" between adjacent wheels.

## Gotchas & lessons learned

_(Add entries here as you run into them.)_
