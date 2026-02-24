# WITB (Wasp-in-the-Box) Occupancy v4

This folder contains the WITB occupancy blueprint and the templated package generator used to create per-room helpers.

## Files

- `witb_plus.yaml`: occupancy blueprint (automation domain).
- `generate_witb_packages_templated.py`: helper/template package generator.
- `witb_plus_package.template.yaml`: template used by the generator.
- `packages/`: output location for generated room package files.

## What the Blueprint Does

WITB infers occupancy for one room using:
- one seal door (privacy/main door behavior),
- one or more transition doors,
- PIR motion,
- optional mmWave support.

Core behavior:
- event-driven occupancy inference (no polling loop),
- optional entry window gating,
- optional failsafe timer behavior,
- optional per-room control helpers (`automation_override`, `force_occupied`, `manual_occupied`).

Create automations from this blueprint in the Home Assistant UI.

## Package Helpers

Generated package files define helpers/templates only (not automations). Load them with:

```yaml
homeassistant:
  packages: !include_dir_merge_named packages/
```

Typical entities include:
- `input_boolean.<slug>_occupied`
- `input_datetime.<slug>_last_motion`
- `input_datetime.<slug>_last_door`
- `input_datetime.<slug>_last_exit_door` (optional)
- `timer.<slug>_failsafe` (optional)
- `binary_sensor.<slug>_occupied_effective` (template sensor)

## Generator Usage

```bash
python generate_witb_packages_templated.py \
  --rooms "Office" "Master Bathroom Toilet" \
  --template witb_plus_package.template.yaml \
  --out ./packages
```

Or run from repo root:

```bash
python blueprints/automation/witb_plus/v4/generate_witb_packages_templated.py \
  --rooms "Office" "Master Bathroom Toilet" \
  --template blueprints/automation/witb_plus/v4/witb_plus_package.template.yaml \
  --out blueprints/automation/witb_plus/v4/packages
```
