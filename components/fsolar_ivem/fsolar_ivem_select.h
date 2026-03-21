#pragma once

#include <algorithm>
#include <string>
#include <utility>
#include <vector>

#include "esphome/components/modbus_controller/modbus_controller.h"
#include "esphome/components/select/select.h"
#include "esphome/core/component.h"
#include "esphome/core/log.h"

namespace esphome {
namespace fsolar_ivem {

class FsolarIvemSelect : public Component,
                         public select::Select,
                         public modbus_controller::SensorItem {
 public:
  FsolarIvemSelect(modbus_controller::SensorValueType sensor_value_type, uint16_t start_address,
                   uint8_t register_count, uint16_t skip_updates, bool force_new_range,
                   std::vector<int64_t> mapping) {
    this->register_type = modbus_controller::ModbusRegisterType::HOLDING;
    this->sensor_value_type = sensor_value_type;
    this->start_address = start_address;
    this->offset = 0;
    this->bitmask = 0xFFFFFFFF;
    this->register_count = register_count;
    this->response_bytes = 0;
    this->skip_updates = skip_updates;
    this->force_new_range = force_new_range;
    this->mapping_ = std::move(mapping);
  }

  using transform_func_t = optional<std::string> (*)(FsolarIvemSelect *const, int64_t,
                                                     const std::vector<uint8_t> &);
  using write_transform_func_t = optional<int64_t> (*)(FsolarIvemSelect *const, const std::string &, int64_t,
                                                       std::vector<uint16_t> &);

  void set_parent(modbus_controller::ModbusController *const parent) { this->parent_ = parent; }
  void set_use_write_mutiple(bool use_write_multiple) { this->use_write_multiple_ = use_write_multiple; }
  void set_optimistic(bool optimistic) { this->optimistic_ = optimistic; }
  void set_template(transform_func_t f) { this->transform_func_ = f; }
  void set_write_template(write_transform_func_t f) { this->write_transform_func_ = f; }

  void dump_config() override {
    ESP_LOGCONFIG("fsolar_ivem.select", "Fsolar IVEM Select '%s'", this->get_name().c_str());
  }

  void parse_and_publish(const std::vector<uint8_t> &data) override {
    int64_t value = modbus_controller::payload_to_number(data, this->sensor_value_type, this->offset, this->bitmask);
    ESP_LOGD("fsolar_ivem.select", "New select value %lld from payload", static_cast<long long>(value));

    optional<std::string> new_state;
    if (this->transform_func_.has_value()) {
      auto transformed = (*this->transform_func_)(this, value, data);
      if (transformed.has_value()) {
        new_state = transformed.value();
        ESP_LOGV("fsolar_ivem.select", "lambda returned option %s", new_state->c_str());
      }
    }

    if (!new_state.has_value()) {
      auto map_it = std::find(this->mapping_.cbegin(), this->mapping_.cend(), value);
      if (map_it != this->mapping_.cend()) {
        size_t index = static_cast<size_t>(std::distance(this->mapping_.cbegin(), map_it));
        ESP_LOGV("fsolar_ivem.select", "Found option %s for value %lld", this->option_at(index),
                 static_cast<long long>(value));
        this->publish_state(index);
        return;
      }

      ESP_LOGE("fsolar_ivem.select", "No option found for mapping %lld", static_cast<long long>(value));
      return;
    }

    this->publish_state(new_state.value());
  }

  void control(size_t index) override {
    if (this->parent_ == nullptr) {
      ESP_LOGW("fsolar_ivem.select", "Cannot write '%s' without a parent controller", this->get_name().c_str());
      return;
    }
    if (index >= this->mapping_.size()) {
      ESP_LOGW("fsolar_ivem.select", "Invalid index %u for '%s'", static_cast<unsigned>(index),
               this->get_name().c_str());
      return;
    }

    optional<int64_t> mapped_value = this->mapping_[index];
    const char *option = this->option_at(index);
    ESP_LOGD("fsolar_ivem.select", "Found value %lld for option '%s'", static_cast<long long>(*mapped_value), option);

    std::vector<uint16_t> payload;
    if (this->write_transform_func_.has_value()) {
      auto transformed = (*this->write_transform_func_)(this, std::string(option), *mapped_value, payload);
      if (transformed.has_value()) {
        mapped_value = transformed.value();
        ESP_LOGV("fsolar_ivem.select", "write_lambda returned mapping value %lld",
                 static_cast<long long>(*mapped_value));
      } else {
        ESP_LOGD("fsolar_ivem.select", "Communication handled by write_lambda - exiting control");
        return;
      }
    }

    if (payload.empty()) {
      modbus_controller::number_to_payload(payload, *mapped_value, this->sensor_value_type);
    } else {
      ESP_LOGV("fsolar_ivem.select", "Using payload from write lambda");
    }

    if (payload.empty()) {
      ESP_LOGW("fsolar_ivem.select", "No payload was created for updating select");
      return;
    }

    const uint16_t write_address = this->start_address + this->offset / 2;
    modbus_controller::ModbusCommandItem write_cmd;
    if (this->register_count == 1 && !this->use_write_multiple_) {
      write_cmd = modbus_controller::ModbusCommandItem::create_write_single_command(this->parent_, write_address,
                                                                                    payload[0]);
    } else {
      write_cmd = modbus_controller::ModbusCommandItem::create_write_multiple_command(
          this->parent_, write_address, this->register_count, payload);
    }

    this->parent_->queue_command(write_cmd);

    if (this->optimistic_) {
      this->publish_state(index);
    }
  }

 protected:
  std::vector<int64_t> mapping_{};
  modbus_controller::ModbusController *parent_{nullptr};
  bool use_write_multiple_{false};
  bool optimistic_{false};
  optional<transform_func_t> transform_func_{nullopt};
  optional<write_transform_func_t> write_transform_func_{nullopt};
};

}  // namespace fsolar_ivem
}  // namespace esphome
