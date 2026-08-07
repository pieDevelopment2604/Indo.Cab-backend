from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User, UserRole, UserStatus
from app.routes.dependencies import RoleChecker
from app.schemas.user import VendorCreate, DriverCreate, UserResponse, UserCreate, UserStatusUpdate
from app.schemas.client import ClientCreate, ClientResponse
from app.services.user import UserService
from app.services.client import ClientService
from app.core.security import normalize_phone_number

router = APIRouter(prefix="/admin", tags=["Admin Operations"])

@router.post("/vendors", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    vendor_in: VendorCreate,
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    normalized_mobile = normalize_phone_number(vendor_in.mobile_number)
    existing_user = await UserService.get_by_email_or_phone(db, normalized_mobile)
    if not existing_user and vendor_in.email:
        existing_user = await UserService.get_by_email_or_phone(db, vendor_in.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email or mobile number already exists."
        )

    user_create = UserCreate(
        email=vendor_in.email,
        mobile_number=normalized_mobile,
        first_name=vendor_in.first_name,
        last_name=vendor_in.last_name,
        password=vendor_in.password,
        role=UserRole.VENDOR,
        profile_image_url=vendor_in.profile_image_url,
        company_name=vendor_in.company_name,
        gst_number=vendor_in.gst_number,
        pan_number=vendor_in.pan_number,
        address=vendor_in.address,
        operating_cities=vendor_in.operating_cities
    )
    return await UserService.create(db, user_create)

@router.get("/vendors", response_model=List[UserResponse])
async def list_vendors(
    status: Optional[UserStatus] = Query(None, description="Filter vendors by status"),
    search: Optional[str] = Query(None, description="Search vendors by company name, contact name, or phone"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    return await UserService.list_vendors(db, status=status, search=search, skip=skip, limit=limit)

@router.get("/vendors/{vendor_id}", response_model=UserResponse)
async def get_vendor(
    vendor_id: int,
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    vendor = await UserService.get_by_id(db, vendor_id)
    if not vendor or vendor.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    return vendor

@router.post("/drivers", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_driver(
    driver_in: DriverCreate,
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    vendor = await UserService.get_by_id(db, driver_in.vendor_id)
    if not vendor or vendor.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specified Vendor ID does not exist."
        )

    normalized_mobile = normalize_phone_number(driver_in.mobile_number)
    existing_user = await UserService.get_by_email_or_phone(db, normalized_mobile)
    if not existing_user and driver_in.email:
        existing_user = await UserService.get_by_email_or_phone(db, driver_in.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email or mobile number already exists."
        )

    user_create = UserCreate(
        email=driver_in.email,
        mobile_number=normalized_mobile,
        first_name=driver_in.first_name,
        last_name=driver_in.last_name,
        password=driver_in.password,
        role=UserRole.DRIVER,
        profile_image_url=driver_in.profile_image_url,
        license_number=driver_in.license_number,
        company_name=vendor.company_name
    )
    db_driver = await UserService.create(db, user_create)
    db_driver.created_by = vendor.user_id
    db.add(db_driver)
    await db.flush()
    return db_driver

@router.get("/drivers", response_model=List[UserResponse])
async def list_drivers(
    vendor_id: Optional[int] = Query(None, description="Filter drivers by Vendor ID"),
    status: Optional[UserStatus] = Query(None, description="Filter drivers by status"),
    search: Optional[str] = Query(None, description="Search drivers by name, phone, or license"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    return await UserService.list_drivers(db, vendor_id=vendor_id, status=status, search=search, skip=skip, limit=limit)

@router.get("/drivers/{driver_id}", response_model=UserResponse)
async def get_driver(
    driver_id: int,
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    driver = await UserService.get_by_id(db, driver_id)
    if not driver or driver.role != UserRole.DRIVER:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    return driver

@router.patch("/users/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    user_id: int,
    status_update: UserStatusUpdate,
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found"
        )
    return await UserService.update_status(db, user, status_update.status)

@router.post("/clients", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def add_client(
    client_in: ClientCreate,
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    existing_client = await ClientService.get_by_email_or_phone(db, client_in.mobile_number, client_in.email)
    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A client with this email or mobile number already exists."
        )
    return await ClientService.create(db, client_in)

@router.get("/clients", response_model=List[ClientResponse])
async def list_clients(
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    return await ClientService.list_clients(db, skip=skip, limit=limit)
