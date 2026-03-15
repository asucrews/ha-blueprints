# README — air_purifier v1

**Blueprint:** `air_purifier.yaml`
**Version:** 1.0.0 (see `CHANGELOG_air_purifier.md`)
**Domain:** automation
**Path:** `blueprints/automation/air_purifier/v1/air_purifier.yaml`
**Min HA version:** 2026.1.0

---

## Overview

Keeps a group of air purifiers synchronized to a twice-daily boost schedule.
During configured boost windows the purifiers run at full (or configurable)
speed. Outside those windows they return to a preset mode (default: `auto`).
A 5-minute reconciler and an HA-restart guard ensure devices stay in the
correct state even after power loss, connectivity drops, or manual overrides.

---

## Inputs

| Input | Type | Default | Description |
|---|---|---|---|
| `purifier_entities` | `fan` (multiple) | — | Air purifier entities to manage as a group |
| `first_start_time` | time | `09:00:00` | Start of first daily boost window |
| `first_end_time` | time | `09:40:00` | End of first daily boost window |
| `second_start_time` | time | `21:00:00` | Start of second daily boost window |
| `second_end_time` | time | `21:40:00` | End of second daily boost window |
| `boost_percentage` | number (1–100) | `100` | Fan speed during boost windows |
| `return_preset_mode` | text | `auto` | Preset mode to restore outside boost windows |

---

## Triggers

| Trigger | Purpose |
|---|---|
| `time` at all four window boundaries | Instant transition at window start and end |
| `time_pattern` every 5 minutes | Periodic reconcile — heals drift and missed commands |
| `homeassistant: start` | Applies correct state immediately after HA restart |

---

## Architecture notes

- **Two-step `variables:` pattern** — top-level block aliases all `!input` values;
  action-level step performs Jinja2 computation. This is required because `!input`
  tags are resolved at YAML parse time and cannot be embedded inside Jinja2
  template strings.
- **Timezone-safe time comparison** — uses `now().strftime('%H:%M:%S')` string
  comparison instead of `today_at()` to avoid `TypeError` from mixing naive and
  timezone-aware datetimes.
- **No-op guards** — service calls are skipped if the device is already at the
  target state, preventing unnecessary Zigbee/Z-Wave traffic and log spam.
- **`| int(-1)` sentinel** — safely handles entities that are off or unavailable
  when reading the `percentage` attribute.

---

## Known limitations

- **Midnight-spanning windows not supported.** Both start and end times for each
  window must fall on the same calendar day. See `rules_air_purifier.md` rule 7.
- **v1.0.0 only:** No `is_on` guard — a purifier manually turned off inside a
  boost window will be unintentionally powered on by the next reconcile tick.
  Fixed in v1.1.0.

---

## Files in this directory

| File | Purpose |
|---|---|
| `air_purifier.yaml` | Blueprint |
| `CHANGELOG_air_purifier.md` | Version history |
| `rules_air_purifier.md` | Behavioral rules and invariants |
| `use_cases_air_purifier.md` | Supported use cases with pass/fail outcomes |

---

## Related docs

- `docs/blueprints/air_purifier.md` — implementation guide and example config
