"""
Smart Waste Bin - MQTT Backend Subscriber

- Subscribes to: smartbin/<BIN_ID>/sensors
- Payload: JSON with fill_level, weight, temperature, humidity, gas_level
- Uses paho-mqtt + asyncio queue for async processing
- Stores data in-memory (can be replaced with DB)
- Prints alerts when fill_level > ALERT_THRESHOLD
"""

import asyncio
import json
import logging
from dataclasses import dataclass, asdict
from typing import Any, Dict, List

import paho.mqtt.client as mqtt

# ========================
# CONFIG
# ========================

MQTT_HOST = "localhost"  # change to your broker host/IP
MQTT_PORT = 1883
MQTT_TOPIC = "smartbin/+/sensors"  # + is wild-card for BIN_ID

ALERT_THRESHOLD = 80  # fill_level > 80 => alert

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


# ========================
# DATA MODELS / STORE
# ========================


@dataclass
class SensorPayload:
    bin_id: str
    fill_level: float
    weight: float
    temperature: float
    humidity: float
    gas_level: float

    @classmethod
    def from_dict(cls, bin_id: str, data: Dict[str, Any]) -> "SensorPayload":
        return cls(
            bin_id=bin_id,
            fill_level=float(data.get("fill_level", 0.0)),
            weight=float(data.get("weight", 0.0)),
            temperature=float(data.get("temperature", 0.0)),
            humidity=float(data.get("humidity", 0.0)),
            gas_level=float(data.get("gas_level", 0.0)),
        )


class InMemoryStore:
    """
    Simple in-memory store.
    Replace with DB calls if needed.
    """

    def __init__(self) -> None:
        # bin_id -> list of readings
        self._data: Dict[str, List[SensorPayload]] = {}

    def add(self, payload: SensorPayload) -> None:
        self._data.setdefault(payload.bin_id, []).append(payload)

    def latest_for_bin(self, bin_id: str) -> SensorPayload | None:
        arr = self._data.get(bin_id)
        return arr[-1] if arr else None


store = InMemoryStore()

# ========================
# ASYNC INGEST QUEUE
# ========================

queue: asyncio.Queue[SensorPayload] = asyncio.Queue(maxsize=1000)


async def process_payload(payload: SensorPayload) -> None:
    """
    Async handler: store the data and trigger alerts.
    """
    store.add(payload)
    logging.info("Stored reading: %s", asdict(payload))

    if payload.fill_level > ALERT_THRESHOLD:
        logging.warning(
            "ALERT: Bin %s is over threshold (%.1f%% > %d%%)",
            payload.bin_id,
            payload.fill_level,
            ALERT_THRESHOLD,
        )
        # Here you could:
        # - send HTTP request to backend API
        # - push notification
        # - write to another MQTT topic, etc.


async def consumer_loop() -> None:
    """
    Async consumer that pulls from queue and processes messages.
    """
    while True:
        payload = await queue.get()
        try:
            await process_payload(payload)
        except Exception:
            logging.exception("Error processing payload")
        finally:
            queue.task_done()


# ========================
# MQTT CALLBACKS (THREAD)
# ========================


def extract_bin_id(topic: str) -> str:
    # Expected topic: smartbin/<BIN_ID>/sensors
    parts = topic.split("/")
    if len(parts) >= 3:
        return parts[1]
    return "UNKNOWN"


def on_connect(client: mqtt.Client, userdata: Any, flags: Dict[str, Any], rc: int, properties=None):
    if rc == 0:
        logging.info("Connected to MQTT broker, subscribing to %s", MQTT_TOPIC)
        client.subscribe(MQTT_TOPIC)
    else:
        logging.error("MQTT connection failed, rc=%s", rc)


def on_message_factory(loop: asyncio.AbstractEventLoop):
    """
    Returns an on_message callback bound to the given asyncio loop.
    It enqueues parsed SensorPayload into the async queue.
    """

    def on_message(client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage):
        try:
            topic = msg.topic
            payload_str = msg.payload.decode("utf-8")
            logging.info("MQTT message on %s: %s", topic, payload_str)

            data = json.loads(payload_str)
            bin_id = extract_bin_id(topic)
            sp = SensorPayload.from_dict(bin_id, data)

            loop.call_soon_threadsafe(queue.put_nowait, sp)
        except Exception:
            logging.exception("Failed to handle MQTT message")

    return on_message


def create_mqtt_client(loop: asyncio.AbstractEventLoop) -> mqtt.Client:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message_factory(loop)
    return client


# ========================
# MAIN (ASYNC ENTRYPOINT)
# ========================


async def main() -> None:
    loop = asyncio.get_running_loop()
    client = create_mqtt_client(loop)
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)

    client.loop_start()

    consumer_task = asyncio.create_task(consumer_loop())

    logging.info("MQTT backend subscriber running. Press Ctrl+C to stop.")
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    finally:
        consumer_task.cancel()
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

