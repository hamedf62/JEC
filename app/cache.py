"""
Redis Cache Manager for caching analysis results.
Handles optional Redis caching with fallback to in-memory caching.
"""

import json
import logging
from typing import Any, Optional
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching with Redis or in-memory fallback."""

    def __init__(self, redis_client=None, ttl_seconds: int = 3600):
        """
        Initialize cache manager.

        Args:
            redis_client: Redis client instance (optional)
            ttl_seconds: Time-to-live for cache entries in seconds
        """
        self.redis_client = redis_client
        self.ttl_seconds = ttl_seconds
        self.in_memory_cache = {}
        self.using_redis = redis_client is not None

    def get_cache_key(self, prefix: str, **kwargs) -> str:
        """
        Generate a cache key from prefix and parameters.

        Args:
            prefix: Cache key prefix
            **kwargs: Additional parameters to include in key

        Returns:
            Generated cache key
        """
        params_str = json.dumps(kwargs, sort_keys=True, default=str)
        hash_suffix = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"{prefix}:{hash_suffix}"

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            if self.using_redis:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                if key in self.in_memory_cache:
                    entry = self.in_memory_cache[key]
                    if entry["expires"] > datetime.now():
                        return entry["value"]
                    else:
                        del self.in_memory_cache[key]

            return None
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: Any) -> bool:
        """
        Store value in cache.

        Args:
            key: Cache key
            value: Value to cache

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.using_redis:
                self.redis_client.setex(
                    key, self.ttl_seconds, json.dumps(value, default=str)
                )
            else:
                self.in_memory_cache[key] = {
                    "value": value,
                    "expires": datetime.now() + timedelta(seconds=self.ttl_seconds),
                }
            return True
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete cache entry.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.using_redis:
                self.redis_client.delete(key)
            else:
                if key in self.in_memory_cache:
                    del self.in_memory_cache[key]
            return True
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
            return False

    def clear(self) -> bool:
        """
        Clear all cache entries.

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.using_redis:
                self.redis_client.flushdb()
            else:
                self.in_memory_cache.clear()
            return True
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")
            return False

    def get_cache_info(self) -> dict:
        """Get cache information."""
        if self.using_redis:
            try:
                info = self.redis_client.info()
                return {
                    "backend": "Redis",
                    "used_memory": info.get("used_memory_human", "N/A"),
                    "connected_clients": info.get("connected_clients", 0),
                }
            except Exception:
                return {"backend": "Redis", "status": "unavailable"}
        else:
            return {
                "backend": "In-Memory",
                "entries": len(self.in_memory_cache),
                "ttl_seconds": self.ttl_seconds,
            }
