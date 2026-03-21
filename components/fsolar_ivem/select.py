from dataclasses import dataclass

import esphome.codegen as cg
from esphome.components import select
import esphome.config_validation as cv
from esphome.cpp_generator import RawStatement
from esphome.const import CONF_ID, ENTITY_CATEGORY_CONFIG

from esphome.components.modbus_controller import (
    ModbusController,
    SENSOR_VALUE_TYPE,
    TYPE_REGISTER_MAP,
    SensorItem,
)
from esphome.components.modbus_controller.const import CONF_MODBUS_CONTROLLER_ID

from . import fsolar_ivem_ns

DEPENDENCIES = ["modbus_controller"]
CODEOWNERS = []

CONF_AC_OUTPUT_FREQUENCY = "ac_output_frequency"
CONF_APPLICATION_MODE = "application_mode"
CONF_BATTERY_TYPE = "battery_type"
CONF_BUZZER = "buzzer"
CONF_CHARGING_SOURCE_PRIORITY = "charging_source_priority"
CONF_LCD_BACKLIGHT = "lcd_backlight"
CONF_OUTPUT_SOURCE_PRIORITY = "output_source_priority"
CONF_OVERLOAD_RESTART = "overload_restart"
CONF_OVERLOAD_TO_BYPASS = "overload_to_bypass"
CONF_OVER_TEMPERATURE_RESTART = "over_temperature_restart"

FsolarIvemSelect = fsolar_ivem_ns.class_(
    "FsolarIvemSelect", cg.Component, select.Select, SensorItem
)
LOCAL_SELECT_HEADER = "esphome/components/fsolar_ivem/fsolar_ivem_select.h"


@dataclass(frozen=True)
class SelectSpec:
    address: int
    options_map: dict[str, int]
    register_count: int | None = None
    value_type: str = "U_WORD"
    entity_category: str | None = ENTITY_CATEGORY_CONFIG


SELECTS: dict[str, SelectSpec] = {
    CONF_AC_OUTPUT_FREQUENCY: SelectSpec(
        address=8489,
        register_count=15,
        options_map={"50Hz": 0, "60Hz": 1},
    ),
    CONF_OUTPUT_SOURCE_PRIORITY: SelectSpec(
        address=8490,
        options_map={
            "Utility First": 0,
            "Solar First": 1,
            "Solar Battery Utility": 2,
        },
    ),
    CONF_APPLICATION_MODE: SelectSpec(
        address=8491,
        options_map={"APL": 0, "UPS": 1},
    ),
    CONF_CHARGING_SOURCE_PRIORITY: SelectSpec(
        address=8492,
        options_map={
            "Solar First": 1,
            "Solar and Utility First": 2,
            "Solar Only": 3,
        },
    ),
    CONF_BATTERY_TYPE: SelectSpec(
        address=8493,
        options_map={"AGM": 0, "Flood": 1, "User Defined": 2, "LiFePO4": 3},
    ),
    CONF_BUZZER: SelectSpec(
        address=8497,
        options_map={"Disable": 0, "Enable": 1},
    ),
    CONF_OVERLOAD_RESTART: SelectSpec(
        address=8499,
        options_map={"Disable": 0, "Enable": 1},
    ),
    CONF_OVER_TEMPERATURE_RESTART: SelectSpec(
        address=8500,
        options_map={"Disable": 0, "Enable": 1},
    ),
    CONF_LCD_BACKLIGHT: SelectSpec(
        address=8501,
        options_map={"Disable": 0, "Enable": 1},
    ),
    CONF_OVERLOAD_TO_BYPASS: SelectSpec(
        address=8503,
        options_map={"Disable": 0, "Enable": 1},
    ),
}


def _select_schema(spec: SelectSpec) -> cv.Schema:
    return select.select_schema(
        FsolarIvemSelect,
        entity_category=spec.entity_category,
    )


CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_MODBUS_CONTROLLER_ID): cv.use_id(ModbusController),
        **{cv.Optional(key): _select_schema(spec) for key, spec in SELECTS.items()},
    }
)


async def _register_select(parent: cg.MockObj, spec: SelectSpec, config: dict) -> None:
    reg_count = spec.register_count
    if reg_count is None:
        reg_count = TYPE_REGISTER_MAP[spec.value_type]

    var = cg.new_Pvariable(
        config[CONF_ID],
        SENSOR_VALUE_TYPE[spec.value_type],
        spec.address,
        reg_count,
        0,
        False,
        list(spec.options_map.values()),
    )
    await cg.register_component(var, config)
    await select.register_select(var, config, options=list(spec.options_map.keys()))
    cg.add(parent.add_sensor_item(var))
    cg.add(var.set_parent(parent))
    cg.add(var.set_use_write_mutiple(False))
    cg.add(var.set_optimistic(False))


async def to_code(config: dict) -> None:
    cg.add_global(RawStatement(f'#include "{LOCAL_SELECT_HEADER}"'))
    parent = await cg.get_variable(config[CONF_MODBUS_CONTROLLER_ID])

    for key, spec in SELECTS.items():
        select_config = config.get(key)
        if select_config is None:
            continue
        await _register_select(parent, spec, select_config)
