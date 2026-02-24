# Bathroom Fan From Humidity Delta

## Scope

- Source blueprint: `blueprints/automation/bathroom_fan_from_humidity/bathroom_fan_from_humidity_delta.yaml`
- Blueprint name: `Bathroom Fan From Humidity Delta v1.0.1`
- Home Assistant minimum: `2026.2.0`
- Domain: `automation`

This blueprint controls a bathroom fan from a humidity-delta signal:
- turns ON when delta is above an ON threshold for a short window,
- turns OFF when delta is below an OFF threshold for a longer window,
- enforces minimum runtime and maximum runtime safety limits.

## Required Inputs

- `delta_sensor` (`sensor.*`): humidity delta in percent.
- `fan_entity` (`fan.*`, `switch.*`, or `light.*`): fan control target.

## Tuning Inputs

- `on_threshold` / `on_for_seconds`
- `off_threshold` / `off_for_seconds`
- `min_run_seconds`
- `max_run_seconds`

## Companion Helper Packages

The blueprint expects a usable delta sensor. You can generate helper package scaffolding with:

```bash
python blueprints/automation/bathroom_fan_from_humidity/generate_humidity_packages_templated.py \
  --rooms "Half Bathroom" \
  --template blueprints/automation/bathroom_fan_from_humidity/room_humidity_baseline_delta_package.template.yaml \
  --out blueprints/automation/bathroom_fan_from_humidity/packages
```
