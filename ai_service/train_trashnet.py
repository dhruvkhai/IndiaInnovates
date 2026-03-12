"""
Training script for YOLOv8 waste classifier using a TrashNet-style dataset.

Assumptions:
- You have prepared a YOLOv8 dataset on disk with:
    datasets/trashnet_yolo/
      images/
        train/
        val/
      labels/
        train/
        val/
  and label files (.txt) using YOLO format.

- Your classes (in order) map to:
    0: plastic
    1: metal
    2: paper
    3: organic
    4: hazardous

Create a data.yaml file like:

  path: datasets/trashnet_yolo
  train: images/train
  val: images/val

  names:
    0: plastic
    1: metal
    2: paper
    3: organic
    4: hazardous

Usage:
  pip install ultralytics
  python train_trashnet.py --data ./datasets/trashnet_yolo/data.yaml --epochs 50 --img 640

The trained model will be saved under runs/detect/exp*/weights/best.pt
You can then copy/rename it as ai_service/waste_yolov8n.pt for inference.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train YOLOv8 waste classifier on TrashNet-style dataset")
    p.add_argument(
        "--data",
        type=str,
        required=True,
        help="Path to YOLO data.yaml (pointing to TrashNet-derived dataset).",
    )
    p.add_argument(
        "--model",
        type=str,
        default="yolov8n.pt",
        help="Base YOLOv8 model to fine-tune (e.g. yolov8n.pt, yolov8s.pt).",
    )
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--img", type=int, default=640, help="Training image size")
    p.add_argument("--batch", type=int, default=16)
    p.add_argument("--project", type=str, default="runs/trashnet")
    p.add_argument("--name", type=str, default="yolov8n-trashnet")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    data_yaml = Path(args.data)
    if not data_yaml.exists():
        raise FileNotFoundError(f"data.yaml not found at {data_yaml}")

    print(f"[train] Using data config: {data_yaml}")
    print(f"[train] Base model: {args.model}")

    # Load base model (pretrained on COCO)
    model = YOLO(args.model)

    # Fine-tune on TrashNet-style dataset
    model.train(
        data=str(data_yaml),
        epochs=args.epochs,
        imgsz=args.img,
        batch=args.batch,
        project=args.project,
        name=args.name,
    )

    print("[train] Training complete. Best weights are in runs/.../weights/best.pt")


if __name__ == "__main__":
    main()

