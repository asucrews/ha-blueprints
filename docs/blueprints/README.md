# Blueprint Docs

This folder contains implementation-focused documentation for the active blueprints in this repository.

## Compatibility Matrix

| Blueprint | Type | Version | Min HA | Docs |
| --- | --- | --- | --- | --- |
| `witb_plus.yaml` | automation | `v4.2.4` | `2026.3.0` | `witb_plus.md` |
| `witb_plus_actions_lights_fan.yaml` | automation | `v3.0.3` | `2026.3.0` | `witb_plus_actions_lights_fan.md` |
| `humidity_controled_fan.yaml` | automation | `v1.1.0` | `2023.4.0` | `bathroom_fan_from_humidity_delta.md` |
| `vacuum_job_manager.yaml` | automation | `v1.3` | `2026.3.0` | `vacuum_job_manager.md` |
| `witb_transit_room.yaml` | automation | `v2.0.0` | `2026.3.0` | `witb_transit_room.md` |
| `witb_plus_bed_force_occupied.yaml` | automation | `v1.0.0` | `2026.3.0` | `witb_plus_bed_force_occupied.md` |
| `witb_lights_on_hook_vzw31sn.yaml` | script | `v2.1.1` | `2024.6.0` | `witb_lights_on_hook_vzw31_sn.md` |
| `witb_lights_off_hook_vzw31sn.yaml` | script | `v2.1.1` | `2024.6.0` | `witb_lights_off_hook_vzw31_sn.md` |

## Automation Blueprints

1. [WITB+ Occupancy](./witb_plus.md)
   - Source: `blueprints/automation/witb_plus/v4/witb_plus.yaml`
   - Companion helpers template: `blueprints/automation/witb_plus/v4/witb_plus_package_template.yaml`
   - Generator: `blueprints/generate_witb_packages_templated.py`

2. [WITB+ Actions - Lights + Fan](./witb_plus_actions_lights_fan.md)
   - Source: `blueprints/automation/witb_plus_actions_lights_fan/v3/witb_plus_actions_lights_fan.yaml`
   - Companion helpers template: `blueprints/automation/witb_plus_actions_lights_fan/v3/witb_plus_actions_lights_fan_package_template.yaml`
   - Generator: `blueprints/generate_witb_packages_templated.py`

3. [Bathroom Fan From Humidity Delta](./bathroom_fan_from_humidity_delta.md)
   - Source: `blueprints/automation/humidity_controled_fan/v1/humidity_controled_fan.yaml`
   - Companion helpers template: `blueprints/automation/humidity_controled_fan/v1/humidity_controled_fan_package_template.yaml`
   - Generator: `blueprints/generate_witb_packages_templated.py`

4. [Vacuum Job Manager](./vacuum_job_manager.md)
   - Source: `blueprints/automation/vacuum_job_manager/v1/vacuum_job_manager.yaml`
   - Companion helpers template: `blueprints/automation/vacuum_job_manager/v1/vacuum_job_manager_package_template.yaml`
   - Generator: `blueprints/generate_witb_packages_templated.py`

5. [WITB Transit Room](./witb_transit_room.md)
   - Source (current, v2): `blueprints/automation/witb_transit_room/v2/witb_transit_room.yaml`
   - Legacy v1: `blueprints/automation/witb_transit_room/v1/witb_transit_room.yaml`, helpers template `blueprints/automation/witb_transit_room/v1/witb_transit_room_package_template.yaml`
   - v2 helper package template: added in a follow-up change.

6. [WITB+ Bed → Force Occupied](./witb_plus_bed_force_occupied.md)
   - Source: `blueprints/automation/witb_plus_bed_sensor/v1/witb_plus_bed_force_occupied.yaml`

## Script Blueprints

1. [WITB Lights ON Hook (VZW31-SN)](./witb_lights_on_hook_vzw31_sn.md)
   - Source: `blueprints/script/witb_switch_light_profiles/v1/witb_lights_on_hook_vzw31sn.yaml`

2. [WITB Lights OFF Hook (VZW31-SN)](./witb_lights_off_hook_vzw31_sn.md)
   - Source: `blueprints/script/witb_switch_light_profiles/v1/witb_lights_off_hook_vzw31sn.yaml`

3. [WITB Lights Hooks Combined Overview](./witb_lights_hooks.md)
   - Covers both ON and OFF hook profiles.

## Relationship

- `WITB+` infers room occupancy.
- `WITB+ Actions` consumes `binary_sensor.<slug>_occupied_effective` and handles lights/fan behavior.
- `Bathroom Fan From Humidity Delta` handles humidity-driven fan control with hysteresis and runtime limits.
- `Vacuum Job Manager` can enable WITB `automation_override` booleans during a cleaning job, then disable them at job end.
- `Vacuum Job Manager` can keep vacuum-job lighting on while cleaning and only turn it off when configured occupancy entities are clear.
- `WITB Transit Room` (v2) is WITB+ 4.4.0 minus doors, for hallways/stairs; its occupancy helper feeds `binary_sensor.<slug>_occupied_effective`, consumed by `WITB Actions V3` exactly like the door-based WITB+ v4 signal. v1 (PIR hold-timer driver) is legacy.
- `WITB+ Bed → Force Occupied` extends WITB+ v4 bedroom occupancy during sleep by driving `force_occupied` — it never initiates occupancy, only holds it while the room is already occupied.
- `WITB Lights Hook Scripts` are optional hook implementations for resilient VZW31-SN smart-bulb control.
- `WITB Lights Hook Scripts` are typically called by ON/OFF hook points in WITB actions flows.
