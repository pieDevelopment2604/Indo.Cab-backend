import random
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.config import settings
from app.core.security import verify_password, create_access_token, create_refresh_token, normalize_phone_number
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
from app.services.recaptcha import RecaptchaService
from app.routes.dependencies import get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

async def _send_otp_internal(mobile_number: str) -> dict:
    """Generate a 6-digit OTP, cache it in Redis, and dispatch via MSG91."""
    normalized_mobile = normalize_phone_number(mobile_number)
    otp_code = str(random.randint(100000, 999999))
    await RedisService.set_otp(normalized_mobile, otp_code, ttl_seconds=300)

    dev_otp = otp_code
    auth_key = settings.MSG91_AUTH_KEY
    template_id = settings.MSG91_TEMPLATE_ID

    if auth_key and not auth_key.startswith("your_") and template_id:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    "https://api.msg91.com/api/v5/otp",
                    headers={"authkey": auth_key},
                    json={
                        "template_id": template_id,
                        "mobile": normalized_mobile,
                        "otp": otp_code
                    }
                )
            dev_otp = None  # Don't expose OTP in production response
        except Exception:
            # MSG91 is unavailable; OTP stays in Redis, surfaced in dev_otp
            dev_otp = otp_code

    return {
        "message": "OTP sent successfully",
        "mobile_number": normalized_mobile,
        "dev_otp": dev_otp
    }


async def _build_token_response(user: User) -> dict:
    """Issue a fresh access + refresh token pair and persist the refresh JTI."""
    access_token = create_access_token(subject=user.user_id)
    refresh_token, jti = create_refresh_token(subject=user.user_id)
    await RedisService.store_refresh_token(jti=jti, user_id=user.user_id)
    
    username = user.email if user.email else user.mobile_number
    
    return {
        "token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user.role.value,
        "username": username,
        "name": f"{user.first_name} {user.last_name}"
    }


# ---------------------------------------------------------------------------
# Auth Endpoints
# ---------------------------------------------------------------------------

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginCredentials, db: AsyncSession = Depends(get_db)):
    """
    Authenticate with email/mobile + password.
    Requires a valid Google reCAPTCHA v3 token.
    """
    await RecaptchaService.verify_token(credentials.recaptcha_token, expected_action="login")

    user = await UserService.get_by_email_or_phone(db, credentials.username)
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if user.status.value != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive or suspended",
        )

    return await _build_token_response(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """
    Exchange a valid refresh token for a new access + refresh token pair.
    The old refresh token is revoked on use (token rotation).
    """
    try:
        payload = jwt.decode(refresh_data.refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id_str: str = payload.get("sub")
        token_type: str = payload.get("type")
        jti: str = payload.get("jti")

        if not user_id_str or token_type != "refresh" or not jti:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Validate the JTI exists in Redis (not revoked / expired)
    stored_user_id = await RedisService.get_refresh_token_user_id(jti)
    if not stored_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked or expired. Please log in again.",
        )

    # Revoke the old token before issuing a new pair (rotation)
    await RedisService.revoke_refresh_token(jti)

    user = await UserService.get_by_id(db, int(user_id_str))
    if not user or user.status.value != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive or suspended",
        )

    return await _build_token_response(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    refresh_data: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Revoke the supplied refresh token.
    Access tokens expire naturally; the client should discard them locally.
    """
    try:
        payload = jwt.decode(refresh_data.refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        jti: str = payload.get("jti")
        if jti:
            await RedisService.revoke_refresh_token(jti)
    except JWTError:
        # Silently ignore malformed token — logout should never fail visibly
        pass


@router.post("/send-otp", response_model=OTPResponse)
async def send_otp(otp_in: SendOTPRequest):
    """
    Send a 6-digit OTP to the provided mobile number.
    Requires a valid Google reCAPTCHA v3 token.
    """
    await RecaptchaService.verify_token(otp_in.recaptcha_token, expected_action="send_otp")
    return await _send_otp_internal(otp_in.mobile_number)


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(verify_in: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    """
    Verify an OTP and return a token pair for the matching user.
    The OTP is deleted from Redis on successful verification (single-use).
    """
    normalized_mobile = normalize_phone_number(verify_in.mobile_number)
    stored_otp = await RedisService.get_otp(normalized_mobile)
    if not stored_otp or stored_otp != verify_in.otp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    user = await UserService.get_by_email_or_phone(db, normalized_mobile)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found for this mobile number.",
        )

    if user.status.value != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive or suspended",
        )

    await RedisService.delete_otp(normalized_mobile)
    return await _build_token_response(user)


@router.post("/forgot-password", response_model=OTPResponse)
async def forgot_password(otp_in: SendOTPRequest, db: AsyncSession = Depends(get_db)):
    """
    Initiate a password reset by sending an OTP to the registered mobile number.
    Requires a valid Google reCAPTCHA v3 token.
    """
    await RecaptchaService.verify_token(otp_in.recaptcha_token, expected_action="forgot_password")
    normalized_mobile = normalize_phone_number(otp_in.mobile_number)
    user = await UserService.get_by_email_or_phone(db, normalized_mobile)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this mobile number.",
        )

    return await _send_otp_internal(normalized_mobile)


@router.post("/reset-password", response_model=dict)
async def reset_password(reset_in: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """
    Reset password using a valid OTP.
    The OTP is consumed on successful reset (single-use).
    """
    normalized_mobile = normalize_phone_number(reset_in.mobile_number)
    stored_otp = await RedisService.get_otp(normalized_mobile)
    if not stored_otp or stored_otp != reset_in.otp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    user = await UserService.get_by_email_or_phone(db, normalized_mobile)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found.",
        )

    await UserService.update_password(db, user, reset_in.new_password)
    await RedisService.delete_otp(normalized_mobile)

    return {"message": "Password updated successfully."}
