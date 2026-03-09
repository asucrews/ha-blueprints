#!/usr/bin/env python3
"""
Cross-check blueprint YAML versions against the compatibility matrix in
docs/blueprints/README.md.

Checks:
  - Every matrix row has a findable blueprint YAML under blueprints/.
  - Every blueprint YAML has a detectable version string.
  - The blueprint version matches the matrix version.
  - Every blueprint YAML appears in the matrix (no orphan blueprints).

Exit 0 on pass, 1 on any failure.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLUEPRINTS_DIR = ROOT / "blueprints"
DOCS_INDEX = ROOT / "docs" / "blueprints" / "README.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def is_blueprint_yaml(text: str) -> bool:
    return bool(re.search(r"(?m)^blueprint:\s*$", text))


def parse_matrix(text: str) -> dict[str, str]:
    """Return {yaml_filename: version_string} from the compatibility matrix.

    Expects rows like:
      | `witb_plus.yaml` | automation | `v4.2.0` | `2026.2.0` | `witb_plus.md` |

    Returned version strings are normalized (leading 'v' stripped).
    """
    rows: dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(
            r"\|\s*`([^`]+\.yaml)`\s*\|\s*\w+\s*\|\s*`v?([^`]+)`\s*\|",
            line,
        )
        if m:
            rows[m.group(1)] = m.group(2).strip()
    return rows


def extract_name_field(text: str) -> str:
    """Extract the blueprint-level 'name:' field (2-space-indented, direct child of blueprint:).

    Input-level name fields are indented much deeper and must not be matched.
    """
    # Single-quoted
    m = re.search(r"^  name:\s*'([^']*)'\s*$", text, re.MULTILINE)
    if m:
        return m.group(1)
    # Double-quoted
    m = re.search(r'^  name:\s*"([^"]*)"\s*$', text, re.MULTILINE)
    if m:
        return m.group(1)
    # Unquoted (rest of line)
    m = re.search(r"^  name:\s*(.+?)\s*$", text, re.MULTILINE)
    if m:
        return m.group(1)
    return ""


def extract_blueprint_version(text: str) -> str | None:
    """Return the blueprint version as a normalized string (no leading 'v'), or None.

    Strategy:
      1. Explicit 'Version: X.Y.Z' tag in the description block.
      2. Version pattern 'vX[.Y[.Z]]' embedded in the name field.
    """
    # 1. Explicit tag in description
    m = re.search(r"Version:\s*(\d[\d.]*)", text)
    if m:
        return m.group(1).rstrip(".")

    # 2. Version in name field
    name = extract_name_field(text)
    if name:
        m = re.search(r"\bv(\d+(?:\.\d+)*)\b", name, re.IGNORECASE)
        if m:
            return m.group(1)

    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    errors: list[str] = []

    if not DOCS_INDEX.exists():
        print(f"ERROR: Docs index not found: {DOCS_INDEX.relative_to(ROOT)}")
        return 1

    matrix = parse_matrix(read_text(DOCS_INDEX))
    if not matrix:
        print("ERROR: No rows parsed from the compatibility matrix.")
        return 1

    # Discover all blueprint YAML files
    blueprint_map: dict[str, tuple[Path, str]] = {}
    for path in BLUEPRINTS_DIR.rglob("*.yaml"):
        text = read_text(path)
        if is_blueprint_yaml(text):
            blueprint_map[path.name] = (path, text)

    # Check each matrix row
    for filename, matrix_version in matrix.items():
        if filename not in blueprint_map:
            errors.append(
                f"Matrix references '{filename}' but no blueprint YAML with that "
                f"name was found under blueprints/"
            )
            continue

        path, text = blueprint_map[filename]
        bp_version = extract_blueprint_version(text)

        if bp_version is None:
            errors.append(
                f"{path.relative_to(ROOT)}: could not extract a version string "
                f"from the blueprint YAML (add 'Version: X.Y.Z' to the description, "
                f"or include 'vX.Y.Z' in the name field)"
            )
            continue

        if bp_version != matrix_version:
            errors.append(
                f"Version mismatch — '{filename}': "
                f"blueprint is v{bp_version}, "
                f"compatibility matrix says v{matrix_version}"
            )

    # Check for blueprints not in the matrix
    for filename, (path, _) in blueprint_map.items():
        if filename not in matrix:
            errors.append(
                f"Blueprint '{path.relative_to(ROOT)}' is not listed in the "
                f"compatibility matrix (docs/blueprints/README.md)"
            )

    if errors:
        print("Blueprint version check failed:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("Blueprint version check passed.")
    print(f"Checked: {len(matrix)} blueprint(s) against the compatibility matrix")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
