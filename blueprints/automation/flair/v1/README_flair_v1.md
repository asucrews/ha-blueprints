# README — flair v1

**Blueprint:** `flair.yaml`
**Version:** 1.0.4 (see `CHANGELOG_flair.md`)
**Domain:** automation
**Path:** `blueprints/automation/flair/v1/flair.yaml`
**Author:** Jeremy Crews
**Min HA version:** 2026.3.0

---

## Overview

Controls Flair smart vents for a single room based on the WITB+
`occupied_effective` occupancy signal. When the room becomes occupied the vent
is set to Active and any hold is cleared. When the room becomes unoccupied the
vent is set to Inactive and any hold is cleared.

This blueprint is a thin translation layer between the WITB+ occupancy
ecosystem and the Flair integration. All occupancy reasoning — door events,
PIR motion, exit evaluation, debounce — lives upstream in the WITB+ occupancy
blueprint. This blueprint reacts only to the final binary result.

---

## How It Works

### Primary control

| `occupied_effective` | Flair action |
|---|---|
| `on` | Set activity status → `Active`, press clear hold |
| `off` | Set activity status → `Inactive`, press clear hold |

### Reconciliation

If `flair_activity_status` changes for any reason (manual Flair app change,
cloud state reset, integration hiccup) and does not match `occupied_effective`,
the blueprint corrects it after `reconciliation_delay` seconds (default 5 s).
The short delay prevents fighting intentional manual changes or brief cloud
state churn.

A pre-delay mismatch check prevents unnecessary reconciliation cycles when this
automation's own service calls trigger the reconciliation path — if the status
already matches at trigger time, the branch exits immediately.

`unknown` and `unavailable` transitions on HA restart are filtered out and do
not trigger reconciliation.

### Startup sync

On every HA restart the blueprint waits 30 seconds for WITB+ and the Flair
integration to fully restore, then reconciles vent state against the current
`occupied_effective`. This recovers from any drift that occurred while HA was
offline.

---

## Inputs

### Required

| Input | Domain | Example | Notes |
|---|---|---|---|
| `occupied_effective` | `binary_sensor` | `binary_sensor.office_occupied_effective` | WITB+ output — **not** the raw `input_boolean` |
| `flair_activity_status` | `select` | `select.office_flair_activity_status` | Flair activity status for this room |
| `flair_clear_hold` | `button` | `button.office_flair_clear_hold` | Flair clear hold button for this room |

### Optional

| Input | Default | Range | Notes |
|---|---|---|---|
| `reconciliation_delay` | `5` seconds | `0–60` | Wait before correcting a mismatched Flair status |

---

## Architecture notes

- **`mode: restart`** — if a new event fires while a reconciliation delay is
  in progress, the run restarts and the delay resets. This naturally handles
  rapid Flair cloud state churn without oscillating. Latest state always wins.
- **WITB+ as single source of truth** — do not wire a raw door sensor, motion
  sensor, or `input_boolean.room_slug_occupied` directly. Those inputs are
  evaluated upstream by WITB+. Using `occupied_effective` ensures this blueprint
  always sees the fully evaluated, debounced occupancy state.
- **Startup delay is intentionally blocking** — the 30-second delay fires once
  per HA restart. Converting it to an event-driven timer helper is not justified
  for a one-time-per-restart path.
- **No `variables` block needed** — `!input` values are consumed directly in
  `state` conditions. No Jinja2 computation is required.

---

## Known limitations

- **Startup sync abandoned on early occupancy change** — if `occupied_effective`
  changes during the 30-second startup delay, `mode: restart` cancels the
  startup sync and runs the occupancy branch instead. The new occupancy state
  is correctly applied but no startup reconciliation occurs. This is acceptable
  because the primary control branch handles the transition correctly.

---

## Files in this directory

| File | Purpose |
|---|---|
| `flair.yaml` | Blueprint |
| `CHANGELOG_flair.md` | Version history |
| `rules_flair.md` | Behavioral rules and invariants |
| `use_cases_flair.md` | Supported use cases with pass/fail outcomes |

---

## Related blueprints

| Blueprint | Purpose |
|---|---|
| `witb_plus` | Occupancy inference — produces `occupied_effective` |
| `witb_plus_actions_lights_fan` | Lights and fan control based on `occupied_effective` |
| `witb_plus_bed_sensor` | Drives `force_occupied` while someone is in bed |
| `witb_transit_room` | PIR-decay occupancy for hallways and transit areas |
