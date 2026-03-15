# README — humidity_controled_fan v1

**Blueprint:** `humidity_controled_fan.yaml`
**Version:** 1.1.1 (see `CHANGELOG_humidity_controled_fan.md`)
**Domain:** automation
**Path:** `blueprints/automation/humidity_controled_fan/v1/humidity_controled_fan.yaml`
**Author:** asucrews
**Min HA version:** 2024.4.0

---

## Overview

Controls a bathroom exhaust fan using a humidity delta sensor. The delta
represents how far above its adaptive baseline the current humidity is —
a much more reliable signal than a fixed RH threshold across seasons.

The blueprint does **not** compute the baseline or delta itself. It expects
a pre-built delta sensor (typically generated via
`humidity_controled_fan_package_template.yaml`).

---

## How It Works

### Core control loop

| Condition | Action |
|---|---|
| Delta >= `on_threshold` for `on_for_seconds` | Turn fan ON |
| Delta <= `off_threshold` for `off_for_seconds` AND fan on >= `min_run_seconds` | Turn fan OFF |
| Fan on for `max_run_seconds` | Turn fan OFF (failsafe) |

### Night mode (optional)

When `night_mode_enabled: true`, turn-ON actions are suppressed during the
configured quiet window. Turn-OFF is never suppressed — if a shower ran
just before the window started, the fan must be allowed to finish clearing
the room.

Overnight spans are supported (e.g. `night_start: "22:00:00"`,
`night_end: "07:00:00"`).

### Startup sync

On every HA restart the blueprint waits 30 seconds for sensors to restore,
then corrects fan state:
- **Turn-OFF correction** is always active — if delta is low and fan is on,
  the fan is turned off.
- **Turn-ON correction** is opt-in via `ha_start_allow_turn_on: true` — if
  delta is high and fan is off, the fan is turned on. Night mode is respected.

---

## Inputs

### Entities

| Input | Domain | Description |
|---|---|---|
| `delta_sensor` | `sensor` | Humidity above baseline in % |
| `fan_entity` | `fan`, `switch`, or `light` | Exhaust fan entity to control |

### Thresholds and timing

| Input | Default | Description |
|---|---|---|
| `on_threshold` | `8%` | Turn ON when delta reaches this value |
| `on_for_seconds` | `120 s` | Delta must stay above threshold for this long before turning on |
| `off_threshold` | `3%` | Turn OFF when delta drops to this value |
| `off_for_seconds` | `600 s` | Delta must stay below threshold for this long before turning off |

### Run limits

| Input | Default | Description |
|---|---|---|
| `min_run_seconds` | `300 s` | Minimum ON time before turn-off is allowed |
| `max_run_seconds` | `5400 s` | Failsafe: force-off after this runtime regardless of humidity |

### Night mode and restart

| Input | Default | Description |
|---|---|---|
| `night_mode_enabled` | `false` | Enables quiet window suppression of turn-on |
| `night_start` | `22:00:00` | Start of quiet window |
| `night_end` | `07:00:00` | End of quiet window (overnight spans supported) |
| `ha_start_allow_turn_on` | `false` | Allow startup sync to turn fan ON when humidity is elevated |
| `suppress_turn_on_after_sensor_restore` | `true` | Suppress turn-on when sensor just restored from unknown/unavailable (HA restart or sensor reconnect) |

---

## Architecture notes

- **Two-step `variables:` pattern** — top-level block aliases `!input` boolean
  and time inputs. `_in_night_window` is computed in an action-step variable
  so `now()` is evaluated fresh on every run, not at automation load time.
- **`mode: restart`** — latest trigger always wins. A new humidity event during
  a startup delay cancels the startup sync and applies the new state immediately.
- **Night window re-evaluated after startup delay** — the `ha_start` branch
  re-computes the night window inline after the 30-second settling delay. A
  restart at 21:59 correctly sees the 22:00 window after settling.
- **`homeassistant.turn_on/off`** — used instead of `fan.turn_on/off` or
  `switch.turn_on/off` to support all three allowed entity domains with a
  single service call.

---

## Known limitations

- **Sensor reconnect mid-shower may delay turn-on (`suppress_turn_on_after_sensor_restore: true`)** —
  if the sensor drops to unavailable during a shower then reconnects, the first
  trigger fire after reconnect is suppressed. Turn-on proceeds normally after
  the sensor makes another state change (which is typical during an active
  shower). Disable `suppress_turn_on_after_sensor_restore` if this is a concern.
- **Midnight-spanning `on_for_seconds`/`off_for_seconds` not an issue** — these
  use HA's native `for:` duration on `numeric_state` triggers, not time
  comparisons, so no midnight-spanning edge case applies.

---

## Companion files

| File | Purpose |
|---|---|
| `humidity_controled_fan_package_template.yaml` | Generates adaptive baseline + delta sensors per room |
| `CHANGELOG_humidity_controled_fan.md` | Version history for blueprint and companion files |
| `rules_humidity_controled_fan.md` | Behavioral rules and invariants |
| `use_cases_humidity_controled_fan.md` | Supported use cases with pass/fail outcomes |

### Generating companion packages

```bash
python blueprints/generate_witb_packages_templated.py \
  --rooms "Half Bathroom" \
  --template blueprints/automation/humidity_controled_fan/v1/humidity_controled_fan_package_template.yaml \
  --out blueprints/automation/humidity_controled_fan/v1/packages
```

Use `--no-tuning-helpers` to omit the `input_boolean` and `input_number`
tuning entities if you prefer hardcoded defaults.

---

## Recommended starting values

| Parameter | Value | Notes |
|---|---|---|
| `on_threshold` | `8%` | Catches showers without false positives |
| `on_for_seconds` | `120 s` | Ignores brief steam spikes |
| `off_threshold` | `3%` | Low enough to confirm room is dry |
| `off_for_seconds` | `600 s` | Prevents premature shutoff while humidity falls |
| `min_run_seconds` | `300 s` | Fan runs at least 5 minutes per activation |
| `max_run_seconds` | `5400 s` | 90-minute failsafe |
