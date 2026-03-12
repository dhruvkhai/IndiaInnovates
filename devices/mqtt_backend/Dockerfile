# Dockerfile for MQTT backend subscriber
#
# Build (on machine with Docker):
#   cd devices/mqtt_backend
#   docker build -t mqtt-backend .
#
# Run (with Mosquitto reachable on host):
#   docker run --rm -it \
#     --network host \ 
#     -e MQTT_HOST=localhost \
#     mqtt-backend
#
# Or, if broker is another container in a user-defined network,
# join that network and set MQTT_HOST to the broker service name.

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mqtt_backend.py ./mqtt_backend.py

CMD ["python", "mqtt_backend.py"]

