# Light Inferred From Lux Delta (Automation Blueprint)

This automation blueprint infers whether a light is on or off using a
**lux delta sensor**:

> **delta = max(lux − adaptive_baseline, 0)**

The delta signal represents "how far above ambient" the current lux reading
is. Because the baseline adapts to environmental conditions (blinds, time of
day, cloud cover), absolute lux thresholds are never needed.

Designed for lights that **cannot be controlled directly by Home Assistant**:
fan-mounted lights, switched outlets on dumb switches, etc.

---

## What this blueprint does

- **Infers light ON** when `delta >= on_threshold` for a short debounce period.
- **Infers light OFF** when `delta <= off_threshold` for a short debounce period.
- Writes inferred state to an `input_boolean` for consumption by other
  automations (e.g. WITB+ Actions `light_gating_entity`).
- Re-evaluates state on Home Assistant restart.

---

## Why delta instead of absolute lux

A fan light might add 200 lx. But on a bright afternoon with the blinds open
the room might already be at 300 lx, making any fixed "light on" threshold
ambiguous. The adaptive baseline tracks the ambient level so the delta isolates
only the contribution of the artificial light regardless of time of day, blinds
position, or season.

---

## Requirements

You must already have:
- A **lux delta sensor** (`sensor.*`) produced by the companion package template
  (`room_lux_baseline_delta_package_template.yaml`).
- An **`input_boolean`** to track the inferred light state.
- The **baseline freeze boolean** (`input_boolean.room_slug_lux_freeze_while_light_on`)
  must be set to `on` for the baseline to hold when the light is inferred on.
  This is the default behaviour and is the most important tuning choice.

---

## Inputs

### Entities
- **delta_sensor** — `sensor.room_lux_delta` from the package template.
- **light_boolean** — `input_boolean` written by this automation; consumed by
  WITB+ or other automations as a binary gate.

### Thresholds & timing
- **on_threshold** (default: 40 lx) — infer ON when delta ≥ this value.
- **on_for_seconds** (default: 10 s) — debounce before inferring ON.
- **off_threshold** (default: 15 lx) — infer OFF when delta ≤ this value.
- **off_for_seconds** (default: 15 s) — debounce before inferring OFF.

The gap between `on_threshold` and `off_threshold` is the hysteresis band.
Keep it meaningful (at least 10–20 lx) to avoid rapid toggling.

---

## Tuning guide

### Light not detected (false negatives)
- Lower **on_threshold** (e.g. 40 → 25)
- Lower **on_for_seconds** (e.g. 10 → 5)
- Check that `big_rise_freeze` on the baseline package is *lower* than the
  lux contribution of the light

### False positives (bright window triggers detection)
- This usually means the baseline is not adapting correctly. Check:
  - Is `alpha_down` large enough to track blind/curtain changes? (try 0.20)
  - Is `alpha_up` slow enough to not drift into light territory? (keep ≤ 0.02)
- If the false trigger is slow (sunrise), increase **on_for_seconds**
- If the false trigger is fast (sudden sun), lower **big_rise_freeze** threshold
  in the package so the baseline freezes on that event too

### Light inferred on, then drops to off while light still on
- The baseline is drifting upward and eroding the delta. Check:
  - Is `input_boolean.room_slug_lux_freeze_while_light_on` set to `on`?
  - Is `alpha_up` very small? (should be 0.01 or less)
  - Is `big_rise_freeze` lower than the light contribution? If not, the
    initial spike is not being frozen and `alpha_up` starts chasing it

### Boolean flickers
- Increase **off_for_seconds** and **on_for_seconds**
- Widen the hysteresis band (lower `off_threshold` or raise `on_threshold`)

---

## Baseline package tuning helpers

| Helper | Default | Purpose |
|---|---|---|
| `freeze_while_light_on` boolean | `on` | Hold baseline when light inferred on |
| `lux_big_rise_freeze` | 50 lx | Rise ≥ this freezes the baseline for one cycle |
| `lux_settle_band` | 10 lx | Small creep within this band follows at `alpha_up` |
| `lux_alpha_up` | 0.01 | How fast baseline tracks upward ambient changes |
| `lux_alpha_down` | 0.15 | How fast baseline tracks downward ambient changes |
| `lux_clamp_min` | 0 lx | Clamp raw lux below this to this value |
| `lux_clamp_max` | 10000 lx | Clamp raw lux above this to this value |
| `lux_delta_floor` | 0 lx | Minimum reported delta (prevents negative values) |

---

## Recommended starting values

These work well for a typical ceiling or fan-mounted light:

| Input | Value |
|---|---|
| on_threshold | 40 lx |
| on_for_seconds | 10 s |
| off_threshold | 15 lx |
| off_for_seconds | 15 s |
| alpha_up | 0.01 |
| alpha_down | 0.15 |
| big_rise_freeze | 50 lx |
| settle_band | 10 lx |

For a dim nightlight or lamp, lower `on_threshold` to 15–20 lx and
`big_rise_freeze` to 20 lx.

---

## Example automation (YAML)

```yaml
automation:
  - use_blueprint:
      path: asucrews/lux_light_inferred_from_delta.yaml
      input:
        delta_sensor: sensor.master_bedroom_lux_delta
        light_boolean: input_boolean.master_bedroom_fan_light_inferred
        on_threshold: 40
        on_for_seconds: 10
        off_threshold: 15
        off_for_seconds: 15
```

---

## Companion package generator

Use `generate_witb_packages_templated.py` with
`room_lux_baseline_delta_package_template.yaml` to generate helper packages.

The generator expects two additional substitution tokens beyond `room_slug`
and `Room Friendly Name`:

- `__LUX_SENSOR__` — entity ID of the physical lux sensor (e.g.
  `sensor.master_bedroom_motion_illuminance`)
- `__LIGHT_BOOLEAN__` — entity ID of the inferred light boolean (e.g.
  `input_boolean.master_bedroom_fan_light_inferred`)

Run from repo root:

```bash
python blueprints/generate_witb_packages_templated.py \
  --rooms "Master Bedroom" \
  --template blueprints/automation/lux_light_inferred/v1/room_lux_baseline_delta_package_template.yaml \
  --out blueprints/automation/lux_light_inferred/v1/packages
```

### Deployment note on `template:` vs `binary_sensor: platform: template`

HA packages loaded via `!include_dir_merge_named` do not support the newer
top-level `template:` list syntax. The trigger-based baseline sensor in this
template uses `template:` and **must be loaded as a regular package file**
(`!include_dir_merge_named packages/`) — this works if your HA config uses
that method. If you encounter issues, move the `template:` block into your
main `configuration.yaml` or a dedicated include file.
