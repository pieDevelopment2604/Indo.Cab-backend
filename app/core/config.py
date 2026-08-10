from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Indo.Cab Backend"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str = "supersecretkeychangeinproduction"
    # Access tokens are short-lived; refresh tokens handle session persistence
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7     # 7 days

    # Comma-separated origins for CORS, e.g. "http://localhost:3000,https://admin.indocab.com"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "indocab"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str | None = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info) -> str:
        if isinstance(v, str) and v:
            # Railway and Heroku provide postgresql:// by default, but we need asyncpg
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+asyncpg://", 1)
            if v.startswith("postgresql://"):
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
            return v
        
        data = info.data
        return (
            f"postgresql+asyncpg://{data.get('POSTGRES_USER')}:"
            f"{data.get('POSTGRES_PASSWORD')}@{data.get('POSTGRES_SERVER')}:"
            f"{data.get('POSTGRES_PORT')}/{data.get('POSTGRES_DB')}"
        )

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None

    @field_validator("CELERY_BROKER_URL", mode="before")
    @classmethod
    def assemble_celery_broker(cls, v: str | None, info) -> str:
        if isinstance(v, str) and v:
            return v
        data = info.data
        return f"redis://{data.get('REDIS_HOST')}:{data.get('REDIS_PORT')}/0"

    @field_validator("CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def assemble_celery_backend(cls, v: str | None, info) -> str:
        if isinstance(v, str) and v:
            return v
        data = info.data
        return f"redis://{data.get('REDIS_HOST')}:{data.get('REDIS_PORT')}/0"

    # MSG91 SMS Gateway
    MSG91_AUTH_KEY: str | None = None
    MSG91_SENDER_ID: str = "INDCAB"
    MSG91_TEMPLATE_ID: str | None = None  # Set in .env — required for production OTP

    # MapMyIndia
    MAP_MY_INDIA_CLIENT_ID: str | None = None
    MAP_MY_INDIA_CLIENT_SECRET: str | None = None

    # Google reCAPTCHA v3
    RECAPTCHA_SECRET_KEY: str | None = None
    RECAPTCHA_MIN_SCORE: float = 0.5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
