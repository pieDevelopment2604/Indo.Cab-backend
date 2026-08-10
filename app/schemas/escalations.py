from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.models.escalation import EscalationReason, EscalationStatus

class EscalationBase(BaseModel):
    booking_id: Optional[UUID] = Field(None, description="Related booking ID")
    trip_id: Optional[UUID] = Field(None, description="Related trip ID")
    reason: EscalationReason = Field(...)
    description: Optional[str] = Field(None, description="Detailed description of the issue")

class EscalationCreate(EscalationBase):
    pass

class EscalationUpdateStatus(BaseModel):
    status: EscalationStatus = Field(...)
    resolution_notes: Optional[str] = Field(None)
    assigned_to: Optional[int] = Field(None, description="User ID of the support agent")

class EscalationResponse(EscalationBase):
    id: UUID
    status: EscalationStatus
    assigned_to: Optional[int]
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
