# Blueprint Docs

This folder contains implementation-focused documentation for the active blueprints in this repository.

## Automation Blueprints

1. [WITB+ v3 Occupancy](./witb_plus_v3.md)
   - Source: `blueprints/automation/witb_plus/v3/witb_plus.yaml`
   - Companion helpers generator: `blueprints/automation/witb_plus/v3/generate_witb_packages.py`

2. [WITB+ Actions - Lights + Fan v1](./witb_plus_actions_lights_fan_v1.md)
   - Source: `blueprints/automation/witb_plus_actions_lights_fan/v1/witb_plus_actions_lights_fan.yaml`
   - Companion helpers generator: `blueprints/automation/witb_plus_actions_lights_fan/v1/generate_witb_plus_actions_packages.py`

## Relationship

- `WITB+ v3` infers room occupancy.
- `WITB+ Actions` consumes `binary_sensor.<slug>_occupied_effective` and handles lights/fan behavior.
