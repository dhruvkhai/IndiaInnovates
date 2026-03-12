# Full folder structure

```text
india/
  README.md
  STRUCTURE.md
  .env.example
  docker-compose.yml

  infra/
    mosquitto/
      mosquitto.conf

  backend/                           # FastAPI + Postgres + MQTT ingest + route + rewards
    README.md
    Dockerfile
    requirements.txt
    app/
      __init__.py
      main.py                         # app bootstrap, CORS, create tables, start MQTT + consumer
      schemas.py                      # pydantic request/response models
      core/
        config.py                     # env-based configuration
      db/
        __init__.py
        base.py                       # SQLAlchemy Declarative base
        session.py                    # async engine + session maker
        models.py                     # Bin, SensorReading, Alerts, Rewards, TruckLocation
      services/
        __init__.py
        ingest_queue.py               # asyncio queue fed by MQTT thread
        mqtt_ingest.py                # paho-mqtt subscriber
        telemetry_handler.py          # persists telemetry + bin-full alerts
      api/
        __init__.py
        router.py                     # mounts routers
        routes/
          __init__.py
          bins.py                     # CRUD/list bins
          telemetry.py                # ingest + query readings
          alerts.py                   # list + resolve alerts
          classifications.py          # store classifications + forward to AI service
          routes.py                   # route optimization endpoint
          rewards.py                  # citizen + points endpoints
          trucks.py                   # ingest + list truck locations

  ai_service/                         # YOLOv8 microservice
    README.md
    Dockerfile
    requirements.txt
    app/
      __init__.py
      main.py                         # /classify/upload and /classify/url

  simulator/                          # Python simulation scripts
    README.md
    requirements.txt
    smart_bin_simulator.py            # publishes MQTT sensor telemetry every few seconds
    image_event_simulator.py          # triggers AI classify via backend (image URL)
    truck_simulator.py                # posts truck locations to backend periodically

  frontend/                           # React (Vite) dashboard
    README.md
    Dockerfile
    package.json
    tsconfig.json
    vite.config.ts
    index.html
    src/
      main.tsx
      ui/
        App.tsx                       # bins + alerts + truck locations
        styles.css
```

# Module mapping to your requirements

## 1) Smart Bin Simulator

- `simulator/smart_bin_simulator.py`
  - **IR waste detection**: `ir_detected`
  - **Ultrasonic fill level**: `fill_level_pct`
  - **Load cell weight**: `weight_kg`
  - **Gas sensor**: `gas_ppm`
  - **Temperature/humidity**: `temperature_c`, `humidity_pct`
  - Publishes JSON to `bins/<bin_id>/telemetry` every `--interval` seconds

## 2) AI Waste Classification (YOLOv8)

- `ai_service/app/main.py`
  - POST `/classify/upload` (multipart upload)
  - POST `/classify/url` (fetch image by URL)
  - Returns `waste_class`: `recyclable | biodegradable | hazardous`

## 3) Backend API

- `backend/app/main.py`: boot + MQTT subscriber + DB
- `backend/app/api/routes/*`: REST endpoints
- Stores:
  - telemetry in `sensor_readings`
  - alerts in `alerts`
  - classifications in `classification_results`

## 4) Route Optimization Engine

- `backend/app/api/routes/routes.py`
  - POST `/routes/optimize`
  - Uses graph shortest paths (NetworkX) and a greedy “nearest-next” visit order as a baseline

## 5) Municipal Monitoring Dashboard

- `frontend/src/ui/App.tsx`
  - Displays bins + fill level bars (from `/telemetry/latest`)
  - Shows active alerts (from `/alerts`)
  - Shows latest truck locations (from `/trucks/locations`)

## 6) Citizen Reward System

- `backend/app/api/routes/rewards.py`
  - POST `/rewards/citizens`
  - GET `/rewards/citizens`
  - POST `/rewards/award` (adds points + logs a transaction)

