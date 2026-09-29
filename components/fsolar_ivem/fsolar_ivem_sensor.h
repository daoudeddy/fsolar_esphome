#pragma once

#include "esphome/components/modbus_controller/modbus_controller.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/core/component.h"

#include <span>

namespace esphome::fsolar_ivem {

using modbus_controller::RangeReuse;
using modbus_controller::SensorItem;
using modbus_controller::payload_to_float;
using modbus::helpers::SensorValueType;

class FsolarIvemSensor final : public Component, public sensor::Sensor, public SensorItem {
 public:
  FsolarIvemSensor(modbus::EntityType register_type, uint16_t start_address, uint8_t offset, uint32_t bitmask,
               SensorValueType value_type, RangeReuse reuse_previous_range) {
    this->register_type = register_type;
    this->set_address(start_address);
    this->set_offset_from_start_address(offset);
    this->bitmask = bitmask;
    this->sensor_value_type = value_type;
    this->reuse_previous_range = reuse_previous_range;
  }

  void parse_and_publish(std::span<const uint8_t> data) override;
  void dump_config() override;
  using transform_func_t = optional<float> (*)(FsolarIvemSensor *, float, std::span<const uint8_t>);

  void set_template(transform_func_t f) { this->transform_func_ = f; }

 protected:
  optional<transform_func_t> transform_func_{nullopt};
};

}  // namespace esphome::fsolar_ivem
