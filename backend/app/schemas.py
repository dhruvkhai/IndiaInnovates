from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


WasteClass = Literal["recyclable", "biodegradable", "hazardous"]


class BinCreate(BaseModel):
    id: str = Field(min_length=1, max_length=64)
    name: str | None = Field(default=None, max_length=128)
    lat: float
    lng: float


class BinOut(BaseModel):
    id: str
    name: str | None
    lat: float
    lng: float
    created_at: datetime


class SensorReadingIn(BaseModel):
    bin_id: str
    ts: datetime | None = None
    ir_detected: int = 0
    fill_level_pct: float = 0.0
    weight_kg: float = 0.0
    gas_ppm: float = 0.0
    temperature_c: float = 0.0
    humidity_pct: float = 0.0


class SensorReadingOut(SensorReadingIn):
    id: int
    ts: datetime


class ClassificationIn(BaseModel):
    bin_id: str
    waste_class: WasteClass
    confidence: float = 0.0
    image_ref: str | None = None
    ts: datetime | None = None


class ClassificationOut(ClassificationIn):
    id: int
    ts: datetime


class AlertOut(BaseModel):
    id: int
    bin_id: str
    type: str
    message: str
    created_at: datetime
    active: int


class OptimizeRouteRequest(BaseModel):
    start_node: str
    nodes: list[str]
    edges: list[tuple[str, str, float]]  # (u, v, distance_km)


class OptimizeRouteResponse(BaseModel):
    path: list[str]
    total_distance_km: float


class CitizenCreate(BaseModel):
    id: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=128)


class CitizenOut(BaseModel):
    id: str
    name: str
    points: int
    created_at: datetime


class AwardPointsRequest(BaseModel):
    citizen_id: str
    bin_id: str | None = None
    waste_class: WasteClass | None = None
    delta_points: int = 0
    reason: str = ""


class TruckLocationIn(BaseModel):
    truck_id: str
    lat: float
    lng: float
    status: str = "idle"
    ts: datetime | None = None


class TruckLocationOut(TruckLocationIn):
    id: int
    ts: datetime


# ========== IoT HTTP ingestion ==========


class BinDataIn(BaseModel):
    bin_id: str
    fill_level: float
    weight_kg: float
    temperature_c: float
    humidity_pct: float
    gas_ppm: float
    ts: datetime | None = None


class WasteClassificationIn(BaseModel):
    bin_id: str
    waste_type: WasteClass
    confidence: float
    image_ref: str | None = None
    ts: datetime | None = None


class BinStatusOut(BaseModel):
    bin_id: str
    name: str | None
    lat: float
    lng: float
    last_update: datetime | None
    fill_level_pct: float | None
    weight_kg: float | None
    temperature_c: float | None
    humidity_pct: float | None
    gas_ppm: float | None
    latest_waste_type: WasteClass | None = None
    latest_waste_confidence: float | None = None

