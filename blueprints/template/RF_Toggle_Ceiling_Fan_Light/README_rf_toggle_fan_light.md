# RF Toggle Ceiling Fan Light — Template Blueprint

**Version:** v1.0.0  
**Domain:** `template` (light entity)  
**Blueprint path:** `config/blueprints/template/local/rf_toggle_fan_light.yaml`  
**See:** `CHANGELOG_rf_toggle_fan_light.md`

---

## Overview

Creates a HA `light` entity for ceiling fan lights that are controlled by an RF remote with a **single toggle button** — no discrete on/off codes. The blueprint wraps the raw RF transmission in a toggle guard so HA-driven calls are idempotent: the RF signal is only transmitted when the tracked state actually needs to change.

Designed for use alongside the WITB+ Actions blueprint. Pass the generated `light.{room}_ceiling_fan_light` entity to the `lights` input as normal.

---

## How it works

### Toggle guard

Because the remote is toggle-only, sending the RF command when the light is already in the desired state would flip it the wrong way. Each `turn_on` and `turn_off` action starts with a condition check against the companion `input_number` helper:

- `turn_on` only transmits if `brightness_helper == 0` (light is currently tracked as off)
- `turn_off` only transmits if `brightness_helper > 0` (light is currently tracked as on)

This makes repeated HA calls safe — calling `turn_on` twice in a row will only send the RF signal once.

### Action ordering

RF command fires **before** `input_number.set_value`. This means the physical light changes state before HA's tracked state updates. If the sequence is interrupted, HA's state lags behind reality rather than running ahead of it, which is the safer failure mode.

### State drift

Physical remote use will still cause drift between the `input_number` and the actual light state. There is no feedback mechanism to detect this. The toggle guard and ordering fix prevent HA from making drift worse on its own, but they cannot self-correct after a physical button press.

---

## Prerequisites

For each fan room:

1. **Create a companion `input_number` helper** in HA with the following settings:
   - Range: `0` to `100`
   - Step: `1`
   - Suggested entity ID: `input_number.{room}_ceiling_fan_light_brightness`
2. **Capture the RF command** from your fan remote using ESPHome RF raw receiver. Since the remote is toggle-only, one capture is sufficient — the same command is used for both on and off.

---

## Blueprint inputs

| Input | Type | Description |
|---|---|---|
| `brightness_helper` | `entity: input_number` | Tracks the light's on/off state. `0` = off, `100` = on. |
| `esphome_service` | `text` | The ESPHome action name for RF transmission. Example: `esphome.master_bedroom_esp360_remote_send_rf_raw` |
| `rf_command` | `object` | The RF raw integer list captured from your remote. |

---

## Installation

1. Copy `rf_toggle_fan_light.yaml` to `config/blueprints/template/local/`
2. For each fan room, create the `input_number` helper (see Prerequisites)
3. Add a `use_blueprint` block to your `template:` config for each room (see Usage)
4. Reload template entities: **Settings → Developer Tools → YAML → Template entities**

---

## Usage

Add one block per fan room to your `template:` config section (or an included template file):

```yaml
template:
  - use_blueprint:
      path: local/rf_toggle_fan_light.yaml
      input:
        brightness_helper: input_number.master_bedroom_ceiling_fan_light_brightness
        esphome_service: esphome.master_bedroom_esp360_remote_send_rf_raw
        rf_command:
          - 278
          - -3358
          - 878
          # ... full command list
    name: Master Bedroom Ceiling Fan Light
    unique_id: master_bedroom_ceiling_fan_light
```

Repeat for each room, substituting the room-specific `brightness_helper`, `esphome_service`, and `rf_command`.

---

## Integration with WITB+ Actions

Pass the template light entity to the WITB+ Actions blueprint as normal:

```yaml
lights:
  - light.master_bedroom_ceiling_fan_light
```

Recommended WITB+ Actions settings for toggle-only lights:

| Setting | Value | Reason |
|---|---|---|
| `skip_on_if_any_light_on` | `true` | Prevents blueprint from calling `turn_on` on an already-on light, which would toggle it off |
| `auto_tag_lights` | `input_boolean.{room}_auto_lights_on` | Required for `manual_off_hold` detection to work correctly |

---

## Limitations

- **No dimming.** The fan light is binary (on/off only). The `level` field in the template light always reflects `0` or `100`. The `brightness_pct` parameter sent by WITB+ Actions is accepted by HA but has no physical effect.
- **No drift correction.** Physical remote use desynchronises HA state from reality. No automatic correction mechanism exists.
- **Single RF code.** Turn-on and turn-off use the same RF command. If your remote is upgraded to support discrete codes in the future, each action should use its own captured command and the toggle guard conditions can be removed.

---

## File structure

```
config/
  blueprints/
    template/
      local/
        rf_toggle_fan_light.yaml        # Blueprint definition
  packages/
    {room}/
      {room}_fan_light.yaml             # use_blueprint instance per room (generated or hand-authored)
CHANGELOG_rf_toggle_fan_light.md
README_rf_toggle_fan_light.md
```
