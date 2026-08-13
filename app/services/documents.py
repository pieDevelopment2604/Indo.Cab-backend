from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.document import Document, DocumentStatus, DocumentEntity
from app.models.vehicle import Vehicle
from app.models.user import User, UserRole
from app.schemas.documents import DocumentUpload, DocumentUpdateStatus

class DocumentService:
    @staticmethod
    async def upload_document(
        db: AsyncSession,
        doc_in: DocumentUpload,
        user_id: Optional[int] = None,
        vehicle_id: Optional[UUID] = None
    ) -> Document:
        # Build document without entity_id (removed from schema)
        doc = Document(
            entity_type=doc_in.entity_type,
            document_type=doc_in.document_type,
            document_url=doc_in.document_url,
            file_name=doc_in.file_name,
            file_size_kb=doc_in.file_size_kb,
            mime_type=doc_in.mime_type,
            expiry_date=doc_in.expiry_date,
            user_id=user_id,
            vehicle_id=vehicle_id,
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        return doc

    @staticmethod
    async def verify_vehicle_ownership(db: AsyncSession, vehicle_id: UUID, user_id: int) -> None:
        """Verify that the given vehicle belongs to the user (vendor)."""
        result = await db.execute(
            select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.is_deleted == False)
        )
        vehicle = result.scalar_one_or_none()
        if not vehicle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")
        if vehicle.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not own this vehicle."
            )

    @staticmethod
    async def get_documents(
        db: AsyncSession,
        entity_type: Optional[DocumentEntity] = None,
        status_filter: Optional[str] = None,
        current_user: Optional[User] = None,
    ) -> List[Document]:
        query = select(Document).where(Document.is_deleted == False)

        if entity_type:
            query = query.where(Document.entity_type == entity_type)
        if status_filter:
            query = query.where(Document.status == status_filter)

        # RBAC filtering
        if current_user and current_user.role.value == "VENDOR":
            # Vendor sees their own user docs + docs for their vehicles
            vendor_vehicle_ids = select(Vehicle.id).where(
                Vehicle.owner_id == current_user.user_id,
                Vehicle.is_deleted == False
            )
            query = query.where(
                (Document.user_id == current_user.user_id) |
                (Document.vehicle_id.in_(vendor_vehicle_ids))
            )
        elif current_user and current_user.role.value == "DRIVER":
            # Driver sees only their own user docs
            query = query.where(Document.user_id == current_user.user_id)
        # Admin sees all (no filter)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_document_by_id(db: AsyncSession, document_id: UUID) -> Document:
        doc = await db.get(Document, document_id)
        if not doc or doc.is_deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        return doc

    @staticmethod
    async def update_document_status(db: AsyncSession, document_id: UUID, status_in: DocumentUpdateStatus) -> Document:
        doc = await DocumentService.get_document_by_id(db, document_id)
        
        if status_in.status == DocumentStatus.REJECTED and not status_in.rejection_reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Rejection reason is required when rejecting a document."
            )
            
        doc.status = status_in.status
        if status_in.status == DocumentStatus.REJECTED:
            doc.rejection_reason = status_in.rejection_reason
        else:
            doc.rejection_reason = None
            
        await db.commit()
        await db.refresh(doc)
        return doc
