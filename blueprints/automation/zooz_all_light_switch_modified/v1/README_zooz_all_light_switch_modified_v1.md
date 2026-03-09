# Zooz All Light Switch (Modified) — v1

Z-Wave Plus 700/800 Series S2 ZEN71/72/76/77 switch button blueprint.

**Source:** [`zooz-all.yaml`](zooz-all.yaml)
**Domain:** automation
**Mode:** single

---

## Overview

Maps physical button presses on Zooz ZEN71, ZEN72, ZEN76, and ZEN77 switches/dimmers to configurable actions. Supports 1x–5x press and held events on both the Up (On) and Down (Off) paddles.

Optionally integrates with WITB+ light profiles via ON/OFF hook scripts — when a hook script is configured, the 1x press routes to the script instead of the raw action input.

---

## Supported Devices

| Model | Type |
|---|---|
| ZEN71 / ZEN71 800LR | On/Off Switch |
| ZEN72 / ZEN72 800LR | Dimmer |
| ZEN76 / ZEN76 800LR | On/Off Switch |
| ZEN77 / ZEN77 800LR | Dimmer |

Multiple devices can be selected in a single blueprint instance.

---

## Inputs

### Device

| Input | Description |
|---|---|
| `zooz-switch` | One or more Zooz switch/dimmer devices (Z-Wave JS integration) |

### Hook Scripts (optional)

| Input | Description |
|---|---|
| `on_hook_script` | WITB Lights ON Hook script. When set, Up/On 1x press calls this script instead of `button_a` |
| `off_hook_script` | WITB Lights OFF Hook script. When set, Down/Off 1x press calls this script instead of `button_b` |

### Button Actions

| Input | Trigger |
|---|---|
| `button_a` | Up/On 1x press (skipped if `on_hook_script` set) |
| `button_a2` – `button_a5` | Up/On 2x–5x press |
| `button_a_held` | Up/On held down |
| `button_b` | Down/Off 1x press (skipped if `off_hook_script` set) |
| `button_b2` – `button_b5` | Down/Off 2x–5x press |
| `button_b_held` | Down/Off held down |

---

## Architecture Notes

Uses `zwave_js_value_notification` events filtered by `device_id`. All button inputs default to empty (`[]`) so unused press counts are silently ignored.

Hook scripts take priority over raw action inputs for 1x presses, allowing WITB+ light profiles to manage brightness and transitions without modifying the switch blueprint.
