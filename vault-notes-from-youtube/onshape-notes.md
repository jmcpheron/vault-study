# Onshape working notes

CAD-tool-specific guidance, distilled from initial research and updated as I
go. `specs.md` is for *what* to model; this file is for *how* to model it in
Onshape specifically.

## FeatureScripts to use

Don't hand-draw involute gear teeth — Onshape's standard custom-feature
library has a **Spur Gear** generator. Add it via "Add custom features" in any
Part Studio.

| Gear | Settings |
| --- | --- |
| Spur gear (qty 12) | Module 0.5, 24 teeth |
| Ring gear | Module 0.5, 120 teeth, internal-gear option |

The 2.4-in outer-diameter target on the ring gear should fall out of the math
once module and tooth count are right; verify against `specs.md` after generating.

## Assembly: getting them to mesh

1. **Revolute Mate** each gear and pin to the base plate so it can rotate
   about its axis.
2. **Gear Relation** between the ring gear and each spur gear. Onshape derives
   the 5:1 ratio from the tooth counts automatically (no need to type it).
3. For the locking pins, a **Rack and Pinion Relation** (rather than Gear
   Relation) ties each pin's linear motion to its spur gear's rotation.

Driving the ring gear should then animate all 12 pins extending in unison.

## Gotchas & lessons learned

_(Add entries here as I run into them.)_
