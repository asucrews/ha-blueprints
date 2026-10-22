# WITB Transit Room Examples

## v2 (current)

Blueprint source:
- `blueprints/automation/witb_transit_room/v2/witb_transit_room.yaml`

Files:
- `stairs_automation.yaml` — Transit Room v2 automation instance for stairs.
- `packages/stairs.yaml` — generated v2 core package.
- `packages/stairs_actions.yaml` — generated WITB Actions V3 helper package (lights only).
- `rooms_stairs_actions.example.yaml` — generator config for the Actions package. The v2 core config lives next
  to its template: `blueprints/automation/witb_transit_room/v2/rooms.yaml`.

How to use:
1. Copy the two packages into your packages directory (loaded with `!include_dir_merge_named`).
2. Restart Home Assistant so the new helpers exist.
3. Copy `stairs_automation.yaml`, update `use_blueprint.path` and entity IDs.
4. Point a WITB Actions V3 automation at `binary_sensor.stairs_occupied_effective`.

See `packages/README.md` for details.

## v1 (legacy)

Blueprint source:
- `blueprints/automation/witb_transit_room/v1/witb_transit_room.yaml`

Files (v1 only):
- `hallway_automation.yaml` — v1 automation example.
- `rooms_transit.example.yaml` — v1 generator config.

Notes for v1:
- The dummy keepalive and instant-off booleans are required by the blueprint even if those features are unused.
- The suppress timer is required even if `instant_off_rearm_timeout_seconds` is `0`.
- v1 drives `input_boolean.<slug>_occupied_effective`, which WITB Actions V3 cannot consume (it needs a `binary_sensor`).
