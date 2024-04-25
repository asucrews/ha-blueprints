# WITB+ (Wasp in the Box Plus) Blueprint 0.2.0

## Overview

WITB+ (Wasp in the Box Plus) is an advanced automation blueprint designed for occupancy detection using multiple sensors. This blueprint is inspired by the concept of "Wasp in a Box" and employs motion and door sensors to monitor occupants within a defined space (the "box"). When motion is detected, indicating the presence of a "wasp" (occupant), the box's state is updated accordingly. The generated binary sensor reflects the presence or absence of a wasp in the box, enabling seamless integration with automation triggers.

## Assumptions

- Motion sensors are typically positioned to detect movement when someone walks into the room, triggering occupancy detection.
- It is assumed that as long as the door to the designated area ("box") is closed, the room is considered occupied, influencing the automation's behavior.
- Users are expected to configure motion and door sensors accurately to detect occupancy within the designated area.
- The blueprint provides options to control smart light bulbs, light switches, and fans within the area based on occupancy detection.
- Users are expected to create input_boolean entities for occupancy tracking and bypass control if they choose to utilize these features.
- For bypass functionality, users need to manually integrate call service actions into their automations or methods to control devices when bypassing occupancy detection is required.

## Inputs

### Door Sensor

- **Description**: Select the door sensor or group of door sensors representing the entrance to the "box."
- **Type**: binary_sensor
- **Selector**: Allows only a single selection.

### Motion Sensor

- **Description**: Choose the motion sensor or group of motion sensors responsible for detecting movement within the designated area ("box").
- **Type**: binary_sensor
- **Selector**: Allows only a single selection.

### Light Bulbs (Optional)

- **Description**: Select a smart light bulb or group of smart light bulbs to control within the designated area ("box").
- **Type**: light
- **Selector**: Allows only a single selection. (Default value: 'light.none')

### Light Switch (Optional)

- **Description**: Choose a light, light group, switch, or switch group to control within the designated area ("box").
- **Type**: light or switch
- **Selector**: Allows only a single selection. (Default value: 'light.none')

### Fan Switch (Optional)

- **Description**: Select a fan or group of fans to control within the designated area ("box").
- **Type**: fan or light
- **Selector**: Allows only a single selection. (Default value: 'fan.none')

### Door Sensor Open Delay (Optional)

- **Description**: Specify the delay time, in seconds, for the door sensor to register an open event after detecting movement.
- **Type**: number
- **Selector**: Allows selection within a range (Default: 0 seconds).

### Door Sensor Close Delay (Optional)

- **Description**: Specify the delay time, in seconds, for the door sensor to register a close event after detecting no movement.
- **Type**: number
- **Selector**: Allows selection within a range (Default: 0 seconds).

### Motion off Delay (Optional)

- **Description**: Set the delay time, in seconds, for the motion sensor to turn off after detecting no movement.
- **Type**: number
- **Selector**: Allows selection within a range (Default: 30 seconds).

### Occupancy Helper (Optional)

- **Description**: Select an input boolean entity to serve as an occupancy helper within the designated area ("box").
- **Type**: input_boolean
- **Selector**: Allows only a single selection. (Default value: 'input_boolean.none')

### Bypass Mode (Optional)

- **Description**: Select the bypass mode to control how the automation handles bypass events.
- **Type**: dropdown
- **Options**: 
  - No Bypass
  - Bypass No Auto OFF
  - Bypass Auto OFF
- **Selector**: Allows selection from dropdown options. (Default value: No Bypass)

### Bypass Helper (Optional)

- **Description**: Select an input boolean entity to serve as a bypass helper within the designated area ("box").
- **Type**: input_boolean
- **Selector**: Allows only a single selection. (Default value: 'input_boolean.none')

### Bypass Auto Off Timer (Optional)

- **Description**: Set the duration, in seconds, for the automatic cancellation of a bypass event.
- **Type**: timer
- **Selector**: Allows only a single selection. (Default value: 'timer.none')

### Bypass Action After Timer Finished (Optional)

- **Description**: Specify the action to be taken after the bypass auto-off timer finishes counting down.
- **Type**: dropdown
- **Options**:
  - Turn Off
  - Do Nothing
- **Selector**: Allows selection from dropdown options. (Default value: Turn Off)

## Source Code

The source code for WITB+ Blueprint 0.2.0 can be found on GitHub:
[View Source Code](https://raw.githubusercontent.com/asucrews/ha-blueprints/main/automations/witb_plus/witb_plus.yaml)

