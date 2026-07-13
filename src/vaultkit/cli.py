"""vaultkit CLI."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from vaultkit import gears, mesh, params, parts, play, release, scad, step_io
from vaultkit.explainers import schematic


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


# ── play ─────────────────────────────────────────────────────────────────


@main.command("play")
@click.option(
    "--throw",
    "throw_deg",
    type=float,
    default=play.DEFAULT_THROW_DEG,
    show_default=True,
    help="Ring-gear throw in degrees for the extended-pin rows.",
)
def play_info(throw_deg: float) -> None:
    """Print the pin-play tolerance stack-up, faithful vs FDM."""
    faithful = play.stackup("faithful", throw_deg=throw_deg)
    fdm = play.stackup("fdm", throw_deg=throw_deg)
    guided_ext = params.PIN_LENGTH_MM - fdm.extension_mm

    click.echo(
        f"Pin-play stack-up at a {throw_deg:g}° ring throw "
        f"(extension {fdm.extension_mm:.2f} mm)"
    )
    click.echo("")
    header = f"{'':38}{'faithful':>12}{'FDM':>12}"
    click.echo(header)
    rows = [
        ("Bore diameter (mm)",
         f"{faithful.fit.bore_diameter_mm:.3f}", f"{fdm.fit.bore_diameter_mm:.3f}"),
        ("Diametral clearance (mm)",
         f"{faithful.fit.diametral_clearance_mm:.3f}",
         f"{fdm.fit.diametral_clearance_mm:.3f}"),
        ("Radial clearance (mm)",
         f"{faithful.fit.radial_clearance_mm:.3f}",
         f"{fdm.fit.radial_clearance_mm:.3f}"),
        (f"Tilt at rest, {params.PIN_LENGTH_MM} mm guided (deg)",
         f"{faithful.tilt_at_rest_deg:.3f}", f"{fdm.tilt_at_rest_deg:.3f}"),
        (f"Tilt extended, {guided_ext:.1f} mm guided (deg)",
         f"{faithful.tilt_extended_deg:.3f}", f"{fdm.tilt_extended_deg:.3f}"),
        ("Lateral play at pin tip (mm)",
         f"{faithful.lateral_play_at_tip_mm:.3f}",
         f"{fdm.lateral_play_at_tip_mm:.3f}"),
        ("Locked-door play (mm)",
         f"{faithful.locked_door_play_mm:.3f}", f"{fdm.locked_door_play_mm:.3f}"),
        ("Door-frame gap (mm)",
         f"{faithful.frame_gap_mm:.3f}", f"{fdm.frame_gap_mm:.3f}"),
    ]
    for label, a, b in rows:
        click.echo(f"{label:38}{a:>12}{b:>12}")
    click.echo("")
    click.echo("Faithful bore is a machined slip fit; modeled as zero clearance.")
    click.echo(
        f"FDM bore is the planned {params.FDM_PIN_BORE_MM} mm from "
        f"cad/fdm/deviations.md — TBD until print-tuned."
    )
    click.echo(
        "Gear backlash is unquantified; it adds a 1:1 travel dead-band "
        "(see vaultkit.play.travel_deadband_mm)."
    )


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


@step.command("extract")
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--out-dir",
    type=click.Path(path_type=Path),
    required=True,
    help="Directory to write per-part PNGs into.",
)
@click.option(
    "--deflection",
    type=float,
    default=0.3,
    show_default=True,
    help="Tessellation deflection in mm.",
)
@click.option(
    "--size",
    type=int,
    default=800,
    show_default=True,
    help="Per-part PNG edge length in pixels (square).",
)
def step_extract(path: Path, out_dir: Path, deflection: float, size: int) -> None:
    """Render one PNG per unique named PRODUCT in a STEP assembly."""
    out_dir.mkdir(parents=True, exist_ok=True)
    click.echo(f"Extracting parts from {path} → {out_dir}/", err=True)
    n_rendered = 0
    for named in parts.iter_named_shapes(path):
        slug = parts.slugify(named.name)
        out_png = out_dir / f"{slug}-{named.index}.iso.png"
        click.echo(
            f"  [{named.index}] {named.name!r:<30} ×{named.instance_count:<3} → {out_png.name}",
            err=True,
        )
        mesh.render_iso_shape(
            named.shape, out_png, deflection_mm=deflection, size_px=(size, size)
        )
        n_rendered += 1
    click.echo(f"Wrote {n_rendered} part PNG(s) to {out_dir}/", err=True)


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
    """Generate diagrams and explainer-page artifacts."""


@explain.command("schematic")
@click.option(
    "--kind",
    type=click.Choice(["mesh", "mechanism", "pin-play"]),
    required=True,
    help="Which schematic to generate.",
)
@click.option("--animated/--no-animated", default=False, show_default=True)
@click.option(
    "--out",
    "out_svg",
    type=click.Path(path_type=Path),
    required=True,
    help="Output SVG path.",
)
def explain_schematic(kind: str, animated: bool, out_svg: Path) -> None:
    """Generate a single SVG schematic."""
    if kind == "mesh":
        schematic.gear_mesh_svg(out_svg, animated=animated)
    elif kind == "pin-play":
        schematic.pin_play_diagram_svg(out_svg)
    else:
        schematic.full_mechanism_svg(out_svg, animated=animated)
    click.echo(f"Wrote {out_svg}", err=True)


@explain.command("animate")
@click.option(
    "--kind",
    type=click.Choice(["cam-sweep", "exploded"]),
    required=True,
    help="Which animation to render.",
)
@click.option(
    "--variant",
    type=click.Choice(["fdm", "faithful"]),
    default="fdm",
    show_default=True,
)
@click.option(
    "--out",
    "out_gif",
    type=click.Path(path_type=Path),
    required=True,
    help="Output GIF path. WebP twin written alongside (same stem, .webp).",
)
@click.option("--frames", type=int, default=24, show_default=True)
@click.option("--size", type=int, default=600, show_default=True,
              help="Output GIF edge length in pixels.")
def explain_animate(
    kind: str, variant: str, out_gif: Path, frames: int, size: int
) -> None:
    """Render a 3D animation GIF via OpenSCAD."""
    step_file = params.VARIANTS[variant]
    out_webp = out_gif.with_suffix(".webp")
    click.echo(f"Rendering {kind} animation for {variant} → {out_gif.name}…", err=True)
    if kind == "cam-sweep":
        scad.render_cam_sweep(
            Path(step_file), out_gif, out_webp=out_webp,
            frames=frames, size_px=size,
        )
    else:
        scad.render_exploded(
            Path(step_file), out_gif, out_webp=out_webp,
            frames=frames, size_px=size,
        )
    click.echo(f"Wrote {out_gif} ({out_gif.stat().st_size:,} bytes)", err=True)
    click.echo(f"Wrote {out_webp} ({out_webp.stat().st_size:,} bytes)", err=True)


@explain.command("render")
@click.option(
    "--out-dir",
    type=click.Path(path_type=Path),
    default=Path("docs/assets/generated"),
    show_default=True,
    help="Root directory for generated artifacts.",
)
@click.option(
    "--includes-dir",
    type=click.Path(path_type=Path),
    default=Path("docs/_includes"),
    show_default=True,
    help="Jekyll _includes directory for inline-embeddable SVGs.",
)
@click.option(
    "--skip-parts",
    is_flag=True,
    help="Skip the per-part PNG renders (slow). Use for SVG-only iterations.",
)
@click.option(
    "--skip-gifs",
    is_flag=True,
    help="Skip the OpenSCAD-driven 3D animation GIFs. Use for SVG-only iterations.",
)
def explain_render(
    out_dir: Path, includes_dir: Path, skip_parts: bool, skip_gifs: bool
) -> None:
    """Regenerate every explainer-page artifact in one call.

    Writes to docs/assets/generated/ and docs/_includes/. Safe to re-run;
    output is deterministic.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    includes_dir.mkdir(parents=True, exist_ok=True)

    click.echo("→ animated gear-mesh hero", err=True)
    schematic.gear_mesh_svg(out_dir / "gear-mesh.animated.svg", animated=True)

    click.echo("→ animated full-mechanism hero", err=True)
    schematic.full_mechanism_svg(out_dir / "mechanism.animated.svg", animated=True)

    click.echo("→ interactive mechanism (Jekyll include)", err=True)
    schematic.full_mechanism_interactive(includes_dir / "mechanism-interactive.svg")

    click.echo("→ technical top view", err=True)
    schematic.technical_top_view_svg(out_dir / "technical-top-view.svg")

    click.echo("→ rack-pinion close-up (static + interactive)", err=True)
    schematic.rack_pinion_closeup_svg(out_dir / "rack-pinion-closeup.svg")
    schematic.rack_pinion_closeup_svg(
        includes_dir / "pin-travel-closeup.svg", interactive=True,
    )

    click.echo("→ pin-travel diagram", err=True)
    schematic.pin_travel_diagram_svg(out_dir / "pin-travel-diagram.svg")

    click.echo("→ pin-play diagram", err=True)
    schematic.pin_play_diagram_svg(out_dir / "pin-play-diagram.svg")

    # Whole-assembly iso renders. Output stems keep their historical names
    # ("fdm-vault"); the STEP paths come from params.VARIANTS.
    for label, variant in [("faithful", "faithful"), ("fdm-vault", "fdm")]:
        step_file = params.VARIANTS[variant]
        out_png = out_dir / f"{label}.iso.png"
        click.echo(f"→ {label} iso hero ({out_png.name})", err=True)
        mesh.render_iso(
            Path(step_file), out_png, deflection_mm=0.2,
            edge_width=0.08, edge_color="#888a8c", face_color="#e1e3e6",
        )

    if not skip_parts:
        # Per-part PNGs for both variants.
        for variant, step_file in params.VARIANTS.items():
            parts_dir = out_dir / "parts" / variant
            parts_dir.mkdir(parents=True, exist_ok=True)
            click.echo(f"→ {variant} per-part renders → {parts_dir}/", err=True)
            for named in parts.iter_named_shapes(Path(step_file)):
                slug = parts.slugify(named.name)
                out_png = parts_dir / f"{slug}-{named.index}.iso.png"
                click.echo(
                    f"    [{named.index}] {named.name!r} ×{named.instance_count} → {out_png.name}",
                    err=True,
                )
                mesh.render_iso_shape(
                    named.shape, out_png, deflection_mm=0.3, size_px=(600, 600)
                )

    if not skip_gifs:
        # OpenSCAD 3D animations — currently FDM only (faithful variant
        # is less developed; revisit when its STEP gets racks + pins).
        for kind, render_fn in [
            ("cam-sweep", scad.render_cam_sweep),
            ("exploded", scad.render_exploded),
        ]:
            out_gif = out_dir / f"mechanism-{kind}-fdm.gif"
            out_webp = out_gif.with_suffix(".webp")
            click.echo(f"→ {kind} animation → {out_gif.name}", err=True)
            render_fn(
                Path(params.VARIANTS["fdm"]),
                out_gif, out_webp=out_webp,
                frames=24, size_px=600,
            )

    click.echo("Done.", err=True)


# ── release ──────────────────────────────────────────────────────────────


@main.group()
def release_group() -> None:
    """Build upload-ready bundles for Printables / MakerWorld."""


main.add_command(release_group, name="release")


@release_group.command("describe")
@click.option(
    "--variant",
    type=click.Choice(["fdm", "faithful"]),
    required=True,
    help="Which variant to describe.",
)
@click.option(
    "--platform",
    type=click.Choice(["printables", "makerworld"]),
    required=True,
    help="Which platform's formatting to emit.",
)
def release_describe(variant: str, platform: str) -> None:
    """Print a listing description (copy-paste into the site form)."""
    click.echo(release.describe(variant, platform))


@release_group.command("build")
@click.option(
    "--variant",
    type=click.Choice(["fdm", "faithful", "all"]),
    default="all",
    show_default=True,
    help="Which variant(s) to bundle.",
)
@click.option(
    "--out-dir",
    type=click.Path(path_type=Path),
    default=Path("dist"),
    show_default=True,
    help="Root directory for the bundle(s).",
)
@click.option("--skip-stl", is_flag=True, help="Skip the whole-assembly STL.")
@click.option("--skip-parts", is_flag=True, help="Skip the per-part STLs.")
@click.option(
    "--skip-anim", is_flag=True, help="Skip the OpenSCAD animation (FDM only)."
)
@click.option("--zip/--no-zip", "make_zip", default=True, show_default=True)
@click.option(
    "--deflection",
    type=float,
    default=0.3,
    show_default=True,
    help="Tessellation deflection in mm for the STLs/renders.",
)
def release_build(
    variant: str,
    out_dir: Path,
    skip_stl: bool,
    skip_parts: bool,
    skip_anim: bool,
    make_zip: bool,
    deflection: float,
) -> None:
    """Build the full bundle(s): STLs, renders, descriptions, license, zip."""
    targets = ["fdm", "faithful"] if variant == "all" else [variant]
    for v in targets:
        dest = release.build_bundle(
            v,
            out_dir,
            skip_stl=skip_stl,
            skip_parts=skip_parts,
            skip_anim=skip_anim,
            make_zip=make_zip,
            deflection=deflection,
        )
        click.echo(f"Built {v} bundle → {dest}", err=True)


if __name__ == "__main__":
    main()
