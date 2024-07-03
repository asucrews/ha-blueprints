# Car Tag Stable (0.2.2)

## Description
Car ESPHome Tag - Opens and Closes Garage Door

## Source
[GitHub - Car Tag Stable](https://github.com/asucrews/ha-blueprints/blob/main/automations/car_tag/car_tag.yaml)

## Domain
Automation

## Home Assistant Minimum Version
2024.6.0

## Inputs

### Required Entities
The required entities for this automation.

- **ESPHome BLE Sensor**
  - **Selector**: `entity`
  - **Domain**: `binary_sensor`
  - **Multiple**: false

- **ESPHome Node Status**
  - **Selector**: `entity`
  - **Integration**: `esphome`
  - **Domain**: `binary_sensor`
  - **Multiple**: true

- **Garage Door Cover**
  - **Name**: Garage Door Cover
  - **Description**: Garage Door Cover?
  - **Selector**: `entity`
  - **Domain**: `cover`
  - **Multiple**: false

### Optional Entities
The optional entities for this automation.

- **Garage Door Timer Helper**
  - **Name**: Garage Door Timer Helper
  - **Description**: Garage Door Timer Helper
  - **Default**: `timer.none`
  - **Selector**: `entity`
  - **Integration**: `timer`
  - **Domain**: `timer`
  - **Multiple**: false

## Variables
- `esphome_ble`: Input ESPHome BLE sensor
- `esphome_node_status`: Input ESPHome node status
- `garage_door_cover`: Input garage door cover
- `garage_door_timer_helper`: Input garage door timer helper

## Triggers
- **ESPHome BLE Found**: Triggered when the ESPHome BLE sensor state changes from "off" to "on".
- **ESPHome BLE Not Found**: Triggered when the ESPHome BLE sensor state changes from "on" to "off".
- **Connected**: Triggered when the ESPHome node status changes from "off" to "on".
- **Disconnected**: Triggered when the ESPHome node status changes from "on" to "off".

## Actions
### On Connected
- **Open Garage Door**: Opens the garage door if it is currently closed or closing.

### On Disconnected
- **Start Timer**: Starts or restarts the garage door timer if the timer is active.

### On ESPHome BLE Found
- **Open Garage Door**: Opens the garage door if it is currently closed or closing.

### On ESPHome BLE Not Found
- **Start Timer**: Starts or restarts the garage door timer if the timer is active.

## Mode
- **Mode**: single
- **Max Exceeded**: silent
