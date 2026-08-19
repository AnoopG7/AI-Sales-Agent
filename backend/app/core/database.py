"""
Async database engine and session factory.

Uses SQLAlchemy async with asyncpg driver.
Initialized on FastAPI lifespan startup.
"""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

_engine: AsyncEngine | None = None
async_session_factory: async_sessionmaker[AsyncSession] | None = None


async def init_db() -> None:
    """Create engine and session factory. Call once on app startup."""
    global _engine, async_session_factory
    settings = get_settings()
    _engine = create_async_engine(
        settings.DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        echo=settings.is_development,
    )
    async_session_factory = async_sessionmaker(
        _engine, expire_on_commit=False, class_=AsyncSession
    )


async def close_db() -> None:
    """Dispose of the engine. Call once on app shutdown."""
    global _engine, async_session_factory
    if _engine:
        await _engine.dispose()
    _engine = None
    async_session_factory = None


def get_session() -> AsyncSession:
    """Get a new session from the factory. Used by FastAPI Depends."""
    if async_session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return async_session_factory()
