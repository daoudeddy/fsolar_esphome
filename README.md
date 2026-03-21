# IVEM6048-II Register Map

This document describes the IVEM6048-II addresses currently implemented by the local ESPHome external component in this directory.

## Notes

- All addresses below are Modbus holding register addresses as currently used by the component.
- `Address (dec)` is the decimal register address used in ESPHome config.
- `Address (hex)` is the same address in hexadecimal for easier cross-reference with inverter documentation and Modbus tools.
- `Count` is the register count configured on the entity today. For read entities, larger counts are used to let `modbus_controller` coalesce contiguous telemetry into fewer read ranges.
- Some addresses appear more than once because the same raw register block is exposed in multiple ways, for example a raw numeric sensor plus decoded text or bit flags.
- The external example `examples/esphome/ivem6048-ii-external.yaml` also includes an ESPHome-side register probe helper for testing unknown holding/input registers from Home Assistant through the ESPHome integration.
- Access values:
  - `R`: read only
  - `R/W`: read and write
  - `R bits`: read bit flags from a holding register
  - `R enum`: read/write enum-style select

## Telemetry Sensors

| Address (dec) | Address (hex) | Key | Description | Type | Count | Access | Notes |
| ---: | ---: | --- | --- | --- | ---: | --- | --- |
| 4355 | `0x1103` | `inverter_fault_code` | Inverter Fault Code | `U_WORD` | 1 | R | Diagnostic |
| 4362 | `0x110A` | `battery_power` | Battery Power | `S_WORD` | 8 | R | Grouped read block |
| 4364 | `0x110C` | `inverter_voltage` | Inverter Voltage | `U_WORD` | 1 | R | Scale `x * 0.1` |
| 4365 | `0x110D` | `inverter_current` | Inverter Current | `S_WORD` | 1 | R | Scale `x * 0.1` |
| 4366 | `0x110E` | `inverter_frequency` | Inverter Frequency | `U_WORD` | 1 | R | Scale `x * 0.01` |
| 4367 | `0x110F` | `inverter_power` | Inverter Power | `S_WORD` | 1 | R | |
| 4368 | `0x1110` | `inverter_apparent_power` | Inverter Apparent Power | `U_WORD` | 1 | R | |
| 4369 | `0x1111` | `ac_output_voltage` | AC Output Voltage | `U_WORD` | 1 | R | Scale `x * 0.1` |
| 4375 | `0x1117` | `ac_input_voltage` | AC Input Voltage | `U_WORD` | 3 | R | Grouped read block, scale `x * 0.1` |
| 4377 | `0x1119` | `ac_input_frequency` | AC Input Frequency | `U_WORD` | 1 | R | Scale `x * 0.01` |
| 4502 | `0x1196` | `ac_input_current` | AC Input Current | `U_WORD` | 4 | R | Grouped read block, scale `x * 0.1` |
| 4503 | `0x1197` | `ac_output_current` | AC Output Current | `U_WORD` | 1 | R | Scale `x * 0.1` |
| 4504 | `0x1198` | `battery_current_summary` | Battery Current Signed | `S_WORD` | 1 | R | Scale `x * 0.1` |
| 4505 | `0x1199` | `pv_current_summary` | PV Current | `U_WORD` | 1 | R | Scale `x * 0.1` |
| 4382 | `0x111E` | `load_power` | Load Power | `S_WORD` | 7 | R | Grouped read block |
| 4383 | `0x111F` | `ac_output_apparent_power` | AC Output Apparent Power | `U_WORD` | 1 | R | |
| 4509 | `0x119D` | `ac_input_power` | AC Input Power | `U_WORD` | 4 | R | Grouped read block |
| 4510 | `0x119E` | `ac_output_power` | AC Output Power | `U_WORD` | 1 | R | |
| 4384 | `0x1120` | `load_percentage` | Load Percentage | `U_WORD` | 1 | R | |
| 4385 | `0x1121` | `transformer_temperature` | Transformer Temperature | `S_WORD` | 1 | R | |
| 4386 | `0x1122` | `inverter_temperature` | Inverter Temperature | `S_WORD` | 1 | R | |
| 4387 | `0x1123` | `battery_temperature` | Battery Temperature | `S_WORD` | 1 | R | |
| 4388 | `0x1124` | `bus_voltage` | Bus Voltage | `U_WORD` | 1 | R | Scale `x * 0.1` |
| 4390 | `0x1126` | `pv1_voltage` | PV1 Voltage | `U_WORD` | 5 | R | Grouped read block, scale `x * 0.1` |
| 4393 | `0x1129` | `pv1_current` | PV1 Current | `S_WORD` | 1 | R | Scale `x * 0.1`, clamp negative to zero |
| 4394 | `0x112A` | `pv1_power` | PV1 Power | `S_WORD` | 1 | R | Clamp negative to zero |
| 4395 | `0x112B` | `scc_temperature` | SCC Temperature | `S_WORD` | 14 | R | Grouped read block |
| 4396 | `0x112C` | `scc_charge_mode` | SCC Charge Mode | `U_WORD` | 1 | R | |
| 4400 | `0x1130` | `bms_flags` | BMS Flags Raw | `U_WORD` | 9 | R | Diagnostic, grouped read block |
| 4401 | `0x1131` | `bms_connect_count` | BMS Connect Count | `U_WORD` | 1 | R | Diagnostic |
| 4402 | `0x1132` | `bms_soc` | BMS SoC | `U_WORD` | 1 | R | |
| 4403 | `0x1133` | `bms_cv_voltage` | BMS CV Voltage | `U_WORD` | 1 | R | Scale `x * 0.1` |
| 4404 | `0x1134` | `bms_float_voltage` | BMS Float Voltage | `U_WORD` | 1 | R | Scale `x * 0.1` |
| 4405 | `0x1135` | `bms_cutoff_voltage` | BMS Cutoff Voltage | `U_WORD` | 1 | R | Scale `x * 0.1` |
| 4406 | `0x1136` | `bms_max_charge_current` | BMS Max Charge Current | `U_WORD` | 1 | R | Scale `x * 0.1` |
| 4407 | `0x1137` | `bms_max_discharge_current` | BMS Max Discharge Current | `U_WORD` | 1 | R | Scale `x * 0.1` |
| 4408 | `0x1138` | `bms_fault_code` | BMS Fault Code | `U_WORD` | 1 | R | Diagnostic |
| 4441 | `0x1159` | `pv2_voltage` | PV2 Voltage | `U_WORD` | 3 | R | Grouped read block, scale `x * 0.1` |
| 4442 | `0x115A` | `pv2_current` | PV2 Current | `S_WORD` | 1 | R | Scale `x * 0.1`, clamp negative to zero |
| 4443 | `0x115B` | `pv2_power` | PV2 Power | `S_WORD` | 1 | R | Clamp negative to zero |
| 4453 | `0x1165` | `generator_voltage` | Generator Voltage | `S_WORD` | 9 | R | Grouped read block, scale `x * 0.1` |
| 4454 | `0x1166` | `generator_current` | Generator Current | `S_WORD` | 1 | R | Scale `x * 0.1` |
| 4455 | `0x1167` | `generator_frequency` | Generator Frequency | `S_WORD` | 1 | R | Scale `x * 0.01` |
| 4456 | `0x1168` | `generator_power` | Generator Power | `U_WORD` | 1 | R | |
| 4457 | `0x1169` | `smart_load_voltage` | Smart Load Voltage | `U_WORD` | 1 | R | Scale `x * 0.1` |
| 4458 | `0x116A` | `smart_load_current` | Smart Load Current | `S_WORD` | 1 | R | Scale `x * 0.1` |
| 4459 | `0x116B` | `smart_load_frequency` | Smart Load Frequency | `U_WORD` | 1 | R | Scale `x * 0.01` |
| 4460 | `0x116C` | `smart_load_power` | Smart Load Power | `U_WORD` | 1 | R | |
| 4461 | `0x116D` | `smart_port_status_raw` | Smart Port Status Raw | `U_WORD` | 1 | R | Diagnostic |
| 4500 | `0x1194` | `eq_stage` | EQ Stage | `U_WORD` | 1 | R | |
| 4511 | `0x119F` | `battery_power_summary` | Battery Power Summary | `S_WORD` | 1 | R | Signed summary power |
| 4512 | `0x11A0` | `pv_power_summary` | PV Power Summary | `U_WORD` | 1 | R | Summary power |
| 4608 | `0x1200` | `battery_line_voltage` | Battery Line Voltage | `U_WORD` | 6 | R | Grouped read block, scale `x * 0.1` |
| 4609 | `0x1201` | `battery_charge_discharge_limit_voltage` | Battery Charge/Discharge Limit Voltage | `U_WORD` | 1 | R | Scale `x * 0.1` |
| 4610 | `0x1202` | `battery_max_charge_current_limit` | Battery Max Charge Current Limit | `U_WORD` | 1 | R | Scale `x * 0.1` |
| 4611 | `0x1203` | `battery_max_discharge_current_limit` | Battery Max Discharge Current Limit | `U_WORD` | 1 | R | Scale `x * 0.1` |
| 4612 | `0x1204` | `battery_system_fault_code` | Battery System Fault Code | `U_WORD` | 1 | R | Diagnostic |
| 4613 | `0x1205` | `battery_system_status_state` | Battery System Status State | `U_WORD` | 1 | R | Diagnostic |
| 4620 | `0x120C` | `battery_current` | Battery Current | `S_WORD` | 6 | R | Grouped read block, scale `x * 0.1` |
| 4621 | `0x120D` | `battery_voltage` | Battery Voltage | `U_WORD` | 1 | R | Scale `x * 0.01` |
| 4624 | `0x1210` | `battery_soc` | Battery SoC | `U_WORD` | 1 | R | Scale `x * 0.1` |
| 4625 | `0x1211` | `battery_soh` | Battery SoH | `U_WORD` | 1 | R | Scale `x * 0.1` |

## Bit-Flag Binary Sensors

All of these read from holding register `4400`.

| Address (dec) | Address (hex) | Bitmask | Key | Description | Access |
| ---: | ---: | --- | --- | --- | --- |
| 4400 | `0x1130` | `0x01` | `bms_communication_connected` | BMS Communication Connected | R bits |
| 4400 | `0x1130` | `0x02` | `bms_version_mismatch` | BMS Version Mismatch | R bits |
| 4400 | `0x1130` | `0x04` | `bms_forced_charge` | BMS Forced Charge | R bits |
| 4400 | `0x1130` | `0x08` | `bms_charge_stopped` | BMS Charge Stopped | R bits |
| 4400 | `0x1130` | `0x10` | `bms_discharge_stopped` | BMS Discharge Stopped | R bits |

## Decoded Text Sensors

| Address (dec) | Address (hex) | Key | Description | Source | Access | Notes |
| ---: | ---: | --- | --- | --- | --- | --- |
| 4461 | `0x116D` | `smart_port_status` | Smart Port Status | Decoded from `smart_port_status_raw` | R | `0 = Generator Input`, `1 = Smart Load Output`, otherwise `Unknown` |

## Writable Number Registers

| Address (dec) | Address (hex) | Key | Description | Type | Count | Access | Notes |
| ---: | ---: | --- | --- | --- | ---: | --- | --- |
| 8479 | `0x211F` | `battery_cut_off_voltage` | Battery Cut-Off Voltage | `U_WORD` | 5 | R/W | Read `x * 0.1`, write `x * 10.0` |
| 8482 | `0x2122` | `battery_cv_charging_voltage` | Battery C.V. Charging Voltage | `U_WORD` | 1 | R/W | Read `x * 0.1`, write `x * 10.0` |
| 8483 | `0x2123` | `battery_floating_charging_voltage` | Battery Floating Charging Voltage | `U_WORD` | 1 | R/W | Read `x * 0.1`, write `x * 10.0` |
| 8494 | `0x212E` | `battery_max_charge_current` | Battery Max Charge Current | `U_WORD` | 3 | R/W | Integer amps |
| 8496 | `0x2130` | `battery_max_ac_charge_current` | Battery Max AC Charge Current | `U_WORD` | 1 | R/W | Integer amps |
| 8534 | `0x2156` | `battery_back_to_charge_voltage` | Battery Back To Charge Voltage | `U_WORD` | 4 | R/W | Read `x * 0.1`, write `x * 10.0` |
| 8537 | `0x2159` | `battery_back_to_discharge_voltage` | Battery Back To Discharge Voltage | `U_WORD` | 1 | R/W | Read `x * 0.1`, write `x * 10.0` |

## Writable Select Registers

| Address (dec) | Address (hex) | Key | Description | Type | Count | Access | Options |
| ---: | ---: | --- | --- | --- | ---: | --- | --- |
| 8489 | `0x2129` | `ac_output_frequency` | AC Output Frequency | `U_WORD` | 15 | R enum | `50Hz=0`, `60Hz=1` |
| 8490 | `0x212A` | `output_source_priority` | Output Source Priority | `U_WORD` | 1 | R enum | `Utility First=0`, `Solar First=1`, `Solar Battery Utility=2` |
| 8491 | `0x212B` | `application_mode` | Application Mode | `U_WORD` | 1 | R enum | `APL=0`, `UPS=1` |
| 8492 | `0x212C` | `charging_source_priority` | Charging Source Priority | `U_WORD` | 1 | R enum | `Solar First=1`, `Solar and Utility First=2`, `Solar Only=3` |
| 8493 | `0x212D` | `battery_type` | Battery Type | `U_WORD` | 1 | R enum | `AGM=0`, `Flood=1`, `User Defined=2`, `LiFePO4=3` |
| 8497 | `0x2131` | `buzzer` | Buzzer | `U_WORD` | 1 | R enum | `Disable=0`, `Enable=1` |
| 8499 | `0x2133` | `overload_restart` | Overload Restart | `U_WORD` | 1 | R enum | `Disable=0`, `Enable=1` |
| 8500 | `0x2134` | `over_temperature_restart` | Over Temperature Restart | `U_WORD` | 1 | R enum | `Disable=0`, `Enable=1` |
| 8501 | `0x2135` | `lcd_backlight` | LCD Backlight | `U_WORD` | 1 | R enum | `Disable=0`, `Enable=1` |
| 8503 | `0x2137` | `overload_to_bypass` | Overload To Bypass | `U_WORD` | 1 | R enum | `Disable=0`, `Enable=1` |

## Coverage Summary

- Read telemetry/status coverage: `4355` through `4625`, with gaps where no entity is currently exposed.
- Writable config coverage: `8479` through `8537`.
- The addresses documented here are the ones currently implemented by the external component, not necessarily every register supported by the inverter firmware.
