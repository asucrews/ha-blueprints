# Tools

Utility scripts for repository validation and maintenance.

## Scripts

- `check_blueprint_docs.py`
  - Validates that each blueprint YAML under `blueprints/` has:
    - a sibling `README.md` or `README_*.md` (version-level READMEs use the descriptive naming convention),
    - a matching mention in `docs/blueprints/README.md`,
    - at least one `docs/blueprints/*.md` page that references the blueprint file name.

## Usage

Run from repo root:

```bash
python tools/check_blueprint_docs.py
```
