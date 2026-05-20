"""Mesh operations — STL/3MF writing, exploded-view layout, hero renders.

Stub. Heavy dependencies: trimesh, matplotlib. The eventual API mirrors
`cardlab explode` and `cardlab render` from the sibling pycon2026 repo:

    def explode(parts: list[Part], *, factor: float = 1.5) -> trimesh.Scene
    def render_iso(scene, out: Path, size: tuple[int, int] = (1200, 1200)) -> None
    def render_gif(scene, out: Path, frames: int = 36) -> None
"""

from __future__ import annotations


def explode(*args, **kwargs) -> None:
    raise NotImplementedError("mesh.explode is a stub.")


def render_iso(*args, **kwargs) -> None:
    raise NotImplementedError("mesh.render_iso is a stub.")
