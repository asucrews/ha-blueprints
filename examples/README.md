# Examples

Copy-ready examples for the active blueprints in this repository.

## Contents

- `witb_plus/`
  - Occupancy package and automation examples (WITB+ v4 blueprint).
- `witb_plus_actions_lights_fan/`
  - Actions package and automation examples (WITB+ Actions v2 blueprint).
- `vacuum_job_manager/`
  - Vacuum helper package and automation example.
- `witb_lights/`
  - Script-hook instance examples and WITB actions binding snippet for VZW31-SN profiles.
- `witb_transit_room/`
  - Transit room (hallway) package and automation examples (WITB Transit Room Driver v1).
- `witb_plus_bed_sensor/`
  - Bed sensor automation example (WITB+ Bed → Force Occupied v1; reuses existing WITB+ v4 helpers).

## Notes

- Package YAML files are meant for `homeassistant.packages`.
- Automation YAML files are meant for `automations.yaml` (or UI YAML mode).
- Replace entity IDs and blueprint `path` values with your own.
