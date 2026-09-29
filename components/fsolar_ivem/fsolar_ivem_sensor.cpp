
#include "fsolar_ivem_sensor.h"
#include "esphome/core/log.h"

namespace esphome::fsolar_ivem {

using modbus_controller::RangeReuse;
using modbus_controller::SensorItem;
using modbus_controller::payload_to_float;
using modbus::helpers::SensorValueType;

static const char *const TAG = "modbus_controller.sensor";

void FsolarIvemSensor::dump_config() { LOG_SENSOR(TAG, "Modbus Controller Sensor", this); }

void FsolarIvemSensor::parse_and_publish(std::span<const uint8_t> data) {
  float result = payload_to_float(data, *this, this->offset);

  // Is there a lambda registered
  // call it with the pre converted value and the raw data array
  if (this->transform_func_.has_value()) {
    // the lambda can parse the response itself
    auto val = (*this->transform_func_)(this, result, data);
    if (val.has_value()) {
      ESP_LOGV(TAG, "Value overwritten by lambda");
      result = val.value();
    }
  }
  ESP_LOGD(TAG, "Sensor new state: %.02f", result);
  // this->sensor_->raw_state = result;
  this->publish_state(result);
}

}  // namespace esphome::fsolar_ivem
