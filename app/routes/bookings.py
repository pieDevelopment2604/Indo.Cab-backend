import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.models.booking import BookingStatus
from app.routes.dependencies import role_required
from app.schemas.bookings import BookingCreate, BookingResponse
from app.services.bookings import BookingService

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_in: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(role_required(["ADMIN", "USER", "VENDOR"]))
):
    """
    Create a new booking.
    """
    return await BookingService.create_booking(db, booking_in)

@router.get("", response_model=List[BookingResponse])
async def list_bookings(
    status_filter: Optional[BookingStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(role_required(["ADMIN"]))
):
    """
    List all bookings, optionally filtered by status.
    """
    return await BookingService.get_bookings(db, status_filter)

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(role_required(["ADMIN", "USER", "VENDOR", "DRIVER"]))
):
    """
    Get details of a specific booking.
    """
    return await BookingService.get_booking_by_id(db, booking_id)
