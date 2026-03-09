# Car Tag Stable (0.2.2)

Car ESPHome Tag - Opens and Closes Garage Door.

## Blueprint Details

- **Name:** Car Tag Stable (0.2.2)
- **Home Assistant Minimum Version:** 2024.6.0
- **Description:** Car ESPHome Tag - Opens and Closes Garage Door
- **Domain:** automation
- **Source URL:** [GitHub](https://github.com/asucrews/ha-blueprints/blob/main/automations/car_tag/car_tag.yaml)

## Inputs

### Required Entities

#### ESPHome BLE

- **Selector:** entity (domain: binary_sensor, multiple: false)

#### ESPHome Node Status

- **Selector:** entity (integration: "esphome", domain: binary_sensor, multiple: true)

#### Garage Door Cover

- **Name:** Garage Door Cover
- **Description:** Garage Door Cover?
- **Selector:** entity (domain: cover, multiple: false)

### Optional Entities

#### Garage Door Timer Helper

- **Name:** Garage Door Timer Helper
- **Description:** Garage Door Timer Helper
- **Default:** timer.none
- **Selector:** entity (integration: "timer", domain: timer, multiple: false)

## Variables

- **esphome_ble:** !input esphome_ble
- **esphome_node_status:** !input esphome_node_status
- **garage_door_cover:** !input garage_door_cover
- **garage_door_timer_helper:** !input garage_door_timer_helper

## Triggers

1. **State Trigger:** When the ESPHome BLE entity changes state from "off" to "on".
2. **State Trigger:** When the ESPHome BLE entity changes state from "on" to "off".
3. **State Trigger:** When the ESPHome Node Status entity changes state from "off" to "on".
4. **State Trigger:** When the ESPHome Node Status entity changes state from "on" to "off".

## Actions

### On Connected

- **Conditions:**
  - Trigger ID: Connected
  - Garage door cover is in state "off", "closed", or "closing"
- **Sequence:**
  - Open the garage door cover.

### On Disconnected

- **Conditions:**
  - Trigger ID: Disconnected
  - Garage door cover is in state "on", "open", or "opening"
- **Sequence:**
  - If the garage door timer helper is active, cancel and start the timer.
  - If the garage door timer helper is not active, start the timer.

### On ESPHome BLE Found

- **Conditions:**
  - Trigger ID: ESPHome BLE Found
  - Garage door cover is in state "off", "closed", or "closing"
- **Sequence:**
  - Open the garage door cover.

### On ESPHome BLE Not Found

- **Conditions:**
  - Trigger ID: ESPHome BLE Not Found
  - Garage door cover is in state "on", "open", or "opening"
- **Sequence:**
  - If the garage door timer helper is active, cancel and start the timer.
  - If the garage door timer helper is not active, start the timer.

## Mode

- **Mode:** single
- **Max Exceeded:** silent