from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.user import UserRole, UserStatus

class UserBase(BaseModel):
    email: EmailStr | None = None
    mobile_number: str = Field(..., max_length=15)
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    profile_image_url: str | None = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)
    role: UserRole = UserRole.DRIVER
    
    company_name: str | None = None
    gst_number: str | None = None
    pan_number: str | None = None
    address: str | None = None
    operating_cities: list[str] | None = None
    license_number: str | None = None

class VendorCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)
    company_name: str = Field(..., max_length=255)
    gst_number: str | None = None
    pan_number: str | None = None
    address: str | None = None
    operating_cities: list[str] | None = None

class DriverCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)
    license_number: str = Field(..., max_length=50)
    vendor_id: int = Field(..., description="ID of the vendor owning the fleet")

class UserStatusUpdate(BaseModel):
    status: UserStatus

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    role: UserRole
    status: UserStatus
    created_at: datetime
    
    company_name: str | None = None
    gst_number: str | None = None
    pan_number: str | None = None
    address: str | None = None
    operating_cities: list[str] | None = None
    license_number: str | None = None
