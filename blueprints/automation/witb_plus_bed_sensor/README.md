# witb_plus_bed_sensor/

WITB+ Bed → Force Occupied blueprint.

## Current version

**v1** — see [`v1/README.md`](v1/README.md)

## Summary

Drives an `input_boolean` `force_occupied` helper to keep a bedroom occupied while someone is in bed. Prevents false vacancy clearances (lights/fan turning off on a sleeping occupant) by extending WITB+ occupancy — never initiating it.
