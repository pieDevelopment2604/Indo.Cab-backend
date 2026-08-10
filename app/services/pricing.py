from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.pricing import PricingZone, RateCard
from app.schemas.pricing import PricingZoneCreate, RateCardCreate

class PricingService:
    @staticmethod
    async def create_zone(db: AsyncSession, zone_in: PricingZoneCreate) -> PricingZone:
        zone = PricingZone(**zone_in.model_dump())
        db.add(zone)
        await db.commit()
        await db.refresh(zone)
        return zone

    @staticmethod
    async def get_zones(db: AsyncSession) -> List[PricingZone]:
        query = select(PricingZone)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_zone_by_id(db: AsyncSession, zone_id: UUID) -> PricingZone:
        zone = await db.get(PricingZone, zone_id)
        if not zone:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")
        return zone

    @staticmethod
    async def create_rate_card(db: AsyncSession, rate_card_in: RateCardCreate) -> RateCard:
        rate_card = RateCard(**rate_card_in.model_dump())
        db.add(rate_card)
        await db.commit()
        await db.refresh(rate_card)
        return rate_card

    @staticmethod
    async def get_rate_cards(db: AsyncSession, zone_id: Optional[UUID] = None) -> List[RateCard]:
        query = select(RateCard)
        if zone_id:
            query = query.where(RateCard.zone_id == zone_id)
        result = await db.execute(query)
        return result.scalars().all()
