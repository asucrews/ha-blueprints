# WITB Lights Hook Scripts (VZW31-SN)

## Scope

Script blueprints:

- `blueprints/script/witb_switch_light_profiles/v1/final_updated_witb_hook_on_vzw31sn_no_value_source_cleaned_final.yaml`
- `blueprints/script/witb_switch_light_profiles/v1/final_updated_witb_hook_off_vzw31sn_no_value_source_cleaned_final.yaml`

Both are `domain: script` with minimum Home Assistant `2024.6.0`.

## Purpose

These scripts are hook profiles for WITB action flows where smart bulbs may be behind an Inovelli VZW31-SN dimmer.

They add resiliency around bulb availability by:

- optionally toggling Smart Bulb Mode (Parameter 52, `0 -> 1`)
- optionally pinging Z-Wave before parameter writes
- waiting/retrying for bulb availability
- running recheck loops to enforce ON/OFF after reconnect
- optionally sending diagnostic notifications

## Shared Inputs

### Hook Payload (typically passed in by automation)

- `lights` (required)
- `transition` (optional)
- optional context: `is_night`, `lux_value`, `lux_threshold`, `reason`

### VZW31-SN Device

- `vzw31_entity` (required, `zwave_js` entity)
- `vzw31_node_status` (optional)
- `vzw31_ping_button` (optional)

### Ping Controls

- `ping_attempts` (default: `2`)
- `ping_timeout_s` (default: `8`)
- `ping_retry_delay_s` (default: `1`)

### Recovery/Timing

- `power_on_delay_ms` (default: `250`)
- `availability_timeout_s` (default: `10`)
- `settle_after_rejoin_ms` (default: `750`)
- `recheck_enabled` (default: `true`)
- `recheck_interval_s` (default: `10`)
- `recheck_attempts` (default: `6`)
- `reset_power_if_unavailable` (default: `true`)
- `ensure_smart_bulb_mode_enabled` (default: `true`)

### Notifications

- `notify_enabled` (default: `true`)
- `notify_mode` (`persistent`, `notify`, `both`; default: `persistent`)
- `notify_service` (default: empty)
- `notify_prefix` (default: `WITB`)

### Smart Bulb Mode Advanced

- `smart_bulb_mode_param` (default: `52`)
- `smart_bulb_mode_disabled_value` (default: `0`)
- `smart_bulb_mode_enabled_value` (default: `1`)
- `sbm_toggle_delay_ms` (default: `300`)

## ON Script Specific

Additional field:

- `brightness_pct` (optional, default behavior uses 100)

Behavior highlights:

- If bulbs are unavailable, can perform SBM reset and retry.
- Enforces brightness every run (helps recover day/night intended level after outages).

## OFF Script Specific

Additional field:

- `recheck_only_if_any_missing` (default: `true`)

Behavior highlights:

- Turns off currently available bulbs immediately.
- Optionally performs SBM reset and recheck loop so late-recovering bulbs still get turned off.

## Integration Notes

1. Create script entities from each script blueprint.
2. Configure per-room VZW31 and recovery options on each script instance.
3. Call these scripts from your automation hook points with `lights` and optional context fields.
4. Start with default recovery settings, then tune recheck and notification behavior to match device reliability.
