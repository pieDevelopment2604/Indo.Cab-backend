from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.document import DocumentEntity
from app.routes.dependencies import get_current_user, RoleChecker
from app.schemas.documents import DocumentUpload, DocumentUpdateStatus, DocumentResponse
from app.services.documents import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    doc_in: DocumentUpload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker([UserRole.ADMIN, UserRole.VENDOR, UserRole.DRIVER]))
):
    """
    Upload a document for a USER or VEHICLE entity.
    - Admins can upload for any user or vehicle.
    - Vendors/Drivers can only upload for themselves (USER) or their own vehicles (VEHICLE).
    """
    if doc_in.entity_type == DocumentEntity.USER:
        # Non-admins can only upload documents for their own account
        if current_user.role.value in ["VENDOR", "DRIVER"] and doc_in.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only upload documents for your own account."
            )
        return await DocumentService.upload_document(
            db=db, doc_in=doc_in,
            user_id=doc_in.user_id,
            vehicle_id=None
        )
    else:
        # VEHICLE document — validate ownership for non-admins
        if current_user.role.value in ["VENDOR", "DRIVER"]:
            await DocumentService.verify_vehicle_ownership(db, doc_in.vehicle_id, current_user.user_id)
        return await DocumentService.upload_document(
            db=db, doc_in=doc_in,
            user_id=None,
            vehicle_id=doc_in.vehicle_id
        )

@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    entity_type: Optional[DocumentEntity] = None,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker([UserRole.ADMIN, UserRole.VENDOR, UserRole.DRIVER]))
):
    """
    List documents.
    - Admins see all documents.
    - Vendors see their own + their vehicles' documents.
    - Drivers see only their own documents.
    """
    return await DocumentService.get_documents(
        db, entity_type=entity_type, status_filter=status_filter,
        current_user=current_user
    )

@router.patch("/{document_id}/status", response_model=DocumentResponse)
async def update_document_status(
    document_id: UUID,
    status_in: DocumentUpdateStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker([UserRole.ADMIN]))
):
    """
    Approve or Reject a document.
    Only Admins can perform this action.
    """
    return await DocumentService.update_document_status(db, document_id, status_in)
