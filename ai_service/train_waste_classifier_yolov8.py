import argparse
import os
from pathlib import Path

from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train YOLOv8 classification on a folder-of-classes dataset.")
    p.add_argument(
        "--data",
        required=True,
        help=(
            "Dataset root folder. Expected structure:\n"
            "  <data>/train/<class_name>/*.jpg\n"
            "  <data>/val/<class_name>/*.jpg\n"
            "  (optional) <data>/test/<class_name>/*.jpg"
        ),
    )
    p.add_argument("--model", default="yolov8n-cls.pt", help="Base classification model/weights.")
    p.add_argument("--imgsz", type=int, default=224)
    p.add_argument("--epochs", type=int, default=30)
    p.add_argument("--batch", type=int, default=32)
    p.add_argument("--device", default="auto", help="e.g. auto, cpu, 0")
    p.add_argument("--project", default="runs-waste")
    p.add_argument("--name", default="yolov8-waste-cls")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    data_dir = Path(args.data).resolve()
    if not data_dir.exists():
        raise SystemExit(f"Dataset folder not found: {data_dir}")

    os.environ.setdefault("WANDB_DISABLED", "true")

    model = YOLO(args.model)
    model.train(
        data=str(data_dir),
        imgsz=args.imgsz,
        epochs=args.epochs,
        batch=args.batch,
        device=args.device,
        project=args.project,
        name=args.name,
        pretrained=True,
    )

    print("Training complete.")


if __name__ == "__main__":
    main()

