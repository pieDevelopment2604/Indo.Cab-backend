import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Enum, ForeignKey, Integer, Numeric, Text, DateTime, Boolean, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class TripStatus(str, enum.Enum):
    ASSIGNED = "ASSIGNED"
    NAVIGATING_TO_PICKUP = "NAVIGATING_TO_PICKUP"
    REACHED_PICKUP = "REACHED_PICKUP"
    IN_PROGRESS = "IN_PROGRESS"
    REACHED_DESTINATION = "REACHED_DESTINATION"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class DutyStatus(str, enum.Enum):
    OFF_DUTY = "OFF_DUTY"
    ON_DUTY = "ON_DUTY"
    ON_TRIP = "ON_TRIP"
    UNAVAILABLE = "UNAVAILABLE"

class ExpenseType(str, enum.Enum):
    TOLL = "TOLL"
    PARKING = "PARKING"
    PERMIT = "PERMIT"
    FUEL = "FUEL"
    MISCELLANEOUS = "MISCELLANEOUS"

class DriverDutyLog(Base):
    __tablename__ = "driver_duty_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    driver_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[DutyStatus] = mapped_column(Enum(DutyStatus), nullable=False)
    
    start_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    
    booking_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="RESTRICT"), unique=True, nullable=False)
    driver_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False, index=True)
    vehicle_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="RESTRICT"), nullable=False, index=True)
    vendor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True, index=True)

    status: Mapped[TripStatus] = mapped_column(Enum(TripStatus), default=TripStatus.ASSIGNED, nullable=False, index=True)

    pre_duty_checked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    pre_duty_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    vehicle_interior_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    vehicle_exterior_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    water_bottle_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cleanliness_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fuel_level_ok: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    documents_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    start_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_km: Mapped[int | None] = mapped_column(Integer, nullable=True)

    start_location_lat: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    start_location_lng: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    end_location_lat: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    end_location_lng: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)

    navigating_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reached_pickup_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    trip_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reached_destination_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    actual_distance_km: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    actual_duration_min: Mapped[int | None] = mapped_column(Integer, nullable=True)

    customer_signature_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    driver_remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    customer_rating: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    customer_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

class TripExpense(Base):
    __tablename__ = "trip_expenses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    
    expense_type: Mapped[ExpenseType] = mapped_column(Enum(ExpenseType), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    receipt_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    approved: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    approved_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class TripLocationHistory(Base):
    __tablename__ = "trip_location_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    driver_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    
    latitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    speed_kmh: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    heading: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    # Append-only high-volume table — suppress Base audit columns
    updated_at = None
    created_by = None
    updated_by = None
    is_deleted = None
    deleted_at = None
