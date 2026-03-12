import json
import logging
from typing import Any

import paho.mqtt.client as mqtt

from app.core.config import settings
from app.services.ingest_queue import telemetry_queue


logger = logging.getLogger(__name__)


def _topic_filter() -> str:
    # bins/<bin_id>/telemetry
    return f"{settings.mqtt_telemetry_topic_prefix}/+/telemetry"


def create_mqtt_client(loop) -> mqtt.Client:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if settings.mqtt_username:
        client.username_pw_set(settings.mqtt_username, settings.mqtt_password or None)

    def on_connect(_client: mqtt.Client, _userdata: Any, _flags: Any, rc: int, _properties: Any = None):
        if rc != 0:
            logger.error("MQTT connect failed rc=%s", rc)
            return
        logger.info("MQTT connected; subscribing to %s", _topic_filter())
        _client.subscribe(_topic_filter(), qos=0)

    def on_message(_client: mqtt.Client, _userdata: Any, msg: mqtt.MQTTMessage):
        try:
            payload = msg.payload.decode("utf-8")
            data = json.loads(payload)
            if not isinstance(data, dict):
                return
            telemetry_queue.put_threadsafe(loop, data)
        except Exception:
            logger.exception("Failed processing MQTT message on %s", msg.topic)

    client.on_connect = on_connect
    client.on_message = on_message
    return client


def start_mqtt(loop) -> mqtt.Client:
    client = create_mqtt_client(loop)
    client.connect(settings.mqtt_host, int(settings.mqtt_port), keepalive=60)
    client.loop_start()
    return client


def stop_mqtt(client: mqtt.Client | None) -> None:
    if client is None:
        return
    try:
        client.loop_stop()
        client.disconnect()
    except Exception:
        logger.exception("Error stopping MQTT client")

