# Inovelli Smart Dimmer FKA 2-1 Switch - VZW31-SN - ZWave-JS (0.2.0)

Perform actions on various scenes supported by the Inovelli Smart Dimmer FKA 2-1 Switch.

## Blueprint Details

- **Name:** Inovelli Smart Dimmer FKA 2-1 Switch - VZW31-SN - ZWave-JS (0.2.0)
- **Description:** 
    Perform actions on various scenes supported by the Inovelli Inovelli Smart Dimmer FKA 2-1 Switch. Note that the x2, x3, x4, x5 variants DO NOT work if you have put your switch in 'Instant On' mode.
- **Home Assistant Minimum Version:** 2024.6.0
- **Domain:** automation
- **Source URL:** [GitHub](https://github.com/asucrews/ha-blueprints/blob/main/automations/inovelli/red/smart_dimmer/smart_dimmer.yaml)

## Inputs

### Required Entities

#### Inovelli On/Off Switch

- **Name:** Inovelli On/Off Switch
- **Description:** The Inovelli On/Off or Dimmer Switch to do actions on
- **Selector:** device (integration: zwave_js, manufacturer: Inovelli, model: VZW31-SN)

### Actions up press

- **Name:** Actions up press
- **Description:** Action to perform when pressing up
- **Inputs:**
    - **Press Up Once Action:** Action to perform when pressing up once
    - **Press Up Twice Action:** Action to perform when pressing up twice
    - **Press Up 3 Times Action:** Action to perform on when pressing up 3 times
    - **Press Up 4 Times Action:** Action to perform when pressing up 4 times
    - **Press Up 5 Times Action:** Action to perform when pressing up 5 times
    - **Hold Up Action:** Action to perform when holding the up button
    - **Release Up Action:** Action to perform when releasing the up button

### Actions down press

- **Name:** Actions down press
- **Description:** Action to perform when pressing down
- **Inputs:**
    - **Press Down Once Action:** Action to perform when pressing down once
    - **Press Down Twice Action:** Action to perform when pressing down twice
    - **Press Down 3 Times Action:** Action to perform when pressing down 3 times
    - **Press Down 4 Times Action:** Action to perform when pressing down 4 times
    - **Press Down 5 Times Action:** Action to perform when pressing down 5 times
    - **Hold Down Action:** Action to perform when holding the down button
    - **Release Down Action:** Action to perform when releasing the down button

### Actions config press

- **Name:** Actions config press
- **Description:** Action to perform when pressing config
- **Inputs:**
    - **Config Button Action:** The action to perform when the config button is pressed once
    - **Press Config Twice Times Action:** Action to perform when pressing config twice
    - **Press config 3 Times Action:** Action to perform when pressing config 3 times
    - **Press config 4 Times Action:** Action to perform when pressing config 4 times
    - **Press config 5 Times Action:** Action to perform when pressing config 5 times
    - **Hold Config Action:** Action to perform when holding the Config button
    - **Release Config Action:** Action to perform when releasing the Config button

### Actions aux up press

- **Name:** Actions aux up press
- **Description:** Action to perform when pressing aux up
- **Inputs:**
    - **Press Up Once Action on Aux Switch:** Action to perform when pressing up once
    - **Press Up Twice Action on Aux Switch:** Action to perform when pressing up twice
    - **Press Up 3 Times Action on Aux Switch:** Action to perform on when pressing up 3 times
    - **Press Up 4 Times Action on Aux Switch:** Action to perform when pressing up 4 times
    - **Press Up 5 Times Action on Aux Switch:** Action to perform when pressing up 5 times
    - **Hold Up Action on Aux Switch:** Action to perform when holding the up button
    - **Aux Up Release Action:** Action to perform when releasing the up button

### Actions aux down press

- **Name:** Actions aux down press
- **Description:** Action to perform when pressing aux down
- **Inputs:**
    - **Press Down Once Action on Aux Switch:** Action to perform when pressing down once
    - **Press Down Twice Action on Aux Switch:** Action to perform when pressing down twice
    - **Press Down 3 Times Action on Aux Switch:** Action to perform when pressing down 3 times
    - **Press Down 4 Times Action on Aux Switch:** Action to perform when pressing down 4 times
    - **Press Down 5 Times Action on Aux Switch:** Action to perform when pressing down 5 times
    - **Hold Down Action on Aux Switch:** Action to perform when holding the down button
    - **Aux Down Release Action:** Action to perform when releasing the down button

### Actions Aux config press

- **Name:** Actions Aux config press
- **Description:** Action to perform when pressing aux config
- **Inputs:**
    - **Config Button Action on Aux Switch:** The action to perform when the config button is pressed once
    - **Press Config Twice Times Action on Aux Switch:** Action to perform when pressing config twice
    - **Press config 3 Times Action on Aux Switch:** Action to perform when pressing config 3 times
    - **Press config 4 Times Action on Aux Switch:** Action to perform when pressing config 4 times
    - **Press config 5 Times Action on Aux Switch:** Action to perform when pressing config 5 times
    - **Hold Config Action on Aux Switch:** Action to perform when holding the Config button
    - **Release Config Action on Aux Switch:** Action to perform when releasing the Config button

## Variables

- **down_button:** "001"
- **up_button:** "002"
- **config_button:** "003"
- **aux_down_button:** "004"
- **aux_up_button:** "005"
- **aux_config_button:** "006"
- **press_x1:** KeyPressed
- **press_x2:** KeyPressed2x
- **press_x3:** KeyPressed3x
- **press_x4:** KeyPressed4x
- **press_x5:** KeyPressed5x
- **hold:** KeyHeldDown
- **release:** KeyReleased
- **button:** "{{ trigger.event.data.property_key_name }}"
- **action_type:** "{{ trigger.event.data.value }}"

## Trigger

- **Platform:** event
- **Event Type:** zwave_js_value_notification
- **ID:** Z-Wave Event
- **Event Data:**
  - **Device ID:** !input inovelli_switch

## Actions

### Up Button Actions

- **Conditions:**
  - Button is up_button
- **Sequence:**
  - If action_type is press_x1, perform up_action
  - If action_type is press_x2, perform up_x2_action
  - If action_type is press_x3, perform up_x3_action
  - If action_type is press_x4, perform up_x4_action
  - If action_type is press_x5, perform up_x5_action
  - If action_type is hold, perform up_hold_action
  - If action_type is release, perform up_release_action

### Down Button Actions

- **Conditions:**
  - Button is down_button
- **Sequence:**
  - If action_type is press_x1, perform down_action
  - If action_type is press_x2, perform down_x2_action
  - If action_type is press_x3, perform down_x3_action
  - If action_type is press_x4, perform down_x4_action
  - If action_type is press_x5, perform down_x5_action
  - If action_type is hold, perform down_hold_action
  - If action_type is release, perform down_release_action

### Config Button Actions

- **Conditions:**
  - Button is config_button
- **Sequence:**
  - If action_type is press_x1, perform config_action
  - If action_type is press_x2, perform config_x2_action
  - If action_type is press_x3, perform config_x3_action
  - If action_type is press_x4, perform config_x4_action
  - If action_type is press_x5, perform config_x5_action
  - If action_type is hold, perform config_hold_action
  - If action_type is release, perform config_release_action

### Aux Up Button Actions

- **Conditions:**
  - Button is aux_up_button
- **Sequence:**
  - If action_type is press_x1, perform aux_up_action
  - If action_type is press_x2, perform aux_up_x2_action
  - If action_type is press_x3, perform aux_up_x3_action
  - If action_type is press_x4, perform aux_up_x4_action
  - If action_type is press_x5, perform aux_up_x5_action
  - If action_type is hold, perform aux_up_hold_action
  - If action_type is release, perform aux_up_release_action

### Aux Down Button Actions

- **Conditions:**
  - Button is aux_down_button
- **Sequence:**
  - If action_type is press_x1, perform aux_down_action
  - If action_type is press_x2, perform aux_down_x2_action
  - If action_type is press_x3, perform aux_down_x3_action
  - If action_type is press_x4, perform aux_down_x4_action
  - If action_type is press_x5, perform aux_down_x5_action
  - If action_type is hold, perform aux_down_hold_action
  - If action_type is release, perform aux_down_release_action

### Aux Config Button Actions

- **Conditions:**
  - Button is aux_config_button
- **Sequence:**
  - If action_type is press_x1, perform aux_config_action
  - If action_type is press_x2, perform aux_config_x2_action
  - If action_type is press_x3, perform aux_config_x3_action
  - If action_type is press_x4, perform aux_config_x4_action
  - If action_type is press_x5, perform aux_config_x5_action
  - If action_type is hold, perform aux_config_hold_action
  - If action_type is release, perform aux_config_release_action

## Mode

- **Mode:** single
- **Max Exceeded:** silent
