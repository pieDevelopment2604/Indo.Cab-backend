import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Enum, ForeignKey, Integer, Numeric, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class InvoiceStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    PAID = "PAID"
    VOID = "VOID"

class SettlementStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PAID = "PAID"
    FAILED = "FAILED"

class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    
    booking_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="RESTRICT"), unique=True, nullable=False, index=True)
    trip_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="SET NULL"), unique=True, nullable=True)
    client_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("clients.id", ondelete="SET NULL"), nullable=True, index=True)
    rate_card_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("rate_cards.id", ondelete="SET NULL"), nullable=True)

    base_fare: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    extra_distance_fare: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    extra_time_fare: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    night_surcharge: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    holiday_surcharge: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    tolls_total: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    parking_total: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    permit_total: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    other_expenses: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    client_discount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    gst_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    gross_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)

    billed_distance_km: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    billed_duration_min: Mapped[int | None] = mapped_column(Integer, nullable=True)

    status: Mapped[InvoiceStatus] = mapped_column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False, index=True)
    issued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    payment_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payment_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

class VendorSettlement(Base):
    __tablename__ = "vendor_settlements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    settlement_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    
    vendor_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False, index=True)
    invoice_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="RESTRICT"), unique=True, nullable=False)
    trip_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="SET NULL"), nullable=True)

    gross_invoice_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    vendor_payout_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    vendor_payout_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    expense_reimbursement: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    total_payout: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)

    status: Mapped[SettlementStatus] = mapped_column(Enum(SettlementStatus), default=SettlementStatus.PENDING, nullable=False, index=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    payment_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payment_mode: Mapped[str | None] = mapped_column(String(50), nullable=True)
    bank_account_no: Mapped[str | None] = mapped_column(String(50), nullable=True)
    bank_ifsc: Mapped[str | None] = mapped_column(String(20), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
