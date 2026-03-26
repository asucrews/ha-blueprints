# CHANGELOG — WITB+ (Where Is The Body — Room Occupancy Inference)

All notable changes to this blueprint are documented here.  
Format: `[version] — date — summary`, followed by itemized changes.

---

## [4.4.0] — 2026-03-25 — Enum Door Sensor Support

### Added

- **Dual door sensor type support** — `seal_door` and `transition_doors` inputs now
  accept both the classic `binary_sensor` (device_class: door, `on`/`off`) and the
  new HA `sensor` enum type (device_class: enum, states: `Open` / `Tilted` / `Closed`).

  Mapping used throughout the blueprint:
  | Sensor type | Closed | Open / Tilted |
  |---|---|---|
  | `binary_sensor` | `off` | `on` |
  | `sensor` (enum) | `Closed` | `Open` or `Tilted` |

  `Tilted` is treated as open everywhere — a tilted door is not sealed, so occupancy
  clearing is not blocked and the door-open exit path fires normally.

### Changed

- **Input selectors updated** — `seal_door` and `transition_doors` now use `filter:`
  with two entries (`binary_sensor / device_class: door` and `sensor / device_class: enum`)
  so both sensor types appear in the entity picker.

- **13 state-check locations updated** across the blueprint:
  - Top-level `variables:` — `sealed_now` and `any_transition_open`
  - Block 1 (latch sync action template)
  - Block 1c (exit mark `trigger.to_state.state` check)
  - Block 2 (force_occupied latch condition)
  - Block 3 (manual_occupied latch condition)
  - Block 4 (motion_on — entry gating seal check + latch condition)
  - Block 4b (mmwave_on — entry gating seal check + latch condition)
  - Block 5 (door-open exit timer start — `trigger.to_state.state` check)
  - Block 5b runtime recompute — `sealed_now_rt` and `any_transition_open_rt`

  Pattern used everywhere:
  ```jinja
  {# sealed (door closed) #}
  states(seal) in ['off', 'Closed']

  {# open (door open or tilted) #}
  states(d) in ['on', 'Open', 'Tilted']

  {# trigger fired on door opening #}
  trigger.to_state.state in ['on', 'Open', 'Tilted']
  ```

### No package template changes

- Door sensor type is an automation input concern only. Package helpers
  (`input_boolean`, `input_datetime`, `timer`, template sensors) are unaffected.

---

## [4.3.0] — 2026-03-24 — Activity Room Idle Support (`allow_idle_when_sealed`)

### Added

- **`allow_idle_when_sealed` input (boolean, default `false`)** — new input in the
  `Clearing & Timeouts` section. When `true`, the room is allowed to clear occupancy
  on motion timeout even if the seal door is currently closed. Designed for **activity
  rooms** (garage, laundry) where motion off reliably means the room is empty
  regardless of door state.

  Leave `false` (default) for **presence rooms** (bedroom, bathroom, closet, toilet)
  where a closed door signals a still occupant and PIR may miss them.

  Recommended per-room settings:
  | Room | `allow_idle_when_sealed` |
  |---|---|
  | Garage | `true` — passing through or working; motion off = gone |
  | Laundry | `true` — nobody stands still in laundry |
  | Half Bath | `false` — sealed = privacy, PIR may miss stillness |
  | Closet | `false` — sealed = someone may be browsing quietly |
  | Master Bath Toilet | `false` — small sealed space, stillness is normal |
  | Master Bedroom | `false` — sleeping = zero motion + sealed |

### Fixed

- **BUG: `motion_off_for` never cleared a sealed room with `exit_recent` active.**
  In `motion_off_for` (block 6), `exit_recent` was correctly satisfying the
  "door seen open" condition but a subsequent unconditional `not sealed_now` check
  was blocking the clear — even though the door had already closed behind the
  departing person. This caused rooms like the garage to stay occupied indefinitely
  after a normal exit until the failsafe fired (up to 2 hours). Fixed by replacing
  the bare `not sealed_now` guard with `(not sealed_now) or idle_when_sealed` across
  all four clearing paths.

### Changed

- **All four clearing paths updated** to respect `idle_when_sealed`:
  - `motion_off_for` (block 6) — `not sealed_now` → `(not sealed_now) or idle_when_sealed`
  - `exit_eval_done` (block 5b) — same, on `sealed_now_rt`
  - `mmwave_off_for` (block 6b) — same
  - Failsafe Condition A (block 8) — both the `exit_recent` substitute check and the
    unconditional seal guard updated

### No package template changes

- `allow_idle_when_sealed` is a blueprint input set in the automation UI, not a
  runtime helper. No new package helpers are required.

---

## [4.2.4] — 2026-03-09 — Seal Door Guard Hardening

### Fixed

- **FIX #11 — Seal door closed ALWAYS blocks clearing.** `exit_recent` no longer
  overrides the sealed door guard. Previously an active exit-recent window could allow
  clearing even when the seal door was closed, risking lights/fan turning off on a
  sleeping occupant. The sealed condition is now an unconditional guard across all
  three clearing paths: `exit_eval_done`, `fail_safe_done`, and the deadlock break.

---

## [4.2.3] — 2026-03-09 — force_occupied Multi-Helper Support

### Added

- **`force_occupied` now accepts multiple helpers** (list or single entity). `force_on`
  is `true` if ANY configured helper is ON. Runtime recomputation added at evaluation
  time so a still-active force helper blocks clearing even after the exit eval timer
  delay fires.

---

## [4.2.2] — 2026-03-09 — manual_occupied Multi-Helper Support

### Added

- **`manual_occupied` now accepts multiple helpers** (list or single entity). `manual_on`
  is `true` if ANY configured helper is ON. Runtime recomputation added at evaluation
  time so a still-active manual-occupied helper blocks clearing even after the exit eval
  timer delay fires.
- **`min_version` bumped to `2026.3.0`** to reflect selector features used.

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
