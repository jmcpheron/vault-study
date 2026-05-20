"""Gear math.

Pure-Python module-and-tooth-count math for spur and internal gears.
No CAD library dependencies — testable in isolation, and the source
of every derived number that appears in specs.md's "Derived values"
section and in the explainer pages.

The formulas here follow the standard metric-module convention used
by Onshape's Spur Gear FeatureScript:

    pitch_diameter = module * tooth_count

Meshing gears must share the same module. Center distance between two
externally meshing gears is the sum of their pitch radii; between an
internal (ring) gear and an external (spur) it's the difference.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Gear:
    """A spur gear specified by module and tooth count."""

    teeth: int
    module_mm: float

    @property
    def pitch_diameter_mm(self) -> float:
        return self.module_mm * self.teeth

    @property
    def pitch_radius_mm(self) -> float:
        return self.pitch_diameter_mm / 2


def ratio(driver: Gear, driven: Gear) -> float:
    """Speed ratio of two meshing gears: turns of driven per turn of driver.

    For the vault: a 120-tooth ring driving a 24-tooth spur gives ratio 5.0
    — the spur turns five times for each full revolution of the ring. This
    matches specs.md's "5:1" callout (tooth-count ratio 120:24).
    """
    if driver.teeth <= 0 or driven.teeth <= 0:
        raise ValueError("tooth counts must be positive")
    if driver.module_mm != driven.module_mm:
        raise ValueError(
            f"meshing gears must share the same module; "
            f"got {driver.module_mm} and {driven.module_mm}"
        )
    return driver.teeth / driven.teeth


def internal_mesh_center_distance_mm(ring: Gear, spur: Gear) -> float:
    """Center distance from ring-gear axis to a satellite spur's axis.

    For an internal (ring) gear meshing with an external spur, the center
    distance is the *difference* of pitch radii, not the sum. This is the
    number that determines the bolt-circle radius for the satellite spurs.
    """
    if ring.module_mm != spur.module_mm:
        raise ValueError(
            f"ring and spur must share the same module; "
            f"got {ring.module_mm} and {spur.module_mm}"
        )
    if ring.teeth <= spur.teeth:
        raise ValueError(
            f"ring must have more teeth than spur; got {ring.teeth} and {spur.teeth}"
        )
    return ring.pitch_radius_mm - spur.pitch_radius_mm


def teeth_between_satellites(ring_teeth: int, satellite_count: int) -> int:
    """How many ring-gear teeth sit between the centers of adjacent satellites.

    The "timing math" Adam emphasises in part-2: for the satellites to
    mesh evenly around the ring, the ring's tooth count must be divisible
    by the number of satellites. 120 / 12 = 10 teeth between adjacent
    spur-gear centers.
    """
    if satellite_count <= 0:
        raise ValueError("satellite_count must be positive")
    if ring_teeth % satellite_count != 0:
        raise ValueError(
            f"ring teeth ({ring_teeth}) is not divisible by satellite count "
            f"({satellite_count}) — the mechanism will not be evenly timed"
        )
    return ring_teeth // satellite_count
