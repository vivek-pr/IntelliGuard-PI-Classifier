import pytest
import pytest
from httpx import AsyncClient, ASGITransport
import fakeredis
from app.main import app
from app import cache
from app.auth import create_access_token


@pytest.fixture(autouse=True)
def _patch_redis(monkeypatch):
    r = fakeredis.aioredis.FakeRedis()
    monkeypatch.setattr(cache, "redis_client", r)
    yield

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_login_and_models():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/v1/auth/login", data={"username": "user@example.com", "password": "password"})
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        resp2 = await ac.get("/api/v1/models", headers=headers)
        assert resp2.status_code == 200
        assert resp2.json() == ["hf-internal-testing/tiny-bert-for-token-classification"]


@pytest.mark.asyncio
async def test_classify_text_api_key():
    token = create_access_token({"sub": "user@example.com"})
    headers = {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/v1/classify/text", json={"text": "Email me at user@example.com"}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data[0]["pii_type"] == "EMAIL"


@pytest.mark.asyncio
async def test_classify_batch_rate_limit():
    token = create_access_token({"sub": "user@example.com"})
    headers = {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = [{"text": "call 123-456-7890"}, {"text": "visit https://example.com"}]
        resp = await ac.post("/api/v1/classify/batch", json=payload, headers=headers)
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) == 2
        assert results[0][0]["pii_type"] == "PHONE"
        assert results[1][0]["pii_type"] == "URL"
