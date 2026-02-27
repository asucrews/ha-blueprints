# WITB+ Bed → Force Occupied v1

Drives an `input_boolean` `force_occupied` helper so WITB+ keeps a bedroom occupied while someone is in bed — preventing false vacancy clearances and the lights/fan turning off on a sleeping occupant.

## Files

- `witb_plus_bed_force_occupied.yaml` — automation blueprint.
- `CHANGELOG_witb_plus_bed_force_occupied.md` — version history.

## How It Works

| Path | Trigger | Condition | Action |
|---|---|---|---|
| **ON** | Bed sensor ON for `bed_on_delay` (default 30s) | `occupied_effective` must already be ON | Set `force_occupied` ON |
| **OFF** | Bed sensor OFF for `bathroom_grace` (default 5 min) | None (unconditional) | Set `force_occupied` OFF |

**Mandatory safety gate:** `force_occupied` can only *extend* existing occupancy — it can never *initiate* it. This prevents objects on the bed (laundry, pets) from creating occupancy in an empty room.

**Bathroom grace:** covers the "midnight bathroom" scenario — leave the bed briefly and return without triggering a false vacancy cycle.

## ESPHome Double-Delay Warning

If your bed sensor already applies a `delayed_off` in ESPHome (e.g. 5 min) and `bathroom_grace` here is also 5 min, the effective delay before `force_occupied` clears is ~10 min. Enforce the grace in **one place only**:

- **Option A (recommended):** keep ESPHome `delayed_off` short; set the full grace here.
- **Option B:** put the full delay in ESPHome; set `bathroom_grace` to `0s` here.

## Inputs

| Input | Default | Description |
|---|---|---|
| `bed_sensor` | — | Binary sensor detecting in-bed presence (use Normal or Slow variant, not Fast) |
| `occupied_effective` | — | WITB+ effective occupancy sensor (`binary_sensor.<slug>_occupied_effective`) |
| `force_occupied` | — | Force-occupied boolean (`input_boolean.<slug>_force_occupied`) |
| `bed_on_delay` | `00:00:30` | How long bed must be ON before triggering |
| `bathroom_grace` | `00:05:00` | How long bed must be OFF before releasing |

## Pairing with WITB+ Actions v2.2+

- This blueprint drives `force_occupied` (occupancy persistence).
- For the Actions blueprint, use the **Fast** variant of your bed sensor as `bed_occupied` — it handles instant lights-on suppression separately.

## Setup

1. Ensure your WITB+ v4 room has a `force_occupied` input_boolean defined in its helper package.
2. Create an automation from `WITB+ Bed → Force Occupied` in the HA UI.
3. Bind `bed_sensor`, `occupied_effective`, and `force_occupied`.
4. Tune `bed_on_delay` and `bathroom_grace` to match your sensor's ESPHome config.
