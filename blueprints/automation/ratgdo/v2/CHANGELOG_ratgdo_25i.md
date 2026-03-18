# CHANGELOG — ratgdo_25i

All notable changes to `ratgdo_25i.yaml` are documented here.
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [2.2.0] — Unreleased

### Changed
- `trigger:` / `action:` singular keys updated to `triggers:` / `actions:`
  plural syntax to eliminate deprecation warnings on HA 2024.6.0+. (Issue #1)
- `optional_entities` input section renamed to `optional_settings` for
  consistency with other blueprints in this repo. `notify_group` is a text
  input, not an entity — the old section name was misleading. (Issue #3)
- `source_url` updated to reference renamed file `ratgdo_25i.yaml`. (Issue #6)
- `description` field corrected to reference `CHANGELOG_ratgdo_25i.md`
  instead of `CHANGELOG_ratgdo_v2.md`. (Issue #2)
- Blueprint `name` field version bumped to `2.2.0`.

### Added
- `icon: mdi:garage` on `required_entities` section. (Issue #4)
- `icon: mdi:tune` on `optional_settings` section. (Issue #4)

### Fixed
- Redundant `timer.cancel` removed before `timer.start` in the obstruction
  `else` branch inside `timer_done`. The timer is already in `idle` state
  when `timer.finished` fires — the cancel was a no-op. (Issue #5)

### File rename
- `ratgdo_2_5i.yaml` → `ratgdo_25i.yaml` per NAMING.md slug rules: dots are
  stripped from slugs (`[a-z0-9_]` only), so "Ratgdo 2.5i" → `ratgdo_25i`.
  All companion doc filenames updated accordingly. (Issue #6)

---

## [2.1.1] — 2026-03-09

### Fixed
- `notify` selector replaced with `text` selector — the `notify` selector
  type is not accepted by all HA versions and caused blueprint import to fail
  with "Unknown selector type notify".

---

## [2.1.0] — 2026-03-09

### Added
- `button_entity` input — optional binary sensor tracking physical button
  presses on the Ratgdo device. When pressed while the door is open and the
  auto-close timer is active, cancels the timer for that session only.
  Auto-close resumes normally the next time the door opens.
- `tag-ratgdo-button` notification tag for button session-cancel events.

---

## [2.0.0] — 2026-03-09

Complete rewrite. Scope reduced to door mechanics only.

### Added
- Bypass notification — when auto-close timer expires but `bypass_helper` is
  `on`, sends a notification and restarts the timer instead of silently doing
  nothing.
- Obstruction notification on the `obstruction_found` trigger path (previously
  only notified via the timer-done path).
- Obstruction notification on the `timer_done` path when obstruction blocks
  auto-close.
- `notify:` selector for `notify_group` input — validated in the HA UI, no
  free-text typo risk.

### Changed
- All optional entity inputs now default to `[]` instead of sentinel strings
  (`timer.none`, `input_boolean.none`, `light.none`). Guards use
  `| length > 0` throughout.
- `notify_group` guard changed from `notify_group is defined` (always true
  for a declared variable) to `notify_group | length > 0`.
- `now().strftime('%H:%M')` replaces `states('sensor.time')` — no helper
  entity dependency.
- Cover state guard corrected: `'on'` removed, only `'open'` and `'opening'`
  used (valid cover states).
- `source_url` corrected to point to raw GitHub URL for direct HA import.
- Blueprint name typo fixed: "Ratdgo" → "Ratgdo".
- `min_version` corrected to `2024.6.0`.
- Removed all unnecessary `metadata: {}` and empty `data: {}` from action
  sequences.

### Removed
- `light_bulbs` input — light control delegated to WITB+ Actions (Garage
  instance).
- `light_switch` input — light control delegated to WITB+ Actions (Garage
  instance).
- `light.turn_on` / `homeassistant.turn_on` calls — no longer in scope.

### Fixed
- `light.turn_on` called on `switch` domain entities (bug in v1.x —
  `light_switch` accepted switch domain but always called `light.turn_on`).
- `bypass_helper` was declared as an input and variable but never referenced
  in any action sequence.
- `notify_group is defined` condition was always `true` because the variable
  was always declared, causing broken `notify.` service calls when left empty.

---

## [1.0.0] — legacy

Initial version. Combined door mechanics, light control, and occupancy in a
single blueprint.

### Known issues (resolved in 2.0.0)
- `notify_group is defined` always evaluates true — notifications fire even
  with empty input.
- `bypass_helper` declared but never used in action sequences.
- `light.turn_on` called on entities that may be in the `switch` domain.
- Invalid cover state `'on'` used in guards — never matches.
- Optional entity defaults used sentinel strings (`timer.none`, `light.none`,
  `input_boolean.none`) requiring fragile string comparison guards.
- `sensor.time` dependency for timestamps.
- `source_url` pointed to GitHub blob viewer instead of raw URL.
- Blueprint name typo: "Ratdgo".
- `min_version: 2025.6.0` — incorrect future version, prevented loading on
  current HA installs.
