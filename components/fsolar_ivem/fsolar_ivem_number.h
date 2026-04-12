#pragma once

#include <vector>

#include "esphome/components/modbus_controller/modbus_controller.h"
#include "esphome/components/number/number.h"
#include "esphome/core/component.h"
#include "esphome/core/log.h"

namespace esphome {
namespace fsolar_ivem {

class FsolarIvemNumber : public number::Number,
                         public Component,
                         public modbus_controller::SensorItem {
 public:
  FsolarIvemNumber(modbus_controller::ModbusRegisterType register_type, uint16_t start_address, uint8_t offset,
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

  void dump_config() override {
    ESP_LOGCONFIG("fsolar_ivem.number", "Fsolar IVEM Number '%s'", this->get_name().c_str());
  }

  void parse_and_publish(const std::vector<uint8_t> &data) override {
    float result = modbus_controller::payload_to_float(data, *this) / this->multiply_by_;

    if (this->transform_func_.has_value()) {
      auto value = (*this->transform_func_)(this, result, data);
      if (value.has_value()) {
        ESP_LOGV("fsolar_ivem.number", "Value overwritten by lambda");
        result = value.value();
      }
    }

    ESP_LOGD("fsolar_ivem.number", "Number new state : %.02f", result);
    this->publish_state(result);
  }

  float get_setup_priority() const override { return setup_priority::HARDWARE; }

  void set_parent(modbus_controller::ModbusController *parent) { this->parent_ = parent; }
  void set_write_multiply(float factor) { this->multiply_by_ = factor; }

  using transform_func_t = optional<float> (*)(FsolarIvemNumber *, float, const std::vector<uint8_t> &);
  using write_transform_func_t = optional<float> (*)(FsolarIvemNumber *, float, std::vector<uint16_t> &);
  void set_template(transform_func_t f) { this->transform_func_ = f; }
  void set_write_template(write_transform_func_t f) { this->write_transform_func_ = f; }
  void set_use_write_mutiple(bool use_write_multiple) { this->use_write_multiple_ = use_write_multiple; }

 protected:
  void control(float value) override {
    if (this->parent_ == nullptr) {
      ESP_LOGW("fsolar_ivem.number", "Cannot write '%s' without a parent controller", this->get_name().c_str());
      return;
    }

    modbus_controller::ModbusCommandItem write_cmd;
    std::vector<uint16_t> payload;
    float write_value = value;

    if (this->write_transform_func_.has_value()) {
      auto transformed = (*this->write_transform_func_)(this, value, payload);
      if (transformed.has_value()) {
        ESP_LOGV("fsolar_ivem.number", "Value overwritten by lambda");
        write_value = transformed.value();
      } else {
        ESP_LOGV("fsolar_ivem.number", "Communication handled by lambda - exiting control");
        return;
      }
    } else {
      write_value = this->multiply_by_ * write_value;
    }

    if (!payload.empty()) {
      write_cmd = modbus_controller::ModbusCommandItem::create_custom_command(
          this->parent_, payload,
          [](modbus_controller::ModbusRegisterType, uint16_t, const std::vector<uint8_t> &) {});
    } else {
      payload = modbus_controller::float_to_payload(write_value, this->sensor_value_type);
      if (payload.empty()) {
        ESP_LOGW("fsolar_ivem.number", "No payload was created for '%s'", this->get_name().c_str());
        return;
      }

      const uint16_t write_address = this->start_address + this->offset / 2;
      ESP_LOGD("fsolar_ivem.number",
               "Updating register: connected Sensor=%s start address=0x%X register count=%d new value=%.02f (val=%.02f)",
               this->get_name().c_str(), this->start_address, this->register_count, value, write_value);

      if (payload.size() == 1 && !this->use_write_multiple_) {
        write_cmd = modbus_controller::ModbusCommandItem::create_write_single_command(this->parent_, write_address,
                                                                                       payload[0]);
      } else {
        write_cmd = modbus_controller::ModbusCommandItem::create_write_multiple_command(
            this->parent_, write_address, this->register_count, payload);
      }
    }

    this->parent_->queue_command(write_cmd);
  }

  optional<transform_func_t> transform_func_{nullopt};
  optional<write_transform_func_t> write_transform_func_{nullopt};
  modbus_controller::ModbusController *parent_{nullptr};
  float multiply_by_{1.0f};
  bool use_write_multiple_{false};
};

}  // namespace fsolar_ivem
}  // namespace esphome
