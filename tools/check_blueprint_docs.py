#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLUEPRINTS_DIR = ROOT / "blueprints"
DOCS_DIR = ROOT / "docs" / "blueprints"
DOCS_INDEX = DOCS_DIR / "README.md"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def is_blueprint_yaml(path: Path) -> bool:
    return re.search(r"(?m)^blueprint:\s*$", read_text(path)) is not None


def main() -> int:
    errors: list[str] = []

    blueprint_files = sorted(
        p for p in BLUEPRINTS_DIR.rglob("*.yaml") if p.is_file() and is_blueprint_yaml(p)
    )
    if not blueprint_files:
        errors.append("No blueprint YAML files found under blueprints/.")

    for blueprint in blueprint_files:
        readme = blueprint.parent / "README.md"
        if not readme.exists():
            errors.append(
                f"Missing sibling README.md for blueprint: {blueprint.relative_to(ROOT)}"
            )

    if not DOCS_INDEX.exists():
        errors.append(f"Missing docs index: {DOCS_INDEX.relative_to(ROOT)}")
        docs_index_text = ""
    else:
        docs_index_text = read_text(DOCS_INDEX)

    docs_pages = sorted(p for p in DOCS_DIR.glob("*.md") if p.name.lower() != "readme.md")
    docs_page_text = {p: read_text(p) for p in docs_pages}

    for blueprint in blueprint_files:
        name = blueprint.name
        matching_pages = [p for p, text in docs_page_text.items() if name in text]

        if not matching_pages:
            errors.append(
                "No docs/blueprints/*.md page references blueprint: "
                f"{blueprint.relative_to(ROOT)}"
            )

        if name not in docs_index_text:
            errors.append(
                "docs/blueprints/README.md does not reference blueprint file name: "
                f"{name}"
            )

    if errors:
        print("Blueprint docs validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Blueprint docs validation passed.")
    print(f"Checked blueprints: {len(blueprint_files)}")
    print(f"Checked docs pages: {len(docs_pages)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
