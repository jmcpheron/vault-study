# FDM variant

The same vault mechanism, redesigned for desktop FDM 3D printers.
Aims to print on a stock Bambu A1 / Prusa Mini class machine in one
evening's worth of jobs, no supports required, no post-machining,
no specialty filaments.

Design philosophy: **preserve the mechanism, swap the manufacturing
language.** Cylinders become hex stock so anti-rotation comes from
geometry instead of keyways. Tolerances loosen from "0.020 in
clearance everywhere" to FDM-realistic numbers. Layer orientation
is chosen per-part. See [`deviations.md`](deviations.md) for the
running list of "why is the FDM one different here?" answers.

## Onshape document

_(Placeholder — fill in once the document is created and shared publicly.)_

`https://cad.onshape.com/documents/<TBD>`

Early STEP export already in
[`../../step-source/fdm-vault.step`](../../step-source/fdm-vault.step).

## Modeling conventions

See [`onshape.md`](onshape.md) for FDM-specific FeatureScript settings
and Assembly notes. Inherits from
[`../faithful/onshape.md`](../faithful/onshape.md); only differences
are recorded.

## Print profile

_(Will live alongside the 3MF bundle once that ships. Aim: 0.2 mm
layer height, 4-wall perimeter on the geared parts, PETG for the
mechanism, PLA for the cosmetic puck.)_

## MakerWorld + Printables

| Site | Status |
| --- | --- |
| MakerWorld | _(not yet listed)_ |
| Printables | _(not yet listed)_ |

When the first listing goes live, paste the URL here, and link back
from the listing description to this repo + the Onshape doc.

## Related

- [`../faithful/`](../faithful/) — the machined-replica variant.
- [`deviations.md`](deviations.md) — the canonical log of FDM
  design choices.
- [`../../docs/fdm-variant.md`](../../docs/fdm-variant.md) — the
  human-facing explainer page about *why* these choices were made.
