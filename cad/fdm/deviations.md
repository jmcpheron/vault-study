# FDM deviations from the faithful variant

The single home for every "why is the FDM one different from Adam's
build?" answer. The two variants will drift. This is where the drift
is explained — not in commit messages, not in Slack, not in the
explainer pages alone.

Each entry: **what changed**, **why** (the manufacturing or
ergonomic reason), and **link to specs.md / params.py** if the change
touched a canonical number.

## Format

```markdown
### Short name of the change

**Parameter / part:** Which thing was modified.
**Faithful value:** What Adam's build uses.
**FDM value:** What this variant uses.
**Why:** The manufacturing or ergonomic reason.
**Trade-off:** What we gave up.
**Related:** Links to specs.md sections, deviations elsewhere, or the
explainer page that motivates the choice.
```

---

## Planned deviations (not yet implemented in the Onshape doc)

### Hex stock instead of cylinders for the rack stock

**Parameter / part:** Rack stock cross-section.
**Faithful value:** 8 mm × 8 mm square stock, M6 turned-down stud
(see [`../../specs.md`](../../specs.md) → "Racks").
**FDM value:** TBD — hexagonal or octagonal stock so the rack can't
spin in its bore without needing a keyway.
**Why:** FDM threaded studs are unreliable at this scale; we want
the rotational lock to come from geometry, not threads.
**Trade-off:** Slightly more complex slot in the door body.
**Related:** [`../../docs/fdm-variant.md`](../../docs/fdm-variant.md)

### Loosened pin-to-bore clearance

**Parameter / part:** Locking-pin radial bore.
**Faithful value:** 10 mm dia bore for a 10 mm pin (effectively
zero clearance — machined slip-fit, see
[`../../specs.md`](../../specs.md) → "Main door body").
**FDM value:** TBD — likely 10.4 mm bore for a 10 mm pin, tuned per
slicer + filament profile.
**Why:** FDM hole tolerances are stack-dependent and tighten on
cooling.
**Trade-off:** Pins rattle slightly when unlocked. Acceptable for a
hobby print.
**Related:** [`../../docs/fdm-variant.md`](../../docs/fdm-variant.md)

### Drop the hinge-and-frame assembly entirely (initial release)

**Parameter / part:** Hinge + aluminum frame.
**Faithful value:** Full multi-bearing hinge on a 1/2 in 6061
aluminum frame.
**FDM value:** First MakerWorld release ships just the round
mechanism puck; no hinge, no frame. Door sits on the table.
**Why:** Hinge requires hardware we don't want first-time printers
to source. Mechanism is the interesting bit.
**Trade-off:** Less complete as a display piece. Plan: hinge as a
v2 add-on.
**Related:** [`../../docs/fdm-variant.md`](../../docs/fdm-variant.md)

---

## Live deviations (in the FDM Onshape doc)

_(Move entries from "Planned" to "Live" as they land in the doc.
Currently empty — the FDM Onshape doc is still being built.)_
