from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.client import Client, ClientStatus
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
    async def get_by_email_or_phone(
        db: AsyncSession, mobile_number: str, email: str | None = None
    ) -> Client | None:
        normalized_phone = normalize_phone_number(mobile_number)

        # Check by phone first
        stmt = select(Client).where(
            (Client.mobile_number == normalized_phone) | (Client.mobile_number == mobile_number),
            Client.is_deleted == False,
        )
        if email:
            # Widen search to also match email
            stmt = select(Client).where(
                (Client.email == email) | (Client.mobile_number == normalized_phone),
                Client.is_deleted == False,
            )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession, client_in: ClientCreate, created_by_id: int | None = None
    ) -> Client:
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
            discount_percentage=client_in.discount_percentage,
            created_by=created_by_id,  # Audit: admin who created this record
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

    @staticmethod
    async def update(db: AsyncSession, client: Client, update_data: dict) -> Client:
        for field, value in update_data.items():
            if field == "mobile_number" and value is not None:
                value = normalize_phone_number(value)
            setattr(client, field, value)
        db.add(client)
        await db.flush()
        return client

    @staticmethod
    async def update_status(db: AsyncSession, client: Client, status: ClientStatus) -> Client:
        client.status = status
        db.add(client)
        await db.flush()
        return client

    @staticmethod
    async def delete(db: AsyncSession, client: Client) -> None:
        client.is_deleted = True
        client.deleted_at = func.now()
        db.add(client)
        await db.flush()
