import esphome.codegen as cg
from esphome.components import button as button_component
from esphome.components import number as number_component
from esphome.components import select as select_component
from esphome.components import text_sensor as text_sensor_component
from esphome.components.modbus_controller import ModbusController
from esphome.components.modbus_controller.const import CONF_MODBUS_CONTROLLER_ID
import esphome.config_validation as cv
from esphome.const import CONF_ID
from esphome.const import ENTITY_CATEGORY_CONFIG
from esphome.const import ENTITY_CATEGORY_DIAGNOSTIC
from esphome.cpp_generator import RawStatement

AUTO_LOAD = ["button", "modbus_controller", "number", "select", "text_sensor"]
DEPENDENCIES = ["button", "modbus_controller", "number", "select", "text_sensor"]
CODEOWNERS = []

fsolar_ivem_ns = cg.esphome_ns.namespace("fsolar_ivem")

FsolarIvemRegisterProbe = fsolar_ivem_ns.class_("FsolarIvemRegisterProbe", cg.Component)
FsolarIvemProbeAddressNumber = fsolar_ivem_ns.class_(
    "FsolarIvemProbeAddressNumber",
    number_component.Number,
    cg.Parented.template(FsolarIvemRegisterProbe),
)
FsolarIvemProbeCountNumber = fsolar_ivem_ns.class_(
    "FsolarIvemProbeCountNumber",
    number_component.Number,
    cg.Parented.template(FsolarIvemRegisterProbe),
)
FsolarIvemProbeRegisterTypeSelect = fsolar_ivem_ns.class_(
    "FsolarIvemProbeRegisterTypeSelect",
    select_component.Select,
    cg.Parented.template(FsolarIvemRegisterProbe),
)
FsolarIvemProbeReadButton = fsolar_ivem_ns.class_(
    "FsolarIvemProbeReadButton",
    button_component.Button,
    cg.Parented.template(FsolarIvemRegisterProbe),
)
FsolarIvemProbeTextSensor = fsolar_ivem_ns.class_(
    "FsolarIvemProbeTextSensor",
    text_sensor_component.TextSensor,
)

CONF_PROBE_ADDRESS = "probe_address"
CONF_PROBE_COUNT = "probe_count"
CONF_PROBE_READ = "probe_read"
CONF_PROBE_REGISTER_TYPE = "probe_register_type"
CONF_PROBE_RESULT = "probe_result"
CONF_PROBE_STATUS = "probe_status"

LOCAL_REGISTER_PROBE_HEADER = "esphome/components/fsolar_ivem/fsolar_ivem_register_probe.h"
PROBE_REGISTER_TYPE_OPTIONS = ["Holding", "Input"]

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(FsolarIvemRegisterProbe),
        cv.GenerateID(CONF_MODBUS_CONTROLLER_ID): cv.use_id(ModbusController),
        cv.Required(CONF_PROBE_ADDRESS): number_component.number_schema(
            FsolarIvemProbeAddressNumber,
            entity_category=ENTITY_CATEGORY_CONFIG,
            icon="mdi:counter",
        ),
        cv.Required(CONF_PROBE_COUNT): number_component.number_schema(
            FsolarIvemProbeCountNumber,
            entity_category=ENTITY_CATEGORY_CONFIG,
            icon="mdi:counter",
        ),
        cv.Required(CONF_PROBE_REGISTER_TYPE): select_component.select_schema(
            FsolarIvemProbeRegisterTypeSelect,
            entity_category=ENTITY_CATEGORY_CONFIG,
            icon="mdi:swap-horizontal",
        ),
        cv.Required(CONF_PROBE_READ): button_component.button_schema(
            FsolarIvemProbeReadButton,
            entity_category=ENTITY_CATEGORY_CONFIG,
            icon="mdi:database-search",
        ),
        cv.Required(CONF_PROBE_STATUS): text_sensor_component.text_sensor_schema(
            FsolarIvemProbeTextSensor,
            entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
            icon="mdi:information-outline",
        ),
        cv.Required(CONF_PROBE_RESULT): text_sensor_component.text_sensor_schema(
            FsolarIvemProbeTextSensor,
            entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
            icon="mdi:format-list-bulleted",
        ),
    }
).extend(cv.COMPONENT_SCHEMA)


async def to_code(config: dict) -> None:
    cg.add_global(RawStatement(f'#include "{LOCAL_REGISTER_PROBE_HEADER}"'))

    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    parent = await cg.get_variable(config[CONF_MODBUS_CONTROLLER_ID])
    cg.add(var.set_parent(parent))

    probe_address = await number_component.new_number(
        config[CONF_PROBE_ADDRESS],
        min_value=1,
        max_value=65535,
        step=1,
    )
    await cg.register_parented(probe_address, var)
    cg.add(var.set_probe_address_number(probe_address))

    probe_count = await number_component.new_number(
        config[CONF_PROBE_COUNT],
        min_value=1,
        max_value=20,
        step=1,
    )
    await cg.register_parented(probe_count, var)
    cg.add(var.set_probe_count_number(probe_count))

    probe_register_type = await select_component.new_select(
        config[CONF_PROBE_REGISTER_TYPE],
        options=PROBE_REGISTER_TYPE_OPTIONS,
    )
    await cg.register_parented(probe_register_type, var)
    cg.add(var.set_probe_register_type_select(probe_register_type))

    probe_read = await button_component.new_button(config[CONF_PROBE_READ])
    await cg.register_parented(probe_read, var)
    cg.add(var.set_probe_read_button(probe_read))

    probe_status = await text_sensor_component.new_text_sensor(config[CONF_PROBE_STATUS])
    cg.add(var.set_probe_status_text_sensor(probe_status))

    probe_result = await text_sensor_component.new_text_sensor(config[CONF_PROBE_RESULT])
    cg.add(var.set_probe_result_text_sensor(probe_result))
