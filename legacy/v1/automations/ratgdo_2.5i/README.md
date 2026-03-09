# Ratdgo 2.5i Stable (0.5.3)

Ratdgo Notification and auto close automation blueprint for Home Assistant.

## Blueprint Details

- **Name:** Ratdgo 2.5i Stable (0.5.3)
- **Description:** Ratdgo Notification and auto close
- **Home Assistant Minimum Version:** 2024.5.0
- **Domain:** automation
- **Source URL:** [GitHub](https://raw.githubusercontent.com/asucrews/ha-blueprints/main/automations/ratgdo_2.5i/ratdgo_2.5i.yaml)

## Inputs

### Required Entities

#### Ratdgo Device

- **Name:** Ratdgo Device
- **Description:** Which Ratdgo Device?
- **Selector:** entity (domain: cover, multiple: false)

#### Obstruction Entity

- **Name:** Obstruction Entity
- **Description:** Which Obstruction Entity?
- **Selector:** entity (domain: binary_sensor, multiple: false)

### Optional Entities

#### Garage Door Timer Helper

- **Name:** Garage Door Timer Helper
- **Description:** Helper for managing the garage door timer
- **Default:** timer.none
- **Selector:** entity (domain: timer, multiple: false)

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

#### Notification Group (Optional)

- **Name:** Notification Group
- **Description:** Group for notifications
- **Default:** ""
- **Selector:** text

#### Bypass Helper

- **Name:** Bypass Helper
- **Description:** Garage Door Bypass helper
- **Default:** input_boolean.none
- **Selector:** entity (domain: input_boolean, multiple: false)

## Variables

- **ratdgo_device:** !input ratdgo_device
- **obstruction_entity:** !input obstruction_entity
- **garage_door_timer_helper:** !input garage_door_timer_helper
- **light_bulbs:** !input light_bulbs
- **light_switch:** !input light_switch
- **notify_group:** !input notify_group
- **bypass_helper:** !input bypass_helper

## Triggers

1. **Garage Door is Open**
   - **Platform:** state
   - **Entity ID:** !input ratdgo_device
   - **From:** opening
   - **To:** open
   - **ID:** Garage Door is Open

2. **Garage Door is Closed**
   - **Platform:** state
   - **Entity ID:** !input ratdgo_device
   - **From:** closing
   - **To:** closed
   - **ID:** Garage Door is Closed

3. **Door Timer is Done**
   - **Platform:** event
   - **Event Type:** timer.finished
   - **Event Data:** entity_id: !input garage_door_timer_helper
   - **ID:** Door timer is done

4. **Obstruction Found**
   - **Platform:** state
   - **Entity ID:** !input obstruction_entity
   - **From:** "off"
   - **To:** "on"
   - **ID:** Obstruction Found

## Actions

### On Garage Door is Open

- **Conditions:** Trigger ID is Garage Door is Open
- **Sequence:**
  - **If light_bulbs is configured and off:**
    - **Service:** light.turn_on
      - **Target:** !input light_bulbs
  - **If light_switch is configured and off:**
    - **Service:** light.turn_on
      - **Target:** !input light_switch
  - **If garage_door_timer_helper is configured:**
    - **Service:** timer.start
      - **Target:** !input garage_door_timer_helper
  - **If notify_group is defined:**
    - **Service:** notify.notify_group
      - **Data:**
        - **Title:** "{{ device_attr(ratdgo_device, 'name') }} | {{ states('sensor.time') }}"
        - **Message:** Garage Door is Open
        - **TTL:** 0
        - **Priority:** high
        - **Tag:** "tag-ratdgo"

### On Garage Door is Closed

- **Conditions:** Trigger ID is Garage Door is Closed
- **Sequence:**
  - **If garage_door_timer_helper is configured and active/paused:**
    - **Service:** timer.cancel
      - **Target:** !input garage_door_timer_helper
  - **If notify_group is defined:**
    - **Service:** notify.notify_group
      - **Data:**
        - **Title:** "{{ device_attr(ratdgo_device, 'name') }} | {{ states('sensor.time') }}"
        - **Message:** Garage Door is Closed
        - **TTL:** 0
        - **Priority:** high
        - **Tag:** "tag-ratdgo"

### On Door Timer is Done

- **Conditions:**
  - Trigger ID is Door timer is done
  - **State:** is_state(ratdgo_device, ['on', 'open'])
- **Sequence:**
  - **If obstruction_entity is off:**
    - **Service:** cover.close_cover
      - **Target:** !input ratdgo_device
  - **Else:**
    - **Service:** timer.cancel
      - **Target:** !input garage_door_timer_helper
    - **Service:** timer.start
      - **Target:** !input garage_door_timer_helper

### On Obstruction Found

- **Conditions:**
  - Trigger ID is Obstruction Found
  - **State:** is_state(ratdgo_device, ['on', 'open', 'opening'])
  - garage_door_timer_helper is configured
- **Sequence:**
  - **Service:** timer.cancel
    - **Target:** !input garage_door_timer_helper
  - **Service:** timer.start
    - **Target:** !input garage_door_timer_helper

## Mode

- **Mode:** single
- **Max Exceeded:** silent