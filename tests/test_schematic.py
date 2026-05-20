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
