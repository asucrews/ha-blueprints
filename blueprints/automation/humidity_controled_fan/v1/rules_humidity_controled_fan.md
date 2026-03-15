# Rules — humidity_controled_fan

Behavioral rules governing `humidity_controled_fan.yaml`. These are the
invariants the blueprint enforces regardless of which trigger fires.

---

## Trigger rules

1. **Turn ON trigger** — fires when `delta_sensor` rises above `on_threshold`
   and stays there for `on_for_seconds`. Uses `numeric_state: above` + `for:`.
2. **Turn OFF trigger** — fires when `delta_sensor` falls below `off_threshold`
   and stays there for `off_for_seconds`. Uses `numeric_state: below` + `for:`.
3. **Failsafe trigger** — fires when `fan_entity` has been in state `on` for
   `max_run_seconds`. Forces a turn-off regardless of humidity level.
4. **HA Start trigger** — fires once on `homeassistant: start`. Initiates
   startup state correction after a settling delay.

---

## Turn ON rules

5. **Turn ON** fires only when all conditions are met:
   - Trigger ID is `turn_on`
   - `fan_entity` is currently `off`
   - Not currently inside the night quiet window (or night mode is disabled)
   - Sensor restore suppression passes (see rule 8)
6. If the fan is already `on` when the turn-on trigger fires, the branch
   exits silently — no service call is made.
7. If inside the night quiet window, the turn-on is suppressed entirely.
   The trigger is consumed and no fan action occurs.
8. **Sensor restore suppression** (`suppress_turn_on_after_sensor_restore`,
   default `true`) — if enabled, turn-on is suppressed when
   `trigger.from_state.state` is `unknown` or `unavailable`. This detects the
   scenario where the sensor just restored from HA restart or a sensor
   reconnect. When suppressed the trigger is consumed with no fan action.
   Disable if you want turn-on to proceed immediately after any sensor
   reconnect.

---

## Turn OFF rules

8. **Turn OFF** fires only when all conditions are met:
   - Trigger ID is `turn_off`
   - `fan_entity` has been in state `on` for at least `min_run_seconds`
9. **Minimum runtime guard** — the fan cannot be turned off before it has
   been on for `min_run_seconds` (default: 300 s). If the delta drops
   quickly, the turn-off branch blocks until `min_run_seconds` is satisfied.
10. Night mode does **not** suppress turn-off — if a shower ran right before
    the quiet window started, the fan must be allowed to finish clearing the
    room rather than get stuck on until morning.

---

## Failsafe rules

11. **Failsafe** turns the fan off unconditionally after `max_run_seconds`
    (default: 5400 s / 90 min) of continuous operation.
12. The failsafe fires even if `delta_sensor` is unavailable or stuck above
    `off_threshold`. It is the only path that can override a stuck sensor.
13. No conditions gate the failsafe — trigger ID `failsafe` is sufficient.

---

## Night mode rules

14. Night mode is disabled by default (`night_mode_enabled: false`).
    When disabled, all turn-on actions proceed normally at any hour.
15. When enabled, the quiet window is defined by `night_start` and `night_end`.
16. **Overnight span support** — if `night_start > night_end` (e.g. 22:00 →
    07:00), the window wraps midnight: active when `t >= night_start OR
    t < night_end`. If `night_start <= night_end`, the window is same-day:
    active when `night_start <= t < night_end`.
17. The night window check (`_in_night_window`) is computed as an **action-step
    variable** on every run so `now()` is always the real current time, not
    the time the automation was last loaded.

---

## HA startup rules

18. On HA restart, the automation waits **30 seconds** (hardcoded) for sensors
    and integrations to finish restoring before reading any state.
19. **Turn-OFF correction** — after the settling delay, if `delta_sensor` is
    below `off_threshold` AND `fan_entity` is `on`, the fan is turned off.
    This path is always active regardless of `ha_start_allow_turn_on`.
20. **Turn-ON correction** — after the settling delay, if `delta_sensor` is
    above `on_threshold` AND `fan_entity` is `off`, the fan is turned on.
    This path is only active when `ha_start_allow_turn_on: true`.
21. Night mode is respected during startup turn-ON correction — if the restart
    settles inside the quiet window, turn-on is suppressed even when
    `ha_start_allow_turn_on` is enabled. Turn-OFF correction is not blocked
    by night mode.
22. The night window for startup is **re-evaluated after the 30-second delay**,
    not at trigger time. A restart at 21:59 that takes 30 seconds to settle
    will correctly be inside the 22:00 night window.

---

## Execution mode rules

23. **`mode: restart`** — if a new trigger fires while any sequence is in
    progress, the current run is canceled and a new run starts immediately
    with the latest trigger context. Latest sensor state always wins.
