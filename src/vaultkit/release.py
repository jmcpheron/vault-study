"""Release-bundle builder — turn a variant's STEP into upload-ready files.

Two layers, deliberately separated:

  * **Description text** (base-install-safe — no OCP). `describe()` and
    `listing_sheet()` pull the gear math from params.py and emit per-platform
    copy-paste blocks. These run on a light `pip install -e "."`.
  * **The bundle** (`build_bundle`) — STLs, a cover render, the animation, the
    license, and a zip. The geometry steps lazy-import mesh/parts/scad (the
    `[heavy]` extras) only when they actually run, so a text-only build still
    works without OpenCascade.

Neither Printables nor MakerWorld has an upload API and both block bots, so
this module stops at *producing* the files. Uploading stays manual (with an
optional headed-browser pre-fill living in vaultkit.capture — not here).

Framing is locked in params.RELEASE_TITLES and the helpers below: "Vault
Study," study-not-tribute, the lathe→flatbed translation as the hook, and the
watch → print → learn ladder as the spine. Credit for the design is Adam
Savage's throughout.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from vaultkit import params

REPO_URL = "https://github.com/jmcpheron/vault-study"
DOCS_URL = "https://jmcpheron.github.io/vault-study"
INTERACTIVE_URL = f"{DOCS_URL}/interactive.html"
TESTED_URL = "https://www.tested.com/"
LICENSE_NAME = "CC BY-SA 4.0"
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"

# Repo root: src/vaultkit/release.py → parents[2] == the repo. Inputs (STEP,
# license) resolve against this; output dirs resolve against the caller's cwd.
REPO_ROOT = Path(__file__).resolve().parents[2]

PLATFORMS = ("printables", "makerworld")


# ── content pieces (shared by both platforms) ────────────────────────────


def _summary(variant: str) -> str:
    if variant == "fdm":
        return (
            "An FDM-printable take on Adam Savage's 1/12-scale mechanical "
            "vault door — turn one dial and twelve pins shoot home in unison."
        )
    return (
        "A faithful CAD study of Adam Savage's machined 1/12-scale vault "
        "door — the reference reproduction, built to understand the mechanism."
    )


def _hook(variant: str) -> str:
    if variant == "fdm":
        return (
            "Adam Savage built this vault door the machinist's way — turned on "
            "a lathe, cut from round metal stock, held to machine-shop "
            "tolerances. This is the same mechanism translated into the 3D "
            "printer's idiom: parts that lie flat on the bed, hex stock where "
            "the original used round (anti-rotation without keyways), and "
            "clearances loosened to numbers an FDM printer can actually hit. "
            "Same 120/24 gear math, same twelve pins — different manufacturing "
            "language."
        )
    return (
        "A faithful CAD reinterpretation of the machined vault door Adam "
        "Savage built on Tested: same dimensions, same gear math, same "
        "combination-lock gatekeeper. This is the reference study — the "
        "lathe-turned original rebuilt parametrically to understand how it "
        "works. To print one at home, see the FDM variant."
    )


def _ladder(variant: str) -> list[tuple[str, str]]:
    """The watch → print → learn rungs, as (label, detail) pairs."""
    onshape = params.ONSHAPE[variant].permalink
    if variant == "fdm":
        print_rung = "the STL files in this bundle (recommended settings below)"
    else:
        print_rung = f"the FDM variant, redesigned for home printers — {REPO_URL}"
    return [
        ("Watch it work", f"the interactive explainer, no printer needed — {INTERACTIVE_URL}"),
        ("Print one", print_rung),
        ("Learn the CAD", f"the parametric Onshape document — {onshape}"),
    ]


def _spec_rows() -> list[tuple[str, str]]:
    ratio = params.RING_TEETH // params.SPUR_TEETH
    return [
        ("Scale", "1/12 of a real vault door"),
        ("Ring gear", f"{params.RING_TEETH} teeth, module {params.MODULE_MM} mm"),
        ("Spur gears", f"{params.SPUR_COUNT} × {params.SPUR_TEETH} teeth"),
        ("Drive ratio", f"{ratio} : 1 (ring → spur)"),
        (
            "Locking pins",
            f"{params.PIN_COUNT} × Ø{params.PIN_DIAMETER_MM} mm × "
            f"{params.PIN_LENGTH_MM} mm",
        ),
    ]


def _tags(variant: str) -> list[str]:
    common = [
        "vault", "vault-door", "mechanical", "gears", "rack-and-pinion",
        "mechanism", "adam-savage", "tested", "miniature",
    ]
    if variant == "fdm":
        return [*common, "fdm", "functional", "no-supports", "petg"]
    return [*common, "cad", "onshape", "reference"]


def _print_settings_lines() -> list[str]:
    s = params.PRINT_SETTINGS["fdm"]
    return [
        f"Layer height: {s['layer_height_mm']} mm",
        f"Wall loops: {s['wall_loops']} (on the geared parts)",
        f"Supports: {s['supports']}",
        (
            f"Material: {s['material_mechanism']} for the mechanism, "
            f"{s['material_cosmetic']} for cosmetic parts"
        ),
    ]


def _attribution_lines(variant: str) -> list[str]:
    onshape = params.ONSHAPE[variant].permalink
    return [
        (
            "Mechanism design, proportions, and gear math are Adam Savage's, "
            f"shown on his Tested YouTube series ({TESTED_URL}). This is an "
            "independent CAD reinterpretation for educational and hobby "
            "purposes — credit for the design is entirely his."
        ),
        f"Source repository (parametric CAD, build notes, math): {REPO_URL}",
        f"Onshape document (the live parametric model): {onshape}",
    ]


def _license_line() -> str:
    return (
        f"3D files licensed {LICENSE_NAME} ({LICENSE_URL}) — remix and share "
        "freely, keep the attribution and the same license."
    )


# ── per-platform formatters ──────────────────────────────────────────────


def _printables_md(variant: str) -> str:
    """Full-Markdown body for Printables (headings, a table, bullet lists)."""
    lines = [
        f"# {params.RELEASE_TITLES[variant]}",
        "",
        _summary(variant),
        "",
        _hook(variant),
        "",
        "## Three ways in",
        "",
    ]
    for i, (label, detail) in enumerate(_ladder(variant), 1):
        lines.append(f"{i}. **{label}** — {detail}")
    lines += ["", "## The mechanism", "", "| | |", "| --- | --- |"]
    lines += [f"| {k} | {v} |" for k, v in _spec_rows()]
    if variant == "fdm":
        lines += ["", "## Recommended print settings", ""]
        lines += [f"- {ln}" for ln in _print_settings_lines()]
    lines += ["", "## Credit & license", ""]
    lines += [f"- {ln}" for ln in _attribution_lines(variant)]
    lines += ["", _license_line()]
    return "\n".join(lines)


def _makerworld_txt(variant: str) -> str:
    """Plain-text body for MakerWorld (no tables; UPPERCASE section labels)."""
    lines = [
        params.RELEASE_TITLES[variant],
        "",
        _summary(variant),
        "",
        _hook(variant),
        "",
        "THREE WAYS IN",
    ]
    for i, (label, detail) in enumerate(_ladder(variant), 1):
        lines.append(f"  {i}. {label}: {detail}")
    lines += ["", "THE MECHANISM"]
    lines += [f"  {k}: {v}" for k, v in _spec_rows()]
    if variant == "fdm":
        lines += ["", "RECOMMENDED PRINT SETTINGS"]
        lines += [f"  {ln}" for ln in _print_settings_lines()]
    lines += ["", "CREDIT & LICENSE"]
    lines += [f"  {ln}" for ln in _attribution_lines(variant)]
    lines += ["", _license_line()]
    return "\n".join(lines)


# ── public API ───────────────────────────────────────────────────────────


def describe(variant: str, platform: str) -> str:
    """Return the listing description for a variant on a given platform."""
    if variant not in params.RELEASE_TITLES:
        raise ValueError(f"unknown variant: {variant!r}")
    if platform == "printables":
        return _printables_md(variant)
    if platform == "makerworld":
        return _makerworld_txt(variant)
    raise ValueError(f"unknown platform: {platform!r} (expected one of {PLATFORMS})")


def _block(name: str, body: str) -> str:
    return f"================= {name} =================\n{body}\n"


def listing_sheet(variant: str) -> str:
    """One sheet with every field blocked out for copy-paste into either site."""
    title = params.RELEASE_TITLES[variant]
    out = [
        f"# Listing sheet — {title}",
        "# Copy each block into the matching field on Printables / MakerWorld.",
        "# Both descriptions say the same thing; use the one that matches the site.",
        "",
        _block("TITLE", title),
        _block("SUMMARY / TAGLINE", _summary(variant)),
        _block("TAGS", ", ".join(_tags(variant))),
    ]
    if variant == "fdm":
        out.append(_block("PRINT SETTINGS", "\n".join(_print_settings_lines())))
    out += [
        _block("DESCRIPTION (Printables — Markdown)", _printables_md(variant)),
        _block("DESCRIPTION (MakerWorld — plain text)", _makerworld_txt(variant)),
        _block("LICENSE", _license_line()),
    ]
    return "\n".join(out)


def build_bundle(
    variant: str,
    out_dir: Path,
    *,
    skip_stl: bool = False,
    skip_parts: bool = False,
    skip_anim: bool = False,
    make_zip: bool = True,
    deflection: float = 0.3,
) -> Path:
    """Assemble a variant's upload bundle under `out_dir/<variant>/`.

    Writes the listing text + license unconditionally (base-install-safe), then
    the geometry (STL, per-part STLs, cover render, FDM animation) unless the
    matching `skip_*` flag is set. Returns the zip path if `make_zip`, else the
    bundle directory. The geometry steps need the `[heavy]` extras; a build with
    all three `skip_*` flags is text-only and runs on a light install.
    """
    if variant not in params.VARIANTS:
        raise ValueError(f"unknown variant: {variant!r}")

    out_dir = Path(out_dir)
    dest = out_dir / variant
    (dest / "renders").mkdir(parents=True, exist_ok=True)

    # --- listing text + license (no OCP) ---
    (dest / "LISTING.md").write_text(listing_sheet(variant))
    (dest / "description-printables.md").write_text(_printables_md(variant))
    (dest / "description-makerworld.txt").write_text(_makerworld_txt(variant))
    if variant == "fdm":
        (dest / "print-settings.txt").write_text(
            "\n".join(_print_settings_lines()) + "\n"
        )

    license_src = REPO_ROOT / "LICENSE-3D-FILES"
    if license_src.exists():
        shutil.copy2(license_src, dest / "LICENSE-3D-FILES")

    # --- geometry (lazy-imports the heavy CAD stack only if a step runs) ---
    step_path = REPO_ROOT / params.VARIANTS[variant]
    wants_geometry = not (skip_stl and skip_parts and skip_anim)
    if wants_geometry:
        from vaultkit import mesh, parts, scad

        if not skip_stl:
            mesh.step_to_stl(
                step_path, dest / f"{variant}-vault.stl", deflection_mm=deflection
            )

        if not skip_parts:
            parts_dir = dest / "parts"
            parts_dir.mkdir(exist_ok=True)
            for named in parts.iter_named_shapes(step_path):
                slug = parts.slugify(named.name)
                mesh.shape_to_stl(
                    named.shape,
                    parts_dir / f"{slug}-{named.index}.stl",
                    deflection_mm=deflection,
                )

        # Cover render always goes with a geometry build (the listing needs an image).
        mesh.render_iso(
            step_path,
            dest / "renders" / f"{variant}.iso.png",
            deflection_mm=deflection,
            edge_width=0.08,
            edge_color="#888a8c",
            face_color="#e1e3e6",
        )

        # OpenSCAD animation — FDM only (the faithful STEP lacks racks + pins).
        if not skip_anim and variant == "fdm":
            gif = dest / "renders" / "cam-sweep.gif"
            scad.render_cam_sweep(step_path, gif, out_webp=gif.with_suffix(".webp"))

    if make_zip:
        archive = shutil.make_archive(
            str(out_dir / f"{variant}-vault"), "zip", root_dir=dest
        )
        return Path(archive)
    return dest
