# 6 Speed Ceiling Fan Remote (0.1.1)

Blueprint for controlling the 6 speed ceiling fan with RF remote using ESP360 Remote.

## Blueprint Details

- **Name:** 6 Speed Ceiling Fan Remote (0.1.1)
- **Description:** Blueprint for controlling the 6 speed ceiling fan with RF remote using ESP360 Remote
- **Home Assistant Minimum Version:** 2024.6.0
- **Domain:** automation
- **Source URL:** [GitHub](https://github.com/asucrews/ha-blueprints/blob/main/automations/esp360_remote/6_speed_fan.yaml)

## Inputs

### RF Event

- **Name:** RF Event
- **Description:** Event for the RF remote
- **Default:** "esphome.rf_code_received"

### Protocol

- **Name:** Protocol
- **Description:** Protocol number to match for RF codes
- **Default:** 4
- **Selector:** number (min: 1, max: 12, step: 1)

### Ceiling Fan Light State

- **Name:** Ceiling Fan Light State
- **Description:** Input boolean for the ceiling fan light state
- **Selector:** entity (domain: input_boolean)

### Ceiling Fan State

- **Name:** Ceiling Fan State
- **Description:** Input boolean for the ceiling fan state
- **Selector:** entity (domain: input_boolean)

### Ceiling Fan Preset Mode

- **Name:** Ceiling Fan Preset Mode
- **Description:** Input select for the ceiling fan preset mode
- **Selector:** entity (domain: input_select)

### Ceiling Fan Direction

- **Name:** Ceiling Fan Direction
- **Description:** Input select for the ceiling fan direction
- **Selector:** entity (domain: input_select)

### Light Code

- **Name:** Light Code
- **Description:** RF code for the light
- **Default:** "833496100"

### Fan Code

- **Name:** Fan Code
- **Description:** RF code for the fan
- **Default:** "833496871"

### Preset Mode 1 Code

- **Name:** Preset Mode 1 Code
- **Description:** RF code for preset mode 1
- **Default:** "833497642"

### Preset Mode 2 Code

- **Name:** Preset Mode 2 Code
- **Description:** RF code for preset mode 2
- **Default:** "833501754"

### Preset Mode 3 Code

- **Name:** Preset Mode 3 Code
- **Description:** RF code for preset mode 3
- **Default:** "833505866"

### Preset Mode 4 Code

- **Name:** Preset Mode 4 Code
- **Description:** RF code for preset mode 4
- **Default:** "833509978"

### Preset Mode 5 Code

- **Name:** Preset Mode 5 Code
- **Description:** RF code for preset mode 5
- **Default:** "833514090"

### Preset Mode 6 Code

- **Name:** Preset Mode 6 Code
- **Description:** RF code for preset mode 6
- **Default:** "833493530"

### Direction Code

- **Name:** Direction Code
- **Description:** RF code for changing the fan direction
- **Default:** "833495843"

## Variables

- **event_protocol:** "{{ trigger.event.data.protocol }}"
- **event_code:** "{{ trigger.event.data.code }}"
- **protocol:** !input protocol
- **light_state:** !input light_state
- **fan_state:** !input fan_state
- **preset_mode:** !input preset_mode
- **direction:** !input direction
- **code_light:** !input code_light
- **code_fan:** !input code_fan
- **code_preset_1:** !input code_preset_1
- **code_preset_2:** !input code_preset_2
- **code_preset_3:** !input code_preset_3
- **code_preset_4:** !input code_preset_4
- **code_preset_5:** !input code_preset_5
- **code_preset_6:** !input code_preset_6
- **code_direction:** !input code_direction

## Trigger

- **Platform:** event
- **Event Type:** !input rf_event

## Actions

### Light Code

- **Conditions:**
  - Event protocol matches the specified protocol
  - Event code matches the light code
- **Sequence:**
  - If the light state is "off", turn it on.
  - If the light state is "on", turn it off.

### Fan Code

- **Conditions:**
  - Event protocol matches the specified protocol
  - Event code matches the fan code
- **Sequence:**
  - If the fan state is "off", turn it on.
  - If the fan state is "on", turn it off.

### Preset Mode 1 Code

- **Conditions:**
  - Event protocol matches the specified protocol
  - Event code matches the preset mode 1 code
- **Sequence:**
  - Set the preset mode to "1".

### Preset Mode 2 Code

- **Conditions:**
  - Event protocol matches the specified protocol
  - Event code matches the preset mode 2 code
- **Sequence:**
  - Set the preset mode to "2".

### Preset Mode 3 Code

- **Conditions:**
  - Event protocol matches the specified protocol
  - Event code matches the preset mode 3 code
- **Sequence:**
  - Set the preset mode to "3".

### Preset Mode 4 Code

- **Conditions:**
  - Event protocol matches the specified protocol
  - Event code matches the preset mode 4 code
- **Sequence:**
  - Set the preset mode to "4".

### Preset Mode 5 Code

- **Conditions:**
  - Event protocol matches the specified protocol
  - Event code matches the preset mode 5 code
- **Sequence:**
  - Set the preset mode to "5".

### Preset Mode 6 Code

- **Conditions:**
  - Event protocol matches the specified protocol
  - Event code matches the preset mode 6 code
- **Sequence:**
  - Set the preset mode to "6".

### Direction Code

- **Conditions:**
  - Event protocol matches the specified protocol
  - Event code matches the direction code
- **Sequence:**
  - If the direction is "forward", set it to "reverse".
  - If the direction is "reverse", set it to "forward".

## Mode

- **Mode:** single
- **Max Exceeded:** silent