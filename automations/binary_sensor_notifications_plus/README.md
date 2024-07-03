# Binary Sensor Notification (0.2.6)

## Description
Send a notification or trigger a custom action depending on the state switch of a binary_sensor

## Source
[https://github.com/asucrews/ha-blueprints/blob/main/automations/binary_sensor_notifications_plus/binary_sensor_notifications_plus.yaml](https://github.com/asucrews/ha-blueprints/blob/main/automations/binary_sensor_notifications_plus/binary_sensor_notifications_plus.yaml)

## Domain
automation

## Home Assistant Minimum Version
2024.6.0

## Inputs

### Required Entities
The required entities for this automation

- **Sensor**
  - **Description**: Sensor which triggers the notification.
  - **Selector**: `{'entity': {'domain': 'binary_sensor'}}`

- **Easy Notify Group - Devices Notified**
  - **Description**: If you've enabled device notifications above, please select the devices to receive the notifications. Enter only entity_id, the part after notify. <br/> This is only for notifications group, see https://www.home-assistant.io/integrations/group/#notify-groups. <br/>Default value: "". Only change if you intend to use notifcations and this input is optional.<br/>

  - **Default**: 

- **Title**
  - **Description**: Notification title

### Optional Entities
The optional entities for this automation

- **Message when entity is on**
  - **Description**: Message to be sent
  - **Default**: None

- **Message when entity is off**
  - **Description**: Message to be sent
  - **Default**: None

- **Message when entity is on for extended period of time**
  - **Description**: Message to be sent
  - **Default**: None

- **Left Open Timer Helper**
  - **Description**: Left Open Timer Helper
  - **Default**: timer.none
  - **Selector**: `{'entity': {'domain': 'timer'}}`

- **Debounce duration**
  - **Description**: Duration time the notification won't be sent again after sensor changed its state.
  - **Default**: 10
  - **Selector**: `{'number': {'min': 0, 'max': 100, 'unit_of_measurement': 's', 'mode': 'slider', 'step': 1}}`

## Variables
- `sensor_entity`: None
- `debounce_duration`: None
- `left_open_timer_helper`: None
- `notify_group`: None
- `title`: None
- `message_open`: None
- `message_close`: None
- `message_left`: None

## Triggers
- **Opened**: Triggered when the state changes from `on` to `off`.
- **Closed**: Triggered when the state changes from `off` to `on`.
- **Timer Finished**: Triggered when the event changes from `Unknown` to `Unknown`.

## Conditions
- **template**: {
  {
    iif(this.attributes.last_triggered == None,
    9999,
    as_timestamp(now()) - as_timestamp(this.attributes.last_triggered,
    default=0) ) >= (debounce_duration | int),
  },
}


## Actions
### Unknown
- **notify.{{ notify_group }}**: {'title': "{{ title }} | {{ states('sensor.time') }}", 'message': '{{ message_open }}', 'data': {'ttl': 0, 'priority': 'high', 'tag': 't"tag-binary-sensor-notification"'}}
- **timer.start**: {}
### Unknown
- **notify.{{ notify_group }}**: {'title': "{{ title }} | {{ states('sensor.time') }}", 'message': '{{ message_close }}', 'data': {'ttl': 0, 'priority': 'high', 'tag': 'tag-binary-sensor-notification'}}
- **timer.cancel**: {}
### Unknown
- **notify.{{ notify_group }}**: {'title': "{{ title }} | {{ states('sensor.time') }}", 'message': '{{ message_left }}', 'data': {'ttl': 0, 'priority': 'high', 'tag': 'tag-binary-sensor-notification'}}
- **timer.start**: {}

## Mode
- **Mode**: single
- **Max Exceeded**: silent
