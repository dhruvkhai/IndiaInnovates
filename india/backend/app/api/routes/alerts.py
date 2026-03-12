from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from app.db.models import Alert
from app.db.session import get_db
from app.schemas import AlertOut


router = APIRouter()


@router.get("", response_model=list[AlertOut])
async def list_alerts(active: int | None = 1, limit: int = 200, db: AsyncSession = Depends(get_db)):
    q = select(Alert).order_by(desc(Alert.created_at)).limit(limit)
    if active is not None:
        q = q.where(Alert.active == active)
    res = await db.execute(q)
    return list(res.scalars().all())


@router.post("/{alert_id}/resolve", response_model=AlertOut)
async def resolve_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    await db.execute(update(Alert).where(Alert.id == alert_id).values(active=0))
    await db.commit()
    row = await db.get(Alert, alert_id)
    return row

