"""STEP file I/O — inspect, tessellate, decompose.

Stub. The intended API:

    def inspect(path: Path) -> StepReport
    def tessellate(path: Path, *, deflection: float = 0.1) -> trimesh.Trimesh
    def split_assembly(path: Path) -> Iterable[NamedPart]

Heavy dependency: cadquery-ocp (via the [heavy] extra). Until implemented,
all functions raise NotImplementedError. See the plan file for sequencing.
"""

from __future__ import annotations

from pathlib import Path


def inspect(path: Path) -> None:
    """Parse a STEP file and return a structured report.

    Will produce: AP242 schema version, assembly tree (named parts),
    bounding box, tessellation stats. Mirrors `cardlab inspect` from
    the sibling pycon2026 repo.
    """
    raise NotImplementedError(
        "step_io.inspect is a stub. Implement with cadquery-ocp once the "
        "[heavy] extras are part of the dev loop."
    )
