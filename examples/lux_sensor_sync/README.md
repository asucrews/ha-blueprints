# Lux Sensor Sync Examples

Blueprint source:
- `blueprints/automation/lux_sensor_sync/v1/lux_sensor_sync.yaml`

Companion package template:
- `blueprints/automation/lux_sensor_sync/v1/lux_sensor_sync_package_template.yaml`

## Files

- `rooms_lux.example.yaml` — rooms config for the package generator
- `packages/office_lux_delta.yaml` — rendered package (baseline + delta sensors + tuning helpers)
- `office_lux_sync_automation.yaml` — automation example

## How To Use

1. **Generate the package** (or copy the example package file):
   - Edit `rooms_lux.example.yaml` with your rooms and sensor entity IDs
   - Run: `python generate_witb_packages_templated.py --config rooms_lux.yaml`
   - Copy the output to your HA packages folder
2. Ensure packages are loaded with `!include_dir_merge_named`.
3. Copy the automation YAML and update:
   - `use_blueprint.path` with your namespace
   - `delta_sensor` — `sensor.<room_slug>_lux_delta` (from the package)
   - `light_boolean` — `input_boolean.<room_slug>_fan_light_inferred` (from the package)
4. Paste into your `automations.yaml` or HA YAML editor.

## Notes

- The package produces `sensor.<slug>_lux_baseline` and `sensor.<slug>_lux_delta`.
- The automation consumes the delta and keeps `light_boolean` in sync with the physical light state.
- Use `light_boolean` as the `light_gating_entity` in WITB+ Actions v3 to prevent auto lights-on when the room light is already on.
- The `__LUX_SENSOR__` token in the rooms file must be filled in per room.
