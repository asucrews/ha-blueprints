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

- Getting started (full guide): [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md)
- Getting started (quick start): [`docs/QUICKSTART.md`](docs/QUICKSTART.md)
- Blueprint docs index: [`docs/blueprints/README.md`](docs/blueprints/README.md)
- Example configs: [`examples/README.md`](examples/README.md)
- Reference links: [`references/README.md`](references/README.md)
- Naming standards: [`NAMING.md`](NAMING.md)
- Contributing: [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Doc backlog: [`todo.md`](todo.md)

## Active Blueprint Files

1. [`blueprints/automation/witb_plus/v4/witb_plus.yaml`](blueprints/automation/witb_plus/v4/witb_plus.yaml)
   - Docs: [`blueprints/automation/witb_plus/v4/README_witb_plus_v4.md`](blueprints/automation/witb_plus/v4/README_witb_plus_v4.md)
   - Purpose: room occupancy inference from doors + motion (+ optional mmWave).

2. [`blueprints/automation/witb_plus_actions_lights_fan/v3/witb_plus_actions_lights_fan.yaml`](blueprints/automation/witb_plus_actions_lights_fan/v3/witb_plus_actions_lights_fan.yaml)
   - Docs: [`blueprints/automation/witb_plus_actions_lights_fan/v3/README_witb_plus_actions_lights_fan_v3.md`](blueprints/automation/witb_plus_actions_lights_fan/v3/README_witb_plus_actions_lights_fan_v3.md)
   - Purpose: occupancy-driven light/fan actions with safety tags, timer-driven run-on/soft-off flows, and external light/fan gating hooks.

3. [`blueprints/automation/humidity_controled_fan/v1/humidity_controled_fan.yaml`](blueprints/automation/humidity_controled_fan/v1/humidity_controled_fan.yaml)
   - Docs: [`blueprints/automation/humidity_controled_fan/v1/README_humidity_controled_fan_v1.md`](blueprints/automation/humidity_controled_fan/v1/README_humidity_controled_fan_v1.md)
   - Purpose: humidity-delta-based bathroom fan control with hysteresis and runtime safety limits.

4. [`blueprints/automation/vacuum_job_manager/v1/vacuum_job_manager.yaml`](blueprints/automation/vacuum_job_manager/v1/vacuum_job_manager.yaml)
   - Docs: [`blueprints/automation/vacuum_job_manager/v1/README_vacuum_job_manager_v1.md`](blueprints/automation/vacuum_job_manager/v1/README_vacuum_job_manager_v1.md)
   - Purpose: queued/scheduled vacuum job orchestration with mission-counter completion and optional WITB/light integration.

5. [`blueprints/automation/witb_transit_room/v1/witb_transit_room.yaml`](blueprints/automation/witb_transit_room/v1/witb_transit_room.yaml)
   - Docs: [`blueprints/automation/witb_transit_room/v1/README_witb_transit_room_v1.md`](blueprints/automation/witb_transit_room/v1/README_witb_transit_room_v1.md)
   - Purpose: PIR-only occupancy driver for hallways/stairs using hold-timer decay; outputs WITB-compatible `occupied_effective` signal.

6. [`blueprints/automation/witb_plus_bed_sensor/v1/witb_plus_bed_force_occupied.yaml`](blueprints/automation/witb_plus_bed_sensor/v1/witb_plus_bed_force_occupied.yaml)
   - Docs: [`blueprints/automation/witb_plus_bed_sensor/v1/README_witb_plus_bed_force_occupied_v1.md`](blueprints/automation/witb_plus_bed_sensor/v1/README_witb_plus_bed_force_occupied_v1.md)
   - Purpose: bedroom sleep guard — drives `force_occupied` to prevent WITB+ from clearing occupancy while someone is in bed.

7. [`blueprints/script/witb_switch_light_profiles/v1/witb_lights_on_hook_vzw31sn.yaml`](blueprints/script/witb_switch_light_profiles/v1/witb_lights_on_hook_vzw31sn.yaml)
   - Docs: [`blueprints/script/witb_switch_light_profiles/v1/README_witb_lights_hooks_vzw31sn_v1.md`](blueprints/script/witb_switch_light_profiles/v1/README_witb_lights_hooks_vzw31sn_v1.md)
   - Purpose: resilient ON hook for bulbs behind VZW31-SN (recovery, rechecks, notifications).

8. [`blueprints/script/witb_switch_light_profiles/v1/witb_lights_off_hook_vzw31sn.yaml`](blueprints/script/witb_switch_light_profiles/v1/witb_lights_off_hook_vzw31sn.yaml)
   - Docs: [`blueprints/script/witb_switch_light_profiles/v1/README_witb_lights_hooks_vzw31sn_v1.md`](blueprints/script/witb_switch_light_profiles/v1/README_witb_lights_hooks_vzw31sn_v1.md)
   - Purpose: resilient OFF hook for bulbs behind VZW31-SN (recovery, rechecks, notifications).

9. [`blueprints/automation/car_tag/v1/car_tag.yaml`](blueprints/automation/car_tag/v1/car_tag.yaml)
   - Docs: [`blueprints/automation/car_tag/v1/README_car_tag_v1.md`](blueprints/automation/car_tag/v1/README_car_tag_v1.md)
   - Purpose: BLE car tag + WiFi backup garage door automation; rising/falling BLE edges drive open/close with asymmetric debounce, time window, person gate, and notification support.

10. [`blueprints/automation/air_purifier/v1/air_purifier.yaml`](blueprints/automation/air_purifier/v1/air_purifier.yaml)
    - Docs: [`blueprints/automation/air_purifier/v1/README_air_purifier_v1.md`](blueprints/automation/air_purifier/v1/README_air_purifier_v1.md)
    - Purpose: twice-daily boost schedule for air purifier groups with periodic reconciler and HA-restart guard.

11. [`blueprints/automation/ratgdo/v2/ratgdo_2.5i.yaml`](blueprints/automation/ratgdo/v2/ratgdo_2.5i.yaml)
    - Docs: [`blueprints/automation/ratgdo/v2/README_ratgdo_v2.md`](blueprints/automation/ratgdo/v2/README_ratgdo_v2.md)
    - Purpose: Ratgdo 2.5i garage door mechanics — auto-close, obstruction safety, bypass, physical button session cancel, and notifications.

12. [`blueprints/automation/lux_sensor_sync/v1/lux_sensor_sync.yaml`](blueprints/automation/lux_sensor_sync/v1/lux_sensor_sync.yaml)
    - Docs: [`blueprints/automation/lux_sensor_sync/v1/README_lux_sensor_sync_v1.md`](blueprints/automation/lux_sensor_sync/v1/README_lux_sensor_sync_v1.md)
    - Purpose: infers light on/off state from an adaptive lux-delta sensor; writes to an `input_boolean` for use as a WITB+ `light_gating_entity`.

13. [`blueprints/automation/flair/v1/flair.yaml`](blueprints/automation/flair/v1/flair.yaml)
    - Docs: [`blueprints/automation/flair/v1/README_flair_v1.md`](blueprints/automation/flair/v1/README_flair_v1.md)
    - Purpose: WITB+ `occupied_effective` → Flair smart vent Active/Inactive control with reconciliation and startup sync.

14. [`blueprints/automation/zooz_all_light_switch_modified/v1/zooz-all.yaml`](blueprints/automation/zooz_all_light_switch_modified/v1/zooz-all.yaml)
    - Docs: [`blueprints/automation/zooz_all_light_switch_modified/v1/README_zooz_all_light_switch_modified_v1.md`](blueprints/automation/zooz_all_light_switch_modified/v1/README_zooz_all_light_switch_modified_v1.md)
    - Purpose: maps 1x–5x press and held events on Zooz ZEN71/72/76/77 switches to configurable actions with optional WITB+ ON/OFF hook script routing.

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
  --template blueprints/automation/witb_plus_actions_lights_fan/v3/witb_plus_actions_lights_fan_package_template.yaml \
  --out blueprints/automation/witb_plus_actions_lights_fan/v3/packages
```

3. Generate bathroom humidity helper packages:

```bash
python blueprints/generate_witb_packages_templated.py \
  --rooms "Half Bathroom" \
  --template blueprints/automation/humidity_controled_fan/v1/humidity_controled_fan_package_template.yaml \
  --out blueprints/automation/humidity_controled_fan/v1/packages
```

Generated files are helper/package YAML files. Automations are created in the Home Assistant UI from blueprints.

4. Vacuum helpers template:

```bash
# POSIX shell example:
cp blueprints/automation/vacuum_job_manager/v1/vacuum_job_manager_package_template.yaml packages/roomba_vacjob.yaml
```

```powershell
# PowerShell example:
Copy-Item "blueprints/automation/vacuum_job_manager/v1/vacuum_job_manager_package_template.yaml" "packages/roomba_vacjob.yaml"
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
