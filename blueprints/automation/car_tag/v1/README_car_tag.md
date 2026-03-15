# Car Tag Automation Blueprint

A Home Assistant blueprint that automates garage door control using a BLE car tag sensor, with a WiFi backup trigger for resilience when the ESPHome node is temporarily offline.

## How It Works

The automation listens for state changes on a BLE iBeacon group sensor attached to the car. Since the tag is only `on` when the car is on, the rising and falling edges of that signal carry clear intent:

- `off → on` (car turned on) → open the garage door
- `on → off` (car turned off) → start the close timer

A WiFi backup trigger fires when the ESPHome node comes back online after being down, catching cases where the BLE rising edge was missed.

## Requirements

- ESPHome node with BLE scanning (ESP32 or ESP32-S3 recommended)
- BLE iBeacon tag in the car powered by the car's ignition
- Ratgdo or compatible garage door cover entity
- HA timer helper for the close delay
- Person entity (optional, used for WiFi backup arriving case)

## Inputs

| Input | Description | Default |
|---|---|---|
| `esphome_ble` | BLE iBeacon group binary sensor(s) | required |
| `garage_door_cover` | Garage door cover entity | required |
| `garage_door_timer_helper` | Timer helper for auto-close delay | required |
| `wifi_backup_entity` | ESPHome node connectivity sensor | required |
| `person_entity` | Person entity for arriving confirmation | optional |
| `open_debounce` | How long BLE must be detected before opening | 5 seconds |
| `close_debounce` | How long BLE must be absent before starting close timer | 30 seconds |
| `open_after` | Earliest time door will auto-open | 00:00:00 (disabled) |
| `open_before` | Latest time door will auto-open | 00:00:00 (disabled) |
| `notify_target` | Notification service (e.g. notify.mobile_app_phone) | optional |

## Use Cases

See [use-cases.md](USE-CASES_car_tag.md) for the full list of supported scenarios.

## Rules

See [rules.md](RULES_car_tag.md) for the full rule set governing this automation.

## Race Condition Handling

When BLE and WiFi backup signals arrive close together, double-action is prevented naturally by the door state gate — if either path already opened the door, the other sees it is no longer `closed` and does nothing.

## Version History

See [CHANGELOG.md](CHANGELOG_car_tag.md) for full version history and release notes.

## Notes

- The `wifi_backup_entity` should be the ESPHome node's own connectivity sensor (`binary_sensor.{node}_status`), **not** a phone or Firewalla tracker. It is specifically for catching missed BLE edges when the node was temporarily offline.
- The physical wall button on the Ratgdo cancels the auto-close timer for the current session.
- Time window (`open_after` / `open_before`) applies to both BLE and WiFi backup open paths. Set both to `00:00:00` to disable.

## File Structure

```
car_tag.yaml        # Blueprint
rules.md            # Automation rules
use-cases.md        # Supported use cases
README.md           # This file
CHANGELOG.md        # Version history
```
