# Motion+ Stable (0.2.1)

Motion+ automation blueprint for Home Assistant.

## Blueprint Details

- **Name:** Motion+ Stable (0.2.1)
- **Description:** Motion+ automation for managing motion sensors and associated devices.
- **Home Assistant Minimum Version:** 2024.6.0
- **Domain:** automation
- **Source URL:** [GitHub](https://github.com/asucrews/ha-blueprints/blob/main/automations/motion_plus/motion_plus.yaml)

## Inputs

### Required Entities

#### Motion Sensor or Motion Sensor Group

- **Name:** Motion Sensor or Motion Sensor Group
- **Description:** Choose the motion sensor or group of motion sensors responsible for detecting movement within the designated area.
- **Selector:** entity (domain: binary_sensor, multiple: false)

### Optional Entities

#### Motion off delay (Optional)

- **Name:** Motion off delay
- **Description:** Set the delay time, in seconds, for the motion sensor to turn off after detecting no movement.
- **Default:** 30
- **Selector:** number (mode: box, min: 0.0, max: 3600.0, unit_of_measurement: seconds, step: 1.0)

#### Smart Light Bulb, or Smart Light Bulb Group (Optional)

- **Name:** Smart Light Bulb, or Smart Light Bulb Group
- **Description:** Select a smart light bulb or group of smart light bulbs to control within the designated area.
- **Default:** "light.none"
- **Selector:** entity (domain: light, multiple: false)

#### Light, Light Group, Switch, or Switch Group (Optional)

- **Name:** Light, Light Group, Switch, or Switch Group
- **Description:** Choose a light, light group, switch, or switch group to control within the designated area.
- **Default:** "light.none"
- **Selector:** entity (domain: light, switch, multiple: false)

#### Fan or Fan Group (Optional)

- **Name:** Fan or Fan Group
- **Description:** Select a fan or group of fans to control within the designated area.
- **Default:** "fan.none"
- **Selector:** entity (domain: fan, light, multiple: false)

#### Occupancy Helper (Optional)

- **Name:** Occupancy Helper
- **Description:** Select an input boolean entity to serve as an occupancy helper within the designated area.
- **Default:** "input_boolean.none"
- **Selector:** entity (domain: input_boolean, multiple: false)

#### Bypass Mode (Optional)

- **Name:** Bypass Mode
- **Description:** Select the bypass mode to control how the automation handles bypass events.
- **Default:** no_bypass
- **Selector:** select (mode: dropdown, options: ["No Bypass", "Bypass No Auto OFF", "Bypass Auto OFF"], custom_value: false, multiple: false, sort: false)

#### Bypass Helper (Optional)

- **Name:** Bypass Helper
- **Description:** Select an input boolean entity to serve as a bypass helper within the designated area.
- **Default:** "input_boolean.none"
- **Selector:** entity (domain: input_boolean, multiple: false)

#### Bypass Auto Off Timer (Optional)

- **Name:** Bypass Auto Off Timer
- **Description:** Set the duration, in seconds, for the automatic cancellation of a bypass event.
- **Default:** "timer.none"
- **Selector:** entity (domain: timer, multiple: false)

#### Bypass Action After Timer Finished (Optional)

- **Name:** Bypass Action After Timer Finished
- **Description:** Specify the action to be taken after the bypass auto-off timer finishes counting down.
- **Default:** turn_off
- **Selector:** select (mode: dropdown, options: ["Turn Off", "Do Nothing"], custom_value: false, multiple: false, sort: false)

#### Idle Timer (Optional)

- **Name:** Idle Timer
- **Description:** Set the duration, in seconds, for the automatic cancellation of a bypass event.
- **Default:** "timer.none"
- **Selector:** entity (domain: timer, multiple: false)

#### Light Control

- **Name:** Light Control
- **Description:** What controls lighting effects? Is it a switch or bulb?
- **Default:** none
- **Selector:** select (mode: dropdown, options: ["None", "Bulb", "Switch"], custom_value: false, multiple: false, sort: false)

#### Light Control Features?

- **Name:** Light Control Features?
- **Description:** What light features to control?
- **Default:** []
- **Selector:** select (multiple: true, options: ["Use brightness", "Use colour temperature", "Use transition"])

#### Light brightness Percentage (Optional)

- **Name:** Light brightness Percentage
- **Description:** Light brightness Percentage 1 to 100%.
- **Default:** 1
- **Selector:** number (mode: box, min: 1, max: 100, unit_of_measurement: percentage, step: 1)

#### Light temperature (Optional)

- **Name:** Light temperature
- **Description:** Light temperature in Kelvin 2000 to 65000
- **Default:** 2000
- **Selector:** number (mode: box, min: 2000, max: 6500, unit_of_measurement: kelvin, step: 1)

#### Light Transition (Optional)

- **Name:** Light Transition
- **Description:** Light Transition 0 to 10 seconds
- **Default:** 0
- **Selector:** number (mode: box, min: 0, max: 10, unit_of_measurement: seconds, step: 1)

## Variables

- **motion_sensor:** !input motion_sensor
- **motion_sensor_delay:** !input motion_sensor_delay
- **light_bulbs:** !input light_bulbs
- **light_switch:** !input light_switch
- **fan_switch:** !input fan_switch
- **occupancy_helper:** !input occupancy_helper
- **bypass_mode:** !input bypass_mode
- **bypass_helper:** !input bypass_helper
- **bypass_timer:** !input bypass_timer
- **bypass_finished_action:** !input bypass_finished_action
- **idle_timer:** !input idle_timer
- **light_control:** !input light_control
- **light_control_features:** !input light_control_features
- **light_brightness_pct:** !input light_brightness_pct
- **light_temperature:** !input light_temperature
- **light_transition:** !input light_transition

## Triggers

1. **Motion Detected**
   - **Platform:** state
   - **Entity ID:** !input motion_sensor
   - **From:** "off"
   - **To:** "on"
   - **ID:** Motion On

2. **Motion Cleared**
   - **Platform:** state
   - **Entity ID:** !input motion_sensor
   - **From:** "on"
   - **To:** "off"
   - **ID:** Motion Off
   - **For:** !input motion_sensor_delay

3. **Bypass Enabled**
   - **Platform:** state
   - **Entity ID:** !input bypass_helper
   - **From:** "off"
   - **To:** "on"
   - **ID:** Bypass Turn on

4. **Bypass Disabled**
   - **Platform:** state
   - **Entity ID:** !input bypass_helper
   - **From:** "on"
   - **To:** "off"
   - **ID:** Bypass Turn off

5. **Bypass Auto Off Timer Ends**
   - **Platform:** event
   - **Event Type:** timer.finished
   - **Event Data:**
     - **Entity ID:** !input bypass_timer
   - **ID:** Bypass Timer Finished

6. **Idle Timer Ends**
   - **Platform:** event
   - **Event Type:** timer.finished
   - **Event Data:**
     - **Entity ID:** !input idle_timer
   - **ID:** Idle Timer Finished

## Actions

### On Motion Detected (Motion On)

- **Conditions:** Trigger ID is Motion On
- **Sequence:**
  - **If occupancy_helper is configured and not none:**
    - Turn on occupancy_helper
  - **If light_bulbs is configured and currently off:**
    - **If light_control is bulb:**
      - Perform actions based on light_control_features
    - **Else:**
      - Turn on light_bulbs
  - **If light_switch is configured and currently off:**
    - Turn on light_switch
  - **If fan_switch is configured and currently off:**
    - Turn on fan_switch
  - **If idle_timer is configured and active:**
    - Cancel and restart idle_timer

### On Motion Cleared (Motion Off)

- **Conditions:** Trigger ID is Motion Off
- **Sequence:**
  - **If bypass_helper is configured and not none:**
    - **If bypass_helper is on:**
      - Stop action (Bypass Enabled)
  - **If occupancy_helper is configured and not none:**
    - Turn off occupancy_helper
  - **If light_bulbs is configured and currently on:**
    - **If light_control is bulb and use_transition is in light_control_features:**
      - Turn off light_bulbs with transition
    - **Else:**
      - Turn off light_bulbs
  - **If light_switch is configured and currently on:**
    - Turn off light_switch
  - **If fan_switch is configured and currently on:**
    - Turn off fan_switch

### On Bypass Enabled (Bypass Turn on)

- **Conditions:** Trigger ID is Bypass Turn on and bypass_helper is configured and not none
- **Sequence:**
  - **If bypass_timer is configured and not none:**
    - Start bypass_timer

### On Bypass Disabled (Bypass Turn off)

- **Conditions:** Trigger ID is Bypass Turn off and bypass_helper is configured and not none and Trigger ID is not Bypass Timer Finished
- **Sequence:**
  - **If bypass_timer is configured and not none:**
    - Finish bypass_timer

### On Bypass Timer Finished

- **Conditions:** Trigger ID is Bypass Timer Finished and bypass_mode is bypass_auto_off
- **Sequence:**
  - **If bypass_helper is configured and not none:**
    - Turn off bypass_helper
  - **If bypass_finished_action is turn_off:**
    - **If occupancy_helper is configured and not none:**
      - Turn off occupancy_helper
    - **If light_bulbs is configured and currently on:**
      - Turn off light_bulbs
    - **If light_switch is configured and currently on:**
      - Turn off light_switch
    - **If fan_switch is configured and currently on:**
      - Turn off fan_switch

### On Idle Timer Finished

- **Conditions:** Trigger ID is Idle Timer Finished and idle_timer is configured and not none
- **Sequence:**
  - **If bypass_helper is configured and not none:**
    - **If bypass_helper is on:**
      - Stop action (Bypass Enabled)
  - **If motion_sensor is off:**
    - **If occupancy_helper is configured and not none:**
      - Turn off occupancy_helper
    - **If light_bulbs is configured and currently on:**
      - **If light_control is bulb and use_transition is in light_control_features:**
        - Turn off light_bulbs with transition
      - **Else:**
        - Turn off light_bulbs
    - **If light_switch is configured and currently on:**
      - Turn off light_switch
    - **If fan_switch is configured and currently on:**
      - Turn off fan_switch

## Mode

- **Mode:** single
- **Max Exceeded:** silent