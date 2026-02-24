# WITB Lights Hook Scripts (VZW31-SN Profile)

This folder contains script blueprints used as ON/OFF hook implementations for WITB Actions when bulbs are behind an Inovelli VZW31-SN dimmer.

## Files

- `final_updated_witb_hook_on_vzw31sn_no_value_source_cleaned_final.yaml`
- `final_updated_witb_hook_off_vzw31sn_no_value_source_cleaned_final.yaml`
- `package_room_witb_profile_with_sbm_helpers.yaml` (optional helper package template)
- `witb_hook_on_vzw31sn.yaml.txt` / `witb_hook_off_vzw31sn.yaml.txt` (text copies)

## Purpose

These scripts are designed to improve reliability when smart bulbs may be unavailable after power events:

- Optional Smart Bulb Mode toggle (`Parameter 52`: `0 -> 1`) to recover bulbs.
- Optional Z-Wave health check/ping before config writes.
- Recheck loops to enforce ON/OFF after bulbs reconnect.
- Optional notifications to distinguish power events from device issues.

## Usage Model

Create script instances from these script blueprints, then call those scripts from your automation hooks with payload fields like:

- `lights`
- `brightness_pct` (ON script)
- `transition`
- optional context: `is_night`, `lux_value`, `lux_threshold`, `reason`

Detailed field documentation is in:
- `docs/blueprints/witb_lights_on_hook_vzw31_sn_v1_7.md`
- `docs/blueprints/witb_lights_off_hook_vzw31_sn_v1_7.md`
- `docs/blueprints/witb_lights_hooks_v1_7.md` (combined overview)
