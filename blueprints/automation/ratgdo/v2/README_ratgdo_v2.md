# Ratgdo 2.5i Blueprint

**Version:** 2.1.1
**Domain:** automation
**Minimum HA Version:** 2024.6.0
**Author:** Jeremy Crews
**Source:** [ratgdo_2.5i.yaml](https://raw.githubusercontent.com/asucrews/ha-blueprints/main/automations/ratgdo_2.5i/ratgdo_2.5i.yaml)

---

## Overview

Door mechanics automation for a garage door controlled by a Ratgdo 2.5i device. Handles auto-close, obstruction safety, bypass, physical button session cancel, and notifications.

This blueprint is **single-responsibility** — it manages the door and nothing else. Light control and room occupancy are handled externally by a WITB+ Actions instance, which consumes the garage door's template binary sensor (`binary_sensor.garage_main_door_status`) as a `manual_occupied` signal.

---

## Use Cases

| Trigger | What Happens |
|---|---|
| Door opens | Auto-close timer starts; open notification sent |
| Door closes | Timer cancelled if active; closed notification sent |
| Timer expires, no obstruction, bypass off | Door auto-closes |
| Timer expires, bypass active | Timer restarts; bypass notification sent |
| Timer expires, obstruction present | Timer restarts; obstruction notification sent |
| Obstruction detected while door is open | Timer restarted; obstruction notification sent |
| Physical button pressed while door is open | Auto-close cancelled for this session only; notification sent |

---

## Inputs

### Required

| Input | Description |
|---|---|
| `ratgdo_device` | The garage door cover entity from the Ratgdo integration |
| `obstruction_entity` | Binary sensor that reports obstruction (`on` = obstruction present) |

### Optional

| Input | Default | Description |
|---|---|---|
| `garage_door_timer_helper` | _(empty)_ | Timer entity for auto-close countdown. Leave empty to disable auto-close entirely |
| `bypass_helper` | _(empty)_ | `input_boolean` — when `on`, auto-close is skipped and the timer restarts instead. Useful for intentional extended sessions |
| `button_entity` | _(empty)_ | Binary sensor tracking physical button presses on the Ratgdo device. When pressed while the door is open, cancels auto-close for that session only. Auto-close resumes normally next time the door opens |
| `notify_group` | _(empty)_ | Notification service name — enter without the `notify.` prefix (e.g. `notify_all` not `notify.notify_all`). Leave empty to disable notifications |

---

## Notification Tags

Each event type uses a distinct notification tag, allowing your notification client to replace rather than stack alerts.

| Event | Tag |
|---|---|
| Door open / closed | `tag-ratgdo` |
| Obstruction detected | `tag-ratgdo-obstruction` |
| Bypass active | `tag-ratgdo-bypass` |
| Button session cancel | `tag-ratgdo-button` |

---

## Integration with WITB+

This blueprint does not control lights or manage occupancy directly. The recommended pattern for a WITB+-managed garage room is:

1. Add `binary_sensor.garage_main_door_status` to the `manual_occupied` input of the Garage WITB+ Actions instance
2. `on` = door open = WITB+ treats the room as occupied (lights on, vacancy timer suppressed)
3. `off` = door closed = WITB+ starts its normal vacancy timer

This keeps door mechanics and room automation fully decoupled.

---

## Required Helpers

| Helper | Type | Purpose |
|---|---|---|
| `timer.garage_door_auto_close` _(suggested)_ | Timer | Auto-close countdown duration |
| `input_boolean.garage_door_bypass` _(suggested)_ | Input Boolean | Manual bypass toggle |

Helpers must be created manually in HA before configuring the blueprint instance. The timer duration is set on the helper itself, not in the blueprint.

---

## Mode

`single` — if the automation is already running when a new trigger fires, the new trigger is silently ignored. This prevents race conditions during opening/closing transitions.
