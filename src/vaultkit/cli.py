"""vaultkit CLI."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from vaultkit import gears, mesh, params, step_io


@click.group()
@click.version_option()
def main() -> None:
    """Vault Study toolkit — gear math, STEP processing, explainer-page generation."""


# ── gears ────────────────────────────────────────────────────────────────


@main.group()
def gears_group() -> None:
    """Gear math derived from src/vaultkit/params.py."""


main.add_command(gears_group, name="gears")


@gears_group.command("info")
def gears_info() -> None:
    """Print the gear-math summary (module, tooth counts, ratio, BCD)."""
    ring = gears.Gear(teeth=params.RING_TEETH, module_mm=params.MODULE_MM)
    spur = gears.Gear(teeth=params.SPUR_TEETH, module_mm=params.MODULE_MM)
    drive_ratio = gears.ratio(driver=ring, driven=spur)
    center_distance = gears.internal_mesh_center_distance_mm(ring=ring, spur=spur)
    teeth_between = gears.teeth_between_satellites(
        ring_teeth=params.RING_TEETH, satellite_count=params.SPUR_COUNT
    )

    click.echo(f"Module:                    {params.MODULE_MM} mm")
    click.echo(f"Ring gear:                 {params.RING_TEETH} teeth")
    click.echo(f"  pitch diameter:          {ring.pitch_diameter_mm} mm")
    click.echo(f"Spur gear ({params.SPUR_COUNT}×):              {params.SPUR_TEETH} teeth")
    click.echo(f"  pitch diameter:          {spur.pitch_diameter_mm} mm")
    click.echo(f"Drive ratio (ring:spur):   {drive_ratio:g} : 1")
    click.echo(f"Center distance (axis):    {center_distance} mm")
    click.echo(f"Measured BCD (specs.md):   {params.SPUR_BCD_MM} mm")
    click.echo(f"  → 2 × center distance =  {2 * center_distance} mm (should match BCD)")
    click.echo(f"Teeth between satellites:  {teeth_between}")


# ── step (stub) ──────────────────────────────────────────────────────────


@main.group()
def step() -> None:
    """STEP file inspection and tessellation."""


@step.command("inspect")
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--deflection",
    type=float,
    default=0.5,
    show_default=True,
    help="Tessellation deflection in mm (smaller = more triangles, slower).",
)
def step_inspect(path: Path, deflection: float) -> None:
    """Print AP242 schema, assembly tree, bounding box, tessellation stats."""
    report = step_io.inspect(path, deflection_mm=deflection)
    click.echo(step_io.format_report(report))


@step.command("render")
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--out",
    "out_png",
    type=click.Path(path_type=Path),
    required=True,
    help="Output PNG path.",
)
@click.option(
    "--deflection",
    type=float,
    default=0.3,
    show_default=True,
    help="Tessellation deflection in mm (smaller = smoother render, slower).",
)
@click.option(
    "--size",
    type=int,
    default=1200,
    show_default=True,
    help="Output image edge length in pixels (square).",
)
def step_render(path: Path, out_png: Path, deflection: float, size: int) -> None:
    """Render a STEP file as an isometric PNG (hero/comparison image)."""
    click.echo(f"Rendering {path} → {out_png} (deflection {deflection} mm)…", err=True)
    mesh.render_iso(path, out_png, deflection_mm=deflection, size_px=(size, size))
    click.echo(f"Wrote {out_png}", err=True)


# ── bom (stub) ───────────────────────────────────────────────────────────


@main.command("bom")
@click.argument("path", type=click.Path(exists=True, path_type=Path))
def bom(path: Path) -> None:
    """Extract a bill of materials from a STEP file. (Not yet implemented.)"""
    click.echo(f"vaultkit bom {path}: not yet implemented.", err=True)
    sys.exit(2)


# ── explain (stub) ───────────────────────────────────────────────────────


@main.group()
def explain() -> None:
    """Generate diagrams and explainer-page artifacts. (Not yet implemented.)"""


@explain.command("render")
def explain_render() -> None:
    """Render the SVG diagrams used by docs/."""
    click.echo("vaultkit explain render: not yet implemented.", err=True)
    sys.exit(2)


if __name__ == "__main__":
    main()
