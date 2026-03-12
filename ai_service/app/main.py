import io
import os
<<<<<<< HEAD
=======
import random
>>>>>>> dhruvBranch
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


<<<<<<< HEAD
class WasteClassificationOut(BaseModel):
    waste_type: str
    confidence: float


=======
>>>>>>> dhruvBranch
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


<<<<<<< HEAD
WASTE_TYPES = ("plastic", "organic", "metal", "paper", "hazardous")

# COCO-ish heuristic hints (fallback only when using a generic pre-trained model).
PLASTIC_HINTS = {
    "bottle",
    "wine glass",
    "cup",
    "fork",
    "spoon",
    "toothbrush",
    "plastic",
    "bag",
}
ORGANIC_HINTS = {
    "banana",
    "apple",
    "sandwich",
    "orange",
    "broccoli",
    "carrot",
    "hot dog",
    "pizza",
    "donut",
    "cake",
    "food",
    "fruit",
    "vegetable",
    "leaf",
}
METAL_HINTS = {
    "can",
    "tin",
    "knife",
    "scissors",
    "metal",
}
PAPER_HINTS = {
    "book",
    "paper",
    "cardboard",
    "newspaper",
    "magazine",
}
HAZARDOUS_HINTS = {
    "battery",
    "syringe",
    "chemical",
    "medicine",
    "lighter",
    "aerosol",
    "paint",
    "pesticide",
}


def _heuristic_waste_type_from_labels(labels: list[str]) -> tuple[str, float]:
    lbls = {l.lower() for l in labels}

    if lbls & HAZARDOUS_HINTS:
        return "hazardous", 0.55
    if lbls & ORGANIC_HINTS:
        return "organic", 0.55
    if lbls & PAPER_HINTS:
        return "paper", 0.55
    if lbls & METAL_HINTS:
        return "metal", 0.55
    if lbls & PLASTIC_HINTS:
        return "plastic", 0.55

    # If we can't infer from a generic model's labels, choose a safe default with low confidence.
    return "organic", 0.10


def _waste_class_3way_from_type(waste_type: str) -> str:
    wt = waste_type.lower()
    if wt == "hazardous":
        return "hazardous"
    if wt == "organic":
        return "biodegradable"
    return "recyclable"


def _require_model():
    model = _lazy_model()
    if model is None:
        raise HTTPException(
            status_code=503,
            detail=f"YOLO model not available. Set YOLO_MODEL_PATH to an existing weights file (current: {settings.yolo_model_path}).",
        )
    return model


def _run_yolo_on_image(img: Image.Image) -> dict[str, Any]:
    model = _require_model()
    results = model.predict(img, verbose=False)
    r0 = results[0]

    probs = getattr(r0, "probs", None)
    if probs is not None:
        names = getattr(r0, "names", {}) or {}
        top1 = int(getattr(probs, "top1", -1))
        top1conf = float(getattr(probs, "top1conf", 0.0))
        pred_name = str(names.get(top1, "")).lower()
        if pred_name in WASTE_TYPES:
            return {
                "waste_type": pred_name,
                "confidence": float(top1conf),
                "detections": [],
                "waste_class": _waste_class_3way_from_type(pred_name),
            }

=======
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

>>>>>>> dhruvBranch
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

<<<<<<< HEAD
    # Prefer direct classification when the model is trained on our target waste classes.
    waste_names = {str(v).lower(): int(k) for k, v in dict(names).items()} if names else {}
    usable = [w for w in WASTE_TYPES if w in waste_names]

    best_waste_type: str | None = None
    best_conf = 0.0

    if usable and boxes is not None:
        usable_idx = {waste_names[w] for w in usable}
        for b in boxes:
            cls_idx = int(b.cls.item()) if hasattr(b, "cls") else None
            if cls_idx in usable_idx:
                c = float(b.conf.item()) if hasattr(b, "conf") else 0.0
                if c >= best_conf:
                    best_conf = c
                    best_waste_type = str(names.get(cls_idx, "")).lower()

    if best_waste_type is None:
        best_waste_type, best_conf = _heuristic_waste_type_from_labels(labels)
        best_conf = max(best_conf, max([d.get("confidence") or 0 for d in detections], default=0.0))

    return {
        "waste_type": str(best_waste_type),
        "confidence": float(best_conf),
        "detections": detections,
        "waste_class": _waste_class_3way_from_type(str(best_waste_type)),
    }
=======
    waste_class, conf = _map_detections_to_waste_class(labels)
    conf = max(conf, max([d.get("confidence") or 0 for d in detections], default=0.0))
    return {"waste_class": waste_class, "confidence": float(conf), "detections": detections}
>>>>>>> dhruvBranch


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

<<<<<<< HEAD

@app.post("/classify/waste/upload", response_model=WasteClassificationOut)
async def classify_waste_upload(file: UploadFile = File(...)):
    """
    Required output shape:
    {
      "waste_type": "plastic|organic|metal|paper|hazardous",
      "confidence": 0.93
    }
    """
    data = await file.read()
    try:
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {e}") from e

    out = _run_yolo_on_image(img)
    return {"waste_type": out["waste_type"], "confidence": out["confidence"]}


@app.post("/classify/waste/url", response_model=WasteClassificationOut)
async def classify_waste_url(image_url: str):
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(image_url)
        r.raise_for_status()
        data = r.content

    try:
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {e}") from e

    out = _run_yolo_on_image(img)
    return {"waste_type": out["waste_type"], "confidence": out["confidence"]}

=======
>>>>>>> dhruvBranch
