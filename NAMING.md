# Naming Standards

Conventions used across this repository for files, directories, and identifiers.

---

## General Rules

### Casing

| Thing | Case | Example |
|---|---|---|
| Filenames (slugs, scripts, templates, YAML) | `lowercase_snake_case` | `vacuum_job_manager.yaml` |
| `README` prefix | UPPERCASE | `README.md`, `README_witb_plus_v4.md` |
| `CHANGELOG` prefix | UPPERCASE | `CHANGELOG_witb_plus.md` |
| Version directories | lowercase `v<N>` | `v1/`, `v4/` |
| Workflow files | `lowercase_snake_case` | `docs-blueprint-check.yml` (hyphens ok for workflows only) |

### Slug Formation

A **slug** is a safe identifier derived from a human-readable name. All slugs must be valid Home Assistant entity ID segments.

Rules (applied in order):
1. Lowercase the entire string.
2. Replace `&` with `and`.
3. Replace spaces and hyphens with `_`.
4. Strip any character that is not `[a-z0-9_]` (ASCII only — no accented or Unicode characters).
5. Collapse consecutive underscores to one.
6. Strip leading and trailing underscores.

Examples:

| Input | Slug |
|---|---|
| `Master Bathroom Toilet` | `master_bathroom_toilet` |
| `Office` | `office` |
| `Half Bathroom` | `half_bathroom` |
| `Lights & Fan` | `lights_and_fan` |

### Characters

- Use `_` to separate words. No hyphens in file or directory names (exception: GitHub Actions workflow files, where hyphens are conventional).
- No spaces anywhere in names.
- No dots except the file extension.
- ASCII only — no accented or Unicode characters.

### Versions

- Version **directories** use `v<major>` only (e.g., `v1`, `v2`, `v4`). Minor versions are tracked in the blueprint metadata and changelog, not in the directory name.
- Create a new version directory only for breaking changes or major rewrites. Minor and patch changes stay in the existing version directory.
- Docs page filenames include minor version when finer granularity is needed: `_v<major>_<minor>` (e.g., `_v1_7`).

### Paired Files

When two files form a logical pair (e.g., ON and OFF hooks), use a directional qualifier:
- `_on_` / `_off_` in individual filenames.
- Drop the qualifier in shared files that cover both (changelog, combined docs page, package template).

---

## Blueprint Files

### Automation blueprints

```
blueprints/automation/<blueprint_name>/<version>/<blueprint_slug>.yaml
```

Examples:
- `blueprints/automation/witb_plus/v4/witb_plus.yaml`
- `blueprints/automation/vacuum_job_manager/v1/vacuum_job_manager.yaml`
- `blueprints/automation/bathroom_fan_from_humidity/v1/bathroom_fan_from_humidity_delta.yaml`

### Script blueprints

```
blueprints/script/<blueprint_family>/<version>/<blueprint_slug>.yaml
```

Examples:
- `blueprints/script/witb_switch_light_profiles/v1/witb_lights_on_hook_vzw31sn.yaml`
- `blueprints/script/witb_switch_light_profiles/v1/witb_lights_off_hook_vzw31sn.yaml`

---

## Changelog Files

```
CHANGELOG_<blueprint_slug>.md
```

- `CHANGELOG_` prefix is uppercase.
- `<blueprint_slug>` matches the blueprint's main YAML filename (without `.yaml`).
- One changelog per blueprint. If a version folder covers multiple related scripts (e.g., ON + OFF hooks), use a shared slug that describes the family.
- Placed in the same versioned directory as the blueprint YAML.

Examples:
- `CHANGELOG_witb_plus.md`
- `CHANGELOG_witb_plus_actions_lights_fan.md`
- `CHANGELOG_bathroom_fan_from_humidity_delta.md`
- `CHANGELOG_vacuum_job_manager.md`
- `CHANGELOG_witb_plus_bed_force_occupied.md`
- `CHANGELOG_witb_lights_hooks_vzw31sn.md`

---

## README Files

Two tiers:

### Section / family level — `README.md`

Used at folder levels that GitHub renders automatically when browsing:
- Repo root
- `blueprints/`, `blueprints/automation/`, `blueprints/script/`
- `docs/`, `docs/blueprints/`, `examples/`, `references/`, `tools/`, `.github/workflows/`
- Blueprint family folders: `blueprints/automation/<blueprint_name>/`, `blueprints/script/<family>/`
- Example folders: `examples/<blueprint_short_name>/`
- Package output folders: `*/packages/`

### Version level — `README_<blueprint_slug>_<version>.md`

Used inside versioned directories (`v1/`, `v2/`, `v4/`). Named to be unambiguous when multiple version READMEs are open in an editor.

```
README_<blueprint_slug>_v<N>.md
```

Examples:
- `blueprints/automation/witb_plus/v4/README_witb_plus_v4.md`
- `blueprints/automation/witb_plus_actions_lights_fan/v2/README_witb_plus_actions_lights_fan_v2.md`
- `blueprints/automation/bathroom_fan_from_humidity/v1/README_bathroom_fan_from_humidity_delta_v1.md`
- `blueprints/automation/vacuum_job_manager/v1/README_vacuum_job_manager_v1.md`
- `blueprints/automation/witb_transit_room/v1/README_witb_transit_room_v1.md`
- `blueprints/automation/witb_plus_bed_sensor/v1/README_witb_plus_bed_force_occupied_v1.md`
- `blueprints/script/witb_switch_light_profiles/v1/README_witb_lights_hooks_vzw31sn_v1.md`

---

## Helper Package Templates

```
<descriptive_slug>_package_template.yaml
```

- Suffix is always `_package_template.yaml` (not `.template.yaml` or `_template.yaml`).
- Placed in the same versioned directory as the blueprint.

Examples:
- `witb_plus_package_template.yaml`
- `room_witb_actions_package_template.yaml`
- `room_humidity_baseline_delta_package_template.yaml`
- `transit_helpers_package_template.yaml`

---

## Generated Package Files

```
<room_slug>.yaml
```

- Output of the generator script.
- Filename is the room slug only (e.g., `office.yaml`, `hallway.yaml`).
- Placed in the `packages/` subdirectory of the versioned blueprint folder.

---

## Docs Pages

```
docs/blueprints/<blueprint_slug>_v<major>[_<minor>].md
```

- Version suffix uses `_v` followed by the major version number.
- Minor version appended with another underscore when needed (e.g., `_v1_7`).
- One doc page per blueprint (or logical grouping like ON+OFF hooks).

Examples:
- `docs/blueprints/witb_plus_v3.md`
- `docs/blueprints/witb_plus_actions_lights_fan_v1.md`
- `docs/blueprints/bathroom_fan_from_humidity_delta_v1.md`
- `docs/blueprints/vacuum_job_manager_v1.md`
- `docs/blueprints/witb_lights_hooks_v1_7.md`

---

## Example Files

### Example automations

```
examples/<blueprint_short_name>/<room_slug>_automation.yaml
```

If the automation type needs disambiguation, insert a qualifier before `_automation`:

```
examples/<blueprint_short_name>/<room_slug>_<qualifier>_automation.yaml
```

Examples:
- `examples/witb_plus/office_automation.yaml`
- `examples/witb_plus_actions_lights_fan/office_actions_automation.yaml`
- `examples/vacuum_job_manager/roomba_vacjob_automation.yaml`
- `examples/witb_transit_room/hallway_automation.yaml`

### Example helper packages

```
examples/<blueprint_short_name>/packages/<room_slug>.yaml
```

If multiple blueprint types share a packages folder, append a qualifier:

```
examples/<blueprint_short_name>/packages/<room_slug>_<qualifier>.yaml
```

Examples:
- `examples/witb_plus/packages/office.yaml`
- `examples/witb_plus_actions_lights_fan/packages/office_witb_actions.yaml`
- `examples/vacuum_job_manager/packages/roomba_vacjob.yaml`

### Example script instances

```
examples/<blueprint_short_name>/<room_slug>_scripts.yaml
```

---

## Python Generator Scripts

```
blueprints/generate_witb_packages_templated.py
```

- A single shared generator handles all package template types by accepting `--template` as an argument.
- No per-blueprint copies of the generator should be created.

---

## Directory Structure Summary

```
blueprints/
  automation/
    <blueprint_name>/                        # family folder
      README.md                              # GitHub-rendered landing page
      <version>/                             # e.g., v1, v2, v4
        README_<blueprint_slug>_v<N>.md      # descriptive version doc
        <blueprint_slug>.yaml
        CHANGELOG_<blueprint_slug>.md
        <descriptive>_package_template.yaml
        packages/
          README.md
          <room_slug>.yaml                   # generated output
  script/
    <blueprint_family>/
      README.md
      <version>/
        README_<slug>_v<N>.md
        <blueprint_slug>.yaml
        CHANGELOG_<slug>.md
        <descriptive>_package_template.yaml  (if applicable)
  generate_witb_packages_templated.py        # single shared generator

docs/
  blueprints/
    README.md                                # compatibility matrix + links
    <blueprint_slug>_v<N>.md                 # per-blueprint implementation docs

examples/
  <blueprint_short_name>/
    README.md
    <room_slug>_automation.yaml
    packages/
      README.md
      <room_slug>.yaml

tools/
  <script_name>.py

.github/
  workflows/
    <workflow-name>.yml                      # hyphens ok here
```
