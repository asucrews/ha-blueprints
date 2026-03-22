# WITB+ Actions (Lights + Fan) — v3

This folder contains the **actions blueprints** that pair with WITB+ occupancy.

Use this when you already have room occupancy sensors from `witb_plus/v4` (for example
`binary_sensor.<slug>_occupied_effective`) and want reliable light/fan actions with
safety tags, external gating, and fully event-driven execution.

---

## 1. Blueprints

### `witb_plus_actions_lights_fan.yaml` — main actions blueprint (v3.0.4)

Controls lights and fan for a single room based on occupancy state changes from
`binary_sensor.<slug>_occupied_effective`. Key behaviors:

- **Fully event-driven (v3.0.0)** — all blocking `delay:` steps replaced with
  dedicated timers. Every automation run completes in milliseconds. `mode:restart`
  is safe across all paths — no run can be killed mid-sequence while waiting.
- **Lights ON/OFF** with day/night brightness profiles and configurable transition speeds.
- **Soft-off warning** — dims to 10% and starts `soft_off_timer` before full lights-off.
- **Lights verify** — starts `lights_verify_timer` after turn-off and retries up to N
  times if lights are still reporting ON.
- **Lights claim** — `lights_claim_if_already_on` (default `true`): the blueprint
  claims ownership of lights that were already on when the room became occupied and
  will turn them off on vacancy. Set `false` only if you want the automation to
  leave pre-existing light state alone entirely.
- **Fan claim** — `fan_claim_if_already_on` (default `true`): same ownership
  semantics for the fan. Set `false` to leave a pre-existing fan state unmanaged.
- **Manual-off hold** — if you turn lights off while occupied they stay off until
  vacancy clears `auto_tag_lights`, then re-arm next occupancy.
- **Bed suppress** — if a bed sensor is configured and someone is in bed, occupancy
  re-assertion does not turn lights back on.
- **Light gating** — wire an external `binary_sensor` computed from lux, sun
  elevation, curtains, or season. Blueprint does not evaluate these inline.
- **Fan ON on occupancy** via `fan_on_delay_timer` (no blocking delay).
- **Fan run-on timer** after vacancy, with optional gate to hold the fan on while
  humidity or other conditions require it.
- **Fan vacancy gate** — wire an external `binary_sensor` (e.g. humidity threshold).
  OFF = hold fan on; ON = ok to turn off. When the gate clears while the room is
  already vacant the fan turns off automatically.
- **Auto-tag helpers** (`input_boolean`) track automation ownership of lights and fan
  for safe "only turn off what we turned on" behavior.

### `witb_plus_actions_lights.yaml` — lights-only variant

Same as above but with fan control removed. Use for rooms with no fan.

> **Note:** The companion `witb_plus_actions_cleanup` blueprint is still recommended
> as belt-and-suspenders but is no longer the primary safety net in v3.

---

## 2. Package Helpers

**Reference template:** `witb_plus_actions_lights_fan_package_template.yaml`
**Generated output location:** `packages/`

Package files provide helper entities such as:

| Entity | Purpose |
|---|---|
| `input_boolean.<slug>_auto_lights_on` | Auto-tag for lights ownership |
| `input_boolean.<slug>_auto_fan_on` | Auto-tag for fan ownership |
| `input_boolean.<slug>_keep_on` | Blocking entity — prevents vacancy off |
| `timer.<slug>_actions_cooldown` | ON-debounce cooldown timer |
| `timer.<slug>_actions_soft_off` | **v3** — drives 15 s soft-off dim warning |
| `timer.<slug>_actions_lights_verify` | **v3** — drives post-off verify/retry delay |
| `timer.<slug>_actions_fan_runon` | Fan run-on countdown timer |
| `timer.<slug>_actions_fan_on_delay` | **v3** — drives fan on-delay without blocking |
| `input_number.<slug>_actions_brightness_day_pct` | Day brightness % |
| `input_number.<slug>_actions_brightness_night_pct` | Night brightness % |
| `input_number.<slug>_actions_verify_attempts` | **v3** — retry counter for verify cycle |
| `input_number.<slug>_actions_fan_pct_day` | Fan speed % day |
| `input_number.<slug>_actions_fan_pct_night` | Fan speed % night |
| `input_number.<slug>_actions_fan_runon_minutes` | Fan run-on duration |
| `input_number.<slug>_actions_fan_on_delay_seconds` | Fan ON delay |
| `input_datetime.<slug>_actions_night_start` | Night window start |
| `input_datetime.<slug>_actions_night_end` | Night window end |
| `binary_sensor.<slug>_actions_cooldown_active` | Cooldown active indicator |
| `binary_sensor.<slug>_actions_soft_off_active` | **v3** — soft-off dim warning active |
| `binary_sensor.<slug>_actions_lights_verify_active` | **v3** — verify/retry active |
| `binary_sensor.<slug>_actions_fan_runon_active` | Fan run-on active indicator |
| `binary_sensor.<slug>_actions_fan_on_delay_active` | **v3** — fan on-delay active |
| `binary_sensor.<slug>_actions_in_night_window` | Night window indicator |

Load packages with:

```yaml
homeassistant:
  packages: !include_dir_merge_named packages/
```

---

## 3. Generator Script

**File:** `assign_areas.py` (generated — see `rooms.yaml`)

Generates per-room helper package YAML files from the template using `rooms.yaml`.
Does **not** generate automations — those are created from blueprints in the HA UI.

---

## 4. Typical Setup Flow

1. Run `witb_plus/v4` blueprint for the room to get `binary_sensor.<slug>_occupied_effective`.
2. Generate helpers via the script and reload/restart HA so all helpers exist.
3. Create an automation from **V3 WITB+ Actions - Lights + Fan** and wire:
   - `occupied_effective` → `binary_sensor.<slug>_occupied_effective`
   - `auto_tag_lights` → `input_boolean.<slug>_auto_lights_on`
   - `auto_tag_fan` → `input_boolean.<slug>_auto_fan_on`
   - `cooldown_timer` → `timer.<slug>_actions_cooldown`
   - `soft_off_timer` → `timer.<slug>_actions_soft_off`
   - `lights_verify_timer` → `timer.<slug>_actions_lights_verify`
   - `fan_runon_timer` → `timer.<slug>_actions_fan_runon`
   - `fan_on_delay_timer` → `timer.<slug>_actions_fan_on_delay`
   - `verify_attempts` → `input_number.<slug>_actions_verify_attempts`
   - `night_start_helper` / `night_end_helper` → corresponding `input_datetime` helpers
   - Brightness and fan % helpers → corresponding `input_number` helpers
   - `light_gating_entity` → your external lux/sun gate sensor (optional)
   - `fan_vacancy_gate_entity` → your external humidity gate sensor (optional)
4. Verify in Developer Tools → Template that the `occupied_effective` sensor
   transitions correctly before testing lights/fan behavior.

---

## 5. Architecture Notes

**Why two blueprints (occupancy + actions)?**
WITB+ deliberately separates *occupancy inference* (WITB+ v4) from *action
orchestration* (Actions). This allows multiple action automations to subscribe
to the same occupancy sensor independently, and keeps each blueprint focused on
one concern.

**Why fully event-driven in v3?**
v2 used blocking `delay:` steps for soft-off, verify, and fan on-delay. With
`mode:restart`, any mid-sequence kill lost the cleanup work. v3 replaces all
blocking delays with dedicated timers — each timer expiry fires a new automation
run that completes in milliseconds. The result: `mode:restart` is safe across all
paths and the cleanup blueprint is demoted from primary safety net to belt-and-suspenders.

**Why external gating?**
Lux evaluation and humidity hold logic are handled in dedicated automations that
write their verdict to a binary sensor. This keeps Actions simple and testable —
you can force the gate ON/OFF manually in the UI to test lighting behavior
independently of ambient conditions.

---

## Summary

| Blueprint | Role | Instance count |
|---|---|---|
| `witb_plus/v4` | Occupancy inference | One per room |
| `witb_plus_actions_lights_fan` | Light + fan control | One per room |
| `witb_plus_actions_lights` | Light-only control | One per room (no fan) |
| `witb_plus_actions_cleanup` | Tag stuck-ON recovery (optional) | One per room |

## v3 vs v2 Helper Differences

New helpers added in v3 (must regenerate packages from v3 template):

| New Helper | Replaces |
|---|---|
| `timer.<slug>_actions_soft_off` | blocking `delay: 15s` in soft-off sequence |
| `timer.<slug>_actions_lights_verify` | blocking `delay:` in verify/retry loop |
| `timer.<slug>_actions_fan_on_delay` | blocking `delay:` for fan on-delay |
| `input_number.<slug>_actions_verify_attempts` | in-memory counter (lost on restart) |
