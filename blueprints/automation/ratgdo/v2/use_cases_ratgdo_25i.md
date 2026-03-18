# Use Cases — ratgdo_25i

Supported scenarios with expected pass/fail outcomes for each branch and
edge condition.

---

## UC-01 — Door opens, timer starts, notification sent

**Setup:** All inputs configured. Door transitions `opening` → `open`.

**Expected:**
- Door Opened trigger fires.
- `garage_door_timer_helper` configured → `timer.start` called.
- `notify_group` configured → open notification sent with tag `tag-ratgdo`.

---

## UC-02 — Door opens, no timer configured

**Setup:** `garage_door_timer_helper` not configured. Door opens.

**Expected:**
- Door Opened trigger fires.
- Timer guard `| length > 0` fails → no `timer.start` called.
- Notification sent if `notify_group` is configured.
- No auto-close will occur this session.

---

## UC-03 — Door closes, timer cancelled, notification sent

**Setup:** Timer is `active`. Door transitions `closing` → `closed`.

**Expected:**
- Door Closed trigger fires.
- Timer guard: configured AND `active` → `timer.cancel` called.
- `notify_group` configured → closed notification sent with tag `tag-ratgdo`.

---

## UC-04 — Door closes, timer already idle

**Setup:** Timer was already cancelled (e.g. by button press). Door closes.

**Expected:**
- Door Closed trigger fires.
- Timer guard: timer is `idle` → `is_state(['active', 'paused'])` fails →
  no cancel called.
- Notification sent if configured.

---

## UC-05 — Timer expires, no obstruction, bypass off → door closes

**Setup:** Timer fires. Door is `open`. No obstruction. Bypass off or
unconfigured.

**Expected:**
- Timer Done trigger fires.
- Door state guard: `open` → passes.
- Bypass check: off or unconfigured → `else` branch.
- Obstruction check: `off` → `cover.close_cover` called.
- Door begins closing.

---

## UC-06 — Timer expires, bypass active → timer restarts, notification sent

**Setup:** Timer fires. Door is `open`. `bypass_helper` = `on`.

**Expected:**
- Timer Done trigger fires.
- Bypass check: configured AND `on` → `then` branch.
- `timer.start` called — timer restarts.
- Bypass notification sent with tag `tag-ratgdo-bypass`.
- No close command issued.

---

## UC-07 — Timer expires, obstruction present → timer restarts, notification sent

**Setup:** Timer fires. Door is `open`. Bypass off. Obstruction present.

**Expected:**
- Timer Done trigger fires.
- Bypass check: off → `else` branch.
- Obstruction check: `on` → obstruction `else` branch.
- `timer.start` called directly (no preceding cancel — timer is already
  idle when `timer.finished` fires).
- Obstruction notification sent with tag `tag-ratgdo-obstruction`.
- No close command issued.

---

## UC-08 — Timer expires, door already closed → branch exits

**Setup:** Timer fires but door has already closed (e.g. manually closed
between timer start and timer fire).

**Expected:**
- Timer Done trigger fires.
- Door state guard: `closed` → `is_state(['open', 'opening'])` fails.
- Branch exits. No action taken.

---

## UC-09 — Obstruction detected while door is open, timer active

**Setup:** Door is `open`. Timer is `active`. Obstruction sensor goes
`off` → `on`.

**Expected:**
- Obstruction Found trigger fires.
- Door state guard: `open` → passes.
- Timer configured guard → passes.
- `timer.cancel` called (timer was active — cancel required before restart).
- `timer.start` called — fresh countdown begins.
- Obstruction notification sent with tag `tag-ratgdo-obstruction`.

---

## UC-10 — Obstruction detected while door is closed → branch exits

**Setup:** Door is `closed`. Obstruction sensor goes `on`.

**Expected:**
- Obstruction Found trigger fires.
- Door state guard: `closed` → `is_state(['open', 'opening'])` fails.
- Branch exits. No action taken.

---

## UC-11 — Obstruction detected, no timer configured → branch exits

**Setup:** Door is `open`. `garage_door_timer_helper` not configured.
Obstruction detected.

**Expected:**
- Obstruction Found trigger fires.
- Door state guard: passes.
- Timer configured guard: `| length > 0` fails → branch exits.
- No action taken. (No timer to restart — auto-close is disabled.)

---

## UC-12 — Physical button pressed while timer is active → session cancelled

**Setup:** Door is `open`. Timer is `active`. Physical button pressed.

**Expected:**
- Button Pressed trigger fires.
- Door state guard: `open` → passes.
- Timer guard: configured AND `active` → passes.
- `timer.cancel` called. Timer not restarted.
- Session-cancel notification sent with tag `tag-ratgdo-button`.
- Auto-close will resume normally next time the door opens.

---

## UC-13 — Physical button pressed while timer already idle → branch exits

**Setup:** Door is `open`. Timer was already cancelled (e.g. prior button
press this session). Physical button pressed again.

**Expected:**
- Button Pressed trigger fires.
- Timer guard: timer is `idle` → `is_state(['active', 'paused'])` fails.
- Branch exits. No action taken. No duplicate notification.

---

## UC-14 — Physical button pressed while door is closed → branch exits

**Setup:** Door is `closed`. Physical button pressed (e.g. to open the door).

**Expected:**
- Button Pressed trigger fires.
- Door state guard: `closed` → `is_state(['open', 'opening'])` fails.
- Branch exits. No action taken.

---

## UC-15 — No notification service configured — all notification calls skipped

**Setup:** `notify_group` left empty (`""`). Any trigger fires.

**Expected:**
- `notify_group | length > 0` evaluates `false` on all branches.
- No `notify.*` service calls made in any branch.
- All door mechanics (timer, cancel, close) operate normally.

---

## UC-16 — Bypass active during obstruction event (timer_done)

**Setup:** Timer fires. Door is `open`. Bypass is `on`. Obstruction is also
present.

**Expected:**
- Timer Done trigger fires.
- Bypass check: `on` → `then` branch fires immediately.
- Obstruction state is **never evaluated** in `timer_done` when bypass is active.
- Timer restarts. Bypass notification sent.
- No obstruction notification from this path.
  (Obstruction notification fires separately via the `obstruction_found` trigger.)
