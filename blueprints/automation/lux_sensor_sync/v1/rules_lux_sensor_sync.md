# Rules — lux_sensor_sync

Behavioral rules governing `lux_sensor_sync.yaml`. These are the invariants
the blueprint enforces regardless of which trigger fires.

---

## Trigger rules

1. **Light ON trigger** — fires when `delta_sensor` rises above `on_threshold`
   and stays there for `on_for_seconds`. Uses `numeric_state: above` + `for:`.
2. **Light OFF trigger** — fires when `delta_sensor` falls below `off_threshold`
   and stays there for `off_for_seconds`. Uses `numeric_state: below` + `for:`.
3. **HA Start trigger** — fires once on `homeassistant: start`. Initiates
   startup state correction after a settling delay.

---

## Infer ON rules

4. **Infer ON** fires only when all conditions are met:
   - Trigger ID is `light_on`
   - `light_boolean` is currently `off`
   - Sensor restore suppression passes (see rule 6)
5. If `light_boolean` is already `on` when the trigger fires, the branch
   exits silently — no service call is made.
6. **Sensor restore suppression** (`suppress_infer_on_after_sensor_restore`,
   default `true`) — if enabled, infer-ON is suppressed when
   `trigger.from_state.state` is `unknown` or `unavailable`. Detects the
   scenario where the sensor just restored from HA restart or a sensor
   reconnect and prevents a false positive inference. Disable if you want
   infer-ON to proceed immediately after any sensor reconnect.

---

## Infer OFF rules

7. **Infer OFF** fires only when all conditions are met:
   - Trigger ID is `light_off`
   - `light_boolean` is currently `on`
8. If `light_boolean` is already `off` when the trigger fires, the branch
   exits silently — no service call is made.
9. Sensor restore suppression does **not** apply to the infer-OFF branch —
   turning the boolean off is always the safe direction.

---

## HA startup rules

10. On HA restart, the automation waits **30 seconds** (hardcoded) for sensors
    and integrations to finish restoring before reading any state.
11. **Infer-ON correction** — after the settling delay, if `delta_sensor` is
    above `on_threshold` AND `light_boolean` is `off`, the boolean is turned on.
12. **Infer-OFF correction** — after the settling delay, if `delta_sensor` is
    below `off_threshold` AND `light_boolean` is `on`, the boolean is turned off.
    This path is always active — correcting to OFF is always safe.
13. Infer-ON and infer-OFF corrections are mutually exclusive in the startup
    branch. If infer-ON conditions pass, the `else` infer-OFF path is not
    evaluated. If infer-ON conditions fail for any reason (delta too low,
    boolean already on), the `else` path runs and attempts infer-OFF.
14. The startup branch does not apply sensor restore suppression — by the time
    the 30-second delay completes, sensors are expected to have fully restored
    to their actual state.

---

## Hysteresis rules

15. `on_threshold` must be set higher than `off_threshold` to create a
    hysteresis band. This prevents rapid toggling when the delta is near a
    single threshold value.
16. The blueprint does not enforce that `on_threshold > off_threshold` at
    configuration time. Misconfiguration (equal or inverted thresholds) can
    cause simultaneous trigger conditions and boolean oscillation.

---

## Execution mode rules

17. **`mode: restart`** — if a new trigger fires while any sequence (including
    the 30-second startup delay) is in progress, the current run is canceled
    and a new run starts immediately. Latest sensor state always wins.
18. If the `ha_start` delay is interrupted by a `light_on` or `light_off`
    trigger, the startup sync is abandoned and the occupancy branch handles
    the transition correctly.
