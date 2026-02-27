# Vacuum Job Manager (iRobot) v1

This folder contains a Home Assistant automation blueprint that manages vacuum runs with helper entities, schedule support, mission-counter completion, and WITB integration hooks.

## Files

- `vacuum_job_manager.yaml`: automation blueprint.
- `vacuum_job_helpers.yaml`: helper package template for required entities.

## What It Does

- Queues vacuum runs from a button and optional schedule.
- Starts a job only when the vacuum is docked and manager is enabled.
- Tracks job state in helpers (`queued`, `cleaning`, `paused`, `returning`, etc.).
- Uses iRobot mission counters for true completion (does not treat `docked` alone as completion).
- Applies watchdog timeout and sends `vacuum.return_to_base` when exceeded.
- During active job:
  - Can turn on configured lights/switches.
  - Can enable WITB `automation_override` booleans.
- On job end:
  - Disables overrides.
  - Turns lights/switches off only if configured occupancy entities are not occupied.

## Setup

1. Load helpers from `vacuum_job_helpers.yaml` (or create equivalent helpers manually).
2. Create automation from `vacuum_job_manager.yaml` in Home Assistant UI.
3. Bind:
   - Vacuum entity
   - Helper entities
   - iRobot mission counters
   - Optional schedule/notify/lighting/WITB override/occupancy entities

Detailed input documentation is in `docs/blueprints/vacuum_job_manager_v1.md`.
