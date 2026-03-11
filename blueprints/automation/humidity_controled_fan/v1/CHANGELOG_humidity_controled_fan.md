# CHANGELOG — Humidity Controlled Fan

---

## humidity_controled_fan.yaml

### v1.1.0 — 2026-03-10

#### New features

- **Night mode** (`night_mode_enabled`, `night_start`, `night_end`).
  When enabled, the fan will not turn ON during the configured quiet window.
  The fan can still turn OFF during night hours — this is intentional, because
  if a shower ran right before the window started you want the fan to finish
  clearing the room rather than get stuck on until morning.
  Supports overnight spans (e.g. 22:00 → 07:00) via the standard
  `s ≤ e` / `s > e` comparison pattern.

- **HA restart guard** (`ha_start_allow_turn_on`).
  The `ha_start` branch previously could turn the fan ON if humidity was
  already elevated at restart time. This is now disabled by default — only a
  turn-OFF correction fires automatically. Set `ha_start_allow_turn_on: true`
  to restore the previous behaviour. Night mode is respected even when
  `ha_start_allow_turn_on` is enabled.

#### Implementation notes

- Added top-level `variables:` block to capture blueprint boolean/time inputs
  under readable names (`_night_mode`, `_night_start`, `_night_end`,
  `_ha_start_allow_turn_on`). These are plain scalar captures — no `now()`
  calls — so they are safe at automation-load scope.
- `_in_night_window` is computed as an **action-step variable** (first step
  in `actions:`) so `now()` is always evaluated fresh per run, not once at
  load time.
- The `ha_start` branch **re-evaluates the night window inline** (after the
  30-second settling delay) via a template condition rather than relying on
  the earlier `_in_night_window` value. This ensures a restart at e.g. 21:59
  that takes 30 seconds to settle cannot accidentally turn the fan on at 22:00.

---

### v1.0.2 — 2026-02-26

#### Bug fixes
- **Removed duplicate condition in `turn_off` branch.** The branch previously
  checked `state: "on"` twice — once bare and once with `for: seconds:
  min_run_seconds`. The bare check was entirely redundant (the timed check
  already implies the current state) and has been removed.

#### Changes
- **Lowered `min_version` from `2026.3.0` to `2023.4.0`.** The features used
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

## humidity_controled_fan_package_template.yaml

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
