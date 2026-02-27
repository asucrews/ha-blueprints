# Examples

Copy-ready examples for the active blueprints in this repository.

## Contents

- `witb_plus_v3/`
  - Occupancy package and automation examples (for WITB+, currently paired with `witb_plus/v4` blueprint source).
- `witb_plus_actions_lights_fan_v1/`
  - Actions package and automation examples (blueprint file version string is currently `v2.x`).
- `vacuum_job_manager_v1/`
  - Vacuum helper package and automation example.
- `witb_lights_v1/`
  - Script-hook instance examples and WITB actions binding snippet for VZW31-SN profiles.
- `witb_transit_room_v1/`
  - Transit room (hallway) package and automation examples (for WITB Transit Room Driver v1).
- `witb_plus_bed_sensor_v1/`
  - Bed sensor automation example (WITB+ Bed → Force Occupied v1; reuses existing WITB+ v4 helpers).

## Notes

- Package YAML files are meant for `homeassistant.packages`.
- Automation YAML files are meant for `automations.yaml` (or UI YAML mode).
- Replace entity IDs and blueprint `path` values with your own.
