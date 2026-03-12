from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.config import settings
from app.db.models import Alert, AlertType, Bin, SensorReading


async def handle_telemetry(session_maker: async_sessionmaker, payload: dict) -> None:
    """
    Payload shape (sent by simulator):
    {
      "bin_id": "BIN_001",
      "ts": "2026-03-12T12:00:00Z",
      "ir_detected": 1,
      "fill_level_pct": 72.5,
      "weight_kg": 14.2,
      "gas_ppm": 120.0,
      "temperature_c": 32.0,
      "humidity_pct": 70.0,
      "lat": 28.6139,
      "lng": 77.2090
    }
    """
    bin_id = str(payload.get("bin_id", "")).strip()
    if not bin_id:
        return

    ts_raw = payload.get("ts")
    ts = None
    if isinstance(ts_raw, str):
        try:
            ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        except ValueError:
            ts = None

    fill = float(payload.get("fill_level_pct") or 0.0)

    async with session_maker() as session:
        bin_row = await session.get(Bin, bin_id)
        if bin_row is None:
            lat = float(payload.get("lat") or 0.0)
            lng = float(payload.get("lng") or 0.0)
            bin_row = Bin(id=bin_id, name=payload.get("name"), lat=lat, lng=lng)
            session.add(bin_row)

        reading = SensorReading(
            bin_id=bin_id,
            ts=ts or datetime.utcnow(),
            ir_detected=int(payload.get("ir_detected") or 0),
            fill_level_pct=fill,
            weight_kg=float(payload.get("weight_kg") or 0.0),
            gas_ppm=float(payload.get("gas_ppm") or 0.0),
            temperature_c=float(payload.get("temperature_c") or 0.0),
            humidity_pct=float(payload.get("humidity_pct") or 0.0),
        )
        session.add(reading)

        if fill >= settings.full_threshold_pct:
            existing = await session.execute(
                select(Alert).where(
                    Alert.bin_id == bin_id,
                    Alert.type == AlertType.bin_full,
                    Alert.active == 1,
                )
            )
            if existing.scalar_one_or_none() is None:
                session.add(
                    Alert(
                        bin_id=bin_id,
                        type=AlertType.bin_full,
                        message=f"Bin {bin_id} is {fill:.1f}% full",
                        active=1,
                    )
                )

        await session.commit()

