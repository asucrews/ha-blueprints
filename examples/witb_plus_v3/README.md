# WITB+ v3 Examples

Blueprint source:
- `blueprints/automation/witb_plus/v3/witb_plus.yaml`

## Files

- `packages/office.yaml`
- `packages/master_bathroom_toilet.yaml`
- `office_automation.yaml`
- `master_bathroom_toilet_automation.yaml`

## How To Use

1. Copy package files to your Home Assistant packages folder.
2. Ensure packages are loaded with `!include_dir_merge_named`.
3. Copy automation example YAML and update:
   - `use_blueprint.path`
   - entity IDs in `input`
4. Reload helpers, templates, and automations.
