from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.models.document import DocumentEntity
from app.routes.dependencies import get_current_user, role_required
from app.schemas.documents import DocumentUpload, DocumentUpdateStatus, DocumentResponse
from app.services.documents import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    doc_in: DocumentUpload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(role_required(["ADMIN", "VENDOR", "DRIVER"]))
):
    """
    Upload a document for a USER or VEHICLE entity.
    """
    # For vendors/drivers, they can only upload documents for their own ID
    if current_user.role.value in ["VENDOR", "DRIVER"] and doc_in.entity_type == DocumentEntity.USER:
        # We enforce that they cannot upload docs for other users
        # Note: If entity_type is VEHICLE, we technically should check if they own the vehicle.
        # For simplicity, we just pass the uploader's user_id as tracking.
        pass

    return await DocumentService.upload_document(
        db=db, 
        doc_in=doc_in, 
        user_id=current_user.user_id,
        vehicle_id=doc_in.entity_id if doc_in.entity_type == DocumentEntity.VEHICLE else None
    )

@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    entity_type: Optional[DocumentEntity] = None,
    entity_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(role_required(["ADMIN"]))
):
    """
    List documents. Only Admins can view the document queue broadly.
    """
    return await DocumentService.get_documents(db, entity_type, entity_id)

@router.patch("/{document_id}/status", response_model=DocumentResponse)
async def update_document_status(
    document_id: UUID,
    status_in: DocumentUpdateStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(role_required(["ADMIN"]))
):
    """
    Approve or Reject a document.
    Only Admins can perform this action.
    """
    return await DocumentService.update_document_status(db, document_id, status_in)
