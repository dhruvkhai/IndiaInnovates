from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import TruckLocation
from app.db.session import get_db
from app.schemas import TruckLocationIn, TruckLocationOut


router = APIRouter()


@router.post("/location", response_model=TruckLocationOut)
async def ingest_truck_location(payload: TruckLocationIn, db: AsyncSession = Depends(get_db)):
    row = TruckLocation(
        truck_id=payload.truck_id,
        ts=payload.ts or datetime.utcnow(),
        lat=payload.lat,
        lng=payload.lng,
        status=payload.status,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


@router.get("/locations", response_model=list[TruckLocationOut])
async def list_latest_truck_locations(limit: int = 200, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(TruckLocation).order_by(desc(TruckLocation.ts)).limit(limit))
    return list(res.scalars().all())

