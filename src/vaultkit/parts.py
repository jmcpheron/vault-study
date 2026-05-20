"""Named-part extraction from STEP files.

STEP files exported from Onshape via the ST-Developer toolchain carry
their assembly tree as XCAF (eXtended CAD Application Framework) data.
The merged `STEPControl_Reader.OneShape()` used in step_io collapses
that tree into one big shape — fine for bounding boxes and triangle
counts, but useless if you want to render the ring gear and a spur
gear as separate PNGs.

`iter_named_shapes(path)` walks the XCAF document, dedupes by PRODUCT
name (Onshape labels all 12 spurs identically), and yields one
NamedShape per unique part — the right granularity for the `vaultkit
step extract` CLI and the per-part hero renders.

The walk is recursive: free shapes → components → referred unique
parts. We capture the *referred* unique part (the original geometry),
not the placed instance, so identically-named instances dedupe to one
shape.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from OCP.TopoDS import TopoDS_Shape


@dataclass(frozen=True)
class NamedShape:
    """A unique named part extracted from a STEP file.

    `name` is the PRODUCT name as it appears in the STEP file.
    `index` is the 0-based discovery order (stable across runs given the
    same file). `instance_count` is how many times this product is
    referenced across the assembly (12 for each spur in our vault).
    """

    name: str
    index: int
    shape: TopoDS_Shape
    instance_count: int


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(name: str) -> str:
    """Turn 'Spur gear (24 teeth)' into 'spur-gear-24-teeth'."""
    lowered = name.lower()
    # Special-case: 'Spur gear (24 teeth)' → 'spur-gear-24t' is more compact;
    # but stick with the generic slug for predictability.
    cleaned = _SLUG_RE.sub("-", lowered).strip("-")
    return cleaned or "unnamed"


def _label_name(label) -> str:
    """Read a TDF_Label's TDataStd_Name attribute, or return '(unnamed)'."""
    from OCP.TCollection import TCollection_ExtendedString
    from OCP.TDataStd import TDataStd_Name

    name_attr = TDataStd_Name()
    if label.FindAttribute(TDataStd_Name.GetID_s(), name_attr):
        ext = TCollection_ExtendedString()
        ext = name_attr.Get()
        return ext.ToExtString() if hasattr(ext, "ToExtString") else str(ext)
    return "(unnamed)"


def iter_named_shapes(step_path: Path) -> Iterator[NamedShape]:
    """Walk a STEP file's XCAF tree and yield one NamedShape per unique part.

    Identically-named PRODUCTs (e.g. all 12 spur gears in our vault) collapse
    to a single yield with the appropriate `instance_count`. Order is
    discovery order — assembly root first, then each unique part in the
    order encountered.
    """
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPCAFControl import STEPCAFControl_Reader
    from OCP.TCollection import TCollection_ExtendedString
    from OCP.TDF import TDF_LabelSequence
    from OCP.TDocStd import TDocStd_Document
    from OCP.XCAFApp import XCAFApp_Application
    from OCP.XCAFDoc import XCAFDoc_DocumentTool

    if not step_path.exists():
        raise FileNotFoundError(step_path)

    app = XCAFApp_Application.GetApplication_s()
    doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
    app.NewDocument(TCollection_ExtendedString("XmlOcaf"), doc)

    reader = STEPCAFControl_Reader()
    if reader.ReadFile(str(step_path)) != IFSelect_RetDone:
        raise RuntimeError(f"OCP failed to read STEP: {step_path}")
    if not reader.Transfer(doc):
        raise RuntimeError(f"OCP failed to transfer STEP into XCAF doc: {step_path}")

    shape_tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())

    # Count instances of each unique-part label across the whole assembly.
    # Walk all components recursively starting from free shapes.
    free_shapes = TDF_LabelSequence()
    shape_tool.GetFreeShapes(free_shapes)

    # Discovery: list of (name, shape, label_tag) preserving first-seen order.
    # label_tag is the unique-part label's entry string (stable identifier
    # within the doc) so we can dedupe even if names collide.
    discovered: list[tuple[str, TopoDS_Shape, str]] = []
    instance_counts: dict[str, int] = {}

    def _label_tag(label) -> str:
        from OCP.TCollection import TCollection_AsciiString
        from OCP.TDF import TDF_Tool
        entry = TCollection_AsciiString()
        TDF_Tool.Entry_s(label, entry)
        return entry.ToCString()

    def _walk(label) -> None:
        """Recurse the assembly tree from `label`."""
        if shape_tool.IsAssembly_s(label):
            components = TDF_LabelSequence()
            shape_tool.GetComponents_s(label, components)
            for i in range(1, components.Length() + 1):
                _walk(components.Value(i))
            return

        # Resolve references to their unique-part label.
        if shape_tool.IsReference_s(label):
            ref_label = label.__class__()  # empty TDF_Label
            shape_tool.GetReferredShape_s(label, ref_label)
            target_label = ref_label
        else:
            target_label = label

        tag = _label_tag(target_label)
        instance_counts[tag] = instance_counts.get(tag, 0) + 1

        # Capture the first time we see this unique-part tag.
        if tag not in {t for _, _, t in discovered}:
            shape = shape_tool.GetShape_s(target_label)
            name = _label_name(target_label)
            discovered.append((name, shape, tag))

    for i in range(1, free_shapes.Length() + 1):
        _walk(free_shapes.Value(i))

    for idx, (name, shape, tag) in enumerate(discovered):
        yield NamedShape(
            name=name,
            index=idx,
            shape=shape,
            instance_count=instance_counts.get(tag, 1),
        )
