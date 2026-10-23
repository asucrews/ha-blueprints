# Use Cases — flair

Supported scenarios with expected pass/fail outcomes for each branch and
edge condition.

---

## UC-01 — Room becomes occupied

**Setup:** `occupied_effective` transitions from `off` → `on`.
`flair_activity_status` is currently `Inactive`.

**Expected:**
- Room Occupied trigger fires.
- `select.select_option` called with `Active` on `flair_activity_status`.
- `button.press` called on `flair_clear_hold`.
- Vent is now Active with hold cleared.

---

## UC-02 — Room becomes unoccupied

**Setup:** `occupied_effective` transitions from `on` → `off` and stays off for
`inactive_delay_minutes` (default 0, immediate). `flair_activity_status` is currently
`Active`.

**Expected:**
- Room Unoccupied trigger fires once the delay has elapsed.
- `select.select_option` called with `Inactive` on `flair_activity_status`.
- `button.press` called on `flair_clear_hold`.
- Vent is now Inactive with hold cleared.

---

## UC-03 — Flair status drifts to wrong state — reconciler corrects it

**Setup:** Room is occupied (`occupied_effective` = `on`). Flair cloud resets
`flair_activity_status` to `Inactive` unexpectedly.

**Expected:**
- Flair Status Changed trigger fires.
- Pre-delay check: `occupied_effective` = `on` AND status = `Inactive` → mismatch, branch enters.
- Waits `reconciliation_delay` seconds.
- Post-delay re-check: mismatch still present.
- `select.select_option` called with `Active`.
- `button.press` called on `flair_clear_hold`.
- Vent returns to Active.

---

## UC-04 — Flair status changes but already matches — pre-delay guard exits

**Setup:** Room is occupied. This automation just set `flair_activity_status`
to `Active`, which triggers the Flair Status Changed trigger again.

**Expected:**
- Flair Status Changed trigger fires.
- Pre-delay check: `occupied_effective` = `on` AND status = `Active` → no
  mismatch, branch exits immediately.
- No delay started, no service call made, no restart cycle.

---

## UC-05 — Flair status churn — mismatch resolves before delay expires

**Setup:** Room is occupied. Flair cloud briefly sets status to `Inactive`,
then corrects itself back to `Active` within `reconciliation_delay` seconds.

**Expected:**
- First Flair Status Changed fires → mismatch detected → delay starts.
- Second Flair Status Changed fires → `mode: restart` cancels the first run,
  new run starts.
- Pre-delay check: status is now `Active`, `occupied_effective` = `on` →
  no mismatch, branch exits immediately.
- No service call made. Automation does not fight the self-correcting cloud state.

---

## UC-06 — HA restarts, room was occupied while offline

**Setup:** HA restarts. When integrations restore, `occupied_effective` = `on`
but `flair_activity_status` = `Inactive` (drifted while offline).

**Expected:**
- HA Started trigger fires.
- Automation waits 30 seconds for WITB+ and Flair integration to restore.
- Post-delay check: `occupied_effective` = `on` AND status ≠ `Active` → mismatch.
- `select.select_option` called with `Active`.
- `button.press` called on `flair_clear_hold`.
- Vent corrected to Active.

---

## UC-07 — HA restarts, room was unoccupied while offline

**Setup:** HA restarts. When integrations restore, `occupied_effective` = `off`
but `flair_activity_status` = `Active` (drifted while offline).

**Expected:**
- HA Started trigger fires.
- Automation waits 30 seconds.
- Post-delay check: `occupied_effective` = `off` AND status ≠ `Inactive` → mismatch.
- `select.select_option` called with `Inactive`.
- `button.press` called on `flair_clear_hold`.
- Vent corrected to Inactive.

---

## UC-08 — HA restarts, vent state already correct

**Setup:** HA restarts. `occupied_effective` = `on`, `flair_activity_status` =
`Active` — no drift occurred.

**Expected:**
- HA Started trigger fires.
- Automation waits 30 seconds.
- Post-delay check: both branches fail (status matches occupancy).
- No service call made. `choose` exits with no action.

---

## UC-09 — Occupancy changes during reconciliation delay

**Setup:** Room is occupied. Flair drifts to `Inactive` → reconciliation delay
starts. Before delay expires, room becomes unoccupied (`occupied_effective`
transitions to `off`).

**Expected:**
- With `inactive_delay_minutes` 0: Room Unoccupied fires immediately →
  `mode: restart` cancels the reconciliation run. New run hits the Room
  Unoccupied branch, calls `select.select_option` with `Inactive` and presses
  `flair_clear_hold`. Latest occupancy state wins.
- With `inactive_delay_minutes` 10 min and `reconciliation_delay` 5 s: Room Unoccupied
  has not fired yet, so the reconciliation run is not cancelled. It finishes
  after 5 s; its occupied-side check no longer matches (room is off), and the
  vacant-side check fails because the room has been off for less than 10 min,
  so no service call is made. Room Unoccupied fires at 10 min and sets
  `Inactive`.
- With a vacancy delay longer than `reconciliation_delay` (the usual case),
  Room Unoccupied does not cancel the reconciliation run; it still sets
  `Inactive` when it fires. If the vacancy delay were shorter, Room Unoccupied
  would fire first and cancel the reconciliation run, then set `Inactive`.

---

## UC-10 — Occupancy changes during startup 30-second delay

**Setup:** HA restarts. During the 30-second startup delay, motion is detected
and `occupied_effective` transitions to `on`.

**Expected:**
- Room Occupied trigger fires → `mode: restart` cancels the startup sync run.
- New run hits Room Occupied branch.
- `select.select_option` called with `Active`.
- `button.press` called on `flair_clear_hold`.
- Startup sync is abandoned but occupancy change is correctly applied.

---

## UC-11 — Flair status transitions through unknown/unavailable during HA restart

**Setup:** HA restarts. `flair_activity_status` passes through `unknown` →
`Inactive` → `Active` during state restoration.

**Expected:**
- Transitions involving `unknown` or `unavailable` are suppressed by `not_from`
  / `not_to` filters on the Flair Status Changed trigger.
- Only transitions between known states (`Active` ↔ `Inactive`) fire the trigger.
- No spurious reconciliation runs during HA restart state restoration.

---

## UC-12 — Reconciliation delay set to 0

**Setup:** `reconciliation_delay` configured to `0`. Flair drifts to wrong state.

**Expected:**
- Flair Status Changed trigger fires.
- Pre-delay check: mismatch detected, branch enters.
- Delay of 0 seconds — effectively immediate correction.
- Post-delay re-check passes.
- Service call corrects the status immediately.

> **Note:** Setting delay to 0 means the automation corrects instantly without
> any tolerance for intentional manual Flair app changes. Use only if the Flair
> cloud is reliable and manual overrides are not expected.

---

## UC-13 — Leave and return within the delay — stays Active

**Setup:** `inactive_delay_minutes` = 10 min. Room is occupied, status `Active`.
`occupied_effective` goes `off`, then back `on` after 4 minutes.

**Expected:**
- Room Unoccupied `for:` timer starts, then is cancelled when the sensor
  returns to `on`. The trigger never fires.
- Room Occupied fires on the return and sets `Active` (already Active) and
  presses clear hold.
- The vent never went Inactive.

---

## UC-14 — Leave for longer than the delay — Inactive after the delay

**Setup:** `inactive_delay_minutes` = 10 min. Room is occupied, status `Active`.
`occupied_effective` goes `off` and stays off.

**Expected:**
- Status stays `Active` for 10 minutes.
- Room Unoccupied trigger fires at 10 minutes.
- `select.select_option` called with `Inactive`, then `button.press` on
  `flair_clear_hold`.

---

## UC-15 — Flair app sets Active during the delay — no correction

**Setup:** `inactive_delay_minutes` = 10 min. Room vacant for 3 minutes, status
`Active`. Someone sets the room to `Inactive` in the Flair app, then back to
`Active` (setting an already-Active select may not fire a state change, so
the test needs a real `Inactive` → `Active` transition).

**Expected:**
- Flair Status Changed fires on `Active` → `Inactive` and on `Inactive` →
  `Active`.
- On the `Inactive` → `Active` change, the pre-delay check finds
  `occupied_effective` off for less than `inactive_delay_minutes`, so `Active` is not
  a mismatch; the branch exits. (The earlier change to `Inactive` is a
  matching state and also exits.)
- No service call. The Room Unoccupied trigger still fires at 10 minutes and
  sets `Inactive`.

---

## UC-16 — HA restarts while the room is vacant — Inactive after about 30 s

**Setup:** `inactive_delay_minutes` = 10 min. HA restarts while the room is vacant and
status is `Active`.

**Expected:**
- HA Started trigger fires; waits 30 seconds.
- Startup sync ignores `inactive_delay_minutes`: `occupied_effective` = `off` AND
  status ≠ `Inactive` → mismatch.
- `select.select_option` called with `Inactive`, then `button.press` on
  `flair_clear_hold`.
- Reason: `last_changed` resets on restart and the pending `for:` trigger is
  lost, so the vacancy age is unknown.

---

## UC-17 — HA restarts with delay 0 and occupancy restores unavailable → off

**Setup:** `inactive_delay_minutes` = 0. HA restarts; `occupied_effective`
restores `unavailable` → `off` while `flair_activity_status` is still
`unavailable`.

**Expected:**
- Room Unoccupied fires, but the top-level condition drops it
  (`from_state` is `unavailable` and the delay is 0). No run starts.
- The HA Started run is not cancelled by `mode: restart`.
- After 30 s startup sync sets `Inactive` and presses clear hold, as in 1.0.5.

---

## UC-18 — Vacant at restart, Flair restores Active during the startup wait

**Setup:** `inactive_delay_minutes` = 10. `occupied_effective` was already
`off` at restart, so no Room Unoccupied transition arms. HA Started begins its
30 s wait. Flair goes `Inactive` → `Active` during the wait, which triggers
reconciliation; that run cancels startup sync, then exits because the room has
been vacant for less than the delay.

**Expected:**
- No timer remains from startup sync or Room Unoccupied.
- Once `occupied_effective` has been off for at least the delay, the next
  Consistency Sweep (within a minute) passes the condition, sets `Inactive` and
  presses clear hold.
- Before that, the sweep finds `Active` acceptable and starts no run.

---

## UC-19 — Fractional delay

**Setup:** `inactive_delay_minutes` set to `0.1` (6 s; the number box accepts
fractions). Flair is `unavailable` while HA starts; the delay expires and
cancels startup sync, then Flair restores to `Active`. That change is excluded
from reconciliation.

**Expected:**
- Room is still `Active` after the restore with no run pending.
- The next Consistency Sweep sees a vacant room, `Active`, and an age of at
  least 6 s, so it sets `Inactive` and presses clear hold within a minute.

---

## UC-20 — Sweep with the room in step

**Setup:** Room occupied and `Active`, or vacant and `Inactive`.

**Expected:**
- The sweep trigger fires every minute but the top-level condition fails; no
  run starts and nothing is cancelled. Traces show "condition not met" runs.
