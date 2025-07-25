"""
FIA v3.0 - Database Configuration
PostgreSQL connection setup with SQLAlchemy
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.infrastructure.settings import settings


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL queries in debug mode
    future=True,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_database_session() -> AsyncSession:
    """
    Dependency to get database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_database():
    """
    Initialize database - create all tables
    """
    async with engine.begin() as conn:
        # Import all models to register them with Base.metadata
        from app.domain.entities import (
            Trainer, Training, TrainingSession, LearnerSession, 
            Slide, ChatMessage, ApiLog
        )
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)