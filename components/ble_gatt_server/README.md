# ESPHome BLE GATT Server Component

A fully custom ESPHome component that turns your ESP32 into a **BLE GATT peripheral**,
discoverable and connectable from an **iPhone / iPad** (or Android).

---

## File structure

```
your_esphome_project/
├── components/
│   └── ble_gatt_server/
│       ├── __init__.py          ← Python config schema + codegen
│       ├── ble_gatt_server.h    ← C++ header
│       └── ble_gatt_server.cpp  ← C++ implementation
├── example.yaml                 ← Full example config
└── secrets.yaml
```

---

## Requirements

| Requirement | Notes |
|---|---|
| **ESP32** (any variant) | ESP32-S3, ESP32-C3 also supported |
| **ESPHome ≥ 2023.12** | For `external_components` local path support |
| **Arduino framework** | `framework: type: arduino` in your `esp32:` block |
| **NimBLE-Arduino library** | Auto-added by the component via `cg.add_library` |

> ⚠️ Do **not** add `esp32_ble:` or `esp32_ble_tracker:` to the same config.
> This component initialises the NimBLE stack itself. Two initialisations will conflict.

---

## Quick start

### 1. Copy the component
Place the `components/` folder next to your `.yaml` file (see structure above).

### 2. Minimal YAML

```yaml
external_components:
  - source:
      type: local
      path: components

ble_gatt_server:
  device_name: "MyESPHome"
  service_uuid: "12345678-1234-1234-1234-123456789ABC"
  characteristics:
    - uuid: "AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA"
      properties: [read, notify]
      initial_value: "hello"
    - uuid: "BBBBBBBB-BBBB-BBBB-BBBB-BBBBBBBBBBBB"
      properties: [read, write]
```

### 3. Flash and test on iPhone

Install **nRF Connect** (free, App Store) or **LightBlue**.

1. Open the app → scan for BLE devices
2. Find **"MyESPHome"** in the list
3. Tap **Connect**
4. Browse your service UUID and characteristics
5. Read / Write / Subscribe to notifications

---

## Configuration reference

```yaml
ble_gatt_server:
  id: my_gatt                          # (optional) for use in automations
  device_name: "ESPHome BLE"           # advertised device name
  service_uuid: "xxxx-..."             # your primary service UUID
  pairing: false                       # true = bonding + MITM (requires passkey)
  passkey: 123456                      # 6-digit passkey (only used when pairing: true)
  max_connections: 3                   # simultaneous BLE connections allowed

  characteristics:
    - uuid: "AAAA-..."
      properties: [read, notify]       # see property list below
      initial_value: "0.0"             # optional startup value

  on_write:                            # fires when any characteristic is written
    - lambda: |-
        // uuid  (std::string) — which characteristic was written
        // value (std::string) — new value
        ESP_LOGI("tag", "wrote %s = %s", uuid.c_str(), value.c_str());

  on_connect:
    - logger.log: "Client connected"

  on_disconnect:
    - logger.log: "Client disconnected"
```

### Characteristic properties

| Property | Meaning |
|---|---|
| `read` | Client can read the current value |
| `write` | Client can write (with acknowledgement) |
| `write_nr` | Client can write without response |
| `notify` | Server pushes updates to subscribed clients |
| `indicate` | Like notify but acknowledged |
| `read_enc` | Read requires encryption |
| `write_enc` | Write requires encryption |
| `broadcast` | Value broadcasts in advertisement |

---

## Automation actions

### `ble_gatt_server.notify`
Push a new value **and** notify all subscribed clients.

```yaml
on_sensor_update:
  - ble_gatt_server.notify:
      id: my_gatt
      uuid: "AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA"
      value: !lambda 'return to_string(x);'
```

### `ble_gatt_server.set_value`
Update the stored value **without** notifying clients.

```yaml
- ble_gatt_server.set_value:
    id: my_gatt
    uuid: "AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA"
    value: "ready"
```

---

## Pairing with iPhone (secure mode)

Set `pairing: true` in your config. When you connect from the iPhone:

1. iOS will show a numeric code
2. Check your **ESPHome logs** — you will see:
   ```
   >>> Passkey requested — show this on iPhone: 123456
   ```
3. Confirm the code on iPhone → bonded ✅

Once bonded, iPhone remembers the device. To un-pair: go to
**Settings → Bluetooth → (i) → Forget This Device**.

---

## BLE + WiFi coexistence

The ESP32 shares its radio between WiFi and BLE. The component already sets the
correct build flags. If you still experience dropouts, add this to your YAML:

```yaml
esp32:
  board: esp32dev
  framework:
    type: arduino
    # Force BLE/WiFi coexistence mode
    sdkconfig_options:
      CONFIG_ESP32_WIFI_SW_COEXIST_ENABLE: "y"
      CONFIG_BT_ENABLED: "y"
```

---

## Connecting from a custom iOS app (CoreBluetooth)

```swift
// Swift snippet — scan for the device
let serviceUUID = CBUUID(string: "12345678-1234-1234-1234-123456789ABC")
centralManager.scanForPeripherals(withServices: [serviceUUID])

// After connecting, discover and subscribe to a notify characteristic
let charUUID = CBUUID(string: "AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA")
peripheral.setNotifyValue(true, for: characteristic)

// Receive updates
func peripheral(_ peripheral: CBPeripheral,
                didUpdateValueFor characteristic: CBCharacteristic,
                error: Error?) {
    if let data = characteristic.value,
       let str = String(data: data, encoding: .utf8) {
        print("Received: \(str)")
    }
}
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Device not appearing in iOS scan | Make sure `pairing: false` first; check logs for "advertising started" |
| Connection drops immediately | Could be iOS security rejection — try `pairing: true` |
| NimBLE library not found | Add `lib_deps: h2zero/NimBLE-Arduino@1.4.2` to your `platformio.ini` |
| Conflict with `esp32_ble_tracker` | Remove `esp32_ble_tracker` — cannot coexist with this component |
| Notify not received on iPhone | Ensure client subscribed to notifications (tap the icon in nRF Connect) |
