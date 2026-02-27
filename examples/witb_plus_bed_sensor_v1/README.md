# WITB+ Bed → Force Occupied v1 Examples

Blueprint source:
- `blueprints/automation/witb_plus_bed_sensor/v1/witb_plus_bed_force_occupied.yaml`

## Files

- `master_bedroom_bed_sensor_automation.yaml`

## How To Use

1. Ensure you already have a WITB+ v4 occupancy automation for the bedroom with a `force_occupied` input_boolean in its helper package.
2. Copy `master_bedroom_bed_sensor_automation.yaml`, update `use_blueprint.path` and entity IDs.
3. Tune `bed_on_delay` and `bathroom_grace` to match your sensor's ESPHome `delayed_off` config.

## No Separate Package File

This blueprint reuses helpers from the existing WITB+ v4 occupancy package (`force_occupied` and `occupied_effective`). No additional helper package is required.

## Sensor Variant Note

- **This blueprint:** use the Normal or Slow bed sensor variant (`binary_sensor.master_bedroom_bed_either_normal`). The debounce here filters quick sits.
- **Actions blueprint:** use the Fast variant (`binary_sensor.master_bedroom_bed_either_fast`) for instant lights-on suppression.
