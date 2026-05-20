"""Tests for vaultkit.parts."""

from __future__ import annotations

from pathlib import Path

from vaultkit.parts import iter_named_shapes, slugify

REPO_ROOT = Path(__file__).resolve().parent.parent
FAITHFUL_STEP = REPO_ROOT / "step-source" / "unauthorized-vault-clone.step"
FDM_STEP = REPO_ROOT / "step-source" / "fdm-vault.step"


def test_slugify() -> None:
    assert slugify("Spur gear (24 teeth)") == "spur-gear-24-teeth"
    assert slugify("Part 1") == "part-1"
    assert slugify("  Funky—Name (v2.0)  ") == "funky-name-v2-0"
    assert slugify("!!!") == "unnamed"


def test_iter_named_shapes_faithful() -> None:
    """The faithful STEP file should yield four unique parts."""
    named = list(iter_named_shapes(FAITHFUL_STEP))
    assert len(named) == 4, f"expected 4 unique parts, got {len(named)}"
    names = [n.name for n in named]
    assert "Spur gear (120 teeth)" in names
    assert "Spur gear (24 teeth)" in names
    assert names.count("Part 1") == 2  # body + one other singleton

    # Instance counts: 12 satellites + 12 of one Part 1 + 1 ring + 1 hub = 26
    total_instances = sum(n.instance_count for n in named)
    assert total_instances == 26


def test_iter_named_shapes_fdm() -> None:
    """The FDM STEP file should yield six unique parts."""
    named = list(iter_named_shapes(FDM_STEP))
    assert len(named) == 6, f"expected 6 unique parts, got {len(named)}"

    # Indices are stable across runs.
    indices = [n.index for n in named]
    assert indices == sorted(indices)
    assert indices == list(range(len(named)))

    # 12 satellites + 12 racks + 12 pins + 1 ring + 1 hub + 1 base = 39
    total_instances = sum(n.instance_count for n in named)
    assert total_instances == 39


def test_iter_named_shapes_deterministic() -> None:
    """Two passes over the same file should yield identical name/index pairs."""
    first = [(n.name, n.index, n.instance_count) for n in iter_named_shapes(FDM_STEP)]
    second = [(n.name, n.index, n.instance_count) for n in iter_named_shapes(FDM_STEP)]
    assert first == second
