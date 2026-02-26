# WITB+ Actions (Lights + Fan)

This folder contains the **actions blueprint** that pairs with WITB+ occupancy.

Use this when you already have room occupancy sensors from `witb_plus/v4` (for example
`binary_sensor.<slug>_occupied_effective`) and want reliable light/fan actions with safety tags.

---

## 1. Blueprint

**File:** `witb_plus_actions_lights_fan.yaml`

This blueprint controls:
- Lights (brightness profiles, optional sun/lux gating)
- Fan (`fan.*` or `switch.*`)
- Vacancy off behavior with optional fan run-on
- Optional humidity hold (fan stays on while humidity remains high)
- Optional startup cleanup for auto-tagged entities

It is intended to be used from the Home Assistant UI via **Create Automation from Blueprint**.

---

## 2. Package Helpers (helpers only)

**Reference template:** `room_witb_actions_package.template.yaml`  
**Generated output location:** `packages/`

Package files provide helper entities such as:
- `input_boolean.<slug>_auto_lights_on`
- `input_boolean.<slug>_auto_fan_on`
- `timer.<slug>_actions_cooldown`
- `timer.<slug>_fan_runon`
- `input_datetime.<slug>_actions_night_start`
- `input_datetime.<slug>_actions_night_end`
- Optional `input_number` tuning helpers (brightness, fan %, lux threshold, humidity thresholds, fan delay)

Load these packages with:

```yaml
homeassistant:
  packages: !include_dir_merge_named packages/
```

---

## 3. Generator Script

**File:** `generate_witb_plus_actions_packages_templated.py`

The script generates helper package YAML files only.  
It does **not** generate automations.

Example:

```bash
python3 generate_witb_plus_actions_packages_templated.py \
  --rooms "Office" "Master Bathroom Toilet" \
  --template room_witb_actions_package.template.yaml \
  --out ./packages
```

Dry run:

```bash
python3 generate_witb_plus_actions_packages_templated.py \
  --rooms "Office" \
  --template room_witb_actions_package.template.yaml \
  --out ./packages \
  --dry-run
```

---

## 4. Typical Setup Flow

1. Create room occupancy with `witb_plus/v4`.
2. Generate helpers into `packages/`.
3. Reload/restart Home Assistant so helpers exist.
4. Create an automation from `WITB+ Actions - Lights + Fan`.
5. Bind `occupied_effective` to `binary_sensor.<slug>_occupied_effective`.
6. Bind lights/fan entities and optional helper inputs.

---

## Summary

- **WITB+ v4** handles occupancy inference.
- **WITB+ Actions** handles light/fan behavior.
- **Package files** provide helper entities for safe automation behavior and dashboard tuning.
