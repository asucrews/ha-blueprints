# Car Tag Automation Use Cases

## BLE Path — `off → on` (car turned on)

- **UC1 — Arriving:** Person `not_home`, door `closed` → open ✅
- **UC2 — Departing:** Person `home`, door `closed` → open ✅

## BLE Path — `on → off` (car turned off)

- **UC3 — Parked:** Person `home`, door `open` → start close timer ✅
- **UC4 — Car off, door already closed:** → do nothing ✅

## WiFi Backup Path (node comes back online, BLE edge may have been missed)

- **UC5 — Arriving:** Person `not_home`, BLE `off`, door `closed` → open ✅
- **UC6 — Departing:** BLE `on` (car is on), door `closed` → open ✅
- **UC7 — Node bounces, car off:** BLE `off`, person `home` → stay closed ✅

## Race Conditions

- **RC1:** WiFi fired → BLE comes on after → door no longer `closed` → BLE branch blocked naturally ✅
- **RC2:** BLE fired → WiFi comes on after → door no longer `closed` → WiFi branch blocked naturally ✅
