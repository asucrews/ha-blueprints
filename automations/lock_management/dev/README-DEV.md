# Lock Management Stable

**Warning**: AI was used to write and format this readme.

## Overview

Lock Management Stable is an automation blueprint designed for managing door locks with additional auto-lock functionality based on specified conditions and triggers.

## Assumptions

- User must have Lock Code Manager configured and working by [Raman325](https://github.com/raman325/lock_code_manager).
- It is assumed that users have configured their door locks and timers correctly within their home automation system.
- Users are expected to ensure that the necessary triggers and conditions are met for the automation to function as intended.

## Inputs

### Required Entities

- **Lock:**
  - **Description:** Lock entity to be controlled.
  - **Selector:** Allows selecting a lock entity. Only one lock can be selected.

### Optional Entities

- **Door Sensor or Door Sensor Group:**
  - **Description:** Select the door sensor or group of door sensors where occupancy is detected.
  - **Default:** `binary_sensor.none`
  - **Selector:** Allows selecting a door sensor entity. Only one door sensor or group can be selected.

- **Auto Lock Timer:**
  - **Description:** Timer entity for auto-lock functionality.
  - **Default:** `timer.none`
  - **Selector:** Allows selecting a timer entity. Only one timer can be selected.

### Notification Entities

- **Easy Notify Group - Devices Notified:**
  - **Description:** Select devices to receive notifications if enabled.
  - **Default:** ""
  - **Selector:** Allows selecting devices for notification. Only entity IDs after `notify.` should be provided.

## Variables

- **lock:** Input variable representing the selected lock entity.
- **auto_lock_timer:** Input variable representing the selected auto-lock timer entity.
- **door_sensor:** Input variable representing the selected door sensor entity or group.

## Triggers

- **LCM Event:**
  - Triggered by the event type `lock_code_manager_lock_state_changed` with specific entity ID.
- **Timer Finished:**
  - Triggered when the selected auto-lock timer transitions from active to idle state.

## Action

The action section defines sequences of actions to be executed based on the triggers and conditions:

- If the lock state changes to locked, and an auto-lock timer is set, cancel the timer if it's active.
- If the lock state changes to unlocked, and an auto-lock timer is set:
  - Cancel the timer if it's active.
  - Start the auto-lock timer.
- If the auto-lock timer finishes and the door is closed, it triggers the lock to be locked

## Mode

- **Queued:** Ensures that no more than 5 instances of this automation can run simultaneously.

## Source Code

The source code for Lock Management Blueprint can be found on GitHub:

- [View Source Code - Stable](https://github.com/asucrews/ha-blueprints/blob/main/automations/lock_management/lock_management.yaml)
- [View Source Code - Dev](https://github.com/asucrews/ha-blueprints/blob/main/automations/lock_management/dev/lock_management_dev.yaml)

## Future Enhancements

## Feedback

We value your input and welcome any feedback or suggestions you may have regarding the Lock Management Blueprint. Whether you have ideas for improvements, encountered issues during implementation, or simply want to share your experience using the blueprint, your feedback is invaluable to us.

Please feel free to leave your comments below or reach out to us on the Home Assistant forum. Your feedback helps us continually improve and refine our offerings for the community. Thank you for your support!
