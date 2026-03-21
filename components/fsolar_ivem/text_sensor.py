from dataclasses import dataclass

import esphome.codegen as cg
from esphome.components import text_sensor
import esphome.config_validation as cv
from esphome.cpp_generator import RawStatement
from esphome.core import Lambda
from esphome.const import ENTITY_CATEGORY_DIAGNOSTIC

from esphome.components.modbus_controller import (
    ModbusController,
    ModbusRegisterType,
    SensorItem,
)
from esphome.components.modbus_controller.const import CONF_MODBUS_CONTROLLER_ID

from . import fsolar_ivem_ns

DEPENDENCIES = ["modbus_controller"]
CODEOWNERS = []

CONF_SMART_PORT_STATUS = "smart_port_status"

FsolarIvemTextSensor = fsolar_ivem_ns.class_(
    "FsolarIvemTextSensor", cg.Component, text_sensor.TextSensor, SensorItem
)
LOCAL_TEXT_SENSOR_HEADER = "esphome/components/fsolar_ivem/fsolar_ivem_text_sensor.h"
RawEncoding_ns = fsolar_ivem_ns.namespace("RawEncoding")
RawEncoding = RawEncoding_ns.enum("RawEncoding")


@dataclass(frozen=True)
class TextSensorSpec:
    address: int
    register_count: int
    response_size: int
    entity_category: str | None = None
    lambda_expr: str | None = None


TEXT_SENSORS: dict[str, TextSensorSpec] = {
    CONF_SMART_PORT_STATUS: TextSensorSpec(
        address=4461,
        register_count=1,
        response_size=2,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        lambda_expr="""
uint16_t raw = 0;
if (data.size() >= 2) {
  raw = (static_cast<uint16_t>(data[0]) << 8) | static_cast<uint16_t>(data[1]);
}
switch (raw) {
  case 0:
    return std::string("Generator Input");
  case 1:
    return std::string("Smart Load Output");
  default:
    return std::string("Unknown");
}
""",
    ),
}


def _text_sensor_schema(spec: TextSensorSpec) -> cv.Schema:
    kwargs: dict[str, object] = {}
    if spec.entity_category is not None:
        kwargs["entity_category"] = spec.entity_category
    return text_sensor.text_sensor_schema(FsolarIvemTextSensor, **kwargs)


CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_MODBUS_CONTROLLER_ID): cv.use_id(ModbusController),
        **{
            cv.Optional(key): _text_sensor_schema(spec)
            for key, spec in TEXT_SENSORS.items()
        },
    }
)


async def _register_text_sensor(parent: cg.MockObj, spec: TextSensorSpec, config: dict) -> None:
    var = cg.new_Pvariable(
        config["id"],
        ModbusRegisterType.HOLDING,
        spec.address,
        0,
        spec.register_count,
        spec.response_size,
        RawEncoding.NONE,
        0,
        False,
    )
    await cg.register_component(var, config)
    await text_sensor.register_text_sensor(var, config)
    cg.add(parent.add_sensor_item(var))

    if spec.lambda_expr is not None:
        template_ = await cg.process_lambda(
            Lambda(spec.lambda_expr),
            [
                (FsolarIvemTextSensor.operator("ptr"), "item"),
                (cg.std_string, "x"),
                (
                    cg.std_vector.template(cg.uint8).operator("const").operator("ref"),
                    "data",
                ),
            ],
            return_type=cg.optional.template(cg.std_string),
        )
        cg.add(var.set_template(template_))


async def to_code(config: dict) -> None:
    cg.add_global(RawStatement(f'#include "{LOCAL_TEXT_SENSOR_HEADER}"'))
    parent = await cg.get_variable(config[CONF_MODBUS_CONTROLLER_ID])

    for key, spec in TEXT_SENSORS.items():
        text_sensor_config = config.get(key)
        if text_sensor_config is None:
            continue
        await _register_text_sensor(parent, spec, text_sensor_config)
