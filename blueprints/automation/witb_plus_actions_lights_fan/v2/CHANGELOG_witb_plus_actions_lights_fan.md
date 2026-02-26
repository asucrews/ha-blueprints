# CHANGELOG — WITB+ Actions: Lights + Fan

All notable changes to this blueprint are documented here.  
Format: `[version] — date — summary`, followed by itemized changes.

---

## [2.2.1] — 2026-02-26 — Bed Sensor Integration

### Added
- **`bed_occupied`** (optional `binary_sensor` input): connects a bed presence sensor
  so the blueprint is aware when an occupant is in bed.
- **`suppress_lights_on_when_in_bed`** (boolean, default `true`): when enabled,
  prevents the `occupied_on` branch from turning lights ON if the bed sensor is ON
  and lights are currently OFF. Solves two failure modes:
  - Midnight bathroom return — motion re-asserts occupancy but lights stay off.
  - In-bed motion events — shifting/rolling in bed won't wake lights.
- **`in_bed`** variable: safe evaluation of the bed sensor that handles `none`/`''`
  input gracefully (`is not none and != ''` guard).
- **`manual_off_hold`** variable: detects when the automation previously turned lights
  on (`auto_tag_lights == on`) but the lights are now all off — meaning the user
  manually turned them off. Prevents lights from auto-reasserting due to continued
  occupancy events until the room goes vacant and `auto_tag_lights` resets. Falls
  back to `false` when `auto_tag_lights` is not configured (fully backward compatible,
  no behavior change for existing instances).
- **Two new condition guards** in the `# ---- Lights ON ----` branch of `occupied_on`:
  - `manual_off_hold` guard — don't re-turn-on lights after a manual off.
  - In-bed suppress guard — don't turn lights on when in bed and currently dark.

### Backward compatibility
All new inputs are optional with safe defaults. Existing automation instances using
v2.2.0 behave identically unless `bed_occupied` is configured.

---

## [2.2.0] — 2026-02-xx — Reliability Fixes

### Fixed
- **FIX #1 — CRITICAL:** `timer_finished` trigger now scoped to `fan_runon_timer`
  only via `event_data` filter. Previously fired on *every* `timer.finished` event
  in the entire HA instance, causing the automation to evaluate all variables on
  every room's exit_eval, failsafe, and cooldown timer completions across the home.
- **FIX #2 — CRITICAL:** `override_ok` and `force_ok` inlined in all blocking
  `while` loops. Both are top-level variables frozen at trigger time. In humidity
  hold loops that can run for up to `humidity_hold_max` (default 1h), turning on
  `automation_override` or a blocking entity mid-loop had no effect — the loop kept
  running. Now checks live entity state directly. Same fix applied to the lights-off
  retry loop occupancy condition.
- **FIX #3:** Lux hysteresis actually implemented. Changelog claimed "10% buffer
  added" but the check was strict `lux_value < lux_threshold` with no buffer at all.
  Fixed: `lux_value < (lux_threshold * 1.1)` so lights turn on up to 10% above
  threshold to prevent dusk flicker.
- **FIX #4:** `fan_runon_active` and `any_light_on` re-evaluated inline in startup
  cleanup. Both were top-level variables computed at `ha_start` time, then checked
  after `startup_cleanup_delay` + 15s double-tap — by which point the cached values
  could be stale.
- **FIX #5:** `fan_switches` domain selector indentation corrected from 1 space to
  2 spaces. Technically invalid YAML that could break on strict parsers.
- **FIX #6:** Optional entity defaults standardized — single-entity optionals use
  `default: ''` consistently; multi-entity optionals use `default: []`. Previously
  mixed usage made guard logic fragile.
- **FIX #7:** Removed stale comment that contradicted the hysteresis fix (lines
  saying "Actually, simple gate… If you want hysteresis…").
- **FIX #8:** Startup cleanup override/force checks now use inline live evaluation
  instead of frozen top-level variables, for consistency with FIX #2.

---

## [2.1.1] — Initial tracked release — Feature baseline

### Features
- **Soft-Off Warning:** Lights dim to 10% for 15s before turning off completely.
- **Dynamic Fan Run-On:** `input_number` helper for configurable run-on minutes.
- **Lux Hysteresis:** 10% buffer on illuminance threshold (*advertised* in this
  version; not actually applied until FIX #3 in v2.2.0).
- **Hardened Startup Cleanup:** Double-tap validation (wait 15s, re-check) prevents
  false cleanup triggers after HA restart.
- **Availability checks** in verification loops (lights-off retry, humidity hold).

---

## Roadmap / known considerations
- `manual_off_hold` resets only on vacancy — there is currently no explicit "re-arm"
  button. If you want lights to auto-assert again while still occupied, toggle
  `auto_tag_lights` off or use `automation_override` then re-enter.
- Per-side bed suppression (Left/Right sensors) is not yet a blueprint input;
  configure the relevant side sensor as `bed_occupied` manually for now.
- A future `sleep_mode` input_boolean is planned to allow "in bed but allow auto-ON"
  as a distinct state from in-bed + suppress.
