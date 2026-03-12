"""
Test publisher to simulate ESP32 smart bin.

Run:
  python test_publisher.py BIN_001
"""

import json
import random
import sys
import time

import paho.mqtt.client as mqtt

MQTT_HOST = "localhost"
MQTT_PORT = 1883


def main(bin_id: str) -> None:
  client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
  client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
  client.loop_start()

  try:
    while True:
      payload = {
        "fill_level": random.uniform(0, 100),
        "weight": round(random.uniform(0, 20), 2),
        "temperature": random.uniform(20, 40),
        "humidity": random.uniform(30, 80),
        "gas_level": random.uniform(50, 200),
      }
      topic = f"smartbin/{bin_id}/sensors"
      client.publish(topic, json.dumps(payload), qos=0)
      print(f"Published to {topic}: {payload}")
      time.sleep(3)
  except KeyboardInterrupt:
    pass
  finally:
    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
  bin_id = sys.argv[1] if len(sys.argv) > 1 else "BIN_001"
  main(bin_id)

