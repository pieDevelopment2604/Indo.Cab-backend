from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator
from datetime import datetime
from app.models.user import UserRole, UserStatus


class UserBase(BaseModel):
    email: EmailStr | None = None
    mobile_number: str = Field(..., max_length=15)
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    profile_image_url: str | None = None


class UserCreate(UserBase):
    """Internal schema used by services/admin routes to create any user type."""
    password: str = Field(..., min_length=6, max_length=100)
    role: UserRole = UserRole.DRIVER

    # Vendor-specific
    company_name: str | None = None
    gst_number: str | None = None
    pan_number: str | None = None
    address: str | None = None
    operating_cities: list[str] | None = None

    # Driver-specific
    license_number: str | None = None
    vendor_id: int | None = None  # FK to the owning vendor (DRIVER role only)


class VendorCreate(UserBase):
    """Used by admin to onboard a new vendor."""
    password: str = Field(..., min_length=6, max_length=100)
    company_name: str = Field(..., max_length=255)
    gst_number: str | None = None
    pan_number: str | None = None
    address: str | None = None
    operating_cities: list[str] | None = None


class DriverCreate(UserBase):
    """Used by admin (or future: vendor portal) to onboard a new driver."""
    password: str = Field(..., min_length=6, max_length=100)
    license_number: str = Field(..., max_length=50)
    vendor_id: int = Field(..., description="ID of the vendor who owns this driver")


class UserStatusUpdate(BaseModel):
    status: UserStatus


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    role: UserRole
    status: UserStatus
    created_at: datetime

    # Vendor fields
    company_name: str | None = None
    gst_number: str | None = None
    pan_number: str | None = None
    address: str | None = None
    operating_cities: list[str] | None = None

    # Driver fields
    license_number: str | None = None
    vendor_id: int | None = None

    @model_validator(mode="after")
    def populate_vendor_id(self) -> "UserResponse":
        if self.role == UserRole.VENDOR:
            self.vendor_id = self.user_id
        return self
