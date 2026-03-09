# Vacuum Job Manager (iRobot) v1

## Scope

- Source blueprint: `blueprints/automation/vacuum_job_manager/v1/vacuum_job_manager.yaml`
- Blueprint name: `Vacuum Job Manager (iRobot) v1.1 - WITB Override + Lights`
- Domain: `automation`
- Home Assistant minimum: `2026.2.0`

This blueprint manages vacuum job lifecycle and helper state with iRobot mission-counter completion, watchdog handling, and optional WITB/light integration.

## Companion File

- Helper package template: `blueprints/automation/vacuum_job_manager/v1/vacuum_job_helpers.yaml`

It defines the required helper entities:
- booleans (`enabled`, `requested`, `active`, `error`)
- phase `input_select`
- last start/end `input_datetime`
- failures `counter`
- max runtime and baseline `input_number` helpers
- run-now `input_button`
- watchdog `timer`

## Core Behavior

1. Request flow:
   - `request_button` press or schedule hit can set `requested` ON and phase to `queued`.
2. Start gate:
   - Starts only when `enabled=on`, `requested=on`, `active=off`, and vacuum is `docked`.
3. Active-job setup:
   - Snapshots baseline mission counters.
   - Starts watchdog timer.
   - Optionally enables WITB overrides and turns on configured lights/switches.
4. Completion detection:
   - Ends job only when mission counters increment (`successful`, `failed`, `canceled`).
   - Does not use `docked` as completion by itself.
5. End-job cleanup:
   - Cancels watchdog.
   - Disables WITB overrides.
   - Turns lights/switches off only when no configured occupancy entity is ON.
   - Updates phase and timestamps.
6. Watchdog timeout:
   - Sends `vacuum.return_to_base` and optional notification.

## Input Reference

### Required Entities

- `vacuum_entity`
- `enabled_boolean`
- `requested_boolean`
- `active_boolean`
- `error_boolean`
- `phase_select`
- `last_start_datetime`
- `last_end_datetime`
- `failures_counter`
- `watchdog_timer`
- `max_runtime_min`
- `request_button`
- `successful_missions_sensor`
- `failed_missions_sensor`
- `canceled_missions_sensor`
- `base_successful_input`
- `base_failed_input`
- `base_canceled_input`

### Schedule

- `use_schedule` (default: `false`)
- `schedule_time` (default: `10:00:00`)
- `schedule_days` (default: `mon..fri`)

### Notifications

- `notify_service` (default: empty)

### v1.1 Integration Controls

- `vacuum_lighting_entities` (default: empty)
- `witb_automation_override_booleans` (default: empty)
- `occupancy_entities` (default: empty)

## Trigger Summary

- request button press
- schedule time tick
- requested boolean ON
- vacuum state changes
- watchdog timer finished
- mission counter changes (`successful`, `failed`, `canceled`)

## Recommended Setup Order

1. Load/create all helpers from `vacuum_job_helpers.yaml`.
2. Create automation from blueprint and bind all required entities.
3. Verify phase transitions and mission-counter completion behavior.
4. Add optional lights/WITB override/occupancy gating after baseline behavior is stable.
