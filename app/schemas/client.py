from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.client import ClientStatus

class ClientCreate(BaseModel):
    company_name: str = Field(..., max_length=255)
    contact_person: str = Field(..., max_length=100)
    email: EmailStr | None = None
    mobile_number: str = Field(..., max_length=15)
    gst_number: str | None = None
    pan_number: str | None = None
    address: str | None = None
    operating_cities: list[str] | None = None
    discount_percentage: float = Field(default=0.0, ge=0.0, le=100.0)

class ClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_name: str
    contact_person: str
    email: str | None = None
    mobile_number: str
    gst_number: str | None = None
    pan_number: str | None = None
    address: str | None = None
    operating_cities: list[str] | None = None
    discount_percentage: float
    status: ClientStatus
    created_at: datetime


class ClientUpdate(BaseModel):
    company_name: str | None = Field(None, max_length=255)
    contact_person: str | None = Field(None, max_length=100)
    email: EmailStr | None = None
    mobile_number: str | None = Field(None, max_length=15)
    gst_number: str | None = None
    pan_number: str | None = None
    address: str | None = None
    operating_cities: list[str] | None = None
    discount_percentage: float | None = Field(None, ge=0.0, le=100.0)


class ClientStatusUpdate(BaseModel):
    status: ClientStatus
