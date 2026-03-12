## Smart Waste Management System (IndiaInnovates)

Full‑stack, IoT‑driven **Smart Waste Management** platform built for the **IndiaInnovates hackathon**.  
It simulates and integrates:

- **Smart bins** with multiple sensors (ultrasonic, load cell, IR, MQ135 gas, DHT11)
- **ESP32 firmware** and **MQTT** telemetry
- **Raspberry Pi camera + YOLOv8** waste classification
- **FastAPI + PostgreSQL** backend (alerts, rewards, route optimization)
- **Raspberry Pi GPS tracker** for garbage trucks
- **Municipal web dashboard** (static HTML/CSS) served via Docker

---

## Tech stack

- **Backend API**: Python **FastAPI** (`backend/`)
- **Database**: **PostgreSQL** (via Docker)
- **Message broker**: **MQTT** (Eclipse Mosquitto)
- **AI models / services**:
  - **YOLOv8** microservice (`ai_service/`)
  - Raspberry Pi **camera classifier** (`devices/raspi_waste_classifier/`)
  - YOLOv8 **training script** for TrashNet (`ai_service/train_trashnet.py`)
- **IoT / devices**:
  - ESP32 firmware (`firmware/esp32/…`)
  - Sensor test sketches (`sensorsTesting/`)
  - Truck GPS tracker (`devices/truck_gps_tracker/`)
  - MQTT backend subscriber (`devices/mqtt_backend/`)
- **Simulation**: Python scripts for bin + truck + image events (`simulator/`)
- **Frontend dashboard**: Static HTML/CSS/JS dashboard (`frontend/index.html`) served by **nginx**

See `STRUCTURE.md` for a detailed folder map.

---

## Architecture overview

- **ESP32 Smart Bin**
  - Reads: ultrasonic (fill), HX711 (weight), IR (insertion), MQ135 (gas), DHT11 (temp/humidity)
  - Publishes MQTT telemetry to: `bins/<BIN_ID>/telemetry`
  - Or POSTs directly to backend: `POST /bin-data`

- **Backend (FastAPI, `backend/app`)**
  - Ingests MQTT telemetry and HTTP `/bin-data`
  - Stores data in Postgres tables: `bins`, `sensor_readings`, `classification_results`, `alerts`, `citizens`, `reward_transactions`, `truck_locations`
  - Triggers alerts when bin fill level or gas exceed thresholds
  - Exposes APIs:
    - `/bins`, `/telemetry`, `/alerts`, `/classifications`
    - `/bin-data`, `/waste-classification`, `/routes/optimize`, `/trucks/location`
    - `/rewards/*` for citizen reward system

- **AI Waste Classification**
  - `ai_service/` YOLOv8 microservice:
    - `POST /classify/upload` – image upload
    - `POST /classify/url` – classify by image URL
  - `devices/raspi_waste_classifier/`:
    - Captures image from Pi camera on `POST /classify?bin_id=…`
    - Saves JPEG to disk and POSTs result to backend `/waste-classification`

- **Route optimization**
  - `backend/app/services/route_optimization.py`: Dijkstra‑based route planning over full bins
  - `POST /routes/optimize` – returns ordered bin list + total distance
  - `simulate_truck_positions()` helps generate time‑stepped truck waypoints

- **Truck GPS tracking**
  - `devices/truck_gps_tracker/` on Raspberry Pi with NEO‑6M GPS
  - Reads NMEA from serial, parses lat/lon, every 10s POSTs to backend:
    - Repo mode: `POST /trucks/location`

- **Dashboard**
  - `frontend/index.html` – rich municipal dashboard using mock data (and can be wired to backend APIs)
  - Served by nginx container as `frontend` service

---

## Running the full system with Docker

### 1. Prerequisites

- Docker Desktop installed and running

### 2. Start all services

From the project root (`india/`):

```bash
cp .env.example .env      # Windows: Copy-Item .env.example .env
docker compose up --build
```

Services started:

- `postgres` – PostgreSQL database
- `mosquitto` – MQTT broker
- `backend` – FastAPI + SQLAlchemy + MQTT ingest
- `ai-service` – YOLOv8 microservice
- `frontend` – nginx serving the HTML dashboard
- `mqtt-backend` – paho‑mqtt subscriber (alerts) running in Docker

### 3. URLs

- **Backend API / docs**: `http://localhost:8000/docs`
- **Frontend dashboard**: `http://localhost:5173`
- **MQTT broker**: `mqtt://localhost:1883`

---

## Local modules (without Docker)

Each module can also be run locally for development:

- **Backend** (`backend/`)
  - `pip install -r requirements.txt`
  - `uvicorn app.main:app --reload --port 8000`

- **AI service** (`ai_service/`)
  - `pip install -r requirements.txt`
  - `uvicorn app.main:app --reload --port 9000`

- **Simulators** (`simulator/`)
  - `pip install -r requirements.txt`
  - Smart bins → `python smart_bin_simulator.py --bins 6 --interval 3`
  - Image AI events → `python image_event_simulator.py --bin-id BIN_001 --image-url https://…`
  - Truck locations → `python truck_simulator.py --interval 5`

- **MQTT backend only** (`devices/mqtt_backend/`)
  - `pip install -r requirements.txt`
  - `python mqtt_backend.py`

- **Raspberry Pi camera classifier** (`devices/raspi_waste_classifier/`)
  - `pip install -r requirements.txt`
  - `uvicorn main:app --host 0.0.0.0 --port 9001`

- **Truck GPS tracker** (`devices/truck_gps_tracker/`)
  - `pip install -r requirements.txt`
  - `python main.py --truck-id TRUCK_01 --serial /dev/serial0 --baud 9600 --backend-mode repo`

---

## ESP32 firmware & sensor testing

- **Main firmware**: `firmware/esp32/smart_waste_bin/smart_waste_bin.ino`
  - Connects to WiFi
  - Reads all sensors and POSTs JSON to backend or publishes to MQTT

- **Individual sensor test sketches** (`sensorsTesting/`):
  - `hc_sr04_test.ino` – HC‑SR04 ultrasonic
  - `hx711_test.ino` – load cell
  - `ir_sensor_test.ino` – IR proximity
  - `mq135_test.ino` – MQ135 gas
  - `dht11_test.ino` – DHT11 temperature/humidity

Upload these from Arduino IDE to validate hardware before running the full firmware.

---

## Typical data flow

1. ESP32 bin or `simulator/smart_bin_simulator.py` sends telemetry to MQTT or `POST /bin-data`.
2. `backend` ingests the data, stores it in Postgres, and raises alerts for high fill level / gas.
3. Raspberry Pi camera (`raspi_waste_classifier`) captures waste images and POSTs classifications to `/waste-classification`.
4. `devices/truck_gps_tracker` periodically POSTs truck GPS positions to `/trucks/location`.
5. `backend/app/services/route_optimization.py` computes an optimal route for trucks to collect from full bins.
6. `frontend/index.html` visualizes bins, trucks, alerts, and statistics for municipal operators.

---

## Hackathon notes

- This project is designed for **demonstrating an end‑to‑end, AI‑powered smart waste ecosystem**:
  - IoT devices (ESP32, sensors)
  - Edge AI (Raspberry Pi + camera)
  - Cloud backend (FastAPI + Postgres + MQTT)
  - Smart routing and monitoring dashboard
- Many pieces are modular and can be run **independently** for demos (only simulators + backend + dashboard are required to show the flow). 
