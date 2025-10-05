from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os
from typing import AsyncGenerator
from dotenv import load_dotenv

load_dotenv()

class Base(DeclarativeBase):
    pass

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./jamanager.db")

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    
    Yields:
        AsyncSession: Database session for dependency injection
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def get_database_url() -> str:
    """
    Get the database URL for direct connections.
    
    Returns:
        str: Database connection URL
    """
    return DATABASE_URL

async def init_database() -> None:
    """
    Initialize database tables.
    
    Creates all database tables defined in the Base metadata.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)