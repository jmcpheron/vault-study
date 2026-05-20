# Onshape working notes — FDM variant

Inherits from [`../faithful/onshape.md`](../faithful/onshape.md).
This file records the **deltas**: settings and mate strategies that
diverge from the faithful build because of FDM constraints.

When in doubt, follow the faithful conventions and document the
deviation here (and in [`deviations.md`](deviations.md)).

## Variables that differ from faithful

Track per-variable. As of bootstrap, all variables match the
faithful values; deltas land here when the FDM Onshape doc starts
diverging.

| Variable | Faithful | FDM | Why |
| --- | --- | --- | --- |
| _(none yet)_ | | | |

## FeatureScripts

Same Spur Gear FeatureScript as the faithful variant — the
mechanism's gear math is the part we explicitly *do not* change.

## FDM-specific modeling patterns

_(Filled in as decisions are made in the Onshape doc. Likely
entries:_

- Hex-stock substitution pattern for cylindrical parts that need
  anti-rotation (avoids printed keyways).
- Tolerance offsets — clearance-fit holes get extra dimension based
  on tested slicer + filament combination.
- Layer-orientation choice per-part, encoded as a part-attribute
  comment so the 3MF bundle can be assembled programmatically.
  _)_

## Gotchas & lessons learned

_(Add entries here as you run into them. FDM has its own catalog
of "wait, that doesn't work because…" — keep them findable.)_
