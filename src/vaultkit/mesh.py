"""Mesh operations — STEP→STL conversion + matplotlib iso renders.

`render_iso(step_path, out_png)` is the hero-render entry point used by
the explainer pages. STEP → OCP tessellation → temporary STL → trimesh
load → matplotlib 3D Poly3DCollection → PNG. Headless-friendly: uses
matplotlib's Agg backend, no OpenGL required.

The output is intentionally simple: light-grey faces, thin black edges,
isometric view (35.264° elev, 45° azim), equal aspect ratio, no axes.
"""

from __future__ import annotations

import tempfile
from pathlib import Path


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


def render_iso(
    step_path: Path,
    out_png: Path,
    *,
    deflection_mm: float = 0.3,
    size_px: tuple[int, int] = (1200, 1200),
    face_color: str = "#d8d8da",
    edge_color: str = "#222222",
    edge_width: float = 0.15,
    background: str = "white",
    elevation_deg: float = 35.264,  # classic isometric
    azimuth_deg: float = 45.0,
) -> None:
    """Render a STEP file as an isometric PNG.

    Uses matplotlib's mpl_toolkits.mplot3d.Poly3DCollection — slow but
    reliable and headless. Intended for hero/comparison images, not for
    interactive viewing. If you need lots of frames or a GIF, swap this
    for trimesh.Scene.save_image (pyglet) or OpenSCAD orthographic
    renders.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import trimesh
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    out_png.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        step_to_stl(step_path, tmp_path, deflection_mm=deflection_mm)
        mesh = trimesh.load(tmp_path, force="mesh")
    finally:
        tmp_path.unlink(missing_ok=True)

    if not isinstance(mesh, trimesh.Trimesh):
        raise RuntimeError(f"trimesh did not return a Trimesh from {step_path}")

    dpi = 100
    fig = plt.figure(
        figsize=(size_px[0] / dpi, size_px[1] / dpi),
        dpi=dpi,
        facecolor=background,
    )
    ax = fig.add_subplot(111, projection="3d", facecolor=background)

    # Build triangle vertex array: (n_faces, 3, 3) — n triangles, 3 vertices, xyz.
    triangles = mesh.vertices[mesh.faces]
    collection = Poly3DCollection(
        triangles,
        facecolor=face_color,
        edgecolor=edge_color,
        linewidths=edge_width,
    )
    ax.add_collection3d(collection)

    # Equal-aspect bounding cube around the geometry.
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

    # set_box_aspect locks the cube proportions in modern matplotlib.
    ax.set_box_aspect((1, 1, 1))

    fig.tight_layout(pad=0)
    fig.savefig(out_png, dpi=dpi, bbox_inches="tight", pad_inches=0.1,
                facecolor=background)
    plt.close(fig)


def explode(*args, **kwargs) -> None:
    """Exploded-view layout. Not yet implemented."""
    raise NotImplementedError("mesh.explode is still a stub.")
