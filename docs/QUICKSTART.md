# Quick Start

**Audience:** Experienced Home Assistant users comfortable with YAML packages, blueprint imports, and running Python scripts. No explanations — just the steps.

> New to HA packages or blueprints? Use [`GETTING_STARTED.md`](GETTING_STARTED.md) instead.

---

## Prerequisites

- Home Assistant 2026.2.0+
- A packages directory configured in `configuration.yaml`:
  ```yaml
  homeassistant:
    packages: !include_dir_merge_named packages/
  ```
- Python 3 available on your workstation (for the helper generator)
- Sensors: one seal door contact, one PIR motion sensor (minimum)

---

## Step 1 — Import blueprints into Home Assistant

In HA: **Settings → Automations & Scenes → Blueprints → Import Blueprint**

| Blueprint | Raw GitHub URL |
|---|---|
| WITB+ Occupancy | `https://raw.githubusercontent.com/asucrews/ha-blueprints/main/blueprints/automation/witb_plus/v4/witb_plus.yaml` |
| WITB+ Actions - Lights + Fan | `https://raw.githubusercontent.com/asucrews/ha-blueprints/main/blueprints/automation/witb_plus_actions_lights_fan/v2/witb_plus_actions_lights_fan.yaml` |

---

## Step 2 — Generate helper packages

Run from repo root. Replace room names with your own.

```bash
# Occupancy helpers
python blueprints/generate_witb_packages_templated.py \
  --rooms "Office" \
  --template blueprints/automation/witb_plus/v4/witb_plus_package_template.yaml \
  --out blueprints/automation/witb_plus/v4/packages

# Actions helpers
python blueprints/generate_witb_packages_templated.py \
  --rooms "Office" \
  --template blueprints/automation/witb_plus_actions_lights_fan/v2/room_witb_actions_package_template.yaml \
  --out blueprints/automation/witb_plus_actions_lights_fan/v2/packages
```

Use `--dry-run` to preview without writing files.

---

## Step 3 — Commit generated packages

Track the generated files in git so your room configs are version controlled.

```bash
git add blueprints/automation/witb_plus/v4/packages/office.yaml \
        blueprints/automation/witb_plus_actions_lights_fan/v2/packages/office_witb_actions.yaml

git commit -m "Add Office WITB+ and actions helper packages"
```

---

## Step 4 — Copy packages to Home Assistant

Copy generated files to your HA packages directory:

```bash
cp blueprints/automation/witb_plus/v4/packages/office.yaml        /path/to/ha/packages/
cp blueprints/automation/witb_plus_actions_lights_fan/v2/packages/office_witb_actions.yaml  /path/to/ha/packages/
```

Then reload: **Developer Tools → YAML → Reload All YAML** (or restart HA).

---

## Step 5 — Create automations in Home Assistant

In HA: **Settings → Automations & Scenes → Create Automation → Use Blueprint**

1. Create one automation from **WITB+ Occupancy** — bind your door/motion sensors and the generated `input_boolean`, `input_datetime`, and `timer` helpers.
2. Create one automation from **WITB+ Actions - Lights + Fan** — bind `binary_sensor.<slug>_occupied_effective` as `occupied_effective`, then bind your lights, fan, and actions helpers.

---

## Step 6 — Verify

Check these entities exist and respond:

| Entity | Expected |
|---|---|
| `input_boolean.office_occupied` | Controlled by WITB+ automation |
| `binary_sensor.office_occupied_effective` | `on` when occupied |
| `binary_sensor.office_witb_override_active` | `on` only when an override is active |
| `sensor.office_minutes_since_motion` | Counts up from last motion event |

Trigger motion or open/close the door — `input_boolean.office_occupied` should flip accordingly.

---

## Other blueprints

| Blueprint | Template | Notes |
|---|---|---|
| Transit Room (hallway) | `transit_helpers_package_template.yaml` | PIR-only, no door needed |
| Bathroom Fan | `room_humidity_baseline_delta_package_template.yaml` | Requires a delta sensor |
| Vacuum Job Manager | `vacuum_job_helpers.yaml` (copy directly) | No generator needed |
| Bed Sensor | none | Reuses WITB+ v4 helpers |

See [`docs/blueprints/README.md`](blueprints/README.md) for the full compatibility matrix.
