from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://crm_user:crm_pass@postgres:5432/crm_db"
    SYNC_DATABASE_URL: str = "postgresql://crm_user:crm_pass@postgres:5432/crm_db"
    REDIS_URL: str = "redis://redis:6379/0"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    AI_PROVIDER: str = "anthropic"
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    EMAILS_FROM: str = "noreply@example.com"
    ENCRYPTION_KEY: str = "Zg5rX2kL9mPqVwTnYsUaJcHdFeBiOxNv"
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"
    ENVIRONMENT: str = "development"
    SLACK_WEBHOOK_URL: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"

settings = Settings()
