from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User, UserRole
from app.routes.dependencies import get_current_user, RoleChecker
from app.schemas.fleet import VehicleCreate, VehicleUpdateStatus, VehicleResponse
from app.services.fleet import FleetService

router = APIRouter(prefix="/fleet/vehicles", tags=["Fleet"])

@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    vehicle_in: VehicleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker([UserRole.ADMIN, UserRole.VENDOR]))
):
    """
    Create a new vehicle. 
    Vendors can only create vehicles for themselves. Admins can create vehicles for any vendor.
    """
    if current_user.role.value == "VENDOR" and vehicle_in.owner_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Vendors can only create vehicles for their own account.")
        
    return await FleetService.create_vehicle(db, vehicle_in)

@router.get("", response_model=List[VehicleResponse])
async def list_vehicles(
    owner_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker([UserRole.ADMIN, UserRole.VENDOR]))
):
    """
    List vehicles.
    Vendors only see their own vehicles. Admins see all, or filtered by owner_id.
    """
    if current_user.role.value == "VENDOR":
        owner_id = current_user.user_id
        
    return await FleetService.get_vehicles(db, owner_id)

@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker([UserRole.ADMIN, UserRole.VENDOR]))
):
    """
    Get vehicle details.
    """
    vehicle = await FleetService.get_vehicle_by_id(db, vehicle_id)
    if current_user.role.value == "VENDOR" and vehicle.owner_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this vehicle.")
    return vehicle

@router.patch("/{vehicle_id}/status", response_model=VehicleResponse)
async def update_vehicle_status(
    vehicle_id: UUID,
    status_in: VehicleUpdateStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker([UserRole.ADMIN]))
):
    """
    Update vehicle status (Approve, Reject, Suspend, etc.).
    Only Admins can update a vehicle's status.
    """
    return await FleetService.update_vehicle_status(db, vehicle_id, status_in)
