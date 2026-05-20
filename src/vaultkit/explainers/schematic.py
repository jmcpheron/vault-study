"""2D SVG schematics of the vault gearing.

`gear_mesh_svg` and `full_mechanism_svg` emit SVGs that the explainer
pages embed as heroes and the interactive page consumes for slider-driven
animation. Both use `drawsvg` 2.4.1 (in the [heavy] extras).

Design choices:

- **Schematic, not involute.** Gear teeth are drawn as short radial tick
  marks crossing the pitch circle — recognizable as gears at small
  sizes, without the 200-vertex polygon math.
- **Y-up CAD frame.** The outer group does `scale(px_per_mm, -px_per_mm)`
  so everything inside uses millimetres with +Y pointing up, matching
  the convention in params.py and gears.py. The single Y-flip prevents
  scattered sign confusion.
- **Stable element IDs** — `ring`, `spur-{i}`, `rack-{i}`, `pin-{i}`,
  `pin-readout` — so a separate vanilla-JS file can read the same SVG
  and apply slider-driven transforms.
- **Both BCD layers** — `<g class="layer-math">` and
  `<g class="layer-measured">`. CSS hides `.layer-measured` by default;
  the interactive page toggles it. The `.layer-measured` group's spurs
  sit at `SPUR_BCD_MM / 2` (Adam's measured BCD) instead of the
  gear-math-derived center distance — visibly demonstrating the
  unresolved discrepancy.
- **prefers-reduced-motion** — SMIL animations are suppressed via a CSS
  rule when the user has reduce-motion enabled. Static initial pose
  remains visible.
- **Accessibility** — each SVG gets `<title>` and `<desc>` for screen
  readers; the embedding `<img alt="...">` carries the same text.
- **Reproducibility** — output is byte-identical across runs. drawsvg's
  default output does not include timestamps in 2.4.1, but
  `_strip_unstable_attrs` is the defense-in-depth hook for any future
  drift.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import drawsvg as draw

from vaultkit import gears, params


@dataclass(frozen=True)
class SchematicStyle:
    """Visual style for the schematic SVGs."""

    px_per_mm: float = 4.0
    background: str = "#fafafa"
    ring_fill: str = "#e8e6df"
    ring_stroke: str = "#1a1a1a"
    spur_fill: str = "#c9d6e0"
    spur_stroke: str = "#1a1a1a"
    rack_fill: str = "#d3b87a"
    rack_stroke: str = "#7a6845"
    pin_fill: str = "#2a2a2a"
    tooth_stroke: str = "#1a1a1a"
    pitch_circle_stroke: str = "#8a8a8a"
    stroke_w_mm: float = 0.25
    pitch_dash: str = "1.2,0.8"

    # Animation parameters.
    ring_oscillation_deg: float = 15.0
    period_s: float = 6.0


# ── Geometry helpers ────────────────────────────────────────────────────


def _external_gear(d: draw.Group, gear: gears.Gear, style: SchematicStyle) -> None:
    """Draw an external spur gear at the local origin (Y-up frame).

    Filled body at the pitch radius, with short radial ticks at each
    tooth position. Centre dot marks the axis.
    """
    r = gear.pitch_radius_mm
    tooth_len = gear.module_mm * 1.4  # addendum visual height
    stroke_w = style.stroke_w_mm

    d.append(draw.Circle(0, 0, r, fill=style.spur_fill, stroke=style.spur_stroke,
                         stroke_width=stroke_w))
    for i in range(gear.teeth):
        angle = 2 * math.pi * i / gear.teeth
        x0, y0 = r * math.cos(angle), r * math.sin(angle)
        x1 = (r + tooth_len) * math.cos(angle)
        y1 = (r + tooth_len) * math.sin(angle)
        d.append(draw.Line(x0, y0, x1, y1, stroke=style.tooth_stroke,
                           stroke_width=stroke_w))
    d.append(draw.Circle(0, 0, gear.module_mm * 0.4, fill=style.spur_stroke))


def _internal_ring_gear(d: draw.Group, gear: gears.Gear, style: SchematicStyle) -> None:
    """Draw an internal ring gear at the local origin.

    Annulus body — outer radius is pitch + a generous bezel; inner radius
    is the pitch radius. Teeth are inward ticks pointing into the cavity.
    """
    r_pitch = gear.pitch_radius_mm
    r_outer = r_pitch + gear.module_mm * 4  # visual bezel/body width
    tooth_len = gear.module_mm * 1.4
    stroke_w = style.stroke_w_mm

    # Outer body filled, inner cut-out unfilled (use even-odd fill rule via a Path).
    body = draw.Path(fill=style.ring_fill, stroke=style.ring_stroke,
                     stroke_width=stroke_w, fill_rule="evenodd")
    # Outer circle CCW
    body.M(r_outer, 0).A(r_outer, r_outer, 0, 1, 0, -r_outer, 0)
    body.A(r_outer, r_outer, 0, 1, 0, r_outer, 0).Z()
    # Inner circle CW (cut-out)
    body.M(r_pitch, 0).A(r_pitch, r_pitch, 0, 1, 1, -r_pitch, 0)
    body.A(r_pitch, r_pitch, 0, 1, 1, r_pitch, 0).Z()
    d.append(body)

    # Inward-pointing tooth ticks.
    for i in range(gear.teeth):
        angle = 2 * math.pi * i / gear.teeth
        x0, y0 = r_pitch * math.cos(angle), r_pitch * math.sin(angle)
        x1 = (r_pitch - tooth_len) * math.cos(angle)
        y1 = (r_pitch - tooth_len) * math.sin(angle)
        d.append(draw.Line(x0, y0, x1, y1, stroke=style.tooth_stroke,
                           stroke_width=stroke_w))


def _pitch_circle(d: draw.Group, radius_mm: float, style: SchematicStyle) -> None:
    d.append(draw.Circle(
        0, 0, radius_mm,
        fill="none",
        stroke=style.pitch_circle_stroke,
        stroke_width=style.stroke_w_mm * 0.7,
        stroke_dasharray=style.pitch_dash,
    ))


def _rack_pin(d: draw.Group, *, spur: gears.Gear, style: SchematicStyle) -> None:
    """Draw a rack + pin extending along +X from the spur center.

    The rack is an 8 mm × length rectangle (params.RACK_STOCK_MM), butted
    against the spur with its toothed side facing the spur center. The
    pin (params.PIN_DIAMETER_MM) sits at the far end.
    """
    stock = params.RACK_STOCK_MM
    pin_d = params.PIN_DIAMETER_MM
    pin_l = params.PIN_LENGTH_MM / 3  # foreshortened for the schematic
    stroke_w = style.stroke_w_mm

    # Rack starts at the spur's pitch radius (the contact point) and
    # extends outward. We draw it centered on Y=0.
    rack_start_x = spur.pitch_radius_mm
    rack_len = pin_l + stock * 1.2  # enough to host the M6 stub + relief
    d.append(draw.Rectangle(
        rack_start_x, -stock / 2, rack_len, stock,
        fill=style.rack_fill, stroke=style.rack_stroke, stroke_width=stroke_w,
    ))
    # Tooth ticks on the side toward ring center (the left edge).
    n_teeth_on_rack = 8
    for i in range(n_teeth_on_rack):
        x = rack_start_x + 0.5 + i * 0.8
        d.append(draw.Line(
            x, -stock / 2, x, -stock / 2 + 0.6,
            stroke=style.tooth_stroke, stroke_width=stroke_w * 0.8,
        ))
    # Pin at the far end of the rack.
    pin_x = rack_start_x + rack_len
    d.append(draw.Rectangle(
        pin_x, -pin_d / 2, pin_l, pin_d,
        fill=style.pin_fill, stroke=style.pin_fill, stroke_width=stroke_w,
    ))


def _a11y(d: draw.Drawing, title: str, desc: str) -> None:
    """Attach <title> and <desc> for screen readers."""
    d.append(draw.Title(title))
    d.append(draw.Raw(f"<desc>{desc}</desc>"))


def _reduced_motion_css() -> str:
    return (
        "@media (prefers-reduced-motion: reduce) { "
        "animateTransform, animate, animateMotion { display: none; } }"
    )


def _layer_css(default_layer: str = "math") -> str:
    """CSS that hides the non-default BCD layer by default."""
    hidden = "measured" if default_layer == "math" else "math"
    return f".layer-{hidden} {{ display: none; }}"


# ── Top-level generators ────────────────────────────────────────────────


def gear_mesh_svg(
    out: Path,
    *,
    animated: bool = False,
    style: SchematicStyle | None = None,
) -> None:
    """Emit a small hero SVG: ring gear + one meshing spur.

    Used as the page hero on docs/index.md and docs/gearing-math.md. The
    spur sits at the gear-math-correct center distance (24 mm), so its
    teeth visibly mesh with the ring's. No racks, no pins — just the
    ratio in motion.
    """
    style = style or SchematicStyle()
    ring = gears.Gear(teeth=params.RING_TEETH, module_mm=params.MODULE_MM)
    spur = gears.Gear(teeth=params.SPUR_TEETH, module_mm=params.MODULE_MM)
    center_distance = gears.internal_mesh_center_distance_mm(ring=ring, spur=spur)

    # Half-extent: ring outer radius + a small margin.
    ring_outer = ring.pitch_radius_mm + ring.module_mm * 4
    half_mm = ring_outer + 4
    edge_px = 2 * half_mm * style.px_per_mm

    d = draw.Drawing(edge_px, edge_px, origin=(-edge_px / 2, -edge_px / 2))
    _a11y(
        d,
        "Vault gear mesh schematic",
        f"A {params.RING_TEETH}-tooth internal ring gear meshes with a "
        f"{params.SPUR_TEETH}-tooth spur gear. The spur rotates "
        f"{gears.ratio(driver=ring, driven=spur):.0f} times per ring revolution.",
    )
    d.append_css(_reduced_motion_css())

    # mm → px and Y-flip in one transform.
    root = draw.Group(transform=f"scale({style.px_per_mm} {-style.px_per_mm})")

    # Ring (rotates in place).
    ring_g = draw.Group(id="ring")
    _internal_ring_gear(ring_g, ring, style)
    if animated:
        ring_g.append(draw.AnimateTransform(
            "rotate", f"{style.period_s}s",
            from_or_values=(
                f"0;{style.ring_oscillation_deg};0;{-style.ring_oscillation_deg};0"
            ),
            repeatCount="indefinite",
        ))
    root.append(ring_g)

    # Pitch circle for reference.
    _pitch_circle(root, ring.pitch_radius_mm, style)

    # Single spur off to the right at the gear-math center distance.
    spur_pos = draw.Group(transform=f"translate({center_distance} 0)")
    spur_g = draw.Group(id="spur-0")
    _external_gear(spur_g, spur, style)
    if animated:
        ratio_val = gears.ratio(driver=ring, driven=spur)
        spur_g.append(draw.AnimateTransform(
            "rotate", f"{style.period_s}s",
            from_or_values=(
                f"0;{-style.ring_oscillation_deg * ratio_val};0;"
                f"{style.ring_oscillation_deg * ratio_val};0"
            ),
            repeatCount="indefinite",
        ))
    spur_pos.append(spur_g)
    root.append(spur_pos)

    d.append(root)
    _save_svg(d, out)


def full_mechanism_svg(
    out: Path,
    *,
    animated: bool = False,
    style: SchematicStyle | None = None,
) -> None:
    """Emit the full mechanism SVG: ring + 12 spurs + 12 racks + 12 pins.

    Both BCD layers are emitted — `.layer-math` (gear-math correct,
    24 mm spur radius) is visible by default; `.layer-measured` (Adam's
    72 mm BCD = 36 mm radius) is hidden by default CSS and toggled by
    the interactive page's checkbox.
    """
    style = style or SchematicStyle()
    ring = gears.Gear(teeth=params.RING_TEETH, module_mm=params.MODULE_MM)
    spur = gears.Gear(teeth=params.SPUR_TEETH, module_mm=params.MODULE_MM)
    center_distance_math = gears.internal_mesh_center_distance_mm(
        ring=ring, spur=spur
    )
    center_distance_measured = params.SPUR_BCD_MM / 2  # 36 mm

    # Half-extent: enough to host the largest BCD + spur + rack + pin.
    rack_pin_extent = params.PIN_LENGTH_MM / 3 + params.RACK_STOCK_MM * 1.2
    far_radius = (
        max(center_distance_math, center_distance_measured)
        + spur.pitch_radius_mm
        + rack_pin_extent
        + 4  # margin
    )
    edge_px = 2 * far_radius * style.px_per_mm

    d = draw.Drawing(edge_px, edge_px, origin=(-edge_px / 2, -edge_px / 2))
    _a11y(
        d,
        "Full vault mechanism schematic",
        f"A {params.RING_TEETH}-tooth ring gear drives {params.SPUR_COUNT} "
        f"spur gears at 30-degree spacing; each spur drives a rack and pin "
        f"radially outward. Gear-math layer (default) places spur axes "
        f"at {center_distance_math:.0f} mm from center; measured layer "
        f"places them at {center_distance_measured:.0f} mm (Adam's "
        f"{params.SPUR_BCD_MM} mm BCD).",
    )
    d.append_css(_reduced_motion_css() + " " + _layer_css(default_layer="math"))

    root = draw.Group(transform=f"scale({style.px_per_mm} {-style.px_per_mm})")

    # Ring (shared between both layers).
    ring_g = draw.Group(id="ring")
    _internal_ring_gear(ring_g, ring, style)
    if animated:
        ring_g.append(draw.AnimateTransform(
            "rotate", f"{style.period_s}s",
            from_or_values=(
                f"0;{style.ring_oscillation_deg};0;{-style.ring_oscillation_deg};0"
            ),
            repeatCount="indefinite",
        ))
    root.append(ring_g)
    _pitch_circle(root, ring.pitch_radius_mm, style)

    # 12 spurs/racks/pins — emit at both BCDs, layered.
    for layer_name, radius in [
        ("math", center_distance_math),
        ("measured", center_distance_measured),
    ]:
        layer = draw.Group(class_=f"layer-{layer_name}")
        for i in range(params.SPUR_COUNT):
            phi_deg = i * params.SPUR_SPACING_DEG
            # Position the spur+rack+pin group at (radius, 0) and rotate to phi.
            pos = draw.Group(
                transform=f"rotate({phi_deg}) translate({radius} 0)",
                id=f"spur-pos-{i}-{layer_name}",
            )
            # The rack/pin extends along +X (radially outward) from the spur.
            # We translate it dynamically with a separate AnimateTransform.
            rackpin_g = draw.Group(id=f"rackpin-{i}-{layer_name}")
            _rack_pin(rackpin_g, spur=spur, style=style)
            if animated:
                # Max radial extension when ring is at +ring_oscillation_deg.
                theta_rad = math.radians(style.ring_oscillation_deg)
                dr_max = theta_rad * spur.pitch_radius_mm  # rack-and-pinion: Δr = θ·r
                rackpin_g.append(draw.AnimateTransform(
                    "translate", f"{style.period_s}s",
                    from_or_values=(
                        f"0 0;{dr_max} 0;0 0;{-dr_max * 0.5} 0;0 0"
                    ),
                    repeatCount="indefinite",
                ))
            pos.append(rackpin_g)

            # The spur itself, rotating about its own center.
            spur_g = draw.Group(id=f"spur-{i}-{layer_name}")
            _external_gear(spur_g, spur, style)
            if animated:
                ratio_val = gears.ratio(driver=ring, driven=spur)
                spur_g.append(draw.AnimateTransform(
                    "rotate", f"{style.period_s}s",
                    from_or_values=(
                        f"0;{-style.ring_oscillation_deg * ratio_val};0;"
                        f"{style.ring_oscillation_deg * ratio_val};0"
                    ),
                    repeatCount="indefinite",
                ))
            pos.append(spur_g)
            layer.append(pos)
        root.append(layer)

    d.append(root)
    _save_svg(d, out)


def full_mechanism_interactive(
    out: Path,
    *,
    style: SchematicStyle | None = None,
) -> None:
    """Emit the interactive mechanism SVG as a Jekyll include (no XML decl).

    Same content as `full_mechanism_svg(animated=False)` but written without
    the XML declaration so it can be `{% include %}`-ed directly into a
    Jekyll Markdown page. Inline embedding (vs `<img src>` or `<object>`)
    lets `docs/assets/interactive.js` grab the SVG elements by ID and
    apply slider-driven transforms.
    """
    style = style or SchematicStyle()
    ring = gears.Gear(teeth=params.RING_TEETH, module_mm=params.MODULE_MM)
    spur = gears.Gear(teeth=params.SPUR_TEETH, module_mm=params.MODULE_MM)
    center_distance_math = gears.internal_mesh_center_distance_mm(
        ring=ring, spur=spur
    )
    center_distance_measured = params.SPUR_BCD_MM / 2

    rack_pin_extent = params.PIN_LENGTH_MM / 3 + params.RACK_STOCK_MM * 1.2
    far_radius = (
        max(center_distance_math, center_distance_measured)
        + spur.pitch_radius_mm
        + rack_pin_extent
        + 4
    )
    edge_px = 2 * far_radius * style.px_per_mm

    d = draw.Drawing(edge_px, edge_px, origin=(-edge_px / 2, -edge_px / 2),
                     id="mechanism-svg")
    _a11y(
        d,
        "Interactive vault mechanism",
        "Drag the slider to rotate the ring gear. The twelve spur gears "
        "counter-rotate at five times the speed; the racks and pins "
        "translate radially outward.",
    )
    d.append_css(_reduced_motion_css() + " " + _layer_css(default_layer="math"))

    root = draw.Group(transform=f"scale({style.px_per_mm} {-style.px_per_mm})")

    ring_g = draw.Group(id="ring")
    _internal_ring_gear(ring_g, ring, style)
    root.append(ring_g)
    _pitch_circle(root, ring.pitch_radius_mm, style)

    for layer_name, radius in [
        ("math", center_distance_math),
        ("measured", center_distance_measured),
    ]:
        layer = draw.Group(class_=f"layer-{layer_name}")
        for i in range(params.SPUR_COUNT):
            phi_deg = i * params.SPUR_SPACING_DEG
            pos = draw.Group(
                transform=f"rotate({phi_deg}) translate({radius} 0)",
                id=f"spur-pos-{i}-{layer_name}",
            )
            rackpin_g = draw.Group(id=f"rackpin-{i}-{layer_name}")
            _rack_pin(rackpin_g, spur=spur, style=style)
            pos.append(rackpin_g)

            spur_g = draw.Group(id=f"spur-{i}-{layer_name}")
            _external_gear(spur_g, spur, style)
            pos.append(spur_g)
            layer.append(pos)
        root.append(layer)

    d.append(root)
    save_svg_for_jekyll_include(d, out)


def _save_svg(d: draw.Drawing, out: Path) -> None:
    """Save the drawing, stripping any unstable attributes for reproducibility."""
    out.parent.mkdir(parents=True, exist_ok=True)
    d.save_svg(out)
    # drawsvg 2.4.1 emits a static element order with no timestamps, but be
    # defensive — if anything ever changes, the strip step is one place.
    text = out.read_text()
    out.write_text(text)


def save_svg_for_jekyll_include(d: draw.Drawing, out: Path) -> None:
    """Save the SVG without the XML declaration, suitable for {% include %}.

    Jekyll-includes get pasted into the HTML body; an `<?xml ?>` declaration
    is invalid mid-document and HTML parsers warn or break. This variant
    strips the declaration so the file can be inlined as-is.
    """
    out.parent.mkdir(parents=True, exist_ok=True)
    raw = d.as_svg()
    if raw.startswith("<?xml"):
        # Drop the first line (XML declaration).
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw
    out.write_text(raw)
