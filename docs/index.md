---
title: Vault Study
---

# Vault Study

A hobby project to redesign **Adam Savage's miniature (1/12-scale)
bank-vault door** in parametric CAD. The repo behind this site lives
at [github.com/jmcpheron/vault-study](https://github.com/jmcpheron/vault-study).

Two variants in parallel:

- **Faithful** — a CAD reinterpretation of the machined design Adam
  built on the [Tested YouTube series](https://www.tested.com/).
- **FDM** — the same mechanism redesigned for desktop 3D printers.
  Cylinders become hex stock, tolerances loosen, parts orient to
  avoid supports.

The faithful design is the **reference**; the FDM design is the
**translation**. Every difference between them is recorded in
[the FDM deviations log](https://github.com/jmcpheron/vault-study/blob/main/cad/fdm/deviations.md).

## How the vault works

A 120-tooth ring gear sits in the center of an acrylic puck.
Twelve 24-tooth spur gears surround it, each driving a rack-and-pinion
that pushes a locking pin radially outward into the vault frame.
A miniature 3-wheel combination lock is the gatekeeper: dial the
right combination and a bell crank releases the ring gear so the
big lever can throw all 12 pins at once.

That's the whole machine. The rest is dimensions.

## Explainer pages

- [The gearing math](gearing-math.html) — module, tooth counts, why
  the 5:1 ratio falls out for free, what the Spur Gear FeatureScript
  actually wants from you.
- [Mechanics overview](mechanics.html) — the full power chain from
  dial → wheels → bell crank → ring gear → spurs → racks → pins.
- [Why twelve pins?](why-twelve-pins.html) — the divisor math, base 12,
  and why halving Adam's "real-vault" 24 still works.
- [The combination lock](combination-lock.html) — watchmaker-scale
  3-wheel mechanism in a 0.75" × 0.5" brass cage.
- [The hinge and frame](hinge-and-frame.html) — heavy door swing
  kinematics; the clearance problem CAD catches for free.
- [FDM design considerations](fdm-variant.html) — what changes when
  the geometry has to come off a Bambu A1 in PETG. Cylinders → hex
  stock, tolerances, layer orientation.
- [Faithful vs FDM, side by side](faithful-vs-fdm.html) — what's
  currently in each STEP file, what's the same, what diverges, and
  what's still missing.
- [Build log](build-log.html) — informal session notes.
- [Sources](sources.html) — the videos, with timestamps and
  attribution.

## Get the files

| Variant | Onshape | MakerWorld | Printables | STEP |
| --- | --- | --- | --- | --- |
| Faithful | _(placeholder)_ | n/a | n/a | [in repo](https://github.com/jmcpheron/vault-study/blob/main/step-source/unauthorized-vault-clone.step) |
| FDM | _(placeholder)_ | n/a | n/a | [in repo](https://github.com/jmcpheron/vault-study/blob/main/step-source/fdm-vault.step) |

## Credit

The mechanism design, the proportions, the gear math — that's
**Adam Savage's work**, shown on the Tested YouTube channel. This
site is an independent educational CAD reinterpretation. Full
attribution in
[ACKNOWLEDGMENTS.md](https://github.com/jmcpheron/vault-study/blob/main/ACKNOWLEDGMENTS.md).
