# Backend (FastAPI)

## What it does

- Subscribes to MQTT telemetry: `bins/<bin_id>/telemetry`
- Stores sensor readings in Postgres
- Creates alerts when bin fill level crosses threshold
- Exposes REST APIs for dashboard + rewards + route optimization

## Run (Docker)

From repo root:

```bash
docker compose up --build backend
```

## Run (local)

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

