# Time of Day Trigger (1.0.0)

Blueprint for triggering actions at a specific time of day.

## Blueprint Details

- **Name:** Time of Day Trigger (1.0.0)
- **Description:** Blueprint for triggering actions at a specific time of day.
- **Home Assistant Minimum Version:** 2024.6.0
- **Domain:** automation
- **Source URL:** [GitHub](https://github.com/asucrews/ha-blueprints/blob/main/automations/time_of_day/time_of_day.yaml)

## Inputs

### Trigger Time

- **Name:** Trigger Time
- **Description:** Time of day to run the actions
- **Selector:** time

### Actions

- **Name:** Actions
- **Description:** Actions to run at the specified time
- **Selector:** action

## Triggers

1. **Time Trigger**
   - **Platform:** time
   - **At:** !input trigger_time

## Conditions

- None

## Actions

### Execute Specified Actions

- **Conditions:** None
- **Sequence:** !input actions

## Mode

- **Mode:** single
- **Max Exceeded:** silent
