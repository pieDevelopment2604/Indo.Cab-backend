from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, normalize_phone_number

class UserService:
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(
            select(User).where(User.user_id == user_id, User.is_deleted == False)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email_or_phone(db: AsyncSession, username: str) -> User | None:
        normalized_username = normalize_phone_number(username) if username and "@" not in username else username
        result = await db.execute(
            select(User).where(
                or_(
                    User.email == username, 
                    User.mobile_number == username,
                    User.mobile_number == normalized_username
                ),
                User.is_deleted == False
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, user_in: UserCreate) -> User:
        hashed_password = get_password_hash(user_in.password)
        normalized_mobile = normalize_phone_number(user_in.mobile_number)
        db_user = User(
            email=user_in.email,
            mobile_number=normalized_mobile,
            password_hash=hashed_password,
            role=user_in.role,
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            profile_image_url=user_in.profile_image_url,
            company_name=user_in.company_name,
            gst_number=user_in.gst_number,
            pan_number=user_in.pan_number,
            address=user_in.address,
            operating_cities=user_in.operating_cities,
            license_number=user_in.license_number
        )
        db.add(db_user)
        await db.flush()
        return db_user

    @staticmethod
    async def update_password(db: AsyncSession, user: User, new_password: str) -> User:
        user.password_hash = get_password_hash(new_password)
        db.add(user)
        await db.flush()
        return user

    @staticmethod
    async def update_status(db: AsyncSession, user: User, status: UserStatus) -> User:
        user.status = status
        db.add(user)
        await db.flush()
        return user

    @staticmethod
    async def list_vendors(
        db: AsyncSession, 
        status: UserStatus | None = None,
        search: str | None = None,
        skip: int = 0, 
        limit: int = 100
    ) -> list[User]:
        stmt = select(User).where(User.role == UserRole.VENDOR, User.is_deleted == False)
        
        if status:
            stmt = stmt.where(User.status == status)
            
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    User.company_name.ilike(search_pattern),
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    User.mobile_number.ilike(search_pattern)
                )
            )
            
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def list_drivers(
        db: AsyncSession, 
        vendor_id: int | None = None,
        status: UserStatus | None = None,
        search: str | None = None,
        skip: int = 0, 
        limit: int = 100
    ) -> list[User]:
        stmt = select(User).where(User.role == UserRole.DRIVER, User.is_deleted == False)
        
        if status:
            stmt = stmt.where(User.status == status)

        if vendor_id:
            # Match drivers associated with a specific vendor
            stmt = stmt.where(User.created_by == vendor_id)
            
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern),
                    User.license_number.ilike(search_pattern),
                    User.mobile_number.ilike(search_pattern)
                )
            )
            
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())
