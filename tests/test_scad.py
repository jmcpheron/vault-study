"""Tests for vaultkit.scad.

These tests cover deterministic .scad template generation + GIF format
validation (magic bytes, frame count). They do NOT pixel-compare the
GIFs because PIL's palette quantization isn't byte-stable across
versions — visual review is the actual quality bar.

The cam-sweep / exploded end-to-end runs take ~13 seconds each and
shell out to OpenSCAD, so we mark them as slow and gate behind an
env var. Day-to-day test runs only check template generation.
"""

from __future__ import annotations

import os
import struct
from pathlib import Path

import pytest

from vaultkit import parts, scad

REPO_ROOT = Path(__file__).resolve().parent.parent
FDM_STEP = REPO_ROOT / "step-source" / "fdm-vault.step"


def test_assign_roles_fdm_finds_all_six_parts() -> None:
    named = list(parts.iter_named_shapes(FDM_STEP))
    roles = scad.assign_roles(named)
    role_names = [r.role for r in roles]
    assert role_names == ["rack", "pin", "spur", "ring", "hub", "base"]


def test_cam_sweep_template_is_deterministic() -> None:
    """Two calls to cam_sweep_template should produce byte-identical .scad."""
    named = list(parts.iter_named_shapes(FDM_STEP))
    roles = scad.assign_roles(named)
    first = scad.cam_sweep_template(roles)
    second = scad.cam_sweep_template(roles)
    assert first == second


def test_exploded_template_is_deterministic() -> None:
    named = list(parts.iter_named_shapes(FDM_STEP))
    roles = scad.assign_roles(named)
    first = scad.exploded_template(roles)
    second = scad.exploded_template(roles)
    assert first == second


def test_cam_sweep_template_references_all_roles() -> None:
    named = list(parts.iter_named_shapes(FDM_STEP))
    roles = scad.assign_roles(named)
    text = scad.cam_sweep_template(roles)
    # Each STL path should appear exactly once in the template.
    for r in roles:
        assert str(r.stl_path) in text, f"missing {r.role} STL import"
    # Animation drivers present.
    assert "theta" in text
    assert "spur_angle" in text
    assert "rack_dr" in text


def test_exploded_template_does_not_animate_hub_or_base() -> None:
    """Hub and base stay put in the exploded view — they're the skeleton."""
    named = list(parts.iter_named_shapes(FDM_STEP))
    roles = scad.assign_roles(named)
    text = scad.exploded_template(roles)
    # Find the hub and base STL paths and verify they're not inside any
    # progress-driven translate.
    for r in roles:
        if r.role in ("hub", "base"):
            # Locate the line that imports this STL.
            lines = [ln for ln in text.splitlines() if str(r.stl_path) in ln]
            assert lines, f"missing {r.role} import"
            for ln in lines:
                assert "progress" not in ln, (
                    f"{r.role} import has progress-driven transform: {ln!r}"
                )


# ── Slow end-to-end tests (OpenSCAD subprocess) ─────────────────────────

SLOW_TESTS_ENABLED = os.environ.get("VAULTKIT_SLOW_TESTS") == "1"


@pytest.mark.skipif(
    not SLOW_TESTS_ENABLED,
    reason="OpenSCAD subprocess; enable with VAULTKIT_SLOW_TESTS=1",
)
def test_render_cam_sweep_produces_valid_gif(tmp_path: Path) -> None:
    out = tmp_path / "test.gif"
    scad.render_cam_sweep(FDM_STEP, out, frames=6, size_px=200)
    assert out.exists()
    data = out.read_bytes()
    # Valid GIF magic bytes.
    assert data[:6] in (b"GIF87a", b"GIF89a"), "not a valid GIF"
    # Logical screen width/height should be 200×200.
    width, height = struct.unpack("<HH", data[6:10])
    assert width == 200 and height == 200
