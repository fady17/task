# app/db/config.py - Alternative approach

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    # Only define the fields you actually use in your app
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # FIXED: This allows extra fields in .env without errors
    )
    
    @property
    def DATABASE_URL(self) -> str:
        """Build the async database URL"""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property 
    def DATABASE_URL_SYNC(self) -> str:
        """Build the sync database URL for Alembic"""
        return f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

settings = Settings() # type: ignore
