"""Gear-math tests."""

from __future__ import annotations

import pytest

from vaultkit import gears, params


def test_ring_gear_pitch_diameter() -> None:
    ring = gears.Gear(teeth=params.RING_TEETH, module_mm=params.MODULE_MM)
    assert ring.pitch_diameter_mm == 60.0


def test_spur_gear_pitch_diameter() -> None:
    spur = gears.Gear(teeth=params.SPUR_TEETH, module_mm=params.MODULE_MM)
    assert spur.pitch_diameter_mm == 12.0


def test_drive_ratio_is_five() -> None:
    ring = gears.Gear(teeth=params.RING_TEETH, module_mm=params.MODULE_MM)
    spur = gears.Gear(teeth=params.SPUR_TEETH, module_mm=params.MODULE_MM)
    assert gears.ratio(driver=ring, driven=spur) == 5.0


def test_mismatched_modules_rejected() -> None:
    a = gears.Gear(teeth=24, module_mm=0.5)
    b = gears.Gear(teeth=24, module_mm=1.0)
    with pytest.raises(ValueError, match="same module"):
        gears.ratio(driver=a, driven=b)


def test_zero_teeth_rejected() -> None:
    a = gears.Gear(teeth=0, module_mm=0.5)
    b = gears.Gear(teeth=24, module_mm=0.5)
    with pytest.raises(ValueError, match="positive"):
        gears.ratio(driver=a, driven=b)


@pytest.mark.xfail(
    reason=(
        "Open CAD question. Gear math gives center distance "
        "= ring_PD/2 - spur_PD/2 = 24 mm, so derived BCD = 48 mm; "
        "Adam's measured BCD in part-2 is 72 mm. The discrepancy is "
        "discussed in docs/gearing-math.md — likely an additional "
        "offset between the ring's pitch circle and the acrylic's "
        "spur-mount face. This test starts passing once the geometry "
        "question is reconciled (either by amending params.py or by "
        "annotating SPUR_BCD_MM as not-derived-from-gear-math)."
    ),
    strict=True,
)
def test_internal_mesh_center_distance_matches_bcd() -> None:
    """The derived spur-axis radius should match the measured BCD."""
    ring = gears.Gear(teeth=params.RING_TEETH, module_mm=params.MODULE_MM)
    spur = gears.Gear(teeth=params.SPUR_TEETH, module_mm=params.MODULE_MM)
    center_distance = gears.internal_mesh_center_distance_mm(ring=ring, spur=spur)
    assert 2 * center_distance == params.SPUR_BCD_MM


def test_internal_mesh_requires_ring_larger() -> None:
    small = gears.Gear(teeth=24, module_mm=0.5)
    smaller = gears.Gear(teeth=24, module_mm=0.5)
    with pytest.raises(ValueError, match="more teeth"):
        gears.internal_mesh_center_distance_mm(ring=smaller, spur=small)


def test_teeth_between_satellites_divides_evenly() -> None:
    assert gears.teeth_between_satellites(
        ring_teeth=params.RING_TEETH,
        satellite_count=params.SPUR_COUNT,
    ) == 10


def test_uneven_satellite_count_rejected() -> None:
    with pytest.raises(ValueError, match="not divisible"):
        gears.teeth_between_satellites(ring_teeth=120, satellite_count=11)
