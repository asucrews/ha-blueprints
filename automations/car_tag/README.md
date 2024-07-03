# Car Tag Stable (0.2.2)

## Description
Car ESPHome Tag - Opens and Closes Garage Door

## Source
[https://github.com/asucrews/ha-blueprints/blob/main/automations/car_tag/car_tag.yaml](https://github.com/asucrews/ha-blueprints/blob/main/automations/car_tag/car_tag.yaml)

## Domain
automation

## Home Assistant Minimum Version
2024.6.0

## Inputs

### Required Entities
The required entities for this automation

- **Unnamed Input**
  - **Description**: No description
  - **Selector**: `{'entity': {'domain': ['binary_sensor'], 'multiple': False}}`

- **Unnamed Input**
  - **Description**: No description
  - **Selector**: `{'entity': {'integration': 'esphome', 'domain': ['binary_sensor'], 'multiple': True}}`

- **Garage Door Cover**
  - **Description**: Garage Door Cover?
  - **Selector**: `{'entity': {'domain': ['cover'], 'multiple': False}}`

### Optional Entities
The optional entities for this automation

- **Garage Door Timer Helper**
  - **Description**: Garage Door Timer Helper
  - **Default**: timer.none
  - **Selector**: `{'entity': {'integration': 'timer', 'domain': ['timer'], 'multiple': False}}`

## Variables
- `esphome_ble`: None
- `esphome_node_status`: None
- `garage_door_cover`: None
- `garage_door_timer_helper`: None

## Triggers
- **ESPHome BLE Found**: Triggered when the state changes from `off` to `on`.
- **ESPHome BLE Not Found**: Triggered when the state changes from `on` to `off`.
- **Connected**: Triggered when the state changes from `off` to `on`.
- **Disconnected**: Triggered when the state changes from `on` to `off`.

## Conditions

## Actions
### Unknown
- **cover.open_cover**: {}
### Unknown
- **Unknown service**: No data
### Unknown
- **cover.open_cover**: {}
### Unknown
- **Unknown service**: No data

## Mode
- **Mode**: single
- **Max Exceeded**: silent
