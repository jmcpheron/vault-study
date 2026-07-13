---
title: Faithful vs FDM
---

# Faithful vs FDM, side by side

Two variants in parallel: a CAD reinterpretation of Adam Savage's
machined design and a redesign for desktop 3D printers. They share
the mechanism — module 0.5 gears, 12 pins, 120/24 tooth counts — and
diverge on everything to do with manufacturing.

This page is the diff. We show what's currently in each STEP file,
what the geometry choices reveal about the two design philosophies,
and what each variant is still missing relative to
[`specs.md`](https://github.com/jmcpheron/vault-study/blob/main/specs.md).

All numbers below come from `vaultkit step inspect`, run against
the two STEP files in
[`step-source/`](https://github.com/jmcpheron/vault-study/tree/main/step-source).

## At a glance

| | Faithful (Adam-replica) | FDM (printable) |
|---|---|---|
| STEP file | [`unauthorized-vault-clone.step`](https://github.com/jmcpheron/vault-study/blob/main/step-source/unauthorized-vault-clone.step) | [`fdm-vault.step`](https://github.com/jmcpheron/vault-study/blob/main/step-source/fdm-vault.step) |
| Onshape doc | [open in Onshape ↗](https://cad.onshape.com/documents/eaf3e87c1faae12ad867b335/w/83a96bb8921d1af3abd7aecd/e/9db299b535aaeded5de5120c) | [open in Onshape ↗](https://cad.onshape.com/documents/017898deda56c430272a5497/w/5d7667d0936a708006b152fa/e/8e68069be3521bc23b864206) |
| Bounding box (mm) | 171 × **50** × 171 | 171 × **31** × 171 |
| Body shape | Chunky puck (mimics Adam's cast-iron cylinder) | Thin washer with radial cutouts |
| Triangle count @ 0.5 mm | 50,896 | 60,428 |
| Total STEP entities | 37,633 | 48,924 |
| Tapers / fillets / ellipses | ❌ none | ✅ present |
| Assembly instances | 26 | 39 |

The X/Z dimensions are nearly identical (within 0.2 mm) — both
target a 6-inch / ~152 mm outer-diameter envelope. The Y dimension
is what tells us the story:

- **Faithful: 50 mm (~1.97")** — closer to the combined acrylic-hub
  (1.25") + cast-iron-puck face thickness. The geometry mimics the
  deep, machined cylinder Adam works from.
- **FDM: 31 mm (~1.22")** — matches the 1.25-inch acrylic-hub
  thickness from [`specs.md`](https://github.com/jmcpheron/vault-study/blob/main/specs.md#main-door-body-acrylic-hub).
  The FDM redesign flattens everything to fit on a 3D-printer build
  plate.

## The two designs

### Faithful

![Faithful variant, isometric render]({{ '/assets/generated/faithful-iso.png' | relative_url }})

The faithful (in-progress) Onshape redesign of Adam's lathe-made
vault. Notable features visible from the iso view:

- **Pin bores on the side rim** — the 12 radial holes for the
  locking pins open through the cylindrical side of the puck, as
  they would on the real vault.
- **Solid puck profile** — the body is one chunky cylinder, not
  yet hollowed out for the gear mechanism. The internal cavity
  Adam mentions in part-3 (see [`specs.md`](https://github.com/jmcpheron/vault-study/blob/main/specs.md#heavy-door-puck-cast-iron-outer))
  (0.5" solid front face, hollow middle, 0.75" closure depth)
  isn't modeled yet.
- **No tapers, fillets, or ellipses** in the STEP entity histogram —
  the 10° edge taper from [`specs.md`](https://github.com/jmcpheron/vault-study/blob/main/specs.md#heavy-door-puck-cast-iron-outer)
  hasn't been added.

What it has so far: the basic puck volume, the side-bored pin
holes, and the two gear products in the assembly.

### FDM

![FDM variant, isometric render]({{ '/assets/generated/fdm-vault-iso.png' | relative_url }})

The FDM-printer-friendly variant. The geometry decisions read
loudly:

- **Donut/washer profile** — the body is a thin flat plate with a
  big central hole. The ring gear sits in the central cavity; the
  spur gears mount in the radial bays around it.
- **12 radial slots** visible in the disc — the cutouts that
  accommodate the spur-and-pin sub-assemblies, replacing the
  side-drilled pin bores of the faithful version. Each part lays
  flat on the build plate.
- **Conical, toroidal, and elliptical surfaces present** in the
  STEP entity histogram — those are the FDM-specific fillets,
  chamfers, and rounded edges that make a part 3D-printable without
  fragile sharp corners.
- **More assembly instances** (39 vs 26) and **more total
  geometry** (49K entities vs 38K) — the FDM design is further
  along in detail, not behind.

The FDM design philosophy in one line: **preserve the mechanism,
swap the manufacturing language.** Same 12 pins, same 120/24 gear
math, same combination-lock-as-gatekeeper — but the body becomes a
stack of flat printable plates instead of a chunky machined puck.

## What both files share

- Both export from Onshape via the ST-Developer / STEP Tools
  toolchain (AP242 Edition 2).
- Both contain exactly four named products: `Assembly N`, `Part 1`
  (the body), `Spur gear (120 teeth)` (the ring — Onshape's Spur
  Gear FeatureScript labels internal gears the same way), and
  `Spur gear (24 teeth)` (the satellites).
- Both reach a ~152 mm outer diameter (the 6-inch door target).
- Both currently model only the **central mechanism**: hub + ring +
  spurs. Nothing else from [`specs.md`](https://github.com/jmcpheron/vault-study/blob/main/specs.md)
  is in either STEP yet.

## What's missing from both (still in spec, not in CAD)

The gap between [`specs.md`](https://github.com/jmcpheron/vault-study/blob/main/specs.md)
and either STEP file:

| Subsystem | In faithful STEP? | In FDM STEP? | Spec section |
|---|---|---|---|
| Ring gear + 12 spur gears | ✅ | ✅ | [Ring/Spur](https://github.com/jmcpheron/vault-study/blob/main/specs.md#ring-gear) |
| Locking pins (12 × 10 mm dia × 30 mm) | ❌ | ❌ | [Locking pins](https://github.com/jmcpheron/vault-study/blob/main/specs.md#locking-pins) |
| Racks (8×8 mm, M6 stud, ball-mill relief) | ❌ | ❌ | [Racks](https://github.com/jmcpheron/vault-study/blob/main/specs.md#racks-drive-the-pins) |
| Heavy cast-iron puck (10° taper, 0.75" depth) | ❌ | n/a (intentional) | [Heavy door puck](https://github.com/jmcpheron/vault-study/blob/main/specs.md#heavy-door-puck-cast-iron-outer) |
| Frame (½" 6061, 6" opening) | ❌ | n/a (deferred) | [Door frame](https://github.com/jmcpheron/vault-study/blob/main/specs.md#door-frame) |
| Hinge (3/8" bearings, 28 × M2) | ❌ | n/a (deferred) | [Hinge](https://github.com/jmcpheron/vault-study/blob/main/specs.md#hinge) |
| Combination lock (3 wheels in 0.75"×0.5" cage) | ❌ | ❌ | [Combo lock](https://github.com/jmcpheron/vault-study/blob/main/specs.md#combination-lock) |

`n/a (intentional)` means the FDM variant chose to skip that
subsystem on purpose — see
[`cad/fdm/deviations.md`](https://github.com/jmcpheron/vault-study/blob/main/cad/fdm/deviations.md).
`❌` means it's still on the to-do list.

## Why the FDM file is more developed

A surprise we hit while writing this page: the FDM STEP has **28
conical surfaces, 8 toroidal surfaces, 193 ellipses**. The faithful
STEP has **zero of each**.

That's not a mistake — it's two different states of progress:

- The **FDM variant** has gotten farther in the redesign, including
  the fillets, chamfers, and rounded transitions that make
  individual parts printable. Sharp corners snap on FDM prints; we
  rounded them off, which means lots of curved surfaces in the
  geometry.
- The **faithful variant** is still at the "block out the basic
  shapes" stage. The 10° tapered edge from part-3 — which would
  produce conical surfaces in the STEP — hasn't landed yet.

So the FDM variant isn't simpler. It's *more refined, in a different
direction*.

## Reproducing this page

Every number and image above came from these commands. Re-run them
after re-exporting either STEP from Onshape and the page updates:

```bash
# Inspect (prints the same data the table rows are pulled from)
vaultkit step inspect step-source/fdm-vault.step
vaultkit step inspect step-source/unauthorized-vault-clone.step

# Hero PNGs (writes to docs/assets/generated/)
vaultkit step render step-source/fdm-vault.step \
    --out docs/assets/generated/fdm-vault-iso.png
vaultkit step render step-source/unauthorized-vault-clone.step \
    --out docs/assets/generated/faithful-iso.png
```

## See also

- [`cad/faithful/`](https://github.com/jmcpheron/vault-study/tree/main/cad/faithful) — faithful-variant docs, Onshape conventions.
- [`cad/fdm/deviations.md`](https://github.com/jmcpheron/vault-study/blob/main/cad/fdm/deviations.md) — the canonical FDM-deviation log.
- [Gearing math]({{ '/gearing-math/' | relative_url }}) — what the shared mechanism actually computes to.
