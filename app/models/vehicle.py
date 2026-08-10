import enum
import uuid
from sqlalchemy import String, Enum, ForeignKey, Integer, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class VehicleType(str, enum.Enum):
    HATCHBACK = "HATCHBACK"
    SEDAN = "SEDAN"
    SUV = "SUV"
    PREMIUM_SEDAN = "PREMIUM_SEDAN"
    TRAVELLER = "TRAVELLER"

class VehicleStatus(str, enum.Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"

class Vehicle(Base):
    __tablename__ = "vehicles"

    # Override integer id with UUID
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    
    vehicle_type: Mapped[VehicleType] = mapped_column(Enum(VehicleType), nullable=False, index=True)
    status: Mapped[VehicleStatus] = mapped_column(
        Enum(VehicleStatus), default=VehicleStatus.PENDING_APPROVAL, nullable=False, index=True
    )

    registration_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(50), nullable=False)
    year_of_manufacture: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seating_capacity: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
