import redis.asyncio as aioredis
from app.core.config import settings

REFRESH_TOKEN_TTL_SECONDS = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

def get_redis_client():
    return aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
        decode_responses=True
    )

class RedisService:
    # -------------------------------------------------------------------------
    # OTP Methods
    # -------------------------------------------------------------------------

    @staticmethod
    async def set_otp(mobile_number: str, otp_code: str, ttl_seconds: int = 300):
        key = f"otp:{mobile_number}"
        client = get_redis_client()
        try:
            await client.set(key, otp_code, ex=ttl_seconds)
        finally:
            await client.aclose()

    @staticmethod
    async def get_otp(mobile_number: str) -> str | None:
        key = f"otp:{mobile_number}"
        client = get_redis_client()
        try:
            return await client.get(key)
        finally:
            await client.aclose()

    @staticmethod
    async def delete_otp(mobile_number: str):
        key = f"otp:{mobile_number}"
        client = get_redis_client()
        try:
            await client.delete(key)
        finally:
            await client.aclose()

    # -------------------------------------------------------------------------
    # Refresh Token Methods
    # Stores `jti` (JWT ID) → user_id mapping so tokens can be revoked.
    # -------------------------------------------------------------------------

    @staticmethod
    async def store_refresh_token(jti: str, user_id: int, ttl_seconds: int = REFRESH_TOKEN_TTL_SECONDS):
        """Persist a refresh token's JTI so it can be validated and revoked."""
        key = f"refresh_token:{jti}"
        client = get_redis_client()
        try:
            await client.set(key, str(user_id), ex=ttl_seconds)
        finally:
            await client.aclose()

    @staticmethod
    async def get_refresh_token_user_id(jti: str) -> str | None:
        """Return the user_id tied to this JTI, or None if revoked/expired."""
        key = f"refresh_token:{jti}"
        client = get_redis_client()
        try:
            return await client.get(key)
        finally:
            await client.aclose()

    @staticmethod
    async def revoke_refresh_token(jti: str):
        """Invalidate a refresh token immediately (logout / token rotation)."""
        key = f"refresh_token:{jti}"
        client = get_redis_client()
        try:
            await client.delete(key)
        finally:
            await client.aclose()
