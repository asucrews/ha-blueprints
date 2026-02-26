# CHANGELOG — WITB+ Bed → Force Occupied

All notable changes to this blueprint are documented here.  
Format: `[version] — date — summary`, followed by itemized changes.

---

## [1.0.0] — 2026-02-26 — Initial release

### Added
- Initial blueprint created.
- Drives `input_boolean` force_occupied helper to keep a room occupied while
  someone is in bed, preventing false vacancy clearances.
- Configurable bed-ON debounce (`bed_on_delay`, default 30s).
- Configurable bathroom grace period (`bathroom_grace`, default 5 min).
- Mandatory safety gate: force_occupied can only extend occupancy, never
  initiate it — requires `occupied_effective` to already be ON on the bed-ON path.
- ESPHome double-delay warning documented in the `bathroom_grace` input description.
