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

from dataclasses import dataclass

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

# ── Pin fit / play ───────────────────────────────────────────────────────
# The faithful bore is a machined slip fit (clearance modeled as zero).
# The FDM bore is the planned deviation from cad/fdm/deviations.md —
# TBD until tuned on an actual print.
FDM_PIN_BORE_MM = 10.4
RACK_STUD_CONCENTRICITY_IN = 0.0125  # part-4: stud offset that made pins bind

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


# ── Onshape source provenance (the git ↔ Onshape version link) ───────────
# The dimension constants above are deliberately flat. This section is
# different: it's structured metadata *about the source documents*, not a
# dimension, so a small dataclass earns its keep. `release` (and, later,
# `capture`) import ONSHAPE so the doc URLs live in exactly one place.


@dataclass(frozen=True)
class OnshapeSource:
    """Where a variant's geometry comes from, and which snapshot it is.

    The `/w/` workspace URL is mutable — it tracks the live document. When a
    milestone is reached, cut a named *Version* in Onshape and record its
    immutable id here; that, committed alongside the re-exported STEP, is what
    ties a git commit to a specific Onshape version. Until then `version_id`
    is None and `permalink` falls back to the live workspace URL.
    """

    doc_url: str  # public /w/ workspace URL — what a reader clicks
    document_id: str
    workspace_id: str
    element_id: str
    step: str  # repo-relative path to the exported STEP
    version_id: str | None = None  # set once a named Version is cut in Onshape
    version_name: str | None = None  # e.g. "v0.1 — first public export"
    exported_utc: str | None = None  # ISO date the current STEP was exported

    @property
    def permalink(self) -> str:
        """Immutable /v/ URL when a Version is pinned, else the live /w/ URL."""
        if self.version_id:
            return (
                f"https://cad.onshape.com/documents/{self.document_id}"
                f"/v/{self.version_id}/e/{self.element_id}"
            )
        return self.doc_url


ONSHAPE = {
    "fdm": OnshapeSource(
        doc_url=(
            "https://cad.onshape.com/documents/017898deda56c430272a5497"
            "/w/5d7667d0936a708006b152fa/e/8e68069be3521bc23b864206"
        ),
        document_id="017898deda56c430272a5497",
        workspace_id="5d7667d0936a708006b152fa",
        element_id="8e68069be3521bc23b864206",
        step="step-source/fdm-vault.step",
    ),
    "faithful": OnshapeSource(
        doc_url=(
            "https://cad.onshape.com/documents/eaf3e87c1faae12ad867b335"
            "/w/83a96bb8921d1af3abd7aecd/e/9db299b535aaeded5de5120c"
        ),
        document_id="eaf3e87c1faae12ad867b335",
        workspace_id="83a96bb8921d1af3abd7aecd",
        element_id="9db299b535aaeded5de5120c",
        step="step-source/faithful-vault.step",
    ),
}

# Variant → STEP path. The one map the CLI loops, the release bundler, and the
# capture tooling all read. Derived from ONSHAPE so it can never drift from it.
VARIANTS = {key: src.step for key, src in ONSHAPE.items()}


# ── Public release framing (Printables / MakerWorld listings) ────────────
# Titles credit Adam and frame this as a study, on purpose. Edit the wording
# here; the release descriptions and listing sheets all read from it.
RELEASE_TITLES = {
    "fdm": "Vault Study — FDM: Adam Savage's vault door, retooled for a flatbed printer",
    "faithful": "Vault Study — Faithful: Adam Savage's 1/12 vault door, in CAD",
}

# Recommended print settings for the FDM listing — grounded in cad/fdm/README.md.
# Only the FDM variant is print-targeted; the faithful variant is a CAD reference.
PRINT_SETTINGS = {
    "fdm": {
        "layer_height_mm": 0.2,
        "wall_loops": 4,  # perimeters on the geared parts
        "supports": "none",
        "material_mechanism": "PETG",
        "material_cosmetic": "PLA",
    },
}
