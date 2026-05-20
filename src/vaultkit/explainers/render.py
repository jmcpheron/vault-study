"""Render explainer-page artifacts.

Stub. Eventual outputs (to docs/assets/generated/):
  - gear-train-schematic.svg     — ring + 12 satellites + 12 pins, top-down
  - bcd-derivation.svg           — pitch-circle math diagram
  - cylinder-vs-hex.svg          — FDM-variant deviation illustration
  - ratio-table.svg              — module / teeth / ratio table

All numbers come from vaultkit.params; no hard-coded dimensions.
"""

from __future__ import annotations

from pathlib import Path


def render_all(out_dir: Path) -> None:
    """Regenerate every explainer-page diagram into out_dir."""
    raise NotImplementedError("explainers.render.render_all is a stub.")
