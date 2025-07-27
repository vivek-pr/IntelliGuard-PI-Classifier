import asyncio
import pytest

from app.db import create_engine, get_sessionmaker, init_db
from app import models

@pytest.mark.asyncio
async def test_crud_cycle():
    engine = create_engine("sqlite+aiosqlite:///:memory:")
    SessionLocal = get_sessionmaker(engine)
    await init_db(engine)

    async with SessionLocal() as session:
        user = models.User(username="u1", hashed_password="x")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        job = models.ClassificationJob(user_id=user.id)
        session.add(job)
        await session.commit()
        await session.refresh(job)

        result = models.ClassificationResult(job_id=job.id, text="t", label="PI", score=0.9)
        session.add(result)
        await session.commit()
        await session.refresh(result)

    from sqlalchemy import select, func

    async with SessionLocal() as session:
        user_count = await session.scalar(select(func.count()).select_from(models.User))
        assert user_count == 1
        result_count = await session.scalar(select(func.count()).select_from(models.ClassificationResult))
        assert result_count == 1
