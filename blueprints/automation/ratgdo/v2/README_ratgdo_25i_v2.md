# README — ratgdo_25i v2

**Blueprint:** `ratgdo_25i.yaml`
**Version:** 2.2.0 (see `CHANGELOG_ratgdo_25i.md`)
**Domain:** automation
**Path:** `blueprints/automation/ratgdo_25i/v2/ratgdo_25i.yaml`
**Author:** Jeremy Crews
**Min HA version:** 2024.6.0

---

## Overview

Door mechanics automation for a garage door controlled by a Ratgdo 2.5i
device. Handles auto-close, obstruction safety, bypass, physical button
session cancel, and notifications.

This blueprint is **single-responsibility** — it manages the door and nothing
else. Light control and room occupancy are handled externally by a WITB+
Actions instance, which consumes the garage door's template binary sensor
(`binary_sensor.garage_main_door_status`) as a `manual_occupied` signal.

---

## How It Works

| Trigger | Action |
|---|---|
| Door opens | Auto-close timer starts; open notification sent |
| Door closes | Timer cancelled if active; closed notification sent |
| Timer expires, no obstruction, bypass off | Door auto-closes |
| Timer expires, bypass active | Timer restarts; bypass notification sent |
| Timer expires, obstruction present | Timer restarts; obstruction notification sent |
| Obstruction detected while door is open | Timer cancel + restart; obstruction notification sent |
| Physical button pressed while door is open | Auto-close cancelled for this session only; notification sent |

---

## Inputs

### Required

| Input | Domain | Description |
|---|---|---|
| `ratgdo_device` | `cover` | Garage door cover entity from the Ratgdo integration |
| `obstruction_entity` | `binary_sensor` | Reports obstruction (`on` = obstruction present) |

### Optional

| Input | Default | Description |
|---|---|---|
| `garage_door_timer_helper` | _(empty)_ | Timer for auto-close countdown. Leave empty to disable auto-close entirely |
| `bypass_helper` | _(empty)_ | `input_boolean` — when `on`, skips auto-close and restarts the timer instead |
| `button_entity` | _(empty)_ | Binary sensor tracking physical button presses. Cancels auto-close for the current session only when pressed while door is open |
| `notify_group` | _(empty)_ | Notification service name without `notify.` prefix (e.g. `notify_all`). Leave empty to disable notifications |

---

## Notification tags

Each event type uses a distinct tag so notification clients replace rather
than stack alerts.

| Event | Tag |
|---|---|
| Door open / closed | `tag-ratgdo` |
| Obstruction detected | `tag-ratgdo-obstruction` |
| Bypass active | `tag-ratgdo-bypass` |
| Button session cancel | `tag-ratgdo-button` |

---

## Architecture notes

- **`mode: single` + `max_exceeded: silent`** — new triggers are silently
  dropped if the automation is already running. All sequences are
  near-instantaneous so the window is extremely short.
- **`| length > 0` guards** — all optional inputs default to `[]`. Guards
  use `| length > 0` throughout so unconfigured inputs produce no service
  calls.
- **Cancel-then-start vs start-only** — the `obstruction_found` branch uses
  `timer.cancel` + `timer.start` because the timer may be `active` when
  obstruction is detected. The `timer_done` obstruction path uses `timer.start`
  only because the timer is already `idle` when `timer.finished` fires.
- **Bypass takes priority over obstruction** in the `timer_done` branch — if
  bypass is active, the obstruction state is never evaluated.
- **No `ha_start` trigger** — this blueprint has no boolean state to correct
  on restart. Timer state is restored by HA automatically.

---

## Required helpers

| Helper | Type | Purpose |
|---|---|---|
| `timer.garage_door_auto_close` _(suggested)_ | Timer | Auto-close countdown duration |
| `input_boolean.garage_door_bypass` _(suggested)_ | Input Boolean | Manual bypass toggle |

Helpers must be created manually in HA before configuring the blueprint
instance. The timer duration is set on the helper itself, not in the blueprint.

---

## Integration with WITB+

This blueprint does not control lights or manage occupancy. The recommended
pattern for a WITB+-managed garage room:

1. Add `binary_sensor.garage_main_door_status` to the `manual_occupied` input
   of the Garage WITB+ Actions instance.
2. `on` = door open = WITB+ treats the room as occupied (lights on, vacancy
   timer suppressed).
3. `off` = door closed = WITB+ starts its normal vacancy timer.

This keeps door mechanics and room automation fully decoupled.

---

## Files in this directory

| File | Purpose |
|---|---|
| `ratgdo_25i.yaml` | Blueprint |
| `CHANGELOG_ratgdo_25i.md` | Version history |
| `rules_ratgdo_25i.md` | Behavioral rules and invariants |
| `use_cases_ratgdo_25i.md` | Supported use cases with pass/fail outcomes |
