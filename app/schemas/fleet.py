from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.models.vehicle import VehicleType, VehicleStatus

class VehicleBase(BaseModel):
    owner_id: int = Field(..., description="ID of the vendor/owner")
    vehicle_type: VehicleType = Field(..., description="Type of the vehicle")
    registration_number: str = Field(..., description="Vehicle registration plate number")
    brand: str = Field(..., description="Make/Brand of the vehicle")
    model: str = Field(..., description="Model of the vehicle")
    color: str = Field(..., description="Color of the vehicle")
    year_of_manufacture: Optional[int] = Field(None, description="Year of manufacture")
    seating_capacity: Optional[int] = Field(None, description="Total seating capacity")

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdateStatus(BaseModel):
    status: VehicleStatus = Field(..., description="New status for the vehicle")

class VehicleResponse(VehicleBase):
    id: UUID
    status: VehicleStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
