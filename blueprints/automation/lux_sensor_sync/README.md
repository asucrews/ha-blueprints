# lux_sensor_sync/

Lux Sensor Sync blueprint.

## Current version

**v1** — see [`v1/README_lux_sensor_sync_v1.md`](v1/README_lux_sensor_sync_v1.md)

## Summary

Infers whether a light is on or off by comparing a lux delta sensor against configurable thresholds. Designed for lights that cannot be controlled directly by Home Assistant (fan-mounted lights, dumb switches, etc.). Updates an input_boolean to keep HA in sync with the physical light state.
