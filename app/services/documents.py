from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.document import Document, DocumentStatus, DocumentEntity
from app.schemas.documents import DocumentUpload, DocumentUpdateStatus

class DocumentService:
    @staticmethod
    async def upload_document(db: AsyncSession, doc_in: DocumentUpload, user_id: Optional[int] = None, vehicle_id: Optional[UUID] = None) -> Document:
        doc = Document(
            **doc_in.model_dump(),
            user_id=user_id,
            vehicle_id=vehicle_id
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        return doc

    @staticmethod
    async def get_documents(db: AsyncSession, entity_type: Optional[DocumentEntity] = None, entity_id: Optional[UUID] = None) -> List[Document]:
        query = select(Document)
        if entity_type:
            query = query.where(Document.entity_type == entity_type)
        if entity_id:
            query = query.where(Document.entity_id == entity_id)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_document_by_id(db: AsyncSession, document_id: UUID) -> Document:
        doc = await db.get(Document, document_id)
        if not doc:
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
