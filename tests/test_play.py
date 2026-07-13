"""Tests for vaultkit.play — pin-fit and tolerance stack-up math."""

from __future__ import annotations

import math

import pytest

from vaultkit import params, play


def test_fdm_fit_clearances() -> None:
    fit = play.FITS["fdm"]
    assert fit.diametral_clearance_mm == pytest.approx(0.4)
    assert fit.radial_clearance_mm == pytest.approx(0.2)


def test_faithful_fit_is_zero_clearance() -> None:
    fit = play.FITS["faithful"]
    assert fit.diametral_clearance_mm == 0
    assert fit.radial_clearance_mm == 0


def test_press_fit_rejected() -> None:
    with pytest.raises(ValueError):
        play.PinFit(pin_diameter_mm=10, bore_diameter_mm=9.8)


def test_frame_gap_is_converted_inches() -> None:
    # 0.020 in × 25.4 = 0.508 mm
    assert play.frame_gap_mm() == pytest.approx(0.508)


def test_pin_extension_matches_theta_r_identity() -> None:
    # Δr = θ_rad × ratio × spur pitch radius = θ_rad × 5 × 6 mm = 30·θ_rad
    assert play.pin_extension_mm(15.0) == pytest.approx(
        math.radians(15.0) * 30, abs=1e-9
    )


def test_tilt_deg_hand_computed() -> None:
    fit = play.PinFit(pin_diameter_mm=10, bore_diameter_mm=10.4)
    # atan(0.4 / 30) = 0.7639...°
    assert play.tilt_deg(fit, 30.0) == pytest.approx(
        math.degrees(math.atan(0.4 / 30)), abs=1e-9
    )
    # Shorter guided length → more tilt.
    assert play.tilt_deg(fit, 20.0) > play.tilt_deg(fit, 30.0)


def test_lateral_play_at_tip_hand_computed() -> None:
    fit = play.PinFit(pin_diameter_mm=10, bore_diameter_mm=10.4)
    guided = 22.0
    overhang = 8.0
    expected = 0.2 + math.tan(math.atan(0.4 / guided)) * overhang
    assert play.lateral_play_at_tip_mm(fit, guided, overhang) == pytest.approx(
        expected, abs=1e-9
    )


def test_locked_door_play_sums_radial_clearances() -> None:
    fdm = play.FITS["fdm"]
    assert play.locked_door_play_mm(fdm, fdm) == pytest.approx(0.4)
    faithful = play.FITS["faithful"]
    assert play.locked_door_play_mm(faithful, faithful) == 0


def test_travel_deadband_passes_through() -> None:
    assert play.travel_deadband_mm(0.15) == pytest.approx(0.15)
    with pytest.raises(ValueError):
        play.travel_deadband_mm(-0.1)


def test_stackup_consistent_with_params() -> None:
    su = play.stackup("fdm")
    assert su.fit.pin_diameter_mm == params.PIN_DIAMETER_MM
    assert su.fit.bore_diameter_mm == params.FDM_PIN_BORE_MM
    assert su.throw_deg == play.DEFAULT_THROW_DEG
    assert su.extension_mm == pytest.approx(play.pin_extension_mm(15.0))
    guided_extended = params.PIN_LENGTH_MM - su.extension_mm
    assert su.tilt_extended_deg == pytest.approx(
        play.tilt_deg(su.fit, guided_extended)
    )
    assert su.lateral_play_at_tip_mm == pytest.approx(
        play.lateral_play_at_tip_mm(
            su.fit, guided_extended, su.extension_mm + play.frame_gap_mm()
        )
    )
    # FDM locked-door play (0.4 mm) is smaller than the frame gap
    # (0.508 mm): the pins bear before the door edge touches the frame.
    assert su.locked_door_play_mm < su.frame_gap_mm


def test_stackup_faithful_is_all_zero_play() -> None:
    su = play.stackup("faithful")
    assert su.tilt_at_rest_deg == 0
    assert su.tilt_extended_deg == 0
    assert su.lateral_play_at_tip_mm == 0
    assert su.locked_door_play_mm == 0
