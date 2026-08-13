from pydantic import BaseModel, Field, model_validator
from uuid import UUID
from datetime import date, datetime
from typing import Optional
from app.models.document import DocumentStatus, DocumentEntity

class DocumentUpload(BaseModel):
    entity_type: DocumentEntity = Field(..., description="Entity type: USER or VEHICLE")
    document_type: str = Field(..., description="Type of document (e.g., RC, Insurance, PAN)")
    document_url: str = Field(..., description="S3 or external URL to the document")
    file_name: Optional[str] = Field(None, description="Original file name")
    file_size_kb: Optional[int] = Field(None, description="Size in KB")
    mime_type: Optional[str] = Field(None, description="MIME type")
    expiry_date: Optional[date] = Field(None, description="Expiration date of the document")
    # For USER documents, provide user_id (int). For VEHICLE documents, provide vehicle_id (UUID).
    user_id: Optional[int] = Field(None, description="Target user ID (required when entity_type is USER)")
    vehicle_id: Optional[UUID] = Field(None, description="Target vehicle ID (required when entity_type is VEHICLE)")

    @model_validator(mode="after")
    def validate_entity_ids(self):
        if self.entity_type == DocumentEntity.USER and self.user_id is None:
            raise ValueError("user_id is required when entity_type is USER")
        if self.entity_type == DocumentEntity.VEHICLE and self.vehicle_id is None:
            raise ValueError("vehicle_id is required when entity_type is VEHICLE")
        return self

class DocumentUpdateStatus(BaseModel):
    status: DocumentStatus = Field(..., description="Status (APPROVED/REJECTED)")
    rejection_reason: Optional[str] = Field(None, description="Required if status is REJECTED")

class DocumentResponse(BaseModel):
    id: UUID
    entity_type: DocumentEntity
    user_id: Optional[int] = None
    vehicle_id: Optional[UUID] = None
    document_type: str
    document_url: str
    file_name: Optional[str] = None
    file_size_kb: Optional[int] = None
    mime_type: Optional[str] = None
    expiry_date: Optional[date] = None
    status: DocumentStatus
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
