# Blueprint Docs

This folder contains implementation-focused documentation for the active blueprints in this repository.

## Compatibility Matrix

| Blueprint | Type | Version | Min HA | Docs |
| --- | --- | --- | --- | --- |
| `witb_plus.yaml` | automation | `v3.5` | `2026.2.0` | `witb_plus_v3.md` |
| `witb_plus_actions_lights_fan.yaml` | automation | `v1.4.1` | `2026.2.0` | `witb_plus_actions_lights_fan_v1.md` |
| `vacuum_job_manager.yaml` | automation | `v1.1` | `2026.2.0` | `vacuum_job_manager_v1.md` |
| `witb_lights_on_hook_profile_vzw31_sn_switch_bulb_v1_7.yaml` | script | `v1.7` | `2024.6.0` | `witb_lights_on_hook_vzw31_sn_v1_7.md` |
| `witb_lights_off_hook_profile_vzw31_sn_switch_bulb_v1_7.yaml` | script | `v1.7` | `2024.6.0` | `witb_lights_off_hook_vzw31_sn_v1_7.md` |

## Automation Blueprints

1. [WITB+ v3 Occupancy](./witb_plus_v3.md)
   - Source: `blueprints/automation/witb_plus/v3/witb_plus.yaml`
   - Companion helpers generator: `blueprints/automation/witb_plus/v3/generate_witb_packages.py`

2. [WITB+ Actions - Lights + Fan v1](./witb_plus_actions_lights_fan_v1.md)
   - Source: `blueprints/automation/witb_plus_actions_lights_fan/v1/witb_plus_actions_lights_fan.yaml`
   - Companion helpers generator: `blueprints/automation/witb_plus_actions_lights_fan/v1/generate_witb_plus_actions_packages.py`

3. [Vacuum Job Manager (iRobot) v1](./vacuum_job_manager_v1.md)
   - Source: `blueprints/automation/vacuum_job_manager/v1/vacuum_job_manager.yaml`
   - Companion helpers package: `blueprints/automation/vacuum_job_manager/v1/vacuum_job_helpers.yaml`

## Script Blueprints

1. [WITB Lights ON Hook (VZW31-SN) v1.7](./witb_lights_on_hook_vzw31_sn_v1_7.md)
   - Source: `blueprints/script/witb_lights/v1/witb_lights_on_hook_profile_vzw31_sn_switch_bulb_v1_7.yaml`

2. [WITB Lights OFF Hook (VZW31-SN) v1.7](./witb_lights_off_hook_vzw31_sn_v1_7.md)
   - Source: `blueprints/script/witb_lights/v1/witb_lights_off_hook_profile_vzw31_sn_switch_bulb_v1_7.yaml`

3. [WITB Lights Hooks Combined Overview](./witb_lights_hooks_v1_7.md)
   - Covers both ON and OFF hook profiles.

## Relationship

- `WITB+ v3` infers room occupancy.
- `WITB+ Actions` consumes `binary_sensor.<slug>_occupied_effective` and handles lights/fan behavior.
- `Vacuum Job Manager` can enable WITB `automation_override` booleans during a cleaning job, then disable them at job end.
- `Vacuum Job Manager` can keep vacuum-job lighting on while cleaning and only turn it off when configured occupancy entities are clear.
- `WITB Lights Hook Scripts` are optional hook implementations for resilient VZW31-SN smart-bulb control.
- `WITB Lights Hook Scripts` are typically called by ON/OFF hook points in WITB actions flows.
