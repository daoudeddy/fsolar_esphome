from dataclasses import dataclass

import esphome.codegen as cg
from esphome.components import sensor
import esphome.config_validation as cv
from esphome.cpp_generator import RawStatement
from esphome.core import Lambda
from esphome.const import (
    CONF_ID,
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_FREQUENCY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_VOLTAGE,
    ENTITY_CATEGORY_DIAGNOSTIC,
    STATE_CLASS_MEASUREMENT,
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

CONF_AC_INPUT_FREQUENCY = "ac_input_frequency"
CONF_AC_INPUT_CURRENT = "ac_input_current"
CONF_AC_INPUT_POWER = "ac_input_power"
CONF_AC_INPUT_VOLTAGE = "ac_input_voltage"
CONF_AC_OUTPUT_CURRENT = "ac_output_current"
CONF_AC_OUTPUT_APPARENT_POWER = "ac_output_apparent_power"
CONF_AC_OUTPUT_POWER = "ac_output_power"
CONF_AC_OUTPUT_VOLTAGE = "ac_output_voltage"
CONF_BATTERY_CHARGE_DISCHARGE_LIMIT_VOLTAGE = "battery_charge_discharge_limit_voltage"
CONF_BATTERY_CURRENT = "battery_current"
CONF_BATTERY_CURRENT_SUMMARY = "battery_current_summary"
CONF_BATTERY_CUTOFF_VOLTAGE = "bms_cutoff_voltage"
CONF_BATTERY_LINE_VOLTAGE = "battery_line_voltage"
CONF_BATTERY_MAX_CHARGE_CURRENT = "bms_max_charge_current"
CONF_BATTERY_MAX_CHARGE_CURRENT_LIMIT = "battery_max_charge_current_limit"
CONF_BATTERY_MAX_DISCHARGE_CURRENT = "bms_max_discharge_current"
CONF_BATTERY_MAX_DISCHARGE_CURRENT_LIMIT = "battery_max_discharge_current_limit"
CONF_BATTERY_POWER = "battery_power"
CONF_BATTERY_POWER_SUMMARY = "battery_power_summary"
CONF_BATTERY_SOC = "battery_soc"
CONF_BATTERY_SOH = "battery_soh"
CONF_BATTERY_SYSTEM_FAULT_CODE = "battery_system_fault_code"
CONF_BATTERY_SYSTEM_STATUS_STATE = "battery_system_status_state"
CONF_BATTERY_TEMPERATURE = "battery_temperature"
CONF_BATTERY_VOLTAGE = "battery_voltage"
CONF_BMS_CONNECT_COUNT = "bms_connect_count"
CONF_BMS_CV_VOLTAGE = "bms_cv_voltage"
CONF_BMS_FAULT_CODE = "bms_fault_code"
CONF_BMS_FLAGS = "bms_flags"
CONF_BMS_FLOAT_VOLTAGE = "bms_float_voltage"
CONF_BMS_SOC = "bms_soc"
CONF_BUS_VOLTAGE = "bus_voltage"
CONF_EQ_STAGE = "eq_stage"
CONF_GENERATOR_CURRENT = "generator_current"
CONF_GENERATOR_FREQUENCY = "generator_frequency"
CONF_GENERATOR_POWER = "generator_power"
CONF_GENERATOR_VOLTAGE = "generator_voltage"
CONF_INVERTER_CURRENT = "inverter_current"
CONF_INVERTER_FAULT_CODE = "inverter_fault_code"
CONF_INVERTER_FREQUENCY = "inverter_frequency"
CONF_INVERTER_APPARENT_POWER = "inverter_apparent_power"
CONF_INVERTER_POWER = "inverter_power"
CONF_INVERTER_TEMPERATURE = "inverter_temperature"
CONF_INVERTER_VOLTAGE = "inverter_voltage"
CONF_LOAD_PERCENTAGE = "load_percentage"
CONF_LOAD_POWER = "load_power"
CONF_PV1_CURRENT = "pv1_current"
CONF_PV1_POWER = "pv1_power"
CONF_PV1_VOLTAGE = "pv1_voltage"
CONF_PV2_CURRENT = "pv2_current"
CONF_PV2_POWER = "pv2_power"
CONF_PV_CURRENT_SUMMARY = "pv_current_summary"
CONF_PV_POWER_SUMMARY = "pv_power_summary"
CONF_PV2_VOLTAGE = "pv2_voltage"
CONF_SCC_CHARGE_MODE = "scc_charge_mode"
CONF_SCC_TEMPERATURE = "scc_temperature"
CONF_SMART_LOAD_CURRENT = "smart_load_current"
CONF_SMART_LOAD_FREQUENCY = "smart_load_frequency"
CONF_SMART_LOAD_POWER = "smart_load_power"
CONF_SMART_LOAD_VOLTAGE = "smart_load_voltage"
CONF_SMART_PORT_STATUS_RAW = "smart_port_status_raw"
CONF_TRANSFORMER_TEMPERATURE = "transformer_temperature"

FsolarIvemSensor = fsolar_ivem_ns.class_(
    "FsolarIvemSensor", cg.Component, sensor.Sensor, SensorItem
)
LOCAL_SENSOR_HEADER = "esphome/components/fsolar_ivem/fsolar_ivem_sensor.h"


@dataclass(frozen=True)
class SensorSpec:
    address: int
    value_type: str
    register_count: int
    accuracy_decimals: int
    unit_of_measurement: str | None = None
    device_class: str | None = None
    state_class: str | None = STATE_CLASS_MEASUREMENT
    entity_category: str | None = None
    icon: str | None = None
    lambda_expr: str | None = None


def _format_float_literal(value: float) -> str:
    literal = f"{value:.10g}"
    if "e" not in literal and "." not in literal:
        literal += ".0"
    return f"{literal}f"


def _scale_lambda(scale: float, *, clamp_min_zero: bool = False) -> str:
    factor = _format_float_literal(scale)
    if clamp_min_zero:
        return f"return x < 0.0f ? 0.0f : x * {factor};"
    return f"return x * {factor};"


def _clamp_nonnegative_lambda() -> str:
    return "return x < 0.0f ? 0.0f : x;"


SENSORS: dict[str, SensorSpec] = {
    CONF_BATTERY_CURRENT: SensorSpec(
        address=4620,
        value_type="S_WORD",
        register_count=6,
        accuracy_decimals=1,
        unit_of_measurement="A",
        device_class=DEVICE_CLASS_CURRENT,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_BATTERY_VOLTAGE: SensorSpec(
        address=4621,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=2,
        unit_of_measurement="V",
        device_class=DEVICE_CLASS_VOLTAGE,
        lambda_expr=_scale_lambda(0.01),
    ),
    CONF_BATTERY_SOC: SensorSpec(
        address=4624,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=1,
        unit_of_measurement="%",
        device_class=DEVICE_CLASS_BATTERY,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_BATTERY_SOH: SensorSpec(
        address=4625,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=1,
        unit_of_measurement="%",
        device_class=DEVICE_CLASS_BATTERY,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_BATTERY_LINE_VOLTAGE: SensorSpec(
        address=4608,
        value_type="U_WORD",
        register_count=6,
        accuracy_decimals=1,
        unit_of_measurement="V",
        device_class=DEVICE_CLASS_VOLTAGE,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_BATTERY_CHARGE_DISCHARGE_LIMIT_VOLTAGE: SensorSpec(
        address=4609,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=1,
        unit_of_measurement="V",
        device_class=DEVICE_CLASS_VOLTAGE,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_BATTERY_MAX_CHARGE_CURRENT_LIMIT: SensorSpec(
        address=4610,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=1,
        unit_of_measurement="A",
        device_class=DEVICE_CLASS_CURRENT,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_BATTERY_MAX_DISCHARGE_CURRENT_LIMIT: SensorSpec(
        address=4611,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=1,
        unit_of_measurement="A",
        device_class=DEVICE_CLASS_CURRENT,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_BATTERY_SYSTEM_FAULT_CODE: SensorSpec(
        address=4612,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=0,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        state_class=None,
    ),
    CONF_BATTERY_SYSTEM_STATUS_STATE: SensorSpec(
        address=4613,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=0,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        state_class=None,
    ),
    CONF_PV1_VOLTAGE: SensorSpec(
        address=4390,
        value_type="U_WORD",
        register_count=5,
        accuracy_decimals=1,
        unit_of_measurement="V",
        device_class=DEVICE_CLASS_VOLTAGE,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_PV1_CURRENT: SensorSpec(
        address=4393,
        value_type="S_WORD",
        register_count=1,
        accuracy_decimals=1,
        unit_of_measurement="A",
        device_class=DEVICE_CLASS_CURRENT,
        lambda_expr=_scale_lambda(0.1, clamp_min_zero=True),
    ),
    CONF_PV1_POWER: SensorSpec(
        address=4394,
        value_type="S_WORD",
        register_count=1,
        accuracy_decimals=0,
        unit_of_measurement="W",
        device_class=DEVICE_CLASS_POWER,
        lambda_expr=_clamp_nonnegative_lambda(),
    ),
    CONF_PV2_VOLTAGE: SensorSpec(
        address=4441,
        value_type="U_WORD",
        register_count=3,
        accuracy_decimals=1,
        unit_of_measurement="V",
        device_class=DEVICE_CLASS_VOLTAGE,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_PV2_CURRENT: SensorSpec(
        address=4442,
        value_type="S_WORD",
        register_count=1,
        accuracy_decimals=1,
        unit_of_measurement="A",
        device_class=DEVICE_CLASS_CURRENT,
        lambda_expr=_scale_lambda(0.1, clamp_min_zero=True),
    ),
    CONF_PV2_POWER: SensorSpec(
        address=4443,
        value_type="S_WORD",
        register_count=1,
        accuracy_decimals=0,
        unit_of_measurement="W",
        device_class=DEVICE_CLASS_POWER,
        lambda_expr=_clamp_nonnegative_lambda(),
    ),
    CONF_INVERTER_FAULT_CODE: SensorSpec(
        address=4355,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=0,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        state_class=None,
    ),
    CONF_BATTERY_POWER: SensorSpec(
        address=4362,
        value_type="S_WORD",
        register_count=8,
        accuracy_decimals=0,
        unit_of_measurement="W",
        device_class=DEVICE_CLASS_POWER,
    ),
    CONF_INVERTER_VOLTAGE: SensorSpec(
        address=4364,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=1,
        unit_of_measurement="V",
        device_class=DEVICE_CLASS_VOLTAGE,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_INVERTER_CURRENT: SensorSpec(
        address=4365,
        value_type="S_WORD",
        register_count=1,
        accuracy_decimals=1,
        unit_of_measurement="A",
        device_class=DEVICE_CLASS_CURRENT,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_INVERTER_FREQUENCY: SensorSpec(
        address=4366,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=2,
        unit_of_measurement="Hz",
        device_class=DEVICE_CLASS_FREQUENCY,
        lambda_expr=_scale_lambda(0.01),
    ),
    CONF_INVERTER_POWER: SensorSpec(
        address=4367,
        value_type="S_WORD",
        register_count=1,
        accuracy_decimals=0,
        unit_of_measurement="W",
        device_class=DEVICE_CLASS_POWER,
    ),
    CONF_INVERTER_APPARENT_POWER: SensorSpec(
        address=4368,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=0,
        unit_of_measurement="VA",
    ),
    CONF_AC_OUTPUT_VOLTAGE: SensorSpec(
        address=4369,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=1,
        unit_of_measurement="V",
        device_class=DEVICE_CLASS_VOLTAGE,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_AC_INPUT_VOLTAGE: SensorSpec(
        address=4375,
        value_type="U_WORD",
        register_count=3,
        accuracy_decimals=1,
        unit_of_measurement="V",
        device_class=DEVICE_CLASS_VOLTAGE,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_AC_INPUT_FREQUENCY: SensorSpec(
        address=4377,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=2,
        unit_of_measurement="Hz",
        device_class=DEVICE_CLASS_FREQUENCY,
        lambda_expr=_scale_lambda(0.01),
    ),
    CONF_AC_INPUT_CURRENT: SensorSpec(
        address=4502,
        value_type="U_WORD",
        register_count=4,
        accuracy_decimals=1,
        unit_of_measurement="A",
        device_class=DEVICE_CLASS_CURRENT,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_AC_OUTPUT_CURRENT: SensorSpec(
        address=4503,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=1,
        unit_of_measurement="A",
        device_class=DEVICE_CLASS_CURRENT,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_BATTERY_CURRENT_SUMMARY: SensorSpec(
        address=4504,
        value_type="S_WORD",
        register_count=1,
        accuracy_decimals=1,
        unit_of_measurement="A",
        device_class=DEVICE_CLASS_CURRENT,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_PV_CURRENT_SUMMARY: SensorSpec(
        address=4505,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=1,
        unit_of_measurement="A",
        device_class=DEVICE_CLASS_CURRENT,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_AC_INPUT_POWER: SensorSpec(
        address=4509,
        value_type="U_WORD",
        register_count=4,
        accuracy_decimals=0,
        unit_of_measurement="W",
        device_class=DEVICE_CLASS_POWER,
    ),
    CONF_AC_OUTPUT_POWER: SensorSpec(
        address=4510,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=0,
        unit_of_measurement="W",
        device_class=DEVICE_CLASS_POWER,
    ),
    CONF_LOAD_POWER: SensorSpec(
        address=4382,
        value_type="S_WORD",
        register_count=7,
        accuracy_decimals=0,
        unit_of_measurement="W",
        device_class=DEVICE_CLASS_POWER,
    ),
    CONF_AC_OUTPUT_APPARENT_POWER: SensorSpec(
        address=4383,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=0,
        unit_of_measurement="VA",
    ),
    CONF_LOAD_PERCENTAGE: SensorSpec(
        address=4384,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=0,
        unit_of_measurement="%",
    ),
    CONF_TRANSFORMER_TEMPERATURE: SensorSpec(
        address=4385,
        value_type="S_WORD",
        register_count=1,
        accuracy_decimals=0,
        unit_of_measurement="°C",
        device_class=DEVICE_CLASS_TEMPERATURE,
    ),
    CONF_INVERTER_TEMPERATURE: SensorSpec(
        address=4386,
        value_type="S_WORD",
        register_count=1,
        accuracy_decimals=0,
        unit_of_measurement="°C",
        device_class=DEVICE_CLASS_TEMPERATURE,
    ),
    CONF_BATTERY_TEMPERATURE: SensorSpec(
        address=4387,
        value_type="S_WORD",
        register_count=1,
        accuracy_decimals=0,
        unit_of_measurement="°C",
        device_class=DEVICE_CLASS_TEMPERATURE,
    ),
    CONF_BUS_VOLTAGE: SensorSpec(
        address=4388,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=1,
        unit_of_measurement="V",
        device_class=DEVICE_CLASS_VOLTAGE,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_SCC_TEMPERATURE: SensorSpec(
        address=4395,
        value_type="S_WORD",
        register_count=14,
        accuracy_decimals=0,
        unit_of_measurement="°C",
        device_class=DEVICE_CLASS_TEMPERATURE,
    ),
    CONF_SCC_CHARGE_MODE: SensorSpec(
        address=4396,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=0,
    ),
    CONF_BMS_FLAGS: SensorSpec(
        address=4400,
        value_type="U_WORD",
        register_count=9,
        accuracy_decimals=0,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        state_class=None,
    ),
    CONF_BMS_CONNECT_COUNT: SensorSpec(
        address=4401,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=0,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        state_class=None,
    ),
    CONF_BMS_SOC: SensorSpec(
        address=4402,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=0,
        unit_of_measurement="%",
        device_class=DEVICE_CLASS_BATTERY,
    ),
    CONF_BMS_CV_VOLTAGE: SensorSpec(
        address=4403,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=1,
        unit_of_measurement="V",
        device_class=DEVICE_CLASS_VOLTAGE,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_BMS_FLOAT_VOLTAGE: SensorSpec(
        address=4404,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=1,
        unit_of_measurement="V",
        device_class=DEVICE_CLASS_VOLTAGE,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_BATTERY_CUTOFF_VOLTAGE: SensorSpec(
        address=4405,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=1,
        unit_of_measurement="V",
        device_class=DEVICE_CLASS_VOLTAGE,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_BATTERY_MAX_CHARGE_CURRENT: SensorSpec(
        address=4406,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=1,
        unit_of_measurement="A",
        device_class=DEVICE_CLASS_CURRENT,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_BATTERY_MAX_DISCHARGE_CURRENT: SensorSpec(
        address=4407,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=1,
        unit_of_measurement="A",
        device_class=DEVICE_CLASS_CURRENT,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_BMS_FAULT_CODE: SensorSpec(
        address=4408,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=0,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        state_class=None,
    ),
    CONF_GENERATOR_VOLTAGE: SensorSpec(
        address=4453,
        value_type="S_WORD",
        register_count=9,
        accuracy_decimals=1,
        unit_of_measurement="V",
        device_class=DEVICE_CLASS_VOLTAGE,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_GENERATOR_CURRENT: SensorSpec(
        address=4454,
        value_type="S_WORD",
        register_count=1,
        accuracy_decimals=1,
        unit_of_measurement="A",
        device_class=DEVICE_CLASS_CURRENT,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_GENERATOR_FREQUENCY: SensorSpec(
        address=4455,
        value_type="S_WORD",
        register_count=1,
        accuracy_decimals=2,
        unit_of_measurement="Hz",
        device_class=DEVICE_CLASS_FREQUENCY,
        lambda_expr=_scale_lambda(0.01),
    ),
    CONF_GENERATOR_POWER: SensorSpec(
        address=4456,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=0,
        unit_of_measurement="W",
        device_class=DEVICE_CLASS_POWER,
    ),
    CONF_SMART_LOAD_VOLTAGE: SensorSpec(
        address=4457,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=1,
        unit_of_measurement="V",
        device_class=DEVICE_CLASS_VOLTAGE,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_SMART_LOAD_CURRENT: SensorSpec(
        address=4458,
        value_type="S_WORD",
        register_count=1,
        accuracy_decimals=1,
        unit_of_measurement="A",
        device_class=DEVICE_CLASS_CURRENT,
        lambda_expr=_scale_lambda(0.1),
    ),
    CONF_SMART_LOAD_FREQUENCY: SensorSpec(
        address=4459,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=2,
        unit_of_measurement="Hz",
        device_class=DEVICE_CLASS_FREQUENCY,
        lambda_expr=_scale_lambda(0.01),
    ),
    CONF_SMART_LOAD_POWER: SensorSpec(
        address=4460,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=0,
        unit_of_measurement="W",
        device_class=DEVICE_CLASS_POWER,
    ),
    CONF_SMART_PORT_STATUS_RAW: SensorSpec(
        address=4461,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=0,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        state_class=None,
    ),
    CONF_EQ_STAGE: SensorSpec(
        address=4500,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=0,
    ),
    CONF_BATTERY_POWER_SUMMARY: SensorSpec(
        address=4511,
        value_type="S_WORD",
        register_count=1,
        accuracy_decimals=0,
        unit_of_measurement="W",
        device_class=DEVICE_CLASS_POWER,
    ),
    CONF_PV_POWER_SUMMARY: SensorSpec(
        address=4512,
        value_type="U_WORD",
        register_count=1,
        accuracy_decimals=0,
        unit_of_measurement="W",
        device_class=DEVICE_CLASS_POWER,
    ),
}


def _sensor_schema(spec: SensorSpec) -> cv.Schema:
    kwargs: dict[str, object] = {"accuracy_decimals": spec.accuracy_decimals}
    if spec.unit_of_measurement is not None:
        kwargs["unit_of_measurement"] = spec.unit_of_measurement
    if spec.device_class is not None:
        kwargs["device_class"] = spec.device_class
    if spec.state_class is not None:
        kwargs["state_class"] = spec.state_class
    if spec.entity_category is not None:
        kwargs["entity_category"] = spec.entity_category
    if spec.icon is not None:
        kwargs["icon"] = spec.icon
    return sensor.sensor_schema(FsolarIvemSensor, **kwargs)


CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_MODBUS_CONTROLLER_ID): cv.use_id(ModbusController),
        **{cv.Optional(key): _sensor_schema(spec) for key, spec in SENSORS.items()},
    }
)


async def _register_sensor(parent: cg.MockObj, spec: SensorSpec, config: dict) -> None:
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
    await sensor.register_sensor(var, config)
    cg.add(parent.add_sensor_item(var))

    if spec.lambda_expr is not None:
        template_ = await cg.process_lambda(
            Lambda(spec.lambda_expr),
            [
                (FsolarIvemSensor.operator("ptr"), "item"),
                (cg.float_, "x"),
                (
                    cg.std_vector.template(cg.uint8).operator("const").operator("ref"),
                    "data",
                ),
            ],
            return_type=cg.optional.template(float),
        )
        cg.add(var.set_template(template_))


async def to_code(config: dict) -> None:
    cg.add_global(RawStatement(f'#include "{LOCAL_SENSOR_HEADER}"'))
    parent = await cg.get_variable(config[CONF_MODBUS_CONTROLLER_ID])

    for key, spec in SENSORS.items():
        sensor_config = config.get(key)
        if sensor_config is None:
            continue
        await _register_sensor(parent, spec, sensor_config)
