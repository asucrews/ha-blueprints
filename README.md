# ha-blueprints

Home Assistant blueprints and helper package generators.

This repository currently centers on a WITB+ occupancy/action workflow plus related automation and script blueprints:
- Occupancy inference for enclosed rooms (`WITB+ v4`)
- Occupancy inference for transit areas / hallways (`WITB Transit Room Driver v1`)
- Bedroom sleep guard to prevent false vacancy while in bed (`WITB+ Bed → Force Occupied v1`)
- Actions control for lights/fan (`WITB+ Actions - Lights + Fan`)
- Bathroom fan control from humidity delta (`Bathroom Fan From Humidity Delta`)
- Vacuum Job Manager automation for iRobot jobs + helper state + optional WITB overrides
- Optional resilient light hook scripts for VZW31-SN smart-bulb setups

## Quick Links

- Blueprint docs index: [`docs/blueprints/README.md`](docs/blueprints/README.md)
- Example configs: [`examples/README.md`](examples/README.md)
- Reference links: [`references/README.md`](references/README.md)
- Doc backlog: [`todo.md`](todo.md)

## Active Blueprint Files

1. [`blueprints/automation/witb_plus/v4/witb_plus.yaml`](blueprints/automation/witb_plus/v4/witb_plus.yaml)
   - Docs: [`blueprints/automation/witb_plus/v4/README.md`](blueprints/automation/witb_plus/v4/README.md)
   - Purpose: room occupancy inference from doors + motion (+ optional mmWave).

2. [`blueprints/automation/witb_plus_actions_lights_fan/v2/witb_plus_actions_lights_fan.yaml`](blueprints/automation/witb_plus_actions_lights_fan/v2/witb_plus_actions_lights_fan.yaml)
   - Docs: [`blueprints/automation/witb_plus_actions_lights_fan/v2/README.md`](blueprints/automation/witb_plus_actions_lights_fan/v2/README.md)
   - Purpose: occupancy-driven light/fan actions with safety tags, run-on, and optional humidity/lux tuning.

3. [`blueprints/automation/bathroom_fan_from_humidity/v1/bathroom_fan_from_humidity_delta.yaml`](blueprints/automation/bathroom_fan_from_humidity/v1/bathroom_fan_from_humidity_delta.yaml)
   - Docs: [`blueprints/automation/bathroom_fan_from_humidity/v1/README.md`](blueprints/automation/bathroom_fan_from_humidity/v1/README.md)
   - Purpose: humidity-delta-based bathroom fan control with hysteresis and runtime safety limits.

4. [`blueprints/automation/vacuum_job_manager/v1/vacuum_job_manager.yaml`](blueprints/automation/vacuum_job_manager/v1/vacuum_job_manager.yaml)
   - Docs: [`blueprints/automation/vacuum_job_manager/v1/README.md`](blueprints/automation/vacuum_job_manager/v1/README.md)
   - Purpose: queued/scheduled vacuum job orchestration with mission-counter completion and optional WITB/light integration.

5. [`blueprints/automation/witb_transit_room/v1/witb_transit_room.yaml`](blueprints/automation/witb_transit_room/v1/witb_transit_room.yaml)
   - Docs: [`blueprints/automation/witb_transit_room/v1/README.md`](blueprints/automation/witb_transit_room/v1/README.md)
   - Purpose: PIR-only occupancy driver for hallways/stairs using hold-timer decay; outputs WITB-compatible `occupied_effective` signal.

6. [`blueprints/automation/witb_plus_bed_sensor/v1/witb_plus_bed_force_occupied.yaml`](blueprints/automation/witb_plus_bed_sensor/v1/witb_plus_bed_force_occupied.yaml)
   - Docs: [`blueprints/automation/witb_plus_bed_sensor/v1/README.md`](blueprints/automation/witb_plus_bed_sensor/v1/README.md)
   - Purpose: bedroom sleep guard — drives `force_occupied` to prevent WITB+ from clearing occupancy while someone is in bed.

7. [`blueprints/script/witb_switch_light_profiles/v1/witb_lights_on_hook_vzw31sn.yaml`](blueprints/script/witb_switch_light_profiles/v1/witb_lights_on_hook_vzw31sn.yaml)
   - Docs: [`blueprints/script/witb_switch_light_profiles/v1/README.md`](blueprints/script/witb_switch_light_profiles/v1/README.md)
   - Purpose: resilient ON hook for bulbs behind VZW31-SN (recovery, rechecks, notifications).

8. [`blueprints/script/witb_switch_light_profiles/v1/witb_lights_off_hook_vzw31sn.yaml`](blueprints/script/witb_switch_light_profiles/v1/witb_lights_off_hook_vzw31sn.yaml)
   - Docs: [`blueprints/script/witb_switch_light_profiles/v1/README.md`](blueprints/script/witb_switch_light_profiles/v1/README.md)
   - Purpose: resilient OFF hook for bulbs behind VZW31-SN (recovery, rechecks, notifications).

## Helper Packages and Generators

Run from repo root.

1. Generate occupancy helpers/templates:

```bash
python blueprints/generate_witb_packages_templated.py \
  --rooms "Office" "Master Bathroom Toilet" \
  --template blueprints/automation/witb_plus/v4/witb_plus_package_template.yaml \
  --out blueprints/automation/witb_plus/v4/packages
```

2. Generate actions helpers:

```bash
python blueprints/generate_witb_packages_templated.py \
  --rooms "Office" "Master Bathroom Toilet" \
  --template blueprints/automation/witb_plus_actions_lights_fan/v2/room_witb_actions_package_template.yaml \
  --out blueprints/automation/witb_plus_actions_lights_fan/v2/packages
```

3. Generate bathroom humidity helper packages:

```bash
python blueprints/generate_witb_packages_templated.py \
  --rooms "Half Bathroom" \
  --template blueprints/automation/bathroom_fan_from_humidity/v1/room_humidity_baseline_delta_package_template.yaml \
  --out blueprints/automation/bathroom_fan_from_humidity/v1/packages
```

Generated files are helper/package YAML files. Automations are created in the Home Assistant UI from blueprints.

4. Vacuum helpers template:

```bash
# POSIX shell example:
cp blueprints/automation/vacuum_job_manager/v1/vacuum_job_helpers.yaml packages/roomba_vacjob.yaml
```

```powershell
# PowerShell example:
Copy-Item "blueprints/automation/vacuum_job_manager/v1/vacuum_job_helpers.yaml" "packages/roomba_vacjob.yaml"
```

```yaml
# Ensure packages are loaded in Home Assistant
homeassistant:
  packages: !include_dir_merge_named packages/
```

## Repository Layout

- `blueprints/automation/`: current blueprint work.
- `blueprints/script/`: current script blueprint work.
- `docs/`: implementation docs and blueprint compatibility matrix.
- `examples/`: copy-ready package and automation examples.
- `references/`: official Home Assistant docs links and third-party references.
- `tools/`: utility scripts and validation helpers.
- `legacy/v1/`: older blueprint collection and docs.

## Legacy

Older content remains under [`legacy/v1/README.md`](legacy/v1/README.md).
