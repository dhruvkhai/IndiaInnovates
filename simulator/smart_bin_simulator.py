import argparse
import json
import os
import random
import time
from dataclasses import dataclass

import paho.mqtt.client as mqtt


@dataclass
class BinState:
    bin_id: str
    lat: float
    lng: float
    fill_level_pct: float = 0.0
    weight_kg: float = 0.0
    gas_ppm: float = 30.0
    temperature_c: float = 28.0
    humidity_pct: float = 55.0


def rand_walk(value: float, step: float, lo: float, hi: float) -> float:
    value += random.uniform(-step, step)
    return max(lo, min(hi, value))


def make_bins(n: int) -> list[BinState]:
    # Roughly around Delhi for demo
    base_lat, base_lng = 28.6139, 77.2090
    out = []
    for i in range(n):
        out.append(
            BinState(
                bin_id=f"BIN_{i+1:03d}",
                lat=base_lat + random.uniform(-0.05, 0.05),
                lng=base_lng + random.uniform(-0.05, 0.05),
            )
        )
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mqtt-host", default=os.getenv("MQTT_HOST", "localhost"))
    parser.add_argument("--mqtt-port", type=int, default=int(os.getenv("MQTT_PORT", "1883")))
    parser.add_argument("--topic-prefix", default=os.getenv("MQTT_TELEMETRY_TOPIC_PREFIX", "bins"))
    parser.add_argument("--bins", type=int, default=8)
    parser.add_argument("--interval", type=float, default=3.0)
    args = parser.parse_args()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(args.mqtt_host, args.mqtt_port, keepalive=60)
    client.loop_start()

    bins = make_bins(args.bins)

    try:
        while True:
            for b in bins:
                # Simulate someone adding waste sometimes
                added = random.random() < 0.30
                ir_detected = 1 if added else 0

                if added:
                    b.fill_level_pct = min(100.0, b.fill_level_pct + random.uniform(0.5, 4.0))
                    b.weight_kg = min(80.0, b.weight_kg + random.uniform(0.05, 0.6))

                # Slow decay/settling
                b.gas_ppm = rand_walk(b.gas_ppm + (0.8 if b.fill_level_pct > 70 else 0.0), 3.0, 10.0, 900.0)
                b.temperature_c = rand_walk(b.temperature_c + (0.1 if b.fill_level_pct > 80 else 0.0), 0.6, 10.0, 60.0)
                b.humidity_pct = rand_walk(b.humidity_pct + (0.2 if b.fill_level_pct > 60 else 0.0), 2.0, 10.0, 100.0)

                payload = {
                    "bin_id": b.bin_id,
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "ir_detected": ir_detected,
                    "fill_level_pct": round(b.fill_level_pct, 2),
                    "weight_kg": round(b.weight_kg, 3),
                    "gas_ppm": round(b.gas_ppm, 2),
                    "temperature_c": round(b.temperature_c, 2),
                    "humidity_pct": round(b.humidity_pct, 2),
                    "lat": b.lat,
                    "lng": b.lng,
                }

                topic = f"{args.topic_prefix}/{b.bin_id}/telemetry"
                client.publish(topic, json.dumps(payload), qos=0)

            time.sleep(args.interval)
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()

