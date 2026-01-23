# Lock Management Stable (0.4.1)

Lock Management is an automation blueprint designed for managing door locks with additional auto-lock functionality based on specified conditions and triggers.

## Blueprint Details

- **Name:** Lock Management Stable (0.4.1)
- **Description:** 
    Lock Management is an automation blueprint designed for managing door locks with additional auto-lock functionality based on specified conditions and triggers.
    Requires Lock Code Manager by Raman325 ([GitHub](https://github.com/raman325/lock_code_manager)).
- **Home Assistant Minimum Version:** 2024.6.0
- **Domain:** automation
- **Source URL:** [GitHub](https://github.com/asucrews/ha-blueprints/blob/main/automations/lock_management/lock_management.yaml)

## Inputs

### Required Entities

#### Lock

- **Name:** Lock
- **Description:** Lock entity to manage
- **Selector:** entity (domain: lock, multiple: false)

### Optional Entities

#### Door Sensor or Door Sensor Group

- **Name:** Door Sensor or Door Sensor Group
- **Description:** 
    Select the door sensor or group of door sensors where occupancy is detected.
    Please note: This input is restricted to entities within the binary_sensor domain and allows only a single selection. This field and this input is optional.
- **Default:** binary_sensor.none
- **Selector:** entity (domain: binary_sensor, multiple: false)

#### Auto Lock Timer

- **Name:** Auto Lock Timer
- **Description:** 
    Set the duration, in seconds, for the automatic lock. After the specified time elapses, it will automatically lock; if the door sensor is enabled then the timer will reset if the door sensor shows open.
    To utilize this function, create a timer helper entity in your Home Assistant configuration or UI ([Timer Integration](https://www.home-assistant.io/integrations/timer/)).
    Default value: 'timer.none'. Only change if you intend to use this field and this input is optional.
- **Default:** timer.none
- **Selector:** entity (domain: timer, multiple: false)

#### Easy Notify Group - Devices Notified

- **Name:** Easy Notify Group - Devices Notified
- **Description:** 
    If you've enabled device notifications above, please select the devices to receive the notifications. Enter only entity_id, the part after notify.
    This is only for notifications group, see [Home Assistant Notify Groups](https://www.home-assistant.io/integrations/group/#notify-groups).
    Default value: "". Only change if you intend to use notifications and this input is optional.
- **Default:** ""

## Variables

- **lock:** !input lock
- **door_sensor:** !input door_sensor
- **auto_lock_timer:** !input auto_lock_timer
- **notify_group:** !input notify_group

## Triggers

1. **Lock Code Manager Lock State Changed**
   - **Platform:** event
   - **Event Type:** lock_code_manager_lock_state_changed
   - **Event Data:**
     - **Entity ID:** !input lock
   - **ID:** LCM Event

2. **Timer Finished**
   - **Platform:** event
   - **Event Type:** timer.finished
   - **Event Data:**
     - **Entity ID:** !input auto_lock_timer
   - **ID:** Timer Finished

## Actions

### On Lock State Change (LCM Event)

- **Conditions:** Trigger ID is LCM Event
- **Sequence:**
  - Set lock_state, code_slot, code_slot_name, action_text from trigger event data.
  - **If locked:**
    - **If auto_lock_timer is set:** Cancel active auto_lock_timer if it is active.
    - **If notify_group is defined:** Send notification with lock state and user info (if applicable).
  - **If unlocked:**
    - **If auto_lock_timer is set:** 
      - Cancel active auto_lock_timer if it is active.
      - Start the auto_lock_timer.

### On Timer Finished

- **Conditions:**
  - auto_lock_timer is set
  - Trigger ID is Timer Finished
- **Sequence:**
  - **If door_sensor is on and defined:** Restart auto_lock_timer.
  - **Else:** Lock the lock.

## Mode

- **Mode:** single
- **Max Exceeded:** silent