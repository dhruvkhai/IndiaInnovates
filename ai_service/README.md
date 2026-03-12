# AI Service (YOLOv8)

Minimal microservice that accepts an image (upload or URL) and returns:

- `waste_class`: `recyclable | biodegradable | hazardous`
- `confidence`: float
- `detections`: raw model detections (starter shape)

It also exposes endpoints that return the required output shape:

```json
{
  "waste_type": "plastic",
  "confidence": 0.93
}
```

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

## API

- `POST /classify/waste/upload` (multipart `file`)
  - Returns: `{ "waste_type": "plastic|organic|metal|paper|hazardous", "confidence": float }`

- `POST /classify/waste/url` (query param `image_url`)
  - Returns: `{ "waste_type": "...", "confidence": float }`

Notes:
- The service loads a model from `YOLO_MODEL_PATH` (defaults to `./models/yolov8n.pt` in the container).
- If your weights are trained with class names `plastic, organic, metal, paper, hazardous`, the service will use those directly.
- If you point it at a generic COCO model, it will fall back to a simple label-heuristic and may be inaccurate.

## Training (YOLOv8)

This repo includes training scripts for both cases:

### 1) Classification dataset (folders per class) — most common

Use this when your dataset looks like:

- `data/train/plastic/*.jpg`
- `data/train/organic/*.jpg`
- ...
- `data/val/plastic/*.jpg`

Train:

```bash
python train_waste_classifier_yolov8.py --data <PATH_TO_DATASET_ROOT> --model yolov8n-cls.pt --epochs 30
```

### 2) Detection dataset (images + bounding boxes)

Train:

```bash
python train_waste_yolov8.py --data datasets/trashnet.yaml --model yolov8n.pt --epochs 50
```

The detection dataset YAML template is at `datasets/trashnet.yaml`.

After training, set `YOLO_MODEL_PATH` to the produced weights (typically `runs-waste/yolov8-waste/weights/best.pt`)
and restart the service.

