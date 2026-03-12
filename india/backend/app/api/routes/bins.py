from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException

from app.db.models import Bin
from app.db.session import get_db
from app.schemas import BinCreate, BinOut


router = APIRouter()


@router.post("", response_model=BinOut)
async def create_bin(payload: BinCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.get(Bin, payload.id)
    if existing is not None:
        raise HTTPException(status_code=409, detail="Bin already exists")
    row = Bin(id=payload.id, name=payload.name, lat=payload.lat, lng=payload.lng)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


@router.get("", response_model=list[BinOut])
async def list_bins(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Bin).order_by(Bin.id.asc()))
    return list(res.scalars().all())


@router.get("/{bin_id}", response_model=BinOut)
async def get_bin(bin_id: str, db: AsyncSession = Depends(get_db)):
    row = await db.get(Bin, bin_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Bin not found")
    return row

