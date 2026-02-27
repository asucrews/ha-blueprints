# Changelog — WITB VZW31-SN Switch + Bulb Hook Profiles

Covers both hook scripts:
- `witb_lights_on_hook_profile_vzw31_sn_switch_bulb` — turns smart bulbs **ON**
- `witb_lights_off_hook_profile_vzw31_sn_switch_bulb` — turns smart bulbs **OFF**

---

## v2.1.1 *(current)*

### Lights ON Hook

**Bug Fixes**
- Added missing `brightness_mode` input (`fixed` / `day_night`) — previously the fixed brightness
  path was silently unreachable, always falling through to day/night logic.
- `homeassistant.event` on SBM reset now only fires when the helper is *not* an `input_datetime`.
  Previously it fired unconditionally, causing double-updates when an `input_datetime` helper was
  configured.

**Improvements**
- Added `recheck_only_if_any_missing` input to match the OFF hook — the recheck loop can now be
  limited to only run when bulbs are actually unavailable after the initial command.
- Verify loop now exits early as soon as all lights confirm on, rather than always running the full
  `verify_attempts` count.
- `_ensure_sbm` Z-Wave write is now skipped when an SBM reset was just performed, avoiding a
  redundant `set_config_parameter` call on every power reset.
- Success cleanup now dismisses all three notification IDs (status, power, device) instead of only
  status, so transient alerts clear automatically when issues resolve.
- Removed dead `_brightness_pct` and `_notify_id_base` variables that were computed but never used.

---

### Lights OFF Hook

**Bug Fixes**
- `sbm_skip_if_recovered` is now honoured before the SBM reset — the script re-checks bulb
  availability immediately before toggling and skips the reset if they recovered on their own.
  Previously this input existed in the OFF hook but had no effect.
- Full SBM reset sequence (force ON → toggle OFF → toggle ON → force ON → event → wait → settle →
  turn off recovered bulbs) is now correctly wrapped inside the `sbm_skip_if_recovered` guard,
  matching the ON hook's pattern.
- `transition` data was misaligned outside the `light.turn_off` action after the SBM reset — it is
  now correctly nested inside the action, so recovered bulbs turn off with the configured fade.

**Improvements**
- Verify loop now exits early as soon as all lights confirm off, rather than always running the full
  `verify_attempts` count.
- `_ensure_sbm` Z-Wave write is now skipped when an SBM reset was just performed, avoiding a
  redundant `set_config_parameter` call on every power reset.
- Success cleanup now dismisses all three notification IDs (status, power, device) instead of only
  status, so transient alerts clear automatically when issues resolve.
- Removed dead `_notify_id_base` variable that was computed but never used.

---

## v2.1

**Both hooks**
- Refactored to use blueprint `input:` sections with logical groupings: Core, Smart Bulb Mode,
  Reliability, Notifications, Local Protection. ON hook adds a Brightness section.
- All settings are now configurable from the blueprint UI — no need to modify WITB or WITB Actions
  automations to change behaviour.

---

## v1.9

**Both hooks**
- Added verify + retry loop for command reliability — handles bulbs that miss the initial ON/OFF.
- Safer SBM reset: forces the switch output ON before and after toggling Parameter 52 to ensure
  bulbs receive power throughout the cycle.
- Optional SBM reset cooldown via `input_datetime` helper or template timestamp sensor — prevents
  rapid repeated resets during instability.
- Fires a custom event for template trackers when an SBM reset occurs, so external blueprints can
  react or log the event.
- Optional local protection enforcement via a Z-Wave JS select entity — prevents the wall paddle
  from cutting power or changing level while automation is in control.
- Notification hygiene: all notifications use a persistent `notification_id` so repeated triggers
  update the existing notification instead of creating duplicates.
