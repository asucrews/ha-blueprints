# WITB+ Bed → Force Occupied v1

Implementation documentation for `witb_plus_bed_force_occupied.yaml`.

## Source

- Blueprint: `blueprints/automation/witb_plus_bed_sensor/v1/witb_plus_bed_force_occupied.yaml`
- Blueprint README: `blueprints/automation/witb_plus_bed_sensor/v1/README_witb_plus_bed_force_occupied_v1.md`
- Changelog: `blueprints/automation/witb_plus_bed_sensor/v1/CHANGELOG_witb_plus_bed_force_occupied.md`

## Purpose

Keeps a bedroom "occupied" while someone is in bed by driving the `force_occupied` input_boolean in WITB+ v4. Without this, WITB+ may clear occupancy when a sleeping person stops triggering motion sensors — resulting in lights or fans turning off during sleep.

## Safety Gate (Critical)

The ON path has a **mandatory `occupied_effective` condition**: `force_occupied` is only set ON if the room is already occupied. This ensures a bed sensor can **extend** occupancy but can never **initiate** it. An object left on the bed (laundry basket, pet) cannot turn on lights in an empty room.

## Behavior

```
Bed sensor ON for bed_on_delay AND occupied_effective ON
  → force_occupied = ON

Bed sensor OFF for bathroom_grace
  → force_occupied = OFF  (unconditional — no occupancy check)
```

The OFF path is unconditional to handle the "midnight bathroom" case: a person leaves the bed, briefly leaves the room, and returns. The grace period absorbs the trip so WITB+ does not run vacancy logic. When grace expires, `force_occupied` is released and WITB+ resumes normal vacancy evaluation.

## ESPHome Double-Delay

If your bed pressure sensor already uses `delayed_off` in ESPHome firmware, stacking `bathroom_grace` here produces cumulative delay. Enforce the grace in exactly one place:

| Option | ESPHome `delayed_off` | `bathroom_grace` here |
|---|---|---|
| A (recommended) | Short (e.g. 10–30s) | Full grace (e.g. 5 min) |
| B | Full grace (e.g. 5 min) | `0s` |

## Inputs

| Input | Default | Purpose |
|---|---|---|
| `bed_sensor` | — | In-bed presence sensor (Normal or Slow variant recommended) |
| `occupied_effective` | — | WITB+ occupancy gate (`binary_sensor.<slug>_occupied_effective`) |
| `force_occupied` | — | Force-occupied helper (`input_boolean.<slug>_force_occupied`) |
| `bed_on_delay` | `00:00:30` | Debounce before setting force_occupied ON |
| `bathroom_grace` | `00:05:00` | Grace period before releasing force_occupied OFF |

## Mode

`restart` — a new trigger restarts the automation, so a rising bed-sensor edge always re-evaluates.

## Pairing with WITB+ Actions v2.2+

- **This blueprint** → drives `force_occupied` (persistence/sleep guard).
- **Actions blueprint** → use the **Fast** bed sensor variant for `bed_occupied` (instant lights-on suppression).

Both blueprints can run simultaneously on the same room. They use different sensor variants (Normal/Slow vs Fast) and serve distinct purposes.

## Minimum HA Version

`2026.2.0`
