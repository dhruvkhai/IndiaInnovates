import argparse
import os
from pathlib import Path

from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train YOLOv8 on a waste dataset (YOLO format).")
    p.add_argument(
        "--data",
        default=str(Path(__file__).parent / "datasets" / "trashnet.yaml"),
        help="Path to YOLO dataset YAML (train/val paths + names).",
    )
    p.add_argument("--model", default="yolov8n.pt", help="Base model/weights to fine-tune.")
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--batch", type=int, default=16)
    p.add_argument("--device", default="auto", help="e.g. auto, cpu, 0")
    p.add_argument("--project", default="runs-waste")
    p.add_argument("--name", default="yolov8-waste")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    data_path = Path(args.data).resolve()
    if not data_path.exists():
        raise SystemExit(f"Dataset YAML not found: {data_path}")

    os.environ.setdefault("WANDB_DISABLED", "true")  # keep runs local by default

    model = YOLO(args.model)
    model.train(
        data=str(data_path),
        imgsz=args.imgsz,
        epochs=args.epochs,
        batch=args.batch,
        device=args.device,
        project=args.project,
        name=args.name,
        pretrained=True,
    )

    # After training, Ultralytics writes best weights to:
    # {project}/{name}/weights/best.pt
    print("Training complete.")


if __name__ == "__main__":
    main()

