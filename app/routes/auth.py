from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.config import settings
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import TokenResponse, LoginCredentials, RefreshTokenRequest
from app.services.user import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await UserService.get_by_email_or_phone(db, user_in.mobile_number)
    if not existing_user and user_in.email:
        existing_user = await UserService.get_by_email_or_phone(db, user_in.email)
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email or mobile number already exists."
        )
    
    return await UserService.create(db, user_in)

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginCredentials, db: AsyncSession = Depends(get_db)):
    user = await UserService.get_by_email_or_phone(db, credentials.username)
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    if user.status.value != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive or suspended"
        )
        
    access_token = create_access_token(subject=user.user_id)
    refresh_token = create_refresh_token(subject=user.user_id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_data: RefreshTokenRequest):
    try:
        payload = jwt.decode(refresh_data.refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id_str: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if not user_id_str or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
        
    access_token = create_access_token(subject=user_id_str)
    refresh_token = create_refresh_token(subject=user_id_str)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
