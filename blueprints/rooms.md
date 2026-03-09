# rooms.yaml Config Reference

The config file is the single source of truth for a generation run — it tells
the script which template to use, where to write output, and what rooms to
generate, along with any per-room feature overrides.

Pass it to the script with `--config`:

```bash
python generate_witb_packages_templated.py --config rooms.yaml
```

---

## Top-level keys

| Key | Required | Description |
|---|---|---|
| `template` | Yes* | Path to the template YAML file, relative to this config file |
| `out` | Yes* | Output directory for generated files, relative to this config file |
| `key_suffix` | No | Suffix appended to the room slug to form the HA package key (default: `_witb`) |
| `file_suffix` | No | File extension for generated files (default: `.yaml`) |
| `rooms` | Yes | List of rooms to generate (see below) |
| `emit_X` | No | Global feature override — see [Global feature flags](#global-feature-flags) |

\* Required unless supplied on the command line via `--template` / `--out`.

---

## Room entries

Each entry in `rooms:` is either a plain string or a mapping with `name` and
optional feature flags.

### Plain string

```yaml
rooms:
  - name: "Office"
```

### With per-room feature flags

```yaml
rooms:
  - name: "Master Bedroom"
    no_latched: true
    no_entry_gating: true
```

A `no_X: true` flag strips that feature block from this room's output only.
All other rooms are unaffected.

### Custom slug

By default the slug is derived from the name (`Master Bedroom` → `master_bedroom`).
Override it explicitly if needed:

```yaml
rooms:
  - name: "Master Bathroom (Ensuite)"
    slug: master_bathroom
```

---

## Available feature flags

These map directly to `# --- BEGIN X ---` block markers in the template file.
The script auto-discovers which features a given template actually has — flags
for features not present in the template are silently ignored.

### witb_plus_package_template.yaml

| Flag | What it controls |
|---|---|
| `no_helpers: true` | Removes core occupancy boolean, last_motion/last_door datetimes, exit_eval timer, and the occupied/occupied_effective/override_active template sensors |
| `no_controls: true` | Removes automation_override, force_occupied, manual_occupied input_booleans |
| `no_latched: true` | Removes the latched debug input_boolean |
| `no_exit_close: true` | Removes last_exit_door datetime (for rooms without a "door closes behind you" pattern) |
| `no_failsafe: true` | Removes the failsafe timer and failsafe_timeout input_number |
| `no_entry_gating: true` | Removes the entry_window_seconds input_number |

### room_witb_actions_package_template.yaml

| Flag | What it controls |
|---|---|
| `no_lights: true` | Removes auto_lights_on, keep_on, brightness day/night helpers, and actions_cooldown timer |
| `no_fan: true` | Removes auto_fan_on, fan speed/delay/runon helpers, and fan_runon timer |
| `no_lux: true` | Removes the lux_threshold input_number |
| `no_humidity: true` | Removes humidity_high/low input_numbers |
| `no_night: true` | Removes night_start/end input_datetimes |

### room_humidity_baseline_delta_package_template.yaml

| Flag | What it controls |
|---|---|
| `no_tuning_helpers: true` | Removes the freeze/band/alpha/clamp input_boolean and input_number tuning helpers — leaves only the template sensors |

---

## Global feature flags

Set at the top level to disable a feature for **all** rooms in one run.
CLI `--no-X` flags override these; per-room `no_X: true` overrides both.

```yaml
emit_latched: false       # disable latched block for every room
emit_entry_gating: false  # disable entry_gating block for every room
```

Priority order (highest → lowest):

```
CLI --no-X flag  >  per-room no_X: true  >  config emit_X: false  >  default (on)
```

---

## Full example

```yaml
# rooms.yaml — WITB+ core helpers
template: witb_plus_package_template.yaml
out: ./packages/rooms
key_suffix: _witb_plus

# Disable latched globally — no room in this file uses it
emit_latched: false

rooms:
  - name: "Garage"

  - name: "Half Bathroom"
    no_exit_close: true     # no "door closes behind you" pattern
    no_entry_gating: true

  - name: "Master Bedroom"

  - name: "Master Bedroom Closet"
    no_failsafe: true
    no_entry_gating: true

  - name: "Master Bathroom"

  - name: "Master Bathroom Toilet"
    no_exit_close: true
    no_entry_gating: true

  - name: "Laundry"

  - name: "Office"
```

---

## Multiple config files (one per template)

Each template typically gets its own config file in the same directory:

```
ha-packages/
  generate_witb_packages_templated.py
  witb_plus_package_template.yaml
  room_witb_actions_package_template.yaml
  transit_helpers_package_template.yaml
  rooms_witb_plus.yaml
  rooms_witb_actions.yaml
  rooms_transit.yaml
  packages/
```

Run each one independently:

```bash
python generate_witb_packages_templated.py --config rooms_witb_plus.yaml
python generate_witb_packages_templated.py --config rooms_witb_actions.yaml
python generate_witb_packages_templated.py --config rooms_transit.yaml
```
