"""STEP file inspection.

`inspect(path)` returns a StepReport: the AP242 schema string, the named
PRODUCTs (the assembly + the unique parts beneath it), how many assembly
instances exist, an entity-type histogram from the ASCII representation,
plus an overall bounding box and triangle count from an OCP tessellation
pass.

The histogram and PRODUCT walk are pure-Python ASCII parses — they work
without OCP installed. The bounding box and triangle count require the
[heavy] extras; if OCP isn't importable, those fields come back as None.

The CLI command `vaultkit step inspect <path>` calls `format_report()`
to produce the human-readable summary.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

# ── ASCII parse helpers ──────────────────────────────────────────────────

# Entity declaration: `#NNN = ENTITY_NAME(...)` possibly preceded by whitespace.
_ENTITY_RE = re.compile(r"^#\d+\s*=\s*([A-Z_][A-Z0-9_]*)")

# Product name in PRODUCT(...): first quoted string is the name.
_PRODUCT_RE = re.compile(r"PRODUCT\s*\(\s*'([^']+)'")

# Assembly-instance occurrences (one per parent→child instantiation).
_NAUO_RE = re.compile(r"^#\d+\s*=\s*NEXT_ASSEMBLY_USAGE_OCCURRENCE", re.IGNORECASE)

# FILE_DESCRIPTION first quoted string ≈ AP242 schema line.
# STEP allows `/* comment */` between FILE_DESCRIPTION( and the schema
# string; use [^']* to skip anything-not-a-quote (comments, parens, etc.)
# up to the first quoted token.
_SCHEMA_RE = re.compile(r"FILE_DESCRIPTION\s*\([^']*'([^']+)'", re.DOTALL)

# FILE_NAME first field — the human/Onshape-given document name.
_DOCNAME_RE = re.compile(r"FILE_NAME\s*\(\s*[^']*'([^']*)'", re.DOTALL)


# ── Public data shapes ──────────────────────────────────────────────────


@dataclass(frozen=True)
class Product:
    """A unique named PRODUCT in a STEP assembly.

    `name` is exactly what appears in the STEP file — Onshape's Spur Gear
    FeatureScript labels both internal and external gears as "Spur gear
    (N teeth)", so a 120-tooth ring gear shows up under that name too.
    `instance_count` is how many times this product is referenced from
    NEXT_ASSEMBLY_USAGE_OCCURRENCE rows (i.e. how many copies appear in
    the assembly).
    """

    name: str
    instance_count: int


@dataclass(frozen=True)
class StepReport:
    """Everything `vaultkit step inspect` knows about a STEP file."""

    path: Path
    file_size_bytes: int
    file_lines: int
    schema: str
    document_name: str
    products: list[Product]
    assembly_instances: int
    entity_histogram: list[tuple[str, int]] = field(default_factory=list)
    # OCP-derived fields. None if the [heavy] extras aren't installed.
    bounding_box_mm: tuple[float, float, float] | None = None
    bounding_box_min_mm: tuple[float, float, float] | None = None
    bounding_box_max_mm: tuple[float, float, float] | None = None
    triangle_count: int | None = None
    deflection_mm: float | None = None


# ── ASCII parse ──────────────────────────────────────────────────────────


def _parse_ascii(path: Path) -> StepReport:
    text = path.read_text(errors="replace")
    lines = text.splitlines()

    schema_match = _SCHEMA_RE.search(text)
    schema = schema_match.group(1) if schema_match else "(unknown schema)"

    docname_match = _DOCNAME_RE.search(text)
    document_name = docname_match.group(1) if docname_match else "(unnamed)"

    # Entity histogram + assembly-instance count, single pass over lines.
    entity_counter: Counter[str] = Counter()
    nauo_count = 0
    for line in lines:
        ent_match = _ENTITY_RE.match(line)
        if ent_match:
            entity_counter[ent_match.group(1)] += 1
        if _NAUO_RE.match(line):
            nauo_count += 1

    # Product names + instance counts. Each NEXT_ASSEMBLY_USAGE_OCCURRENCE
    # references its child via product reference; counting unique product
    # *names* is sufficient for the summary (Onshape names every spur gear
    # the same way, so distinct counts collapse to the named-part list).
    product_names = _PRODUCT_RE.findall(text)
    # Distinct preserves first-seen order so the assembly root appears first.
    seen: dict[str, int] = {}
    for name in product_names:
        seen[name] = seen.get(name, 0) + 1
    products = [Product(name=name, instance_count=count) for name, count in seen.items()]

    return StepReport(
        path=path,
        file_size_bytes=path.stat().st_size,
        file_lines=len(lines),
        schema=schema,
        document_name=document_name,
        products=products,
        assembly_instances=nauo_count,
        entity_histogram=entity_counter.most_common(),
    )


# ── OCP tessellation pass (heavy extras) ─────────────────────────────────


def _ocp_bounds_and_tessellation(
    path: Path,
    deflection_mm: float = 0.5,
) -> tuple[
    tuple[float, float, float],
    tuple[float, float, float],
    tuple[float, float, float],
    int,
] | None:
    """Read the STEP via OCP and return (extents, min, max, triangle_count).

    Returns None if OCP can't be imported (heavy extras not installed) or
    if reading the file fails.
    """
    try:
        from OCP.Bnd import Bnd_Box
        from OCP.BRep import BRep_Tool
        from OCP.BRepBndLib import BRepBndLib
        from OCP.BRepMesh import BRepMesh_IncrementalMesh
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.STEPControl import STEPControl_Reader
        from OCP.TopAbs import TopAbs_FACE
        from OCP.TopExp import TopExp_Explorer
        from OCP.TopLoc import TopLoc_Location
        from OCP.TopoDS import TopoDS
    except ImportError:
        return None

    reader = STEPControl_Reader()
    status = reader.ReadFile(str(path))
    if status != IFSelect_RetDone:
        return None
    reader.TransferRoots()
    shape = reader.OneShape()

    box = Bnd_Box()
    BRepBndLib.Add_s(shape, box)
    xmin, ymin, zmin, xmax, ymax, zmax = box.Get()
    extents = (xmax - xmin, ymax - ymin, zmax - zmin)
    bbmin = (xmin, ymin, zmin)
    bbmax = (xmax, ymax, zmax)

    # Tessellate and count triangles.
    BRepMesh_IncrementalMesh(shape, deflection_mm, False, 0.5, True)
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    triangle_count = 0
    location = TopLoc_Location()
    while explorer.More():
        face = TopoDS.Face_s(explorer.Current())
        triangulation = BRep_Tool.Triangulation_s(face, location)
        if triangulation is not None:
            triangle_count += triangulation.NbTriangles()
        explorer.Next()

    return extents, bbmin, bbmax, triangle_count


# ── Public entry point ──────────────────────────────────────────────────


def inspect(path: Path, *, deflection_mm: float = 0.5) -> StepReport:
    """Inspect a STEP file. Returns a StepReport with both ASCII-parsed
    metadata and (if OCP is available) bounding box + triangle count.
    """
    if not path.exists():
        raise FileNotFoundError(path)

    report = _parse_ascii(path)
    ocp_result = _ocp_bounds_and_tessellation(path, deflection_mm=deflection_mm)
    if ocp_result is not None:
        extents, bbmin, bbmax, triangle_count = ocp_result
        # Replace the report with one that has the OCP-derived fields.
        # Dataclass is frozen; build a new instance.
        report = StepReport(
            **{**report.__dict__,
               "bounding_box_mm": extents,
               "bounding_box_min_mm": bbmin,
               "bounding_box_max_mm": bbmax,
               "triangle_count": triangle_count,
               "deflection_mm": deflection_mm,
               }
        )
    return report


# ── Human-readable formatter ─────────────────────────────────────────────


def format_report(report: StepReport, *, histogram_rows: int = 5) -> str:
    """Render a StepReport as the multi-line summary `vaultkit step inspect` prints."""
    lines: list[str] = []
    lines.append(f"{report.schema} — {report.path}")
    lines.append(f"Document name: {report.document_name}")

    lines.append(
        f"Products ({len(report.products)} unique, "
        f"{report.assembly_instances} assembly instances):"
    )
    for product in report.products:
        suffix = f"  ×{product.instance_count}" if product.instance_count > 1 else ""
        lines.append(f"  {product.name}{suffix}")

    if report.bounding_box_mm is not None:
        x, y, z = report.bounding_box_mm
        lines.append(f"Bounding box (mm): {x:.2f} × {y:.2f} × {z:.2f}")
    else:
        lines.append("Bounding box: (OCP not installed — install [heavy] extras)")

    if report.triangle_count is not None:
        lines.append(
            f"Tessellation: {report.triangle_count:,} triangles "
            f"@ {report.deflection_mm} mm deflection"
        )

    lines.append(f"Entity histogram (top {histogram_rows}):")
    for name, count in report.entity_histogram[:histogram_rows]:
        lines.append(f"  {name:<24} {count:>6,}")

    lines.append(
        f"File size: {report.file_size_bytes:,} bytes  /  {report.file_lines:,} lines"
    )
    return "\n".join(lines)
