import enum
import uuid
from sqlalchemy import String, Enum, ForeignKey, Numeric, Boolean, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base
from app.models.vehicle import VehicleType

class PricingZoneType(str, enum.Enum):
    CITY = "CITY"
    STATE = "STATE"
    NATIONAL = "NATIONAL"

class PricingTripType(str, enum.Enum):
    ONE_WAY = "ONE_WAY"
    ROUND_TRIP = "ROUND_TRIP"
    LOCAL = "LOCAL"
    AIRPORT = "AIRPORT"

class PricingZone(Base):
    __tablename__ = "pricing_zones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    zone_type: Mapped[PricingZoneType] = mapped_column(Enum(PricingZoneType), nullable=False)
    cities: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

class RateCard(Base):
    __tablename__ = "rate_cards"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    vehicle_type: Mapped[VehicleType] = mapped_column(Enum(VehicleType), nullable=False, index=True)
    trip_type: Mapped[PricingTripType] = mapped_column(Enum(PricingTripType), nullable=False)
    
    zone_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pricing_zones.id", ondelete="SET NULL"), nullable=True, index=True
    )

    base_fare: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    per_km_rate: Mapped[float] = mapped_column(Numeric(8, 4), default=0.00, nullable=False)
    per_minute_rate: Mapped[float] = mapped_column(Numeric(8, 4), default=0.00, nullable=False)
    included_km: Mapped[float] = mapped_column(Numeric(8, 2), default=0.00, nullable=False)
    included_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    extra_km_rate: Mapped[float] = mapped_column(Numeric(8, 4), default=0.00, nullable=False)
    extra_minute_rate: Mapped[float] = mapped_column(Numeric(8, 4), default=0.00, nullable=False)
    night_charge_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00, nullable=False)
    holiday_charge_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00, nullable=False)

    vendor_payout_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00, nullable=False)
    vendor_flat_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)

    gst_rate_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=5.00, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
