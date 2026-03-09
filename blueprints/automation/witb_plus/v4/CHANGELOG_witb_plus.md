# CHANGELOG — WITB+ (Where Is The Body — Room Occupancy Inference)

All notable changes to this blueprint are documented here.  
Format: `[version] — date — summary`, followed by itemized changes.

---

## [4.2.0] — 2026-02-26 — Reliability Fixes

### Fixed
- **FIX #1 — Duplicate triggers removed:** `transition_open` and `seal_open` triggers
  removed. Door-open logic now uses `trigger.to_state.state == 'on'` checks inside
  the `transition_change` / `seal_change` blocks to eliminate double-execution races
  under `mode: restart`.

- **FIX #2 — Timer-based exit evaluation (non-blocking):** Block 5 now starts a
  dedicated `exit_eval_timer` instead of blocking with `wait_template`. The automation
  run completes immediately. When the timer fires, a new run evaluates whether to
  clear occupancy. Motion returning before the timer fires cancels it cleanly.
  This allows `mode: restart` to be used (fast, non-blocking) and eliminates stale
  queued evaluations from piling up.

- **FIX #3 — `exit_recent` recomputed post-delay:** The `exit_eval_done` handler
  recalculates `exit_recent_rt` at runtime so an expired exit window is never treated
  as still-recent at evaluation time.

- **FIX #4 — Deadlock break guards `force_occupied`:** Condition B of the failsafe
  (hard deadlock break) no longer clears occupancy when `force_occupied` is ON.
  A forced-occupied room cannot be cleared by the motion-idle deadlock path.

- **FIX #5 — Latch sync gated to relevant triggers:** Action 1 (latch sync) only
  fires on door/seal/motion triggers, preventing churn on failsafe, override, and
  force-change events.

- **FIX #6 — mmWave uses `platform: state` triggers:** Replaced unreliable template
  triggers with proper `platform: state` triggers for `mmwave_on` / `mmwave_off_for`.
  Template triggers without a watched `entity_id` can miss transitions.

- **FIX #7 — Optional entity triggers safely ignored:** Control triggers
  (override/force/manual) use empty-list inputs that HA 2024.4+ skips cleanly when
  the helper is not configured.

- **FIX #8 — `fs_duration_hms` capped at 99 hours:** Prevents invalid timer strings
  for durations ≥ 100 hours. The slider max of 5940 min (99h) makes this a safety
  net, but the cap is enforced in the template regardless.

- **FIX #9 — Shared "assert occupied" logic:** Occupancy-assertion steps are now
  consistently structured across all assert paths (motion, mmWave, force, manual),
  reducing divergence and future maintenance surface.

- **FIX #10 — `seconds_since_door` precision:** Removed `| int` truncation from
  `now().timestamp()` so sub-second precision is preserved. This matters for short
  entry windows (5–15 s) where integer truncation could cause boundary misses.

---

## [4.0.5] — prior release — Feature baseline

### Features
- **PIR-based occupancy assertion** with configurable exit timeout.
- **Transition door semantics:** one or more doors representing boundary crossings.
  A door-open + motion-off path drives exit evaluation.
- **Seal door semantics:** main/privacy door. When CLOSED, clearing is blocked
  (protects sleeping or still occupants).
- **mmWave support (optional):** Can block clearing while ON and/or assert occupancy.
  Recommended: blocks-clear only, to avoid cross-room false positives.
- **Failsafe timer (optional):** Prevents permanently stuck occupied states.
  Safe behavior: never clears while seal door is CLOSED; restarts instead.
  Hard deadlock break at 1.5× failsafe duration when motion has been off that long.
- **Force Occupied:** Pins the room occupied; blocks all clearing paths including
  the failsafe deadlock break.
- **Manual Occupied:** Asserts occupancy but still allows normal exit-based clearing.
- **Automation Override:** When ON, the automation does nothing (full manual handoff).
- **Entry gating (optional):** Prevents walk-by false positives on open-door sightlines.
  Motion only asserts occupancy if a door event occurred within `entry_window_seconds`,
  or if the seal door is closed, or if the room is already occupied.
- **"Door closes behind you" path (optional):** Supports bedroom/garage-style exits
  where the door closes after you leave. Uses `last_exit_door_helper` and a
  configurable `exit_recent_window_seconds` to allow clearing after close.
- **Latch helper (optional debug):** `input_boolean` that mirrors "sealed + occupied"
  state for dashboard debugging.

---

## Roadmap / known considerations
- `entry_window_helper` currently lives inside the `failsafe` input section in the UI.
  This is a cosmetic placement issue — it will move to the `entry_gating` section in
  a future release.
- Per-room package scaffolding (all required helpers pre-created) is planned as a
  companion template to reduce first-time setup friction.
- A `last_mmwave_helper` (input_datetime) for mmWave-specific idle tracking is under
  consideration for rooms where PIR coverage is poor.
