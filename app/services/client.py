from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.client import Client
from app.schemas.client import ClientCreate
from app.core.security import normalize_phone_number

class ClientService:
    @staticmethod
    async def get_by_id(db: AsyncSession, client_id: int) -> Client | None:
        result = await db.execute(
            select(Client).where(Client.id == client_id, Client.is_deleted == False)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email_or_phone(db: AsyncSession, mobile_number: str, email: str | None = None) -> Client | None:
        normalized_phone = normalize_phone_number(mobile_number)
        stmt = select(Client).where(
            (Client.mobile_number == normalized_phone) | (Client.mobile_number == mobile_number),
            Client.is_deleted == False
        )
        if email:
            stmt = select(Client).where(
                (Client.email == email) | (Client.mobile_number == normalized_phone),
                Client.is_deleted == False
            )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, client_in: ClientCreate) -> Client:
        normalized_phone = normalize_phone_number(client_in.mobile_number)
        db_client = Client(
            company_name=client_in.company_name,
            contact_person=client_in.contact_person,
            email=client_in.email,
            mobile_number=normalized_phone,
            gst_number=client_in.gst_number,
            pan_number=client_in.pan_number,
            address=client_in.address,
            operating_cities=client_in.operating_cities,
            discount_percentage=client_in.discount_percentage
        )
        db.add(db_client)
        await db.flush()
        return db_client

    @staticmethod
    async def list_clients(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Client]:
        result = await db.execute(
            select(Client)
            .where(Client.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
