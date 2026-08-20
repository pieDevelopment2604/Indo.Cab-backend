from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime, date
from typing import Optional
from app.models.vehicle import VehicleType, VehicleStatus, FuelType

class VehicleBase(BaseModel):
    owner_id: int = Field(..., description="ID of the vendor/owner")
    vehicle_type: VehicleType = Field(..., description="Type of the vehicle")
    registration_number: str = Field(..., description="Vehicle registration plate number")
    brand: str = Field(..., description="Make/Brand of the vehicle")
    model: str = Field(..., description="Model of the vehicle")
    color: str = Field(..., description="Color of the vehicle")
    year_of_manufacture: Optional[int] = Field(None, description="Year of manufacture")
    seating_capacity: Optional[int] = Field(None, description="Total seating capacity")
    fuel_type: Optional[FuelType] = Field(None, description="Type of fuel used by the vehicle")
    engine_number: Optional[str] = Field(None, description="Engine number (optional)")
    chassis_number: Optional[str] = Field(None, description="Chassis number (optional)")
    rc_valid_upto: Optional[date] = Field(None, description="RC validity date")
    puc_number: Optional[str] = Field(None, description="PUC certificate number")
    puc_valid_upto: Optional[date] = Field(None, description="PUC validity date")
    insurance_policy_number: Optional[str] = Field(None, description="Insurance policy number")
    insurance_valid_upto: Optional[date] = Field(None, description="Insurance validity date")
    permit_type_and_number: Optional[str] = Field(None, description="Permit type and number")
    permit_valid_upto: Optional[date] = Field(None, description="Permit validity date")
    fitness_cert_number: Optional[str] = Field(None, description="Fitness certificate number")
    fitness_valid_upto: Optional[date] = Field(None, description="Fitness validity date")
    fastag_barcode: Optional[str] = Field(None, description="FASTag barcode or Tag ID")
    road_tax_paid_upto: Optional[date] = Field(None, description="Road tax validity date")

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
