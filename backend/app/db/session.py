"""
PostgreSQL Database Session & Connection Lifecycle Management.
Utilizes SQLAlchemy 2.x async engine with psycopg 3 driver.
"""

import sys
import asyncio

if sys.platform == "win32":
    try:
        if not isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsSelectorEventLoopPolicy):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from typing import AsyncGenerator, Dict, Any, Optional
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)
from sqlalchemy import text

try:
    from backend.app.core.config import settings
    from backend.app.core.logging import logger
except ImportError:
    from app.core.config import settings
    from app.core.logging import logger


_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.async_database_url,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_timeout=settings.DATABASE_POOL_TIMEOUT,
            pool_pre_ping=True,
            echo=False,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding an async database session per request."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_database_health() -> Dict[str, Any]:
    """
    Diagnostic health check verifying PostgreSQL connectivity and pgvector availability.
    Strictly redacts credentials and database connection strings.
    """
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            # 1. Connectivity check
            await conn.execute(text("SELECT 1"))
            
            # 2. Check pgvector extension
            res = await conn.execute(
                text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            )
            has_vector = res.scalar() is not None

            return {
                "connected": True,
                "vector_extension": has_vector,
                "status": "healthy" if has_vector else "degraded",
            }
    except Exception as e:
        logger.warning(f"Database health check failed: {type(e).__name__}")
        return {
            "connected": False,
            "vector_extension": False,
            "status": "unavailable",
            "error_type": type(e).__name__,
        }


async def close_database() -> None:
    """Disposes engine connection pool during application shutdown."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("PostgreSQL database connection pool disposed.")
