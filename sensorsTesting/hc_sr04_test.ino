// HC-SR04 test on ESP32

const int TRIG_PIN = 5;   // change as wired
const int ECHO_PIN = 18;  // use level shifting if ECHO is 5V

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  Serial.println("HC-SR04 test started");
}

float readDistanceCm() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  unsigned long duration = pulseIn(ECHO_PIN, HIGH, 30000UL); // 30ms timeout
  if (duration == 0) return -1.0;

  float distance = (duration * 0.0343f) / 2.0f; // cm
  return distance;
}

void loop() {
  float d = readDistanceCm();
  if (d < 0) {
    Serial.println("No echo / timeout");
  } else {
    Serial.print("Distance: ");
    Serial.print(d, 2);
    Serial.println(" cm");
  }
  delay(500);
}