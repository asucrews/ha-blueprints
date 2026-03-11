# Humidity Controlled Fan Examples

Blueprint source:
- `blueprints/automation/humidity_controled_fan/v1/humidity_controled_fan.yaml`

Companion package template:
- `blueprints/automation/humidity_controled_fan/v1/humidity_controled_fan_package_template.yaml`

## Files

- `rooms_humidity.example.yaml` — rooms config for the package generator
- `packages/master_bathroom_humidity_delta.yaml` — rendered package (baseline + delta sensors + tuning helpers)
- `master_bathroom_humidity_fan_automation.yaml` — automation example

## How To Use

1. **Generate the package** (or copy the example package file):
   - Edit `rooms_humidity.example.yaml` with your rooms and sensor entity IDs
   - Run: `python generate_witb_packages_templated.py --config rooms_humidity.yaml`
   - Copy the output to your HA packages folder
2. Ensure packages are loaded with `!include_dir_merge_named`.
3. Copy the automation YAML and update:
   - `use_blueprint.path` with your namespace
   - `delta_sensor` — `sensor.<room_slug>_humidity_delta` (from the package)
   - `fan_entity` — your fan switch or relay entity
4. Paste into your `automations.yaml` or HA YAML editor.

## Notes

- The package produces `sensor.<slug>_humidity_baseline` and `sensor.<slug>_humidity_delta`.
- The automation consumes the delta sensor and drives the fan via hysteresis thresholds.
- The `__HUMIDITY_SENSOR__` and `__FAN_ENTITY__` tokens in the rooms file must be filled in — they cannot be derived from the room slug.
