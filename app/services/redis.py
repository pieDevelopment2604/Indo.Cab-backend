import redis.asyncio as aioredis
from app.core.config import settings

def get_redis_client():
    return aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
        decode_responses=True
    )

class RedisService:
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
