# WITB Transit Room Driver v1

Implementation documentation for `witb_transit_room.yaml`.

## Source

- Blueprint: `blueprints/automation/witb_transit_room/v1/witb_transit_room.yaml`
- Helpers template: `blueprints/automation/witb_transit_room/v1/transit_helpers_package_template.yaml`
- Blueprint README: `blueprints/automation/witb_transit_room/v1/README.md`

## Purpose

Occupancy driver for transit areas (hallways, stairs, open connectors) that have no doors. Uses PIR sensors with a hold timer for decay-based presence. Outputs `input_boolean.<slug>_occupied_effective` — the same signal consumed by WITB+ Actions v2.

## Design Overview

The blueprint uses a sequential choose-block "case statement" with early `stop` exits. Cases are evaluated in priority order:

| Priority | Case | Action |
|---|---|---|
| 1 | Maintenance override ON | Force occupied ON, cancel timer |
| 2 | Instant OFF triggered | Force occupied OFF, cancel timer, optional suppress |
| 3 | Suppress timer finished | Re-check motion; re-enable if currently ON |
| 4 | HA restart | Recover state from current motion/keepalive |
| 5 | Suppress active (gate) | Ignore motion + keepalive triggers |
| 6 | Motion ON | Occupied ON + restart hold timer |
| 7 | Keepalive changed | Cancel timer (if keepalive ON) or start release decay |
| 8 | Hold timer finished | Clear if no motion AND no keepalive |
| 9 | Maintenance toggle | Resume normal logic on override OFF |

## Trigger Sources

- `motion` — any configured PIR sensor goes `on`
- `hold_finished` — `timer.finished` on the hold timer
- `keepalive_change` — any configured keepalive entity state changes
- `instant_off` — any instant-off entity goes `on`
- `suppress_finished` — `timer.finished` on the suppress/rearm timer
- `maintenance_change` — maintenance override entity state changes
- `ha_start` — `homeassistant.start` event

## Keepalive Behavior

- **`extend_only`** (default): prevents clearing (timer idle while keepalive ON) but does not turn occupancy ON.
- **`extend_and_turn_on`**: neighbor occupancy can also turn this transit room ON (useful for hallways adjacent to occupied rooms).

Keepalive entities must always be provided. Use `<slug>_keepalive_dummy` if the feature is unused.

## Instant OFF Behavior

- Forces `occupied_effective` OFF immediately, cancels hold timer.
- Optional suppress/rearm: if `instant_off_rearm_timeout_seconds > 0`, a suppress timer blocks motion/keepalive re-enables for that duration. On expiry, motion is re-checked.
- For repeatable triggering from scripts, set the instant_off boolean ON then immediately OFF.

## Helper Package

Copy and customize `transit_helpers_package_template.yaml` replacing `room_slug` → your slug and `Friendly Name` → display name.

Required helpers:

| Entity | Pattern | Notes |
|---|---|---|
| `input_boolean` | `<slug>_occupied_effective` | Occupancy output |
| `input_boolean` | `<slug>_maintenance_override` | Maintenance hold |
| `input_boolean` | `<slug>_keepalive_dummy` | Dummy for unused keepalive |
| `input_boolean` | `<slug>_instant_off_dummy` | Dummy for unused instant off |
| `timer` | `<slug>_transit_hold` | Decay hold timer |
| `timer` | `<slug>_instant_off_suppress` | Suppress/rearm timer |
| `input_text` | `<slug>_last_motion` | Debug: last triggered sensor |

Load packages:

```yaml
homeassistant:
  packages: !include_dir_merge_named packages/
```

## Setup Flow

1. Copy template → fill in slug and display name → save to `packages/`.
2. Reload HA (or restart) so helpers exist.
3. Create automation from blueprint in HA UI.
4. Bind all required selectors; select dummies for unused features.
5. Optionally pair with a WITB+ Actions v2 automation watching `binary_sensor.<slug>_occupied_effective`.

## Minimum HA Version

`2026.2.0`
