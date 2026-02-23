# Adaptive Humidity Baseline + Delta (Home Assistant)

This setup gives you a **season-proof humidity signal** you can use to drive bathroom exhaust fans.

Instead of “humidity > X%” (which breaks across seasons), it builds a **dynamic baseline** for the room and then computes a **delta**:

> **delta = max(humidity − baseline, 0)**

So the fan logic becomes “turn on when humidity rises *above normal* by N%”.

---

## Why this exists

Relative humidity (RH) drifts a lot with:
- seasons (winter vs summer)
- HVAC cycles
- open windows / rain days
- daily patterns

A fixed threshold (e.g., 55%) is either too sensitive in humid months or too insensitive in dry months.

This approach detects **events** (showers) by measuring “how far above normal” the room is right now.

---

## What you get

### 1) Baseline Sensor (template blueprint)
Creates a sensor like:

- `sensor.master_bathroom_toilet_humidity_baseline`

This value represents “normal room humidity right now” and adapts over time.

### 2) Delta Sensor (template blueprint)
Creates a sensor like:

- `sensor.master_bathroom_toilet_humidity_delta`

This is the **event signal** you trigger automations from.

---

## How it works (plain English)

### Baseline behavior

The baseline is a “slow-moving” value that updates when triggered (humidity changes and/or periodic tick).

It has three key behaviors:

1) **Follows DOWN faster than UP**
- If humidity drops (room drying out), the baseline moves down **faster** so it doesn’t stay stuck high.
- If humidity rises slowly over days (season drift), the baseline creeps up **slowly** so it still tracks reality.

2) **Freezes during a big rise (shower)**
If humidity jumps above baseline by `big_rise_freeze` (e.g. +3%), the baseline stops moving temporarily.
That prevents the baseline from “chasing” the shower spike.

3) **Optionally freezes while the fan is ON**
If enabled, baseline won’t learn the shower spike while the fan is actively running.

### Delta behavior

Delta is just:

- humidity − baseline
- clamped so it never goes negative (defaults to floor = 0)

So:
- when the room is normal → delta is near **0**
- when a shower starts → delta rises quickly (e.g. **8–15%+**)

---

## Typical fan strategy

Use the delta sensor for fan decisions:

- **Fan ON** when `delta >= 8%` for 1–2 minutes
- **Fan OFF** when `delta <= 3%` for ~10 minutes
- Optional: min runtime + max runtime failsafe

This gives you:
- quick turn-on during showers
- stable turn-off (no chattering)
- works across seasons

---

## Installation

### File locations

Put these blueprints into your HA config:

- `config/blueprints/template/asucrews/adaptive_humidity_baseline.yaml`
- `config/blueprints/template/asucrews/humidity_delta_from_baseline.yaml`

(Optional automation blueprint)
- `config/blueprints/automation/asucrews/bathroom_fan_from_humidity_delta.yaml`

Then reload:
- **Settings → Devices & services → YAML → Reload Template Entities**
(or restart HA)

---

## Usage (example)

Your templates config (package/snippet) looks like this:

```yaml
exhaust_fan:
  template:
    - use_blueprint:
        path: asucrews/adaptive_humidity_baseline.yaml
        input:
          humidity_sensor: sensor.master_bathroom_toilet_temp_and_humidity_sensor_humidity
          fan_entity: switch.master_bathroom_toilet_fan
      name: Master Bathroom Toilet Humidity Baseline
      unique_id: master_bathroom_toilet_humidity_baseline

    - use_blueprint:
        path: asucrews/humidity_delta_from_baseline.yaml
        input:
          humidity_sensor: sensor.master_bathroom_toilet_temp_and_humidity_sensor_humidity
          baseline_sensor: sensor.master_bathroom_toilet_humidity_baseline
      name: Master Bathroom Toilet Humidity Delta
      unique_id: master_bathroom_toilet_humidity_delta