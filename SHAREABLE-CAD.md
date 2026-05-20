# Shareable CAD — pattern reference

This repository follows the **Shareable CAD** pipeline pattern:

```
   Onshape doc          ← source of truth (parametric CAD in the cloud)
       │ STEP export, committed to the repo
       ▼
   GitHub repo          ← Python tooling, parameters, history, issues
       │ auto-built artifacts (STL / GLB / GIF / SVG / explainer pages)
       ▼
   MakerWorld + Printables   ← consumer-facing sharing endpoints
                              (3MF bundle + slicer profile + photos)
```

The pattern was first developed in the sibling `pycon2026` repo
across three projects (a PyCon gear card, a spiral-spring cat toy,
and the early stages of this vault study). It's flattened here for a
single-project repo.

The core ideas, applied here:

1. **Parametric.** Every dimension lives in
   [`src/vaultkit/params.py`](src/vaultkit/params.py) — one Python
   module, mirrored into the Onshape variable sheet by hand.
2. **Code-trackable.** A parameter change is a one-line git diff
   with a date and a commit message. Not a screenshot of an Onshape
   revision label.
3. **Derivable.** Every artifact a reader might want — explainer
   page, hero render, exploded GIF, BOM — is *built* by
   [`vaultkit`](src/vaultkit/) from `params.py` plus the STEP file.
4. **Printable.** The end state is a 3MF bundle on MakerWorld and
   Printables that anyone can print at home without reading any of
   this.

The full pattern doc lives in the `pycon2026` repo. This file is a
pointer; if `pycon2026/SHAREABLE-CAD.md` updates with new
conventions, port them back here.

Companion files in *this* repo:

- [`README.md`](README.md) — front-door story.
- [`specs.md`](specs.md) — canonical dimensions; source of truth for
  numbers that appear in prose and code alike.
- [`cad/faithful/`](cad/faithful/) and [`cad/fdm/`](cad/fdm/) — the
  two parallel CAD variants.
- [`src/vaultkit/`](src/vaultkit/) — the Python kernel.
- [`docs/`](docs/) — GitHub Pages explainer site.
