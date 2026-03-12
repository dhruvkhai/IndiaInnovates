from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import Alert, AlertType, Bin, ClassificationResult, SensorReading, WasteClass
from app.db.session import get_db
from app.schemas import BinDataIn, BinStatusOut, WasteClassificationIn


router = APIRouter()


@router.post("/bin-data")
async def receive_bin_data(payload: BinDataIn, db: AsyncSession = Depends(get_db)):
    """
    HTTP endpoint for ESP32 devices to push sensor data directly.
    Mirrors the MQTT ingestion logic but over REST.
    """
    bin_row = await db.get(Bin, payload.bin_id)
    if bin_row is None:
        # No coordinates provided in this schema; default to (0,0).
        bin_row = Bin(id=payload.bin_id, name=None, lat=0.0, lng=0.0)
        db.add(bin_row)

    reading = SensorReading(
        bin_id=payload.bin_id,
        ts=payload.ts or datetime.utcnow(),
        ir_detected=1,  # treat HTTP push as an insertion event
        fill_level_pct=payload.fill_level,
        weight_kg=payload.weight_kg,
        gas_ppm=payload.gas_ppm,
        temperature_c=payload.temperature_c,
        humidity_pct=payload.humidity_pct,
    )
    db.add(reading)

    if payload.fill_level > 80.0:
        existing = await db.execute(
            select(Alert).where(
                Alert.bin_id == payload.bin_id,
                Alert.type == AlertType.bin_full,
                Alert.active == 1,
            )
        )
        if existing.scalar_one_or_none() is None:
            db.add(
                Alert(
                    bin_id=payload.bin_id,
                    type=AlertType.bin_full,
                    message=f"Bin {payload.bin_id} is {payload.fill_level:.1f}% full",
                    active=1,
                )
            )

    await db.commit()
    return {"status": "ok"}


@router.post("/waste-classification")
async def receive_waste_classification(payload: WasteClassificationIn, db: AsyncSession = Depends(get_db)):
    """
    HTTP endpoint for Raspberry Pi AI service to push classification results.
    """
    bin_row = await db.get(Bin, payload.bin_id)
    if bin_row is None:
        bin_row = Bin(id=payload.bin_id, name=None, lat=0.0, lng=0.0)
        db.add(bin_row)

    row = ClassificationResult(
        bin_id=payload.bin_id,
        ts=payload.ts or datetime.utcnow(),
        waste_class=WasteClass(payload.waste_type),
        confidence=payload.confidence,
        image_ref=payload.image_ref,
    )
    db.add(row)
    await db.commit()
    return {"status": "ok"}


@router.get("/bins", response_model=list[BinStatusOut])
async def list_bin_status(db: AsyncSession = Depends(get_db)):
    """
    Return high-level status per bin (latest sensor + latest classification).
    """
    res = await db.execute(select(Bin))
    bins = list(res.scalars().all())

    out: list[BinStatusOut] = []
    for b in bins:
        latest_reading = (
            await db.execute(
                select(SensorReading)
                .where(SensorReading.bin_id == b.id)
                .order_by(desc(SensorReading.ts))
                .limit(1)
            )
        ).scalar_one_or_none()

        latest_cls = (
            await db.execute(
                select(ClassificationResult)
                .where(ClassificationResult.bin_id == b.id)
                .order_by(desc(ClassificationResult.ts))
                .limit(1)
            )
        ).scalar_one_or_none()

        out.append(
            BinStatusOut(
                bin_id=b.id,
                name=b.name,
                lat=b.lat,
                lng=b.lng,
                last_update=latest_reading.ts if latest_reading else None,
                fill_level_pct=latest_reading.fill_level_pct if latest_reading else None,
                weight_kg=latest_reading.weight_kg if latest_reading else None,
                temperature_c=latest_reading.temperature_c if latest_reading else None,
                humidity_pct=latest_reading.humidity_pct if latest_reading else None,
                gas_ppm=latest_reading.gas_ppm if latest_reading else None,
                latest_waste_type=latest_cls.waste_class if latest_cls else None,
                latest_waste_confidence=latest_cls.confidence if latest_cls else None,
            )
        )

    return out

