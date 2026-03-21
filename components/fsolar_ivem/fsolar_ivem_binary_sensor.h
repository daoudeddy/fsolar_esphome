#pragma once

#include <vector>

#include "esphome/components/binary_sensor/binary_sensor.h"
#include "esphome/components/modbus_controller/modbus_controller.h"
#include "esphome/core/component.h"
#include "esphome/core/log.h"

namespace esphome {
namespace fsolar_ivem {

class FsolarIvemBinarySensor : public Component,
                               public binary_sensor::BinarySensor,
                               public modbus_controller::SensorItem {
 public:
  FsolarIvemBinarySensor(modbus_controller::ModbusRegisterType register_type, uint16_t start_address, uint8_t offset,
                         uint32_t bitmask, uint16_t skip_updates, bool force_new_range) {
    this->register_type = register_type;
    this->start_address = start_address;
    this->offset = offset;
    this->bitmask = bitmask;
    this->sensor_value_type = modbus_controller::SensorValueType::BIT;
    this->skip_updates = skip_updates;
    this->force_new_range = force_new_range;

    if (register_type == modbus_controller::ModbusRegisterType::COIL ||
        register_type == modbus_controller::ModbusRegisterType::DISCRETE_INPUT) {
      this->register_count = offset + 1;
    } else {
      this->register_count = 1;
    }
  }

  void parse_and_publish(const std::vector<uint8_t> &data) override {
    bool value = false;

    switch (this->register_type) {
      case modbus_controller::ModbusRegisterType::DISCRETE_INPUT:
      case modbus_controller::ModbusRegisterType::COIL:
        value = modbus_controller::coil_from_vector(this->offset, data);
        break;
      default:
        value = (modbus_controller::get_data<uint16_t>(data, this->offset) & this->bitmask) != 0;
        break;
    }

    if (this->transform_func_.has_value()) {
      auto transformed = (*this->transform_func_)(this, value, data);
      if (transformed.has_value()) {
        ESP_LOGV("fsolar_ivem.binary_sensor", "Value overwritten by lambda");
        value = transformed.value();
      }
    }

    this->publish_state(value);
  }

  void set_state(bool state) { this->state = state; }

  void dump_config() override {
    ESP_LOGCONFIG("fsolar_ivem.binary_sensor", "Fsolar IVEM Binary Sensor '%s'", this->get_name().c_str());
  }

  using transform_func_t = optional<bool> (*)(FsolarIvemBinarySensor *, bool, const std::vector<uint8_t> &);
  void set_template(transform_func_t f) { this->transform_func_ = f; }

 protected:
  optional<transform_func_t> transform_func_{nullopt};
};

}  // namespace fsolar_ivem
}  // namespace esphome
