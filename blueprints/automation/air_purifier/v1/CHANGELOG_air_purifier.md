# CHANGELOG — air_purifier

All notable changes to `air_purifier.yaml` are documented here.
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [1.1.0] — Unreleased

### Fixed
- Added `is_on` guard before `fan.set_percentage` during boost windows. Previously, a purifier that was manually turned off would be inadvertently powered on when the next reconcile fired inside a boost window. Now the service call is skipped entirely if the entity state is not `on`. (Issue #2)

### Changed
- Bumped `min_version` from `2025.6.0` to `2026.1.0` to reflect current deployment baseline. (Issue #1)

### Changed (low priority)
- Replaced `mode: single` with `mode: queued` + `max: 2` so boundary-time triggers are never silently dropped if a prior reconcile run is still in progress. (Issue #6)

### Removed
- Removed redundant `| int` cast on `boost_pct` in the percentage guard condition. `boost_pct` is already numeric from the `number` selector. (Issue #4)

---

## [1.0.0] — Initial release

- Two configurable daily boost windows (`first_start/end`, `second_start/end`).
- Self-correction every 5 minutes via `time_pattern` trigger.
- HA restart guard via `homeassistant: start` trigger.
- Instant boundary transitions via `time` trigger on all four window edges.
- Guard conditions prevent no-op service calls (skips if device is already at target state).
- Two-step `variables:` pattern: top-level for `!input` aliasing, action-level for Jinja2 computation.
- `strftime('%H:%M:%S')` string comparison for timezone-safe window evaluation.
- `| int(-1)` sentinel on `state_attr(..., 'percentage')` handles off/unavailable entities safely.
