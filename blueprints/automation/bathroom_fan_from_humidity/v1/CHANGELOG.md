# Changelog

---

## bathroom_fan_from_humidity_delta.yaml

### v1.0.2 — 2026-02-26

#### Bug fixes
- **Removed duplicate condition in `turn_off` branch.** The branch previously
  checked `state: "on"` twice — once bare and once with `for: seconds:
  min_run_seconds`. The bare check was entirely redundant (the timed check
  already implies the current state) and has been removed.

#### Changes
- **Lowered `min_version` from `2026.2.0` to `2023.4.0`.** The features used
  (trigger `id:`, `choose:`, `numeric_state`, `homeassistant` trigger) have
  been stable since early 2023. The previous value was a future release date
  that blocked installation on all current HA versions.
- **Changed `mode` from `single` to `restart`.** Because each action sequence
  is a single, near-instantaneous service call, `restart` is strictly safer —
  a new trigger will always be acted on rather than silently dropped if the
  automation happened to be mid-run.

#### New features
- **Added `ha_start` trigger (`homeassistant: event: start`).** On HA restart,
  the automation now re-evaluates current conditions after a 30-second settling
  delay and turns the fan on or off as appropriate. This prevents the fan from
  being stuck in the wrong state until the next humidity change.

#### Documentation
- Added `description:` fields to `on_for_seconds`, `off_for_seconds`,
  `min_run_seconds`, and `max_run_seconds` inputs explaining the purpose of
  each debounce/guard parameter.

---

## room_humidity_baseline_delta_package_template.yaml

### v1.1 — 2026-02-26

#### Bug fixes
- **Added `# --- BEGIN tuning_helpers ---` / `# --- END tuning_helpers ---`
  block markers** around the `input_boolean` and `input_number` sections.
  Previously the `--no-tuning-helpers` flag in the generator had no effect
  because the template contained no markers for it to act on — the helper
  entities were always emitted. The flag now correctly omits them. The baseline
  sensor Jinja2 logic is unaffected; it already falls back to hardcoded
  defaults when the helpers are absent.

#### Documentation
- Added version comment (`v1.1`) and a block-marker reference at the top of
  the file.

---

## generate_humidity_packages_templated.py

### v1.1.0 — 2026-02-26

#### New features
- **Added `__version__ = "1.1.0"`** module-level constant.
- **Added `--version` CLI flag** that prints the version string and exits.

#### Changes
- **`--no-tuning-helpers` now works as documented.** The corresponding template
  (`room_humidity_baseline_delta_package_template.yaml` v1.1) now contains the
  required `# --- BEGIN/END tuning_helpers ---` markers. Updated the flag's
  help text to describe this dependency explicitly.
- Improved `argparse` setup: added `formatter_class=RawDescriptionHelpFormatter`
  so the module docstring is preserved when `--help` is invoked.
- Minor style: extracted long string literals in `argparse` calls to improve
  readability; no behaviour changes.
