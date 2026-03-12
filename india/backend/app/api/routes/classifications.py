from datetime import datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import ClassificationResult, WasteClass
from app.db.session import get_db
from app.schemas import ClassificationIn, ClassificationOut


router = APIRouter()


@router.post("", response_model=ClassificationOut)
async def create_classification(payload: ClassificationIn, db: AsyncSession = Depends(get_db)):
    row = ClassificationResult(
        bin_id=payload.bin_id,
        ts=payload.ts or datetime.utcnow(),
        waste_class=WasteClass(payload.waste_class),
        confidence=payload.confidence,
        image_ref=payload.image_ref,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


@router.get("/{bin_id}", response_model=list[ClassificationOut])
async def list_for_bin(bin_id: str, limit: int = 200, db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(ClassificationResult)
        .where(ClassificationResult.bin_id == bin_id)
        .order_by(desc(ClassificationResult.ts))
        .limit(limit)
    )
    return list(res.scalars().all())


@router.post("/ai/classify")
async def classify_via_ai_service(bin_id: str, image_url: str):
    """
    Convenience endpoint: forwards to AI service and returns its result.
    (Dashboard can call backend only; backend calls AI service.)
    """
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            r = await client.post(f"{settings.ai_service_url}/classify/url", json={"bin_id": bin_id, "image_url": image_url})
            r.raise_for_status()
            return r.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"AI service error: {e}") from e

