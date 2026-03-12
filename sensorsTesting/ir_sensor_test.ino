// IR proximity sensor test on ESP32

const int IR_PIN = 27;  // digital output from IR module

void setup() {
  Serial.begin(115200);
  pinMode(IR_PIN, INPUT);
  Serial.println("IR sensor test started");
}

void loop() {
  int val = digitalRead(IR_PIN);

  // Many modules are active LOW; if yours is opposite, flip logic here.
  bool triggered = (val == LOW);

  Serial.print("IR raw: ");
  Serial.print(val);
  Serial.print("  Triggered: ");
  Serial.println(triggered ? "YES" : "NO");

  delay(200);
}