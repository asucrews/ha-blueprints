# Use Cases — air_purifier

Supported scenarios with expected pass/fail outcomes for each branch and
edge condition.

---

## UC-01 — Boost window starts on time

**Setup:** Automation is running. Current time advances to `first_start_time`.
One purifier is in `auto` preset mode.

**Expected:**
- `time` trigger fires immediately.
- `should_boost` evaluates `true`.
- `fan.set_percentage` is called with `boost_percentage`.
- Purifier moves to full speed.

---

## UC-02 — Boost window ends on time

**Setup:** Current time advances to `first_end_time`. One purifier is at
`boost_percentage`.

**Expected:**
- `time` trigger fires immediately.
- `should_boost` evaluates `false`.
- `fan.set_preset_mode` is called with `return_preset_mode`.
- Purifier returns to `auto` (or configured preset).

---

## UC-03 — Reconciler heals a drifted device mid-window

**Setup:** Inside a boost window. One purifier was manually set to 50% by the
user 3 minutes ago.

**Expected:**
- Next `time_pattern` tick (≤5 min) fires.
- `should_boost` evaluates `true`.
- Guard detects `percentage != boost_percentage`.
- `fan.set_percentage` is called; purifier returns to `boost_percentage`.

---

## UC-04 — Reconciler heals a drifted device outside window

**Setup:** Outside a boost window. One purifier was manually set to 100% by
the user.

**Expected:**
- Next `time_pattern` tick fires.
- `should_boost` evaluates `false`.
- Guard detects `preset_mode != return_preset_mode`.
- `fan.set_preset_mode` is called; purifier returns to configured preset.

---

## UC-05 — No-op guard — device already at target state

**Setup:** Inside a boost window. Purifier `percentage` already equals
`boost_percentage`.

**Expected:**
- `should_boost` evaluates `true`.
- Guard condition `percentage != boost_percentage` is `false`.
- `fan.set_percentage` is **not** called.
- No log entry, no Zigbee/Z-Wave traffic.

---

## UC-06 — HA restarts mid-window

**Setup:** HA restarts while current time is inside a boost window. Purifiers
may be in any state post-restart.

**Expected:**
- `homeassistant: start` trigger fires.
- `should_boost` evaluates `true`.
- Any purifier not already at `boost_percentage` is corrected immediately.
- No wait for the next 5-minute tick.

---

## UC-07 — HA restarts outside window

**Setup:** HA restarts while current time is outside both windows.

**Expected:**
- `homeassistant: start` trigger fires.
- `should_boost` evaluates `false`.
- Any purifier not already in `return_preset_mode` is corrected immediately.

---

## UC-08 — Purifier offline or unavailable during reconcile

**Setup:** One purifier is unavailable (e.g. power-cycled) when a reconcile
fires.

**Expected — boost branch (v1.1.0+):**
- `states(repeat.item)` returns `'unavailable'`, not `'on'`.
- `is_on` guard fails; sequence exits immediately.
- `fan.set_percentage` is **not** called — entity is silently skipped.
- No HA error logged for this entity.
- Other purifiers in the list continue to be processed normally.

**Expected — non-boost branch (v1.1.0+):**
- No `is_on` guard in the `default` branch.
- `state_attr(repeat.item, 'preset_mode')` returns `None` for an unavailable entity.
- Guard condition `None != return_mode` is `true`.
- `fan.set_preset_mode` is attempted; HA will log an error for the unavailable entity.
- Other purifiers in the list continue to be processed normally.

> **Note:** A future improvement could add an `is_available` guard to the
> non-boost branch to silently skip unavailable entities there as well.

---

## UC-09 — Purifier manually turned off during boost window (v1.1.0+)

**Setup:** Inside a boost window. User manually turns off one purifier.

**Expected (v1.1.0+):**
- `is_on` guard detects entity state is `off`.
- `fan.set_percentage` is **not** called.
- Purifier remains off until the user turns it on again.

**Expected (v1.0.0 — known bug):**
- Guard is absent; `fan.set_percentage` is called.
- Purifier is unintentionally powered on by the reconciler.

---

## UC-10 — Second boost window (same behavior as UC-01 through UC-05)

All scenarios above apply identically to `second_start_time` / `second_end_time`.
Both windows are evaluated in a single `OR` expression; behavior is symmetric.

---

## UC-11 — Midnight-spanning window (unsupported)

**Setup:** `second_start_time` = `23:00:00`, `second_end_time` = `01:00:00`.

**Expected:** ❌ Incorrect behavior. The string comparison
`t_now >= second_start AND t_now < second_end` evaluates `false` for times
between 23:00 and 23:59 because `"23:xx" < "01:00"` is false.

> Midnight-spanning windows are not supported. Both start and end times must
> fall on the same calendar day. See `rules_air_purifier.md` rule 7.
