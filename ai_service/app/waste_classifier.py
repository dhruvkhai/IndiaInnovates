"""
YOLOv8 Waste Classification Module

Provides:
  - load_model(model_path: str | None) -> YOLO
  - classify_image(image_path: str, model: YOLO | None = None) -> dict

Waste classes (target taxonomy):
  - plastic
  - metal
  - paper
  - organic
  - hazardous

Returned JSON example:
{
  "waste_type": "plastic",
  "confidence": 0.92
}
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np
from ultralytics import YOLO

# Target classes for this domain
TARGET_CLASSES = ["plastic", "metal", "paper", "organic", "hazardous"]


def load_model(model_path: str | None = None) -> YOLO:
    """
    Load a YOLOv8 model.

    If model_path is None, defaults to 'waste_yolov8n.pt' next to this file.
    """
    if model_path is None:
        here = Path(__file__).resolve().parent
        model_path = str(here.parent / "waste_yolov8n.pt")

    model = YOLO(model_path)
    return model


def _map_label_to_waste_type(label: str) -> str:
    """
    Map a model class label to one of the 5 target classes.

    If your model is trained directly with those class names, this will
    simply normalize to lowercase. Otherwise, some simple heuristics
    are applied (for COCO-style labels, etc.).
    """
    l = label.lower()

    if l in TARGET_CLASSES:
        return l

    if any(s in l for s in ["bottle", "cup", "bag", "plastic", "container", "wrapper", "can"]):
        return "plastic"

    if any(s in l for s in ["paper", "cardboard", "box", "newspaper", "tissue"]):
        return "paper"

    if any(s in l for s in ["metal", "tin", "steel", "aluminum"]):
        return "metal"

    if any(s in l for s in ["food", "banana", "apple", "fruit", "vegetable", "leaf", "organic"]):
        return "organic"

    if any(s in l for s in ["battery", "syringe", "chemical", "medicine", "mask", "hazard"]):
        return "hazardous"

    # Safety fallback
    return "hazardous"


def classify_image(image_path: str, model: YOLO | None = None) -> dict[str, Any]:
    """
    Run YOLOv8 on a single image and return JSON:

    {
      "waste_type": "<one of TARGET_CLASSES>",
      "confidence": 0.92
    }

    If model is None, a default one is loaded.
    """
    if model is None:
        model = load_model()

    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    # Ensure image is in correct format (BGR is fine for YOLOv8)
    results = model.predict(source=img, verbose=False)
    if not results:
        return {"waste_type": "hazardous", "confidence": 0.0}

    res = results[0]
    boxes = res.boxes
    if boxes is None or len(boxes) == 0:
        return {"waste_type": "hazardous", "confidence": 0.0}

    best_label = None
    best_conf = -1.0

    for box in boxes:
        conf = float(box.conf.item()) if hasattr(box, "conf") else 0.0
        cls_id = int(box.cls.item()) if hasattr(box, "cls") else -1
        label = str(res.names.get(cls_id, cls_id))
        if conf > best_conf:
            best_conf = conf
            best_label = label

    if best_label is None:
        return {"waste_type": "hazardous", "confidence": 0.0}

    waste_type = _map_label_to_waste_type(best_label)
    # Clamp confidence to [0,1]
    confidence = float(np.clip(best_conf, 0.0, 1.0))

    return {
        "waste_type": waste_type,
        "confidence": round(confidence, 4),
    }


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m app.waste_classifier <image_path>")
        raise SystemExit(1)

    img_path = sys.argv[1]
    clf_model = load_model()
    out = classify_image(img_path, clf_model)
    print(json.dumps(out, indent=2))

