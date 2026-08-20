import enum
import uuid
from datetime import date
from sqlalchemy import String, Enum, Text, JSON, Integer, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base


class UserRole(str, enum.Enum):
    SUPERADMIN = "SUPERADMIN"
    ADMIN = "ADMIN"
    VENDOR = "VENDOR"
    DRIVER = "DRIVER"


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INVITED = "INVITED"
    SUSPENDED = "SUSPENDED"
    INACTIVE = "INACTIVE"


class User(Base):
    __tablename__ = "users"

    # Override the generic `id` from Base with role-specific `user_id`
    id = None
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)

    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    mobile_number: Mapped[str] = mapped_column(String(15), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    profile_image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)

    # -------------------------------------------------------------------------
    # Vendor-specific fields (populated when role = VENDOR)
    # -------------------------------------------------------------------------
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gst_number: Mapped[str | None] = mapped_column(String(15), nullable=True)
    pan_number: Mapped[str | None] = mapped_column(String(10), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    operating_cities: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # -------------------------------------------------------------------------
    # Driver-specific fields (populated when role = DRIVER)
    # -------------------------------------------------------------------------
    license_number: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)

    # Foreign key to the vendor who owns this driver.
    # Only populated for DRIVER role. Replaces the previous created_by abuse.
    vendor_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # Extra Driver Profile Fields
    aadhaar_number: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    blood_group: Mapped[str | None] = mapped_column(String(5), nullable=True)
    date_of_birth: Mapped[Date | None] = mapped_column(Date, nullable=True)
    dl_expiry: Mapped[Date | None] = mapped_column(Date, nullable=True)
    dl_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    experience_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hub: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pincode: Mapped[str | None] = mapped_column(String(10), nullable=True)

    assigned_vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True, index=True
    )
