# air_purifier/

Twice-daily boost schedule automation for air purifiers.

## Current version

**v1** — see [`v1/README_air_purifier_v1.md`](v1/README_air_purifier_v1.md)

## Summary

Keeps a group of air purifiers synchronized to a configurable twice-daily boost schedule. During boost windows the purifiers run at full (or configurable) speed; outside those windows they return to a preset mode (default: `auto`). A 5-minute reconciler and an HA-restart guard ensure devices stay in the correct state after power loss or manual overrides.
