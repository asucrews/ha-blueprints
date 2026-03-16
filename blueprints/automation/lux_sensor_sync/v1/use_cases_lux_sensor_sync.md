# Use Cases — lux_sensor_sync

Supported scenarios with expected pass/fail outcomes for each branch and
edge condition.

---

## UC-01 — Light turned on, boolean inferred ON

**Setup:** Light is off (`light_boolean` = `off`). Someone turns on the fan
light. Delta rises above `on_threshold` and holds for `on_for_seconds`.
Sensor prior state was a valid numeric value.

**Expected:**
- `light_on` trigger fires.
- `light_boolean` is `off` — guard passes.
- Sensor restore suppression: `trigger.from_state.state` is a number → passes.
- `input_boolean.turn_on` called.
- `light_boolean` set to `on`.

---

## UC-02 — Light turned off, boolean inferred OFF

**Setup:** Light is on (`light_boolean` = `on`). Someone turns off the fan
light. Delta falls below `off_threshold` and holds for `off_for_seconds`.

**Expected:**
- `light_off` trigger fires.
- `light_boolean` is `on` — guard passes.
- `input_boolean.turn_off` called.
- `light_boolean` set to `off`.

---

## UC-03 — No-op guard — boolean already matches inferred state

**Setup (ON):** `light_boolean` is already `on`. Delta rises above
`on_threshold` again (e.g. lux sensor briefly dipped and recovered).

**Expected:**
- `light_on` trigger fires.
- `light_boolean` is `on` — guard fails. Branch exits.
- No service call. No state change.

**Setup (OFF):** `light_boolean` is already `off`. Delta falls below
`off_threshold` again.

**Expected:**
- `light_off` trigger fires.
- `light_boolean` is `off` — guard fails. Branch exits.
- No service call. No state change.

---

## UC-04 — HA restarts, light was on while offline

**Setup:** HA restarts. After settling: `delta_sensor` above `on_threshold`,
`light_boolean` = `off` (drifted during offline period).

**Expected:**
- HA Start trigger fires; automation waits 30 seconds.
- Infer-ON `if` conditions: delta above threshold AND boolean is `off` → pass.
- `input_boolean.turn_on` called.
- `light_boolean` corrected to `on`.

---

## UC-05 — HA restarts, light was off while offline

**Setup:** HA restarts. After settling: `delta_sensor` below `off_threshold`,
`light_boolean` = `on` (drifted during offline period).

**Expected:**
- HA Start trigger fires; automation waits 30 seconds.
- Infer-ON `if` conditions: delta not above threshold → fails.
- `else` infer-OFF: delta below threshold AND boolean is `on` → pass.
- `input_boolean.turn_off` called.
- `light_boolean` corrected to `off`.

---

## UC-06 — HA restarts, boolean already correct

**Setup:** HA restarts. After settling: delta and `light_boolean` already
match (both indicate light is on, or both indicate off).

**Expected:**
- HA Start trigger fires; automation waits 30 seconds.
- Infer-ON: delta above threshold but boolean already `on` → fails.
- `else` infer-OFF: delta not below threshold → fails.
- No service call. Boolean stays correct.

---

## UC-07 — Sensor restores above threshold after HA restart — boolean stays off
           (`suppress_infer_on_after_sensor_restore: true`)

**Setup:** HA restarts. Delta sensor was above `on_threshold` before restart.
After restart, sensor restores from `unknown` → 45 lx and holds above threshold
for `on_for_seconds`. `suppress_infer_on_after_sensor_restore: true` (default).

**Expected:**
- `light_on` trigger fires after `on_for_seconds`.
- `trigger.from_state.state` = `'unknown'`.
- Suppress condition: from_state in `['unknown', 'unavailable']` → fails.
- Branch exits. `light_boolean` stays `off`.
- Meanwhile, `ha_start` branch fires, waits 30 s, then correctly evaluates
  and sets `light_boolean` to `on` via startup sync.

---

## UC-08 — Normal mid-session lux rise — boolean infers ON correctly
           (`suppress_infer_on_after_sensor_restore: true`)

**Setup:** HA has been running for hours. Light is switched on. Delta
transitions from 3 lx → 45 lx and holds above `on_threshold` for
`on_for_seconds`.

**Expected:**
- `light_on` trigger fires.
- `trigger.from_state.state` = `'3'` (valid numeric prior state).
- Suppress condition: from_state not in `['unknown', 'unavailable']` → passes.
- `light_boolean` is `off` → guard passes.
- `input_boolean.turn_on` called. Boolean infers ON correctly.

---

## UC-09 — Sensor WiFi blip restores above threshold
           (`suppress_infer_on_after_sensor_restore: true`)

**Setup:** Delta sensor drops to `unavailable` mid-session (WiFi blip),
then restores to 45 lx above `on_threshold`. Holds for `on_for_seconds`.

**Expected:**
- `light_on` trigger fires.
- `trigger.from_state.state` = `'unavailable'`.
- Suppress condition: from_state in `['unknown', 'unavailable']` → fails.
- Branch exits. No false positive inference.
- Next sensor state change produces a valid numeric `from_state`, and if
  delta remains above threshold after `on_for_seconds`, the trigger fires
  again and infer-ON proceeds normally.

---

## UC-10 — Sensor restore suppression disabled
           (`suppress_infer_on_after_sensor_restore: false`)

**Setup:** HA restarts. Delta sensor restores from `unknown` → 45 lx and
holds above `on_threshold` for `on_for_seconds`.
`suppress_infer_on_after_sensor_restore: false`.

**Expected:**
- `light_on` trigger fires.
- Suppress condition: disabled → passes.
- `light_boolean` is `off` → guard passes.
- `input_boolean.turn_on` called immediately.
- Boolean infers ON without waiting for `ha_start` branch.

---

## UC-11 — Lux trigger fires during startup delay (`mode: restart`)

**Setup:** HA restarts. During the 30-second startup delay, the light is
switched on and `light_on` trigger fires.

**Expected:**
- `mode: restart` cancels the startup sync run.
- New run enters `light_on` branch.
- Restore suppression: `trigger.from_state.state` reflects pre-restart state
  (`unknown`) → suppressed if `suppress_infer_on_after_sensor_restore: true`.
- If suppressed: boolean stays `off` until next sensor update.
- If not suppressed: `input_boolean.turn_on` called immediately.

---

## UC-12 — Inverted thresholds (misconfiguration)

**Setup:** `on_threshold` = 15 lx, `off_threshold` = 40 lx (inverted — OFF
threshold is higher than ON threshold).

**Expected:** ❌ Undefined behavior. When delta is between 15 and 40 lx, both
`light_on` and `light_off` triggers are simultaneously satisfiable. The
boolean will oscillate rapidly. The blueprint does not validate threshold
ordering at configuration time.

> Keep `on_threshold` meaningfully higher than `off_threshold`
> (at least 10–20 lx gap recommended). See `rules_lux_sensor_sync.md` rule 16.

---

## UC-13 — Brief delta spike — debounce prevents false inference

**Setup:** A brief reflection or sensor glitch causes delta to spike above
`on_threshold` for less than `on_for_seconds`, then drop back below.

**Expected:**
- `light_on` trigger requires delta to hold above threshold for `on_for_seconds`.
- Spike does not satisfy `for:` duration.
- Trigger never fires. `light_boolean` stays `off`.
