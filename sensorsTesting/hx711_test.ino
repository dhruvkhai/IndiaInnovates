// HX711 load cell test on ESP32

#include "HX711.h"

const int HX711_DT  = 19;  // DOUT
const int HX711_SCK = 23;  // SCK

HX711 scale;

// set this after calibration (start with -7050 or similar)
float CALIBRATION_FACTOR = -7050.0;

void setup() {
  Serial.begin(115200);
  scale.begin(HX711_DT, HX711_SCK);
  scale.set_scale(CALIBRATION_FACTOR);
  scale.tare();  // zero the scale
  Serial.println("HX711 test started");
}

void loop() {
  if (!scale.is_ready()) {
    Serial.println("HX711 not ready");
    delay(500);
    return;
  }

  // average of 10 readings
  float units = scale.get_units(10);

  Serial.print("Raw units: ");
  Serial.println(units, 3);  // interpret as grams/kg depending on calibration

  delay(500);
}