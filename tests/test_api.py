import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.auth import create_access_token

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
        assert resp2.json() == ["pi-base-model"]


@pytest.mark.asyncio
async def test_classify_text_api_key():
    token = create_access_token({"sub": "user@example.com"})
    headers = {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/v1/classify/text", json={"text": "hello"}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["label"] == "PI"


@pytest.mark.asyncio
async def test_classify_batch_rate_limit():
    token = create_access_token({"sub": "user@example.com"})
    headers = {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = [{"text": "a"}, {"text": "b"}]
        resp = await ac.post("/api/v1/classify/batch", json=payload, headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2
