import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.booking import Booking, BookingStatus
from app.schemas.bookings import BookingCreate

class BookingService:
    @staticmethod
    async def create_booking(db: AsyncSession, booking_in: BookingCreate) -> Booking:
        # Generate a unique 8-character booking number
        booking_number = f"BKG-{str(uuid.uuid4())[:8].upper()}"
        
        booking = Booking(
            **booking_in.model_dump(),
            booking_number=booking_number,
            status=BookingStatus.PENDING
        )
        db.add(booking)
        await db.commit()
        await db.refresh(booking)
        return booking

    @staticmethod
    async def get_bookings(db: AsyncSession, status_filter: Optional[BookingStatus] = None) -> List[Booking]:
        query = select(Booking)
        if status_filter:
            query = query.where(Booking.status == status_filter)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_booking_by_id(db: AsyncSession, booking_id: uuid.UUID) -> Booking:
        booking = await db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
        return booking

    @staticmethod
    async def update_booking_status(db: AsyncSession, booking_id: uuid.UUID, new_status: BookingStatus) -> Booking:
        booking = await BookingService.get_booking_by_id(db, booking_id)
        booking.status = new_status
        await db.commit()
        await db.refresh(booking)
        return booking
