import random
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.config import settings
from app.core.security import verify_password, create_access_token, create_refresh_token, normalize_phone_number
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import (
    TokenResponse, 
    LoginCredentials, 
    RefreshTokenRequest,
    SendOTPRequest,
    VerifyOTPRequest,
    ResetPasswordRequest,
    OTPResponse
)
from app.services.user import UserService
from app.services.redis import RedisService

router = APIRouter(prefix="/auth", tags=["Authentication"])

async def _send_otp_internal(mobile_number: str) -> dict:
    normalized_mobile = normalize_phone_number(mobile_number)
    otp_code = str(random.randint(100000, 999999))
    await RedisService.set_otp(normalized_mobile, otp_code, ttl_seconds=300)
    
    dev_otp = otp_code
    if settings.MSG91_AUTH_KEY and not settings.MSG91_AUTH_KEY.startswith("your_"):
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    "https://api.msg91.com/api/v5/otp",
                    headers={"authkey": settings.MSG91_AUTH_KEY},
                    json={
                        "template_id": "YOUR_TEMPLATE_ID",
                        "mobile": normalized_mobile,
                        "otp": otp_code
                    }
                )
            dev_otp = None
        except Exception:
            dev_otp = otp_code
        
    return {
        "message": "OTP sent successfully",
        "mobile_number": normalized_mobile,
        "dev_otp": dev_otp
    }

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    user_in.mobile_number = normalize_phone_number(user_in.mobile_number)
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

@router.post("/send-otp", response_model=OTPResponse)
async def send_otp(otp_in: SendOTPRequest):
    return await _send_otp_internal(otp_in.mobile_number)

@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(verify_in: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    normalized_mobile = normalize_phone_number(verify_in.mobile_number)
    stored_otp = await RedisService.get_otp(normalized_mobile)
    if not stored_otp or stored_otp != verify_in.otp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
        
    user = await UserService.get_by_email_or_phone(db, normalized_mobile)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found for this mobile number."
        )
        
    if user.status.value != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive or suspended"
        )
        
    await RedisService.delete_otp(normalized_mobile)
    
    access_token = create_access_token(subject=user.user_id)
    refresh_token = create_refresh_token(subject=user.user_id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/forgot-password", response_model=OTPResponse)
async def forgot_password(otp_in: SendOTPRequest, db: AsyncSession = Depends(get_db)):
    normalized_mobile = normalize_phone_number(otp_in.mobile_number)
    user = await UserService.get_by_email_or_phone(db, normalized_mobile)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this mobile number."
        )
        
    return await _send_otp_internal(normalized_mobile)

@router.post("/reset-password", response_model=dict)
async def reset_password(reset_in: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    normalized_mobile = normalize_phone_number(reset_in.mobile_number)
    stored_otp = await RedisService.get_otp(normalized_mobile)
    if not stored_otp or stored_otp != reset_in.otp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
        
    user = await UserService.get_by_email_or_phone(db, normalized_mobile)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found."
        )
        
    await UserService.update_password(db, user, reset_in.new_password)
    await RedisService.delete_otp(normalized_mobile)
    
    return {"message": "Password updated successfully."}
