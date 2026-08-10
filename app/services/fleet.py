from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.vehicle import Vehicle, VehicleStatus
from app.schemas.fleet import VehicleCreate, VehicleUpdateStatus

class FleetService:
    @staticmethod
    async def create_vehicle(db: AsyncSession, vehicle_in: VehicleCreate) -> Vehicle:
        vehicle = Vehicle(**vehicle_in.model_dump())
        db.add(vehicle)
        await db.commit()
        await db.refresh(vehicle)
        return vehicle

    @staticmethod
    async def get_vehicles(db: AsyncSession, owner_id: Optional[int] = None) -> List[Vehicle]:
        query = select(Vehicle)
        if owner_id:
            query = query.where(Vehicle.owner_id == owner_id)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_vehicle_by_id(db: AsyncSession, vehicle_id: UUID) -> Vehicle:
        vehicle = await db.get(Vehicle, vehicle_id)
        if not vehicle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
        return vehicle

    @staticmethod
    async def update_vehicle_status(db: AsyncSession, vehicle_id: UUID, status_in: VehicleUpdateStatus) -> Vehicle:
        vehicle = await FleetService.get_vehicle_by_id(db, vehicle_id)
        vehicle.status = status_in.status
        await db.commit()
        await db.refresh(vehicle)
        return vehicle
