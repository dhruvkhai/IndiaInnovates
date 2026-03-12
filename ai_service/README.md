# AI Service (YOLOv8)

Minimal microservice that accepts an image (upload or URL) and returns:

- `waste_class`: `recyclable | biodegradable | hazardous`
- `confidence`: float
- `detections`: raw model detections (starter shape)

## Run (Docker)

From repo root:

```bash
docker compose up --build ai-service
```

## Run (local)

```bash
cd ai_service
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 9000
```

