# WITB Transit Room Driver v1

Occupancy driver for transit areas (hallways, stairs, open connectors) using PIR-only decay logic. Outputs a WITB-compatible `input_boolean.*_occupied_effective` signal that WITB+ Actions v2 consumes.

## Files

- `witb_transit_room.yaml` — automation blueprint.
- `transit_helpers_package_template.yaml` — helper package template for required entities.

## What the Blueprint Does

Transit rooms have no doors to anchor state, so occupancy decays via a hold timer after motion stops:

- **Motion ON** → `occupied_effective` ON + restart hold timer.
- **Hold timer expires** → clear only if no motion AND no keepalive is active.
- **Keepalive ON** → hold timer cancelled (timer stays idle to prevent event spam); occupancy held ON.
- **Keepalive OFF** (all) + no motion → start release-decay timer to clear.
- **Instant OFF** → force `occupied_effective` OFF immediately + cancel timer; optional suppress/rearm window.
- **Maintenance override** → force `occupied_effective` ON indefinitely (stairs safety / cleaning).
- **HA restart restore** → recover state from current motion/keepalive without needing a fresh PIR edge.

## Required Helpers

Copy `transit_helpers_package_template.yaml`, replace `room_slug` / `Friendly Name`, and load it as a package:

```yaml
homeassistant:
  packages: !include_dir_merge_named packages/
```

| Helper | Entity ID pattern | Purpose |
|---|---|---|
| `input_boolean` | `<slug>_occupied_effective` | Occupancy output (feed into Actions v2) |
| `input_boolean` | `<slug>_maintenance_override` | Forces occupied ON indefinitely |
| `input_boolean` | `<slug>_keepalive_dummy` | Dummy — select if not using keepalive |
| `input_boolean` | `<slug>_instant_off_dummy` | Dummy — select if not using instant off |
| `timer` | `<slug>_transit_hold` | Decay hold timer |
| `timer` | `<slug>_instant_off_suppress` | Instant-off rearm suppression timer |
| `input_text` | `<slug>_last_motion` | Debug: last triggered motion sensor |

> **Note on dummy helpers:** Home Assistant state triggers require at least one entity. Select the dummy booleans/timer in the blueprint when you do not want keepalive or instant-off for a room.

## Key Inputs

| Input | Default | Description |
|---|---|---|
| `motion_sensors` | — | PIR sensors (one or more) |
| `occupied_effective` | — | Output boolean |
| `hold_timer` | — | Decay timer |
| `night_mode` | `sun` | `sun` (below_horizon) or `boolean` |
| `night_entity` | `sun.sun` | Entity for night detection |
| `hold_seconds_day` | 60 s | Hold duration (day) |
| `hold_seconds_night` | 120 s | Hold duration (night) |
| `min_on_seconds` | 20 s | Minimum ON time (anti-flicker) |
| `keepalive_entities` | — | Booleans that prevent clearing (use dummy if unused) |
| `keepalive_mode` | `extend_only` | `extend_only` or `extend_and_turn_on` |
| `keepalive_release_decay_seconds_day/night` | 0 | Decay after keepalive releases (0 = use normal hold) |
| `instant_off_entities` | — | Force OFF immediately (use dummy if unused) |
| `instant_off_suppress_timer` | — | Rearm suppression timer (use dummy if unused) |
| `instant_off_rearm_timeout_seconds` | 0 | 0 = strict OFF; >0 = recheck motion after N seconds |
| `maintenance_override_entity` | — | Forces occupied ON indefinitely |
| `last_motion_text` | — | Debug input_text |
| `restore_on_restart` | `true` | Recover state on HA restart |
| `debug` | `false` | Write logbook entries |

## Setup

1. Copy `transit_helpers_package_template.yaml` → rename with your room slug → load as HA package.
2. Reload Home Assistant so the helpers exist.
3. Create an automation from `WITB Transit Room Driver v1` in the HA UI.
4. Bind all required entities; select dummy booleans/timer for features you don't use.
5. Optionally bind `binary_sensor.*_occupied_effective` as input to a WITB+ Actions v2 automation.

## Differences from WITB+ v4

| | WITB+ v4 | Transit Room Driver v1 |
|---|---|---|
| Door inputs | Yes (seal + transition) | No |
| Motion | PIR + optional mmWave | PIR only |
| Decay | Timer-based (exit window) | Timer-based (hold timer) |
| Keepalive | `force_occupied` | `keepalive_entities` booleans |
| Instant OFF | `automation_override` | Dedicated `instant_off_entities` |
| Use case | Enclosed rooms | Hallways / stairs / open connectors |
