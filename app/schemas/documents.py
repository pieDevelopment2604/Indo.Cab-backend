from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date, datetime
from typing import Optional
from app.models.document import DocumentStatus, DocumentEntity

class DocumentBase(BaseModel):
    entity_type: DocumentEntity = Field(..., description="Entity type: USER or VEHICLE")
    entity_id: UUID = Field(..., description="ID of the entity (UUID)")
    document_type: str = Field(..., description="Type of document (e.g., RC, Insurance, PAN)")
    document_url: str = Field(..., description="S3 or external URL to the document")
    file_name: Optional[str] = Field(None, description="Original file name")
    file_size_kb: Optional[int] = Field(None, description="Size in KB")
    mime_type: Optional[str] = Field(None, description="MIME type")
    expiry_date: Optional[date] = Field(None, description="Expiration date of the document")

class DocumentUpload(DocumentBase):
    pass

class DocumentUpdateStatus(BaseModel):
    status: DocumentStatus = Field(..., description="Status (APPROVED/REJECTED)")
    rejection_reason: Optional[str] = Field(None, description="Required if status is REJECTED")

class DocumentResponse(DocumentBase):
    id: UUID
    user_id: Optional[int]
    vehicle_id: Optional[UUID]
    status: DocumentStatus
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
