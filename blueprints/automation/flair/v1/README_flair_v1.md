# README — flair v1

**Blueprint:** `flair.yaml`
**Version:** 1.1.0 (see `CHANGELOG_flair.md`)
**Domain:** automation
**Path:** `blueprints/automation/flair/v1/flair.yaml`
**Author:** Jeremy Crews
**Min HA version:** 2026.3.0

---

## Overview

Controls Flair smart vents for a single room based on the WITB+
`occupied_effective` occupancy signal. When the room becomes occupied the vent
is set to Active and any hold is cleared. When the room has stayed unoccupied
for `inactive_delay_minutes` whole minutes (default 0, immediate) the vent is set to Inactive and any
hold is cleared.

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
| `off` for `inactive_delay_minutes` | Set activity status → `Inactive`, press clear hold |
| `off`, back `on` inside the delay | Delay cancelled; Room Occupied fires: `select_option` → `Active` (already Active) and clear hold pressed |

### Reconciliation

If `flair_activity_status` changes for any reason (manual Flair app change,
cloud state reset, integration hiccup) and does not match `occupied_effective`,
the blueprint corrects it after `reconciliation_delay` seconds (default 5 s).
The short delay prevents fighting intentional manual changes or brief cloud
state churn.

While the room is vacant but has been off for less than `inactive_delay_minutes`,
`Active` is correct and is not corrected. It is only corrected to `Inactive`
once `occupied_effective` has been off for at least `inactive_delay_minutes`.

A pre-delay mismatch check prevents unnecessary reconciliation cycles when this
automation's own service calls trigger the reconciliation path — if the status
already matches at trigger time, the branch exits immediately.

`unknown` and `unavailable` transitions on HA restart are filtered out and do
not trigger reconciliation.

### Consistency sweep

Once a minute a `time_pattern` trigger checks whether the room is out of step.
A top-level condition lets the sweep start a run only if both
`occupied_effective` and the Flair status are known and either the room is
occupied and not `Active`, or it has been vacant for at least
`inactive_delay_minutes` and is not `Inactive`, and the Flair status has been
unchanged for at least `reconciliation_delay`, so the sweep never cuts a
reconciliation wait short. Inside the delay either status is accepted. The run sets the desired status and presses clear hold. When the
room is in step, no run starts, so the sweep never cancels startup sync or a
pending reconciliation. Traces show these as "condition not met" runs. The
sweep corrects a lost vacancy timer, a startup sync cancelled by a real event,
or Flair restoring from `unavailable`. Recovery happens at the next sweep after
both entities are known, the Flair status state has stayed unchanged for at
least `reconciliation_delay`, and (for a vacant room only) the vacancy delay
has elapsed, subject to the service calls succeeding. Continuous Flair flapping
can postpone correction; recovery resumes once the status stays unchanged for
`reconciliation_delay`. For example, occupancy restoring `unavailable` → `on`
against a long-standing `Inactive` status makes the next sweep eligible
immediately.
An uninterrupted startup sync checks after 30 s; at delay 0 an eligible sweep
inside the startup wait can correct earlier and replace the startup run.

#### Traces

A sweep whose condition fails still creates a trace every minute, which
crowds out HA's default 5 stored traces. Raise `stored_traces` on the
automation (in its YAML) for a longer history.

### Startup sync

On every HA restart the blueprint waits 30 seconds for WITB+ and the Flair
integration to fully restore, then reconciles vent state against the current
`occupied_effective`. This recovers from any drift that occurred while HA was
offline. Startup sync ignores `inactive_delay_minutes`: a vacant room is set Inactive
after the 30 seconds if the run is uninterrupted, because the vacancy timer
does not survive a restart. A real event can cancel the run, and an eligible
consistency sweep can replace it earlier at delay 0.

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
| `inactive_delay_minutes` | `0` (immediate) | `0–60` minutes | Whole minutes the room must be vacant before Flair is set Inactive; returning inside the delay keeps it Active |
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
- **Variables and a template condition** — a small `variables:` block holds
  the delay (`inactive_delay_is_zero`) and the entity IDs, and a top-level
  template condition gates the Room Unoccupied and Consistency Sweep triggers.
  Rejected triggers do not start (or restart) the action script.

---

## Known limitations

- **Startup sync abandoned on early occupancy change** — if `occupied_effective`
  goes `on` during the 30-second startup delay (or goes `off` with
  `inactive_delay_minutes` 0), `mode: restart` cancels the startup sync and runs the
  occupancy branch instead. The new occupancy state is correctly applied but no
  startup reconciliation occurs. This is acceptable because the primary
  control branch handles the transition correctly. Startup sync can be
  cancelled by a real event; the consistency sweep then corrects any remaining
  mismatch at the next eligible sweep (see Consistency sweep).
- **Positive `inactive_delay_minutes` and startup** — an `on` → `off` change
  during the startup delay does not cancel startup sync, because Room
  Unoccupied only fires after the delay. Startup sync finishes at 30 s and
  sets Inactive if the room is vacant (it ignores the delay). A delay shorter
  than 30 s (the number box accepts fractions) could expire first and cancel
  startup sync; use whole minutes.
- **Availability blips** — with a positive delay, `unavailable`/`unknown` →
  `off` also starts the vacancy window, so a blip during the delay restarts it
  instead of losing it. At `inactive_delay_minutes` 0 a top-level condition
  drops that trigger, so `unavailable` → `off` (for example at HA start) does
  not start a run or cancel the startup sync; behavior is exactly 1.0.5.

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
