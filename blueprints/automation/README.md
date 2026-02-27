# blueprints/automation/

Active automation blueprints.

## Blueprints

1. [`witb_plus/`](witb_plus/README.md) — WITB+ Occupancy (v4)
   - Room occupancy inference from doors + motion + optional mmWave.

2. [`witb_plus_actions_lights_fan/`](witb_plus_actions_lights_fan/README.md) — WITB+ Actions - Lights + Fan (v2)
   - Occupancy-driven light/fan control with safety tags, lux gating, and humidity hold.

3. [`bathroom_fan_from_humidity/`](bathroom_fan_from_humidity/README.md) — Bathroom Fan From Humidity Delta (v1)
   - Humidity-delta-based fan control with hysteresis and runtime safety limits.

4. [`vacuum_job_manager/`](vacuum_job_manager/README.md) — Vacuum Job Manager (v1)
   - Queued/scheduled vacuum job orchestration with mission-counter completion and optional WITB integration.

5. [`witb_transit_room/`](witb_transit_room/README.md) — WITB Transit Room Driver (v1)
   - PIR-only occupancy driver for hallways/stairs using hold-timer decay; outputs a WITB-compatible `occupied_effective` signal.

6. [`witb_plus_bed_sensor/`](witb_plus_bed_sensor/README.md) — WITB+ Bed → Force Occupied (v1)
   - Bedroom sleep guard; drives `force_occupied` to prevent WITB+ from clearing occupancy while someone is in bed.
