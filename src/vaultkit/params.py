"""Canonical parameters — Python mirror of specs.md.

Every dimension that appears in specs.md as a `live` row should appear here
as a constant with a matching value. The drift test in
tests/test_no_drift.py asserts that — change a number in specs.md, you must
change it here, and vice versa.

When you add a new section to specs.md, mirror it here under the same
heading comment. The constants are deliberately flat (no dataclasses, no
nesting) so a `grep PIN_DIAMETER_MM` finds every reference across the repo.

Units are encoded in the suffix: `_MM`, `_IN`, `_DEG`. No silent unit
conversions; if you need millimeters from an inch value, use the helper
in vaultkit.units (TODO — not yet written; for now do the math at the
call site and comment it).
"""

# ── Global gear math ─────────────────────────────────────────────────────
MODULE_MM = 0.5
SCALE = 1 / 12  # 1/12-scale relative to a real vault door

# ── Ring gear ────────────────────────────────────────────────────────────
RING_TEETH = 120
RING_OD_IN = 2.401
RING_ID_IN = 2.003
RING_TOOTH_DEPTH_IN = 0.044

# ── Spur gears ───────────────────────────────────────────────────────────
SPUR_COUNT = 12
SPUR_TEETH = 24
SPUR_BCD_MM = 72  # bolt-circle diameter
SPUR_SPACING_DEG = 30  # 360 / 12
SPUR_AXLE_SLIP_FIT_MM = 0.1  # shoulder bolt is 0.1 mm under gear bore

# ── Locking pins ─────────────────────────────────────────────────────────
PIN_COUNT = 12
PIN_DIAMETER_MM = 10  # revised in part-4 (was 12 mm — see specs.md)
PIN_LENGTH_MM = 30

# ── Racks ────────────────────────────────────────────────────────────────
RACK_STOCK_MM = 8  # square stock, 8 mm × 8 mm
RACK_THREAD_DIAMETER_MM = 6  # M6 stud at the end
RACK_QUANTITY_MACHINED = 14  # need 12; "always make more than you need"

# ── Main door body (acrylic hub) ─────────────────────────────────────────
HUB_OD_IN = 6.0
HUB_THICKNESS_IN = 1.25

# ── Heavy door puck (cast iron outer) ────────────────────────────────────
PUCK_OD_IN = 6.0
PUCK_FRONT_THICKNESS_IN = 0.5
PUCK_TAPER_DEG = 10  # nominal; actually three stepped angles
PUCK_CLOSURE_DEPTH_IN = 0.75

# ── Door frame ───────────────────────────────────────────────────────────
FRAME_THICKNESS_IN = 0.5
FRAME_OPENING_IN = 6.0
FRAME_CLEARANCE_IN = 0.020  # 20 thou all around the seated door

# ── Hinge ────────────────────────────────────────────────────────────────
HINGE_BEARING_OD_IN = 3 / 8
HINGE_PIN_IN = 1 / 8
HINGE_SCREW_COUNT = 28  # M2
HINGE_HOLE_INNER_X_IN = 0.245
HINGE_HOLE_COLUMN_SPACING_IN = 0.508
HINGE_HOLE_OUTER_X_IN = 0.753  # = inner + spacing
HINGE_HOLE_Y_SPAN_IN = 0.9125  # ± from center

# ── Combination lock ─────────────────────────────────────────────────────
COMBO_CAGE_LENGTH_IN = 0.75
COMBO_CAGE_WIDTH_IN = 0.5
COMBO_CAGE_BRASS_THICKNESS_IN = 0.025
COMBO_WHEEL_COUNT = 3
COMBO_WHEEL_DIAMETER_IN = 0.450
COMBO_DIAL_SPINDLE_IN = 1 / 8
COMBO_DIAL_DIVISIONS = 36
COMBO_DIAL_DIVISION_DEG = 10  # = 360 / 36
