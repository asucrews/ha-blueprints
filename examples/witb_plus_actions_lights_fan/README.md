# WITB+ Actions - Lights + Fan v1 Examples

Blueprint source:
- `blueprints/automation/witb_plus_actions_lights_fan/v2/witb_plus_actions_lights_fan.yaml`

## Files

- `packages/office_witb_actions.yaml`
- `packages/master_bathroom_toilet_witb_actions.yaml`
- `office_actions_automation.yaml`
- `master_bathroom_toilet_actions_automation.yaml`

## How To Use

1. Copy package files to your Home Assistant packages folder.
2. Ensure packages are loaded with `!include_dir_merge_named`.
3. Copy automation example YAML and update:
   - `use_blueprint.path`
   - entity IDs in `input`
4. Point `occupied_effective` to your WITB+ effective occupancy sensor (currently from `witb_plus/v4`).
