# Vault Study

A hobby project to redesign **Adam Savage's miniature (1/12-scale)
bank-vault door** in parametric CAD. Two variants in parallel:

- **Faithful** — a CAD reinterpretation of Adam's machined design as
  built on his [Tested YouTube series](https://www.tested.com/). Same
  module-0.5 gears, same 120-tooth ring + 12 × 24-tooth spurs + 12
  rack-driven locking pins, same combination-lock-as-gatekeeper.
- **FDM** — the same mechanism redesigned for desktop 3D printers.
  Cylinders become hex stock (anti-rotation without keyways),
  tolerances loosen, parts orient to avoid supports. Aims to be
  printable on a stock Bambu A1 / Prusa Mini class machine in one
  evening's worth of jobs.

The repo is the workshop. The CAD source of truth lives in two
public **Onshape** documents (links below, both still being built).
The end-state is a 3MF bundle on **MakerWorld** and **Printables**
that anyone can print at home without reading any of this.

## Pipeline

```
   Onshape doc (faithful)   Onshape doc (FDM)
       │                          │
       │ STEP export              │ STEP export
       ▼                          ▼
   step-source/unauthorized-     step-source/fdm-vault.step
   vault-clone.step
       │                          │
       └────────── vaultkit ──────┘
                       │
                       │ derived artifacts (STL / 3MF / SVG / GIF / explainer pages)
                       ▼
            docs/ → github.io
                       │
                       ▼
            MakerWorld + Printables
```

## What's where

| Path | What it is |
| --- | --- |
| [`specs.md`](specs.md) | Canonical dimensions, source-tagged to the video they came from. The keystone. |
| [`src/vaultkit/`](src/vaultkit/) | Python kernel — `gears.py`, `params.py`, CLI, and stubs for the heavier STEP/render pipeline. |
| [`cad/faithful/`](cad/faithful/) | Faithful-variant docs: Onshape doc link, machining notes, FeatureScript settings. |
| [`cad/fdm/`](cad/fdm/) | FDM-variant docs + [`deviations.md`](cad/fdm/deviations.md) — the home for every "why is the FDM one different?" answer. |
| [`step-source/`](step-source/) | Raw STEP exports from Onshape. The inbox; the kernel reads from here. |
| [`docs/`](docs/) | GitHub Pages explainer site (Jekyll). Mechanics, gearing math, FDM design choices. |
| [`log.md`](log.md) | Build journal. Reverse-chronological. |
| [`vault-notes-from-youtube/`](vault-notes-from-youtube/) | **Will be removed** in a follow-up commit once the absorption into `specs.md` is verified. |

## Status (live links)

| Variant | Onshape | MakerWorld | Printables |
| --- | --- | --- | --- |
| Faithful | _(in progress — placeholder)_ | n/a | n/a |
| FDM | _(in progress — placeholder)_ | n/a | n/a |

The early STEP exports for both are already in [`step-source/`](step-source/).

## Quick start

```bash
# Light extras (no CAD libraries) — enough to run the gear math + tests
pip install -e ".[dev]"

# Show the gear-math summary derived from specs.md / params.py
vaultkit gears info

# Tests + lint
pytest
ruff check src tests
```

The heavy CAD libraries (cadquery-ocp, trimesh, etc.) are behind
`pip install -e ".[heavy]"` so contributors who only want to edit
prose aren't forced into a 180 MB OpenCascade wheel.

## Attribution

Mechanism design, proportions, and gear math are Adam Savage's,
shown on the Tested YouTube series. This repo is an independent
educational CAD reinterpretation. Full attribution and source
links in [`ACKNOWLEDGMENTS.md`](ACKNOWLEDGMENTS.md).

## Licenses

- **Code** (`vaultkit`, tests, configs): MIT — see [`LICENSE`](LICENSE).
- **3D geometry** (STEP files, derived STL/3MF/renders): CC BY-SA 4.0
  — see [`LICENSE-3D-FILES`](LICENSE-3D-FILES).

## Pattern

This repo follows the **Shareable CAD** pattern. The short version
lives in [`SHAREABLE-CAD.md`](SHAREABLE-CAD.md); the long version
lives in the sibling `pycon2026` repo.
