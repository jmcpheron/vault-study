"""Pin-fit and tolerance stack-up math.

Pure-Python (stdlib only, like gears.py) answers to "how much can a
locking pin actually move?" for a given pin/bore fit. The blog post on
pin play and the `vaultkit play` CLI table both read their numbers from
here, so prose can never drift from the math.

Model and assumptions (kept deliberately simple):

  * A pin is a rigid cylinder in a straight bore. Diametral clearance is
    `bore - pin`; radial clearance is half that.
  * Tilt: a pin can cock inside its bore until it touches both walls —
    `atan(diametral / guided_length)`. Shorter guided length → more tilt.
  * Lateral play at the tip: the radial clearance (pure translation) plus
    the tilt projected over the unsupported overhang past the bore.
  * Locked-door play: with pins extended into the frame receivers, the
    door can shift until pins bear on both bores. We assume the receiver
    bore uses the same fit as the door bore.
  * Gear backlash adds a travel dead-band that passes 1:1 through the
    rack (`travel_deadband_mm`). We have no measured backlash figure, so
    it is an input here, never a constant.

The faithful variant's bore is a machined slip fit; we model its
clearance as exactly zero. The FDM bore is the planned value in
params.FDM_PIN_BORE_MM (see cad/fdm/deviations.md — TBD until a print
is tuned).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from vaultkit import gears, params

# The canonical lever throw used across the explainer pages and the
# schematic animations (SchematicStyle.ring_oscillation_deg).
DEFAULT_THROW_DEG = 15.0


@dataclass(frozen=True)
class PinFit:
    """A pin in a bore, both diameters in millimetres."""

    pin_diameter_mm: float
    bore_diameter_mm: float

    def __post_init__(self) -> None:
        if self.pin_diameter_mm <= 0:
            raise ValueError("pin diameter must be positive")
        if self.bore_diameter_mm < self.pin_diameter_mm:
            raise ValueError(
                f"bore ({self.bore_diameter_mm} mm) is smaller than the pin "
                f"({self.pin_diameter_mm} mm) — that's a press fit, not a slide"
            )

    @property
    def diametral_clearance_mm(self) -> float:
        return self.bore_diameter_mm - self.pin_diameter_mm

    @property
    def radial_clearance_mm(self) -> float:
        return self.diametral_clearance_mm / 2


# Variant → fit. Faithful is a machined slip fit, modeled as zero
# clearance; FDM is the planned printed bore.
FITS = {
    "faithful": PinFit(
        pin_diameter_mm=params.PIN_DIAMETER_MM,
        bore_diameter_mm=params.PIN_DIAMETER_MM,
    ),
    "fdm": PinFit(
        pin_diameter_mm=params.PIN_DIAMETER_MM,
        bore_diameter_mm=params.FDM_PIN_BORE_MM,
    ),
}


def frame_gap_mm() -> float:
    """The door-to-frame clearance from specs.md, converted to mm."""
    return params.FRAME_CLEARANCE_IN * 25.4


def pin_extension_mm(ring_angle_deg: float) -> float:
    """Radial pin travel for a given ring-gear rotation.

    Same identity the pin-travel page derives: linear travel = θ · r,
    chained through the 5:1 ring:spur ratio.
    """
    ring = gears.Gear(teeth=params.RING_TEETH, module_mm=params.MODULE_MM)
    spur = gears.Gear(teeth=params.SPUR_TEETH, module_mm=params.MODULE_MM)
    ratio_val = gears.ratio(driver=ring, driven=spur)
    return math.radians(ring_angle_deg) * ratio_val * spur.pitch_radius_mm


def tilt_deg(fit: PinFit, guided_length_mm: float) -> float:
    """Max cock angle of a pin guided over `guided_length_mm` of bore."""
    if guided_length_mm <= 0:
        raise ValueError("guided length must be positive")
    return math.degrees(math.atan2(fit.diametral_clearance_mm, guided_length_mm))


def lateral_play_at_tip_mm(
    fit: PinFit, guided_length_mm: float, overhang_mm: float
) -> float:
    """How far the pin tip can move sideways, tip overhanging the bore.

    Radial clearance (pure translation) plus the tilt angle projected
    over the unsupported overhang.
    """
    if overhang_mm < 0:
        raise ValueError("overhang cannot be negative")
    tilt_rad = math.radians(tilt_deg(fit, guided_length_mm))
    return fit.radial_clearance_mm + math.tan(tilt_rad) * overhang_mm


def locked_door_play_mm(door_fit: PinFit, receiver_fit: PinFit) -> float:
    """How far the locked door can shift before pins bear on both bores.

    With a pin bridging the door bore and the frame receiver, the door
    can translate by the sum of the two radial clearances before metal
    (or PETG) touches.
    """
    return door_fit.radial_clearance_mm + receiver_fit.radial_clearance_mm


def travel_deadband_mm(backlash_at_pitch_line_mm: float) -> float:
    """Travel dead-band contributed by gear backlash.

    A rack-and-pinion passes pitch-line backlash straight through to
    linear travel, 1:1. We have no measured backlash figure for the
    module-0.5 gears (printed or machined) — when one is measured, it
    becomes a params.py constant and this stops being an input.
    """
    if backlash_at_pitch_line_mm < 0:
        raise ValueError("backlash cannot be negative")
    return backlash_at_pitch_line_mm


@dataclass(frozen=True)
class Stackup:
    """The full pin-play stack-up for one variant at one lever throw."""

    variant: str
    fit: PinFit
    throw_deg: float
    extension_mm: float
    tilt_at_rest_deg: float
    tilt_extended_deg: float
    lateral_play_at_tip_mm: float
    locked_door_play_mm: float
    frame_gap_mm: float


def stackup(variant: str, *, throw_deg: float = DEFAULT_THROW_DEG) -> Stackup:
    """Compute the stack-up table for a variant.

    At rest the pin is fully guided (params.PIN_LENGTH_MM of bore).
    Extended, the guided length shrinks by the extension and the tip
    overhangs the door bore by the extension plus the door-frame gap.
    """
    fit = FITS[variant]
    extension = pin_extension_mm(throw_deg)
    guided_at_rest = params.PIN_LENGTH_MM
    guided_extended = params.PIN_LENGTH_MM - extension
    overhang = extension + frame_gap_mm()
    return Stackup(
        variant=variant,
        fit=fit,
        throw_deg=throw_deg,
        extension_mm=extension,
        tilt_at_rest_deg=tilt_deg(fit, guided_at_rest),
        tilt_extended_deg=tilt_deg(fit, guided_extended),
        lateral_play_at_tip_mm=lateral_play_at_tip_mm(
            fit, guided_extended, overhang
        ),
        locked_door_play_mm=locked_door_play_mm(fit, fit),
        frame_gap_mm=frame_gap_mm(),
    )
