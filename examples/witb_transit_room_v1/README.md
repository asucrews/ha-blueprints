# WITB Transit Room Driver v1 Examples

Blueprint source:
- `blueprints/automation/witb_transit_room/v1/witb_transit_room.yaml`

## Files

- `packages/hallway.yaml`
- `hallway_automation.yaml`

## How To Use

1. Copy `packages/hallway.yaml` into your Home Assistant packages directory, renaming as needed.
2. Ensure packages are loaded (`!include_dir_merge_named`).
3. Reload Home Assistant so helpers exist.
4. Copy `hallway_automation.yaml`, update `use_blueprint.path` and entity IDs.

## Notes

- The dummy keepalive and instant-off booleans are required by the blueprint even if those features are unused. Select them in the blueprint inputs when not using keepalive or instant-off.
- The suppress timer is required even if `instant_off_rearm_timeout_seconds` is `0`.
- Pair `binary_sensor`-compatible `occupied_effective` output with a WITB+ Actions v2 automation using `input_boolean.hallway_occupied_effective` (the blueprint drives this boolean directly).
