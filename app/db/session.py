"""Database session management with optimized connection pooling."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, QueuePool

from app.config import settings

# Use asyncpg for PostgreSQL async operations (faster than psycopg2)
# Convert postgresql:// to postgresql+asyncpg://
database_url_async = settings.database_url.replace(
    "postgresql://", "postgresql+asyncpg://", 1
)

# Optimized engine configuration for high performance
engine = create_async_engine(
    database_url_async,
    # Connection pool optimization
    poolclass=QueuePool,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout,
    pool_recycle=settings.database_pool_recycle,
    pool_pre_ping=True,  # Verify connections before using
    # Performance optimizations
    echo=settings.debug,  # Log SQL queries only in debug mode
    future=True,
    # Connection optimization
    connect_args={
        "server_settings": {
            "application_name": settings.app_name,
            "jit": "off",  # Disable JIT for faster query planning on small queries
        },
        "command_timeout": 30,
    },
    # Reduce overhead
    execution_options={
        "isolation_level": "AUTOCOMMIT",  # Use autocommit for read operations
    },
)

# Session factory with optimized settings
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit (performance)
    autoflush=False,  # Manual flush control (performance)
    autocommit=False,
)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session with automatic cleanup."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Base class for models
Base = declarative_base()
