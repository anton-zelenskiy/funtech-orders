import inspect
from functools import wraps
from typing import Any, Callable

import structlog
from aiocache import Cache
from aiocache.backends.redis import RedisCache
from aiocache.serializers import JsonSerializer
from pydantic import BaseModel

from app.core.config import settings

DEFAULT_TTL = 300

_cache: Cache | None = None

logger = structlog.get_logger(__name__)


def _parse_redis_url(url: str) -> dict:
    from urllib.parse import urlparse

    parsed = urlparse(url)
    return {
        "endpoint": parsed.hostname or "localhost",
        "port": parsed.port or 6379,
        "db": int(parsed.path.lstrip("/")) if parsed.path else 0,
        "password": parsed.password,
    }


def get_cache() -> Cache:
    global _cache
    if _cache is None:
        params = _parse_redis_url(settings.redis_url)
        _cache = Cache(
            RedisCache,
            endpoint=params["endpoint"],
            port=params["port"],
            db=params["db"],
            password=params.get("password"),
            ttl=DEFAULT_TTL,
            serializer=JsonSerializer(),
        )
    return _cache


async def invalidate_cache(cache_key: str) -> None:
    cache = get_cache()
    try:
        await cache.delete(cache_key)
        logger.info('cache invalidated', cache_key=cache_key)
    except Exception:
        logger.error('error invalidating cache', cache_key=cache_key)   


def cached_entity(
    key_prefix: str,
    key_param_name: str | Callable[..., str | int] = "id",
    ttl: int = DEFAULT_TTL,
    response_model: type[BaseModel] | None = None,
):
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())
        key_param_index = param_names.index(key_param_name) if key_param_name in param_names else None

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache = get_cache()

            if callable(key_param_name):
                cache_key_value = key_param_name(*args, **kwargs)
            else:
                cache_key_value = kwargs.get(key_param_name)
                if cache_key_value is None and key_param_index is not None and key_param_index < len(args):
                    cache_key_value = args[key_param_index]

            if cache_key_value is None:
                return await func(*args, **kwargs)

            cache_key = f"{key_prefix}{cache_key_value}"

            try:
                cached_data = await cache.get(cache_key)
                if cached_data is not None:
                    if response_model:
                        logger.info('cache hit', cache_key=cache_key)
                        return response_model.model_validate(cached_data)
                    return cached_data
            except Exception:
                logger.error('error getting cached data', cache_key=cache_key)

            logger.info('cache miss', cache_key=cache_key)

            result = await func(*args, **kwargs)

            if result is not None:
                try:
                    if isinstance(result, BaseModel):
                        data_to_cache = result.model_dump(mode="json")
                    else:
                        data_to_cache = result
                    await cache.set(cache_key, data_to_cache, ttl=ttl)
                except Exception:
                    logger.error('error setting cached data', cache_key=cache_key)

            return result

        return wrapper

    return decorator
