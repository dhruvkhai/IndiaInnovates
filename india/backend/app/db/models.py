import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class WasteClass(str, enum.Enum):
    recyclable = "recyclable"
    biodegradable = "biodegradable"
    hazardous = "hazardous"


class Bin(Base):
    __tablename__ = "bins"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    readings: Mapped[list["SensorReading"]] = relationship(back_populates="bin", cascade="all, delete-orphan")
    classifications: Mapped[list["ClassificationResult"]] = relationship(
        back_populates="bin", cascade="all, delete-orphan"
    )


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bin_id: Mapped[str] = mapped_column(ForeignKey("bins.id", ondelete="CASCADE"), index=True)

    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    # Sensors (simulated)
    ir_detected: Mapped[int] = mapped_column(Integer, default=0)  # 0/1
    fill_level_pct: Mapped[float] = mapped_column(Float, default=0.0)  # ultrasonic -> %
    weight_kg: Mapped[float] = mapped_column(Float, default=0.0)  # load cell
    gas_ppm: Mapped[float] = mapped_column(Float, default=0.0)  # gas sensor
    temperature_c: Mapped[float] = mapped_column(Float, default=0.0)
    humidity_pct: Mapped[float] = mapped_column(Float, default=0.0)

    bin: Mapped["Bin"] = relationship(back_populates="readings")


class ClassificationResult(Base):
    __tablename__ = "classification_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bin_id: Mapped[str] = mapped_column(ForeignKey("bins.id", ondelete="CASCADE"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    waste_class: Mapped[WasteClass] = mapped_column(Enum(WasteClass), index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    image_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)

    bin: Mapped["Bin"] = relationship(back_populates="classifications")


class AlertType(str, enum.Enum):
    bin_full = "bin_full"
    high_gas = "high_gas"
    high_temp = "high_temp"


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (UniqueConstraint("bin_id", "type", "active", name="uq_alert_bin_type_active"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bin_id: Mapped[str] = mapped_column(ForeignKey("bins.id", ondelete="CASCADE"), index=True)
    type: Mapped[AlertType] = mapped_column(Enum(AlertType), index=True)
    message: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    active: Mapped[int] = mapped_column(Integer, default=1)  # 0/1


class Citizen(Base):
    __tablename__ = "citizens"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    points: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class RewardTransaction(Base):
    __tablename__ = "reward_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    citizen_id: Mapped[str] = mapped_column(ForeignKey("citizens.id", ondelete="CASCADE"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    bin_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    waste_class: Mapped[WasteClass | None] = mapped_column(Enum(WasteClass), nullable=True)
    delta_points: Mapped[int] = mapped_column(Integer, default=0)
    reason: Mapped[str] = mapped_column(String(256), default="")


class TruckLocation(Base):
    __tablename__ = "truck_locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    truck_id: Mapped[str] = mapped_column(String(64), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(64), default="idle")

