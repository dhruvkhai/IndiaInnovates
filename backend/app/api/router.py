from fastapi import APIRouter

from app.api.routes import alerts, bins, classifications, rewards, routes, telemetry, trucks


api_router = APIRouter()
api_router.include_router(bins.router, prefix="/bins", tags=["bins"])
api_router.include_router(telemetry.router, prefix="/telemetry", tags=["telemetry"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(classifications.router, prefix="/classifications", tags=["classifications"])
api_router.include_router(routes.router, prefix="/routes", tags=["routes"])
api_router.include_router(rewards.router, prefix="/rewards", tags=["rewards"])
api_router.include_router(trucks.router, prefix="/trucks", tags=["trucks"])

