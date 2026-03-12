<<<<<<< HEAD
AI-Driven Circular Waste Intelligence System
Smart Waste Management using AI, IoT and Intelligent Route Optimization

An AI + IoT based Smart Waste Management Platform that monitors waste bins, classifies waste using computer vision, and optimizes garbage truck routes using real-time data.

The system integrates:

Smart IoT waste bins

AI-based waste classification

Real-time cloud communication

Intelligent route optimization

Municipal monitoring dashboard

This creates a data-driven smart waste ecosystem for cities.

1. Overview

Urban cities generate a large amount of municipal waste daily. However, most waste management systems still rely on:

Manual monitoring of bins

Fixed garbage collection schedules

Lack of waste segregation

These issues often lead to:

Overflowing garbage bins

Inefficient waste collection

Increased fuel consumption

Environmental pollution

The AI-Driven Circular Waste Intelligence System introduces a smart and automated waste management platform that continuously monitors waste bins, classifies waste using AI, and optimizes garbage collection routes.

2. Problem Statement

Current urban waste management systems face several major challenges:

Lack of waste segregation at the source

Overflowing garbage bins in public areas

Fixed garbage collection routes regardless of bin status

High operational and fuel costs

Large amounts of waste going to landfills

Limited real-time monitoring for municipal authorities

Because of these limitations, city administrators cannot make data-driven decisions, leading to inefficient waste management.

3. Proposed Solution

The proposed system introduces a Smart Circular Waste Intelligence Platform powered by:

Artificial Intelligence (AI)

Internet of Things (IoT)

Cloud Computing

Route Optimization Algorithms

The system converts traditional waste management into an automated, intelligent, and real-time monitored ecosystem.

4. Key Features

The system provides the following major features:

Smart Waste Bins equipped with multiple sensors to monitor bin status

AI-Based Waste Classification using computer vision models

Real-Time Data Transmission using MQTT communication protocol

Cloud Backend Processing for storing and analyzing waste data

Intelligent Garbage Truck Route Optimization

Municipal Monitoring Dashboard for real-time visualization

Simulation Tools for testing the system without physical hardware

5. System Architecture

The complete system consists of five main components.

5.1 Smart Waste Bin (IoT Device)

Smart waste bins are equipped with sensors and a microcontroller that continuously monitor bin conditions.

Sensors Used

Ultrasonic Sensor – measures bin fill level

Load Cell + HX711 – measures waste weight

IR Sensor – detects waste insertion

MQ135 Gas Sensor – detects harmful gases

DHT11 Sensor – measures temperature and humidity

Controller

ESP32 microcontroller processes sensor data

Sends telemetry data to the backend server

5.2 Edge AI Waste Classification

A camera module connected to a Raspberry Pi captures images of waste placed in the bin.

The images are processed using a YOLOv8 computer vision model.

Waste Categories Detected

Plastic

Paper

Metal

Organic waste

Hazardous waste

The classification results are transmitted to the cloud backend.

5.3 Cloud Backend

The cloud backend is built using FastAPI.

Responsibilities of Backend

Receiving sensor data from smart bins

Processing waste classification results

Storing data in a PostgreSQL database

Triggering alerts when:

Bin is full

Gas level is high

Running route optimization algorithms for garbage trucks

5.4 Route Optimization System

Garbage trucks should only visit bins that require collection.

The system uses graph-based shortest path algorithms to generate optimal routes.

Example API Endpoint
POST /routes/optimize
Output

The API returns:

List of bins requiring pickup

Optimized collection route

Estimated travel distance

This significantly reduces fuel consumption and travel time.

5.5 Monitoring Dashboard

A web-based municipal dashboard provides real-time monitoring.

Dashboard Capabilities

Visualizing smart bin locations on a map

Monitoring waste fill levels

Viewing waste classification statistics

Tracking garbage truck positions via GPS

Receiving alerts and notifications

This enables real-time operational decision making.

6. Technologies Used
Programming Language

Python

Backend Technologies

FastAPI

SQLAlchemy

PostgreSQL

IoT Communication

MQTT (Eclipse Mosquitto)

Artificial Intelligence

YOLOv8

OpenCV

TensorFlow / PyTorch

IoT Hardware

ESP32

Raspberry Pi

Sensors

Ultrasonic Sensor (HC-SR04)

Load Cell + HX711

IR Sensor

MQ135 Gas Sensor

DHT11

Visualization Tools

HTML

CSS

JavaScript

Streamlit / Plotly

Containerization

Docker

Docker Compose

7. Hardware Components
Component	Purpose
ESP32	Smart bin microcontroller
Raspberry Pi	Edge AI processing
Camera Module	Waste image capture
Ultrasonic Sensor	Bin fill level detection
Load Cell + HX711	Waste weight measurement
IR Sensor	Waste insertion detection
MQ135 Sensor	Gas detection
DHT11	Temperature & humidity monitoring
GPS Module	Garbage truck location tracking
8. Hardware Wiring Diagram

The following diagram represents the connection between sensors and the ESP32 microcontroller.

[Ultrasonic Sensor]  → ESP32
[Load Cell + HX711]  → ESP32
[IR Sensor]          → ESP32
[MQ135 Gas Sensor]   → ESP32
[DHT11 Sensor]       → ESP32

The Raspberry Pi camera module is used separately for AI waste classification.

9. System Workflow

The system operates through the following sequence:

Citizen disposes waste into the smart bin

IR sensor detects waste insertion

Camera captures image of the waste

AI model classifies the waste type

Sensors measure bin fill level and weight

Sensor data is sent to the cloud backend via MQTT

Backend stores data in PostgreSQL database

Route optimizer identifies bins that require collection

Garbage truck receives optimized route

Dashboard displays real-time system data

10. Project Structure
AI-Circular-Waste-Intelligence-System

├── README.md
├── requirements.txt

├── docs
│   ├── system_architecture.png
│   ├── workflow_diagram.png
│   └── hardware_setup.png

├── hardware
│   ├── components_list.md
│   ├── sensor_connections.md
│   └── circuit_diagram.png

├── firmware
│   └── esp32/

├── backend
│   ├── api_server.py
│   ├── route_optimizer.py
│   └── database_schema.md

├── ai_service
│   ├── train_trashnet.py
│   └── yolo_classifier.py

├── simulator
│   ├── smart_bin_simulator.py
│   ├── image_event_simulator.py
│   └── truck_simulator.py

├── devices
│   ├── raspi_waste_classifier
│   └── truck_gps_tracker

├── frontend
│   └── index.html

└── dashboard
    ├── app.py
    ├── charts.py
    └── map_visualization.py
11. Running the System with Docker

Start the complete platform using Docker:

docker compose up --build
Services Started

PostgreSQL Database

MQTT Broker

FastAPI Backend

AI Classification Service

Monitoring Dashboard

12. Local Development
Run Backend
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
Run Simulators
python simulator/smart_bin_simulator.py
python simulator/truck_simulator.py

The simulators generate virtual sensor data and truck GPS locations without requiring physical hardware.

13. Dashboard Features

The dashboard provides the following capabilities:

Real-time smart bin monitoring

Waste type distribution analytics

Interactive map visualization

Optimized garbage truck route display

GPS tracking of garbage trucks

Alerts for full bins or gas leaks

14. Expected Impact

The system provides several benefits for urban cities:

Improved waste segregation efficiency

Reduced landfill waste

Optimized garbage collection routes

Lower fuel consumption and operational costs

Data-driven decision making for municipalities

15. Future Improvements

Possible future extensions include:

AI-based prediction of waste generation trends

Robotic waste sorting systems

Integration with smart city infrastructure

Citizen reward systems for proper waste segregation

16. License

MIT License
=======
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
>>>>>>> dhruvBranch
