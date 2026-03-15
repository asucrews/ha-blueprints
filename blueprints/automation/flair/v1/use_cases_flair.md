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

**Setup:** `occupied_effective` transitions from `on` → `off`.
`flair_activity_status` is currently `Active`.

**Expected:**
- Room Unoccupied trigger fires.
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
- Room Unoccupied trigger fires → `mode: restart` cancels the reconciliation run.
- New run hits Room Unoccupied branch.
- `select.select_option` called with `Inactive`.
- `button.press` called on `flair_clear_hold`.
- Vent correctly set to Inactive — latest occupancy state wins.

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
