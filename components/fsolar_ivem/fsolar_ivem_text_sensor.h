#pragma once

#include <cstdio>
#include <string>
#include <vector>

#include "esphome/components/modbus_controller/modbus_controller.h"
#include "esphome/components/text_sensor/text_sensor.h"
#include "esphome/core/component.h"
#include "esphome/core/log.h"

namespace esphome {
namespace fsolar_ivem {

enum class RawEncoding { NONE = 0, HEXBYTES = 1, COMMA = 2, ANSI = 3 };

class FsolarIvemTextSensor : public Component,
                             public text_sensor::TextSensor,
                             public modbus_controller::SensorItem {
 public:
  FsolarIvemTextSensor(modbus_controller::ModbusRegisterType register_type, uint16_t start_address, uint8_t offset,
                       uint8_t register_count, uint16_t response_bytes, RawEncoding encode, uint16_t skip_updates,
                       bool force_new_range) {
    this->register_type = register_type;
    this->start_address = start_address;
    this->offset = offset;
    this->response_bytes = response_bytes;
    this->register_count = register_count;
    this->encode_ = encode;
    this->skip_updates = skip_updates;
    this->bitmask = 0xFFFFFFFF;
    this->sensor_value_type = modbus_controller::SensorValueType::RAW;
    this->force_new_range = force_new_range;
  }

  void dump_config() override {
    ESP_LOGCONFIG("fsolar_ivem.text_sensor", "Fsolar IVEM Text Sensor '%s'", this->get_name().c_str());
  }

  void parse_and_publish(const std::vector<uint8_t> &data) override {
    std::string output{};
    uint16_t items_left = this->response_bytes;
    size_t index = this->offset;

    while (items_left > 0 && index < data.size()) {
      uint8_t value = data[index];
      switch (this->encode_) {
        case RawEncoding::HEXBYTES: {
          char hex_buf[3];
          std::snprintf(hex_buf, sizeof(hex_buf), "%02x", value);
          output += hex_buf;
          break;
        }
        case RawEncoding::COMMA: {
          char dec_buf[5];
          std::snprintf(dec_buf, sizeof(dec_buf), index != this->offset ? ",%u" : "%u",
                        static_cast<unsigned>(value));
          output += dec_buf;
          break;
        }
        case RawEncoding::ANSI:
          if (value < 0x20) {
            break;
          }
          [[fallthrough]];
        case RawEncoding::NONE:
        default:
          output.push_back(static_cast<char>(value));
          break;
      }
      --items_left;
      ++index;
    }

    if (this->transform_func_.has_value()) {
      auto transformed = (*this->transform_func_)(this, output, data);
      if (transformed.has_value()) {
        ESP_LOGV("fsolar_ivem.text_sensor", "Value overwritten by lambda");
        output = transformed.value();
      }
    }

    this->publish_state(output);
  }

  using transform_func_t = optional<std::string> (*)(FsolarIvemTextSensor *, std::string,
                                                     const std::vector<uint8_t> &);
  void set_template(transform_func_t f) { this->transform_func_ = f; }

 protected:
  optional<transform_func_t> transform_func_{nullopt};
  RawEncoding encode_;
};

}  // namespace fsolar_ivem
}  // namespace esphome
