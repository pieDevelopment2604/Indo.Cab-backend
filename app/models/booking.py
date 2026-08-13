import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Enum, ForeignKey, Integer, Numeric, SmallInteger, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base_class import Base
from app.models.vehicle import VehicleType
from app.models.pricing import PricingTripType

class BookingSource(str, enum.Enum):
    MAKEMYTRIP = "MAKEMYTRIP"
    SAVAARI = "SAVAARI"
    INTERNAL = "INTERNAL"
    DIRECT = "DIRECT"

class BookingStatus(str, enum.Enum):
    RECEIVED = "RECEIVED"
    VENDOR_ASSIGNED = "VENDOR_ASSIGNED"
    VENDOR_ACCEPTED = "VENDOR_ACCEPTED"
    VENDOR_REJECTED = "VENDOR_REJECTED"
    DRIVER_ASSIGNED = "DRIVER_ASSIGNED"
    DRIVER_ACCEPTED = "DRIVER_ACCEPTED"
    DRIVER_REJECTED = "DRIVER_REJECTED"
    TRIP_SCHEDULED = "TRIP_SCHEDULED"
    TRIP_STARTED = "TRIP_STARTED"
    TRIP_COMPLETED = "TRIP_COMPLETED"
    CANCELLED = "CANCELLED"
    ESCALATED = "ESCALATED"

class AssignmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    TIMEOUT = "TIMEOUT"
    REASSIGNED = "REASSIGNED"

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)

    source_platform: Mapped[BookingSource] = mapped_column(Enum(BookingSource), nullable=False, index=True)
    external_booking_id: Mapped[str | None] = mapped_column(String(150), unique=True, nullable=True)
    
    client_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("clients.id", ondelete="SET NULL"), nullable=True, index=True
    )
    rate_card_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rate_cards.id", ondelete="SET NULL"), nullable=True
    )

    vehicle_type_required: Mapped[VehicleType] = mapped_column(Enum(VehicleType), nullable=False)
    trip_type: Mapped[PricingTripType] = mapped_column(Enum(PricingTripType), default=PricingTripType.ONE_WAY, nullable=False)

    pickup_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    pickup_address: Mapped[str] = mapped_column(Text, nullable=False)
    pickup_latitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    pickup_longitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    pickup_city: Mapped[str | None] = mapped_column(String(100), nullable=True)

    destination_address: Mapped[str] = mapped_column(Text, nullable=False)
    destination_latitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    destination_longitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    destination_city: Mapped[str | None] = mapped_column(String(100), nullable=True)

    estimated_distance_km: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    estimated_duration_min: Mapped[int | None] = mapped_column(Integer, nullable=True)

    stops: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    passenger_name: Mapped[str] = mapped_column(String(155), nullable=False)
    passenger_phone: Mapped[str] = mapped_column(String(15), nullable=False)
    passenger_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    passenger_count: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)
    special_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus), default=BookingStatus.RECEIVED, nullable=False, index=True)

    assigned_vendor_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True, index=True
    )
    assigned_driver_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True, index=True
    )
    assigned_vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True
    )

    sla_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    vendor_response_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    driver_response_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancelled_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True
    )

class BookingAssignmentLog(Base):
    __tablename__ = "booking_assignment_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    vendor_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True, index=True
    )
    driver_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True, index=True
    )
    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True
    )

    status: Mapped[AssignmentStatus] = mapped_column(Enum(AssignmentStatus), nullable=False, index=True)

    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    assigned_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True
    )
