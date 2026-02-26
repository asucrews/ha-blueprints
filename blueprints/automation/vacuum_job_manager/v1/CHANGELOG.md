# Vacuum Job Manager (iRobot) — Changelog

---

## v1.3 — 2026-02-26

### Changes

**Separate `canceled_counter` from `failures_counter` (item #6)**
Previously, user-canceled missions incremented `failures_counter`, conflating
two distinct outcomes. A user manually sending the robot home mid-clean is not
the same as an error or a failed mission.

Changes made:
- New `canceled_counter` input added to the blueprint (required — wire it to
  `counter.roomba_vacjob_canceled` from the helpers file).
- Canceled branch in Block 1 now increments `canceled_counter` only.
- `failures_counter` now reserved strictly for: iRobot-reported failed missions
  and Block 4 watchdog force-closes (abnormal, unrecoverable closes).
- Helpers file: added `roomba_vacjob_canceled` counter alongside
  `roomba_vacjob_failures`.

**Remove deprecated `initial:` from `input_number` (item #9)**
The `initial:` key on `input_number` helpers has been deprecated in recent HA
versions — it is only applied on first entity creation and silently ignored
thereafter. Removed from `roomba_vacjob_max_runtime_min` in the helpers file.
A comment has been added in its place directing users to set the value via the UI
after creation.

> **Migration note:** After reloading the helpers package, open the
> `roomba_vacjob_max_runtime_min` helper in Settings → Helpers and confirm the
> value is set to your desired default (240 min is recommended). The new
> `roomba_vacjob_canceled` counter will be created at 0 automatically.

---

## v1.2 — 2026-02-26

### Bug Fixes

**Multi-entity service calls broken (`join(',')` → list)**
`overrides_ids` and `lights_ids` were built with `| join(',')`, producing a
comma-separated string (e.g. `"input_boolean.foo,input_boolean.bar"`). Home
Assistant requires a list for `target.entity_id` when targeting multiple entities;
the comma-separated string was silently rejected. Any install with more than one
light or override boolean had those features not working at all.
Fix: removed the intermediate `join(',')` variables entirely and pass `overrides`
and `lights_targets` (already lists) directly as `entity_id`.
Affected: Block 2 start sequence and all three completion branches in Block 1.

**Button request bypassed `enabled_boolean`**
The `button_request` branch queued a job without checking whether the system was
enabled. A button press would queue the robot even while disabled.
Fix: added `condition: state` checks for `enabled_boolean: "on"` and
`requested_boolean: "off"` to the `button_request` conditions.

**No recovery when watchdog fires but counter never increments**
The watchdog sent `vacuum.return_to_base` and stopped. If the iRobot cloud counter
never updated (brief offline, dock flap, HA restart), `active_boolean` stayed `on`
permanently with no second chance to clear it — requiring manual intervention every
time.
Fix: added Block 4 (post-watchdog docked recovery). When the vacuum transitions to
`docked` while `active_boolean` is on and the watchdog timer is already `idle`, a
30-second settle delay runs to allow any in-flight counter update to land. If
`active_boolean` is cleared by Block 1 during that window, the block exits cleanly.
If it is still on after 30 s and no counter incremented, the job is force-closed as
`canceled` with a notification.

---

### Logic Fixes

**Schedule could double-queue an already-queued job**
The `schedule_request` branch checked `active_boolean: "off"` but not
`requested_boolean`. A scheduled time trigger would fire again while a job was
already queued (`requested=on`, `active=off`), turning the boolean on a second time
and spawning a redundant queued run.
Fix: added `condition: state` for `requested_boolean: "off"` to the
`schedule_request` conditions.

**Counter triggers vulnerable to `unavailable`/`unknown` sensor states**
When a mission sensor briefly went `unavailable` (parsed as `int 0`), a baseline
snapshotted before the drop could be non-zero, making `now > base` evaluate false
on recovery — acceptable. However the reverse (baseline snapshotted as `0` during
an unavailable period) could cause a premature completion once the sensor recovered
to its real value.
Fix: added a template condition to the counter-changed branch that requires all
three mission sensors to be neither `unavailable` nor `unknown` before evaluating
baselines.

---

### Improvements

**Completion notifications**
The watchdog already sent a notification, but successful, failed, and canceled
completions were silent. A `notify` step (guarded by `notify != ''`) has been added
at the end of each completion branch in Block 1 and in the Block 4 force-close path.

**Reduced `max` in queued mode**
`max: 10` was unnecessarily high. A button press spawns at most 2 runs
(`button_request` sets `requested_boolean` → `requested_on` fires a second run).
Reduced to `max: 3` to give one extra slot for a scheduler overlap without
allowing a large backlog.

**Inline comments**
Added inline comments throughout explaining the purpose of each fix and documenting
the "canceled counted as failure" behaviour so the intent is clear to future
editors.

---

## v1.1

- Turn ON configurable lights/switches during job.
- Enable WITB `automation_override` booleans during job (WITB override lock).
- On job end: disable overrides and turn OFF lights unless occupancy entity is active.
- Occupancy gate: configurable list of occupancy entities; any `on` prevents lights
  being turned off at job end.

---

## v1.0

- Initial release.
- Roomba-safe job manager: does NOT treat `docked` as complete.
- Completion detection based solely on iRobot mission counter increments
  (successful / failed / canceled).
- Schedule support with configurable days and time.
- Manual run-now button support.
- Watchdog timer with configurable max runtime; sends `return_to_base` on expiry.
- Phase tracking helper (`input_select`) mirroring vacuum entity state.
- Baseline snapshot helpers to detect counter deltas correctly across reboots.
- Optional notify service for watchdog alerts.
