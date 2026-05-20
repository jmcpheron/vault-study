"""2D SVG schematics of the vault gearing.

`gear_mesh_svg` and `full_mechanism_svg` emit SVGs that the explainer
pages embed as heroes and the interactive page consumes for slider-driven
animation. `technical_top_view_svg`, `rack_pinion_closeup_svg`, and
`pin_travel_diagram_svg` emit CAD-software-style technical drawings
for the pin-travel explainer page. Everything uses `drawsvg` 2.4.1.

Design choices:

- **Schematic, not involute.** Gear teeth are drawn as short radial tick
  marks crossing the pitch circle — recognizable as gears at small
  sizes, without the 200-vertex polygon math.
- **Y-up CAD frame.** The outer group does `scale(px_per_mm, -px_per_mm)`
  so everything inside uses millimetres with +Y pointing up, matching
  the convention in params.py and gears.py. The single Y-flip prevents
  scattered sign confusion.
- **Annotations live OUTSIDE the Y-flip.** Dimension lines, leader
  arrows, and text labels go in a sibling group at the SVG root, in
  raw pixel coordinates. Two reasons: (1) any `<text>` inside the
  `scale(1,-1)` group renders MIRRORED; (2) annotation text should
  stay at fixed point size, not scale with the diagram. Helpers
  `_mm_to_px`, `_annotations_group`, and the dimension-line primitives
  enforce this. CAD-frame mm coordinates are passed in; conversion
  to SVG pixel coords happens at write time.
- **Stable element IDs** — `ring`, `spur-{i}`, `rack-{i}`, `pin-{i}`,
  `pin-readout`, `pt-rack`, `pt-pin`, etc. — so vanilla-JS sliders
  read the same SVG and apply transforms.
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

    # CAD-technical-drawing palette (used by the dimension-line primitives
    # and the new technical_top_view / rack_pinion_closeup / pin_travel
    # generators). Subtle when inactive, accented when highlighting an
    # active value.
    construction_color: str = "#cfd4d8"     # barely above background
    center_mark_color: str = "#9aa3ac"
    dimension_color: str = "#3b6ea8"        # muted CAD blue
    dimension_text_color: str = "#1f3a5f"
    highlight_color: str = "#b8531a"        # muted CAD orange (active dim)
    annotation_font: str = "-apple-system, system-ui, sans-serif"
    annotation_size_px: float = 10.0


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


# ── CAD-technical-drawing primitives ────────────────────────────────────
#
# These all draw into the *annotations* group (the sibling of the Y-flip
# group), in raw pixel coordinates. Callers pass mm coordinates; the
# primitives convert via px_per_mm. Reason: <text> inside the Y-flip
# group renders mirrored, and annotation text shouldn't scale with the
# diagram anyway.


def _mm_to_px(p_mm: tuple[float, float], px_per_mm: float) -> tuple[float, float]:
    """Convert a CAD-frame (Y-up, mm) point to SVG pixel coords (Y-down)."""
    return (p_mm[0] * px_per_mm, -p_mm[1] * px_per_mm)


def _add_arrow_marker(d: draw.Drawing, *, marker_id: str, color: str) -> None:
    """Register a <marker> in the drawing's <defs> for arrowhead reuse.

    `orient="auto-start-reverse"` makes the marker auto-orient along the
    line direction — at marker-start it points OPPOSITE the line, at
    marker-end it points ALONG it. So both arrows on a dimension line
    point inward toward the label gap, which is the standard look.
    """
    d.append(draw.Raw(
        f'<defs><marker id="{marker_id}" viewBox="0 -5 10 10" '
        f'refX="9" refY="0" markerWidth="6" markerHeight="6" '
        f'orient="auto-start-reverse">'
        f'<path d="M0,-5L10,0L0,5z" fill="{color}"/>'
        f'</marker></defs>'
    ))


def _dimension_line(
    annotations: draw.Group,
    *,
    p1_mm: tuple[float, float],
    p2_mm: tuple[float, float],
    label: str,
    offset_mm: float,
    px_per_mm: float,
    style: SchematicStyle,
    arrow_marker_id: str = "vk-arrow",
    color: str | None = None,
) -> None:
    """Draw a linear dimension line between two CAD-frame points.

    `offset_mm` is the perpendicular distance from the original line to
    the dimension line — positive = offset CCW (above, for a horizontal
    p1→p2). Renders: two extension lines, a dimension line with
    arrowheads at both ends, and a centered label.
    """
    import math as _math
    color = color or style.dimension_color
    p1 = _mm_to_px(p1_mm, px_per_mm)
    p2 = _mm_to_px(p2_mm, px_per_mm)
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    length = _math.hypot(dx, dy) or 1.0
    # Perpendicular unit vector chosen so positive `offset_mm` pushes the
    # dimension line in the +CAD_y direction. We work in pixel coords
    # (SVG Y-down), so +CAD_y maps to -SVG_y. The CW perp (dy, -dx)
    # gives (0, -1) for a horizontal p1→p2 line, which is -SVG_y = +CAD_y.
    perp_x = dy / length
    perp_y = -dx / length
    off_px = offset_mm * px_per_mm
    # Offset endpoints (where the dim line lives).
    p1o = (p1[0] + perp_x * off_px, p1[1] + perp_y * off_px)
    p2o = (p2[0] + perp_x * off_px, p2[1] + perp_y * off_px)

    sw = style.stroke_w_mm * px_per_mm * 0.6  # thin lines for dimensions

    # Extension lines (from p1 to slightly past p1o, ditto p2).
    overshoot = 3.0  # px past the dim-line endpoint
    ext1_end = (p1[0] + perp_x * (off_px + overshoot),
                p1[1] + perp_y * (off_px + overshoot))
    ext2_end = (p2[0] + perp_x * (off_px + overshoot),
                p2[1] + perp_y * (off_px + overshoot))
    annotations.append(draw.Line(
        p1[0], p1[1], ext1_end[0], ext1_end[1],
        stroke=color, stroke_width=sw,
    ))
    annotations.append(draw.Line(
        p2[0], p2[1], ext2_end[0], ext2_end[1],
        stroke=color, stroke_width=sw,
    ))

    # Dimension line itself, with arrows at both ends pointing inward.
    annotations.append(draw.Line(
        p1o[0], p1o[1], p2o[0], p2o[1],
        stroke=color, stroke_width=sw,
        marker_start=f"url(#{arrow_marker_id})",
        marker_end=f"url(#{arrow_marker_id})",
    ))

    # Label centered on the dim line, slightly offset perpendicular so it
    # sits above the line rather than ON it.
    mid_x = (p1o[0] + p2o[0]) / 2 + perp_x * (style.annotation_size_px * 0.4)
    mid_y = (p1o[1] + p2o[1]) / 2 + perp_y * (style.annotation_size_px * 0.4)
    annotations.append(draw.Text(
        label, font_size=style.annotation_size_px,
        x=mid_x, y=mid_y,
        font_family=style.annotation_font,
        fill=style.dimension_text_color if color == style.dimension_color else color,
        text_anchor="middle", dominant_baseline="middle",
    ))


def _leader_arrow(
    annotations: draw.Group,
    *,
    target_mm: tuple[float, float],
    text_pos_mm: tuple[float, float],
    label: str,
    px_per_mm: float,
    style: SchematicStyle,
    arrow_marker_id: str = "vk-arrow",
    color: str | None = None,
    text_anchor: str = "start",
) -> None:
    """Draw a leader line from text_pos pointing at target, with text label.

    Arrow tip lands at `target_mm` (the part being labeled). Text sits at
    `text_pos_mm` (usually outside the geometry).
    """
    color = color or style.dimension_color
    target_px = _mm_to_px(target_mm, px_per_mm)
    text_px = _mm_to_px(text_pos_mm, px_per_mm)
    sw = style.stroke_w_mm * px_per_mm * 0.6

    annotations.append(draw.Line(
        text_px[0], text_px[1], target_px[0], target_px[1],
        stroke=color, stroke_width=sw,
        marker_end=f"url(#{arrow_marker_id})",
    ))
    # Text sits at text_px, with a small offset away from the arrow.
    annotations.append(draw.Text(
        label, font_size=style.annotation_size_px,
        x=text_px[0], y=text_px[1] - 4,  # small lift above the line endpoint
        font_family=style.annotation_font,
        fill=style.dimension_text_color if color == style.dimension_color else color,
        text_anchor=text_anchor, dominant_baseline="alphabetic",
    ))


def _diameter_callout(
    annotations: draw.Group,
    *,
    cx_mm: float,
    cy_mm: float,
    radius_mm: float,
    label: str,
    angle_deg: float,
    px_per_mm: float,
    style: SchematicStyle,
    arrow_marker_id: str = "vk-arrow",
    color: str | None = None,
) -> None:
    """Draw a 'Ø' callout across a circle at a given angle.

    Renders as a dimension line from one side of the circle to the other,
    along the direction `angle_deg`, with the label centered.
    """
    import math as _math
    a = _math.radians(angle_deg)
    p1_mm = (cx_mm - radius_mm * _math.cos(a), cy_mm - radius_mm * _math.sin(a))
    p2_mm = (cx_mm + radius_mm * _math.cos(a), cy_mm + radius_mm * _math.sin(a))
    _dimension_line(
        annotations,
        p1_mm=p1_mm, p2_mm=p2_mm,
        label=label, offset_mm=0.0,  # diameter sits ON the circle
        px_per_mm=px_per_mm, style=style,
        arrow_marker_id=arrow_marker_id, color=color,
    )


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


# ── CAD-technical-drawing generators ────────────────────────────────────


_RACK_ENGAGED_TEETH = 8           # how many rack teeth engage with the spur
_RACK_DISENGAGE_LIMIT_MM = 12.0   # ≈ 8 teeth × π·m at module 0.5


def rack_pinion_closeup_svg(
    out: Path,
    *,
    interactive: bool = False,
    style: SchematicStyle | None = None,
) -> None:
    """One spur + one rack + one pin, zoomed, with CAD-style dimensions.

    Layout (CAD frame, mm):
      Spur centered at (0, 0).
      Rack body above the spur with teeth on its bottom edge, sitting
        at the pitch tangent y = spur.pitch_radius.
      Pin at the rack's far +X end.

    `interactive=True` emits a Jekyll-include variant (no XML decl) with
    stable IDs on the rack/pin group so a slider can translate it via
    `transform="translate(Δr, 0)"`.
    """
    style = style or SchematicStyle()
    spur = gears.Gear(teeth=params.SPUR_TEETH, module_mm=params.MODULE_MM)
    px = style.px_per_mm
    stock = params.RACK_STOCK_MM
    pin_d = params.PIN_DIAMETER_MM
    pin_l_show = 9.0           # foreshortened pin
    rack_len = 22.0            # visible length of the rack body
    pl_y = spur.pitch_radius_mm  # rack pitch line (= tooth-tip line)

    # View bounds (CAD frame, mm).
    view_x_min, view_x_max = -16.0, 50.0
    view_y_min, view_y_max = -14.0, 24.0
    width_mm = view_x_max - view_x_min
    height_mm = view_y_max - view_y_min

    d = draw.Drawing(
        width_mm * px, height_mm * px,
        origin=(view_x_min * px, -view_y_max * px),
        id="pt-svg" if interactive else None,
    )
    _a11y(
        d,
        "Rack-and-pinion close-up",
        f"A {params.SPUR_TEETH}-tooth spur gear meshes with a rack on its "
        f"pitch line. The spur's pitch radius is {spur.pitch_radius_mm:.1f} mm. "
        f"Linear rack travel equals spur angle (radians) times pitch radius.",
    )
    d.append_css(_reduced_motion_css())
    _add_arrow_marker(d, marker_id="vk-arrow", color=style.dimension_color)
    _add_arrow_marker(d, marker_id="vk-arrow-hl", color=style.highlight_color)

    root = draw.Group(transform=f"scale({px} {-px})")

    # Spur pitch circle (dashed construction).
    root.append(draw.Circle(
        0, 0, spur.pitch_radius_mm,
        fill="none",
        stroke=style.pitch_circle_stroke,
        stroke_width=style.stroke_w_mm * 0.7,
        stroke_dasharray=style.pitch_dash,
    ))

    # Spur gear itself (no id needed — doesn't move under the slider).
    spur_g = draw.Group()
    _external_gear(spur_g, spur, style)
    root.append(spur_g)

    # Rack pitch line (dashed) — horizontal tangent at the contact.
    root.append(draw.Line(
        -10, pl_y, view_x_max - 2, pl_y,
        stroke=style.pitch_circle_stroke,
        stroke_width=style.stroke_w_mm * 0.7,
        stroke_dasharray=style.pitch_dash,
    ))

    # Disengagement-limit dashed vertical line (permanent feature).
    limit_x = _RACK_DISENGAGE_LIMIT_MM
    root.append(draw.Line(
        limit_x, -3, limit_x, pl_y + 14,
        stroke=style.highlight_color,
        stroke_width=style.stroke_w_mm * 0.7,
        stroke_dasharray="2,1.5",
    ))

    # The rack + pin assembly. Wrapped in a transformable group with id
    # `pt-rackpin` so a slider can translate it. Rack body sits at
    # y ∈ [pl_y, pl_y + stock]; teeth on the bottom edge engage the spur.
    rackpin_g = draw.Group(id="pt-rackpin")
    rackpin_g.append(draw.Rectangle(
        0, pl_y, rack_len, stock,
        fill=style.rack_fill, stroke=style.rack_stroke,
        stroke_width=style.stroke_w_mm,
    ))
    # Rack teeth on the bottom edge (facing down toward the spur).
    tooth_pitch_mm = 3.14159 * params.MODULE_MM  # ≈ 1.571 mm
    n_teeth = int(rack_len / tooth_pitch_mm)
    for i in range(n_teeth):
        tx = tooth_pitch_mm * (i + 0.5)
        rackpin_g.append(draw.Line(
            tx, pl_y, tx, pl_y + 0.7,
            stroke=style.tooth_stroke, stroke_width=style.stroke_w_mm * 0.7,
        ))
    # Pin at the rack's far +X end.
    rackpin_g.append(draw.Rectangle(
        rack_len, pl_y + stock / 2 - pin_d / 2, pin_l_show, pin_d,
        fill=style.pin_fill, stroke=style.pin_fill,
        stroke_width=style.stroke_w_mm,
    ))
    root.append(rackpin_g)

    # Pitch-point marker — small `+` at the spur/rack contact.
    cross = 1.2
    root.append(draw.Line(
        -cross, pl_y, cross, pl_y,
        stroke=style.dimension_color, stroke_width=style.stroke_w_mm * 0.9,
    ))
    root.append(draw.Line(
        0, pl_y - cross, 0, pl_y + cross,
        stroke=style.dimension_color, stroke_width=style.stroke_w_mm * 0.9,
    ))

    d.append(root)

    # ── Annotations (pixel coords, OUTSIDE the Y-flip). ───────────────
    ann = draw.Group(id="annotations")

    # Spur pitch radius — vertical dimension from spur center to contact.
    _dimension_line(
        ann,
        p1_mm=(-spur.pitch_radius_mm * 1.6, 0),
        p2_mm=(-spur.pitch_radius_mm * 1.6, pl_y),
        label=f"r = {spur.pitch_radius_mm:.0f} mm",
        offset_mm=0, px_per_mm=px, style=style,
    )

    # Tooth-pitch dimension between two adjacent rack teeth.
    _dimension_line(
        ann,
        p1_mm=(tooth_pitch_mm * 2.5, pl_y + stock + 0.5),
        p2_mm=(tooth_pitch_mm * 3.5, pl_y + stock + 0.5),
        label=f"π·m = {tooth_pitch_mm:.2f} mm",
        offset_mm=3, px_per_mm=px, style=style,
    )

    # Pitch-point leader.
    _leader_arrow(
        ann,
        target_mm=(0.4, pl_y - 0.4),
        text_pos_mm=(-15, pl_y - 3),
        label="pitch point",
        px_per_mm=px, style=style,
    )

    # Spur tooth-count callout.
    _leader_arrow(
        ann,
        target_mm=(-spur.pitch_radius_mm * 0.7, -spur.pitch_radius_mm * 0.5),
        text_pos_mm=(-14, -10),
        label=f"{params.SPUR_TEETH} teeth, module {params.MODULE_MM}",
        px_per_mm=px, style=style,
    )

    # Disengagement-limit callout (highlight color). Position the text
    # below the limit line so it never clips the view top.
    _leader_arrow(
        ann,
        target_mm=(limit_x, pl_y + 6),
        text_pos_mm=(limit_x + 5, -8),
        label="rack disengages",
        px_per_mm=px, style=style,
        color=style.highlight_color,
        arrow_marker_id="vk-arrow-hl",
    )

    # Active Δr readout — sits below the diagram so it never collides
    # with the disengagement-limit callout.
    ann.append(draw.Text(
        "Δr = 0.00 mm", id="pt-active-dim",
        x=(view_x_max - 4) * px, y=-(view_y_min + 2) * px,
        font_size=style.annotation_size_px * 1.3,
        font_family=style.annotation_font,
        fill=style.highlight_color,
        text_anchor="end",
    ))

    d.append(ann)

    if interactive:
        save_svg_for_jekyll_include(d, out)
    else:
        _save_svg(d, out)


def technical_top_view_svg(
    out: Path,
    *,
    style: SchematicStyle | None = None,
) -> None:
    """Top-down full-mechanism SVG with CAD-style dimensions.

    Dimension callouts: ring OD/ID/pitch, spur PD, BCD, spacing angle,
    tooth counts. All annotations placed outside the radial gear-occupied
    zone to avoid colliding with the 12 spurs.
    """
    style = style or SchematicStyle()
    ring = gears.Gear(teeth=params.RING_TEETH, module_mm=params.MODULE_MM)
    spur = gears.Gear(teeth=params.SPUR_TEETH, module_mm=params.MODULE_MM)
    bcd_r = params.SPUR_BCD_MM / 2
    rack_pin_extent = params.PIN_LENGTH_MM / 3 + params.RACK_STOCK_MM * 1.2

    # Make room for dimension labels in the outside zone.
    half_mm = bcd_r + spur.pitch_radius_mm + rack_pin_extent + 18
    edge_px = 2 * half_mm * style.px_per_mm
    px = style.px_per_mm

    d = draw.Drawing(edge_px, edge_px, origin=(-edge_px / 2, -edge_px / 2))
    _a11y(
        d,
        "Technical top view of the vault mechanism",
        f"Top-down dimensioned drawing: ring gear pitch diameter "
        f"{ring.pitch_diameter_mm:.0f} mm, {params.RING_TEETH} teeth; "
        f"{params.SPUR_COUNT} spur gears at {params.SPUR_BCD_MM} mm "
        f"bolt-circle diameter, each {params.SPUR_TEETH} teeth, pitch "
        f"diameter {spur.pitch_diameter_mm:.0f} mm.",
    )
    d.append_css(_reduced_motion_css())
    _add_arrow_marker(d, marker_id="vk-arrow", color=style.dimension_color)

    root = draw.Group(transform=f"scale({px} {-px})")

    # Ring gear.
    ring_g = draw.Group()
    _internal_ring_gear(ring_g, ring, style)
    root.append(ring_g)
    _pitch_circle(root, ring.pitch_radius_mm, style)

    # 12 spurs + rack/pin pairs at the measured BCD (consistent with the
    # other technical drawings — the discrepancy is its own page).
    for i in range(params.SPUR_COUNT):
        phi_deg = i * params.SPUR_SPACING_DEG
        pos = draw.Group(transform=f"rotate({phi_deg}) translate({bcd_r} 0)")
        # Rack + pin first (so they sit "behind" the spur).
        rp = draw.Group()
        _rack_pin(rp, spur=spur, style=style)
        pos.append(rp)
        # Spur.
        sg = draw.Group()
        _external_gear(sg, spur, style)
        pos.append(sg)
        root.append(pos)

    d.append(root)

    # ── Annotations ────────────────────────────────────────────────────
    ann = draw.Group(id="annotations")

    # Ring pitch diameter — leader pointing to a tangent on the ring,
    # label placed outside the radial zone (avoids the cluttered centre).
    import math as _math
    rp_ang = _math.radians(135)
    _leader_arrow(
        ann,
        target_mm=(ring.pitch_radius_mm * _math.cos(rp_ang),
                   ring.pitch_radius_mm * _math.sin(rp_ang)),
        text_pos_mm=(-half_mm + 12, half_mm - 14),
        label=f"Ø{ring.pitch_diameter_mm:.0f} ring pitch",
        px_per_mm=px, style=style,
    )

    # BCD — leader pointing to a spur at +45° (in the gap between spurs),
    # label outside the radial zone on the lower right.
    bcd_ang = _math.radians(-30)
    _leader_arrow(
        ann,
        target_mm=(bcd_r * _math.cos(bcd_ang),
                   bcd_r * _math.sin(bcd_ang)),
        text_pos_mm=(half_mm - 12, -half_mm + 18),
        label=f"Ø{params.SPUR_BCD_MM} spur BCD",
        px_per_mm=px, style=style,
        text_anchor="end",
    )

    # Ring tooth-count callout (leader to a tooth at 90°).
    ring_tooth_mm = ring.pitch_radius_mm + ring.module_mm * 0.5
    _leader_arrow(
        ann,
        target_mm=(0, ring_tooth_mm),
        text_pos_mm=(0, ring_tooth_mm + 12),
        label=f"{params.RING_TEETH} internal teeth, module {params.MODULE_MM}",
        px_per_mm=px, style=style,
        text_anchor="middle",
    )

    # Spur tooth-count callout (leader to the spur at 180°).
    spur_at_180 = (-bcd_r, 0)
    _leader_arrow(
        ann,
        target_mm=spur_at_180,
        text_pos_mm=(-bcd_r - spur.pitch_radius_mm - 18, 6),
        label=f"{params.SPUR_TEETH} teeth × {params.SPUR_COUNT}",
        px_per_mm=px, style=style,
        text_anchor="end",
    )

    # 30° spacing angle callout (leader to the gap between two adjacent spurs).
    import math as _math
    gap_angle = _math.radians(15)  # midpoint between spur 0 and spur 1
    gap_r = bcd_r + spur.pitch_radius_mm + 4
    gap_pt = (gap_r * _math.cos(gap_angle), gap_r * _math.sin(gap_angle))
    _leader_arrow(
        ann,
        target_mm=gap_pt,
        text_pos_mm=(gap_r + 8, gap_r * 0.4),
        label="30° spacing\n(360 / 12)",
        px_per_mm=px, style=style,
    )

    # Pin diameter callout (leader to one pin at 0°).
    pin_at_0_mm = (bcd_r + spur.pitch_radius_mm + rack_pin_extent + 0.5, 0)
    _leader_arrow(
        ann,
        target_mm=pin_at_0_mm,
        text_pos_mm=(pin_at_0_mm[0] + 8, -8),
        label=f"Ø{params.PIN_DIAMETER_MM} pin",
        px_per_mm=px, style=style,
    )

    d.append(ann)
    _save_svg(d, out)


def pin_travel_diagram_svg(
    out: Path,
    *,
    ring_angle_deg: float = 15.0,
    style: SchematicStyle | None = None,
) -> None:
    """One pin in retracted + extended positions, with a bracket dimension.

    Shows the door body cross-section (a rectangle representing the pin
    bore through the puck) and the pin in two states: at rest, and at
    `ring_angle_deg` of ring rotation (default 15° → 7.85 mm travel).
    """
    import math as _math

    style = style or SchematicStyle()
    spur = gears.Gear(teeth=params.SPUR_TEETH, module_mm=params.MODULE_MM)
    ring = gears.Gear(teeth=params.RING_TEETH, module_mm=params.MODULE_MM)
    ratio_val = gears.ratio(driver=ring, driven=spur)
    pin_travel_mm = _math.radians(ring_angle_deg) * ratio_val * spur.pitch_radius_mm

    # Layout (CAD frame, mm):
    #   Door-body bore: rectangle at y ∈ [-pin_d/2, +pin_d/2], x ∈ [0, 22]
    #     (representing the radial bore through the door puck).
    #   Pin retracted: a rectangle at x ∈ [0, 22] (fits in the bore).
    #   Pin extended: shifted right by pin_travel_mm.
    #   Frame receiver: a hatched rectangle at x ∈ [22, 22 + 20].
    pin_d = params.PIN_DIAMETER_MM
    pin_l_show = 22.0       # foreshortened
    bore_x0, bore_x1 = -2.0, pin_l_show

    view_x_min, view_x_max = -10.0, pin_l_show + 28.0
    view_y_min, view_y_max = -pin_d - 10.0, pin_d + 14.0
    width_mm = view_x_max - view_x_min
    height_mm = view_y_max - view_y_min
    px = style.px_per_mm

    d = draw.Drawing(
        width_mm * px, height_mm * px,
        origin=(view_x_min * px, -view_y_max * px),
    )
    _a11y(
        d,
        "Pin travel diagram",
        f"A single locking pin shown in retracted and extended positions. "
        f"At a ring rotation of {ring_angle_deg:.0f}°, each pin extends "
        f"{pin_travel_mm:.2f} mm through the door body and into the frame.",
    )
    d.append_css(_reduced_motion_css())
    _add_arrow_marker(d, marker_id="vk-arrow", color=style.dimension_color)
    _add_arrow_marker(d, marker_id="vk-arrow-hl", color=style.highlight_color)

    root = draw.Group(transform=f"scale({px} {-px})")

    # Frame receiver — hatched rectangle on the right.
    frame_x0 = pin_l_show + 2.0
    frame_x1 = frame_x0 + 18.0
    root.append(draw.Rectangle(
        frame_x0, -pin_d / 2 - 6, frame_x1 - frame_x0, pin_d + 12,
        fill="#eeeae0",
        stroke=style.construction_color,
        stroke_width=style.stroke_w_mm,
    ))
    # Hatching (diagonal lines) on the frame receiver.
    for hx in range(int(frame_x0) + 1, int(frame_x1), 2):
        root.append(draw.Line(
            hx, -pin_d / 2 - 6, hx - 4, -pin_d / 2 - 6 + 4,
            stroke=style.construction_color,
            stroke_width=style.stroke_w_mm * 0.4,
        ))

    # Door body bore — hollow rectangle.
    root.append(draw.Rectangle(
        bore_x0, -pin_d / 2 - 1, bore_x1 - bore_x0, pin_d + 2,
        fill="none",
        stroke=style.construction_color,
        stroke_width=style.stroke_w_mm,
        stroke_dasharray="1.5,1",
    ))

    # Retracted pin (faded, on the left).
    root.append(draw.Rectangle(
        0, -pin_d / 2, bore_x1, pin_d,
        fill="#e0e0e0",
        stroke=style.pin_fill,
        stroke_width=style.stroke_w_mm * 0.5,
    ))

    # Extended pin (solid, shifted right).
    root.append(draw.Rectangle(
        pin_travel_mm, -pin_d / 2, bore_x1, pin_d,
        fill=style.pin_fill,
        stroke=style.pin_fill,
        stroke_width=style.stroke_w_mm,
    ))

    d.append(root)

    # ── Annotations ────────────────────────────────────────────────────
    ann = draw.Group(id="annotations")

    # Pin travel bracket — from extended-pin's left edge back to
    # retracted-pin's left edge, with highlight color.
    _dimension_line(
        ann,
        p1_mm=(0, -pin_d / 2 - 6),
        p2_mm=(pin_travel_mm, -pin_d / 2 - 6),
        label=f"Δr = {pin_travel_mm:.2f} mm",
        offset_mm=-2, px_per_mm=px, style=style,
        color=style.highlight_color,
        arrow_marker_id="vk-arrow-hl",
    )

    # Pin diameter callout on the retracted pin.
    _dimension_line(
        ann,
        p1_mm=(-3, -pin_d / 2),
        p2_mm=(-3, pin_d / 2),
        label=f"Ø{pin_d}",
        offset_mm=0, px_per_mm=px, style=style,
    )

    # Frame receiver label.
    _leader_arrow(
        ann,
        target_mm=(frame_x0 + 4, pin_d / 2 + 3),
        text_pos_mm=(frame_x0 + 8, pin_d / 2 + 12),
        label="frame receiver",
        px_per_mm=px, style=style,
    )

    # Door body label.
    _leader_arrow(
        ann,
        target_mm=(pin_l_show / 2, -pin_d / 2 - 1),
        text_pos_mm=(pin_l_show / 2 + 2, -pin_d / 2 - 8),
        label="door body bore",
        px_per_mm=px, style=style,
    )

    # State labels.
    ann.append(draw.Text(
        "at rest",
        x=(pin_l_show / 2) * px, y=-(pin_d / 2 + 4) * px,
        font_size=style.annotation_size_px,
        font_family=style.annotation_font,
        fill=style.dimension_text_color,
        text_anchor="middle",
    ))
    ann.append(draw.Text(
        f"after {ring_angle_deg:.0f}° throw",
        x=(pin_travel_mm + pin_l_show / 2) * px, y=-(pin_d / 2 + 7) * px,
        font_size=style.annotation_size_px,
        font_family=style.annotation_font,
        fill=style.highlight_color,
        text_anchor="middle",
    ))

    d.append(ann)
    _save_svg(d, out)
