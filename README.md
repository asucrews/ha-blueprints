# ha-blueprints

Home Assistant blueprints and helper package generators.

This repository currently centers on a WITB+ occupancy/action workflow plus related automation and script blueprints:
- Occupancy inference (`WITB+ v3`)
- Actions control for lights/fan (`WITB+ Actions - Lights + Fan`)
- Optional resilient light hook scripts for VZW31-SN smart-bulb setups
- Vacuum Job Manager automation for iRobot jobs + helper state + optional WITB overrides

## Quick Links

- Blueprint docs index: `docs/blueprints/README.md`
- Example configs: `examples/README.md`
- Reference links: `references/README.md`
- Doc backlog: `todo.md`

## Active Blueprint Files

1. `blueprints/automation/witb_plus/v3/witb_plus.yaml`
   - Docs: `blueprints/automation/witb_plus/v3/README.md`
   - Purpose: room occupancy inference from doors + motion (+ optional mmWave).

2. `blueprints/automation/witb_plus_actions_lights_fan/v1/witb_plus_actions_lights_fan.yaml`
   - Docs: `blueprints/automation/witb_plus_actions_lights_fan/v1/README.md`
   - Purpose: occupancy-driven light/fan actions with safety tags, run-on, and optional humidity/lux tuning.

3. `blueprints/automation/vacuum_job_manager/v1/vacuum_job_manager.yaml`
   - Docs: `blueprints/automation/vacuum_job_manager/v1/README.md`
   - Purpose: queued/scheduled vacuum job orchestration with mission-counter completion and optional WITB/light integration.

4. `blueprints/script/witb_lights/v1/witb_lights_on_hook_profile_vzw31_sn_switch_bulb_v1_7.yaml`
   - Docs: `blueprints/script/witb_lights/v1/README.md`
   - Purpose: resilient ON hook for bulbs behind VZW31-SN (recovery, rechecks, notifications).

5. `blueprints/script/witb_lights/v1/witb_lights_off_hook_profile_vzw31_sn_switch_bulb_v1_7.yaml`
   - Docs: `blueprints/script/witb_lights/v1/README.md`
   - Purpose: resilient OFF hook for bulbs behind VZW31-SN (recovery, rechecks, notifications).

## Helper Packages and Generators

Run from repo root.

1. Generate occupancy helpers/templates:

```bash
python blueprints/automation/witb_plus/v3/generate_witb_packages.py \
  --rooms "Office" "Master Bathroom Toilet" \
  --out blueprints/automation/witb_plus/v3/packages
```

2. Generate actions helpers:

```bash
python blueprints/automation/witb_plus_actions_lights_fan/v1/generate_witb_plus_actions_packages.py \
  --rooms "Office" "Master Bathroom Toilet" \
  --out blueprints/automation/witb_plus_actions_lights_fan/v1/packages
```

Generated files are helper-only package YAML files. Automations are created in the Home Assistant UI from blueprints.

3. Vacuum helpers template:

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

Older content remains under `legacy/v1/README.md`.
