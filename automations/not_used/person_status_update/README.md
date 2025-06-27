# Person: Status Update Fork (1.1.0)

Making Home Assistant’s Presence Detection not so Binary.

## Blueprint Details

- **Name:** Person: Status Update Fork (1.1.0)
- **Description:** Making Home Assistant’s Presence Detection not so Binary ([Source](https://gist.github.com/cliffordwhansen/aa993e4173d2ce2e44fc6a0cb0af3599))
- **Home Assistant Minimum Version:** 2024.6.0
- **Domain:** automation
- **Source URL:** [GitHub](https://github.com/asucrews/ha-blueprints/blob/main/automations/person_status_update/person_status_update.yaml)

## Inputs

### Required Entities

#### Person entity

- **Name:** Person entity
- **Description:** The person entity to track
- **Selector:** entity (domain: person)

#### Input select

- **Name:** Input select
- **Description:** The input select that tracks the person's status
- **Selector:** entity (domain: input_select)

### Optional Entities

#### Time till marked away

- **Name:** Time till marked away
- **Description:** How long to wait in "Just Left" before getting set as "Away"
- **Default:** 10
- **Selector:** number (min: 0, max: 60, unit_of_measurement: minutes)

#### Time till marked home

- **Name:** Time till marked home
- **Description:** How long to wait in "Just Arrived" before getting set as "Home"
- **Default:** 10
- **Selector:** number (min: 0, max: 60, unit_of_measurement: minutes)

#### Time till marked extended away

- **Name:** Time till marked extended away
- **Description:** How long to wait in "Away" before being set to "Extended Away"
- **Default:** 24
- **Selector:** number (min: 0, max: 168, unit_of_measurement: hours)

## Triggers

1. **Device Tracker Home**
   - **Platform:** state
   - **Entity ID:** !input person_device_tracker
   - **To:** home
   - **ID:** device_tracker_home

2. **Input Select Wait Arrived**
   - **Platform:** state
   - **Entity ID:** !input person_input_select
   - **For:** !input time_till_marked_home
   - **To:** Just Arrived
   - **ID:** input_select_wait_arrived

3. **Input Select Debounce**
   - **Platform:** state
   - **Entity ID:** !input person_input_select
   - **From:** Just Left
   - **To:** Just Arrived
   - **ID:** input_select_debounce

4. **Device Tracker Not Home**
   - **Platform:** state
   - **Entity ID:** !input person_device_tracker
   - **From:** home
   - **ID:** device_tracker_not_home

5. **Input Select Wait Left**
   - **Platform:** state
   - **Entity ID:** !input person_input_select
   - **For:** !input time_till_marked_away
   - **To:** Just Left
   - **ID:** input_select_wait_left

6. **Input Select Wait Away**
   - **Platform:** state
   - **Entity ID:** !input person_input_select
   - **For:** !input time_till_marked_extended_away
   - **To:** Away
   - **ID:** input_select_wait_away

## Conditions

- **Condition:** template
  - **Value Template:** "{{ trigger.to_state.state != trigger.from_state.state }}"

## Actions

### Device Tracker Home

- **Conditions:**
  - Trigger ID is device_tracker_home
  - Person input select state is Just Left
- **Sequence:**
  - **Service:** input_select.select_option
    - **Target:** !input person_input_select
    - **Data:**
      - **Option:** Home

### Device Tracker Home (No Condition)

- **Conditions:**
  - Trigger ID is device_tracker_home
- **Sequence:**
  - **Service:** input_select.select_option
    - **Target:** !input person_input_select
    - **Data:**
      - **Option:** Just Arrived

### Input Select Wait Arrived or Debounce

- **Conditions:**
  - Trigger ID is input_select_wait_arrived or input_select_debounce
- **Sequence:**
  - **Service:** input_select.select_option
    - **Target:** !input person_input_select
    - **Data:**
      - **Option:** Home

### Device Tracker Not Home

- **Conditions:**
  - Trigger ID is device_tracker_not_home
- **Sequence:**
  - **Service:** input_select.select_option
    - **Target:** !input person_input_select
    - **Data:**
      - **Option:** Just Left

### Input Select Wait Left

- **Conditions:**
  - Trigger ID is input_select_wait_left
- **Sequence:**
  - **Service:** input_select.select_option
    - **Target:** !input person_input_select
    - **Data:**
      - **Option:** Away

### Default (Input Select Wait Away)

- **Conditions:**
  - Trigger ID is input_select_wait_away
- **Sequence:**
  - **Service:** input_select.select_option
    - **Target:** !input person_input_select
    - **Data:**
      - **Option:** Extended Away

## Mode

- **Mode:** single
- **Max Exceeded:** silent
This completes the conversion of the YAML file to README.md format. If you have any more YAML files or need further assistance, feel free to ask!