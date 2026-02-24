# Bathroom Fan From Humidity Delta (Automation Blueprint)

This automation blueprint controls a bathroom exhaust fan using a **humidity delta** sensor:

> **delta = max(humidity − baseline, 0)**

The delta signal is designed to represent “how far above normal humidity” the room is right now, which is much more reliable than a fixed RH threshold across seasons.

This blueprint **does not** compute the baseline or delta itself. It expects you to provide a **delta sensor** (typically created via template blueprints).

---

## What this blueprint does

- **Turns fan ON** when `delta >= ON threshold` for a short time (to ignore brief spikes).
- **Turns fan OFF** when `delta <= OFF threshold` for a longer time (to avoid chattering).
- Enforces a **minimum runtime** so the fan stays on long enough to matter.
- Enforces a **failsafe maximum runtime** so the fan can’t run forever.

This is standard “event + hysteresis + safety” control.

---

## Requirements

You must already have:
- A **humidity delta sensor** (`sensor.*`) that reports a number in `%` (commonly 0.0–30.0+)
- A fan entity to control:
  - `fan.*` (preferred)
  - or `switch.*` (if your fan is a switch)

---

## Inputs

### Entities
- **delta_sensor**  
  The sensor representing “humidity above baseline” in percent.

- **fan_entity**  
  The fan or switch entity you want to control.

### Thresholds & timing
- **on_threshold** (default: 8%)  
  Fan turns ON when delta is at or above this value.

- **on_for_seconds** (default: 120s)  
  Delta must remain above the ON threshold for this long before turning on.

- **off_threshold** (default: 3%)  
  Fan turns OFF when delta is at or below this value.

- **off_for_seconds** (default: 600s)  
  Delta must remain below the OFF threshold for this long before turning off.

### Run limits
- **min_run_seconds** (default: 300s)  
  Fan must be ON for at least this long before OFF is allowed.

- **max_run_seconds** (default: 5400s / 90m)  
  Failsafe: if the fan stays ON this long, it will be turned OFF.

---

## Recommended starting values (most bathrooms)

These defaults work well for typical shower detection:
- ON threshold: **8%**
- ON for: **2 minutes**
- OFF threshold: **3%**
- OFF for: **10 minutes**
- Minimum run: **5 minutes**
- Max run failsafe: **90 minutes**

---

## Tuning guide

### Fan turns on too easily (false positives)
- Increase **on_threshold** (e.g., 8 → 10)
- Increase **on_for_seconds** (e.g., 120 → 180)
- Increase **off_for_seconds** so it doesn’t bounce

### Fan turns on too late / misses showers
- Lower **on_threshold** (e.g., 8 → 6)
- Lower **on_for_seconds** (e.g., 120 → 60)

### Fan turns off too soon
- Increase **off_for_seconds** (e.g., 600 → 900)
- Lower **off_threshold** (e.g., 3 → 2)

### Fan runs too long after shower
- Increase **off_threshold** slightly (e.g., 3 → 4) *only if delta drops slowly*
- Reduce **off_for_seconds** slightly (e.g., 600 → 480)

### Fan never turns off
- Confirm delta eventually returns near 0 after the room dries
- Reduce **min_run_seconds** if it’s overly large
- Confirm **max_run_seconds** failsafe is enabled and reasonable

---

## Example: Create an automation from this blueprint (YAML)

```yaml
automation:
  - use_blueprint:
      path: asucrews/bathroom_fan_from_humidity_delta.yaml
      input:
        delta_sensor: sensor.master_bathroom_toilet_humidity_delta
        fan_entity: switch.master_bathroom_toilet_fan
        on_threshold: 8
        on_for_seconds: 120
        off_threshold: 3
        off_for_seconds: 600
        min_run_seconds: 300
        max_run_seconds: 5400
```

## Companion package generator

Use `generate_humidity_packages_templated.py` with `room_humidity_baseline_delta_package.template.yaml` to generate helper packages in `packages/`.
