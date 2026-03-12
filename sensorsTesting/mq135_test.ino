// MQ135 gas sensor test on ESP32

const int MQ135_PIN = 34;  // analog-capable input pin

void setup() {
  Serial.begin(115200);
  analogReadResolution(12); // 0–4095
  Serial.println("MQ135 test started");
}

void loop() {
  int raw = analogRead(MQ135_PIN);
  float voltage = (raw / 4095.0f) * 3.3f;  // assuming 3.3V reference

  Serial.print("MQ135 raw: ");
  Serial.print(raw);
  Serial.print("  Voltage: ");
  Serial.print(voltage, 3);
  Serial.println(" V");

  delay(500);
}