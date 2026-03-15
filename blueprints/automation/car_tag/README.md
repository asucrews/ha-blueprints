# car_tag/

BLE car tag garage door automation.

## Current version

**v1** — see [`v1/README_car_tag_v1.md`](v1/README_car_tag_v1.md)

## Summary

Automates garage door open/close from a BLE iBeacon car tag wired to the car's ignition. Rising edge (car on) opens the door; falling edge (car off) starts the auto-close timer. A WiFi backup trigger catches missed BLE edges when the ESPHome node was temporarily offline.
