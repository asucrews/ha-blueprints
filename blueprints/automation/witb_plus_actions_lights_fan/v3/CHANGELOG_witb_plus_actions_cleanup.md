# CHANGELOG — WITB+ Actions Tag Cleanup

## [1.0.1] — 2026-10-22 — Optional tag inputs safe when empty

### Fixed

- `auto_tag_lights` and `auto_tag_fan` were used directly as the `entity_id` of a `condition: state`.
  With the documented default (empty), Home Assistant failed validation at load and the automation was
  `unavailable`. A room without a fan (for example the Stairs) could not use the blueprint without a dummy
  fan helper. Both are now `condition: template` checks (`is_state(tag, 'on')`) behind a non-empty guard
  (`has_tag_lights` / `has_tag_fan`). Behaviour when the input is set is unchanged.
- An empty lights tag skips the lights branch and an empty fan tag skips the fan branch.

## [1.0.0]

Initial release: time-delayed soak check that clears stuck `auto_tag_lights` / `auto_tag_fan` helpers.
