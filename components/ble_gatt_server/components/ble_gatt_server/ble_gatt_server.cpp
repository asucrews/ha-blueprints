#include "ble_gatt_server.h"
#include "esphome/core/log.h"
#include "esphome/core/application.h"

namespace esphome {
namespace ble_gatt_server {

static const char *TAG = "ble_gatt_server";

// ============================================================================
// setup()
// ============================================================================
void BLEGattServerComponent::setup() {
  ESP_LOGI(TAG, "Initialising BLE GATT Server...");

  // --- Init NimBLE stack ---------------------------------------------------
  NimBLEDevice::init(this->device_name_);
  NimBLEDevice::setPower(ESP_PWR_LVL_P9);  // Max TX power

  // --- Security / pairing (required for iOS bonding) ----------------------
  if (this->pairing_enabled_) {
    // Require bonding, MITM protection and Secure Connections
    NimBLEDevice::setSecurityAuth(
        BLE_SM_PAIR_AUTHREQ_BOND |
        BLE_SM_PAIR_AUTHREQ_MITM |
        BLE_SM_PAIR_AUTHREQ_SC);
    NimBLEDevice::setSecurityPasskey(this->passkey_);
    // Display-only: iPhone shows passkey that the ESP32 "displays" via log
    NimBLEDevice::setSecurityIOCap(BLE_HS_IO_DISPLAY_ONLY);
    NimBLEDevice::setSecurityCallbacks(this);
    ESP_LOGI(TAG, "Pairing enabled — passkey: %06" PRIu32, this->passkey_);
  } else {
    // Open, no security — easiest for development
    NimBLEDevice::setSecurityAuth(false, false, false);
    ESP_LOGI(TAG, "Pairing disabled (open access)");
  }

  // --- Create server -------------------------------------------------------
  this->server_ = NimBLEDevice::createServer();
  this->server_->setCallbacks(this);
  this->server_->advertiseOnDisconnect(false);  // We restart manually

  // --- Create service ------------------------------------------------------
  this->service_ = this->server_->createService(this->service_uuid_);

  // --- Add all characteristics from config --------------------------------
  for (auto &cfg : this->char_configs_) {
    NimBLECharacteristic *ch =
        this->service_->createCharacteristic(cfg.uuid, cfg.properties);
    ch->setCallbacks(this);
    if (!cfg.initial_value.empty()) {
      ch->setValue(cfg.initial_value);
    }
    this->characteristics_[cfg.uuid] = ch;
    ESP_LOGI(TAG, "  + Characteristic %s  props=0x%04X  init='%s'",
             cfg.uuid.c_str(), cfg.properties, cfg.initial_value.c_str());
  }

  // --- Start service -------------------------------------------------------
  this->service_->start();

  // --- Advertising ---------------------------------------------------------
  this->advertising_ = NimBLEDevice::getAdvertising();
  this->advertising_->addServiceUUID(this->service_uuid_);
  this->advertising_->setScanResponse(true);
  // iOS needs these interval hints for reliable discovery
  this->advertising_->setMinPreferred(0x06);
  this->advertising_->setMaxPreferred(0x12);

  this->start_advertising_();

  ESP_LOGI(TAG, "GATT Server ready — advertising as '%s'",
           this->device_name_.c_str());
}

// ============================================================================
// dump_config()
// ============================================================================
void BLEGattServerComponent::dump_config() {
  ESP_LOGCONFIG(TAG, "BLE GATT Server:");
  ESP_LOGCONFIG(TAG, "  Device name : %s", this->device_name_.c_str());
  ESP_LOGCONFIG(TAG, "  Service UUID: %s", this->service_uuid_.c_str());
  ESP_LOGCONFIG(TAG, "  Pairing     : %s", this->pairing_enabled_ ? "yes" : "no");
  if (this->pairing_enabled_)
    ESP_LOGCONFIG(TAG, "  Passkey     : %06" PRIu32, this->passkey_);
  ESP_LOGCONFIG(TAG, "  Characteristics (%d):", (int) this->char_configs_.size());
  for (auto &cfg : this->char_configs_)
    ESP_LOGCONFIG(TAG, "    - %s  props=0x%04X", cfg.uuid.c_str(), cfg.properties);
}

// ============================================================================
// loop()
// ============================================================================
void BLEGattServerComponent::loop() {
  // Nothing periodic needed — NimBLE drives itself via FreeRTOS tasks.
}

// ============================================================================
// Internal helpers
// ============================================================================
void BLEGattServerComponent::start_advertising_() {
  if (!this->advertising_->isAdvertising()) {
    this->advertising_->start();
    ESP_LOGD(TAG, "Advertising started");
  }
}

// ============================================================================
// Runtime API
// ============================================================================
void BLEGattServerComponent::notify_characteristic(const std::string &uuid,
                                                    const std::string &value) {
  auto it = this->characteristics_.find(uuid);
  if (it == this->characteristics_.end()) {
    ESP_LOGW(TAG, "notify: unknown UUID %s", uuid.c_str());
    return;
  }
  it->second->setValue(value);
  it->second->notify();
  ESP_LOGD(TAG, "Notified %s = '%s'", uuid.c_str(), value.c_str());
}

void BLEGattServerComponent::set_characteristic_value(const std::string &uuid,
                                                       const std::string &value) {
  auto it = this->characteristics_.find(uuid);
  if (it == this->characteristics_.end()) {
    ESP_LOGW(TAG, "set_value: unknown UUID %s", uuid.c_str());
    return;
  }
  it->second->setValue(value);
  ESP_LOGD(TAG, "Set %s = '%s'", uuid.c_str(), value.c_str());
}

std::string BLEGattServerComponent::get_characteristic_value(
    const std::string &uuid) {
  auto it = this->characteristics_.find(uuid);
  if (it == this->characteristics_.end()) {
    ESP_LOGW(TAG, "get_value: unknown UUID %s", uuid.c_str());
    return "";
  }
  return it->second->getValue();
}

// ============================================================================
// NimBLEServerCallbacks
// ============================================================================
void BLEGattServerComponent::onConnect(NimBLEServer *server,
                                        ble_gap_conn_desc *desc) {
  this->connected_count_++;
  ESP_LOGI(TAG, "Client connected  addr=%s  total=%d",
           NimBLEAddress(desc->peer_ota_addr).toString().c_str(),
           this->connected_count_);

  this->on_connect_trigger_.trigger();

  // Keep advertising so additional clients can connect (up to max)
  if (server->getConnectedCount() < this->max_connections_) {
    this->start_advertising_();
  }
}

void BLEGattServerComponent::onDisconnect(NimBLEServer *server) {
  this->connected_count_ = server->getConnectedCount();
  ESP_LOGI(TAG, "Client disconnected  remaining=%d", this->connected_count_);

  this->on_disconnect_trigger_.trigger();

  // Always restart advertising after a disconnect
  this->start_advertising_();
}

void BLEGattServerComponent::onMTUChange(uint16_t MTU,
                                          ble_gap_conn_desc *desc) {
  ESP_LOGI(TAG, "MTU changed to %d (conn_handle=%d)", MTU, desc->conn_handle);
}

// ============================================================================
// NimBLECharacteristicCallbacks
// ============================================================================
void BLEGattServerComponent::onRead(NimBLECharacteristic *characteristic) {
  const std::string uuid = characteristic->getUUID().toString();

  for (auto &cfg : this->char_configs_) {
    if (cfg.uuid == uuid && cfg.on_read) {
      std::string val = cfg.on_read();
      characteristic->setValue(val);
      ESP_LOGD(TAG, "Read %s => '%s'", uuid.c_str(), val.c_str());
      return;
    }
  }
  ESP_LOGD(TAG, "Read %s => '%s'", uuid.c_str(),
           characteristic->getValue().c_str());
}

void BLEGattServerComponent::onWrite(NimBLECharacteristic *characteristic) {
  const std::string uuid  = characteristic->getUUID().toString();
  const std::string value = characteristic->getValue();

  ESP_LOGI(TAG, "Write %s = '%s' (%d bytes)",
           uuid.c_str(), value.c_str(), (int) value.size());

  // Fire the global on_write trigger with (uuid, value)
  this->on_write_trigger_.trigger(uuid, value);

  // Fire per-characteristic callback if configured
  for (auto &cfg : this->char_configs_) {
    if (cfg.uuid == uuid && cfg.on_write) {
      cfg.on_write(value);
      return;
    }
  }
}

void BLEGattServerComponent::onSubscribe(NimBLECharacteristic *characteristic,
                                          ble_gap_conn_desc *desc,
                                          uint16_t subValue) {
  const std::string uuid = characteristic->getUUID().toString();
  if (subValue == 1)
    ESP_LOGI(TAG, "Client subscribed to NOTIFY  on %s", uuid.c_str());
  else if (subValue == 2)
    ESP_LOGI(TAG, "Client subscribed to INDICATE on %s", uuid.c_str());
  else
    ESP_LOGI(TAG, "Client unsubscribed from %s", uuid.c_str());
}

// ============================================================================
// NimBLESecurityCallbacks
// ============================================================================
uint32_t BLEGattServerComponent::onPassKeyRequest() {
  ESP_LOGI(TAG, ">>> Passkey requested — show this on iPhone: %06" PRIu32,
           this->passkey_);
  return this->passkey_;
}

bool BLEGattServerComponent::onConfirmPIN(uint32_t pin) {
  ESP_LOGI(TAG, "Confirm PIN: %06" PRIu32 " — accepting", pin);
  return true;
}

void BLEGattServerComponent::onAuthenticationComplete(
    ble_gap_conn_desc *desc) {
  if (!desc->sec_state.encrypted) {
    ESP_LOGW(TAG, "Link not encrypted — disconnecting for security");
    NimBLEDevice::getServer()->disconnect(desc->conn_handle);
    return;
  }
  ESP_LOGI(TAG, "Auth complete — encrypted=%s  bonded=%s",
           desc->sec_state.encrypted ? "yes" : "no",
           desc->sec_state.bonded ? "yes" : "no");
}

bool BLEGattServerComponent::onSecurityRequest() {
  ESP_LOGI(TAG, "Security request received — accepting");
  return true;
}

}  // namespace ble_gatt_server
}  // namespace esphome
