# witb_transit_room/

WITB Transit Room blueprint.

## Current version

**v2** — see [`v2/README_witb_transit_room_v2.md`](v2/README_witb_transit_room_v2.md)

## Legacy version

**v1** — see [`v1/README_witb_transit_room_v1.md`](v1/README_witb_transit_room_v1.md). Kept as-is; v2 is not a drop-in replacement.

## Summary

v2 is WITB+ 4.4.0 minus doors, for transit areas (hallways, stairs, open connectors). Same motion/mmWave logic, override/force/manual controls and failsafe as WITB+, with all door logic removed. Its occupancy helper feeds `binary_sensor.<slug>_occupied_effective`, consumed by WITB Actions V3.

v1 is the older PIR-only hold-timer driver with keepalive, instant-off and day/night hold.
