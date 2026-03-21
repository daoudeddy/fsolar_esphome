from dataclasses import dataclass

import esphome.codegen as cg
from esphome.components import number
import esphome.config_validation as cv
from esphome.cpp_generator import RawStatement
from esphome.core import Lambda
from esphome.const import (
    CONF_ID,
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_VOLTAGE,
    ENTITY_CATEGORY_CONFIG,
)

from esphome.components.modbus_controller import (
    ModbusController,
    ModbusRegisterType,
    SENSOR_VALUE_TYPE,
    SensorItem,
)
from esphome.components.modbus_controller.const import CONF_MODBUS_CONTROLLER_ID

from . import fsolar_ivem_ns

DEPENDENCIES = ["modbus_controller"]
CODEOWNERS = []

CONF_BATTERY_BACK_TO_CHARGE_VOLTAGE = "battery_back_to_charge_voltage"
CONF_BATTERY_BACK_TO_DISCHARGE_VOLTAGE = "battery_back_to_discharge_voltage"
CONF_BATTERY_CUTOFF_VOLTAGE = "battery_cut_off_voltage"
CONF_BATTERY_CV_CHARGING_VOLTAGE = "battery_cv_charging_voltage"
CONF_BATTERY_FLOATING_CHARGING_VOLTAGE = "battery_floating_charging_voltage"
CONF_BATTERY_MAX_AC_CHARGE_CURRENT = "battery_max_ac_charge_current"
CONF_BATTERY_MAX_CHARGE_CURRENT = "battery_max_charge_current"

FsolarIvemNumber = fsolar_ivem_ns.class_(
    "FsolarIvemNumber", cg.Component, number.Number, SensorItem
)
LOCAL_NUMBER_HEADER = "esphome/components/fsolar_ivem/fsolar_ivem_number.h"


@dataclass(frozen=True)
class NumberSpec:
    address: int
    value_type: str
    register_count: int
    min_value: float
    max_value: float
    step: float
    unit_of_measurement: str | None = None
    device_class: str | None = None
    entity_category: str | None = ENTITY_CATEGORY_CONFIG
    read_lambda: str | None = None
    write_lambda: str | None = None


def _format_float_literal(value: float) -> str:
    literal = f"{value:.10g}"
    if "e" not in literal and "." not in literal:
        literal += ".0"
    return f"{literal}f"


def _scale_lambda(scale: float) -> str:
    return f"return x * {_format_float_literal(scale)};"


NUMBERS: dict[str, NumberSpec] = {
    CONF_BATTERY_CUTOFF_VOLTAGE: NumberSpec(
        address=8479,
        value_type="U_WORD",
        register_count=5,
        min_value=21.0,
        max_value=60.1,
        step=0.1,
        unit_of_measurement="V",
        device_class=DEVICE_CLASS_VOLTAGE,
        read_lambda=_scale_lambda(0.1),
        write_lambda=_scale_lambda(10.0),
    ),
    CONF_BATTERY_CV_CHARGING_VOLTAGE: NumberSpec(
        address=8482,
        value_type="U_WORD",
        register_count=1,
        min_value=21.0,
        max_value=60.1,
        step=0.1,
        unit_of_measurement="V",
        device_class=DEVICE_CLASS_VOLTAGE,
        read_lambda=_scale_lambda(0.1),
        write_lambda=_scale_lambda(10.0),
    ),
    CONF_BATTERY_FLOATING_CHARGING_VOLTAGE: NumberSpec(
        address=8483,
        value_type="U_WORD",
        register_count=1,
        min_value=21.0,
        max_value=60.1,
        step=0.1,
        unit_of_measurement="V",
        device_class=DEVICE_CLASS_VOLTAGE,
        read_lambda=_scale_lambda(0.1),
        write_lambda=_scale_lambda(10.0),
    ),
    CONF_BATTERY_MAX_CHARGE_CURRENT: NumberSpec(
        address=8494,
        value_type="U_WORD",
        register_count=3,
        min_value=10.0,
        max_value=100.0,
        step=1.0,
        unit_of_measurement="A",
        device_class=DEVICE_CLASS_CURRENT,
    ),
    CONF_BATTERY_MAX_AC_CHARGE_CURRENT: NumberSpec(
        address=8496,
        value_type="U_WORD",
        register_count=1,
        min_value=10.0,
        max_value=100.0,
        step=1.0,
        unit_of_measurement="A",
        device_class=DEVICE_CLASS_CURRENT,
    ),
    CONF_BATTERY_BACK_TO_CHARGE_VOLTAGE: NumberSpec(
        address=8534,
        value_type="U_WORD",
        register_count=4,
        min_value=21.0,
        max_value=60.1,
        step=0.1,
        unit_of_measurement="V",
        device_class=DEVICE_CLASS_VOLTAGE,
        read_lambda=_scale_lambda(0.1),
        write_lambda=_scale_lambda(10.0),
    ),
    CONF_BATTERY_BACK_TO_DISCHARGE_VOLTAGE: NumberSpec(
        address=8537,
        value_type="U_WORD",
        register_count=1,
        min_value=21.0,
        max_value=60.1,
        step=0.1,
        unit_of_measurement="V",
        device_class=DEVICE_CLASS_VOLTAGE,
        read_lambda=_scale_lambda(0.1),
        write_lambda=_scale_lambda(10.0),
    ),
}


def _number_schema(spec: NumberSpec) -> cv.Schema:
    return number.number_schema(
        FsolarIvemNumber,
        device_class=spec.device_class,
        entity_category=spec.entity_category,
        unit_of_measurement=spec.unit_of_measurement,
    )


CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_MODBUS_CONTROLLER_ID): cv.use_id(ModbusController),
        **{cv.Optional(key): _number_schema(spec) for key, spec in NUMBERS.items()},
    }
)


async def _register_number(parent: cg.MockObj, spec: NumberSpec, config: dict) -> None:
    var = cg.new_Pvariable(
        config[CONF_ID],
        ModbusRegisterType.HOLDING,
        spec.address,
        0,
        0xFFFFFFFF,
        SENSOR_VALUE_TYPE[spec.value_type],
        spec.register_count,
        0,
        False,
    )
    await cg.register_component(var, config)
    await number.register_number(
        var,
        config,
        min_value=spec.min_value,
        max_value=spec.max_value,
        step=spec.step,
    )
    cg.add(var.set_parent(parent))
    cg.add(parent.add_sensor_item(var))

    if spec.read_lambda is not None:
        template_ = await cg.process_lambda(
            Lambda(spec.read_lambda),
            [
                (FsolarIvemNumber.operator("ptr"), "item"),
                (cg.float_, "x"),
                (
                    cg.std_vector.template(cg.uint8).operator("const").operator("ref"),
                    "data",
                ),
            ],
            return_type=cg.optional.template(float),
        )
        cg.add(var.set_template(template_))

    if spec.write_lambda is not None:
        template_ = await cg.process_lambda(
            Lambda(spec.write_lambda),
            [
                (FsolarIvemNumber.operator("ptr"), "item"),
                (cg.float_, "x"),
                (cg.std_vector.template(cg.uint16).operator("ref"), "payload"),
            ],
            return_type=cg.optional.template(float),
        )
        cg.add(var.set_write_template(template_))


async def to_code(config: dict) -> None:
    cg.add_global(RawStatement(f'#include "{LOCAL_NUMBER_HEADER}"'))
    parent = await cg.get_variable(config[CONF_MODBUS_CONTROLLER_ID])

    for key, spec in NUMBERS.items():
        number_config = config.get(key)
        if number_config is None:
            continue
        await _register_number(parent, spec, number_config)
