# Car Tag - Garage Door Examples

Blueprint source:
- `blueprints/automation/car_tag/v1/car_tag.yaml`

## Files

- `car_tag_automation.yaml`

## How To Use

1. Copy `car_tag_automation.yaml` and update:
   - `use_blueprint.path` with your namespace
   - `esphome_ble` — your BLE presence binary sensor(s)
   - `garage_door_cover` — your cover entity
   - `person_entity` — your person/device tracker (strongly recommended)
   - `garage_door_timer_helper` — create a `timer` helper in HA for auto-close delay
   - `esphome_node_status` — your ESPHome node connectivity sensor (optional)
   - `notify_target` — your notification service (optional)
2. Paste the result into your `automations.yaml` or HA YAML editor.
3. Create a companion automation to close the door when `garage_door_timer_helper` fires.
