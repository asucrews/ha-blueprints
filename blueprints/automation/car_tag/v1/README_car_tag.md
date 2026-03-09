# Car Tag (1.2.0)

Car ESPHome Tag - Opens and Closes Garage Door.

## Blueprint Details

- **Name:** Car Tag (1.2.0)
- **Home Assistant Minimum Version:** 2024.6.0
- **Description:** Car ESPHome Tag - Opens and Closes Garage Door
- **Domain:** automation
- **Source URL:** [GitHub](https://github.com/asucrews/ha-blueprints/blob/main/automations/car_tag/car_tag.yaml)

## Design Notes

### Asymmetric Debounce
- **Open debounce is short (default 10s):** Nobody wants to wait in the driveway. A brief delay filters transient BLE noise without a noticeable lag on arrival.
- **Close debounce is long (default 5 min):** Closing the door is higher stakes — a false close is a safety risk. A longer delay confirms actual departure vs. momentary signal loss.

### Connected/Disconnected Triggers Removed
ESPHome node reboot events are no longer used to actuate the door. The BLE Found trigger will fire within seconds of a node recovering anyway, and the reboot-based triggers introduced risk (door opening at 2am on a node crash). Removed in 1.2.0.

### Multiple Vehicle Support
`esphome_ble` now accepts multiple sensors. Any detected tag triggers the automation. The notification message includes `trigger.entity_id` so you can see which sensor fired.

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
| Person / Device Tracker | *(none)* | Confirmation gate — open only when `not_home`, start timer only when `home` |
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
