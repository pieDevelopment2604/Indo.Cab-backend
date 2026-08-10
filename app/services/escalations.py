from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.escalation import Escalation, EscalationStatus
from app.schemas.escalations import EscalationCreate, EscalationUpdateStatus

class EscalationService:
    @staticmethod
    async def create_escalation(db: AsyncSession, escalation_in: EscalationCreate) -> Escalation:
        escalation = Escalation(**escalation_in.model_dump())
        db.add(escalation)
        await db.commit()
        await db.refresh(escalation)
        return escalation

    @staticmethod
    async def get_escalations(db: AsyncSession, status_filter: Optional[EscalationStatus] = None) -> List[Escalation]:
        query = select(Escalation)
        if status_filter:
            query = query.where(Escalation.status == status_filter)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_escalation_by_id(db: AsyncSession, escalation_id: UUID) -> Escalation:
        escalation = await db.get(Escalation, escalation_id)
        if not escalation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escalation not found")
        return escalation

    @staticmethod
    async def update_escalation_status(db: AsyncSession, escalation_id: UUID, status_in: EscalationUpdateStatus) -> Escalation:
        escalation = await EscalationService.get_escalation_by_id(db, escalation_id)
        
        escalation.status = status_in.status
        if status_in.resolution_notes:
            escalation.resolution_notes = status_in.resolution_notes
        if status_in.assigned_to:
            escalation.assigned_to = status_in.assigned_to
            
        await db.commit()
        await db.refresh(escalation)
        return escalation
