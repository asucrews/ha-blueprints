# Smart Vents - Flair (0.2.0)

Automation blueprint for managing smart vents using Flair.

## Blueprint Details

- **Name:** Smart Vents - Flair (0.2.0)
- **Description:** Automation blueprint for managing smart vents using Flair.
- **Home Assistant Minimum Version:** 2024.6.0
- **Domain:** automation
- **Source URL:** [GitHub](https://github.com/asucrews/ha-blueprints/blob/main/automations/smart_vents/flair.yaml)

## Inputs

### Required Entities

#### Door Sensor, Door Sensor Group, or Occupancy Helper

- **Name:** Door Sensor, Door Sensor Group, or Occupancy Helper
- **Description:** Select the door sensor, group of door sensors, or Occupancy Helper.
- **Selector:** entity (domain: binary_sensor, input_boolean, multiple: false)

#### Flair Activity Status

- **Name:** Flair Activity Status
- **Description:** Flair Activity Status
- **Selector:** entity (domain: select, multiple: false)

#### Flair Clear Hold Button

- **Name:** Flair Clear Hold Button
- **Description:** Flair Clear Hold Button
- **Selector:** entity (domain: button, multiple: false)

### Optional Entities

#### Door Sensor Open Delay (Optional)

- **Name:** Door Sensor Open Delay
- **Description:** Specify the delay time, in seconds, for the door sensor to register an open event after detecting movement.
- **Default:** 0
- **Selector:** number (mode: box, min: 0.0, max: 60.0, unit_of_measurement: seconds, step: 1.0)

#### Door Sensor Close Delay (Optional)

- **Name:** Door Sensor Close Delay
- **Description:** Specify the delay time, in seconds, for the door sensor to register a close event after detecting no movement.
- **Default:** 0
- **Selector:** number (mode: box, min: 0.0, max: 60.0, unit_of_measurement: seconds, step: 1.0)

#### HVAC Smart Sensor Occupancy

- **Name:** HVAC Smart Sensor Occupancy
- **Description:** HVAC Smart Sensor Occupancy
- **Default:** "binary_sensor.none"
- **Selector:** entity (domain: binary_sensor, multiple: false)

## Variables

- **room_occupancy_sensor:** !input room_occupancy_sensor
- **door_sensor_open_delay:** !input door_sensor_open_delay
- **door_sensor_close_delay:** !input door_sensor_close_delay
- **flair_activity_status:** !input flair_activity_status
- **flair_clear_hold:** !input flair_clear_hold
- **hvac_smart_sensor_occupancy:** !input hvac_smart_sensor_occupancy

## Triggers

1. **Room Occupied**
   - **Platform:** state
   - **Entity ID:** !input room_occupancy_sensor
   - **From:** "off"
   - **To:** "on"
   - **ID:** Room Occupied
   - **For:** !input door_sensor_open_delay

2. **Room Unoccupied**
   - **Platform:** state
   - **Entity ID:** !input room_occupancy_sensor
   - **From:** "on"
   - **To:** "off"
   - **ID:** Room Unoccupied
   - **For:** !input door_sensor_close_delay

3. **HVAC Occupied**
   - **Platform:** state
   - **Entity ID:** !input hvac_smart_sensor_occupancy
   - **From:** "off"
   - **To:** "on"
   - **ID:** HVAC Occupied

4. **HVAC Unoccupied**
   - **Platform:** state
   - **Entity ID:** !input hvac_smart_sensor_occupancy
   - **From:** "on"
   - **To:** "off"
   - **ID:** HVAC Unoccupied

## Actions

### On Room Occupied

- **Conditions:** Trigger ID is Room Occupied
- **Sequence:**
  - **Service:** select.select_option
    - **Data:**
      - **Option:** Active
    - **Target:** !input flair_activity_status
  - **Service:** button.press
    - **Data:** {}
    - **Target:** !input flair_clear_hold

### On Room Unoccupied

- **Conditions:** Trigger ID is Room Unoccupied
- **Sequence:**
  - **Service:** select.select_option
    - **Data:**
      - **Option:** Active
    - **Target:** !input flair_activity_status
  - **Service:** button.press
    - **Data:** {}
    - **Target:** !input flair_clear_hold

### On HVAC Occupied

- **Conditions:**
  - Trigger ID is HVAC Occupied
  - **State:** !input room_occupancy_sensor is "on"
- **Sequence:**
  - **Service:** select.select_option
    - **Data:**
      - **Option:** Active
    - **Target:** !input flair_activity_status
  - **Service:** button.press
    - **Data:** {}
    - **Target:** !input flair_clear_hold

### On HVAC Unoccupied

- **Conditions:**
  - Trigger ID is HVAC Unoccupied
  - **State:** !input room_occupancy_sensor is "on"
- **Sequence:**
  - **Service:** select.select_option
    - **Data:**
      - **Option:** Inactive
    - **Target:** !input flair_activity_status
  - **Service:** button.press
    - **Data:** {}
    - **Target:** !input flair_clear_hold

## Mode

- **Mode:** single
- **Max Exceeded:** silent