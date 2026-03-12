

#include <WiFi.h>
#include <HTTPClient.h>
#include <time.h>
#include <DHT.h>
#include "HX711.h"

// ===================
// USER CONFIG
// ===================
static const char* WIFI_SSID     = "OnePlus 11R 5G";
static const char* WIFI_PASSWORD = "mahakaleshwar";

// Your backend endpoint (change this)
static const char* BACKEND_URL = "http://192.168.1.50:8000/telemetry";

static const char* BIN_ID = "BIN_001";

// NTP (for ISO timestamp)
static const char* NTP_SERVER = "pool.ntp.org";
static const long  GMT_OFFSET_SEC = 0;
static const int   DAYLIGHT_OFFSET_SEC = 0;

// ===================
// PIN CONFIG
// ===================
constexpr int IR_PIN      = 27;

constexpr int TRIG_PIN    = 5;
constexpr int ECHO_PIN    = 18;

constexpr int HX711_DT    = 19;
constexpr int HX711_SCK   = 23;

constexpr int MQ135_PIN   = 34;

constexpr int DHT_PIN     = 4;
constexpr int DHT_TYPE    = DHT11;

// ===================
// BIN GEOMETRY CONFIG
// ===================
constexpr float BIN_HEIGHT_CM = 60.0;
constexpr float EMPTY_DIST_CM  = 55.0;  // calibrate
constexpr float FULL_DIST_CM   = 10.0;  // calibrate

// ===================
// HX711 CALIBRATION
// ===================
float HX711_CALIBRATION_FACTOR = -7050.0; // example; you must calibrate

// ===================
// GLOBALS
// ===================
DHT dht(DHT_PIN, DHT_TYPE);
HX711 scale;

unsigned long lastLoopMs = 0;
const unsigned long LOOP_INTERVAL_MS = 5000;

bool timeReady = false;

// ===================
// HELPERS
// ===================
void logLine(const String& msg) {
  Serial.println(msg);
}

bool ensureWiFiConnected() {
  if (WiFi.status() == WL_CONNECTED) return true;

  logLine("[WiFi] Connecting...");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long start = millis();
  const unsigned long timeoutMs = 15000;

  while (WiFi.status() != WL_CONNECTED && (millis() - start) < timeoutMs) {
    delay(300);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    logLine("[WiFi] Connected. IP: " + WiFi.localIP().toString());
    return true;
  }

  logLine("[WiFi] Failed to connect (timeout).");
  return false;
}

void initTime() {
  configTime(GMT_OFFSET_SEC, DAYLIGHT_OFFSET_SEC, NTP_SERVER);

  logLine("[Time] Syncing NTP...");
  unsigned long start = millis();
  const unsigned long timeoutMs = 10000;

  time_t now = 0;
  while ((millis() - start) < timeoutMs) {
    time(&now);
    if (now > 1700000000) { // after ~2023
      timeReady = true;
      logLine("[Time] NTP sync OK.");
      return;
    }
    delay(300);
  }
  logLine("[Time] NTP sync failed (will use millis-based timestamp).");
}

String isoTimestamp() {
  if (!timeReady) return String("millis_") + String(millis());

  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) return String("millis_") + String(millis());

  char buf[32];
  strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
  return String(buf);
}

float randWalk(float value, float step, float lo, float hi) {
  value += random(-1000, 1000) / 1000.0f * step;
  if (value < lo) value = lo;
  if (value > hi) value = hi;
  return value;
}

// ===================
// SENSOR FUNCTIONS
// ===================

bool readIRTriggered() {
  // Many IR modules are active-low; if yours is active-low, change to (val == LOW)
  int val = digitalRead(IR_PIN);
  bool triggered = (val == HIGH);
  logLine("[IR] Raw=" + String(val) + " Triggered=" + String(triggered ? "YES" : "NO"));
  return triggered;
}

float readUltrasonicDistanceCm() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  unsigned long duration = pulseIn(ECHO_PIN, HIGH, 30000UL);
  if (duration == 0) {
    logLine("[HC-SR04] Timeout / no echo");
    return -1.0;
  }

  float distance = (duration * 0.0343f) / 2.0f;
  logLine("[HC-SR04] Distance(cm)=" + String(distance, 2));
  return distance;
}

int computeFillLevelPercent(float distanceCm) {
  if (distanceCm < 0) return -1;

  float d = distanceCm;
  if (d > EMPTY_DIST_CM) d = EMPTY_DIST_CM;
  if (d < FULL_DIST_CM)  d = FULL_DIST_CM;

  float fill = (EMPTY_DIST_CM - d) / (EMPTY_DIST_CM - FULL_DIST_CM) * 100.0f;
  int fillPct = (int)roundf(fill);
  fillPct = max(0, min(100, fillPct));

  logLine("[Fill] Fill%=" + String(fillPct));
  return fillPct;
}

float readWeightKg() {
  if (!scale.is_ready()) {
    logLine("[HX711] Not ready");
    return -1.0;
  }
  float weightUnits = scale.get_units(10);
  float weightKg = weightUnits;
  if (weightKg < 0) weightKg = 0;
  logLine("[Weight] kg=" + String(weightKg, 3));
  return weightKg;
}

int readGasLevelRaw() {
  int raw = analogRead(MQ135_PIN);
  logLine("[MQ135] Raw ADC=" + String(raw));
  return raw;
}

bool readDHT(float &tempC, float &humPct) {
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  if (isnan(h) || isnan(t)) {
    logLine("[DHT11] Read failed");
    return false;
  }
  tempC = t;
  humPct = h;
  logLine("[DHT11] TempC=" + String(tempC, 1) + " Hum%=" + String(humPct, 0));
  return true;
}

// ===================
// HTTP POST
// ===================
bool postTelemetryJSON(
  int fillLevel,
  float weightKg,
  float tempC,
  float humPct,
  int gasLevel,
  const String& timestamp
) {
  if (WiFi.status() != WL_CONNECTED) {
    logLine("[HTTP] WiFi not connected; skip POST");
    return false;
  }

  HTTPClient http;
  http.begin(BACKEND_URL);
  http.addHeader("Content-Type", "application/json");

  String json = "{";
  json += "\"bin_id\":\"" + String(BIN_ID) + "\",";
  json += "\"fill_level\":" + String(fillLevel) + ",";
  json += "\"weight\":" + String(weightKg, 3) + ",";
  json += "\"temperature\":" + String(tempC, 1) + ",";
  json += "\"humidity\":" + String(humPct, 0) + ",";
  json += "\"gas_level\":" + String(gasLevel) + ",";
  json += "\"timestamp\":\"" + timestamp + "\"";
  json += "}";

  logLine("[HTTP] POST " + String(BACKEND_URL));
  logLine("[HTTP] Payload: " + json);

  int code = http.POST(json);
  String resp = http.getString();

  logLine("[HTTP] Status=" + String(code));
  if (resp.length() > 0) logLine("[HTTP] Response=" + resp);

  http.end();
  return (code >= 200 && code < 300);
}

void setup() {
  Serial.begin(115200);
  delay(300);

  logLine("=== Smart Waste Bin ESP32 Boot ===");

  pinMode(IR_PIN, INPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  analogReadResolution(12);

  dht.begin();
  logLine("[Init] DHT11 OK");

  scale.begin(HX711_DT, HX711_SCK);
  scale.set_scale(HX711_CALIBRATION_FACTOR);
  scale.tare();
  logLine("[Init] HX711 OK (tare done)");

  if (ensureWiFiConnected()) {
    initTime();
  }
}

void loop() {
  unsigned long now = millis();
  if (now - lastLoopMs < LOOP_INTERVAL_MS) return;
  lastLoopMs = now;

  logLine("\n--- Loop tick (5s) ---");

  if (WiFi.status() != WL_CONNECTED) {
    ensureWiFiConnected();
  }

  bool triggered = readIRTriggered();
  if (!triggered) {
    logLine("[Main] No insertion detected; skipping sensor + POST this cycle.");
    return;
  }

  float distanceCm = readUltrasonicDistanceCm();
  int fillPct = computeFillLevelPercent(distanceCm);
  float weightKg = readWeightKg();
  int gasRaw = readGasLevelRaw();

  float tempC = 0, hum = 0;
  if (!readDHT(tempC, hum)) {
    tempC = -1;
    hum = -1;
  }

  String ts = isoTimestamp();
  postTelemetryJSON(fillPct, weightKg, tempC, hum, gasRaw, ts);
}

