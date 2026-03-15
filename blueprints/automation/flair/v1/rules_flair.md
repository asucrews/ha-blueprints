# Rules — flair

Behavioral rules governing `flair.yaml`. These are the invariants the
blueprint enforces regardless of which trigger fires.

---

## Trigger rules

1. **Room Occupied trigger** — fires on `occupied_effective` state change
   strictly from `off` → `on`. Does not fire on `unknown`/`unavailable`
   transitions.
2. **Room Unoccupied trigger** — fires on `occupied_effective` state change
   strictly from `on` → `off`. Does not fire on `unknown`/`unavailable`
   transitions.
3. **Flair Status Changed trigger** — fires on any state change to
   `flair_activity_status`, excluding `unknown` and `unavailable` in both
   `from` and `to`. Suppresses spurious reconciliation during HA restart
   state restoration.
4. **HA Started trigger** — fires once on `homeassistant: start`. Initiates
   startup sync sequence.

---

## Primary control rules

5. **Room Occupied** → call `select.select_option` with `Active` on
   `flair_activity_status`, then call `button.press` on `flair_clear_hold`.
6. **Room Unoccupied** → call `select.select_option` with `Inactive` on
   `flair_activity_status`, then call `button.press` on `flair_clear_hold`.
7. **Clear hold is always pressed** after every activity status change,
   in both primary control and reconciliation branches.

---

## Reconciliation rules

8. **Pre-delay mismatch check** — the `Flair Status Changed` branch only
   enters if a mismatch exists at trigger time:
   - `occupied_effective` is `on` AND `flair_activity_status` is not `Active`, OR
   - `occupied_effective` is `off` AND `flair_activity_status` is not `Inactive`.
   If the status already matches (e.g. this automation's own service call just
   set it correctly), the branch exits immediately — no delay, no restart cycle.
9. **Reconciliation delay** — after the pre-delay check passes, wait
   `reconciliation_delay` seconds (default 5, range 0–60) before correcting.
   The delay absorbs intentional manual changes and brief cloud state churn.
10. **Post-delay re-evaluation** — after the delay, re-check the mismatch
    condition before correcting. If the mismatch has resolved on its own, no
    service call is made.
11. **Reconciliation is bidirectional** — corrects in both directions:
    occupied + not-Active → set Active; unoccupied + not-Inactive → set Inactive.
12. **No `default` in reconciliation `choose`** — if neither branch matches
    after the delay (unexpected state), the sequence exits silently. Primary
    control handles normal occupancy transitions; reconciliation is a safety net.

---

## Startup sync rules

13. **Startup delay** — on HA restart, wait 30 seconds (hardcoded,
    non-configurable) for WITB+ and the Flair integration to fully restore
    before reconciling.
14. **Startup reconciliation** — after 30 seconds, evaluate
    `occupied_effective` vs `flair_activity_status` and correct if mismatched.
    Recovers from drift that occurred while HA was offline.
15. **Startup delay is intentionally blocking** — the 30-second delay fires
    once per HA restart. Converting it to a timer helper is not justified for
    a one-time-per-restart path.

---

## Execution mode rules

16. **`mode: restart`** — if a new trigger fires while any sequence is in
    progress (including during a reconciliation delay), the current run is
    canceled and a new run starts immediately with the latest trigger context.
17. Rapid Flair cloud state churn causes repeated restarts that keep resetting
    the reconciliation delay, preventing oscillation against a churning cloud
    state.
18. If `occupied_effective` changes while a startup sync delay is in progress,
    the automation restarts and the relevant occupancy branch (Occupied or
    Unoccupied) runs instead. The startup sync is abandoned but the new
    occupancy state is correctly applied.
