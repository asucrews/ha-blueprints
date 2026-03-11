# WITB+ Actions - Lights + Fan Examples

## v3 (current)

Blueprint source:
- `blueprints/automation/witb_plus_actions_lights_fan/v3/witb_plus_actions_lights_fan.yaml`

### Files

- `v3_office_actions_automation.yaml`
- `v3_master_bathroom_toilet_actions_automation.yaml`

### How To Use

1. Copy the relevant automation YAML and update:
   - `use_blueprint.path` with your namespace
   - `occupied_effective` — your WITB+ effective occupancy sensor (`binary_sensor.<slug>_occupied_effective`)
   - entity IDs in `input` to match your room helpers
2. Create any required timer/input_number helpers referenced in the example.
3. Paste into your `automations.yaml` or HA YAML editor.

> **Note:** v3 removed built-in humidity control and the illuminance gate selector.
> Use the `lux_sensor_sync` blueprint to produce a `light_gating_entity` binary sensor instead.

---

## v2 (legacy)

Blueprint source:
- `blueprints/automation/witb_plus_actions_lights_fan/v2/witb_plus_actions_lights_fan.yaml`

### Files

- `packages/office_witb_actions.yaml`
- `packages/master_bathroom_toilet_witb_actions.yaml`
- `office_actions_automation.yaml`
- `master_bathroom_toilet_actions_automation.yaml`

### How To Use

1. Copy package files to your Home Assistant packages folder.
2. Ensure packages are loaded with `!include_dir_merge_named`.
3. Copy automation example YAML and update:
   - `use_blueprint.path`
   - entity IDs in `input`
4. Point `occupied_effective` to your WITB+ effective occupancy sensor (from `witb_plus/v4`).
