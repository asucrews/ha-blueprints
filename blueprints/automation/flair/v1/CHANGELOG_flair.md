# CHANGELOG — flair

All notable changes to `flair.yaml` are documented here.
Versioning follows [Semantic Versioning](https://semver.org/).

---

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
