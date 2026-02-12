# ha-blueprints

Home Assistant blueprints and helper package generators.

This repository currently centers on a two-blueprint WITB+ workflow:
- Occupancy inference (`WITB+ v3`)
- Actions control for lights/fan (`WITB+ Actions - Lights + Fan`)

## Active Blueprints

1. `blueprints/automation/witb_plus/v3/witb_plus.yaml`
   - Docs: `blueprints/automation/witb_plus/v3/README.md`
   - Purpose: room occupancy inference from doors + motion (+ optional mmWave).

2. `blueprints/automation/witb_plus_actions_lights_fan/v1/witb_plus_actions_lights_fan.yaml`
   - Docs: `blueprints/automation/witb_plus_actions_lights_fan/v1/README.md`
   - Purpose: occupancy-driven light/fan actions with safety tags, run-on, and optional humidity/lux tuning.

## Helper Package Generators

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

## Repository Layout

- `blueprints/automation/`: current blueprint work.
- `legacy/v1/`: older blueprint collection and docs.
- `references/`: third-party references.
- `docs/`, `examples/`, `tools/`: reserved/support folders.

## Legacy

Older content remains under `legacy/v1/README.md`.
