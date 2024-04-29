**Warning**: AI was used to write and format this readme

# Lock Management Dev (0.1.0)

## Overview

Lock Management Dev (0.1.0) is an automation blueprint designed for managing door locks with additional auto-lock functionality based on specified conditions and triggers.

## Assumptions

- User must have Lock Code Manager configured and working by raman325 (Github)[https://github.com/raman325/lock_code_manager]
- It is assumed that users have configured their door locks and timers correctly within their home automation system.
- Users are expected to ensure that the necessary triggers and conditions are met for the automation to function as intended.

## Inputs

### Lock

- **Description:** Lock entity to be controlled.
- **Selector:** Allows selecting a lock entity. Only one lock can be selected.

### Auto Lock Timer

- **Description:** Timer entity for auto-lock functionality.
- **Default:** `timer.none`
- **Selector:** Allows selecting a timer entity. Only one timer can be selected.

## Variables

- **lock:** Input variable representing the selected lock entity.
- **auto_lock_timer:** Input variable representing the selected auto-lock timer entity.

## Triggers

- **LCM Event:**
  - Triggered by the event type `lock_code_manager_lock_state_changed` with specific entity ID.
- **Timer Finished:**
  - Triggered when the selected auto-lock timer transitions from active to idle state.

## Action

The action section defines sequences of actions to be executed based on the triggers and conditions:

- If the lock state changes to locked, and an auto-lock timer is set, cancel the timer if it's active.
- If the lock state changes to unlocked, and an auto-lock timer is set:
  - Cancel the timer if it's active.
  - Start the auto-lock timer.

If the auto-lock timer finishes (transitions from active to idle), it triggers the lock to be locked.

## Mode

- **Queued:** Ensures that no more than 5 instances of this automation can run simultaneously.

This blueprint offers a flexible and customizable solution for managing door locks with additional auto-lock functionality based on specified conditions and triggers.
