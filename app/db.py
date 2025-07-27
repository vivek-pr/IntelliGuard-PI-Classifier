from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData

from .config import settings

metadata = MetaData()
Base = declarative_base(metadata=metadata)


def create_engine(url: str | None = None):
    url = url or settings.database_url
    kwargs = {"future": True}
    if not url.startswith("sqlite"):
        kwargs.update({"pool_size": settings.db_pool_size, "max_overflow": 0})
    return create_async_engine(url, **kwargs)


def get_sessionmaker(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


async def init_db(engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
