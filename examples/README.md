# Examples

Copy-ready examples for the active blueprints in this repository.

## Contents

- `witb_plus/`
  - Occupancy package and automation examples (WITB+ v4 blueprint).
- `witb_plus_actions_lights_fan/`
  - Actions package and automation examples (WITB+ Actions v2 and v3 blueprints).
- `vacuum_job_manager/`
  - Vacuum helper package and automation example.
- `witb_lights/`
  - Script-hook instance examples and WITB actions binding snippet for VZW31-SN profiles.
- `witb_transit_room/`
  - Transit room (hallway) package and automation examples (WITB Transit Room Driver v1).
- `witb_plus_bed_sensor/`
  - Bed sensor automation example (WITB+ Bed → Force Occupied v1; reuses existing WITB+ v4 helpers).
- `humidity_controlled/`
  - Humidity baseline/delta package and fan automation example (Humidity Controlled Fan v1 blueprint).
- `lux_sensor_sync/`
  - Lux baseline/delta package and light-inference automation example (Lux Sensor Sync v1 blueprint).
- `car_tag/`
  - BLE-based garage door automation example (Car Tag v1 blueprint).
- `flair/`
  - Flair smart vent activity automation example (Flair v1 blueprint).
- `ratgdo/`
  - Ratgdo 2.5i garage door automation example (Ratgdo v2 blueprint).
- `zooz/`
  - Zooz Z-Wave switch button-mapping example (Zooz All Light Switch v1 blueprint).

## Notes

- Package YAML files are meant for `homeassistant.packages`.
- Automation YAML files are meant for `automations.yaml` (or UI YAML mode).
- Replace entity IDs and blueprint `path` values with your own.
