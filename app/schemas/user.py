from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole, UserStatus

class UserBase(BaseModel):
    email: EmailStr | None = None
    mobile_number: str = Field(..., max_length=15)
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    profile_image_url: str | None = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)
    role: UserRole = UserRole.USER
    
    # Optional Vendor details
    company_name: str | None = None
    gst_number: str | None = None
    pan_number: str | None = None
    address: str | None = None
    operating_cities: list[str] | None = None

    # Optional Driver details
    license_number: str | None = None

class UserResponse(UserBase):
    user_id: int
    role: UserRole
    status: UserStatus
    created_at: datetime
    
    # Profile details
    company_name: str | None = None
    gst_number: str | None = None
    pan_number: str | None = None
    address: str | None = None
    operating_cities: list[str] | None = None
    license_number: str | None = None
    
    class Config:
        from_attributes = True
