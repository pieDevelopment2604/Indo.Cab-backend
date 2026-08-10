import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Enum, ForeignKey, Integer, Text, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.sql import func
from app.db.base_class import Base
from app.models.user import UserRole

class AuditAction(str, enum.Enum):
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    SUSPEND = "SUSPEND"
    ACTIVATE = "ACTIVATE"
    ASSIGN = "ASSIGN"
    REASSIGN = "REASSIGN"
    ACCEPT = "ACCEPT"
    DECLINE = "DECLINE"
    TRIP_START = "TRIP_START"
    TRIP_COMPLETE = "TRIP_COMPLETE"
    TRIP_CANCEL = "TRIP_CANCEL"
    INVOICE_ISSUE = "INVOICE_ISSUE"
    SETTLEMENT_PAID = "SETTLEMENT_PAID"
    DOCUMENT_UPLOAD = "DOCUMENT_UPLOAD"
    DOCUMENT_APPROVE = "DOCUMENT_APPROVE"
    DOCUMENT_REJECT = "DOCUMENT_REJECT"

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    actor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True, index=True)
    actor_role: Mapped[UserRole | None] = mapped_column(Enum(UserRole), nullable=True)
    
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction), nullable=False, index=True)
    
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    entity_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    old_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # AuditLogs are immutable, we just need created_at. We override the base defaults.
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    
    # Disable update/delete fields for this specific immutable table
    updated_at = None
    created_by = None
    updated_by = None
    is_deleted = None
    deleted_at = None
