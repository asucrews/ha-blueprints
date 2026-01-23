# Home Assistant Start and Stop Trigger (1.0.0)

Blueprint for triggering actions on Home Assistant start and stop.

## Blueprint Details

- **Name:** Home Assistant Start and Stop Trigger (1.0.0)
- **Description:** Blueprint for triggering actions on Home Assistant start and stop
- **Home Assistant Minimum Version:** 2024.6.0
- **Domain:** automation
- **Source URL:** [GitHub](https://github.com/asucrews/ha-blueprints/blob/main/automations/ha_restart/ha_restart.yaml)

## Inputs

### Actions to Run on Start

- **Name:** Actions to Run on Start
- **Description:** Actions to run when Home Assistant starts
- **Selector:** action

### Actions to Run on Stop

- **Name:** Actions to Run on Stop
- **Description:** Actions to run when Home Assistant stops
- **Selector:** action

## Triggers

1. **Home Assistant Start**
   - **Platform:** homeassistant
   - **Event:** start
   - **ID:** home_assistant_start

2. **Home Assistant Shutdown**
   - **Platform:** homeassistant
   - **Event:** shutdown
   - **ID:** home_assistant_shutdown

## Conditions

- None

## Actions

### On Home Assistant Start

- **Conditions:** Trigger ID is `home_assistant_start`
- **Sequence:** !input start_actions

### On Home Assistant Shutdown

- **Conditions:** Trigger ID is `home_assistant_shutdown`
- **Sequence:** !input stop_actions

## Mode

- **Mode:** single