import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.services.ingest_queue import telemetry_queue
from app.services.mqtt_ingest import start_mqtt, stop_mqtt
from app.services.telemetry_handler import handle_telemetry

# Ensure models are imported/registered
from app.db import models as _models  # noqa: F401  (import for side-effects)


logging.basicConfig(level=getattr(logging, settings.backend_log_level.upper(), logging.INFO))

app = FastAPI(title="Smart Waste Management API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.backend_cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health():
    return {"ok": True}


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    loop = asyncio.get_running_loop()
    app.state.mqtt_client = start_mqtt(loop)

    async def consumer():
        await telemetry_queue.run_consumer(lambda payload: handle_telemetry(SessionLocal, payload))

    app.state.telemetry_task = asyncio.create_task(consumer())


@app.on_event("shutdown")
async def on_shutdown():
    stop_mqtt(getattr(app.state, "mqtt_client", None))
    task = getattr(app.state, "telemetry_task", None)
    if task is not None:
        task.cancel()

