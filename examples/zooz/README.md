# Zooz Z-Wave Switch Examples

Blueprint source:
- `blueprints/automation/zooz_all_light_switch_modified/v1/zooz-all.yaml`

Supports: ZEN71, ZEN72, ZEN76, ZEN77 (and 800LR variants)

## Files

- `zooz_automation.yaml`

## How To Use

1. Copy `zooz_automation.yaml` and update:
   - `use_blueprint.path` with your namespace
   - `zooz-switch` — find your device ID in HA under **Settings > Devices & Services > Z-Wave JS > your device**
   - `on_hook_script` / `off_hook_script` — script instances from the WITB Lights ON/OFF Hook blueprints (see `examples/witb_lights/`). Remove or set to `""` if not using WITB.
   - Fill in `button_a`, `button_b`, and multi-tap actions as needed
2. Paste into your `automations.yaml` or HA YAML editor.

## Notes

- `on_hook_script` overrides `button_a` (1x press). `off_hook_script` overrides `button_b` (1x press).
- Multi-tap actions (`button_a2`, `button_b3`, etc.) are always active regardless of hook scripts.
- For non-WITB rooms, remove both hook script inputs and define `button_a` / `button_b` directly.
