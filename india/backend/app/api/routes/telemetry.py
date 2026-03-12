from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import SensorReading
from app.db.session import get_db
from app.schemas import SensorReadingIn, SensorReadingOut


router = APIRouter()


@router.post("", response_model=SensorReadingOut)
async def ingest_telemetry(payload: SensorReadingIn, db: AsyncSession = Depends(get_db)):
    row = SensorReading(
        bin_id=payload.bin_id,
        ts=payload.ts or datetime.utcnow(),
        ir_detected=payload.ir_detected,
        fill_level_pct=payload.fill_level_pct,
        weight_kg=payload.weight_kg,
        gas_ppm=payload.gas_ppm,
        temperature_c=payload.temperature_c,
        humidity_pct=payload.humidity_pct,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


@router.get("/latest", response_model=list[SensorReadingOut])
async def latest_per_bin(limit: int = 200, db: AsyncSession = Depends(get_db)):
    # Simple starter query: return most recent readings globally
    res = await db.execute(select(SensorReading).order_by(desc(SensorReading.ts)).limit(limit))
    return list(res.scalars().all())


@router.get("/{bin_id}", response_model=list[SensorReadingOut])
async def readings_for_bin(bin_id: str, limit: int = 200, db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(SensorReading).where(SensorReading.bin_id == bin_id).order_by(desc(SensorReading.ts)).limit(limit)
    )
    return list(res.scalars().all())

