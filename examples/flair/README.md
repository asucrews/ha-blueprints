# Flair Smart Vent Examples

Blueprint source:
- `blueprints/automation/flair/v1/flair.yaml`

## Files

- `flair_automation.yaml`

## How To Use

1. Copy `flair_automation.yaml` once per room that has a Flair vent and update:
   - `use_blueprint.path` with your namespace
   - `occupied_effective` — `binary_sensor.<room_slug>_occupied_effective` from your WITB+ package
   - `flair_activity_status` — the Flair activity select entity for the room
   - `flair_clear_hold` — the Flair clear hold button entity for the room
2. Update `id` and `alias` for each room instance (e.g. `flair_v1_living_room`).
3. Paste into your `automations.yaml` or HA YAML editor.
