# CHANGELOG — generate_witb_packages_templated.py

## v4.1 — Flat-template area extraction fix

### Bug fixes

- **BUG #13** — `extract_inner_if_single_package()` misidentified HA platform section
  keys (`input_boolean`, `input_number`, `template`, etc.) as package wrapper keys when
  templates start directly with an HA section rather than a custom package key
  (e.g. `room_slug_witb:`). This caused `input_boolean:` to be stripped entirely from
  lux/humidity generated packages, breaking area extraction — all entity lists came back
  empty, producing `"Note: No area assignments to write"`. Fixed by checking the detected
  wrapper key against `_HA_SECTIONS` and returning the template unchanged if it matches.

---

## v4.0 — Per-room custom tokens

### New features

- **NEW #8** — `Room` dataclass now carries `tokens: dict[str, str]` for arbitrary
  per-room substitutions (e.g. `__HUMIDITY_SENSOR__`, `__FAN_ENTITY__`, `__LUX_SENSOR__`).
  Tokens are defined under a `tokens:` key in the per-room config dict and applied by
  `apply_tokens()` after the standard slug/name substitutions. Token keys are substituted
  literally as written, so use whatever delimiter the template uses.

  These tokens exist specifically for entity references that live **outside** the generated
  package — physical device sensors and switches assigned by HA at device integration time
  that cannot be derived from `room_slug` alone.

- **NEW #9** — `apply_tokens()` warns on stderr if any `__TOKEN__` placeholders remain
  unsubstituted after all passes, identifying the room and token names. Prevents silently
  broken HA config when a `tokens:` entry is missing from `rooms.yaml`.

---

## v3.0 — Area assignment support

### New features

- **NEW #5** — `Room` dataclass now carries `area` (friendly name) and `area_id`
  (HA slug, auto-derived from `area` via `slugify()` if not explicitly set).

- **NEW #6** — `build_room()` parses `area:` and optional `area_id:` from per-room
  config dicts.

- **NEW #7** — `--areas-script` flag emits a standalone `assign_areas.py` that calls the
  HA WebSocket API to assign areas to all helpers. Entity list per room respects each
  room's active feature flags so disabled-block entities are never included.

- **NEW #7b** — `areas_script` can be set in `rooms.yaml` so the `--areas-script` CLI
  flag is never needed.

### Bug fixes

- **BUG #10** — `assign_areas.py` used a GET pre-check that silently failed for
  YAML-defined helpers, causing all entities to be SKIPped. Removed.

- **BUG #11** — `assign_areas.py` gave no detail on PATCH failures. Now shows HTTP status
  and response body on failure.

- **BUG #12** — `assign_areas.py` assumed areas already existed in HA. Now checks the
  area registry first and creates any missing areas automatically.

---

## v2.0 — Auto-discovery + multi-template hardening

### New features

- **NEW #1** — Feature blocks are now **auto-discovered** from the template file at startup
  by scanning for `# --- BEGIN X ---` markers. The static `_STATIC_FEATURES` list is kept
  as a fallback/documentation artifact but is no longer the sole source of `--no-X` CLI
  flags. Any new template block name is picked up automatically without editing this script.

- **NEW #2** — `apply_tokens()` now handles both token styles:
  - `"Room Friendly Name"` — witb_plus / witb_actions / humidity templates
  - `"Friendly Name"` — transit template (no "Room" prefix)

  First pass replaces `"Room Friendly Name"` → `room.name`; second pass replaces any
  remaining bare `"Friendly Name"` → `room.name` so transit templates work without
  modification.

- **NEW #3** — `remove_empty_section()` now covers all HA platform section headers,
  including `input_text` (transit) and `counter` (vacuum) which were previously unhandled,
  leaving bare section keys in the output.

- **NEW #4** — `extract_inner_if_single_package()` de-indents by the **actual** wrapper
  indentation width instead of hard-coding 2 spaces. Wrapper blocks indented by 4 spaces
  (or any other depth) now unwrap correctly.

### Bug fixes

- **BUG #1** — `input_number` missing from `remove_empty_section` cleanup list. Fixed.
- **BUG #2** — Config `emit_X` overrode CLI `--no-X` flags. CLI now wins.
- **BUG #3** — No duplicate slug detection. Added.
- **BUG #4** — `slugify()` matched Unicode word chars. Fixed with `re.ASCII`.
- **BUG #5** — Dead-code regex in `apply_tokens()`. Removed.
- **BUG #6** — No `--dry-run` mode. Added.
- **BUG #7** — No existence check on `--template` path. Added.
- **BUG #8** — Redundant dual override syntax. Unified to `no_X` per-room.
- **BUG #9** — `remove_empty_section` used `DOTALL`, ate real content. Fixed.

---

## v1.0 — Initial release

Template-driven generator for HA `merge_named` packages. Supports per-room feature flag
overrides via config file, `# --- BEGIN X --- / # --- END X ---` block stripping, and
standard `room_slug` / `"Room Friendly Name"` token substitution.
