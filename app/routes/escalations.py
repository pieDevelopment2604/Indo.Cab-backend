from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.models.escalation import EscalationStatus
from app.routes.dependencies import role_required
from app.schemas.escalations import EscalationCreate, EscalationUpdateStatus, EscalationResponse
from app.services.escalations import EscalationService

router = APIRouter(prefix="/escalations", tags=["Escalations"])

@router.post("", response_model=EscalationResponse, status_code=status.HTTP_201_CREATED)
async def create_escalation(
    escalation_in: EscalationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(role_required(["ADMIN", "USER", "VENDOR", "DRIVER"]))
):
    """
    Create a new escalation ticket.
    """
    return await EscalationService.create_escalation(db, escalation_in)

@router.get("", response_model=List[EscalationResponse])
async def list_escalations(
    status_filter: Optional[EscalationStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(role_required(["ADMIN"]))
):
    """
    List all escalations.
    """
    return await EscalationService.get_escalations(db, status_filter)

@router.get("/{escalation_id}", response_model=EscalationResponse)
async def get_escalation(
    escalation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(role_required(["ADMIN"]))
):
    """
    Get a specific escalation.
    """
    return await EscalationService.get_escalation_by_id(db, escalation_id)

@router.patch("/{escalation_id}/status", response_model=EscalationResponse)
async def update_escalation_status(
    escalation_id: UUID,
    status_in: EscalationUpdateStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(role_required(["ADMIN"]))
):
    """
    Update the status of an escalation ticket.
    """
    return await EscalationService.update_escalation_status(db, escalation_id, status_in)
