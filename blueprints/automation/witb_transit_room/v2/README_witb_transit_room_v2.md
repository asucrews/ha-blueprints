# WITB Transit Room v2

WITB+ 4.4.0 minus doors, for transit rooms (stairs, hallways, open connectors). Same engine, inputs and
behavior as WITB+ for motion, mmWave, override/force/manual controls and the failsafe; everything that
depends on a door is removed.

## Files

- `witb_transit_room.yaml` — automation blueprint.
- `CHANGELOG_witb_transit_room.md` — version history.
- Helper package template and generator support for v2 are added in a follow-up change.

## What the Blueprint Does

- **Motion ON** → occupancy helper ON, `last_motion` updated, failsafe timer (re)started.
- **Motion OFF for `exit_timeout_seconds`** → occupancy OFF, unless a manual helper is ON or mmWave blocks.
- **mmWave** (optional) → can assert, can block clearing while ON, and clears after being off for the timeout
  when PIR is also off.
- **Automation Override ON** → automation does nothing.
- **Force Occupied ON** → pins occupancy ON, blocks all clearing including the failsafe deadlock break.
- **Manual Occupied ON** → asserts occupancy and blocks clearing while ON. Turning force/manual OFF does not
  clear immediately; the next motion-off or failsafe evaluation does.
- **Failsafe** → on timer finish, clears if motion is off, mmWave allows it and no manual helper is ON;
  otherwise restarts. Deadlock break clears after 1.5x the failsafe duration without motion (force OFF).

## Output

The blueprint drives `input_boolean.<slug>_occupied`. The room package builds
`binary_sensor.<slug>_occupied_effective` (occupied OR force OR manual) from it, which WITB Actions V3 and
Tag Cleanup consume like a WITB+ room.

## Required Helpers

| Helper | Entity ID pattern | Purpose |
|---|---|---|
| `input_boolean` | `<slug>_occupied` | Occupancy helper |
| `input_datetime` | `<slug>_last_motion` | Last motion timestamp |
| `timer` | `<slug>_failsafe` | Failsafe timer (if failsafe enabled) |
| `input_number` | `<slug>_failsafe_timeout` | Failsafe timeout, minutes (optional) |
| `input_boolean` | override / force / manual | Optional controls |

## Differences from WITB+ 4.4.0

| | WITB+ 4.4.0 | Transit Room v2 |
|---|---|---|
| Door inputs | seal + transition doors | none |
| Exit evaluation timer | yes (door-open path) | none; motion-off timeout clears |
| "Door closes behind you" | optional | none |
| Latch helper / idle when sealed | optional | none |
| Entry gating | optional | none |
| Failsafe seal guard | yes | none |
| Everything else | — | same |

## Setup

1. Create the helpers above (package support follows in a later change).
2. Create an automation from `WITB Transit Room (2.0.0)` and bind motion, occupancy, last-motion and failsafe.
3. Point WITB Actions V3 at `binary_sensor.<slug>_occupied_effective`.

## Legacy

v1 (hold-timer driver with keepalive, instant-off and day/night hold) remains in `../v1/`.
