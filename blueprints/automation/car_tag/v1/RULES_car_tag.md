# Car Tag Automation Rules

## Car Tag
- Tag is only `on` when car is on
- Trigger `off → on`: car turned on
- Trigger `on → off`: car turned off
- Open debounce: 5 seconds
- Close debounce: 30 seconds

## Door
- Must be `closed` before opening
- Must be `open` before closing
- Must not be `unavailable`

## Person Gate
- Confirms presence before acting
- Used in WiFi backup arriving case (UC5)

## Time Window
- `open_after` / `open_before` gate
- Set both to `00:00:00` to disable

## WiFi Backup
- Fires when ESPHome node comes back online
- Backup for when BLE rising edge was missed
- Independent of BLE state

## Race Condition Prevention
- **Rule 1:** WiFi fires → BLE comes on after → ignore BLE (WiFi already handled it)
- **Rule 2:** BLE fires → WiFi comes on after → ignore WiFi (BLE already handled it)
- Both RC1 and RC2 are enforced naturally by the door state gate — if either path already opened the door, the other sees it is no longer `closed` and does nothing

## Ratgdo
- Physical wall button cancels auto-close for current session
