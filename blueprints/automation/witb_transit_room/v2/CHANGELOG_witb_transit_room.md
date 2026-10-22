# CHANGELOG — WITB Transit Room (v2)

## v2.0.0 — 2026-10-22 — WITB+ minus doors

Rewrite on the WITB+ 4.4.0 engine. v1 (hold-timer driver) stays in `../v1/` as the legacy version.

### Changed

- The blueprint is now WITB+ 4.4.0 with every door-dependent part removed, for transit rooms
  (stairs, hallways, open connectors) that have no door.
- Door-open, "exit recent" and "sealed" checks that gated clearing are gone: occupancy may always
  clear once motion has been off for `exit_timeout_seconds` (and mmWave, if configured, allows it).
- Failsafe no longer has a seal guard; it clears when motion is off, mmWave allows it and no manual
  helper is ON, otherwise it restarts. The 1.5x deadlock break is kept.
- Output is meant to feed `binary_sensor.<slug>_occupied_effective` (built by the room package from the
  occupancy, force and manual helpers) so WITB Actions V3 can consume it. v1 produced an `input_boolean`
  that Actions V3 does not accept.

### Kept from WITB+ 4.4.0

- Motion assert; motion-off-for clear; mmWave assert / block clear / off-for clear.
- `occupancy_helper`, `last_motion_helper`.
- `automation_override`, `force_occupied` and `manual_occupied` (multiple entities each); force/manual
  turning OFF does not clear immediately.
- Failsafe timer, minutes, timeout helper and deadlock break.

### Fixed (before first release)

- `failsafe_minutes` was declared but never read (inherited from WITB+ 4.4.0). It is now the fallback for
  `failsafe_timeout_helper`: the helper wins only when it is set and has a numeric value.

### Removed (vs WITB+ 4.4.0)

- Inputs: `seal_door`, `transition_doors`, `last_door_helper`, `exit_eval_timer`,
  `last_exit_door_helper`, `exit_recent_window_seconds`, `exit_mark_requires_recent_motion`,
  `exit_mark_motion_window_seconds`, `latched_helper`, `allow_idle_when_sealed`,
  `require_door_for_entry`, `entry_window_seconds`, `entry_window_helper`.
- Logic: door-change branches, exit evaluation timer branch, latch sync, entry gating.

### Not carried over from v1

Keepalive, instant-off/suppress, day/night hold, minimum-on, maintenance override and HA-start recovery.

### Migration from v1

Not drop-in: inputs and helpers differ. Create the v2 helpers, create a new automation from the v2
blueprint, point WITB Actions V3 at `binary_sensor.<slug>_occupied_effective`, then retire the v1 automation.
