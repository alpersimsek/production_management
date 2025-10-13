from pydantic import BaseModel
import os

class Settings(BaseModel):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change_me")
    JWT_EXPIRES_MIN: int = int(os.getenv("JWT_EXPIRES_MIN", "60"))
    REFRESH_EXPIRES_MIN: int = int(os.getenv("REFRESH_EXPIRES_MIN", "1440"))
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

settings = Settings()

