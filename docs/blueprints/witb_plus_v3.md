# WITB+ v3 Occupancy

## Scope

- Source blueprint: `blueprints/automation/witb_plus/v3/witb_plus.yaml`
- Blueprint name: `WITB+ v3.5`
- Home Assistant minimum: `2026.2.0`
- Domain: `automation`

This blueprint infers occupancy for one room using door semantics plus motion:
- One seal door (`main/privacy` semantics)
- One or more transition doors (`entry/exit` semantics)
- PIR motion, with optional mmWave support

## Behavior Model

1. Motion asserts occupancy.
2. Occupancy clears only when exit is possible.
3. Closed seal door blocks normal clear behavior.
4. Optional failsafe timer can clear only when exit conditions are valid.
5. Optional control booleans gate behavior:
   - `automation_override` ON: automation is hands-off.
   - `force_occupied` ON: pins occupancy ON.
   - `manual_occupied` ON: asserts ON but still allows normal clear rules.

## Required Helpers

Per room, create and bind:
- `input_boolean.<slug>_occupied`
- `input_datetime.<slug>_last_motion`
- `input_datetime.<slug>_last_door`

Optional but supported:
- `input_datetime.<slug>_last_exit_door`
- `input_boolean.<slug>_latched`
- `input_boolean.<slug>_automation_override`
- `input_boolean.<slug>_force_occupied`
- `input_boolean.<slug>_manual_occupied`
- `timer.<slug>_failsafe`

Use generator:

```bash
python blueprints/automation/witb_plus/v3/generate_witb_packages.py \
  --rooms "Office" "Master Bathroom Toilet" \
  --out blueprints/automation/witb_plus/v3/packages
```

## Input Reference

### Sensors

- `seal_door`: main/privacy door (`binary_sensor` with door device class).
- `transition_doors`: one or more entry/exit doors (`binary_sensor` door, multiple).
- `motion_sensor`: PIR motion (`binary_sensor` motion).

### Optional mmWave

- `mmwave_sensor` (default: empty): optional presence sensor.
- `mmwave_blocks_clear` (default: `true`): if ON, mmWave ON blocks occupancy clearing.
- `mmwave_asserts_occupied` (default: `false`): if ON, mmWave may assert occupancy ON.

### Occupancy Helpers

- `occupancy_helper`: target occupancy `input_boolean`.
- `last_motion_helper`: `input_datetime` storing last motion ON.
- `last_door_helper`: `input_datetime` storing last door state change.
- `last_exit_door_helper` (default: empty): optional open-while-occupied timestamp helper.
- `exit_recent_window_seconds` (default: `180`): recency window used with `last_exit_door_helper`.
- `latched_helper` (default: empty): optional debug latch helper.
- `exit_timeout_seconds` (default: `60`): no-motion exit delay before clearing.

### Per-Room Controls

- `automation_override` (default: empty): if ON, automation does nothing.
- `force_occupied` (default: empty): if ON, keeps occupancy ON.
- `manual_occupied` (default: empty): soft assert ON control.

### Entry Gating

- `require_door_for_entry` (default: `false`): require recent door activity for motion-based entry.
- `entry_window_seconds` (default: `15`): recent-door window used by entry gating.

### Failsafe

- `enable_failsafe` (default: `true`): enable safe timer-based stuck-state recovery.
- `failsafe_timer` (default: empty): timer entity used when failsafe enabled.
- `failsafe_minutes` (default: `180`): failsafe duration loaded on occupancy assert/refresh.

## Trigger/Action Summary

- Motion ON updates occupancy and timestamps.
- Door changes refresh door timestamps.
- Door-open and motion-off-for windows perform clear checks.
- Optional mmWave off-for window participates in clear checks.
- Timer finished event handles safe failsafe clear logic.

## Recommended Setup Order

1. Generate/load room helpers and template sensors.
2. Create automation from this blueprint in Home Assistant UI.
3. Bind door/motion entities and helpers.
4. Validate behavior with short `exit_timeout_seconds` first, then tune upward.
