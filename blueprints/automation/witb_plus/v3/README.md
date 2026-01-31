# WITB (Wasp-in-the-Box) Occupancy

This project provides a **Wasp-in-the-Box (WITB)** occupancy blueprint for Home Assistant,
along with helper/template packages and a small generator script.

This README only documents **what each piece is and how to use it**.
It does not assume any specific repository layout.

---

## 1. Blueprint

**File:** `witb_plus.yaml`

The blueprint contains all occupancy logic.

It infers room occupancy using:
- A boundary **door sensor**
- A **motion sensor** (PIR or mmWave)
- Helper entities provided by the package file

Key characteristics:
- Event-driven (no polling)
- Supports long still periods (sleeping, bathroom use)
- Optional failsafe (do not clear while door is closed)
- Supports per-room override / force / manual occupied helpers

Automations using this blueprint are intended to be **created via the Home Assistant UI**.

---

## 2. Package Files (helpers + templates only)

Package files define **helpers and template sensors**, not automations.

They are loaded using:

```yaml
homeassistant:
  packages: !include_dir_merge_named packages/
```

### Required package format

Each package file **must** start with a package key:

```yaml
---
<slug>_witb:
  input_boolean:
  input_datetime:
  timer:
  template:
```

### Helpers created per room

- `input_boolean.<slug>_occupied`
- `input_boolean.<slug>_automation_override`
- `input_boolean.<slug>_force_occupied`
- `input_boolean.<slug>_manual_occupied`
- `input_boolean.<slug>_latched`
- `input_datetime.<slug>_last_motion`
- `input_datetime.<slug>_last_door`
- `timer.<slug>_failsafe` (optional)

### Template sensors

- `<Room> Occupied Effective`
- `<Room> WITB Override Active`
- `<Room> Minutes Since Motion`

These helpers and sensors are selected when creating the automation from the blueprint.

---

## 3. Generator Script

**File:** `generate_witb_packages_helpers_only.py`

This script generates **package YAML files** containing:
- helpers
- template sensors

It intentionally does **not** generate automations.

### Example usage

```bash
python3 generate_witb_packages_helpers_only.py \
  --rooms "Master Bedroom" "Loft" "Master Bathroom Toilet" \
  --out ./packages
```

Each room name is slugified automatically.

---

## 4. Creating the Automation

For each room:

1. Go to **Settings → Automations & Scenes**
2. Create a new automation
3. Choose **Blueprint**
4. Select the WITB blueprint
5. Bind:
   - Door sensor
   - Motion sensor
   - Helpers from the package file
6. Save

---

## Summary

- **Blueprint** = logic
- **Package files** = helpers + templates
- **UI automations** = glue between devices and blueprint

This separation keeps YAML simple, avoids blueprint path issues,
and scales cleanly as more rooms are added.
