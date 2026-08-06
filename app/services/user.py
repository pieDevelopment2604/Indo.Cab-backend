from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
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
