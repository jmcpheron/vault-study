"""Mesh operations — STEP→STL conversion + matplotlib iso renders.

`render_iso(step_path, out_png)` is the hero-render entry point for the
"whole assembly" case; `render_iso_shape(shape, out_png)` is the
shape-aware variant used by vaultkit.parts when rendering individual
named PRODUCTs. Both share `_shape_to_trimesh` and a single matplotlib
3D rendering function.

STEP/shape → OCP tessellation → temporary STL → trimesh load →
matplotlib 3D Poly3DCollection → PNG. Headless-friendly: matplotlib's
Agg backend, no OpenGL required.

Output style is intentionally simple: light-grey faces, thin grey edges,
isometric view (35.264° elev, 45° azim), equal aspect ratio, no axes.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import trimesh
    from OCP.TopoDS import TopoDS_Shape


def step_to_stl(step_path: Path, stl_path: Path, *, deflection_mm: float = 0.3) -> None:
    """Tessellate a STEP file and write the result to STL."""
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_Reader
    from OCP.StlAPI import StlAPI_Writer

    reader = STEPControl_Reader()
    if reader.ReadFile(str(step_path)) != IFSelect_RetDone:
        raise RuntimeError(f"OCP failed to read STEP: {step_path}")
    reader.TransferRoots()
    shape = reader.OneShape()

    BRepMesh_IncrementalMesh(shape, deflection_mm, False, 0.5, True)

    writer = StlAPI_Writer()
    writer.ASCIIMode = False
    if not writer.Write(shape, str(stl_path)):
        raise RuntimeError(f"OCP failed to write STL: {stl_path}")


def shape_to_stl(
    shape: TopoDS_Shape, stl_path: Path, *, deflection_mm: float = 0.3
) -> None:
    """Tessellate a TopoDS_Shape (already loaded) and write to STL."""
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.StlAPI import StlAPI_Writer

    BRepMesh_IncrementalMesh(shape, deflection_mm, False, 0.5, True)

    writer = StlAPI_Writer()
    writer.ASCIIMode = False
    if not writer.Write(shape, str(stl_path)):
        raise RuntimeError(f"OCP failed to write STL: {stl_path}")


def _shape_to_trimesh(
    shape_or_path: TopoDS_Shape | Path, deflection_mm: float
) -> trimesh.Trimesh:
    """Tessellate a STEP path or TopoDS_Shape via OCP and return a Trimesh."""
    import trimesh as _trimesh

    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        if isinstance(shape_or_path, Path):
            step_to_stl(shape_or_path, tmp_path, deflection_mm=deflection_mm)
        else:
            shape_to_stl(shape_or_path, tmp_path, deflection_mm=deflection_mm)
        mesh = _trimesh.load(tmp_path, force="mesh")
    finally:
        tmp_path.unlink(missing_ok=True)

    if not isinstance(mesh, _trimesh.Trimesh):
        raise RuntimeError("trimesh did not return a Trimesh from the input")
    return mesh


def _render_mesh_iso(
    mesh: trimesh.Trimesh,
    out_png: Path,
    *,
    size_px: tuple[int, int],
    face_color: str,
    edge_color: str,
    edge_width: float,
    background: str,
    elevation_deg: float,
    azimuth_deg: float,
) -> None:
    """Render a Trimesh as an iso PNG via matplotlib 3D."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    out_png.parent.mkdir(parents=True, exist_ok=True)

    dpi = 100
    fig = plt.figure(
        figsize=(size_px[0] / dpi, size_px[1] / dpi),
        dpi=dpi,
        facecolor=background,
    )
    ax = fig.add_subplot(111, projection="3d", facecolor=background)

    triangles = mesh.vertices[mesh.faces]
    collection = Poly3DCollection(
        triangles,
        facecolor=face_color,
        edgecolor=edge_color,
        linewidths=edge_width,
    )
    ax.add_collection3d(collection)

    bb_min = mesh.vertices.min(axis=0)
    bb_max = mesh.vertices.max(axis=0)
    extents = bb_max - bb_min
    center = (bb_min + bb_max) / 2
    radius = float(np.max(extents)) / 2 * 1.05
    ax.set_xlim(center[0] - radius, center[0] + radius)
    ax.set_ylim(center[1] - radius, center[1] + radius)
    ax.set_zlim(center[2] - radius, center[2] + radius)

    ax.set_axis_off()
    ax.view_init(elev=elevation_deg, azim=azimuth_deg)
    ax.set_box_aspect((1, 1, 1))

    fig.tight_layout(pad=0)
    fig.savefig(
        out_png, dpi=dpi, bbox_inches="tight", pad_inches=0.1, facecolor=background
    )
    plt.close(fig)


def render_iso(
    step_path: Path,
    out_png: Path,
    *,
    deflection_mm: float = 0.3,
    size_px: tuple[int, int] = (1200, 1200),
    face_color: str = "#e1e3e6",
    edge_color: str = "#888a8c",
    edge_width: float = 0.08,
    background: str = "white",
    elevation_deg: float = 35.264,
    azimuth_deg: float = 45.0,
) -> None:
    """Render a STEP file as an isometric PNG (whole-assembly hero render)."""
    mesh = _shape_to_trimesh(step_path, deflection_mm)
    _render_mesh_iso(
        mesh,
        out_png,
        size_px=size_px,
        face_color=face_color,
        edge_color=edge_color,
        edge_width=edge_width,
        background=background,
        elevation_deg=elevation_deg,
        azimuth_deg=azimuth_deg,
    )


def render_iso_shape(
    shape: TopoDS_Shape,
    out_png: Path,
    *,
    deflection_mm: float = 0.3,
    size_px: tuple[int, int] = (1200, 1200),
    face_color: str = "#e1e3e6",
    edge_color: str = "#888a8c",
    edge_width: float = 0.08,
    background: str = "white",
    elevation_deg: float = 35.264,
    azimuth_deg: float = 45.0,
) -> None:
    """Render a TopoDS_Shape (already extracted) as an isometric PNG."""
    mesh = _shape_to_trimesh(shape, deflection_mm)
    _render_mesh_iso(
        mesh,
        out_png,
        size_px=size_px,
        face_color=face_color,
        edge_color=edge_color,
        edge_width=edge_width,
        background=background,
        elevation_deg=elevation_deg,
        azimuth_deg=azimuth_deg,
    )


def explode(*args, **kwargs) -> None:
    """Exploded-view layout. Not yet implemented."""
    raise NotImplementedError("mesh.explode is still a stub.")
