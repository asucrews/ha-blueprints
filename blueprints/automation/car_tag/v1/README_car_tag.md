# Car Tag (1.4.0)

Car ESPHome Tag - Opens and Closes Garage Door.

## Blueprint Details

- **Name:** Car Tag (1.4.0)
- **Home Assistant Minimum Version:** 2024.6.0
- **Description:** Car ESPHome Tag - Opens and Closes Garage Door
- **Domain:** automation
- **Source URL:** [GitHub](https://github.com/asucrews/ha-blueprints/blob/main/automations/car_tag/car_tag.yaml)

## Design Notes

### Asymmetric Debounce
- **Open debounce is short (default 10s):** Nobody wants to wait in the driveway. A brief delay filters transient BLE noise without a noticeable lag on arrival.
- **Close debounce is long (default 5 min):** Closing the door is higher stakes — a false close is a safety risk. A longer delay confirms actual departure vs. momentary signal loss.

### WiFi Backup Trigger
If BLE misses the car tag, a secondary WiFi signal fires as a fallback open trigger. Two entity types are supported:

**Option A — Firewalla / Router `device_tracker` (preferred):**
When a Firewalla (or other router-based) HA integration is configured, it creates `device_tracker` entities per network device tracked by MAC address. If your car's infotainment system or a device in the car connects to home WiFi on arrival, that `device_tracker` transitioning `not_home → home` is a precise, car-specific signal.

To find your entity: open the Firewalla app → Devices, note the car device name, then find it under HA Settings → Devices & Services → Entities (search for the device name). The entity ID will look like `device_tracker.my_car_infotainment`.

**Option B — ESPHome node status `binary_sensor`:**
The ESPHome node's connectivity sensor (e.g. `binary_sensor.garage_ble_scanner_status`) fires `off → on` whenever the node comes online. Useful when no Firewalla or router integration is available, but less precise — it fires on any reboot or power event, not just car arrival.

Both options use the same `wifi_backup_entity` input and the same action branch. The trigger watches for `to: "on"` (binary_sensor) and `to: "home"` (device_tracker) simultaneously.

### WiFi Backup Safety Gates
The WiFi backup branch has two guards that are stricter than the BLE branches:

1. **`person_entity` is required, not optional.** If no person entity is configured, the WiFi backup branch is skipped entirely. A Firewalla device_tracker going `home` on a phone reconnect after sleep, or an ESPHome node rebooting overnight, would otherwise open the door. This is a hard requirement with no bypass.
2. **Dedup check.** If any BLE sensor is already `on` when the backup fires, the branch is skipped. BLE fired first — the door is already opening.

### Multiple Vehicle Support
`esphome_ble` accepts multiple sensors. Any detected tag triggers the automation. The notification message includes `trigger.entity_id` so you can see which sensor fired.

> **Note:** This blueprint starts a timer on departure but does not directly close the door. A companion automation triggered by the **Garage Door Timer Helper** firing is required to issue the actual `cover.close_cover` call.

---

## Inputs

### Required Entities

| Input | Description |
|---|---|
| ESPHome BLE Sensor(s) | Binary sensor(s) indicating BLE tag presence. Accepts multiple for multiple vehicles. |
| Garage Door Cover | Cover entity for the garage door |

### Optional Entities

| Input | Default | Description |
|---|---|---|
| Garage Door Timer Helper | *(none)* | Timer started on departure; companion automation closes the door when it fires |
| Person / Device Tracker | *(none)* | Confirmation gate — open only when `not_home`, start timer only when `home`. **Required for WiFi backup to function.** |
| WiFi Backup Trigger Entity | *(none)* | Fallback open trigger when BLE hasn't fired. Accepts `binary_sensor` (ESPHome node status) or `device_tracker` (Firewalla / router). Requires person entity. |
| Notification Target | *(none)* | Notify service to call on door events, e.g. `notify.mobile_app_iphone` |

### Timing

| Input | Default | Description |
|---|---|---|
| Open Debounce | `00:00:10` | BLE must be detected for this long before opening |
| Close Debounce | `00:05:00` | BLE must be absent for this long before starting the close timer |
| Open After | `00:00:00` | Earliest time auto-open is allowed |
| Open Before | `00:00:00` | Latest time auto-open is allowed. Set both to `00:00:00` to disable the window restriction. |

**Overnight windows are supported.** Setting `open_after: 22:00:00` and `open_before: 06:00:00` correctly allows opens from 10pm to 6am.

---

## Triggers

| Trigger ID | Description |
|---|---|
| `ESPHome BLE Found` | BLE tag detected (sustained for open debounce duration) |
| `ESPHome BLE Not Found` | BLE tag lost (sustained for close debounce duration) |
| `WiFi Backup Online` | WiFi backup entity reaches `on` (binary_sensor) or `home` (device_tracker) |

---

## Actions

### ESPHome BLE Found — Open
All conditions must pass:
1. Cover is not `unavailable`
2. Door is `closed`, `closing`, or `off`
3. Person entity is `not_home` *(or no person entity configured)*
4. Current time is within the open window *(or window is disabled)*

**Action:** Open the garage door, then send a notification *(if configured)*.

### ESPHome BLE Not Found — Start Close Timer
All conditions must pass:
1. Cover is not `unavailable`
2. Door is `open`, `opening`, or `on`
3. Timer helper is configured
4. Person entity is `home` *(or no person entity configured)*

**Action:** Start the close timer, then send a notification *(if configured)*.

### WiFi Backup Online — Fallback Open
All conditions must pass:
1. Cover is not `unavailable`
2. Door is `closed`, `closing`, or `off`
3. **Person entity is configured AND is `not_home`** *(hard requirement — skips entirely if no person entity)*
4. No BLE sensor is currently `on` *(dedup: BLE hasn't already opened the door)*
5. Current time is within the open window *(or window is disabled)*

**Action:** Open the garage door, then send a notification *(if configured)* indicating WiFi backup fired.

---

## Upgrading from v1.3.0

The `esphome_node_status` input has been renamed to `wifi_backup_entity`. After
updating the blueprint file, open the automation instance in the HA UI and
re-select your backup entity in the **WiFi Backup Trigger Entity** field.

---

## Companion Automation

The timer helper entity must be paired with a separate automation that closes the door when the timer fires:

```yaml
trigger:
  - trigger: event
    event_type: timer.finished
    event_data:
      entity_id: timer.garage_door_close_delay
action:
  - action: cover.close_cover
    target:
      entity_id: cover.garage_door
```

---

## Mode

- **Mode:** `single`
- **Max Exceeded:** `silent`
