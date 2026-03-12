# AI-Driven Circular Waste Intelligence System

## Smart Waste Management Using AI, IoT, and Intelligent Route Optimization

A full-stack **AI + IoT based Smart Waste Management Platform** that monitors waste bins, classifies waste using computer vision, and optimizes garbage truck routes using real-time data.

The system integrates **smart bins, edge AI, cloud backend, route optimization algorithms, and a municipal monitoring dashboard**.

---

# Overview

Urban cities generate massive amounts of municipal waste every day. However, traditional waste management systems rely heavily on **manual monitoring and fixed garbage collection routes**, which often results in overflowing bins, inefficient waste collection, and increased environmental pollution.

The **AI-Driven Circular Waste Intelligence System** introduces a **data-driven smart waste ecosystem** that automatically monitors bins, classifies waste, and optimizes garbage collection operations.

This platform integrates:

• IoT smart bins with multiple sensors
• AI-based waste classification using computer vision
• Real-time telemetry using MQTT and REST APIs
• Cloud backend for data processing and storage
• Route optimization algorithms for garbage trucks
• Municipal monitoring dashboard

---

# Problem Statement

Urban waste management systems face several critical challenges:

* Lack of waste segregation at the source
* Overflowing garbage bins in public areas
* Fixed garbage collection routes regardless of bin status
* High operational and fuel costs
* Increased landfill waste and environmental pollution

Without intelligent monitoring systems, municipal authorities cannot make **real-time, data-driven decisions**, leading to inefficient waste management operations.

---

# Proposed Solution

The proposed system introduces a **smart circular waste intelligence platform** powered by **Artificial Intelligence and Internet of Things (IoT)** technologies.

The platform transforms traditional waste management into an **automated, intelligent, and data-driven process**.

## Key Features

* Smart waste bins with multiple environmental sensors
* AI-based waste classification using camera and YOLO model
* Real-time telemetry using MQTT protocol
* Cloud backend for data ingestion and processing
* Intelligent garbage truck route optimization
* Municipal monitoring dashboard for city operators
* Simulation tools for testing the system without physical hardware

---

# System Architecture

The system consists of **five major components**.

### 1. Smart Waste Bin (IoT Device)

Smart bins use sensors and microcontrollers to monitor bin status.

Sensors include:

* Ultrasonic Sensor → bin fill level
* Load Cell + HX711 → waste weight
* IR Sensor → waste insertion detection
* MQ135 → gas detection
* DHT11 → temperature & humidity

Firmware runs on **ESP32**, sending telemetry to the backend.

---

### 2. Edge AI Waste Classification

A **Raspberry Pi camera module** captures images of disposed waste.

The images are processed using **YOLOv8 computer vision model** to classify waste types such as:

* Plastic
* Paper
* Metal
* Organic
* Hazardous

Classification results are sent to the backend.

---

### 3. Cloud Backend

The backend is built using **FastAPI** and processes real-time telemetry.

Responsibilities include:

* Receiving sensor telemetry from bins
* Storing data in PostgreSQL database
* Triggering alerts when bins are full or gas levels are high
* Storing waste classification results
* Computing optimal garbage truck routes

---

### 4. Route Optimization System

Garbage trucks should only visit bins that require collection.

The backend uses **graph-based shortest path algorithms** to calculate optimized routes.

Endpoint example:

```
POST /routes/optimize
```

Returns:

* list of bins requiring pickup
* optimized route order
* estimated travel distance

---

### 5. Monitoring Dashboard

A municipal web dashboard visualizes system data including:

* smart bin locations
* waste levels
* waste classification statistics
* garbage truck positions
* alerts and notifications

The dashboard helps authorities monitor waste collection operations in real time.

---

# Technologies Used

## Programming

* Python

## Backend

* FastAPI
* SQLAlchemy
* PostgreSQL

## IoT Communication

* MQTT (Eclipse Mosquitto)

## Artificial Intelligence

* YOLOv8
* OpenCV
* TensorFlow / PyTorch

## IoT Hardware

* ESP32
* Raspberry Pi
* Ultrasonic Sensor (HC-SR04)
* Load Cell + HX711
* IR Sensor
* MQ135 Gas Sensor
* DHT11

## Visualization

* HTML / CSS / JavaScript
* Streamlit / Plotly

## Containerization

* Docker
* Docker Compose

---

# Hardware Components

| Component         | Purpose                         |
| ----------------- | ------------------------------- |
| ESP32             | Smart bin microcontroller       |
| Raspberry Pi      | Edge AI processing              |
| Camera Module     | Waste image capture             |
| Ultrasonic Sensor | Bin fill level                  |
| Load Cell + HX711 | Waste weight                    |
| IR Sensor         | Waste insertion detection       |
| MQ135 Sensor      | Gas detection                   |
| DHT11             | Temperature & humidity          |
| GPS Module        | Garbage truck location tracking |

---

# Hardware Wiring Diagram

The following diagram shows the wiring connections between the sensors and the microcontroller.

![Wiring Diagram](hardware/circuit_diagram.png)

---

# System Workflow

1. Citizen disposes waste into smart bin
2. IR sensor detects waste insertion
3. Camera captures waste image
4. AI model classifies waste type
5. Sensors measure bin fill level and weight
6. Telemetry is sent to backend via MQTT / REST API
7. Backend stores data in PostgreSQL
8. Route optimizer identifies bins requiring pickup
9. Garbage truck receives optimized route
10. Dashboard displays system data in real time

---

# Project Structure

```
AI-Circular-Waste-Intelligence-System

├── README.md
├── requirements.txt
│
├── docs
│   ├── system_architecture.png
│   ├── workflow_diagram.png
│   └── hardware_setup.png
│
├── hardware
│   ├── components_list.md
│   ├── sensor_connections.md
│   └── circuit_diagram.png
│
├── firmware
│   └── esp32/
│
├── backend
│   ├── api_server.py
│   ├── route_optimizer.py
│   └── database_schema.md
│
├── ai_service
│   ├── train_trashnet.py
│   └── yolo_classifier.py
│
├── simulator
│   ├── smart_bin_simulator.py
│   ├── image_event_simulator.py
│   └── truck_simulator.py
│
├── devices
│   ├── raspi_waste_classifier
│   └── truck_gps_tracker
│
├── frontend
│   └── index.html
│
└── dashboard
    ├── app.py
    ├── charts.py
    └── map_visualization.py
```

---

# Running the System with Docker

### Start the entire platform

```
docker compose up --build
```

Services started:

* PostgreSQL database
* MQTT broker
* FastAPI backend
* AI classification service
* Dashboard frontend

---

# Local Development

### Run backend

```
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

### Run simulators

```
python simulator/smart_bin_simulator.py
python simulator/truck_simulator.py
```

These simulators generate **virtual sensor data and truck locations** without real hardware.

---

# Dashboard Features

The monitoring dashboard provides:

* Real-time smart bin status
* Waste type distribution analytics
* Map visualization of bin locations
* Optimized garbage collection routes
* Garbage truck GPS tracking
* Alerts for full bins or gas leaks

---

# Expected Impact

The AI-Driven Circular Waste Intelligence System helps cities:

* Improve waste segregation efficiency
* Reduce landfill waste
* Optimize garbage collection routes
* Lower fuel consumption and operational costs
* Enable data-driven municipal decision making

---

# Future Improvements

* AI prediction of waste generation trends
* Automated robotic waste sorting
* Integration with smart city IoT infrastructure
* Citizen reward system for proper waste segregation

---

# License

MIT License
