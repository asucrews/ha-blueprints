# generate_witb_packages_templated.py

Template-driven generator for Home Assistant
[merge_named](https://www.home-assistant.io/docs/configuration/packages/) package files.

Point it at a template YAML file and a list of rooms — it produces one fully
populated, ready-to-use package file per room with all tokens replaced and any
unwanted feature blocks stripped.

Works with all WITB+ template files out of the box, and automatically adapts
to any new template you create in the future without needing script edits.

---

## Requirements

- Python 3.8 or later
- [PyYAML](https://pypi.org/project/PyYAML/) (only needed for YAML config files)

```bash
pip install pyyaml
```

---

## Quickstart

### Option A — config file (recommended)

Create a `rooms.yaml` next to your template files:

```yaml
template: witb_plus_package_template.yaml
out: ./packages/rooms
key_suffix: _witb_plus

rooms:
  - name: "Office"
  - name: "Master Bedroom"
  - name: "Bathroom"
```

Then run:

```bash
python generate_witb_packages_templated.py --config rooms.yaml
```

See [rooms.md](rooms.md) for the full config reference.

### Option B — command line only

```bash
python generate_witb_packages_templated.py \
  --template witb_plus_package_template.yaml \
  --rooms "Office" "Master Bedroom" "Bathroom" \
  --out ./packages/rooms
```

---

## Always preview first

`--dry-run` prints exactly what would be generated without writing any files:

```bash
python generate_witb_packages_templated.py --config rooms.yaml --dry-run
```

Example output:

```
[DRY RUN] Would write: ./packages/rooms/office.yaml
          Features:    helpers, controls, latched, exit_close, failsafe, entry_gating
          Package key: office_witb_plus

[DRY RUN] Would write: ./packages/rooms/master_bedroom.yaml
          Features:    helpers, controls, exit_close, failsafe, entry_gating
          Package key: master_bedroom_witb_plus

Dry run complete. 2 file(s) would be written to: ./packages/rooms
```

---

## Command-line reference

```
usage: generate_witb_packages_templated.py
       [--config CONFIG]
       [--template TEMPLATE]
       [--out OUT]
       [--rooms ROOM [ROOM ...]]
       [--key-suffix KEY_SUFFIX]
       [--file-suffix FILE_SUFFIX]
       [--dry-run]
       [--no-helpers] [--no-controls] [--no-latched] [--no-exit-close]
       [--no-failsafe] [--no-entry-gating]
       [--no-lights] [--no-fan] [--no-lux] [--no-humidity] [--no-night]
       [--no-tuning-helpers] [--no-sbm]
```

| Flag | Description |
|---|---|
| `--config FILE` | YAML or JSON config file (recommended — can contain template, out, key_suffix, and rooms) |
| `--template FILE` | Template YAML file to generate from |
| `--out DIR` | Directory to write generated package files into |
| `--rooms NAME …` | One or more room names on the command line (quote multi-word names) |
| `--key-suffix SUFFIX` | Suffix appended to the room slug to form the HA package key (default: `_witb`) |
| `--file-suffix EXT` | File extension for output files (default: `.yaml`) |
| `--dry-run` | Preview output without writing any files |
| `--no-X` | Disable feature block `X` for all rooms in this run |

CLI flags always take priority over values in the config file.

---

## How it works

### Templates

Templates are standard YAML files with two kinds of special markers:

**Token placeholders** — replaced with room-specific values at generation time:

| Token | Replaced with |
|---|---|
| `room_slug` | ASCII slug derived from the room name, e.g. `master_bedroom` |
| `Room Friendly Name` | The room name as written, e.g. `Master Bedroom` |
| `Friendly Name` | Same as above — alternate style used by some templates |

**Feature blocks** — optional sections that can be stripped per-room or globally:

```yaml
# --- BEGIN latched ---
room_slug_latched:
  name: "Room Friendly Name latched"
  icon: mdi:door-closed-lock
# --- END latched ---
```

Any block can be disabled with `--no-latched` on the CLI or `no_latched: true`
in a room's config entry. The script auto-discovers block names from the
template — no changes to the script are needed when you add new blocks.

### Output

Each room produces one file named `{slug}.yaml` containing a single HA
`merge_named` package key:

```yaml
---
master_bedroom_witb_plus:
  input_boolean:
    master_bedroom_occupied:
      name: "Master Bedroom occupied"
      ...
```

---

## Recommended folder layout

Keep all template files, config files, and the script in the same directory
so that `template:` and `out:` paths in your config files resolve correctly:

```
ha-packages/
  generate_witb_packages_templated.py
  witb_plus_package_template.yaml
  room_witb_actions_package_template.yaml
  transit_helpers_package_template.yaml
  room_humidity_baseline_delta_package_template.yaml
  rooms_witb_plus.yaml        ← one config per template
  rooms_witb_actions.yaml
  rooms_transit.yaml
  rooms_humidity.yaml
  packages/
    rooms/
    actions/
    transit/
    humidity/
```

---

## Per-room feature overrides

Disable specific blocks for individual rooms in the config file:

```yaml
rooms:
  - name: "Half Bathroom"
    no_exit_close: true      # no door-behind-you pattern
    no_entry_gating: true

  - name: "Master Bedroom"
    no_latched: true

  - name: "Office"            # all defaults — no overrides
```

---

## Global feature overrides

Disable a block for every room in a run using `emit_X: false` in the config,
or `--no-X` on the CLI:

```yaml
# rooms.yaml
emit_latched: false    # strips latched from all rooms in this file
```

```bash
# CLI equivalent (also strips latched from all rooms)
python generate_witb_packages_templated.py --config rooms.yaml --no-latched
```

Priority order (highest → lowest):

```
CLI --no-X  >  per-room no_X: true  >  config emit_X: false  >  default (on)
```

---

## Supported templates

| Template file | Key suffix convention | Feature blocks |
|---|---|---|
| `witb_plus_package_template.yaml` | `_witb_plus` | helpers, controls, latched, exit_close, failsafe, entry_gating |
| `room_witb_actions_package_template.yaml` | `_witb_actions` | lights, fan, lux, humidity, night |
| `room_humidity_baseline_delta_package_template.yaml` | `_humidity` | tuning_helpers |
| `transit_helpers_package_template.yaml` | `_transit` | *(flat — no feature blocks)* |
| `vacuum_job_helpers.yaml` | `_vacuum` | *(flat — no feature blocks)* |

---

## Writing your own templates

1. Use `room_slug` and `Room Friendly Name` as placeholders anywhere in the file.
2. Wrap optional sections in `# --- BEGIN name ---` / `# --- END name ---` markers.
3. Optionally wrap the whole file in a single top-level key (e.g. `my_template:`) —
   the script detects and unwraps it automatically.
4. Point a config file at it — new block names are discovered automatically
   and get their own `--no-name` CLI flag with no script changes required.
