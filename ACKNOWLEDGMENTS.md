# Acknowledgments

## Adam Savage's vault-door build series

This repository exists because **Adam Savage** built a 1/12-scale
mechanical bank-vault door on camera, on the
[Tested YouTube channel](https://www.tested.com/), and showed every
gear ratio, every dimension, every machining decision. The mechanism
design, the proportions, the 12-pin layout, the 120 / 24 gear math
— that's all Adam's work. This repo is an independent CAD
reinterpretation and FDM-friendly redesign for educational and hobby
purposes, with sources tracked back to the original videos in
[`specs.md`](specs.md) and [`docs/sources.md`](docs/sources.md).

If you found this repo and you haven't watched Adam's series, go do
that first. The videos are the original work; everything here is
commentary.

## Third-party tools

- **[Onshape](https://www.onshape.com/)** — cloud parametric CAD;
  source of truth for the geometry. Free hobbyist tier with public
  documents.
- **[OpenSCAD](https://openscad.org/)** — used by `vaultkit` for
  orthographic renders and the FDM-variant sandbox.
- **[build123d](https://github.com/gumyr/build123d)** /
  **[CadQuery](https://github.com/CadQuery/cadquery)** — Python CAD
  libraries used by the `vaultkit[heavy]` extras for mesh
  operations and render generation.
- **[trimesh](https://github.com/mikedh/trimesh)** — STL/3MF reading
  and mesh manipulation.
- **[drawsvg](https://github.com/cduck/drawsvg)** — SVG diagrams in
  the explainer pages.

## Pattern reference

The repo layout follows the "Shareable CAD" pattern developed in
the sibling `pycon2026` repo — see [`SHAREABLE-CAD.md`](SHAREABLE-CAD.md).
