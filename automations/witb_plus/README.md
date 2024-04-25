# WITB+ (Wasp in the Box Plus) Blueprint

## Overview

WITB+ (Wasp in the Box Plus) is an advanced automation blueprint designed for occupancy detection using multiple sensors. This blueprint is inspired by the concept of "Wasp in a Box" and employs motion and door sensors to monitor occupants within a defined space (the "box"). When motion is detected, indicating the presence of a "wasp" (occupant), the box's state is updated accordingly. The generated binary sensor reflects the presence or absence of a wasp in the box, enabling seamless integration with automation triggers.


[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fasucrews%2Fha-blueprints%2Fblob%2Fmain%2Fautomations%2Fwitb_plus%2Fwitb_plus.yaml)

## Assumptions

- Motion sensors are typically positioned to detect movement when someone walks into the room, triggering occupancy detection.
- It is assumed that as long as the door to the designated area ("box") is closed, the room is considered occupied, influencing the automation's behavior.
- Users are expected to configure motion and door sensors accurately to detect occupancy within the designated area.
- The blueprint provides options to control smart light bulbs, light switches, and fans within the area based on occupancy detection.
- Users are expected to create input_boolean entities for occupancy tracking and bypass control if they choose to utilize these features.
- For bypass functionality, users need to manually integrate call service actions into their automations or methods to control devices when bypassing occupancy detection is required.

## Inputs

### Door Sensor

- **Description**: Select the door sensor representing the entrance to the designated area.
- **Type**: Binary Sensor
- **Selector**: Allows only a single selection.

### Motion Sensor

- **Description**: Choose the motion sensor responsible for detecting movement within the designated area.
- **Type**: Binary Sensor
- **Selector**: Allows only a single selection.

### Smart Light Bulb

- **Description**: Select a smart light bulb to control within the designated area.
- **Type**: Light
- **Selector**: Allows only a single selection. Default: 'light.none'.

### Light Switch

- **Description**: Choose a light switch to control within the designated area.
- **Type**: Light or Switch
- **Selector**: Allows only a single selection. Default: 'light.none'.

### Fan Switch

- **Description**: Select a fan to control within the designated area.
- **Type**: Fan or Light
- **Selector**: Allows only a single selection. Default: 'fan.none'.

### Door Sensor Open Delay

- **Description**: Specify the delay time, in seconds, for the door sensor to register an open event after detecting movement.
- **Type**: Number
- **Selector**: Allows selection within a range (Default: 0 seconds).
- **Min Value**: 0 seconds
- **Max Value**: 60 seconds

### Door Sensor Close Delay

- **Description**: Specify the delay time, in seconds, for the door sensor to register a close event after detecting no movement.
- **Type**: Number
- **Selector**: Allows selection within a range (Default: 0 seconds).
- **Min Value**: 0 seconds
- **Max Value**: 60 seconds

### Motion off Delay

- **Description**: Set the delay time, in seconds, for the motion sensor to turn off after detecting no movement.
- **Type**: Number
- **Selector**: Allows selection within a range (Default: 30 seconds).
- **Min Value**: 0 seconds
- **Max Value**: 3600 seconds

### Occupancy Helper

- **Description**: Select an input boolean entity to serve as an occupancy helper within the designated area.
- **Type**: Input Boolean
- **Selector**: Allows only a single selection. Default: 'input_boolean.none'.

### Bypass Mode

- **Description**: Select the bypass mode to control how the automation handles bypass events.
- **Type**: Dropdown
- **Selector**: Allows selection from predefined options. Default: No Bypass.
- **Options**:
  - No Bypass
  - Bypass No Auto OFF
  - Bypass Auto OFF

### Bypass Helper

- **Description**: Select an input boolean entity to serve as a bypass helper within the designated area.
- **Type**: Input Boolean
- **Selector**: Allows only a single selection. Default: 'input_boolean.none'.

### Bypass Auto Off Timer

- **Description**: Set the duration, in seconds, for the automatic cancellation of a bypass event.
- **Type**: Timer
- **Selector**: Allows only a single selection. Default: 'timer.none'.

### Bypass Action After Timer Finished

- **Description**: Specify the action to be taken after the bypass auto-off timer finishes counting down.
- **Type**: Dropdown
- **Selector**: Allows selection from predefined options. Default: Turn Off.
- **Options**:
  - Turn Off
  - Do Nothing

## Source Code

The source code for WITB+ Blueprint can be found on GitHub:
[View Source Code - Stable](https://raw.githubusercontent.com/asucrews/ha-blueprints/main/automations/witb_plus/witb_plus.yaml)
[View Source Code - Dev](https://raw.githubusercontent.com/asucrews/ha-blueprints/main/automations/witb_plus/witb_plus_dev.yaml)

## Future Enhancements
- **Additional Lighting Controls:** We plan to expand the capabilities of the blueprint by incorporating more advanced lighting controls. This could include adjusting brightness, changing colors, or even integrating scene selection functionality.
- **Customization Options:** We aim to provide users with more customization options to tailor the blueprint to their specific needs and preferences. This might involve configurable parameters for sensitivity, timing, or integration with other devices.
- **Integration with Environmental Sensors:** In future iterations, we envision integrating the blueprint with environmental sensors to enhance automation based on factors like ambient light, temperature, or humidity.
- **Improved Bypass Functionality:** We're exploring ways to enhance the bypass functionality to make it more intuitive and user-friendly. This could involve simplifying the setup process or adding additional bypass modes for greater flexibility.
- **Time of Day Events:** We're considering adding time-based events to the blueprint, allowing users to configure different behaviors based on the time of day. This could include features like nightlight settings, where the lighting adjusts automatically based on the time, creating a more comfortable environment during nighttime hours.

## Feedback

We value your input and welcome any feedback or suggestions you may have regarding the WITB+ Blueprint. Whether you have ideas for improvements, encountered issues during implementation, or simply want to share your experience using the blueprint, your feedback is invaluable to us.

Please feel free to leave your comments below or reach out to us on the Home Assistant forum. Your feedback helps us continually improve and refine our offerings for the community. Thank you for your support!
