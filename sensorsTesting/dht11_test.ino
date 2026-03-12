// DHT11 test on ESP32

#include <DHT.h>

const int DHT_PIN  = 4;    // data pin
const int DHT_TYPE = DHT11;

DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();
  Serial.println("DHT11 test started");
}

void loop() {
  float h = dht.readHumidity();
  float t = dht.readTemperature(); // °C

  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT11");
  } else {
    Serial.print("Temperature: ");
    Serial.print(t, 1);
    Serial.print(" °C  Humidity: ");
    Serial.print(h, 0);
    Serial.println(" %");
  }

  delay(2000);
}