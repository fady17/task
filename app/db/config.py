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
# from pydantic import BaseModel, Field, AliasChoices
# from pydantic_settings import BaseSettings, SettingsConfigDict

# class Settings(BaseSettings):
#     POSTGRES_USER: str = Field(..., validation_alias=AliasChoices("POSTGRES_USER"))
#     POSTGRES_PASSWORD: str = Field(..., validation_alias=AliasChoices("POSTGRES_PASSWORD"))
#     POSTGRES_DB: str = Field(..., validation_alias=AliasChoices("POSTGRES_DB"))
#     POSTGRES_HOST: str = Field("localhost", validation_alias=AliasChoices("POSTGRES_HOST"))
#     POSTGRES_PORT: str = Field("5432", validation_alias=AliasChoices("POSTGRES_PORT"))

#     @property
#     def DATABASE_URL(self) -> str:
#         """Async database URL for the application"""
#         return (
#             f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
#             f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
#         )
    
#     @property
#     def DATABASE_URL_SYNC(self) -> str:
#         """Sync database URL for Alembic migrations"""
#         return (
#             f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
#             f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
#         )

#     model_config = SettingsConfigDict(env_file=".env")

# settings = Settings() # type: ignore