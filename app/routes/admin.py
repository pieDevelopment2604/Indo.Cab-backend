from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User, UserRole, UserStatus
from app.routes.dependencies import RoleChecker, get_current_user
from app.schemas.user import VendorCreate, DriverCreate, UserResponse, UserCreate, UserStatusUpdate, VendorUpdate, DriverUpdate, UserProfileUpdate
from app.schemas.client import ClientCreate, ClientResponse, ClientUpdate, ClientStatusUpdate
from app.services.user import UserService
from app.services.client import ClientService
from app.core.security import normalize_phone_number

router = APIRouter(prefix="/admin", tags=["Admin Operations"])


# ---------------------------------------------------------------------------
# Vendor Management
# ---------------------------------------------------------------------------

@router.post("/vendors", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    vendor_in: VendorCreate,
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Create and onboard a new vendor. Only accessible by admins."""
    normalized_mobile = normalize_phone_number(vendor_in.mobile_number)
    existing_user = await UserService.get_by_email_or_phone(db, normalized_mobile)
    if not existing_user and vendor_in.email:
        existing_user = await UserService.get_by_email_or_phone(db, vendor_in.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email or mobile number already exists.",
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
        operating_cities=vendor_in.operating_cities,
    )
    return await UserService.create(db, user_create, created_by_id=current_admin.user_id)


@router.get("/vendors", response_model=List[UserResponse])
async def list_vendors(
    status: Optional[UserStatus] = Query(None, description="Filter vendors by status"),
    search: Optional[str] = Query(None, description="Search by company name, contact name, or phone"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    return await UserService.list_vendors(db, status=status, search=search, skip=skip, limit=limit)


@router.get("/vendors/{vendor_id}", response_model=UserResponse)
async def get_vendor(
    vendor_id: int,
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    vendor = await UserService.get_by_id(db, vendor_id)
    if not vendor or vendor.role != UserRole.VENDOR:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    return vendor


# ---------------------------------------------------------------------------
# Driver Management
# ---------------------------------------------------------------------------

@router.post("/drivers", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_driver(
    driver_in: DriverCreate,
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Create and onboard a new driver under a vendor. Only accessible by admins."""
    # Validate the vendor exists
    vendor = await UserService.get_by_id(db, driver_in.vendor_id)
    if not vendor or vendor.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specified Vendor ID does not exist.",
        )

    normalized_mobile = normalize_phone_number(driver_in.mobile_number)
    existing_user = await UserService.get_by_email_or_phone(db, normalized_mobile)
    if not existing_user and driver_in.email:
        existing_user = await UserService.get_by_email_or_phone(db, driver_in.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email or mobile number already exists.",
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
        # Proper vendor association — NOT via created_by
        vendor_id=driver_in.vendor_id,
        # Inherit company_name from vendor for display purposes
        company_name=vendor.company_name,
    )
    # created_by_id = admin's user_id, preserving audit trail integrity
    return await UserService.create(db, user_create, created_by_id=current_admin.user_id)


@router.get("/drivers", response_model=List[UserResponse])
async def list_drivers(
    vendor_id: Optional[int] = Query(None, description="Filter drivers by Vendor ID"),
    status: Optional[UserStatus] = Query(None, description="Filter drivers by status"),
    search: Optional[str] = Query(None, description="Search by name, phone, or license"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    return await UserService.list_drivers(
        db, vendor_id=vendor_id, status=status, search=search, skip=skip, limit=limit
    )


@router.get("/drivers/{driver_id}", response_model=UserResponse)
async def get_driver(
    driver_id: int,
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    driver = await UserService.get_by_id(db, driver_id)
    if not driver or driver.role != UserRole.DRIVER:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
    return driver


# ---------------------------------------------------------------------------
# User Account Status Control
# ---------------------------------------------------------------------------

@router.patch("/users/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    user_id: int,
    status_update: UserStatusUpdate,
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Activate, suspend, or deactivate any user account."""
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User account not found")
    return await UserService.update_status(db, user, status_update.status)


# ---------------------------------------------------------------------------
# Corporate Client Management
# ---------------------------------------------------------------------------

@router.post("/clients", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def add_client(
    client_in: ClientCreate,
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Register a new corporate client (e.g. MakeMyTrip, Savaari, direct B2B)."""
    existing_client = await ClientService.get_by_email_or_phone(db, client_in.mobile_number, client_in.email)
    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A client with this email or mobile number already exists.",
        )
    return await ClientService.create(db, client_in, created_by_id=current_admin.user_id)


@router.get("/clients", response_model=List[ClientResponse])
async def list_clients(
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    return await ClientService.list_clients(db, skip=skip, limit=limit)


# ---------------------------------------------------------------------------
# Profile & Account Management Updates
# ---------------------------------------------------------------------------

@router.put("/vendors/{vendor_id}", response_model=UserResponse)
async def update_vendor(
    vendor_id: int,
    vendor_update: VendorUpdate,
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Update details of an existing vendor. Only accessible by admins."""
    vendor = await UserService.get_by_id(db, vendor_id)
    if not vendor or vendor.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found."
        )
    return await UserService.update_user(db, vendor, vendor_update.model_dump(exclude_unset=True))


@router.put("/drivers/{driver_id}", response_model=UserResponse)
async def update_driver(
    driver_id: int,
    driver_update: DriverUpdate,
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Update details of an existing driver. Only accessible by admins."""
    driver = await UserService.get_by_id(db, driver_id)
    if not driver or driver.role != UserRole.DRIVER:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found."
        )
    
    # If vendor_id is changing, validate that the new vendor exists
    update_dict = driver_update.model_dump(exclude_unset=True)
    if "vendor_id" in update_dict and update_dict["vendor_id"] is not None:
        vendor = await UserService.get_by_id(db, update_dict["vendor_id"])
        if not vendor or vendor.role != UserRole.VENDOR:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY if hasattr(status, 'HTTP_422_UNPROCESSABLE_ENTITY') else status.HTTP_400_BAD_REQUEST,
                detail="New Vendor ID does not exist."
            )
        # Also inherit company_name from vendor for display purposes
        update_dict["company_name"] = vendor.company_name

    return await UserService.update_user(db, driver, update_dict)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update basic profile details for the currently logged-in user (Admin/Vendor/Driver)."""
    return await UserService.update_user(db, current_user, profile_update.model_dump(exclude_unset=True))


@router.delete("/vendors/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vendor(
    vendor_id: int,
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete an existing vendor and all their drivers. Only accessible by admins."""
    vendor = await UserService.get_by_id(db, vendor_id)
    if not vendor or vendor.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found."
        )
    await UserService.delete_user(db, vendor)


@router.delete("/drivers/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_driver(
    driver_id: int,
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete an existing driver. Only accessible by admins."""
    driver = await UserService.get_by_id(db, driver_id)
    if not driver or driver.role != UserRole.DRIVER:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found."
        )
    await UserService.delete_user(db, driver)


# ---------------------------------------------------------------------------
# Corporate Client Management Updates
# ---------------------------------------------------------------------------

@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve details of a corporate client. Only accessible by admins."""
    client = await ClientService.get_by_id(db, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corporate client not found."
        )
    return client


@router.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_update: ClientUpdate,
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Update details of a corporate client. Only accessible by admins."""
    client = await ClientService.get_by_id(db, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corporate client not found."
        )
    return await ClientService.update(db, client, client_update.model_dump(exclude_unset=True))


@router.patch("/clients/{client_id}/status", response_model=ClientResponse)
async def update_client_status(
    client_id: int,
    status_update: ClientStatusUpdate,
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Update status of a corporate client. Only accessible by admins."""
    client = await ClientService.get_by_id(db, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corporate client not found."
        )
    return await ClientService.update_status(db, client, status_update.status)


@router.delete("/clients/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    current_admin: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete an existing corporate client. Only accessible by admins."""
    client = await ClientService.get_by_id(db, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corporate client not found."
        )
    await ClientService.delete(db, client)
