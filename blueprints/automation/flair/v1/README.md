# Smart Vents - Flair

**Version:** 1.0.4
**Author:** Jeremy Crews
**Domain:** automation
**Min HA version:** 2025.6.0

---

## Overview

Controls Flair smart vents for a single room based on the WITB+ `occupied_effective`
occupancy signal. When the room becomes occupied the vent is set to Active and any
hold is cleared. When the room becomes unoccupied the vent is set to Inactive and
any hold is cleared.

This blueprint is a thin translation layer between the WITB+ occupancy ecosystem and
the Flair integration. All occupancy reasoning — door events, PIR motion, exit
evaluation, debounce — lives upstream in the WITB+ occupancy blueprint. This
blueprint reacts only to the final binary result.

---

## How It Works

### Primary control

| `occupied_effective` | Flair action |
|---|---|
| `on` | Set activity status → `Active`, press clear hold |
| `off` | Set activity status → `Inactive`, press clear hold |

### Reconciliation

If `flair_activity_status` changes for any reason (manual Flair app change, cloud
state reset, integration hiccup) and does not match `occupied_effective`, the
blueprint corrects it after `reconciliation_delay` seconds (default 5 s). The short
delay prevents fighting intentional manual changes or brief cloud state churn.

A pre-delay mismatch check prevents unnecessary reconciliation cycles when this
automation's own service calls trigger the reconciliation path — if the status
already matches after the trigger fires, the branch exits immediately.

`unknown` and `unavailable` transitions on HA restart are filtered out and do not
trigger reconciliation.

### Startup sync

On every HA restart the blueprint waits 30 seconds for WITB+ and the Flair
integration to fully restore, then reconciles vent state against the current
`occupied_effective`. This recovers from any drift that occurred while HA was
offline.

---

## Required Entities

Create one automation instance per room. Each instance requires:

| Entity | Example | Notes |
|---|---|---|
| `binary_sensor` | `binary_sensor.office_occupied_effective` | WITB+ output — **not** the raw `input_boolean` |
| `select` | `select.office_flair_activity_status` | Flair activity status for this room |
| `button` | `button.office_flair_clear_hold` | Flair clear hold button for this room |

---

## Configuration

### Required

- **WITB+ Occupied Effective** — `binary_sensor.room_slug_occupied_effective` from
  the WITB+ occupancy blueprint for this room.
- **Flair Activity Status** — The Flair activity status select entity for this room.
- **Flair Clear Hold Button** — The Flair clear hold button entity for this room.

### Optional

- **Flair Status Reconciliation Delay** (default: `5` seconds, range: `0–60`) —
  How long to wait before correcting a mismatched Flair status. Increase if your
  Flair integration takes longer to settle after a manual change. Set to `0` to
  correct immediately.

---

## Design Notes

- **`mode: restart`** — If a new event fires while a reconciliation delay is in
  progress, the run restarts and the delay resets. This naturally handles rapid Flair
  cloud state churn without oscillating.

- **WITB+ as single source of truth** — Do not wire a raw door sensor, motion sensor,
  or `input_boolean.room_slug_occupied` directly into this blueprint. Those inputs are
  evaluated upstream by WITB+. Using `occupied_effective` ensures this blueprint
  always sees the fully evaluated, debounced occupancy state.

- **Startup delay is intentionally blocking** — The 30-second delay in the startup
  sync sequence fires once per HA restart. Converting it to an event-driven timer
  helper is not justified for a one-time-per-restart path.

---

## Rooms

This blueprint is designed to be instantiated once per room that has a Flair vent.
Typical rooms in a WITB+ deployment:

- Garage
- Half Bathroom
- Master Bedroom
- Master Bedroom Closet
- Master Bathroom
- Master Bathroom Toilet
- Laundry
- Office

---

## Related Blueprints

| Blueprint | Purpose |
|---|---|
| `witb_plus` | Occupancy inference — produces `occupied_effective` |
| `witb_plus_actions_lights_fan` | Lights and fan control based on `occupied_effective` |
| `witb_plus_bed_sensor` | Drives `force_occupied` while someone is in bed |
| `witb_transit_room` | PIR-decay occupancy for hallways and transit areas |
