# Changelog — RF Toggle Ceiling Fan Light Blueprint

## v1.0.0 — 2026-03-13

Initial release.

### Added
- Template light blueprint for RF-controlled ceiling fan lights with toggle-only remotes
- Toggle guard on `turn_on`: RF signal is only transmitted when `brightness_helper` reports `0`, preventing double-toggle if HA calls `turn_on` on an already-on light
- Toggle guard on `turn_off`: RF signal is only transmitted when `brightness_helper` reports `> 0`, same rationale
- Correct action ordering: RF command fires before `input_number.set_value` so physical state changes before HA state updates — prevents state drift on interrupted sequences
- Three blueprint inputs: `brightness_helper` (entity selector), `esphome_service` (text), `rf_command` (object)
- `!input` substitution at instantiation time for both `esphome_service` and `rf_command` — no runtime Jinja2 evaluation needed
- `level` template reads from `brightness_helper` so HA reports brightness correctly
- `state` template derived from `brightness_helper` — light is `on` when value > 0
