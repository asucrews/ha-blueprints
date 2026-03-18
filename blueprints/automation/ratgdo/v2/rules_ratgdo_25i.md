# Rules — ratgdo_25i

Behavioral rules governing `ratgdo_25i.yaml`. These are the invariants the
blueprint enforces regardless of which trigger fires.

---

## Trigger rules

1. **Door Opened trigger** — fires on `ratgdo_device` state change strictly
   from `opening` → `open`. Does not fire on direct `closed` → `open`
   transitions or from `unknown`/`unavailable`.
2. **Door Closed trigger** — fires on `ratgdo_device` state change strictly
   from `closing` → `closed`.
3. **Timer Done trigger** — fires on `timer.finished` event with
   `entity_id` matching `garage_door_timer_helper`. Never fires if
   `garage_door_timer_helper` is unconfigured (empty list never matches an
   event entity_id).
4. **Obstruction Found trigger** — fires on `obstruction_entity` state change
   from `off` → `on`. Does not fire on `unknown`/`unavailable` transitions.
5. **Button Pressed trigger** — fires on `button_entity` state change from
   `off` → `on`. Never fires if `button_entity` is unconfigured (empty list
   never matches any entity state change).

---

## Door Opened rules

6. On door open: if `garage_door_timer_helper` is configured, start the
   auto-close timer.
7. On door open: if `notify_group` is configured, send an open notification
   with tag `tag-ratgdo`.
8. Both actions (timer start and notification) are independent — either or
   both may be skipped depending on which optional inputs are configured.

---

## Door Closed rules

9. On door close: if `garage_door_timer_helper` is configured AND the timer
   is currently `active` or `paused`, cancel the timer.
10. On door close: if `notify_group` is configured, send a closed notification
    with tag `tag-ratgdo`.
11. The timer cancel is guarded — no service call is made if the timer is
    already `idle` (e.g. was already cancelled by button press or never started).

---

## Auto-Close (timer_done) rules

12. The `timer_done` branch only enters if `ratgdo_device` is `open` or
    `opening` at the moment the timer fires. If the door has already closed,
    the branch exits immediately.
13. **Bypass active** (`bypass_helper` configured AND `on`):
    - Timer is restarted.
    - Bypass notification sent with tag `tag-ratgdo-bypass`.
    - No close command issued.
14. **Bypass off or unconfigured, no obstruction** (`obstruction_entity` = `off`):
    - `cover.close_cover` called on `ratgdo_device`.
    - No timer restart.
15. **Bypass off or unconfigured, obstruction present** (`obstruction_entity` = `on`):
    - Timer is restarted (no preceding cancel needed — timer is already idle
      when `timer.finished` fires).
    - Obstruction notification sent with tag `tag-ratgdo-obstruction`.
    - No close command issued.
16. Bypass check takes priority over obstruction check — if bypass is active,
    the obstruction state is never evaluated in the `timer_done` branch.

---

## Obstruction Found rules

17. The `obstruction_found` branch only enters if:
    - `ratgdo_device` is `open` or `opening`, AND
    - `garage_door_timer_helper` is configured.
18. On obstruction: cancel the current timer, then immediately restart it.
    The cancel-then-start pattern is intentional here — the timer may be
    `active` or `paused` at the time obstruction is detected, so cancel is
    required before restart.
19. Obstruction notification sent with tag `tag-ratgdo-obstruction`.
20. The `obstruction_found` branch does not issue a close command. It only
    resets the timer so the door gets another full countdown before the next
    auto-close attempt.

---

## Button Pressed (session cancel) rules

21. The `button_pressed` branch only enters if:
    - `ratgdo_device` is `open` or `opening`, AND
    - `garage_door_timer_helper` is configured AND the timer is `active`
      or `paused`.
22. On button press: cancel the timer for this session only. The timer is not
    restarted. Auto-close resumes normally the next time the door opens.
23. Button session-cancel notification sent with tag `tag-ratgdo-button`.
24. If the door is not open, or the timer is already idle (e.g. already
    cancelled), the `button_pressed` branch exits silently.

---

## Execution mode rules

25. **`mode: single`** — if a new trigger fires while a sequence is in
    progress, it is silently dropped (`max_exceeded: silent`). This prevents
    race conditions during rapid opening/closing transitions.
26. All sequences are near-instantaneous (no delays) so the single-run window
    is extremely short. The practical risk of dropping a trigger is very low.
