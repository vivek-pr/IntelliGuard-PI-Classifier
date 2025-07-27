import pytest
import fakeredis

from app import cache
from app.main import fake_classify

@pytest.mark.asyncio
async def test_cache_set_get(monkeypatch):
    r = fakeredis.aioredis.FakeRedis()
    monkeypatch.setattr(cache, "redis_client", r)
    key = cache.text_key("t", "hello")
    await cache.cache_set(key, {"x": 1}, ttl=10)
    val = await cache.cache_get(key)
    assert val == {"x": 1}
    ttl = await r.ttl(key)
    assert ttl > 0

@pytest.mark.asyncio
async def test_fake_classify_uses_cache(monkeypatch):
    r = fakeredis.aioredis.FakeRedis()
    monkeypatch.setattr(cache, "redis_client", r)
    await r.flushdb()
    res1 = await fake_classify("hi")
    assert await r.exists(cache.text_key("classify", "hi")) == 1
    res2 = await fake_classify("hi")
    assert res1 == res2

