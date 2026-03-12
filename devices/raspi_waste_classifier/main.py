"""
Raspberry Pi Waste Classification Service
- Hardware: Raspberry Pi 4 + Camera Module
- Software: Python, OpenCV, FastAPI, Ultralytics YOLOv8

Install deps (on Pi):
  pip install fastapi uvicorn[standard] opencv-python ultralytics pydantic httpx

Run:
  uvicorn main:app --host 0.0.0.0 --port 9001

ESP32 (or backend) can trigger:
  POST http://<pi-ip>:9001/classify
"""

import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

import httpx
import cv2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ultralytics import YOLO

# ========================
# CONFIG
# ========================

# Camera index: 0 is typical for Pi cam via /dev/video0 or USB cam
CAMERA_INDEX = 0

# Path to your trained YOLOv8 model on the Pi (custom model with your 5 classes)
YOLO_MODEL_PATH = "waste_yolov8n.pt"

# Expected waste classes in your model
WASTE_CLASSES = ["plastic", "paper", "metal", "organic", "hazardous"]

# Directory on the Pi where captured images are stored
IMAGE_ROOT_DIR = Path("/home/pi/smart_waste_images")

# Backend endpoint to receive classification events.
# This service will POST JSON:
# {
#   "bin_id": "BIN_001",
#   "waste_type": "plastic",
#   "confidence": 0.92,
#   "image_ref": "/home/pi/smart_waste_images/BIN_001/2026-03-12T12-00-01Z.jpg"
# }
BACKEND_CLASSIFICATION_URL = os.getenv(
    "BACKEND_CLASSIFICATION_URL",
    "http://localhost:8000/raspi/classifications",
)

# ========================
# FASTAPI APP
# ========================

app = FastAPI(
    title="Raspberry Pi Waste Classification",
    version="0.1.0",
)

# ========================
# CAMERA HANDLING
# ========================

_cam_lock = threading.Lock()
_camera: cv2.VideoCapture | None = None


def init_camera() -> None:
    """Initialize global camera object."""
    global _camera
    with _cam_lock:
        if _camera is not None and _camera.isOpened():
            return

        cap = cv2.VideoCapture(CAMERA_INDEX)
        if not cap.isOpened():
            raise RuntimeError(f"Could not open camera index {CAMERA_INDEX}")

        # Optional: set resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        _camera = cap


def capture_frame() -> "cv2.Mat":
    """Capture a single frame from the camera."""
    if _camera is None or not _camera.isOpened():
        init_camera()

    with _cam_lock:
        ok, frame = _camera.read()
        if not ok or frame is None:
            raise RuntimeError("Failed to capture frame from camera")
        return frame  # BGR image


# ========================
# YOLO MODEL HANDLING
# ========================

_model_lock = threading.Lock()
_model: YOLO | None = None


def load_model() -> YOLO:
    """Lazy-load YOLOv8 model (thread-safe)."""
    global _model
    with _model_lock:
        if _model is None:
            try:
                _model = YOLO(YOLO_MODEL_PATH)
            except Exception as e:  # pragma: no cover - runtime only
                raise RuntimeError(f"Failed to load YOLO model: {e}") from e
        return _model


# ========================
# WASTE CLASS MAPPING
# ========================

def map_label_to_waste_class(label: str) -> str:
    """
    Map model label to one of:
    ['plastic', 'paper', 'metal', 'organic', 'hazardous']

    If you trained your model directly with those class names,
    this can just return label.lower(). Here we add a few synonyms
    in case you used COCO labels or similar.
    """
    l = label.lower()

    # Direct if already in WASTE_CLASSES
    if l in WASTE_CLASSES:
        return l

    # Simple heuristic mappings
    if any(s in l for s in ["bottle", "cup", "bag", "plastic", "container", "wrapper"]):
        return "plastic"

    if any(s in l for s in ["paper", "cardboard", "newspaper", "tissue"]):
        return "paper"

    if any(s in l for s in ["can", "tin", "aluminum", "metal", "steel"]):
        return "metal"

    if any(s in l for s in ["food", "banana", "apple", "fruit", "vegetable", "leaf", "organic"]):
        return "organic"

    if any(s in l for s in ["battery", "syringe", "chemical", "medicine", "mask", "hazard"]):
        return "hazardous"

    # Fallback: if we don't recognize it, classify as 'hazardous' for safety
    return "hazardous"


def classify_frame(frame: "cv2.Mat") -> Tuple[str, float]:
    """
    Run YOLO on the frame and return (waste_type, confidence).

    Assumes:
    - A single dominant waste object in the frame.
    - We'll take the highest-confidence detection.
    """
    model = load_model()

    # YOLO expects BGR or RGB; cv2 is BGR so we pass frame directly.
    results = model.predict(source=frame, verbose=False)
    if not results:
        raise RuntimeError("No YOLO results returned")

    res = results[0]
    boxes = res.boxes
    if boxes is None or len(boxes) == 0:
        # No objects detected -> treat as unknown hazardous by default
        return "hazardous", 0.0

    best_label = None
    best_conf = -1.0

    for box in boxes:
        conf = float(box.conf.item()) if hasattr(box, "conf") else 0.0
        cls_id = int(box.cls.item()) if hasattr(box, "cls") else -1

        # Map class id to label via result's names dict
        label = str(res.names.get(cls_id, cls_id))
        if conf > best_conf:
            best_conf = conf
            best_label = label

    if best_label is None:
        return "hazardous", 0.0

    waste_type = map_label_to_waste_class(best_label)
    return waste_type, float(best_conf)


# ========================
# API MODELS
# ========================

class ClassificationResponse(BaseModel):
    waste_type: str
    confidence: float
    image_ref: str | None = None


# ========================
# API ENDPOINTS
# ========================

@app.on_event("startup")
def on_startup() -> None:
    # Initialize camera and model on startup for faster first request.
    # Comment these out if you prefer lazy initialization.
    init_camera()
    load_model()


@app.get("/health")
def health() -> dict:
    """Health check endpoint."""
    model_loaded = _model is not None
    cam_ok = _camera is not None and _camera.isOpened()
    return {
        "ok": True,
        "model_loaded": model_loaded,
        "camera_ok": cam_ok,
    }


@app.post("/classify", response_model=ClassificationResponse)
def classify(bin_id: str) -> ClassificationResponse:
    """
    Trigger from ESP32 / backend:
      POST http://<pi-ip>:9001/classify?bin_id=BIN_001

    Response:
    {
      "waste_type": "plastic",
      "confidence": 0.92,
      "image_ref": "/home/pi/smart_waste_images/BIN_001/..."
    }
    """
    try:
        frame = capture_frame()
    except Exception as e:  # pragma: no cover - runtime only
        raise HTTPException(status_code=500, detail=f"Camera error: {e}") from e

    # Save image to disk
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    bin_dir = IMAGE_ROOT_DIR / bin_id
    bin_dir.mkdir(parents=True, exist_ok=True)
    image_path = bin_dir / f"{ts}.jpg"

    ok = cv2.imwrite(str(image_path), frame)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to write image to disk")

    try:
        waste_type, confidence = classify_frame(frame)
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Model error: {e}") from e

    # Fire-and-forget POST to backend (errors logged but do not break response)
    payload = {
        "bin_id": bin_id,
        "waste_type": waste_type,
        "confidence": confidence,
        "image_ref": str(image_path),
    }
    try:
        with httpx.Client(timeout=5) as client:
            client.post(BACKEND_CLASSIFICATION_URL, json=payload)
    except Exception:
        # For simplicity, we don't raise HTTP error here; ESP32 still gets classification.
        pass

    return ClassificationResponse(waste_type=waste_type, confidence=confidence, image_ref=str(image_path))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=9001, reload=False)

