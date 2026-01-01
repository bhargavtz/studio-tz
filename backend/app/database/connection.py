"""
NCD INAI - Database Connection Management
"""

from typing import AsyncGenerator, Optional
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import declarative_base
from app.config import settings

logger = logging.getLogger(__name__)

# Base class for models
Base = declarative_base()

# Engine and session factory (initialized conditionally)
engine: Optional[AsyncEngine] = None
AsyncSessionLocal: Optional[async_sessionmaker] = None


def get_async_database_url() -> str:
    """
    Convert database URL to use asyncpg driver.
    Neon provides URLs like: postgresql://user:pass@host/db?sslmode=require
    We need: postgresql+asyncpg://user:pass@host/db?ssl=require
    
    Note: asyncpg uses 'ssl' parameter instead of 'sslmode'
    """
    url = settings.database_url
    if not url:
        return ""
    
    # Convert postgresql:// to postgresql+asyncpg://
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif not url.startswith("postgresql+asyncpg://"):
        # If it's something else like postgresql+psycopg2://, convert it
        if "://" in url:
            protocol_end = url.index("://")
            url = "postgresql+asyncpg://" + url[protocol_end + 3:]
    
    # Convert sslmode parameter to ssl for asyncpg
    # asyncpg uses 'ssl=require' instead of 'sslmode=require'
    url = url.replace("sslmode=require", "ssl=require")
    url = url.replace("sslmode=verify-full", "ssl=require")
    url = url.replace("sslmode=prefer", "ssl=prefer")
    
    return url


def init_engine():
    """Initialize the database engine if database is enabled."""
    global engine, AsyncSessionLocal
    
    if not settings.use_database or not settings.database_url:
        logger.warning("Database not configured (USE_DATABASE=false or DATABASE_URL empty)")
        return
    
    async_url = get_async_database_url()
    
    if not async_url:
        logger.warning("Invalid database URL")
        return
    
    # Create async engine
    engine = create_async_engine(
        async_url,
        echo=settings.debug,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_pre_ping=True,  # Verify connections before using
    )
    
    # Create session factory
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    logger.info("Database engine initialized")


# Initialize on module load (only if database is configured)
if settings.use_database and settings.database_url:
    init_engine()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database sessions.
    
    Usage:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    if not AsyncSessionLocal:
        raise RuntimeError(
            "Database not configured. Set USE_DATABASE=true and DATABASE_URL in .env"
        )
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database - create tables if they don't exist.
    This is a utility function for development.
    In production, use migrations (Alembic).
    """
    if not engine:
        logger.warning("Cannot init_db: engine not configured")
        return
    
    # Import models first to register them with Base
    from app.database import models  # noqa: F401
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections."""
    if engine:
        await engine.dispose()

