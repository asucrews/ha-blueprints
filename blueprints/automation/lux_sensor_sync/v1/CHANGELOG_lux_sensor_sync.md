# CHANGELOG — Lux Sensor Sync

---

## lux_sensor_sync.yaml

### v1.0.0 — 2026-03-09

#### Initial release

- Infers light on/off state from a lux delta sensor for lights that cannot be
  directly controlled by Home Assistant (fan-mounted lights, dumb switches, etc.).
- Writes inferred state to an `input_boolean` for consumption by other
  automations (e.g. WITB+ Actions `light_gating_entity`).
- Trigger-based: fires on `numeric_state` crossing configurable `on_threshold`
  and `off_threshold` with independent debounce timers (`on_for_seconds`,
  `off_for_seconds`).
- Both conditions guard against redundant actions (only turns on if currently
  off, only turns off if currently on).
- `ha_start` trigger re-evaluates state after a 30 s settling delay on HA
  restart so the boolean does not drift until the next lux change.
- `mode: restart` ensures a new trigger is always acted on rather than dropped
  if the automation is mid-run.

---

## lux_sensor_sync_package_template.yaml

### v1.0 — 2026-03-09

#### Initial release

- Adaptive exponential-weighted-average (EWA) lux baseline sensor
  (`sensor.room_slug_lux_baseline`) implemented as a trigger-based template
  sensor. Fires on every lux state change and every 5 minutes.
- Baseline freeze logic:
  - **Freeze while light on**: when `input_boolean.room_slug_lux_freeze_while_light_on`
    is `on` and the inferred light boolean (`__LIGHT_BOOLEAN__`) is `on`, the
    baseline holds its previous value. Prevents the baseline from chasing the
    light-on level and eroding the delta signal over time.
  - **Big rise freeze**: a sudden lux jump ≥ `big_rise_freeze` threshold freezes
    the baseline for one cycle, letting the cause be identified before the
    baseline reacts. Defaults to 50 lx.
  - **Ambient fall** (cur ≤ prev): baseline follows downward at `alpha_down`
    (default 0.15). Tracks blinds closing and sunset reasonably quickly.
  - **Small ambient creep** (rise < `settle_band`): follows at `alpha_up`
    (default 0.01). Very slow upward tracking to handle gradual sunrise
    without drifting into light-on territory.
  - **Rise above band but below big_rise**: baseline holds. Lets ambiguous
    mid-range rises settle before committing.
- Lux delta sensor (`sensor.room_slug_lux_delta`): `max(lux − baseline, 0)`,
  floored at `input_number.room_slug_lux_delta_floor` (default 0 lx).
- Tuning helpers block (`# --- BEGIN/END tuning_helpers ---`) with
  `input_boolean` and seven `input_number` entities. Omit with
  `--no-tuning-helpers` in the package generator. Baseline logic falls back
  to hardcoded defaults when helpers are absent.
- Placeholder `binary_sensor` block included to satisfy HA package
  `!include_dir_merge_named` requirements. See README for deployment notes.
