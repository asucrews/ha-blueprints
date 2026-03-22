"""ESPHome custom component: BLE GATT Server.

Allows an ESP32 to act as a BLE GATT peripheral, discoverable and connectable
from iOS (iPhone/iPad) and Android devices.
"""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import automation
from esphome.const import CONF_ID, CONF_TRIGGER_ID

# --------------------------------------------------------------------------
# Namespace / class references
# --------------------------------------------------------------------------
ble_gatt_server_ns = cg.esphome_ns.namespace("ble_gatt_server")

BLEGattServerComponent = ble_gatt_server_ns.class_(
    "BLEGattServerComponent", cg.Component
)

# Actions
BLENotifyAction   = ble_gatt_server_ns.class_("BLENotifyAction",   automation.Action)
BLESetValueAction = ble_gatt_server_ns.class_("BLESetValueAction", automation.Action)

# Triggers
BLEOnWriteTrigger      = ble_gatt_server_ns.class_("Trigger", automation.Trigger.template(cg.std_string, cg.std_string))
BLEOnConnectTrigger    = ble_gatt_server_ns.class_("Trigger", automation.Trigger.template())
BLEOnDisconnectTrigger = ble_gatt_server_ns.class_("Trigger", automation.Trigger.template())

# --------------------------------------------------------------------------
# Property flag helpers
# --------------------------------------------------------------------------
PROPERTY_FLAGS = {
    "read":           0x0001,
    "read_enc":       0x0002,
    "read_authen":    0x0004,
    "write":          0x0008,
    "write_nr":       0x0010,   # write without response
    "notify":         0x0020,
    "indicate":       0x0040,
    "write_enc":      0x0080,
    "write_authen":   0x0100,
    "broadcast":      0x0200,
}


def _properties_to_int(props):
    """Convert a list of property names to a bitmask integer."""
    mask = 0
    for p in props:
        p = p.lower()
        if p not in PROPERTY_FLAGS:
            raise cv.Invalid(
                f"Unknown BLE property '{p}'. Valid: {list(PROPERTY_FLAGS.keys())}"
            )
        mask |= PROPERTY_FLAGS[p]
    return mask


# --------------------------------------------------------------------------
# Characteristic sub-schema
# --------------------------------------------------------------------------
CONF_CHARACTERISTICS = "characteristics"
CONF_UUID            = "uuid"
CONF_PROPERTIES      = "properties"
CONF_INITIAL_VALUE   = "initial_value"

CHARACTERISTIC_SCHEMA = cv.Schema(
    {
        cv.Required(CONF_UUID): cv.string_strict,
        cv.Required(CONF_PROPERTIES): cv.ensure_list(
            cv.one_of(*PROPERTY_FLAGS.keys(), lower=True)
        ),
        cv.Optional(CONF_INITIAL_VALUE, default=""): cv.string,
    }
)

# --------------------------------------------------------------------------
# Trigger sub-schemas
# --------------------------------------------------------------------------
CONF_ON_WRITE      = "on_write"
CONF_ON_CONNECT    = "on_connect"
CONF_ON_DISCONNECT = "on_disconnect"

# --------------------------------------------------------------------------
# Top-level component schema
# --------------------------------------------------------------------------
CONF_DEVICE_NAME    = "device_name"
CONF_SERVICE_UUID   = "service_uuid"
CONF_PAIRING        = "pairing"
CONF_PASSKEY        = "passkey"
CONF_MAX_CONN       = "max_connections"

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(BLEGattServerComponent),

        cv.Required(CONF_DEVICE_NAME): cv.string_strict,
        cv.Required(CONF_SERVICE_UUID): cv.string_strict,

        cv.Optional(CONF_PAIRING, default=False): cv.boolean,
        cv.Optional(CONF_PASSKEY, default=123456): cv.int_range(min=0, max=999999),
        cv.Optional(CONF_MAX_CONN, default=3): cv.int_range(min=1, max=9),

        cv.Optional(CONF_CHARACTERISTICS, default=[]): cv.ensure_list(
            CHARACTERISTIC_SCHEMA
        ),

        # Automation triggers
        cv.Optional(CONF_ON_WRITE): automation.validate_automation(
            {
                cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(
                    automation.Trigger.template(cg.std_string, cg.std_string)
                )
            }
        ),
        cv.Optional(CONF_ON_CONNECT): automation.validate_automation(
            {cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(automation.Trigger.template())}
        ),
        cv.Optional(CONF_ON_DISCONNECT): automation.validate_automation(
            {cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(automation.Trigger.template())}
        ),
    }
).extend(cv.COMPONENT_SCHEMA)


# --------------------------------------------------------------------------
# Code generation
# --------------------------------------------------------------------------
async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    # Basic config
    cg.add(var.set_device_name(config[CONF_DEVICE_NAME]))
    cg.add(var.set_service_uuid(config[CONF_SERVICE_UUID]))
    cg.add(var.set_pairing_enabled(config[CONF_PAIRING]))
    cg.add(var.set_passkey(config[CONF_PASSKEY]))
    cg.add(var.set_max_connections(config[CONF_MAX_CONN]))

    # Characteristics
    CharCfg = ble_gatt_server_ns.struct("CharacteristicConfig")
    for ch in config[CONF_CHARACTERISTICS]:
        props = _properties_to_int(ch[CONF_PROPERTIES])
        cfg_var = cg.StructInitializer(
            CharCfg,
            ("uuid",          ch[CONF_UUID]),
            ("properties",    props),
            ("initial_value", ch[CONF_INITIAL_VALUE]),
        )
        cg.add(var.add_characteristic(cfg_var))

    # on_write trigger
    for conf in config.get(CONF_ON_WRITE, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID],
                                   cg.RawExpression("decltype(std::declval<esphome::ble_gatt_server::BLEGattServerComponent>().get_on_write_trigger())()"))
        await automation.build_automation(
            var.get_on_write_trigger(), [(cg.std_string, "uuid"), (cg.std_string, "value")], conf
        )

    # on_connect trigger
    for conf in config.get(CONF_ON_CONNECT, []):
        await automation.build_automation(var.get_on_connect_trigger(), [], conf)

    # on_disconnect trigger
    for conf in config.get(CONF_ON_DISCONNECT, []):
        await automation.build_automation(var.get_on_disconnect_trigger(), [], conf)

    # NimBLE library dependency
    cg.add_library("h2zero/NimBLE-Arduino", "1.4.2")

    # ESP-IDF / Arduino SDK config needed for BLE + WiFi coexistence
    cg.add_build_flag("-DCONFIG_BT_NIMBLE_ROLE_PERIPHERAL=1")
    cg.add_build_flag("-DCONFIG_BT_NIMBLE_ROLE_BROADCASTER=1")


# --------------------------------------------------------------------------
# Action schemas
# --------------------------------------------------------------------------
CONF_ACTION_UUID  = "uuid"
CONF_ACTION_VALUE = "value"

BLE_NOTIFY_ACTION_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.use_id(BLEGattServerComponent),
        cv.Required(CONF_ACTION_UUID): cv.templatable(cv.string),
        cv.Required(CONF_ACTION_VALUE): cv.templatable(cv.string),
    }
)

BLE_SET_VALUE_ACTION_SCHEMA = BLE_NOTIFY_ACTION_SCHEMA


@automation.register_action(
    "ble_gatt_server.notify", BLENotifyAction, BLE_NOTIFY_ACTION_SCHEMA
)
async def ble_notify_action_to_code(config, action_id, template_arg, args):
    paren = await cg.get_variable(config[CONF_ID])
    var = cg.new_Pvariable(action_id, template_arg, paren)
    template_ = await cg.templatable(config[CONF_ACTION_UUID], args, cg.std_string)
    cg.add(var.set_uuid(template_))
    template_ = await cg.templatable(config[CONF_ACTION_VALUE], args, cg.std_string)
    cg.add(var.set_value(template_))
    return var


@automation.register_action(
    "ble_gatt_server.set_value", BLESetValueAction, BLE_SET_VALUE_ACTION_SCHEMA
)
async def ble_set_value_action_to_code(config, action_id, template_arg, args):
    paren = await cg.get_variable(config[CONF_ID])
    var = cg.new_Pvariable(action_id, template_arg, paren)
    template_ = await cg.templatable(config[CONF_ACTION_UUID], args, cg.std_string)
    cg.add(var.set_uuid(template_))
    template_ = await cg.templatable(config[CONF_ACTION_VALUE], args, cg.std_string)
    cg.add(var.set_value(template_))
    return var
