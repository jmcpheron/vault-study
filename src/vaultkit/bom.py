"""Bill of materials extraction.

Stub. Reads a tessellated STEP assembly and produces a per-part CSV
(name, count, bounding-box volume, material if encoded). Pairs with
step_io.split_assembly.
"""

from __future__ import annotations

from pathlib import Path


def extract(step_path: Path) -> None:
    """Walk an assembly and produce a BOM row per unique part."""
    raise NotImplementedError("bom.extract is a stub.")
