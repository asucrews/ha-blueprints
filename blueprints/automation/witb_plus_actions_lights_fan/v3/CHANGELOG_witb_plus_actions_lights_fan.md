# CHANGELOG — WITB+ Actions: Lights + Fan

All notable changes to this blueprint are documented here.  
Format: `[version] — date — summary`, followed by itemized changes.

---

## [3.0.5] — 2026-03-22 — Universal fan switch actions

### Fixed

- **FIX — `fan_switches` actions now use `homeassistant.turn_on/off` instead of
  `switch.turn_on/off`.** Some manufacturers wire fan speed controls as `light`
  domain entities rather than `switch`. The previous `switch.*` service calls were
  no-ops for those entities, leaving the fan uncontrolled. All 6 fan_switches action
  sites (occupied_on immediate path, fan_on_delay_done, fan_runon_done, vacancy fan-off,
  fan_gate_cleared, startup cleanup) now use the universal `homeassistant` domain
  services which work on any entity domain. The selector already allowed both `switch`
  and `light` entities — the action calls now match.

---

## [3.0.4] — 2026-03-22 — Rename claim inputs, flip logic

### Changed

- **RENAME — `skip_on_if_any_light_on` → `lights_claim_if_already_on`.**
  The old name described a side effect (skipping the ON action); the new name
  describes the intent (claiming ownership of pre-existing light state). Default
  changed from `true` (skip by default) to `true` (claim by default) — the
  polarity of the input has flipped so `true` now means the opposite of what
  `skip=true` meant. The automation now claims ownership by default, which is
  the correct posture: if a blueprint is deployed for a room, it should control
  that room unless explicitly told not to.

  Logic in `occupied_on` updated accordingly:
  `(not skip_on_if_any_light_on) or (not any_light_on)`
  → `lights_claim_if_already_on or (not any_light_on)`

  **Migration:** Any room that previously relied on the default (`skip_on_if_any_light_on`
  not set, defaulting to `true` = skip) will now claim by default. If you have a room
  where you intentionally did not want the automation to claim pre-existing light state,
  explicitly set `lights_claim_if_already_on: false`.

- **RENAME — `fan_skip_on_if_already_on` → `fan_claim_if_already_on`.**
  Same rationale as above. Default is `true` (claim). Both the immediate-on path
  and the `fan_on_delay_done` path updated.

  Logic updated in both fan-on conditions:
  `(not fan_skip_on_if_already_on) or (not fan_is_on)`
  → `fan_claim_if_already_on or (not fan_is_on)`

  **Migration:** Same as lights — if you had a room where you intentionally set
  `fan_skip_on_if_already_on: false`, set `fan_claim_if_already_on: false` instead.
  All other rooms get claim-by-default automatically.

---

## [3.0.1] — 2026-03-22 — Rename claim input, flip logic (lights-only variant)

### Changed

- **RENAME — `skip_on_if_any_light_on` → `lights_claim_if_already_on`.**
  Same change as `lights_fan` v3.0.4 above. Applies to the lights-only blueprint.
  Default is `true` (claim by default). Logic condition flipped identically.

  **Migration:** Same as above — if you intentionally had a room not claiming
  pre-existing state, set `lights_claim_if_already_on: false` explicitly.

---

## [3.0.3] — 2026-03-09 — Post-Delay Vacancy Guard Fix

### Fixed

- **FIX — Post-delay occupancy check moved to outer sequence level.** The occupancy
  re-check after `fan_on_delay_done` must live at the outer `choose` condition level,
  not inside a nested sequence. Previously, a room going vacant during the fan on-delay
  could still trigger fan turn-on because the inner guard was not evaluated at the
  correct nesting depth. The check `is_state(occ, 'on')` is now a top-level condition
  on the `fan_on_delay_done` branch, ensuring vacancy mid-delay correctly aborts the
  fan turn-on.

---

## [3.0.2] — 2026-03-09 — min_version bump

### Changed

- **`min_version` bumped to `2026.3.0`** to reflect selector and trigger features used.

---

## [3.0.1] — 2026-03-03 — Fix fan_gate_cleared trigger crash

### Fixed
- **FIX — CRITICAL: Blueprint generates invalid automation for any room that does
  not configure `fan_vacancy_gate_entity`.** The `fan_gate_cleared` trigger uses
  `entity_id: !input fan_vacancy_gate_entity`. When the input is not provided, HA
  resolves the default `''` to `None` for the trigger's `entity_id` field and rejects
  the entire automation with "Entity is neither a valid entity ID nor a valid UUID".
  Every room without a vacancy gate — i.e. most rooms — was affected.

  Fix: changed `fan_vacancy_gate_entity` input `default` from `''` to `[]`. HA
  2024.4+ silently skips state triggers whose `entity_id` is an empty list, so the
  trigger is omitted entirely for unconfigured rooms. Added `fan_gate_enabled`
  variable (`fan_vacancy_gate_entity is string and fan_vacancy_gate_entity | length > 0`)
  and updated `fan_ok_to_turn_off` and the `fan_gate_cleared` condition guard to use
  it instead of `== ''` comparisons.

  This is the same pattern used in WITB+ v4.2 for all optional trigger entities
  (FIX #7 in that CHANGELOG).

---

## [2.3.3] — 2026-03-09 — Post-Delay Vacancy Guard Fix

### Fixed

- **FIX — Post-delay occupancy check moved to outer sequence level.** The occupancy
  re-check after the lights-off delay must live at the outer `choose` condition level.
  Previously, a room going vacant during the delay could still proceed through nested
  sequences because the guard was evaluated at the wrong nesting depth. The check is
  now a top-level condition on the `lights_off` branch, ensuring vacancy mid-delay
  correctly aborts the sequence.

---

## [2.3.2] — 2026-03-03 — Fix fan_gate_cleared trigger crash

### Fixed
- **FIX — CRITICAL: Same as v3.0.1 above.** `fan_vacancy_gate_entity` default
  changed from `''` to `[]`. Added `fan_gate_enabled` variable. Updated
  `fan_ok_to_turn_off` and condition guard. See v3.0.1 entry for full rationale.

---

## [3.0.0] — 2026-03-03 — Fully Event-Driven

### Summary
All blocking `delay:` steps in action sequences have been replaced with dedicated
timers. Every automation run now completes in milliseconds across all paths.
`mode:restart` is fully safe — no run can be killed mid-sequence while waiting.

### Added
- **`fan_on_delay_timer`** input (`timer.<slug>_actions_fan_on_delay`): replaces the
  blocking `delay:` in the `occupied_on` fan-on sequence. When delay > 0 and this
  timer is configured, `occupied_on` starts the timer and returns immediately. The new
  `fan_on_delay_done` trigger fires when the timer expires and performs the actual
  fan turn-on, guarded by `is_state(occ, 'on')` so a mid-delay vacancy cancels it.

- **`soft_off_timer`** input (`timer.<slug>_actions_soft_off`): replaces the `delay:
  00:00:15` in the soft-off dim warning sequence. `lights_off` dims to 10% and starts
  this 15 s timer, then returns immediately. The new `soft_off_done` trigger fires when
  the timer expires and sends the full `light.turn_off`, then chains into verify.

- **`lights_verify_timer`** input (`timer.<slug>_actions_lights_verify`): replaces the
  verify delay and the entire `repeat:` retry loop. After lights-off, the timer is
  started with `lights_off_verify_delay` as duration. When `lights_verify_done` fires:
  - Lights confirmed off → clear tag, reset counter.
  - Still on, retries remaining → increment counter, retry turn-off, restart timer
    with `lights_off_verify_retry_interval`.
  - Retries exhausted → handle tag per `lights_off_keep_tag_on_failure`, reset counter.

- **`lights_verify_attempts_helper`** input (`input_number.<slug>_actions_verify_attempts`):
  persists the retry count across independent timer-fired runs. Reset to 0 on
  `occupied_on` and after each verify cycle (pass or exhausted). If not configured,
  only a single verify check is performed (no retries).

- **Three new trigger IDs**: `fan_on_delay_done`, `soft_off_done`, `lights_verify_done`.
  All use `event_data` scoping so they only fire for this room's specific timer.

- **Package template v3**: adds `soft_off`, `lights_verify`, `fan_on_delay` timers
  and `verify_attempts` input_number. Adds five new binary_sensor indicators:
  `soft_off_active`, `lights_verify_active`, `fan_on_delay_active` (plus existing
  `cooldown_active`, `fan_runon_active`). All useful for dashboard diagnostics.

### Changed
- `occupied_on` now cancels all four vacancy-side timers (`fan_runon`, `fan_on_delay`,
  `soft_off`, `lights_verify`) and resets `verify_attempts` to 0 when room re-occupies.
  This ensures no stale timers fire after a re-occupy.
- `vacancy_began` now cancels `fan_on_delay_timer` as its first action, ensuring the
  fan never turns on after the room goes vacant mid-delay.
- Fan run-on timer is still started before the verify block per the v2.3.1 fix,
  preserving immunity to restart at that point.
- `timer_finished` trigger ID renamed to `fan_runon_done` for clarity (breaking
  change from v2 instances — update any custom YAML referencing this ID).
- Startup cleanup retains two blocking `delay:` steps (`startup_cleanup_delay` +
  `00:00:15` double-tap). These are intentional — `ha_start` fires once per restart
  and the stuck-state risk is negligible compared to the complexity of making them
  event-driven.

### Migration from v2
This is a **new blueprint in a new folder** (`v3/`). v2 instances continue working
unchanged. To migrate a room:
1. Generate a new v3 package from `witb_plus_actions_lights_fan_package_template.yaml`
   (v3 version) and load it — this creates the four new helpers.
2. Restart HA so helpers exist.
3. Create a new automation from the v3 blueprint for the room.
4. Wire all existing inputs plus the four new timer/number inputs.
5. Disable the v2 automation for that room.
6. The companion `witb_plus_actions_cleanup` blueprint is still recommended
   but is no longer the primary safety net.

### Removed
- Blocking `delay:` steps from all non-startup action sequences.
- Inline `repeat:` retry loop (replaced by event-driven verify cycle).

---

## [2.3.1] — 2026-03-03 — Fan Run-On Orphan Fix + Tag Cleanup Blueprint

### Fixed
- **FIX — CRITICAL: Fan run-on timer orphaned by mode:restart mid-sequence.**
  The `timer.start` for the fan run-on was previously located after the lights
  verify/retry block in the `lights_off` sequence. Any `mode:restart` kill during
  verify/retry delays would prevent the timer from starting. The fan would stay ON
  permanently with no timer ever firing to turn it off.

  Fix: `timer.start` is now called before the verify block, immediately after the
  first `light.turn_off` command. `timer.start` on an already-running timer is
  idempotent, so early invocation is safe in all paths. `timer_finished` still
  owns the actual fan-off.

- **FIX: `auto_tag_lights` stuck ON after mode:restart kill during verify loop.**
  Addressed by the new companion cleanup blueprint (see Added below).

### Added
- **Companion blueprint: `witb_plus_actions_cleanup.yaml` v1.0.0.**
  Belt-and-suspenders automation that catches `auto_tag_lights` or `auto_tag_fan`
  stuck-ON states. Inputs mirror the Actions instance for the same room.
  Deploy one instance per room alongside the Actions automation.

### Changed
- Verbose inline `# FIX v2.3.x` comment blocks removed from blueprint YAML.
  Replaced with brief `# See CHANGELOG vX.Y.Z` pointers.

---

## [2.3.0] — 2026-03-xx — External Gating (Lights + Fan)

### Added
- **`light_gating_entity`** (optional `binary_sensor`): replaces inline lux/sun
  evaluation. Must be ON for lights to assert. Leave empty for no gating.
- **`fan_vacancy_gate_entity`** (optional `binary_sensor`): replaces inline humidity
  polling loop. OFF = hold fan on; ON = ok to turn fan off. New `fan_gate_cleared`
  trigger fires when this transitions ON while room is vacant and fan is running.
- **`lights_ok_to_turn_on`** and **`fan_ok_to_turn_off`** variables.

### Removed
- Inline lux threshold inputs and evaluation logic.
- Inline humidity hold inputs and polling `while` loop.

### Migration
Create external automations for lux/humidity that write to a `binary_sensor`, then
wire into `light_gating_entity` / `fan_vacancy_gate_entity`.

---

## [2.2.1] — 2026-02-26 — Bed Sensor Integration

### Added
- **`bed_occupied`** (optional `binary_sensor`): bed presence sensor.
- **`suppress_lights_on_when_in_bed`** (boolean, default `true`): prevents
  `occupied_on` from turning lights ON when bed sensor is ON and lights are OFF.
  Solves midnight bathroom return and in-bed motion event false assertions.
- **`in_bed`** variable with safe `none`/`''` guard.
- **`manual_off_hold`** variable: detects user-manually-off state and prevents
  re-assertion until next vacancy cycle.

---

## [2.2.0] — 2026-02-xx — Reliability Fixes

### Fixed
- **FIX #1 — CRITICAL:** `timer_finished` scoped to `fan_runon_timer` via
  `event_data` filter — previously fired on every `timer.finished` in the instance.
- **FIX #2 — CRITICAL:** `override_ok` and `force_ok` inlined in all blocking
  loops — previously frozen at trigger time.
- **FIX #3:** Lux hysteresis actually implemented (`lux_value < lux_threshold * 1.1`).
- **FIX #4:** `fan_runon_active` and `any_light_on` re-evaluated inline in startup
  cleanup instead of using stale top-level variables.
- **FIX #5:** `fan_switches` domain selector indentation corrected.
- **FIX #6:** Optional entity defaults standardized (`''` / `[]`).
- **FIX #7:** Removed stale comment contradicting hysteresis fix.
- **FIX #8:** Startup cleanup checks use inline live evaluation.

---

## [2.1.1] — Initial tracked release — Feature baseline

### Features
- Soft-Off Warning, Dynamic Fan Run-On, Lux Hysteresis (advertised; applied in FIX #3),
  Hardened Startup Cleanup, availability checks in verification loops.

---

## Roadmap / known considerations
- `manual_off_hold` resets only on vacancy. To re-arm while still occupied, toggle
  `auto_tag_lights` off or use `automation_override` then re-enter.
- Per-side bed suppression (Left/Right) not yet a blueprint input.
- Startup cleanup `delay:` steps are intentionally left blocking in v3 — low risk.
- A `sleep_mode` input_boolean is planned to allow "in bed but allow auto-ON"
  as a distinct state from in-bed + suppress.
