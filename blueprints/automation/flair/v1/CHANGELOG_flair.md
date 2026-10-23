# CHANGELOG — flair

All notable changes to `flair.yaml` are documented here.
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [1.1.0] — Vacancy delay

### Added
- `inactive_delay_minutes` optional input (whole minutes, 0–60, default 0).
  How long `occupied_effective` must stay off before Flair is set Inactive.
  Applied as `for:` on the `Room Unoccupied` trigger, so returning inside the
  delay cancels it and the room stays Active, with no timer helper. Default 0
  keeps the 1.0.5 behavior (immediate). The selector step does not enforce
  whole minutes (HA accepts 0.1); the consistency sweep below makes a
  fractional delay harmless.

### Changed
- Reconciliation respects `inactive_delay_minutes`: Active while the room is vacant is
  correct until `occupied_effective` has been off for `inactive_delay_minutes`. Both
  the pre-delay entry check and the post-delay check only correct to Inactive
  once the room has been off for at least that long. The occupied → Active
  side is unchanged. `unknown`/`unavailable` is not treated as vacant.
- Startup sync ignores `inactive_delay_minutes` (vacant = Inactive after the 30 s
  wait). `last_changed` resets on HA restart and a pending `for:` trigger is
  lost, so the vacancy age cannot be known after a restart.

- Room Unoccupied trigger now starts from `on`, `unavailable` or `unknown`
  (`to: "off"` plus `for:`). An availability blip during the delay would
  otherwise cancel the `for:` timer and, since `unavailable → off` did not
  match, never restart it, leaving the room Active indefinitely.
- Consistency Sweep: a `time_pattern` trigger every minute. A top-level
  condition lets it start a run only when the room is out of step: both
  `occupied_effective` and the Flair status are known and either the room is
  occupied and not Active, or it has been vacant for at least
  `inactive_delay_minutes` and is not Inactive, and the Flair status has been
  unchanged for at least `reconciliation_delay` (so the sweep never cuts a
  reconciliation wait short or reacts to a brief cloud flicker). Inside the
  delay either status is accepted. When nothing is wrong no run starts (the trace list shows
  "condition not met" runs), so the sweep cannot cancel startup sync or a
  pending reconciliation. It corrects a lost vacancy timer, a startup sync
  cancelled by a real event, or Flair restoring from unavailable, at the next
  sweep once both entities are known, the Flair status state has stayed
  unchanged for at least `reconciliation_delay` and, for a vacant room only,
  the vacancy delay has elapsed. Continuous Flair flapping can postpone
  correction; recovery resumes once the status stays unchanged for
  `reconciliation_delay`. At delay 0 the
  blueprint is 1.0.5 plus the sweep, which corrects mismatches 1.0.5 would
  have left in place, and some it would have corrected later (for example
  inside the 30 s startup wait). Failed-condition sweep runs appear in traces
  every minute; see the README Traces note.
- Top-level `conditions:` drops a Room Unoccupied trigger whose previous state
  was `unavailable`/`unknown` when `inactive_delay_minutes` is 0. Without it,
  `unavailable → off` at HA start would restart (and cancel) the 30 s startup
  sync via `mode: restart`. With the guard, delay 0 behaves exactly like 1.0.5.
- Reconciliation vacancy checks skip the `for:` age test when `inactive_delay_minutes`
  is 0, because HA's `for:` uses a strict greater-than and a zero `for:` is not
  identical to no `for:`. Keeps 1.0.5 behavior at the default.

### Fixed
- `platform:` inside `triggers:` changed to `trigger:` (the 1.0.5 entry said
  this was done; it was not).

---

## Unreleased

- source_url fixed (metadata only; no behaviour or version change).

## [1.0.5] — Unreleased

### Changed
- `trigger:` / `action:` singular keys updated to `triggers:` / `actions:`
  plural syntax. Required for `min_version: 2026.3.0` to avoid deprecation
  warnings in HA 2026.x. (Issue #2)
- Blueprint `description` field updated to reference `CHANGELOG_flair.md`
  instead of `CHANGELOG.md` to match NAMING.md conventions. (Issue #3)

---

## [1.0.4] — Reconciliation hardening

### Added
- `homeassistant: start` trigger with 30-second blocking startup sync. On HA
  restart, waits for WITB+ and the Flair integration to restore before
  reconciling vent state against current `occupied_effective`. Recovers from
  drift that occurred while HA was offline.

### Fixed
- **Self-triggering reconciliation loop**: added pre-delay mismatch check as
  an entry condition on the `Flair Status Changed` branch. If
  `flair_activity_status` already matches `occupied_effective` at branch entry
  (e.g. this automation's own service call just set it correctly), the branch
  exits immediately without entering the delay. Eliminates unnecessary restart
  cycles on every occupancy change.
- **Unknown/unavailable suppression**: added `not_from` and `not_to` filters
  (`unknown`, `unavailable`) to the `Flair Status Changed` trigger. Prevents
  spurious reconciliation runs during HA restart state restoration.

---

## [1.0.3] — Reconciliation

### Added
- `flair_activity_status` state change trigger (`Flair Status Changed`). Fires
  on any transition between known states, excluding `unknown`/`unavailable`.
- Reconciliation sequence: waits `reconciliation_delay` seconds, then checks
  `occupied_effective` against current `flair_activity_status` and corrects if
  mismatched. Handles both directions (occupied + not-Active, unoccupied +
  not-Inactive).
- `reconciliation_delay` configurable input (default: 5 s, range: 0–60 s) with
  per-room override support.

---

## [1.0.2] — WITB+ integration and simplification

### Changed
- `room_occupancy_sensor` input replaced by purpose-named `occupied_effective`
  input restricted to `binary_sensor` domain only. Reflects that this blueprint
  is exclusively a WITB+ downstream consumer.
- Input descriptions updated to explicitly reference
  `binary_sensor.room_slug_occupied_effective` and warn against wiring raw
  sensors or the `input_boolean` helper directly.
- Input grouping (`required_entities` / `optional_entities`) retained and
  updated with `icon` fields to match WITB+ blueprint conventions.

### Removed
- `door_sensor_open_delay` and `door_sensor_close_delay` inputs. All debounce
  and exit evaluation is handled upstream by the WITB+ occupancy blueprint.
  Double-debouncing here was redundant.
- `hvac_smart_sensor_occupancy` input and all associated triggers, conditions,
  and branches. The Ecobee TempSure sensors feeding occupancy feed into WITB+
  upstream; this blueprint reacts only to `occupied_effective`. HVAC sensor
  logic was not needed.
- `variables` block. No variables required after removing HVAC sensor logic.

---

## [1.0.1] — Bug fixes and mode correction

### Fixed
- **`Room Unoccupied` branch set `Active` instead of `Inactive`** — critical
  logic inversion. Vent was never set to Inactive on vacancy.
- **`hvac_smart_sensor_occupancy` default `binary_sensor.none`** changed to
  `[]`. The fake entity string caused load-time trigger evaluation errors for
  users who did not configure this input. HA 2024.4+ silently skips triggers
  against an empty list.
- Added `hvac_smart_sensor_enabled` variable (`length > 0` check) and guard
  conditions on both HVAC branches to prevent misfires when the input is
  unconfigured.

### Changed
- `mode: single` → `mode: restart`. For a 2-step near-instantaneous sequence
  where latest state must always win, `restart` is correct. Dropped events
  under `single` meant the last occupancy state could be silently ignored.
- Removed `max_exceeded: silent` — not applicable to `restart` mode.
- Blueprint `description` field populated (was empty whitespace/`<br/>` tags).
- Input descriptions cleaned up — removed door-sensor-specific framing from
  delay inputs that also accept occupancy helpers.

---

## [1.0.0] — Initial release

- Room occupancy → Flair activity status (Active/Inactive) + clear hold.
- Optional HVAC smart sensor occupancy input gated on room occupancy state.
- Optional open/close delay inputs for door sensor debounce.
- `mode: single`, `max_exceeded: silent`.
