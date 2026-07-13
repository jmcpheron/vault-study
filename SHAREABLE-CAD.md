# Shareable CAD — pattern reference

This is the supporting pattern doc for the tooling. The project's
front door is the Onshape model and the
[build blog](https://jmcpheron.github.io/vault-study/); this file
explains the pipeline that keeps them honest.

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

## Re-exporting from Onshape (the version loop)

The git ↔ Onshape link is deliberate. When the model reaches a
milestone worth freezing:

1. **Cut a named Version in Onshape** (the version graph → *Create
   version*, e.g. `v0.1 — first public export`). A Version is
   immutable; a workspace keeps moving.
2. **Export STEP from that Version** and drop it in
   [`step-source/`](step-source/), replacing the existing file.
3. **Bump the provenance** in
   [`src/vaultkit/params.py`](src/vaultkit/params.py) →
   `ONSHAPE[variant]`: set `version_id`, `version_name`, and
   `exported_utc`. `OnshapeSource.permalink` then resolves to the
   immutable `/v/<versionId>` URL the release descriptions link to.
4. **Commit the STEP and the params bump together.** Now `git log` of
   `params.py` and the Onshape version graph tell the same story:
   which commit's files came from which Onshape Version.

Until a Version is cut, `version_id` stays `None` and everything
points at the live `/w/` workspace URL — fine for an early public
doc, just not a frozen snapshot.

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
