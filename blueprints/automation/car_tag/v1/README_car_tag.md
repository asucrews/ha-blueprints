# Car Tag (1.3.0)

Car ESPHome Tag - Opens and Closes Garage Door.

## Blueprint Details

- **Name:** Car Tag (1.3.0)
- **Home Assistant Minimum Version:** 2024.6.0
- **Description:** Car ESPHome Tag - Opens and Closes Garage Door
- **Domain:** automation
- **Source URL:** [GitHub](https://github.com/asucrews/ha-blueprints/blob/main/automations/car_tag/car_tag.yaml)

## Design Notes

### Asymmetric Debounce
- **Open debounce is short (default 10s):** Nobody wants to wait in the driveway. A brief delay filters transient BLE noise without a noticeable lag on arrival.
- **Close debounce is long (default 5 min):** Closing the door is higher stakes — a false close is a safety risk. A longer delay confirms actual departure vs. momentary signal loss.

### WiFi Backup Trigger
If BLE misses the car tag (e.g. the ESPHome scanner is mid-boot when the car pulls in), the node status sensor transitioning `off → on` acts as a fallback open trigger. The WiFi backup branch has two additional safety guards not present in the BLE branches:

1. **`person_entity` is required, not optional.** If no person entity is configured, the WiFi backup branch is skipped entirely. Node reboots, power blips, and OTA firmware updates all cause the node status to cycle — without the person gate this would open the door unsafely.
2. **Dedup check.** If any BLE sensor is already `on` when the node comes online, the WiFi branch is skipped. BLE fired first and the door is already opening.

### Connected/Disconnected Triggers Removed (v1.2.0)
The original node-connected triggers were removed in v1.2.0 due to the 2am-crash risk. The v1.3.0 WiFi backup re-introduces this capability safely via the mandatory person gate.

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
| ESPHome Node Status | *(none)* | WiFi backup trigger — opens door if node comes online and BLE hasn't already fired. Requires person entity. |
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
| `ESPHome Node Online` | ESPHome node WiFi status transitions off → on (WiFi backup, optional) |

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

### ESPHome Node Online — WiFi Backup Open
All conditions must pass:
1. Cover is not `unavailable`
2. Door is `closed`, `closing`, or `off`
3. **Person entity is configured AND is `not_home`** *(hard requirement — skips if no person entity)*
4. No BLE sensor is currently `on` *(dedup: BLE hasn't already opened the door)*
5. Current time is within the open window *(or window is disabled)*

**Action:** Open the garage door, then send a notification *(if configured)* indicating WiFi backup fired.

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
