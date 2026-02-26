# Blueprint Docs

This folder contains implementation-focused documentation for the active blueprints in this repository.

## Compatibility Matrix

| Blueprint | Type | Version | Min HA | Docs |
| --- | --- | --- | --- | --- |
| `witb_plus.yaml` | automation | `v4.2.0` | `2026.2.0` | `witb_plus_v3.md` |
| `witb_plus_actions_lights_fan.yaml` | automation | `v2.2.0` | `2026.2.0` | `witb_plus_actions_lights_fan_v1.md` |
| `bathroom_fan_from_humidity_delta.yaml` | automation | `v1.0.1` | `2026.2.0` | `bathroom_fan_from_humidity_delta_v1.md` |
| `vacuum_job_manager.yaml` | automation | `v1.1` | `2026.2.0` | `vacuum_job_manager_v1.md` |
| `final_updated_witb_hook_on_vzw31sn_no_value_source_cleaned_final.yaml` | script | `v2.1` | `2024.6.0` | `witb_lights_on_hook_vzw31_sn_v1_7.md` |
| `final_updated_witb_hook_off_vzw31sn_no_value_source_cleaned_final.yaml` | script | `v2.1` | `2024.6.0` | `witb_lights_off_hook_vzw31_sn_v1_7.md` |

## Automation Blueprints

1. [WITB+ Occupancy](./witb_plus_v3.md)
   - Source: `blueprints/automation/witb_plus/v4/witb_plus.yaml`
   - Companion helpers generator: `blueprints/automation/witb_plus/v4/generate_witb_packages_templated.py`

2. [WITB+ Actions - Lights + Fan](./witb_plus_actions_lights_fan_v1.md)
   - Source: `blueprints/automation/witb_plus_actions_lights_fan/v2/witb_plus_actions_lights_fan.yaml`
   - Companion helpers generator: `blueprints/automation/witb_plus_actions_lights_fan/v2/generate_witb_plus_actions_packages_templated.py`

3. [Bathroom Fan From Humidity Delta](./bathroom_fan_from_humidity_delta_v1.md)
   - Source: `blueprints/automation/bathroom_fan_from_humidity/bathroom_fan_from_humidity_delta.yaml`
   - Companion helpers generator: `blueprints/automation/bathroom_fan_from_humidity/generate_humidity_packages_templated.py`

4. [Vacuum Job Manager (iRobot) v1](./vacuum_job_manager_v1.md)
   - Source: `blueprints/automation/vacuum_job_manager/v1/vacuum_job_manager.yaml`
   - Companion helpers package: `blueprints/automation/vacuum_job_manager/v1/vacuum_job_helpers.yaml`

## Script Blueprints

1. [WITB Lights ON Hook (VZW31-SN)](./witb_lights_on_hook_vzw31_sn_v1_7.md)
   - Source: `blueprints/script/witb_switch_light_profiles/v1/final_updated_witb_hook_on_vzw31sn_no_value_source_cleaned_final.yaml`

2. [WITB Lights OFF Hook (VZW31-SN)](./witb_lights_off_hook_vzw31_sn_v1_7.md)
   - Source: `blueprints/script/witb_switch_light_profiles/v1/final_updated_witb_hook_off_vzw31sn_no_value_source_cleaned_final.yaml`

3. [WITB Lights Hooks Combined Overview](./witb_lights_hooks_v1_7.md)
   - Covers both ON and OFF hook profiles.

## Relationship

- `WITB+` infers room occupancy.
- `WITB+ Actions` consumes `binary_sensor.<slug>_occupied_effective` and handles lights/fan behavior.
- `Bathroom Fan From Humidity Delta` handles humidity-driven fan control with hysteresis and runtime limits.
- `Vacuum Job Manager` can enable WITB `automation_override` booleans during a cleaning job, then disable them at job end.
- `Vacuum Job Manager` can keep vacuum-job lighting on while cleaning and only turn it off when configured occupancy entities are clear.
- `WITB Lights Hook Scripts` are optional hook implementations for resilient VZW31-SN smart-bulb control.
- `WITB Lights Hook Scripts` are typically called by ON/OFF hook points in WITB actions flows.
