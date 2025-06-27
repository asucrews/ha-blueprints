# Binary Sensor Notification (0.2.6)

Send a notification or trigger a custom action depending on the state switch of a binary_sensor.

## Blueprint Details

- **Name:** Binary Sensor Notification (0.2.6)
- **Description:** Send a notification or trigger a custom action depending on the state switch of a binary_sensor.
- **Source URL:** [GitHub](https://github.com/asucrews/ha-blueprints/blob/main/automations/binary_sensor_notifications_plus/binary_sensor_notifications_plus.yaml)
- **Domain:** automation
- **Home Assistant Minimum Version:** 2024.6.0

## Inputs

### Required Entities

#### Sensor

- **Name:** Sensor
- **Description:** Sensor which triggers the notification.
- **Selector:** entity (domain: binary_sensor)

#### Notify Group

- **Name:** Easy Notify Group - Devices Notified
- **Description:** 
  If you've enabled device notifications above, please select the devices to receive the notifications. Enter only entity_id, the part after notify.
  This is only for notifications group, see [Home Assistant Notify Groups](https://www.home-assistant.io/integrations/group/#notify-groups).
  Default value: "". Only change if you intend to use notifications and this input is optional.
- **Default:** ""

#### Title

- **Name:** Title
- **Description:** Notification title

### Optional Entities

#### Message when entity is on

- **Name:** Message when entity is on
- **Description:** Message to be sent
- **Default:** "None"

#### Message when entity is off

- **Name:** Message when entity is off
- **Description:** Message to be sent
- **Default:** "None"

#### Message when entity is on for extended period of time

- **Name:** Message when entity is on for extended period of time
- **Description:** Message to be sent
- **Default:** "None"

#### Left Open Timer Helper

- **Name:** Left Open Timer Helper
- **Description:** Left Open Timer Helper
- **Default:** timer.none
- **Selector:** entity (domain: timer)

#### Debounce Duration

- **Name:** Debounce duration
- **Description:** Duration time the notification won't be sent again after sensor changed its state.
- **Default:** 10
- **Selector:** number (min: 0, max: 100, unit_of_measurement: "s", mode: slider, step: 1)

## Variables

- **sensor_entity:** !input sensor_entity
- **debounce_duration:** !input debounce_duration
- **left_open_timer_helper:** !input left_open_timer_helper
- **notify_group:** !input notify_group
- **title:** !input title
- **message_open:** !input message_open
- **message_close:** !input message_close
- **message_left:** !input message_left

## Triggers

1. **State Trigger:** When the entity changes state from "on" to "off".
2. **State Trigger:** When the entity changes state from "off" to "on".
3. **Event Trigger:** When the specified timer finishes.

## Conditions

1. **Template Condition:** Ensure the debounce duration has passed since the last trigger.

## Actions

### On Opened

- **Conditions:**
  - Trigger ID: Opened
  - Message when entity is on is not "None"
- **Sequence:**
  - Send notification to the notify group with the specified title and message.
  - Start the left open timer.

### On Closed

- **Conditions:**
  - Trigger ID: Closed
  - Message when entity is off is not "None"
- **Sequence:**
  - Send notification to the notify group with the specified title and message.
  - Cancel the left open timer.

### On Timer Finished

- **Conditions:**
  - Trigger ID: Timer Finished
  - Message when entity is on for extended period of time is not "None"
  - The entity state is "on"
- **Sequence:**
  - Send notification to the notify group with the specified title and message.
  - Restart the left open timer.

## Mode

- **Mode:** single
- **Max Exceeded:** silent
