# WITB+ Actions (Lights + Fan)

This folder contains the **actions blueprint** that pairs with WITB+ occupancy.

Use this when you already have room occupancy sensors from `witb_plus/v4` (for example
`binary_sensor.<slug>_occupied_effective`) and want reliable light/fan actions with
safety tags, external gating, and automatic tag cleanup.

---

## 1. Blueprints

### `witb_plus_actions_lights_fan.yaml` — main actions blueprint (v2.3.3)

Controls lights and fan for a single room based on occupancy state changes from
`binary_sensor.<slug>_occupied_effective`. Key behaviors:

- **Lights ON/OFF** with day/night brightness profiles and optional soft-off dim warning.
- **Manual-off hold** — if you turn lights off while occupied they stay off until
  vacancy clears `auto_tag_lights`, then re-arm next occupancy.
- **Bed suppress** — if someone is in bed and lights are off, motion re-assertion
  (e.g. midnight bathroom return) does not turn lights back on.
- **Light gating** — wire an external `binary_sensor` computed from lux, sun
  elevation, curtains, or season. Blueprint does not evaluate these inline.
- **Fan ON on occupancy** with optional delay and night-disable mode.
- **Fan run-on timer** after vacancy, with optional gate to hold the fan on while
  humidity or other conditions require it.
- **Fan vacancy gate** — wire an external `binary_sensor` (e.g. humidity threshold).
  OFF = hold fan on; ON = ok to turn off. When the gate clears while the room is
  already vacant the fan turns off automatically.
- **Auto-tag helpers** (`input_boolean`) track automation ownership of lights and fan
  for safe "only turn off what we turned on" behavior.
- **Startup cleanup** with double-tap validation after HA restart.

### `witb_plus_actions_cleanup.yaml` — tag cleanup blueprint (v1.0.0)

Belt-and-suspenders companion that catches `auto_tag_lights` and `auto_tag_fan`
helpers stuck ON after a `mode:restart` kill mid-sequence in the main automation.
Deploy **one instance per room** alongside the main Actions instance.

- Two independent soak timers fire after vacancy: lights check (default 5 min),
  fan check (default 20 min).
- Lights tag only cleared when all controlled lights are confirmed OFF.
- Fan tag never cleared while `fan_runon_timer` is active.
- Both checks re-confirm vacancy at evaluation time.
- Inputs mirror the main Actions instance — wire the same entities.

See `CHANGELOG_witb_plus_actions_lights_fan.md` for full fix rationale.

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
| `timer.<slug>_actions_fan_runon` | Fan run-on countdown timer |
| `input_datetime.<slug>_actions_night_start` | Night window start |
| `input_datetime.<slug>_actions_night_end` | Night window end |
| `input_number.<slug>_actions_brightness_day_pct` | Day brightness % |
| `input_number.<slug>_actions_brightness_night_pct` | Night brightness % |
| `input_number.<slug>_actions_fan_pct_day` | Fan speed % day |
| `input_number.<slug>_actions_fan_pct_night` | Fan speed % night |
| `input_number.<slug>_actions_fan_runon_minutes` | Fan run-on duration |
| `input_number.<slug>_actions_fan_on_delay_seconds` | Fan ON delay |
| `binary_sensor.<slug>_actions_cooldown_active` | Cooldown active indicator |
| `binary_sensor.<slug>_actions_fan_runon_active` | Fan run-on active indicator |
| `binary_sensor.<slug>_actions_in_night_window` | Night window indicator |

Load packages with:

```yaml
homeassistant:
  packages: !include_dir_merge_named packages/
```

---

## 3. Generator Script

**File:** `blueprints/generate_witb_packages_templated.py`

Generates per-room helper package YAML files from the template. Does **not**
generate automations — those are created from blueprints in the HA UI.

```bash
# Generate packages for specific rooms
python blueprints/generate_witb_packages_templated.py \
  --rooms "Office" "Master Bathroom Toilet" \
  --template witb_plus_actions_lights_fan_package_template.yaml \
  --out ./packages

# Dry run to preview output
python blueprints/generate_witb_packages_templated.py \
  --rooms "Office" \
  --template witb_plus_actions_lights_fan_package_template.yaml \
  --out ./packages \
  --dry-run
```

---

## 4. Typical Setup Flow

1. Run `witb_plus/v4` blueprint for the room to get `binary_sensor.<slug>_occupied_effective`.
2. Generate helpers via the script and reload/restart HA so all helpers exist.
3. Create an automation from **WITB+ Actions - Lights + Fan** and wire:
   - `occupied_effective` → `binary_sensor.<slug>_occupied_effective`
   - `auto_tag_lights` → `input_boolean.<slug>_auto_lights_on`
   - `auto_tag_fan` → `input_boolean.<slug>_auto_fan_on`
   - `cooldown_timer` → `timer.<slug>_actions_cooldown`
   - `fan_runon_timer` → `timer.<slug>_actions_fan_runon`
   - `night_start_helper` / `night_end_helper` → corresponding `input_datetime` helpers
   - Brightness and fan % helpers → corresponding `input_number` helpers
   - `light_gating_entity` → your external lux/sun gate sensor (optional)
   - `fan_vacancy_gate_entity` → your external humidity gate sensor (optional)
4. Create a second automation from **WITB+ Actions Tag Cleanup** for the same room,
   wiring the same lights, fan, tags, and timers. Use `mode: single`.
5. Verify in Developer Tools → Template that the `occupied_effective` sensor
   transitions correctly before testing lights/fan behavior.

---

## 5. Architecture Notes

**Why two blueprints (occupancy + actions)?**  
WITB+ deliberately separates *occupancy inference* (WITB+ v4) from *action
orchestration* (Actions). This allows multiple action automations to subscribe
to the same occupancy sensor independently, and keeps each blueprint focused on
one concern.

**Why external gating (v2.3.0+)?**  
Lux evaluation and humidity hold logic were removed from the Actions blueprint
in v2.3.0. These belong in dedicated automations that write their verdict to a
binary sensor. This keeps Actions simple and testable — you can force the gate
ON/OFF manually in the UI to test lighting behavior independently of ambient
conditions.

**Why a cleanup blueprint (v2.3.1+)?**  
`mode:restart` is the correct mode for an event-driven automation — it prevents
stale queued runs from accumulating. The tradeoff is that any run killed mid-
sequence cannot clean up after itself. The cleanup blueprint handles this with a
time-delayed soak check that is safe, idempotent, and never turns anything off —
it only clears boolean tags.

---

## Summary

| Blueprint | Role | Instance count |
|---|---|---|
| `witb_plus/v4` | Occupancy inference | One per room |
| `witb_plus_actions_lights_fan` | Light + fan control | One per room |
| `witb_plus_actions_cleanup` | Tag stuck-ON recovery | One per room |
