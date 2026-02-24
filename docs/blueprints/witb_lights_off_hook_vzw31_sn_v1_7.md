# WITB Lights OFF Hook (VZW31-SN)

## Scope

- Source blueprint: `blueprints/script/witb_switch_light_profiles/v1/final_updated_witb_hook_off_vzw31sn_no_value_source_cleaned_final.yaml`
- Blueprint name: `WITB Lights OFF Hook (Profile: VZW31-SN Switch + Bulb) v2.1 (inputs)`
- Domain: `script`
- Home Assistant minimum: `2024.6.0`

This script blueprint is an OFF hook profile for WITB actions in setups where smart bulbs are behind an Inovelli VZW31-SN dimmer.

## Primary Behavior

- Accepts `lights` list and optional `transition`.
- Turns off currently available bulbs immediately.
- If bulbs are unavailable/unknown, can recover by toggling Smart Bulb Mode (`0 -> 1`) and retrying.
- Can run Z-Wave ping attempts before config writes.
- Uses recheck loop to enforce OFF as bulbs reconnect.
- Can emit persistent and/or notify-service diagnostics.

## Inputs

### Hook Payload

- `lights` (required)
- `transition` (optional)
- optional context: `is_night`, `lux_value`, `lux_threshold`, `reason`

### Device/Recovery

- `vzw31_entity` (required)
- optional: `vzw31_node_status`, `vzw31_ping_button`
- ping controls: `ping_attempts`, `ping_timeout_s`, `ping_retry_delay_s`
- timing: `power_on_delay_ms`, `availability_timeout_s`, `settle_after_rejoin_ms`
- recheck: `recheck_enabled`, `recheck_interval_s`, `recheck_attempts`, `recheck_only_if_any_missing`
- recovery toggles: `reset_power_if_unavailable`, `ensure_smart_bulb_mode_enabled`

### Notifications

- `notify_enabled`
- `notify_mode` (`persistent`, `notify`, `both`)
- `notify_service`
- `notify_prefix`

### Smart Bulb Mode Advanced

- `smart_bulb_mode_param` (default: `52`)
- `smart_bulb_mode_disabled_value` (default: `0`)
- `smart_bulb_mode_enabled_value` (default: `1`)
- `sbm_toggle_delay_ms` (default: `300`)

## Integration Notes

1. Create a script instance from this blueprint for each room profile.
2. Set room-specific VZW31 entity and recovery settings.
3. Call the script from your action hook with `lights`, and optionally `transition` and context.
