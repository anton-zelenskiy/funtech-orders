from functools import wraps
from uuid import UUID

from aiocache import Cache
from aiocache.serializers import JsonSerializer

from app.core.config import settings

ORDER_CACHE_TTL = 300
_ORDER_KEY_PREFIX = "order:"


def _parse_redis_url(url: str) -> dict:
    from urllib.parse import urlparse

    parsed = urlparse(url)
    return {
        "endpoint": parsed.hostname or "localhost",
        "port": parsed.port or 6379,
        "db": int(parsed.path.lstrip("/")) if parsed.path else 0,
        "password": parsed.password,
    }


def _order_cache_key(order_id: UUID) -> str:
    return f"{_ORDER_KEY_PREFIX}{order_id}"


def _get_cache() -> Cache:
    params = _parse_redis_url(settings.redis_url)
    return Cache(
        "redis",
        endpoint=params["endpoint"],
        port=params["port"],
        db=params["db"],
        password=params.get("password"),
        ttl=ORDER_CACHE_TTL,
        serializer=JsonSerializer(),
    )


_cache: Cache | None = None


def get_order_cache() -> Cache:
    global _cache
    if _cache is None:
        _cache = _get_cache()
    return _cache


async def get_order_cached(order_id: UUID) -> dict | None:
    cache = get_order_cache()
    key = _order_cache_key(order_id)
    try:
        return await cache.get(key)
    except Exception:
        return None


async def set_order_cached(order_id: UUID, data: dict, ttl: int = ORDER_CACHE_TTL) -> None:
    cache = get_order_cache()
    key = _order_cache_key(order_id)
    try:
        await cache.set(key, data, ttl=ttl)
    except Exception:
        pass


async def invalidate_order_cached(order_id: UUID) -> None:
    cache = get_order_cache()
    key = _order_cache_key(order_id)
    try:
        await cache.delete(key)
    except Exception:
        pass


def cached_order(ttl: int = ORDER_CACHE_TTL):
    def decorator(f):
        @wraps(f)
        async def wrapper(order_id: UUID):
            data = await get_order_cached(order_id)
            if data is not None:
                return data
            data = await f(order_id)
            if data is not None:
                await set_order_cached(order_id, data, ttl=ttl)
            return data

        return wrapper

    return decorator
