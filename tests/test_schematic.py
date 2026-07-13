"""Tests for vaultkit.explainers.schematic."""

from __future__ import annotations

from pathlib import Path

from vaultkit.explainers import schematic


def test_gear_mesh_svg_contains_expected_ids(tmp_path: Path) -> None:
    out = tmp_path / "mesh.svg"
    schematic.gear_mesh_svg(out, animated=False)
    text = out.read_text()
    assert 'id="ring"' in text
    assert 'id="spur-0"' in text
    assert "<title>" in text
    assert "<desc>" in text


def test_gear_mesh_svg_animated_includes_animatetransform(tmp_path: Path) -> None:
    out = tmp_path / "mesh.animated.svg"
    schematic.gear_mesh_svg(out, animated=True)
    text = out.read_text()
    assert "<animateTransform" in text
    assert 'attributeName="transform"' in text


def test_full_mechanism_svg_has_both_bcd_layers(tmp_path: Path) -> None:
    out = tmp_path / "mech.svg"
    schematic.full_mechanism_svg(out, animated=False)
    text = out.read_text()
    assert 'class="layer-math"' in text
    assert 'class="layer-measured"' in text
    # 12 spurs × 2 layers
    for i in range(12):
        assert f'id="spur-{i}-math"' in text
        assert f'id="spur-{i}-measured"' in text
        assert f'id="rackpin-{i}-math"' in text
        assert f'id="rackpin-{i}-measured"' in text


def test_interactive_svg_has_no_xml_declaration(tmp_path: Path) -> None:
    out = tmp_path / "interactive.svg"
    schematic.full_mechanism_interactive(out)
    text = out.read_text()
    assert not text.startswith("<?xml"), "Jekyll-include SVG must not have XML decl"
    assert "<svg" in text
    assert 'id="mechanism-svg"' in text


def test_schematic_output_is_reproducible(tmp_path: Path) -> None:
    """Generating twice should produce byte-identical output."""
    out1 = tmp_path / "first.svg"
    out2 = tmp_path / "second.svg"
    schematic.full_mechanism_svg(out1, animated=True)
    schematic.full_mechanism_svg(out2, animated=True)
    assert out1.read_bytes() == out2.read_bytes(), (
        "schematic.full_mechanism_svg is not reproducible — something time-"
        "dependent or randomised crept in."
    )


def test_reduced_motion_css_present(tmp_path: Path) -> None:
    out = tmp_path / "mesh.svg"
    schematic.gear_mesh_svg(out, animated=True)
    assert "prefers-reduced-motion" in out.read_text()


def test_technical_top_view_contains_dimension_labels(tmp_path: Path) -> None:
    out = tmp_path / "topview.svg"
    schematic.technical_top_view_svg(out)
    text = out.read_text()
    assert "120 internal teeth" in text
    assert f"{schematic.params.SPUR_TEETH} teeth" in text
    assert "Ø60" in text  # ring pitch diameter
    assert f"Ø{schematic.params.SPUR_BCD_MM}" in text  # BCD callout
    assert "30°" in text  # spacing angle
    assert "<marker" in text  # arrow marker registered


def test_rack_pinion_closeup_contains_pitch_point(tmp_path: Path) -> None:
    out = tmp_path / "closeup.svg"
    schematic.rack_pinion_closeup_svg(out)
    text = out.read_text()
    assert "pitch point" in text
    assert "r = 6 mm" in text  # spur pitch radius
    assert "π·m" in text  # tooth-pitch callout
    assert "rack disengages" in text
    assert 'id="pt-active-dim"' in text


def test_rack_pinion_closeup_interactive_has_ids(tmp_path: Path) -> None:
    out = tmp_path / "closeup-interactive.svg"
    schematic.rack_pinion_closeup_svg(out, interactive=True)
    text = out.read_text()
    # Jekyll-include variant: no XML decl.
    assert not text.startswith("<?xml")
    # Stable IDs the slider needs.
    assert 'id="pt-rackpin"' in text
    assert 'id="pt-svg"' in text
    assert 'id="pt-active-dim"' in text


def test_pin_travel_diagram_shows_both_states(tmp_path: Path) -> None:
    out = tmp_path / "pintravel.svg"
    schematic.pin_travel_diagram_svg(out, ring_angle_deg=15.0)
    text = out.read_text()
    assert "at rest" in text
    assert "after 15° throw" in text
    assert "Δr = 7.85 mm" in text  # computed travel for 15° ring
    assert f"Ø{schematic.params.PIN_DIAMETER_MM}" in text
    assert "door body bore" in text
    assert "frame receiver" in text


def test_pin_play_diagram_contains_computed_callouts(tmp_path: Path) -> None:
    out = tmp_path / "pinplay.svg"
    schematic.pin_play_diagram_svg(out)
    text = out.read_text()
    assert f"Ø{schematic.params.PIN_DIAMETER_MM} pin" in text
    assert f"Ø{schematic.params.FDM_PIN_BORE_MM} bore" in text
    assert "0.2 mm radial clearance" in text
    assert "0.508 mm door-frame gap" in text
    assert "max tilt" in text
    assert "exaggerated" in text
    assert "door body" in text
    assert "frame receiver" in text


def test_new_technical_svgs_reproducible(tmp_path: Path) -> None:
    """Each new generator should produce byte-identical output across runs."""
    for name, generator in [
        ("topview", schematic.technical_top_view_svg),
        ("closeup", schematic.rack_pinion_closeup_svg),
        ("pintravel", schematic.pin_travel_diagram_svg),
        ("pinplay", schematic.pin_play_diagram_svg),
    ]:
        out1 = tmp_path / f"{name}-1.svg"
        out2 = tmp_path / f"{name}-2.svg"
        generator(out1)
        generator(out2)
        assert out1.read_bytes() == out2.read_bytes(), (
            f"{name} is not reproducible — something time-dependent crept in."
        )
