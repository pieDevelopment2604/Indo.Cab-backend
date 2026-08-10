from pydantic import BaseModel, Field, condecimal
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from app.models.pricing import PricingZoneType, PricingTripType
from app.models.vehicle import VehicleType
from decimal import Decimal

class PricingZoneBase(BaseModel):
    name: str = Field(..., description="Name of the pricing zone")
    zone_type: PricingZoneType = Field(..., description="Zone type")
    cities: List[str] = Field(..., description="List of cities covered in this zone")

class PricingZoneCreate(PricingZoneBase):
    pass

class PricingZoneResponse(PricingZoneBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RateCardBase(BaseModel):
    name: str = Field(..., description="Name of the rate card")
    vehicle_type: VehicleType = Field(..., description="Vehicle type")
    trip_type: PricingTripType = Field(..., description="Trip type")
    zone_id: Optional[UUID] = Field(None, description="Optional zone UUID")

    base_fare: Decimal = Field(..., max_digits=10, decimal_places=2)
    per_km_rate: Decimal = Field(..., max_digits=8, decimal_places=4)
    per_minute_rate: Decimal = Field(..., max_digits=8, decimal_places=4)
    included_km: Decimal = Field(..., max_digits=8, decimal_places=2)
    included_minutes: int = Field(...)

    extra_km_rate: Decimal = Field(..., max_digits=8, decimal_places=4)
    extra_minute_rate: Decimal = Field(..., max_digits=8, decimal_places=4)
    night_charge_pct: Decimal = Field(..., max_digits=5, decimal_places=2)
    holiday_charge_pct: Decimal = Field(..., max_digits=5, decimal_places=2)

    vendor_payout_pct: Decimal = Field(..., max_digits=5, decimal_places=2)
    vendor_flat_amount: Decimal = Field(..., max_digits=10, decimal_places=2)

    gst_rate_pct: Decimal = Field(default=5.00, max_digits=5, decimal_places=2)
    is_active: bool = Field(default=True)

class RateCardCreate(RateCardBase):
    pass

class RateCardResponse(RateCardBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
