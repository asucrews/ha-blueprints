# Changelog — Car Tag Blueprint

All notable changes to this blueprint are documented here.

---

## [1.3.0] - 2026-03-10

### Added
- **WiFi backup trigger (`esphome_node_status`):** Optional binary sensor input
  for the ESPHome node's connectivity status. When the node comes online and BLE
  has not already detected the tag, the door opens as a fallback. Handles the
  case where the car enters BLE range while the scanner is mid-boot and misses
  the initial advertisement window.
- **Dedup guard on WiFi backup branch:** Checks that no BLE sensor is currently
  `on` before acting. Prevents the WiFi trigger from double-firing milliseconds
  after BLE has already opened the door.

### Safety Notes
- The WiFi backup branch enforces a **hard `person_entity` requirement**: if no
  person entity is configured, the branch is skipped entirely. Node reboots,
  power blips, and firmware OTA events all cause the node status sensor to
  transition `off → on`; without the person gate this would open the door
  unsafely. This is intentionally stricter than the BLE branches, which allow
  operation without a person gate.

### Changed
- `esphome_ble` added to `variables` block (required to evaluate the dedup guard
  template across all action branches).

---

## [1.2.0] - 2026-03-09

### Added
- **Multiple BLE sensor support:** `esphome_ble` now accepts `multiple: true`.
  Any detected tag triggers the automation. `trigger.entity_id` is included in
  notification messages to identify which sensor fired. Supports multiple
  vehicles in a single blueprint instance.
- **Person / Device Tracker confirmation gate (`person_entity`):** Optional
  input accepting `person` or `device_tracker` domains. When configured, open
  only fires when entity is `not_home`; close timer only fires when `home`.
  Prevents acting on stale BLE state when the vehicle is already inside.
- **Notification support (`notify_target`):** Optional text input for a notify
  service (e.g. `notify.mobile_app_iphone`). Sends a titled notification on
  door open and on close timer start, including the triggering entity ID.
- **Time-of-day window (`open_after` / `open_before`):** Optional time inputs
  restricting when auto-open is permitted. Overnight windows supported (e.g.
  22:00–06:00). Set both to `00:00:00` to disable the restriction entirely.
- **`unavailable` state guard:** Each action branch now checks that the cover
  entity is not `unavailable` before attempting to actuate. Prevents silent
  failures during Z-Wave or cover integration outages.

### Removed
- **`Connected` / `Disconnected` triggers and all associated action branches.**
  ESPHome node reboot events are no longer used to actuate the door. The BLE
  Found trigger fires within seconds of node recovery anyway, and the reboot
  path introduced an unacceptable risk of the door opening on a 2am node crash.
- **`esphome_node_status` input** (no longer needed with triggers removed).

### Changed
- `esphome_ble` selector changed from `multiple: false` to `multiple: true`.

---

## [1.1.0] - 2026-03-09

### Added
- `open_debounce` input (default `00:00:10`): BLE Found trigger now requires
  sustained detection before opening. Filters transient noise without
  noticeable delay on arrival.
- `close_debounce` input (default `00:05:00`): BLE Not Found trigger now
  requires sustained absence before starting the close timer. Confirms actual
  departure vs. brief signal loss.

### Fixed
- `garage_door_timer_helper` default changed from `timer.none` to `[]`.
  The previous default caused HA to reject automations with `entity_id: None`.
- Added `{{ garage_door_timer_helper | length > 0 }}` guard on all timer
  action branches to prevent errors when no timer helper is selected.
- Removed redundant `timer.cancel` + `timer.start` sequence. `timer.start`
  on an already-active timer restarts it automatically.
- Removed `metadata: {}` noise from timer actions.
- `Connected` trigger: added BLE state guard to prevent door opening on node
  reboot when car is not present.
- Restored `integration: esphome` filter on node status selector.

### Changed
- Blueprint version aligned to `1.1.0` (README showed `0.2.2`, YAML showed
  `1.0.0`).
- `min_version` corrected to `2024.6.0` (was incorrectly `2025.6.0`).

---

## [1.0.0] - Initial YAML Release

- Core open/close logic via BLE Found/Not Found triggers
- ESPHome node Connected/Disconnected triggers
- Optional timer helper for close delay
- `mode: single`, `max_exceeded: silent`
