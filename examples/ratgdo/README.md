# Ratgdo 2.5i Examples

Blueprint source:
- `blueprints/automation/ratgdo/v2/ratgdo_2.5i.yaml`

## Files

- `ratgdo_automation.yaml`

## How To Use

1. Copy `ratgdo_automation.yaml` and update:
   - `use_blueprint.path` with your namespace
   - `ratgdo_device` — your Ratgdo cover entity
   - `obstruction_entity` — your Ratgdo obstruction binary sensor
   - `garage_door_timer_helper` — create a `timer` helper in HA for auto-close (optional)
   - `bypass_helper` — create an `input_boolean` helper for bypass mode (optional)
   - `button_entity` — your Ratgdo wall button binary sensor (optional)
   - `notify_group` — your notification service name without `notify.` prefix (optional)
2. Paste into your `automations.yaml` or HA YAML editor.
