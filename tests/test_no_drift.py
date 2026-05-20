"""specs.md ↔ params.py drift test.

Asserts that every numeric value mentioned in a `live` row of specs.md
also appears (with whole-number boundaries) in params.py. One-way check:
numbers in specs must appear in params. The reverse is fine — params
may hold derived constants or values that aren't in specs.md.

Caveats:
  * The "Derived values" section is skipped — its numbers come from
    gears.py at runtime, not from params.py constants.
  * Rows whose value cell contains strikethrough (`~~…~~`) or that have
    a Status column reading `superseded …` are skipped.
  * The check is a substring match with regex word-boundaries. It catches
    "I forgot to mirror a number into params.py" reliably. It does NOT
    catch every kind of fine-grained drift — if you change `10` to `11`
    in specs.md and forget to update params.py, the test may still pass
    if `10` happens to appear elsewhere in params.py. For now, eyes-on
    review covers that gap. A future enhancement (deferred): a per-row
    key column that maps each specs row to its params constant by name.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS_PATH = REPO_ROOT / "specs.md"
PARAMS_PATH = REPO_ROOT / "src" / "vaultkit" / "params.py"

# Match a numeric token: integer or decimal, optional leading sign, no
# surrounding digits. Excludes things like 0.0125 if we wanted to (we
# don't — values up to 4 decimal places are fair game).
NUMBER_RE = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])")

# Values that appear in specs.md but aren't expected to be canonical
# constants in params.py. Document the reason for each exemption.
EXEMPT_VALUES = {
    # Source-tag part numbers ([part-1] .. [part-5]) + ratio-related digits
    "1", "2", "3", "4", "5", "10",
    # Year mentioned in source URLs / log headings
    "2026",
    # 360° denominator in derivations
    "360",
    # Material-grade callouts — informational, not modeled in CAD
    "416",   # 416 stainless (ring gear, Adam's build only)
    "6061",  # 6061 aluminum (door frame)
    # Range/approximation parts that aren't the canonical value
    "15",    # "15–20 lb" weight target — range, not a parameter
    "2.4",   # "≈ 2.4 in" — parenthetical approximation of RING_OD_IN = 2.401
    "25",    # "(25 thousandths)" — unit restatement of 0.025 in
}


def _strip_skipped_sections(text: str) -> str:
    """Return specs.md text with the 'Derived values' section removed."""
    lines = text.splitlines()
    out: list[str] = []
    skipping = False
    for line in lines:
        if line.startswith("## Derived values"):
            skipping = True
            continue
        if skipping and line.startswith("## "):
            skipping = False
        if not skipping:
            out.append(line)
    return "\n".join(out)


def _is_table_data_row(line: str) -> bool:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return False
    # Skip header separator like `| --- | --- |`
    if set(stripped.replace("|", "").replace(" ", "").replace(":", "")) <= {"-"}:
        return False
    # Skip header row (heuristic: contains "Parameter" or "Value" or "Source")
    if "Parameter" in stripped and "Value" in stripped:
        return False
    return True


def _is_superseded_row(line: str) -> bool:
    # Row is superseded if its value cell uses strikethrough, or status reads "superseded"
    return "~~" in line or "superseded" in line.lower()


def _extract_numbers_from_specs(text: str) -> set[str]:
    text = _strip_skipped_sections(text)
    found: set[str] = set()
    for line in text.splitlines():
        if not _is_table_data_row(line):
            continue
        if _is_superseded_row(line):
            continue
        for match in NUMBER_RE.finditer(line):
            found.add(match.group(1))
    return found - EXEMPT_VALUES


def _params_contains_number(params_text: str, value: str) -> bool:
    """True if `value` appears in params.py with non-digit, non-dot boundaries."""
    pattern = re.compile(rf"(?<![\w.]){re.escape(value)}(?![\w.])")
    return bool(pattern.search(params_text))


def test_specs_numbers_appear_in_params() -> None:
    specs_text = SPECS_PATH.read_text()
    params_text = PARAMS_PATH.read_text()
    spec_values = _extract_numbers_from_specs(specs_text)

    missing = sorted(
        v for v in spec_values if not _params_contains_number(params_text, v)
    )
    assert not missing, (
        f"specs.md mentions these numeric values but params.py does not: "
        f"{missing}. Either mirror them into src/vaultkit/params.py or add "
        f"them to EXEMPT_VALUES in this test with a comment explaining why."
    )
