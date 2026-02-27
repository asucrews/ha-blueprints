# Contributing

Guidelines for adding or modifying blueprints in this repository.

---

## Before You Start

- Read [`NAMING.md`](NAMING.md) — all file names, directory structure, slug formation, and version conventions are defined there.
- Run the validation tool to confirm the repo is clean before making changes:
  ```bash
  python tools/check_blueprint_docs.py
  ```

---

## Adding a New Blueprint

### 1. Create the directory structure

Follow the layout defined in `NAMING.md`. For an automation blueprint:

```
blueprints/automation/<blueprint_name>/
  README.md                              # family landing page
  <version>/
    README_<blueprint_slug>_v<N>.md      # version detail doc
    <blueprint_slug>.yaml                # blueprint file
    CHANGELOG_<blueprint_slug>.md        # version history
    <descriptive>_package_template.yaml  # if helpers are needed
    packages/
      README.md
```

For a script blueprint, use `blueprints/script/` instead.

### 2. Name files correctly

- Blueprint YAML: `<blueprint_slug>.yaml` — descriptive, snake_case, matches the HA blueprint `name` field intent.
- README: `README_<blueprint_slug>_v<N>.md` at version level; `README.md` at family level.
- CHANGELOG: `CHANGELOG_<blueprint_slug>.md`.
- Package template: `<descriptive>_package_template.yaml`.

See [`NAMING.md`](NAMING.md) for slug formation rules and the full directory reference.

### 3. Write the CHANGELOG

Start with the initial version entry. Use this format:

```markdown
# CHANGELOG — <Blueprint Friendly Name>

## v1.0.0

Initial release.

- Brief description of what the blueprint does.
- List of key behaviors and configurable options.
```

### 4. Write the docs page

Add a page to `docs/blueprints/<blueprint_slug>_v<N>.md`. Minimum sections:

- **Scope** — what this blueprint does and doesn't do.
- **Source** — path to the blueprint YAML.
- **Min HA version**.
- **Inputs** — every input with type, default, and purpose.
- **Behavior** — trigger/condition/action summary.
- **Setup order** — step-by-step for first-time setup.

### 5. Update the docs index

Add a row to the compatibility matrix in `docs/blueprints/README.md` and a numbered entry under the appropriate section (Automation Blueprints or Script Blueprints).

### 6. Add examples

Create a folder under `examples/<blueprint_short_name>/` with:
- `README.md`
- At least one `<room_slug>_automation.yaml`
- `packages/<room_slug>.yaml` if the blueprint uses helpers

### 7. Run validation

```bash
python tools/check_blueprint_docs.py
```

All checks must pass before opening a PR.

---

## Modifying an Existing Blueprint

### Minor changes (bug fixes, new optional inputs)

- Edit in place within the existing version directory.
- Update the CHANGELOG with a new version entry.
- Update the docs page if behavior or inputs changed.
- Re-run `tools/check_blueprint_docs.py`.

### Breaking changes

- Create a new version directory (e.g., `v2/` → `v3/`).
- Follow the full "Adding a New Blueprint" flow for the new version.
- Add a migration notes section to the new docs page.
- Update the compatibility matrix version number.

---

## Pull Request Checklist

- [ ] `tools/check_blueprint_docs.py` passes with no errors.
- [ ] New/changed blueprint YAML is valid (the `yaml-lint` CI workflow will verify on push).
- [ ] CHANGELOG updated.
- [ ] Docs page added or updated.
- [ ] `docs/blueprints/README.md` compatibility matrix updated.
- [ ] Examples added or updated if inputs changed.
- [ ] File names follow [`NAMING.md`](NAMING.md).
