"""Tests for vaultkit.release.

The description/listing layer is pure text derived from params.py, so these
run on a light install (no OpenCascade) and assert determinism plus that the
framing, attribution, and license always survive into the output. The actual
bundle build (STL tessellation) is slow and OCP-bound, so it's gated behind
VAULTKIT_SLOW_TESTS=1, like the scad end-to-end tests.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from vaultkit import params, release

VARIANTS = ["fdm", "faithful"]


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("platform", release.PLATFORMS)
def test_describe_is_deterministic(variant: str, platform: str) -> None:
    assert release.describe(variant, platform) == release.describe(variant, platform)


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("platform", release.PLATFORMS)
def test_describe_has_attribution_and_license(variant: str, platform: str) -> None:
    text = release.describe(variant, platform)
    assert "Adam Savage" in text
    # The repo's recurring attribution phrase — must always make it in.
    assert "educational and hobby" in text
    assert "CC BY-SA 4.0" in text
    assert release.REPO_URL in text
    assert params.ONSHAPE[variant].permalink in text


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("platform", release.PLATFORMS)
def test_describe_threads_the_framing(variant: str, platform: str) -> None:
    text = release.describe(variant, platform)
    assert "Vault Study" in text  # umbrella name
    assert "lathe" in text  # the lathe → flatbed hook
    # Spec table is derived from params — the gear numbers must appear.
    assert str(params.RING_TEETH) in text
    assert str(params.SPUR_TEETH) in text


def test_fdm_description_mentions_flatbed_and_print_settings() -> None:
    text = release.describe("fdm", "printables")
    assert "flatbed" in text
    assert "Layer height" in text
    assert params.PRINT_SETTINGS["fdm"]["material_mechanism"] in text


def test_faithful_description_points_to_fdm_for_printing() -> None:
    text = release.describe("faithful", "printables")
    assert "FDM variant" in text
    # No print-settings block on the CAD-reference listing.
    assert "Layer height" not in text


def test_describe_rejects_unknown_inputs() -> None:
    with pytest.raises(ValueError):
        release.describe("nope", "printables")
    with pytest.raises(ValueError):
        release.describe("fdm", "thingiverse")


@pytest.mark.parametrize("variant", VARIANTS)
def test_listing_sheet_blocks(variant: str) -> None:
    sheet = release.listing_sheet(variant)
    for block in ("TITLE", "SUMMARY", "TAGS", "LICENSE"):
        assert block in sheet
    assert "DESCRIPTION (Printables" in sheet
    assert "DESCRIPTION (MakerWorld" in sheet
    # Print settings only on the FDM (print-targeted) sheet.
    assert ("PRINT SETTINGS" in sheet) == (variant == "fdm")


def test_text_only_build_is_base_install_safe(tmp_path: Path) -> None:
    """All geometry skipped → no OCP import, just the listing files + license."""
    dest = release.build_bundle(
        "fdm",
        tmp_path,
        skip_stl=True,
        skip_parts=True,
        skip_anim=True,
        make_zip=False,
    )
    assert (dest / "LISTING.md").is_file()
    assert (dest / "description-printables.md").is_file()
    assert (dest / "description-makerworld.txt").is_file()
    assert (dest / "print-settings.txt").is_file()
    assert (dest / "LICENSE-3D-FILES").is_file()
    assert not list(dest.glob("*.stl"))  # nothing tessellated


# ── Slow end-to-end build (OCP STEP tessellation) ───────────────────────

SLOW_TESTS_ENABLED = os.environ.get("VAULTKIT_SLOW_TESTS") == "1"


@pytest.mark.skipif(
    not SLOW_TESTS_ENABLED,
    reason="OCP STEP tessellation; enable with VAULTKIT_SLOW_TESTS=1",
)
def test_build_bundle_fdm_produces_stl_and_cover(tmp_path: Path) -> None:
    dest = release.build_bundle(
        "fdm",
        tmp_path,
        skip_parts=True,
        skip_anim=True,
        make_zip=False,
    )
    stl = dest / "fdm-vault.stl"
    assert stl.is_file() and stl.stat().st_size > 1000
    assert (dest / "renders" / "fdm.iso.png").is_file()
