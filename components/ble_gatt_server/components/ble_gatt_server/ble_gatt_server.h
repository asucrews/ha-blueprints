#pragma once

#include "esphome/core/component.h"
#include "esphome/core/log.h"
#include "esphome/core/automation.h"

#include <NimBLEDevice.h>
#include <NimBLEServer.h>
#include <NimBLEService.h>
#include <NimBLECharacteristic.h>
#include <NimBLEAdvertising.h>

#include <functional>
#include <map>
#include <string>
#include <vector>

namespace esphome {
namespace ble_gatt_server {

// ---------------------------------------------------------------------------
// Callback types used per-characteristic
// ---------------------------------------------------------------------------
using WriteCallback = std::function<void(const std::string &value)>;
using ReadCallback  = std::function<std::string()>;

// ---------------------------------------------------------------------------
// Internal struct for each characteristic declared in YAML
// ---------------------------------------------------------------------------
struct CharacteristicConfig {
  std::string  uuid;
  uint32_t     properties{0};
  std::string  initial_value;
  WriteCallback on_write{nullptr};
  ReadCallback  on_read{nullptr};
};

// ---------------------------------------------------------------------------
// Forward declaration for the Action helpers
// ---------------------------------------------------------------------------
class BLEGattServerComponent;

// ---------------------------------------------------------------------------
// Action: ble_gatt_server.notify
// ---------------------------------------------------------------------------
template<typename... Ts>
class BLENotifyAction : public Action<Ts...> {
 public:
  explicit BLENotifyAction(BLEGattServerComponent *parent) : parent_(parent) {}
  TEMPLATABLE_VALUE(std::string, uuid)
  TEMPLATABLE_VALUE(std::string, value)
  void play(Ts... x) override;
 private:
  BLEGattServerComponent *parent_;
};

// ---------------------------------------------------------------------------
// Action: ble_gatt_server.set_value
// ---------------------------------------------------------------------------
template<typename... Ts>
class BLESetValueAction : public Action<Ts...> {
 public:
  explicit BLESetValueAction(BLEGattServerComponent *parent) : parent_(parent) {}
  TEMPLATABLE_VALUE(std::string, uuid)
  TEMPLATABLE_VALUE(std::string, value)
  void play(Ts... x) override;
 private:
  BLEGattServerComponent *parent_;
};

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------
class BLEGattServerComponent : public Component,
                                public NimBLEServerCallbacks,
                                public NimBLECharacteristicCallbacks,
                                public NimBLESecurityCallbacks {
 public:
  // ---- ESPHome lifecycle ------------------------------------------------
  void setup() override;
  void loop() override;
  void dump_config() override;
  float get_setup_priority() const override { return setup_priority::AFTER_WIFI; }

  // ---- Configuration setters (called from generated code) ---------------
  void set_device_name(const std::string &name) { device_name_ = name; }
  void set_service_uuid(const std::string &uuid) { service_uuid_ = uuid; }
  void set_pairing_enabled(bool enabled)         { pairing_enabled_ = enabled; }
  void set_passkey(uint32_t key)                 { passkey_ = key; }
  void set_max_connections(uint8_t n)            { max_connections_ = n; }

  void add_characteristic(const CharacteristicConfig &cfg) {
    char_configs_.push_back(cfg);
  }

  // ---- Runtime API (used by automations / lambdas) ----------------------

  /** Push a new value to a NOTIFY/INDICATE characteristic */
  void notify_characteristic(const std::string &uuid, const std::string &value);

  /** Silently update a characteristic value without notifying */
  void set_characteristic_value(const std::string &uuid, const std::string &value);

  /** Return current value of a characteristic */
  std::string get_characteristic_value(const std::string &uuid);

  bool is_connected() const      { return connected_count_ > 0; }
  int  connected_count() const   { return connected_count_; }

  // ---- NimBLEServerCallbacks --------------------------------------------
  void onConnect(NimBLEServer *server, ble_gap_conn_desc *desc) override;
  void onDisconnect(NimBLEServer *server) override;
  void onMTUChange(uint16_t MTU, ble_gap_conn_desc *desc) override;

  // ---- NimBLECharacteristicCallbacks ------------------------------------
  void onRead(NimBLECharacteristic *characteristic) override;
  void onWrite(NimBLECharacteristic *characteristic) override;
  void onSubscribe(NimBLECharacteristic *characteristic,
                   ble_gap_conn_desc *desc, uint16_t subValue) override;

  // ---- NimBLESecurityCallbacks ------------------------------------------
  uint32_t onPassKeyRequest() override;
  bool     onConfirmPIN(uint32_t pin) override;
  void     onAuthenticationComplete(ble_gap_conn_desc *desc) override;
  bool     onSecurityRequest() override;

  // ---- Trigger accessors (declared in generated code) -------------------
  Trigger<std::string, std::string> *get_on_write_trigger() {
    return &on_write_trigger_;
  }
  Trigger<> *get_on_connect_trigger()    { return &on_connect_trigger_; }
  Trigger<> *get_on_disconnect_trigger() { return &on_disconnect_trigger_; }

 protected:
  std::string device_name_{"ESPHome"};
  std::string service_uuid_{"12345678-1234-1234-1234-123456789ABC"};
  bool        pairing_enabled_{false};
  uint32_t    passkey_{123456};
  uint8_t     max_connections_{3};
  int         connected_count_{0};

  NimBLEServer      *server_{nullptr};
  NimBLEService     *service_{nullptr};
  NimBLEAdvertising *advertising_{nullptr};

  std::vector<CharacteristicConfig>          char_configs_;
  std::map<std::string, NimBLECharacteristic *> characteristics_;

  Trigger<std::string, std::string> on_write_trigger_;
  Trigger<>                          on_connect_trigger_;
  Trigger<>                          on_disconnect_trigger_;

  void start_advertising_();
};

// ---------------------------------------------------------------------------
// Action implementations (need full class definition, so placed here)
// ---------------------------------------------------------------------------
template<typename... Ts>
void BLENotifyAction<Ts...>::play(Ts... x) {
  parent_->notify_characteristic(this->uuid_.value(x...), this->value_.value(x...));
}

template<typename... Ts>
void BLESetValueAction<Ts...>::play(Ts... x) {
  parent_->set_characteristic_value(this->uuid_.value(x...), this->value_.value(x...));
}

}  // namespace ble_gatt_server
}  // namespace esphome
