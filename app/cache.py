import hashlib
import json
from typing import Any

import redis.asyncio as redis

from .config import settings

pool = redis.ConnectionPool.from_url(
    settings.redis_url,
    max_connections=settings.redis_max_connections,
    socket_timeout=settings.redis_timeout,
    decode_responses=True,
)
redis_client = redis.Redis(connection_pool=pool)

async def cache_get(key: str) -> Any:
    val = await redis_client.get(key)
    if val is None:
        return None
    return json.loads(val)

async def cache_set(key: str, value: Any, ttl: int | None = None) -> None:
    val = json.dumps(value)
    await redis_client.set(key, val, ex=ttl)

async def cache_delete(key: str) -> None:
    await redis_client.delete(key)

def text_key(prefix: str, text: str) -> str:
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"{prefix}:{h}"
