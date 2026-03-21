from dataclasses import dataclass

import esphome.codegen as cg
from esphome.components import binary_sensor
import esphome.config_validation as cv
from esphome.cpp_generator import RawStatement
from esphome.const import DEVICE_CLASS_CONNECTIVITY, DEVICE_CLASS_PROBLEM

from esphome.components.modbus_controller import (
    ModbusController,
    ModbusRegisterType,
    SensorItem,
)
from esphome.components.modbus_controller.const import CONF_MODBUS_CONTROLLER_ID

from . import fsolar_ivem_ns

DEPENDENCIES = ["modbus_controller"]
CODEOWNERS = []

CONF_BMS_CHARGE_STOPPED = "bms_charge_stopped"
CONF_BMS_COMMUNICATION_CONNECTED = "bms_communication_connected"
CONF_BMS_DISCHARGE_STOPPED = "bms_discharge_stopped"
CONF_BMS_FORCED_CHARGE = "bms_forced_charge"
CONF_BMS_VERSION_MISMATCH = "bms_version_mismatch"

FsolarIvemBinarySensor = fsolar_ivem_ns.class_(
    "FsolarIvemBinarySensor", cg.Component, binary_sensor.BinarySensor, SensorItem
)
LOCAL_BINARY_SENSOR_HEADER = "esphome/components/fsolar_ivem/fsolar_ivem_binary_sensor.h"


@dataclass(frozen=True)
class BinarySensorSpec:
    address: int
    bitmask: int
    device_class: str | None = None
    entity_category: str | None = None
    icon: str | None = None


BINARY_SENSORS: dict[str, BinarySensorSpec] = {
    CONF_BMS_COMMUNICATION_CONNECTED: BinarySensorSpec(
        address=4400,
        bitmask=0x01,
        device_class=DEVICE_CLASS_CONNECTIVITY,
    ),
    CONF_BMS_VERSION_MISMATCH: BinarySensorSpec(
        address=4400,
        bitmask=0x02,
        device_class=DEVICE_CLASS_PROBLEM,
    ),
    CONF_BMS_FORCED_CHARGE: BinarySensorSpec(address=4400, bitmask=0x04),
    CONF_BMS_CHARGE_STOPPED: BinarySensorSpec(address=4400, bitmask=0x08),
    CONF_BMS_DISCHARGE_STOPPED: BinarySensorSpec(address=4400, bitmask=0x10),
}


def _binary_sensor_schema(spec: BinarySensorSpec) -> cv.Schema:
    kwargs: dict[str, object] = {}
    if spec.device_class is not None:
        kwargs["device_class"] = spec.device_class
    if spec.entity_category is not None:
        kwargs["entity_category"] = spec.entity_category
    if spec.icon is not None:
        kwargs["icon"] = spec.icon
    return binary_sensor.binary_sensor_schema(FsolarIvemBinarySensor, **kwargs)


CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_MODBUS_CONTROLLER_ID): cv.use_id(ModbusController),
        **{
            cv.Optional(key): _binary_sensor_schema(spec)
            for key, spec in BINARY_SENSORS.items()
        },
    }
)


async def _register_binary_sensor(parent: cg.MockObj, spec: BinarySensorSpec, config: dict) -> None:
    var = cg.new_Pvariable(
        config["id"],
        ModbusRegisterType.HOLDING,
        spec.address,
        0,
        spec.bitmask,
        0,
        False,
    )
    await cg.register_component(var, config)
    await binary_sensor.register_binary_sensor(var, config)
    cg.add(parent.add_sensor_item(var))


async def to_code(config: dict) -> None:
    cg.add_global(RawStatement(f'#include "{LOCAL_BINARY_SENSOR_HEADER}"'))
    parent = await cg.get_variable(config[CONF_MODBUS_CONTROLLER_ID])

    for key, spec in BINARY_SENSORS.items():
        binary_sensor_config = config.get(key)
        if binary_sensor_config is None:
            continue
        await _register_binary_sensor(parent, spec, binary_sensor_config)
