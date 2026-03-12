from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException

from app.db.models import Citizen, RewardTransaction, WasteClass
from app.db.session import get_db
from app.schemas import AwardPointsRequest, CitizenCreate, CitizenOut


router = APIRouter()


@router.post("/citizens", response_model=CitizenOut)
async def create_citizen(payload: CitizenCreate, db: AsyncSession = Depends(get_db)):
    row = await db.get(Citizen, payload.id)
    if row is not None:
        raise HTTPException(status_code=409, detail="Citizen already exists")
    row = Citizen(id=payload.id, name=payload.name)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


@router.get("/citizens", response_model=list[CitizenOut])
async def list_citizens(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Citizen).order_by(Citizen.id.asc()))
    return list(res.scalars().all())


@router.post("/award", response_model=CitizenOut)
async def award_points(payload: AwardPointsRequest, db: AsyncSession = Depends(get_db)):
    citizen = await db.get(Citizen, payload.citizen_id)
    if citizen is None:
        raise HTTPException(status_code=404, detail="Citizen not found")

    await db.execute(
        update(Citizen)
        .where(Citizen.id == payload.citizen_id)
        .values(points=Citizen.points + int(payload.delta_points))
    )
    db.add(
        RewardTransaction(
            citizen_id=payload.citizen_id,
            bin_id=payload.bin_id,
            waste_class=WasteClass(payload.waste_class) if payload.waste_class else None,
            delta_points=int(payload.delta_points),
            reason=payload.reason or "",
        )
    )
    await db.commit()
    updated = await db.get(Citizen, payload.citizen_id)
    return updated

