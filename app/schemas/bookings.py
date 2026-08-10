from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from app.models.booking import BookingSource, BookingStatus
from app.models.vehicle import VehicleType
from app.models.pricing import PricingTripType

class BookingBase(BaseModel):
    source_platform: BookingSource = Field(..., description="Source of the booking")
    external_booking_id: Optional[str] = Field(None, description="External booking ID if applicable")
    client_id: Optional[int] = Field(None, description="Optional Client ID for corporate bookings")
    rate_card_id: Optional[UUID] = Field(None, description="Rate card used for this booking")

    vehicle_type_required: VehicleType = Field(..., description="Requested vehicle type")
    trip_type: PricingTripType = Field(..., description="Type of trip")

    pickup_datetime: datetime = Field(..., description="Pickup date and time")
    pickup_address: str = Field(...)
    pickup_latitude: float = Field(...)
    pickup_longitude: float = Field(...)
    pickup_city: Optional[str] = Field(None)

    destination_address: str = Field(...)
    destination_latitude: float = Field(...)
    destination_longitude: float = Field(...)
    destination_city: Optional[str] = Field(None)

    estimated_distance_km: Optional[float] = Field(None)
    estimated_duration_min: Optional[int] = Field(None)

    stops: List[dict] = Field(default=[], description="List of intermediate stops")

    passenger_name: str = Field(...)
    passenger_phone: str = Field(...)
    passenger_email: Optional[EmailStr] = Field(None)
    passenger_count: int = Field(default=1)
    special_instructions: Optional[str] = Field(None)

class BookingCreate(BookingBase):
    pass

class BookingResponse(BookingBase):
    id: UUID
    booking_number: str
    status: BookingStatus
    
    assigned_vendor_id: Optional[int]
    assigned_driver_id: Optional[int]
    assigned_vehicle_id: Optional[UUID]

    sla_deadline: Optional[datetime]
    vendor_response_at: Optional[datetime]
    driver_response_at: Optional[datetime]

    cancelled_at: Optional[datetime]
    cancellation_reason: Optional[str]
    cancelled_by: Optional[int]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
