"""OpenSCAD-driven 3D animations: cam-sweep + exploded-view GIFs.

Why OpenSCAD instead of matplotlib? matplotlib's Poly3DCollection has
no proper z-sorting against itself for non-convex meshes (the existing
iso PNGs show the artifacts), no lighting, and rendering 18+ frames
takes forever. OpenSCAD's CGAL backend produces clean orthographic
renders with real shading in seconds per frame.

Pipeline:
    parts.iter_named_shapes(step_path)
      → mesh.shape_to_stl into /tmp/vaultkit-cache/stl/<hash>.stl
      → assemble per-part imports into a single .scad template using
        OpenSCAD's `$t` animation parameter
      → subprocess: `openscad --animate N --imgsize W,W --render
        --colorscheme=Cornfield --camera=... template.scad`
      → walk the resulting frame00000.png … frame{N-1}.png in the
        tempdir, downsample to size/2 with PIL LANCZOS (cheap AA),
        palette-quantize, and stitch into GIF + WebP.

The .scad templates are generated from a Python format string driven
by params.py + gears.py — no hard-coded dimensions.

Coordinate convention: STEP files are Y-up (we confirmed earlier from
bounding boxes); OpenSCAD is Z-up. Every imported STL is wrapped in a
`rotate([90,0,0])` once at the top of the template so .scad source
reads correctly to anyone familiar with OpenSCAD conventions.
"""

from __future__ import annotations

import hashlib
import subprocess
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from vaultkit import gears, mesh, params, parts

OPENSCAD_BIN = "/opt/homebrew/bin/openscad"
CACHE_DIR = Path("/tmp/vaultkit-cache/stl")
OPENSCAD_TIMEOUT_S = 600  # per `--animate` call (entire batch of frames)
DEFAULT_DEFLECTION_MM = 0.15  # tighter than render_iso's 0.3 for OpenSCAD import quality


# ── Part-role mapping ───────────────────────────────────────────────────


@dataclass(frozen=True)
class PartRole:
    """Maps a NamedShape to its role in the mechanism.

    Roles drive the .scad template — `ring` and `hub`/`base` stay put,
    `spur` and `rack`/`pin` get animated transforms. The mapping is
    a small heuristic over the discovery order + instance counts we
    confirmed visually from the extracted per-part PNGs.
    """

    role: str  # one of: ring, spur, rack, pin, hub, base
    stl_path: Path


def assign_roles(named_shapes: Iterable[parts.NamedShape]) -> list[PartRole]:
    """Map NamedShapes to mechanism roles.

    Rules (FDM variant, from confirmed visual inspection):
      Spur gear (120 teeth)   → ring
      Spur gear (24 teeth)    → spur
      Part 1 #0 (×12)         → rack
      Part 1 #1 (×12)         → pin
      Part 1 #4 (×1)          → hub
      Part 1 #5 (×1)          → base
    """
    roles: list[PartRole] = []
    part_1_singletons_seen = 0
    part_1_dozens_seen = 0
    for ns in named_shapes:
        stl = _cached_stl(ns)
        if "120 teeth" in ns.name:
            role = "ring"
        elif "24 teeth" in ns.name:
            role = "spur"
        elif ns.name == "Part 1":
            if ns.instance_count == 12:
                role = "rack" if part_1_dozens_seen == 0 else "pin"
                part_1_dozens_seen += 1
            else:
                role = "hub" if part_1_singletons_seen == 0 else "base"
                part_1_singletons_seen += 1
        else:
            role = "unknown"
        roles.append(PartRole(role=role, stl_path=stl))
    return roles


# ── STL cache ───────────────────────────────────────────────────────────


def _cached_stl(ns: parts.NamedShape, *, deflection_mm: float = DEFAULT_DEFLECTION_MM) -> Path:
    """Write the NamedShape's geometry to /tmp/vaultkit-cache/stl/<hash>.stl.

    Cache key hashes the part name + index + deflection. Two runs over
    the same STEP file reuse the cached STLs; CI starts from empty cache.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = f"{ns.name}|{ns.index}|{deflection_mm}".encode()
    digest = hashlib.sha256(key).hexdigest()[:16]
    out = CACHE_DIR / f"{digest}.stl"
    if not out.exists():
        mesh.shape_to_stl(ns.shape, out, deflection_mm=deflection_mm)
    return out


# ── Template generation ─────────────────────────────────────────────────


def _scad_header() -> str:
    """Common preamble: $fn, per-role orientation correctors, palette.

    Different parts come out of Onshape's STEP export with different
    local-frame conventions. We don't apply assembly transforms (those
    live in the STEP's NEXT_ASSEMBLY_USAGE_OCCURRENCE entries — we'd
    need a different XCAF walk to use them); instead we hand-correct
    per role based on each STL's bbox principal axis:

    - ring / spur / hub: rotation axis along local +Y → rotate Y→Z so
      the part sits flat on the door.
    - base: posts already along local +Z; no rotation needed.
    - pin: long axis along local +Z → rotate so it extends radially
      outward (local +X in the assembly frame).
    - rack: long axis already along local +X (radial); no rotation
      needed.
    """
    return (
        "// Generated by vaultkit.scad — do not hand-edit.\n"
        "$fn = 64;\n\n"
        "// Per-role orientation correctors. See _scad_header docstring\n"
        "// for the reasoning behind each rotation.\n"
        "module orient_y_up()  { rotate([90, 0, 0]) children(); }  // ring/spur/hub\n"
        "module orient_z_up()  { children(); }                     // base (no-op)\n"
        "module orient_pin()   { rotate([0, 90, 0]) children(); }  // long axis Z→X\n"
        "module orient_rack()  { children(); }                     // already X-radial\n\n"
        "// Material-inspired palette.\n"
        "RING_COLOR  = \"Goldenrod\";    // brass\n"
        "SPUR_COLOR  = \"Silver\";       // steel\n"
        "RACK_COLOR  = \"Burlywood\";    // brass-tan\n"
        "PIN_COLOR   = \"DimGray\";      // dark steel\n"
        "HUB_COLOR   = \"WhiteSmoke\";   // clear acrylic\n"
        "BASE_COLOR  = \"Gainsboro\";    // platform plate\n\n"
    )


def cam_sweep_template(
    roles: list[PartRole],
    *,
    ring_oscillation_deg: float = 12.0,
) -> str:
    """Render the .scad template for the cam-sweep animation.

    $t ∈ [0, 1) is the animation parameter. The ring oscillates back and
    forth via sin(360*$t); spurs counter-rotate at the 5:1 ratio; racks
    and pins translate radially by the rack-and-pinion identity.
    """
    ring_g = gears.Gear(teeth=params.RING_TEETH, module_mm=params.MODULE_MM)
    spur_g = gears.Gear(teeth=params.SPUR_TEETH, module_mm=params.MODULE_MM)
    ratio_val = gears.ratio(driver=ring_g, driven=spur_g)
    bcd_r = params.SPUR_BCD_MM / 2  # 36 mm — measured BCD for visual layout

    # Z stacking: the base's axle posts stick up ~13 mm; lift the spurs
    # to sit on top so they don't interpenetrate the posts. The ring
    # sits a bit above the base too.
    spur_z_lift = 13.0  # base post height
    ring_z_lift = 5.0

    # Rack length (from STL bbox) — needed to position the pin at the
    # rack's far end so they don't overlap.
    rack_length_mm = 26.0  # bbox extent X of the rack STL

    by_role: dict[str, list[Path]] = {}
    for r in roles:
        by_role.setdefault(r.role, []).append(r.stl_path)

    lines: list[str] = [_scad_header()]
    lines.append(f"theta = {ring_oscillation_deg} * sin(360 * $t);  // ring angle (deg)")
    lines.append(f"spur_angle = -{ratio_val} * theta;               // 5:1 counter-rotation")
    lines.append(
        f"rack_dr = (theta * PI / 180) * {spur_g.pitch_radius_mm};  "
        "// rack-and-pinion Δr = θ·r"
    )
    lines.append("")

    # Hub — stationary; sits at the bottom of the stack.
    for stl in by_role.get("hub", []):
        lines.append("// hub (acrylic body)")
        lines.append(f'color(HUB_COLOR) orient_y_up() import("{stl}");')
    lines.append("")

    # Base — stationary; axle posts sit on top of the hub.
    for stl in by_role.get("base", []):
        lines.append("// base (axle-post ring)")
        lines.append(f'color(BASE_COLOR) orient_z_up() import("{stl}");')
    lines.append("")

    # Ring — single instance, oscillates about Z, sits above the base.
    for stl in by_role.get("ring", []):
        lines.append("// ring gear — oscillates about Z")
        lines.append(f"translate([0, 0, {ring_z_lift}])")
        lines.append("    rotate([0, 0, theta])")
        lines.append(f'        color(RING_COLOR) orient_y_up() import("{stl}");')
    lines.append("")

    # 12 spurs — each at angle phi_i, counter-rotating about its own Z,
    # lifted to sit on the base posts.
    spur_stls = by_role.get("spur", [])
    if spur_stls:
        spur_stl = spur_stls[0]
        lines.append(f"// 12 spurs at {bcd_r} mm radius, 30° apart, counter-rotating")
        lines.append("for (i = [0 : 11]) {")
        lines.append("    phi = i * 30;")
        lines.append(
            f"    translate([{bcd_r} * cos(phi), {bcd_r} * sin(phi), {spur_z_lift}])"
        )
        lines.append("        rotate([0, 0, spur_angle])")
        lines.append(f'            color(SPUR_COLOR) orient_y_up() import("{spur_stl}");')
        lines.append("}")
        lines.append("")

    # 12 rack + pin pairs — each at angle phi_i, translating radially outward
    # together. Rack starts at the BCD; pin sits at the rack's far end.
    rack_stls = by_role.get("rack", [])
    pin_stls = by_role.get("pin", [])
    if rack_stls or pin_stls:
        lines.append(f"// 12 rack/pin pairs at {bcd_r} mm radius, translating radially")
        lines.append("for (i = [0 : 11]) {")
        lines.append("    phi = i * 30;")
        lines.append("    rotate([0, 0, phi])")
        lines.append(f"        translate([{bcd_r} + rack_dr, 0, {spur_z_lift / 2}])")
        lines.append("    {")
        if rack_stls:
            lines.append(f'        color(RACK_COLOR) orient_rack() import("{rack_stls[0]}");')
        if pin_stls:
            lines.append(f"        translate([{rack_length_mm}, 0, 0])")
            lines.append(f'            color(PIN_COLOR) orient_pin() import("{pin_stls[0]}");')
        lines.append("    }")
        lines.append("}")

    return "\n".join(lines) + "\n"


def exploded_template(
    roles: list[PartRole],
    *,
    max_offset_mm: float = 40.0,
) -> str:
    """Render the .scad template for the exploded-view animation.

    progress = abs(sin(180*$t)) — a smooth 0 → 1 → 0 envelope over $t∈[0,1).
    Each part translates radially outward from origin by progress * max.
    Hub and base stay put (they're the structural skeleton; nothing
    explodes them).
    """
    bcd_r = params.SPUR_BCD_MM / 2
    spur_z_lift = 13.0
    ring_z_lift = 5.0
    rack_length_mm = 26.0

    by_role: dict[str, list[Path]] = {}
    for r in roles:
        by_role.setdefault(r.role, []).append(r.stl_path)

    lines: list[str] = [_scad_header()]
    lines.append("progress = abs(sin(180 * $t));  // 0 → 1 → 0 over $t ∈ [0,1)")
    lines.append(f"max_offset = {max_offset_mm};")
    lines.append("")

    # Hub — stationary.
    for stl in by_role.get("hub", []):
        lines.append("// hub (acrylic body)")
        lines.append(f'color(HUB_COLOR) orient_y_up() import("{stl}");')
    lines.append("")

    # Base — stationary.
    for stl in by_role.get("base", []):
        lines.append("// base (axle-post ring)")
        lines.append(f'color(BASE_COLOR) orient_z_up() import("{stl}");')
    lines.append("")

    # Ring — lifts along +Z as it explodes.
    for stl in by_role.get("ring", []):
        lines.append("// ring — lifts along +Z")
        lines.append(f"translate([0, 0, {ring_z_lift} + progress * max_offset * 0.5])")
        lines.append(f'    color(RING_COLOR) orient_y_up() import("{stl}");')
    lines.append("")

    # 12 spurs — fan outward radially, lifted to sit on the base posts.
    spur_stls = by_role.get("spur", [])
    if spur_stls:
        lines.append("// 12 spurs — fan outward")
        lines.append("for (i = [0 : 11]) {")
        lines.append("    phi = i * 30;")
        lines.append(
            f"    translate([({bcd_r} + progress * max_offset) * cos(phi),"
            f" ({bcd_r} + progress * max_offset) * sin(phi), {spur_z_lift}])"
        )
        lines.append(f'        color(SPUR_COLOR) orient_y_up() import("{spur_stls[0]}");')
        lines.append("}")
        lines.append("")

    # 12 rack + pin pairs — fan outward, further than the spurs.
    rack_stls = by_role.get("rack", [])
    pin_stls = by_role.get("pin", [])
    if rack_stls or pin_stls:
        lines.append("// 12 rack/pin pairs — fan outward, further than the spurs")
        lines.append("for (i = [0 : 11]) {")
        lines.append("    phi = i * 30;")
        lines.append("    rotate([0, 0, phi])")
        lines.append(
            f"        translate([{bcd_r} + progress * max_offset * 1.5, 0, "
            f"{spur_z_lift / 2}])"
        )
        lines.append("    {")
        if rack_stls:
            lines.append(f'        color(RACK_COLOR) orient_rack() import("{rack_stls[0]}");')
        if pin_stls:
            lines.append(f"        translate([{rack_length_mm}, 0, 0])")
            lines.append(f'            color(PIN_COLOR) orient_pin() import("{pin_stls[0]}");')
        lines.append("    }")
        lines.append("}")

    return "\n".join(lines) + "\n"


# ── OpenSCAD invocation + GIF stitching ─────────────────────────────────


def _run_openscad_animate(
    scad_text: str,
    *,
    frames: int,
    render_size_px: int,
    camera: str,
    colorscheme: str = "Cornfield",
) -> list[Path]:
    """Run `openscad --animate N` and return the list of frame PNGs.

    Uses the OpenCSG preview renderer (no `--render` flag) — ~1500× faster
    than full CGAL and visually indistinguishable for animation purposes.
    Renders to a tempdir which is also the subprocess cwd (OpenSCAD writes
    `frame00000.png` etc. in its cwd by default with --animate).
    """
    tmpdir = Path(tempfile.mkdtemp(prefix="vaultkit-scad-"))
    scad_path = tmpdir / "template.scad"
    scad_path.write_text(scad_text)

    cmd = [
        OPENSCAD_BIN,
        "--animate", str(frames),
        "--imgsize", f"{render_size_px},{render_size_px}",
        "--colorscheme", colorscheme,
        "--camera", camera,
        "-o", "frame.png",  # base name; OpenSCAD appends frame index
        str(scad_path),
    ]
    subprocess.run(
        cmd, cwd=tmpdir, timeout=OPENSCAD_TIMEOUT_S, check=True,
        capture_output=True,
    )

    frame_paths = sorted(tmpdir.glob("frame*.png"))
    if not frame_paths:
        raise RuntimeError(
            f"OpenSCAD --animate produced no frames in {tmpdir} — "
            f"check the .scad source."
        )
    return frame_paths


def _stitch_gif_and_webp(
    frame_paths: list[Path],
    out_gif: Path,
    out_webp: Path | None,
    *,
    target_size_px: int,
    duration_ms: int,
) -> None:
    """Downsample frames to target_size_px and stitch as GIF + optional WebP."""
    from PIL import Image

    frames = []
    for fp in frame_paths:
        img = Image.open(fp).convert("RGB")
        img = img.resize((target_size_px, target_size_px), Image.LANCZOS)
        frames.append(img)

    # GIF (palette-quantized for compactness).
    gif_frames = [f.convert("P", palette=Image.ADAPTIVE, colors=128) for f in frames]
    out_gif.parent.mkdir(parents=True, exist_ok=True)
    gif_frames[0].save(
        out_gif, save_all=True, append_images=gif_frames[1:],
        duration=duration_ms, loop=0, optimize=True, disposal=2,
    )

    # WebP (animated, much smaller than GIF for the same content).
    if out_webp is not None:
        out_webp.parent.mkdir(parents=True, exist_ok=True)
        frames[0].save(
            out_webp, save_all=True, append_images=frames[1:],
            duration=duration_ms, loop=0, quality=85, method=6,
        )


# ── Public entry points ─────────────────────────────────────────────────


_DEFAULT_CAMERA = "0,0,0,45,0,15,260"   # tx,ty,tz, rx,ry,rz, dist — 3/4 iso from above


def render_cam_sweep(
    step_path: Path,
    out_gif: Path,
    *,
    out_webp: Path | None = None,
    frames: int = 24,
    size_px: int = 600,
    period_s: float = 6.0,
    camera: str = _DEFAULT_CAMERA,
) -> None:
    """Render the cam-sweep animation as a GIF (and optional WebP).

    With preview rendering, 24 frames × 600px is fast enough (~5s) that
    we render at the target size directly — no 2× upscale needed.
    """
    roles = assign_roles(parts.iter_named_shapes(step_path))
    scad = cam_sweep_template(roles)
    frame_paths = _run_openscad_animate(
        scad, frames=frames, render_size_px=size_px, camera=camera,
    )
    duration_ms = int(period_s * 1000 / frames)
    _stitch_gif_and_webp(
        frame_paths, out_gif, out_webp,
        target_size_px=size_px, duration_ms=duration_ms,
    )


def render_exploded(
    step_path: Path,
    out_gif: Path,
    *,
    out_webp: Path | None = None,
    frames: int = 24,
    size_px: int = 600,
    period_s: float = 6.0,
    max_offset_mm: float = 40.0,
    camera: str = _DEFAULT_CAMERA,
) -> None:
    """Render the exploded-view animation as a GIF (and optional WebP)."""
    roles = assign_roles(parts.iter_named_shapes(step_path))
    scad = exploded_template(roles, max_offset_mm=max_offset_mm)
    frame_paths = _run_openscad_animate(
        scad, frames=frames, render_size_px=size_px, camera=camera,
    )
    duration_ms = int(period_s * 1000 / frames)
    _stitch_gif_and_webp(
        frame_paths, out_gif, out_webp,
        target_size_px=size_px, duration_ms=duration_ms,
    )


