# Changelog — Ratgdo 2.5i Blueprint

All notable changes to this blueprint are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [2.1.1] — 2026-03-09

### Fixed
- `notify` selector replaced with `text` selector — the `notify` selector type is not accepted by all HA versions and caused blueprint import to fail with "Unknown selector type notify".

---

## [2.1.0] — 2026-03-09

### Added
- `button_entity` input — optional binary sensor tracking physical button presses on the Ratgdo device. When pressed while the door is open and the auto-close timer is active, cancels the timer for that session only. Auto-close resumes normally the next time the door opens.
- `tag-ratgdo-button` notification tag for button session-cancel events.

---

## [2.0.0] — 2026-03-09

Complete rewrite. Scope reduced to door mechanics only.

### Added
- Bypass notification — when auto-close timer expires but `bypass_helper` is `on`, sends a notification and restarts the timer instead of silently doing nothing.
- Obstruction notification on the `obstruction_found` trigger path (previously only notified via the timer-done path).
- Obstruction notification on the `timer_done` path when obstruction blocks auto-close.
- `notify:` selector for `notify_group` input — validated in the HA UI, no free-text typo risk.

### Changed
- All optional entity inputs now default to `[]` instead of sentinel strings (`timer.none`, `input_boolean.none`, `light.none`). Guards use `| length > 0` throughout.
- `notify_group` guard changed from `notify_group is defined` (always true for a declared variable) to `notify_group | length > 0`.
- `now().strftime('%H:%M')` replaces `states('sensor.time')` — no helper entity dependency.
- Cover state guard corrected: `'on'` removed, only `'open'` and `'opening'` used (valid cover states).
- `source_url` corrected to point to raw GitHub URL for direct HA import.
- Blueprint name typo fixed: "Ratdgo" → "Ratgdo".
- `min_version` corrected to `2024.6.0`.
- Removed all unnecessary `metadata: {}` and empty `data: {}` from action sequences.

### Removed
- `light_bulbs` input — light control delegated to WITB+ Actions (Garage instance).
- `light_switch` input — light control delegated to WITB+ Actions (Garage instance).
- `light.turn_on` / `homeassistant.turn_on` calls — no longer in scope.

### Fixed
- `light.turn_on` called on `switch` domain entities (bug in v1.x — `light_switch` accepted switch domain but always called `light.turn_on`).
- `bypass_helper` was declared as an input and variable but never referenced in any action sequence.
- `notify_group is defined` condition was always `true` because the variable was always declared, causing broken `notify.` service calls when left empty.

---

## [1.0.0] — legacy

Initial version. Combined door mechanics, light control, and occupancy in a single blueprint.

### Known Issues (resolved in 2.0.0)
- `notify_group is defined` always evaluates true — notifications fire even with empty input.
- `bypass_helper` declared but never used in action sequences.
- `light.turn_on` called on entities that may be in the `switch` domain.
- Invalid cover state `'on'` used in guards — never matches.
- Optional entity defaults used sentinel strings (`timer.none`, `light.none`, `input_boolean.none`) requiring fragile string comparison guards.
- `sensor.time` dependency for timestamps.
- `source_url` pointed to GitHub blob viewer instead of raw URL.
- Blueprint name typo: "Ratdgo".
- `min_version: 2025.6.0` — incorrect future version, prevented loading on current HA installs.
