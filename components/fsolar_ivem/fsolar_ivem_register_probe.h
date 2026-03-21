#pragma once

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdint>
#include <string>
#include <vector>

#include "esphome/components/button/button.h"
#include "esphome/components/modbus_controller/modbus_controller.h"
#include "esphome/components/number/number.h"
#include "esphome/components/select/select.h"
#include "esphome/components/text_sensor/text_sensor.h"
#include "esphome/core/component.h"
#include "esphome/core/helpers.h"
#include "esphome/core/log.h"

namespace esphome {
namespace fsolar_ivem {

static const char *const TAG = "fsolar_ivem.probe";

class FsolarIvemRegisterProbe;

class FsolarIvemProbeAddressNumber : public number::Number, public Parented<FsolarIvemRegisterProbe> {
 protected:
  void control(float value) override;
};

class FsolarIvemProbeCountNumber : public number::Number, public Parented<FsolarIvemRegisterProbe> {
 protected:
  void control(float value) override;
};

class FsolarIvemProbeRegisterTypeSelect : public select::Select, public Parented<FsolarIvemRegisterProbe> {
 protected:
  void control(size_t index) override;
};

class FsolarIvemProbeReadButton : public button::Button, public Parented<FsolarIvemRegisterProbe> {
 protected:
  void press_action() override;
};

class FsolarIvemProbeTextSensor : public text_sensor::TextSensor {};

class FsolarIvemRegisterProbe : public Component {
 public:
  void setup() override {
    if (this->probe_address_number_ != nullptr) {
      this->probe_address_number_->publish_state(this->probe_address_);
    }
    if (this->probe_count_number_ != nullptr) {
      this->probe_count_number_->publish_state(this->probe_count_);
    }
    if (this->probe_register_type_select_ != nullptr) {
      this->probe_register_type_select_->publish_state(this->register_type_label_());
    }
    this->publish_status_("Idle");
    this->publish_result_("");
  }

  void dump_config() override {
    ESP_LOGCONFIG("fsolar_ivem.probe", "Fsolar IVEM Register Probe");
    LOG_NUMBER("  ", "Probe Address", this->probe_address_number_);
    LOG_NUMBER("  ", "Probe Count", this->probe_count_number_);
    LOG_SELECT("  ", "Probe Register Type", this->probe_register_type_select_);
    LOG_BUTTON("  ", "Probe Read", this->probe_read_button_);
    LOG_TEXT_SENSOR("  ", "Probe Status", this->probe_status_text_sensor_);
    LOG_TEXT_SENSOR("  ", "Probe Result", this->probe_result_text_sensor_);
  }

  void set_parent(modbus_controller::ModbusController *parent) { this->parent_ = parent; }

  void set_probe_address(uint16_t value) { this->probe_address_ = value; }
  void set_probe_count(uint16_t value) { this->probe_count_ = std::max<uint16_t>(1, std::min<uint16_t>(20, value)); }
  void set_probe_register_type(size_t index) {
    this->probe_register_type_ = index == 1 ? modbus_controller::ModbusRegisterType::READ
                                            : modbus_controller::ModbusRegisterType::HOLDING;
  }

  uint16_t get_probe_address() const { return this->probe_address_; }
  uint16_t get_probe_count() const { return this->probe_count_; }
  const char *register_type_label_() const {
    return this->probe_register_type_ == modbus_controller::ModbusRegisterType::READ ? "Input" : "Holding";
  }

  void execute_probe() {
    if (this->parent_ == nullptr) {
      this->publish_status_("No modbus controller configured");
      return;
    }
    if (this->probe_pending_) {
      this->publish_status_("Probe already pending");
      return;
    }

    const uint16_t start_address = this->probe_address_;
    const uint16_t register_count = this->probe_count_;
    const auto register_type = this->probe_register_type_;

    this->probe_pending_ = true;
    this->publish_result_("");
    this->publish_status_(
        std::string("Queued ") + this->register_type_label_() + " read @ " + std::to_string(start_address) +
        " count " + std::to_string(register_count));

    this->set_timeout("probe-timeout", 5000, [this]() {
      if (!this->probe_pending_) {
        return;
      }
      this->probe_pending_ = false;
      this->publish_status_("Probe timed out");
    });

    auto command = modbus_controller::ModbusCommandItem::create_read_command(
        this->parent_, register_type, start_address, register_count,
        [this, start_address, register_count](modbus_controller::ModbusRegisterType register_type, uint16_t,
                                              const std::vector<uint8_t> &data) {
          this->cancel_timeout("probe-timeout");
          this->probe_pending_ = false;

          this->publish_result_(this->format_register_values_(start_address, data));

          const char *type_label = register_type == modbus_controller::ModbusRegisterType::READ ? "Input" : "Holding";
          this->publish_status_(std::string("Read ") + type_label + " @ " + std::to_string(start_address) +
                                " count " + std::to_string(register_count) + " ok");
        });
    this->parent_->queue_command(command);
  }

  void set_probe_address_number(number::Number *number) { this->probe_address_number_ = number; }
  void set_probe_count_number(number::Number *number) { this->probe_count_number_ = number; }
  void set_probe_register_type_select(select::Select *select) { this->probe_register_type_select_ = select; }
  void set_probe_read_button(button::Button *button) { this->probe_read_button_ = button; }
  void set_probe_status_text_sensor(text_sensor::TextSensor *text_sensor) {
    this->probe_status_text_sensor_ = text_sensor;
  }
  void set_probe_result_text_sensor(text_sensor::TextSensor *text_sensor) {
    this->probe_result_text_sensor_ = text_sensor;
  }

 protected:
  void publish_status_(const std::string &value) {
    ESP_LOGD("fsolar_ivem.probe", "%s", value.c_str());
    if (this->probe_status_text_sensor_ != nullptr) {
      this->probe_status_text_sensor_->publish_state(value);
    }
  }

  void publish_result_(const std::string &value) {
    if (this->probe_result_text_sensor_ != nullptr) {
      this->probe_result_text_sensor_->publish_state(value);
    }
  }

  std::string format_register_values_(uint16_t start_address, const std::vector<uint8_t> &data) const {
    if (data.empty()) {
      return "<empty response>";
    }

    std::string result;
    const size_t word_count = data.size() / 2;
    for (size_t index = 0; index < word_count; index++) {
      const size_t byte_index = index * 2;
      const uint16_t value = (static_cast<uint16_t>(data[byte_index]) << 8) |
                             static_cast<uint16_t>(data[byte_index + 1]);
      if (!result.empty()) {
        result += ", ";
      }
      const uint16_t address = start_address + static_cast<uint16_t>(index);
      char buffer[64];
      snprintf(buffer, sizeof(buffer), "%u=0x%04X (%u)", address, value, value);
      result += buffer;
    }

    if ((data.size() % 2U) != 0U) {
      result += " [odd byte count]";
    }

    return result;
  }

  modbus_controller::ModbusController *parent_{nullptr};
  number::Number *probe_address_number_{nullptr};
  number::Number *probe_count_number_{nullptr};
  select::Select *probe_register_type_select_{nullptr};
  button::Button *probe_read_button_{nullptr};
  text_sensor::TextSensor *probe_status_text_sensor_{nullptr};
  text_sensor::TextSensor *probe_result_text_sensor_{nullptr};
  uint16_t probe_address_{4400};
  uint16_t probe_count_{1};
  modbus_controller::ModbusRegisterType probe_register_type_{modbus_controller::ModbusRegisterType::HOLDING};
  bool probe_pending_{false};
};

inline void FsolarIvemProbeAddressNumber::control(float value) {
  if (this->parent_ == nullptr) {
    return;
  }
  const auto rounded = static_cast<uint16_t>(std::lroundf(value));
  this->parent_->set_probe_address(rounded);
  this->publish_state(this->parent_->get_probe_address());
}

inline void FsolarIvemProbeCountNumber::control(float value) {
  if (this->parent_ == nullptr) {
    return;
  }
  const auto rounded = static_cast<uint16_t>(std::lroundf(value));
  this->parent_->set_probe_count(rounded);
  this->publish_state(this->parent_->get_probe_count());
}

inline void FsolarIvemProbeRegisterTypeSelect::control(size_t index) {
  if (this->parent_ == nullptr) {
    return;
  }
  this->parent_->set_probe_register_type(index);
  this->publish_state(index == 1 ? "Input" : "Holding");
}

inline void FsolarIvemProbeReadButton::press_action() {
  if (this->parent_ == nullptr) {
    return;
  }
  this->parent_->execute_probe();
}

}  // namespace fsolar_ivem
}  // namespace esphome
