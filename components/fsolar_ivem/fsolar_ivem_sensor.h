#pragma once

#include <vector>

#include "esphome/components/modbus_controller/modbus_controller.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/core/component.h"
#include "esphome/core/log.h"

namespace esphome {
namespace fsolar_ivem {

class FsolarIvemSensor : public Component,
                         public sensor::Sensor,
                         public modbus_controller::SensorItem {
 public:
  FsolarIvemSensor(modbus_controller::ModbusRegisterType register_type, uint16_t start_address, uint8_t offset,
                   uint32_t bitmask, modbus_controller::SensorValueType value_type, int register_count,
                   uint16_t skip_updates, bool force_new_range) {
    this->register_type = register_type;
    this->start_address = start_address;
    this->offset = offset;
    this->bitmask = bitmask;
    this->sensor_value_type = value_type;
    this->register_count = register_count;
    this->skip_updates = skip_updates;
    this->force_new_range = force_new_range;
  }

  void parse_and_publish(const std::vector<uint8_t> &data) override {
    float result = modbus_controller::payload_to_float(data, *this);

    if (this->transform_func_.has_value()) {
      auto value = (*this->transform_func_)(this, result, data);
      if (value.has_value()) {
        ESP_LOGV("fsolar_ivem.sensor", "Value overwritten by lambda");
        result = value.value();
      }
    }

    ESP_LOGD("fsolar_ivem.sensor", "Sensor new state: %.02f", result);
    this->publish_state(result);
  }

  void dump_config() override {
    ESP_LOGCONFIG("fsolar_ivem.sensor", "Fsolar IVEM Sensor '%s'", this->get_name().c_str());
  }

  using transform_func_t = optional<float> (*)(FsolarIvemSensor *, float, const std::vector<uint8_t> &);
  void set_template(transform_func_t f) { this->transform_func_ = f; }

 protected:
  optional<transform_func_t> transform_func_{nullopt};
};

}  // namespace fsolar_ivem
}  // namespace esphome
