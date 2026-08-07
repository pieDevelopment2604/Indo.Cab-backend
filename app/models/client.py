import enum
from sqlalchemy import String, Enum, Text, JSON, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base

class ClientStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class Client(Base):
    __tablename__ = "clients"

    id = None
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)

    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    contact_person: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    mobile_number: Mapped[str] = mapped_column(String(15), unique=True, nullable=False, index=True)

    gst_number: Mapped[str | None] = mapped_column(String(15), nullable=True)
    pan_number: Mapped[str | None] = mapped_column(String(10), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    operating_cities: Mapped[list | None] = mapped_column(JSON, nullable=True)

    discount_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[ClientStatus] = mapped_column(Enum(ClientStatus), default=ClientStatus.ACTIVE, nullable=False)
