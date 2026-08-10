from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.routes.dependencies import role_required
from app.schemas.pricing import PricingZoneCreate, PricingZoneResponse, RateCardCreate, RateCardResponse
from app.services.pricing import PricingService

router = APIRouter(prefix="/pricing", tags=["Pricing"])

@router.post("/zones", response_model=PricingZoneResponse, status_code=status.HTTP_201_CREATED)
async def create_pricing_zone(
    zone_in: PricingZoneCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(role_required(["ADMIN"]))
):
    """
    Create a new pricing zone. Admins only.
    """
    return await PricingService.create_zone(db, zone_in)

@router.get("/zones", response_model=List[PricingZoneResponse])
async def list_pricing_zones(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(role_required(["ADMIN"]))
):
    """
    List all pricing zones.
    """
    return await PricingService.get_zones(db)

@router.post("/rate-cards", response_model=RateCardResponse, status_code=status.HTTP_201_CREATED)
async def create_rate_card(
    rate_card_in: RateCardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(role_required(["ADMIN"]))
):
    """
    Create a new rate card. Admins only.
    """
    return await PricingService.create_rate_card(db, rate_card_in)

@router.get("/rate-cards", response_model=List[RateCardResponse])
async def list_rate_cards(
    zone_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(role_required(["ADMIN"]))
):
    """
    List all rate cards, optionally filtered by zone.
    """
    return await PricingService.get_rate_cards(db, zone_id)
