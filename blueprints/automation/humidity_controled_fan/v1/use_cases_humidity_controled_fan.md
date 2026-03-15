# Use Cases — humidity_controled_fan

Supported scenarios with expected pass/fail outcomes for each branch and
edge condition.

---

## UC-01 — Shower detected, fan turns on

**Setup:** Night mode disabled. Delta rises above `on_threshold` and holds
for `on_for_seconds`. Fan is currently `off`.

**Expected:**
- `turn_on` trigger fires.
- Fan is `off` — guard passes.
- Not in night window — guard passes.
- `homeassistant.turn_on` called on `fan_entity`.
- Fan turns on.

---

## UC-02 — Room dries out, fan turns off

**Setup:** Fan is `on`. Delta falls below `off_threshold` and holds for
`off_for_seconds`. Fan has been on for longer than `min_run_seconds`.

**Expected:**
- `turn_off` trigger fires.
- Fan is `on` for >= `min_run_seconds` — guard passes.
- `homeassistant.turn_off` called on `fan_entity`.
- Fan turns off.

---

## UC-03 — Fan turns off too soon — minimum runtime blocks it

**Setup:** Fan is `on`. Delta drops quickly and holds below `off_threshold`
for `off_for_seconds`, but fan has only been on for less than `min_run_seconds`.

**Expected:**
- `turn_off` trigger fires.
- `condition: state … for: seconds: min_run_seconds` fails — fan has not
  been on long enough.
- Branch exits. Fan stays on.
- Fan turns off only once `min_run_seconds` is satisfied.

---

## UC-04 — Failsafe fires after max runtime

**Setup:** Fan has been on for `max_run_seconds`. Delta is still above
`off_threshold` (e.g. sensor stuck or very long shower).

**Expected:**
- `failsafe` trigger fires.
- No conditions — `homeassistant.turn_off` called unconditionally.
- Fan turns off.

---

## UC-05 — Night mode suppresses turn-on during quiet window

**Setup:** Night mode enabled. Current time is inside the quiet window.
Delta rises above `on_threshold` and holds for `on_for_seconds`.

**Expected:**
- `turn_on` trigger fires.
- `_in_night_window` evaluates `true`.
- Night window guard fails — branch exits.
- Fan stays off. No service call made.

---

## UC-06 — Night mode does not suppress turn-off

**Setup:** Night mode enabled. Current time is inside the quiet window.
Fan is on (started before the quiet window). Delta falls below `off_threshold`
for `off_for_seconds`. `min_run_seconds` satisfied.

**Expected:**
- `turn_off` trigger fires.
- Night mode does not gate the turn-off branch.
- `homeassistant.turn_off` called.
- Fan turns off normally.

---

## UC-07 — Night mode with overnight span — turn-on suppressed past midnight

**Setup:** `night_start = 22:00`, `night_end = 07:00`. Current time is 02:30.
Delta rises above threshold.

**Expected:**
- `_in_night_window`: `night_start (22:00) > night_end (07:00)` → overnight span.
- `t (02:30) >= 22:00` is false; `t (02:30) < 07:00` is true → window active.
- Turn-on suppressed.

---

## UC-08 — Night mode with overnight span — turn-on allowed after window ends

**Setup:** `night_start = 22:00`, `night_end = 07:00`. Current time is 09:00.
Delta rises above threshold.

**Expected:**
- `_in_night_window`: `t (09:00) >= 22:00` is false; `t (09:00) < 07:00` is false → window inactive.
- Turn-on proceeds normally.

---

## UC-09 — HA restart, fan on but humidity normal (`ha_start_allow_turn_on: false`)

**Setup:** HA restarts. After settling: `fan_entity` = `on`, `delta_sensor`
below `off_threshold`. `ha_start_allow_turn_on: false`.

**Expected:**
- HA Start trigger fires; automation waits 30 seconds.
- Turn-ON `if` condition: `ha_start_allow_turn_on` is false → evaluates `false`.
- `else` block runs: delta below threshold AND fan is on → turn-off conditions
  pass.
- `homeassistant.turn_off` called.
- Fan turns off. Drift corrected.

---

## UC-10 — HA restart, fan off but humidity elevated (`ha_start_allow_turn_on: true`)

**Setup:** HA restarts. After settling: `fan_entity` = `off`, `delta_sensor`
above `on_threshold`. `ha_start_allow_turn_on: true`. Night mode disabled.

**Expected:**
- HA Start trigger fires; automation waits 30 seconds.
- Turn-ON `if` condition: `ha_start_allow_turn_on` true + not in night window →
  evaluates `true`.
- `then` conditions: delta above threshold AND fan off → pass.
- `homeassistant.turn_on` called.
- Fan turns on. Drift corrected.

---

## UC-11 — HA restart, fan on and humidity elevated — no correction needed (`ha_start_allow_turn_on: false`)

**Setup:** HA restarts. After settling: `fan_entity` = `on`, `delta_sensor`
above `on_threshold`. `ha_start_allow_turn_on: false`.

**Expected:**
- Turn-ON `if` condition: false (allow_turn_on disabled) → `else` runs.
- `else` turn-off: delta is NOT below `off_threshold` → condition fails.
- No service call. Fan stays on correctly.

---

## UC-12 — HA restart, fan on and humidity elevated (`ha_start_allow_turn_on: true`)

**Setup:** HA restarts. After settling: `fan_entity` = `on`, `delta_sensor`
above `on_threshold`. `ha_start_allow_turn_on: true`. Night mode disabled.

**Expected:**
- Turn-ON `if` condition: true → `then` runs.
- `then` conditions: delta above threshold — passes; fan `off` — **fails**
  (fan is already `on`).
- `then` sequence does not execute. No service call made.
- `else` turn-off block runs: delta not below off_threshold → no action.
- Fan stays on correctly.

---

## UC-13 — HA restart settles inside night window (`ha_start_allow_turn_on: true`)

**Setup:** HA restarts at 21:59. Night window starts at 22:00. After the
30-second settling delay the actual time is 22:00+. Delta is above threshold,
fan is off.

**Expected:**
- Turn-ON `if` condition: `ha_start_allow_turn_on` true; night window
  re-evaluated after delay → now inside window → `if` evaluates `false`.
- `else` turn-off block runs: fan is off → condition fails. No service call.
- Turn-on correctly suppressed despite `ha_start_allow_turn_on: true`.

---

## UC-14 — Delta spike — does not trigger fan (on_for_seconds debounce)

**Setup:** Delta briefly exceeds `on_threshold` for less than `on_for_seconds`
(e.g. steam from a kettle), then drops back below.

**Expected:**
- `turn_on` trigger requires delta to remain above threshold for `on_for_seconds`.
- Brief spike does not satisfy the `for:` duration.
- Trigger never fires. Fan stays off.

---

## UC-15 — New trigger fires during reconciliation run (`mode: restart`)

**Setup:** `ha_start` trigger fires and the automation is waiting through the
30-second settling delay. Before the delay completes, `turn_on` trigger fires
(delta rose during startup).

**Expected:**
- `mode: restart` cancels the startup sync run.
- New run enters `turn_on` branch immediately.
- Night window check and fan state check evaluated.
- If conditions pass, fan turns on. Latest state wins.

---

## UC-16 — Fan stays off after HA restart when sensor restores above threshold (`suppress_turn_on_after_sensor_restore: true`)

**Setup:** HA restarts. Delta sensor was above `on_threshold` before restart.
After restart, sensor restores from `unknown` → 9.5% (above threshold) and
holds there for `on_for_seconds`. `suppress_turn_on_after_sensor_restore: true`
(default). `ha_start_allow_turn_on: false` (default).

**Expected:**
- `ha_start` branch runs: 30s delay, `ha_start_allow_turn_on=false` → turn-ON
  blocked; delta not below off_threshold → turn-OFF not needed. No action.
- After `on_for_seconds`, `turn_on` trigger fires.
- `trigger.from_state.state` = `'unknown'` (sensor came from unknown on restore).
- Suppress condition: `_suppress_restore=true` AND from_state is `'unknown'`
  → condition fails → branch exits.
- Fan stays off. Unexpected post-restart turn-on suppressed.

---

## UC-17 — Fan turns on normally mid-day (`suppress_turn_on_after_sensor_restore: true`)

**Setup:** Mid-day, HA has been running for hours. Shower causes delta to rise
above `on_threshold`. Sensor transitions from 2.5% → 9.5%, holds for
`on_for_seconds`.

**Expected:**
- `turn_on` trigger fires.
- `trigger.from_state.state` = `'2.5'` (valid previous reading, not unknown).
- Suppress condition: from_state not in `['unknown', 'unavailable']` → passes.
- Other conditions (fan off, not in night window) pass.
- `homeassistant.turn_on` called. Fan turns on normally.

---

## UC-18 — Sensor reconnects mid-shower (`suppress_turn_on_after_sensor_restore: true`)

**Setup:** During a shower, the delta sensor drops to `unavailable` (WiFi
blip) then restores to 9.5% (above threshold). Sensor holds above threshold
for `on_for_seconds`.

**Expected:**
- `turn_on` trigger fires.
- `trigger.from_state.state` = `'unavailable'`.
- Suppress condition: `_suppress_restore=true` AND from_state is `'unavailable'`
  → condition fails → branch exits.
- Fan does NOT turn on immediately.
- If humidity continues to change (sensor updates to 9.6%, etc.), a new
  `for:` countdown starts. Next trigger fire will have a valid numeric
  `from_state` and turn-on will proceed normally.

> **Note:** With `suppress_turn_on_after_sensor_restore: false`, turn-on
> proceeds immediately after the sensor reconnects and the `for:` duration
> elapses regardless of prior state.
