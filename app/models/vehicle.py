import enum
import uuid
from datetime import date
from sqlalchemy import String, Enum, ForeignKey, Integer, SmallInteger, Date
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

class FuelType(str, enum.Enum):
    PETROL = "PETROL"
    DIESEL = "DIESEL"
    CNG = "CNG"
    ELECTRIC = "ELECTRIC"
    HYBRID = "HYBRID"

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
    
    fuel_type: Mapped[FuelType | None] = mapped_column(Enum(FuelType), nullable=True)
    engine_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    chassis_number: Mapped[str | None] = mapped_column(String(100), nullable=True)

    rc_valid_upto: Mapped[date | None] = mapped_column(Date, nullable=True)
    puc_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    puc_valid_upto: Mapped[date | None] = mapped_column(Date, nullable=True)
    insurance_policy_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    insurance_valid_upto: Mapped[date | None] = mapped_column(Date, nullable=True)
    permit_type_and_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    permit_valid_upto: Mapped[date | None] = mapped_column(Date, nullable=True)
    fitness_cert_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    fitness_valid_upto: Mapped[date | None] = mapped_column(Date, nullable=True)
    fastag_barcode: Mapped[str | None] = mapped_column(String(100), nullable=True)
    road_tax_paid_upto: Mapped[date | None] = mapped_column(Date, nullable=True)
