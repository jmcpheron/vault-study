---
title: FDM design considerations
---

# FDM design considerations

_(Stub — to be written. Goal: explain the design choices that make
the FDM variant printable at home: cylinders → hex stock for
anti-rotation, tolerance loosening for FDM hole stack-up, layer
orientation per part, support-free part design. Each choice cites
back to a specific entry in the
[deviations log](https://github.com/jmcpheron/vault-study/blob/main/cad/fdm/deviations.md).)_

The canonical record of every FDM-specific decision lives in
[`cad/fdm/deviations.md`](https://github.com/jmcpheron/vault-study/blob/main/cad/fdm/deviations.md).
This page is the human-facing explanation of *why*.

## See also

- [Pin travel](pin-travel.html) — the kinematic math, identical for
  both variants (module, tooth counts, and ratio are preserved).
- [Faithful vs FDM](faithful-vs-fdm.html) — STEP-level differences.
