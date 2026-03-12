# Smart Waste Management System (AI + IoT Simulation)

Full-stack starter project simulating **smart bins**, **MQTT telemetry**, **AI waste classification (YOLOv8)**, **municipal monitoring dashboard**, **route optimization**, and a **citizen reward system**.

## Tech stack

- **Backend API**: Python **FastAPI**
- **Database**: **PostgreSQL**
- **AI model**: **YOLOv8** (Ultralytics)
- **Message broker**: **MQTT** (Eclipse Mosquitto)
- **Frontend dashboard**: **React** (Vite)
- **Simulation**: Python scripts (sensor + image events)

## Repo layout

See the full structure in `STRUCTURE.md`.

## Quick start (Docker)

1) Copy env template:

```bash
cp .env.example .env
```

2) Start everything:

```bash
docker compose up --build
```

3) URLs:

- **Backend API**: `http://localhost:8000` (OpenAPI docs at `/docs`)
- **Frontend**: `http://localhost:5173`
- **MQTT broker**: `mqtt://localhost:1883`

## Quick start (local dev without Docker)

You can run each module locally; see module READMEs:
- `backend/README.md`
- `ai_service/README.md`
- `simulator/README.md`
- `frontend/README.md`

## Typical flow

1. `simulator/` publishes sensor telemetry to MQTT topic `bins/<bin_id>/telemetry`.
2. `backend/` subscribes to those topics, stores readings in Postgres, and triggers alerts on full bins.
3. `simulator/` (or your UI) sends image classification requests to `ai_service/`.
4. `backend/` stores classification results and updates stats/rewards.
5. `frontend/` polls backend endpoints to visualize bin status, alerts, and stats.

