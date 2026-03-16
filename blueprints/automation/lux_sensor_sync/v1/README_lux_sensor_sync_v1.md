# README — lux_sensor_sync v1

**Blueprint:** `lux_sensor_sync.yaml`
**Version:** 1.1.0 (see `CHANGELOG_lux_sensor_sync.md`)
**Domain:** automation
**Path:** `blueprints/automation/lux_sensor_sync/v1/lux_sensor_sync.yaml`
**Author:** asucrews
**Min HA version:** 2024.4.0

---

## Overview

Infers whether a light is on or off using a **lux delta sensor**:

> **delta = max(lux − adaptive_baseline, 0)**

The delta represents "how far above ambient" the current lux reading is.
Because the baseline adapts to environmental conditions (blinds, time of day,
cloud cover), absolute lux thresholds are never needed.

Designed for lights that **cannot be controlled directly by Home Assistant**:
fan-mounted lights, switched outlets on dumb switches, relay-only circuits.
Writes inferred state to an `input_boolean` consumed by WITB+ Actions as a
`light_gating_entity`.

---

## How It Works

### Inference logic

| Condition | Action |
|---|---|
| Delta >= `on_threshold` for `on_for_seconds` | Set `light_boolean` → `on` |
| Delta <= `off_threshold` for `off_for_seconds` | Set `light_boolean` → `off` |

### Sensor restore suppression

By default (`suppress_infer_on_after_sensor_restore: true`), infer-ON is
suppressed when the sensor just transitioned from `unknown` or `unavailable`.
This prevents the boolean from incorrectly flipping ON after HA restarts or
sensor reconnects. The `ha_start` branch handles startup correction
independently via a 30-second settling delay.

### Startup sync

On every HA restart the blueprint waits 30 seconds for sensors to restore,
then corrects the `light_boolean` against current delta:
- If delta is above `on_threshold` and boolean is `off` → set boolean `on`.
- If delta is below `off_threshold` and boolean is `on` → set boolean `off`.

---

## Inputs

### Required

| Input | Domain | Description |
|---|---|---|
| `delta_sensor` | `sensor` | Lux above ambient baseline in lx. Produced by companion package template. |
| `light_boolean` | `input_boolean` | Output boolean tracking inferred light state. Consumed by WITB+ Actions `light_gating_entity`. |

### Thresholds and timing

| Input | Default | Description |
|---|---|---|
| `on_threshold` | `40 lx` | Infer ON when delta reaches this value |
| `on_for_seconds` | `10 s` | Delta must stay above threshold for this long before inferring ON |
| `off_threshold` | `15 lx` | Infer OFF when delta drops to this value |
| `off_for_seconds` | `15 s` | Delta must stay below threshold for this long before inferring OFF |

### Behavior

| Input | Default | Description |
|---|---|---|
| `suppress_infer_on_after_sensor_restore` | `true` | Suppress infer-ON when sensor just restored from `unknown`/`unavailable` |

---

## Architecture notes

- **`mode: restart`** — latest trigger always wins. A lux event during the
  startup delay cancels the startup sync and applies the new state immediately.
- **No variables block needed** — `!input` values are consumed directly in
  `numeric_state` and `state` conditions. No Jinja2 computation required.
- **Hysteresis band** — `on_threshold` must be set higher than `off_threshold`
  to create a stable hysteresis band. Recommended minimum gap: 10–20 lx.
  Inverted thresholds cause boolean oscillation.
- **Infer-OFF is never suppressed** — turning the boolean off is always the
  safe direction. Sensor restore suppression applies only to infer-ON.

---

## Known limitations

- **Sensor reconnect may delay infer-ON** (`suppress_infer_on_after_sensor_restore: true`)
  — if the sensor drops to unavailable mid-session and reconnects with delta
  above threshold, the first trigger fire is suppressed. Infer-ON proceeds
  normally after the sensor makes another state change. Disable the input if
  this is a concern.
- **Threshold inversion not validated** — the blueprint does not check that
  `on_threshold > off_threshold` at load time. Misconfiguration causes
  oscillation. See `rules_lux_sensor_sync.md` rule 16.

---

## Companion files

| File | Purpose |
|---|---|
| `lux_sensor_sync_package_template.yaml` | Generates adaptive lux baseline + delta sensors per room |
| `CHANGELOG_lux_sensor_sync.md` | Version history for blueprint and companion files |
| `rules_lux_sensor_sync.md` | Behavioral rules and invariants |
| `use_cases_lux_sensor_sync.md` | Supported use cases with pass/fail outcomes |

### Generating companion packages

```bash
python blueprints/generate_witb_packages_templated.py \
  --rooms "Master Bedroom" \
  --template blueprints/automation/lux_sensor_sync/v1/lux_sensor_sync_package_template.yaml \
  --out blueprints/automation/lux_sensor_sync/v1/packages
```

The generator requires two additional token substitutions beyond `room_slug`
and `Room Friendly Name` — set these in `rooms.yaml` under `tokens:`:

| Token | Example | Description |
|---|---|---|
| `__LUX_SENSOR__` | `sensor.master_bedroom_motion_illuminance` | Physical lux sensor entity ID |
| `__LIGHT_BOOLEAN__` | `input_boolean.master_bedroom_fan_light_inferred` | Inferred light boolean entity ID |

Use `--no-tuning-helpers` to omit the `input_boolean` and `input_number`
tuning entities. Baseline logic falls back to hardcoded defaults when helpers
are absent.

### Deployment note on `template:` syntax

HA packages loaded via `!include_dir_merge_named` do not support the newer
top-level `template:` list syntax. The trigger-based baseline sensor in this
template uses `template:` and must be loaded as a regular package file.
If you encounter issues, move the `template:` block into your main
`configuration.yaml` or a dedicated include file.

---

## Baseline package tuning helpers

| Helper | Default | Purpose |
|---|---|---|
| `freeze_while_light_on` boolean | `on` | Hold baseline when light is inferred on |
| `lux_big_rise_freeze` | 50 lx | Rise ≥ this freezes the baseline for one cycle |
| `lux_settle_band` | 10 lx | Small creep within this band follows at `alpha_up` |
| `lux_alpha_up` | 0.01 | How fast baseline tracks upward ambient changes |
| `lux_alpha_down` | 0.15 | How fast baseline tracks downward ambient changes |
| `lux_clamp_min` | 0 lx | Clamp raw lux below this to this value |
| `lux_clamp_max` | 10000 lx | Clamp raw lux above this to this value |
| `lux_delta_floor` | 0 lx | Minimum reported delta (prevents negative values) |

---

## Recommended starting values

| Input | Value | Notes |
|---|---|---|
| `on_threshold` | `40 lx` | Well above sensor noise, below dimmest light contribution |
| `on_for_seconds` | `10 s` | Light switches are near-instantaneous |
| `off_threshold` | `15 lx` | Creates a 25 lx hysteresis band |
| `off_for_seconds` | `15 s` | Absorbs brief dips while light is still on |
| `alpha_up` | `0.01` | Very slow upward drift to avoid chasing light-on levels |
| `alpha_down` | `0.15` | Tracks blinds and sunset reasonably fast |
| `big_rise_freeze` | `50 lx` | Must be lower than the dimmest light's lux contribution |
| `settle_band` | `10 lx` | Absorbs small ambient creep |

For a dim nightlight or lamp, lower `on_threshold` to 15–20 lx and
`big_rise_freeze` to 20 lx.
