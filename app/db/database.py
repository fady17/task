# app/database.py

from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

from .config import settings


engine = create_async_engine(settings.DATABASE_URL, echo=True)

SessionLocal = async_sessionmaker(
    autocommit=False,     
    autoflush=False,       
    bind=engine,            
    class_=AsyncSession   
)


Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    A dependency that provides a database session for a single API request.
    The type hint now correctly identifies this as an AsyncGenerator that yields
    AsyncSession objects.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()