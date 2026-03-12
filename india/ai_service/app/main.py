import io
import os
import random
from typing import Any

import httpx
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from PIL import Image

try:
    from ultralytics import YOLO
except Exception:  # pragma: no cover
    YOLO = None  # type: ignore


class Settings(BaseModel):
    ai_service_port: int = 9000
    yolo_model_path: str = "./models/yolov8n.pt"


settings = Settings(
    ai_service_port=int(os.getenv("AI_SERVICE_PORT", "9000")),
    yolo_model_path=os.getenv("YOLO_MODEL_PATH", "./models/yolov8n.pt"),
)


app = FastAPI(title="Smart Waste AI Service", version="0.1.0")


class ClassifyUrlRequest(BaseModel):
    bin_id: str
    image_url: str


def _lazy_model():
    if getattr(app.state, "model", None) is not None:
        return app.state.model

    if YOLO is None:
        app.state.model = None
        return None

    if not os.path.exists(settings.yolo_model_path):
        app.state.model = None
        return None

    app.state.model = YOLO(settings.yolo_model_path)
    return app.state.model


RECYCLE_HINTS = {"bottle", "can", "plastic", "cup", "paper", "cardboard", "glass", "tin"}
BIO_HINTS = {"banana", "apple", "food", "bread", "vegetable", "fruit", "leaf"}
HAZ_HINTS = {"battery", "syringe", "chemical", "medicine", "mask", "lighter"}


def _map_detections_to_waste_class(labels: list[str]) -> tuple[str, float]:
    lbls = {l.lower() for l in labels}
    if lbls & HAZ_HINTS:
        return "hazardous", 0.75
    if lbls & RECYCLE_HINTS:
        return "recyclable", 0.70
    if lbls & BIO_HINTS:
        return "biodegradable", 0.70
    # Fallback: random but deterministic-ish for demo
    choice = random.choice(["recyclable", "biodegradable", "hazardous"])
    return choice, 0.55


def _run_yolo_on_image(img: Image.Image) -> dict[str, Any]:
    model = _lazy_model()
    if model is None:
        waste_class, conf = _map_detections_to_waste_class([])
        return {"waste_class": waste_class, "confidence": conf, "detections": []}

    results = model.predict(img, verbose=False)
    r0 = results[0]

    names = getattr(r0, "names", {}) or {}
    boxes = getattr(r0, "boxes", None)

    detections: list[dict[str, Any]] = []
    labels: list[str] = []

    if boxes is not None:
        for b in boxes:
            cls_idx = int(b.cls.item()) if hasattr(b, "cls") else None
            label = names.get(cls_idx, str(cls_idx))
            labels.append(str(label))
            detections.append(
                {
                    "label": str(label),
                    "confidence": float(b.conf.item()) if hasattr(b, "conf") else None,
                }
            )

    waste_class, conf = _map_detections_to_waste_class(labels)
    conf = max(conf, max([d.get("confidence") or 0 for d in detections], default=0.0))
    return {"waste_class": waste_class, "confidence": float(conf), "detections": detections}


@app.get("/health")
async def health():
    model_loaded = _lazy_model() is not None
    return {"ok": True, "model_loaded": model_loaded, "model_path": settings.yolo_model_path}


@app.post("/classify/upload")
async def classify_upload(bin_id: str, file: UploadFile = File(...)):
    data = await file.read()
    try:
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {e}") from e

    out = _run_yolo_on_image(img)
    return {"bin_id": bin_id, **out}


@app.post("/classify/url")
async def classify_url(payload: ClassifyUrlRequest):
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(payload.image_url)
        r.raise_for_status()
        data = r.content

    try:
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {e}") from e

    out = _run_yolo_on_image(img)
    return {"bin_id": payload.bin_id, "image_url": payload.image_url, **out}

