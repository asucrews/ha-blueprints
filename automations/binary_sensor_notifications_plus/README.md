# Binary Sensor Notification (0.2.6)

## Description
Send a notification or trigger a custom action depending on the state switch of a binary_sensor.

## Source
[GitHub - Binary Sensor Notification](https://github.com/asucrews/ha-blueprints/blob/main/automations/binary_sensor_notifications_plus/binary_sensor_notifications_plus.yaml)

## Domain
Automation

## Home Assistant Minimum Version
2024.6.0

## Inputs

### Required Entities
The required entities for this automation.

- **Sensor**
  - **Description**: Sensor which triggers the notification.
  - **Selector**: `entity`
  - **Domain**: `binary_sensor`

- **Easy Notify Group - Devices Notified**
  - **Description**: If you've enabled device notifications above, please select the devices to receive the notifications. Enter only entity_id, the part after `notify`. This is only for notifications group, see [Home Assistant Notify Groups](https://www.home-assistant.io/integrations/group/#notify-groups).
  - **Default**: ""
  
- **Title**
  - **Description**: Notification title

### Optional Entities
The optional entities for this automation.

- **Message when entity is on**
  - **Description**: Message to be sent when the entity is on.
  - **Default**: "None"

- **Message when entity is off**
  - **Description**: Message to be sent when the entity is off.
  - **Default**: "None"

- **Message when entity is on for extended period of time**
  - **Description**: Message to be sent when the entity is on for an extended period of time.
  - **Default**: "None"

- **Left Open Timer Helper**
  - **Description**: Left Open Timer Helper
  - **Default**: `timer.none`
  - **Selector**: `entity`
  - **Domain**: `timer`

- **Debounce duration**
  - **Description**: Duration time the notification won't be sent again after the sensor changed its state.
  - **Default**: 10 seconds
  - **Selector**: `number`
  - **Min**: 0
  - **Max**: 100
  - **Unit of Measurement**: "s"
  - **Mode**: slider
  - **Step**: 1

## Variables
- `sensor_entity`: Input sensor entity
- `debounce_duration`: Input debounce duration
- `left_open_timer_helper`: Input left open timer helper
- `notify_group`: Input notify group
- `title`: Input title
- `message_open`: Input message when entity is on
- `message_close`: Input message when entity is off
- `message_left`: Input message when entity is on for an extended period of time

## Triggers
- **Opened**: Triggered when the sensor entity state changes from "on" to "off".
- **Closed**: Triggered when the sensor entity state changes from "off" to "on".
- **Timer Finished**: Triggered when the left open timer finishes.

## Conditions
- **Debounce Duration**: Ensures that the notification is not sent again within the debounce duration.

## Actions
### On Opened
- **Notification**: Sends a notification with the `message_open`.
- **Start Timer**: Starts the left open timer.

### On Closed
- **Notification**: Sends a notification with the `message_close`.
- **Cancel Timer**: Cancels the left open timer.

### On Timer Finished
- **Notification**: Sends a notification with the `message_left` if the sensor entity is still on.
- **Restart Timer**: Restarts the left open timer.

## Mode
- **Mode**: single
- **Max Exceeded**: silent
