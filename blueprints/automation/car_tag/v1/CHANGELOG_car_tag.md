# Car Tag Automation Changelog

## [1.6.0] - 2026-03-16

### Added
- New input `garage_door_status_entity` (binary sensor) — clean binary door state: `on` = open, `off` = closed. Typically `binary_sensor.garage_main_door_status` derived from the cover entity via template sensor.

### Changed
- All branch door state checks now use `garage_door_status_entity` instead of multi-value `is_state(garage_door_cover, [...])` checks:
  - Branch 1 & 3 (must be closed to open): `is_state(garage_door_status_entity, 'off')`
  - Branch 2 (must be open to start close timer): `is_state(garage_door_status_entity, 'on')`
- `unavailable` guard retained on `garage_door_cover` (correct entity for that check)

### Root Cause (from trace `2026-03-16T00:02:42`)
Cover entity states (`open`, `opening`, `closing`, `closed`) made closed/open checks ambiguous. Template sensor provides a clean binary signal, eliminating the need for multi-value state lists in conditions.

### Migration
Re-save the automation instance in the UI after deploying to wire up the new `garage_door_status_entity` input.

---

## [1.5.0] - 2026-03-15

### Fixed
- **Branch 1 (BLE Found):** Removed `person not_home` gate. Car on + door closed = open intent regardless of direction (arriving or departing). Previously blocked UC2 (departing while person still `home`).
- **Branch 3 (WiFi Backup):** Replaced `person not_home AND BLE off` condition with `BLE on OR person not_home`. This correctly handles both UC5 (arriving, BLE missed) and UC6 (departing, car is on when node comes back). UC7 (node bounce, car off) is still blocked naturally since neither condition passes.

### Added
- `rules.md` — formal rule set governing automation behavior
- `use-cases.md` — full list of supported use cases with pass/fail status
- `README.md` — setup and usage documentation

### Root Cause (from trace `2026-03-15T20:40:10`)
Automation triggered via WiFi backup (`binary_sensor.lan_s_esphome_ct_node_status` came online). Reached `choose/2/conditions/3` and failed because `person.lan_nguyen` was `home`. Node had been offline since `05:17:16`, missing the BLE rising edge. WiFi backup branch could not recover the departure because the `not_home` gate blocked it.

### Use Cases Resolved
- UC2 (departing via BLE) ✅
- UC6 (departing via WiFi backup) ✅

---

## [1.4.0] - 2026-01-19

### Added
- WiFi backup trigger supporting both `binary_sensor` and `device_tracker` domains
- Asymmetric debounce (short open delay, long close delay)
- Person entity confirmation gate
- Time-of-day open window (`open_after` / `open_before`)
- Notification target input
- `max_exceeded: silent` to prevent queued duplicate runs

### Notes
- Initial production release
- Ratgdo physical wall button cancel behavior handled by separate Ratgdo blueprint (v2.1.1)
