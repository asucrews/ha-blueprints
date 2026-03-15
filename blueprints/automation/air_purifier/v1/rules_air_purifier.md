# Rules — air_purifier

Behavioral rules governing `air_purifier.yaml`. These are the invariants the
blueprint enforces regardless of which trigger fires.

---

## Trigger rules

1. **Boundary trigger** — fires at exactly `first_start_time`, `first_end_time`,
   `second_start_time`, and `second_end_time`. Provides instant state transitions
   at window edges.
2. **Reconcile trigger** — fires every 5 minutes via `time_pattern`. Heals any
   device that drifted, was offline, or was manually changed while inside or
   outside a boost window.
3. **Startup trigger** — fires once on `homeassistant: start`. Ensures correct
   state is applied immediately after an HA reboot without waiting for the next
   reconcile tick.

---

## Window evaluation rules

4. A device is **inside a boost window** when:
   `(t_now >= first_start AND t_now < first_end) OR (t_now >= second_start AND t_now < second_end)`
   where `t_now` is `now().strftime('%H:%M:%S')`.
5. The comparison is performed as an **HH:MM:SS string comparison**, making it
   timezone-safe and avoiding `TypeError` from mixing `today_at()` (naive) with
   `now()` (timezone-aware).
6. The `first_end` and `second_end` boundaries are **exclusive** — a device
   transitions out of boost at exactly the end time, not one second later.
7. **Midnight-spanning windows are not supported.** If `second_end_time` is
   earlier than `second_start_time` (e.g. 23:00–01:00), the string comparison
   will evaluate incorrectly.

---

## Device control rules

8. **During a boost window:** call `fan.set_percentage` with `boost_percentage`
   on every entity in `purifier_entities`.
9. **Outside a boost window:** call `fan.set_preset_mode` with `return_preset_mode`
   on every entity in `purifier_entities`.
10. **No-op guard (percentage):** skip `fan.set_percentage` if the entity's
    current `percentage` attribute already equals `boost_percentage`. Prevents
    log spam and unnecessary Zigbee/Z-Wave traffic.
11. **No-op guard (preset):** skip `fan.set_preset_mode` if the entity's current
    `preset_mode` attribute already equals `return_preset_mode`.
12. **`is_on` guard (v1.1.0+):** skip `fan.set_percentage` if the entity state is
    not `on`. A purifier that was manually turned off must not be powered on by
    the reconciler during a boost window.
13. Entities are processed **sequentially** via `repeat.for_each`. There is no
    parallel dispatch — all purifiers in the group are reconciled in list order
    on every run.

---

## Execution mode rules

14. `mode: single` (v1.0.0) — if a reconcile run is already in progress when a
    new trigger fires, the new trigger is **silently dropped**.
15. `mode: queued, max: 2` (v1.1.0+) — at most one pending run is queued behind
    an active run, so no boundary trigger is ever dropped.
