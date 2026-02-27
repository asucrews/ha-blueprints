# CHANGELOG — WITB Transit Room Driver

## v1.0.0

Initial release.

- PIR-only occupancy driver for transit areas (hallways, stairs, open connectors).
- Hold-timer decay model: motion ON restarts the hold timer; occupancy clears when the timer expires.
- Outputs `occupied_effective` as an `input_boolean` compatible with WITB+ Actions v2.
- Case-statement priority pattern with sequential `choose` blocks:
  - Motion ON — assert occupied, restart decay timer.
  - Hold timer finished — clear occupancy.
  - Keepalive ON — extend hold without re-triggering the timer.
  - Instant OFF — force occupancy off immediately and cancel timer.
  - Suppress timer — rearm mitigation for PIR dead-time.
  - Maintenance override — hold occupancy on indefinitely.
  - HA restart — restore state if motion is currently on.
- Day/night hold durations configurable via sun entity or boolean helper.
- Minimum ON seconds guard to prevent flicker on brief transits.
