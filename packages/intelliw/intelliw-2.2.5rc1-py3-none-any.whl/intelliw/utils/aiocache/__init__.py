import logging
from typing import Any, Dict, Type

from .backends.memory import SimpleMemoryCache
from .base import BaseCache

__version__ = "1.0.0a0"

logger = logging.getLogger(__name__)

AIOCACHE_CACHES: Dict[str, Type[BaseCache[Any]]] = {SimpleMemoryCache.NAME: SimpleMemoryCache}

try:
    import redis
    from intelliw.utils.aiocache.backends.redis import RedisCache

    AIOCACHE_CACHES[RedisCache.NAME] = RedisCache
except (ImportError, ModuleNotFoundError):
    logger.debug("redis not installed, RedisCache unavailable")
else:
    del redis

try:
    import aiomcache
    from intelliw.utils.aiocache.backends.memcached import MemcachedCache
    AIOCACHE_CACHES[MemcachedCache.NAME] = MemcachedCache
except (ImportError, ModuleNotFoundError):
    logger.debug("aiomcache not installed, Memcached unavailable")
else:
    del aiomcache

from .decorators import cached, cached_stampede, multi_cached  # noqa: E402,I202
from .factory import Cache, caches  # noqa: E402
from . import common

__all__ = (
    "caches",
    "Cache",
    "cached",
    "cached_stampede",
    "multi_cached",
    "common",
    *(c.__name__ for c in AIOCACHE_CACHES.values()),
)
