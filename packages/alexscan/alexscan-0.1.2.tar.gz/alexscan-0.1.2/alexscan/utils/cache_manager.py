"""Redis cache manager for domain analysis results."""

import json
import logging
from typing import Any, Dict, Optional

# Check if Redis is available at import time
try:
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis-based cache manager for domain analysis results."""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, ttl: int = 86400):
        """
        Initialize cache manager.

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            ttl: Time to live for cached entries in seconds (default: 1 day)
        """
        self.host = host
        self.port = port
        self.db = db
        self.ttl = ttl
        self.client = None
        self._connected = False

        if REDIS_AVAILABLE:
            self._connect()

    def _connect(self) -> bool:
        """Connect to Redis server."""
        try:
            # Import redis here to allow for proper mocking in tests
            import redis

            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
            )
            # Test connection
            self.client.ping()
            self._connected = True
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            self._connected = False
            return False

    def is_connected(self) -> bool:
        """Check if Redis connection is active."""
        if not REDIS_AVAILABLE or not self.client:
            return False

        try:
            self.client.ping()
            return True
        except Exception:
            self._connected = False
            return False

    def _get_cache_key(self, domain: str, analyzer: str) -> str:
        """Generate cache key for domain and analyzer."""
        return f"alexscan:domain:{domain}:analyzer:{analyzer}"

    def get_cached_result(self, domain: str, analyzer: str) -> Optional[Dict[str, Any]]:
        """
        Get cached analysis result for domain and analyzer.

        Args:
            domain: Domain name
            analyzer: Analyzer name (dns, whois, ssl, blocklist, dga, crawler)

        Returns:
            Cached result dict or None if not found/expired
        """
        if not self.is_connected():
            return None

        # Don't cache LLM summaries
        if analyzer == "llm_summary":
            return None

        try:
            cache_key = self._get_cache_key(domain, analyzer)
            cached_data = self.client.get(cache_key)

            if cached_data:
                result = json.loads(cached_data)
                logger.info(f"Cache hit for {domain} - {analyzer}")
                return result
            else:
                logger.debug(f"Cache miss for {domain} - {analyzer}")
                return None

        except Exception as e:
            logger.error(f"Error retrieving cached result for {domain} - {analyzer}: {e}")
            return None

    def set_cached_result(self, domain: str, analyzer: str, result: Dict[str, Any]) -> bool:
        """
        Cache analysis result for domain and analyzer.

        Args:
            domain: Domain name
            analyzer: Analyzer name
            result: Analysis result to cache

        Returns:
            True if successfully cached, False otherwise
        """
        if not self.is_connected():
            return False

        # Don't cache LLM summaries
        if analyzer == "llm_summary":
            return False

        try:
            cache_key = self._get_cache_key(domain, analyzer)

            # Serialize result to JSON
            cached_data = json.dumps(result, default=str, ensure_ascii=False)

            # Set with TTL
            success = self.client.setex(cache_key, self.ttl, cached_data)

            if success:
                logger.info(f"Cached result for {domain} - {analyzer} (TTL: {self.ttl}s)")
            else:
                logger.warning(f"Failed to cache result for {domain} - {analyzer}")

            return bool(success)

        except Exception as e:
            logger.error(f"Error caching result for {domain} - {analyzer}: {e}")
            return False

    def invalidate_domain(self, domain: str) -> int:
        """
        Invalidate all cached results for a domain.

        Args:
            domain: Domain name

        Returns:
            Number of keys deleted
        """
        if not self.is_connected():
            return 0

        try:
            pattern = f"alexscan:domain:{domain}:*"
            keys = self.client.keys(pattern)

            if keys:
                deleted = self.client.delete(*keys)
                logger.info(f"Invalidated {deleted} cached results for {domain}")
                return deleted
            else:
                return 0

        except Exception as e:
            logger.error(f"Error invalidating cache for {domain}: {e}")
            return 0

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics."""
        if not self.is_connected():
            return {"connected": False}

        try:
            info = self.client.info()
            stats = {
                "connected": True,
                "total_keys": info.get("db0", {}).get("keys", 0) if "db0" in info else 0,
                "memory_used": info.get("used_memory_human", "N/A"),
                "memory_peak": info.get("used_memory_peak_human", "N/A"),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "evicted_keys": info.get("evicted_keys", 0),
            }

            # Calculate hit rate
            total_requests = stats["hits"] + stats["misses"]
            if total_requests > 0:
                stats["hit_rate"] = round((stats["hits"] / total_requests) * 100, 2)
            else:
                stats["hit_rate"] = 0.0

            return stats

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"connected": False, "error": str(e)}

    def clear_cache(self) -> bool:
        """Clear all AlexScan cached data."""
        if not self.is_connected():
            return False

        try:
            pattern = "alexscan:*"
            keys = self.client.keys(pattern)

            if keys:
                deleted = self.client.delete(*keys)
                logger.info(f"Cleared {deleted} cache entries")
                return True
            else:
                logger.info("No cache entries to clear")
                return True

        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False


# Global cache manager instance
_cache_manager = None


def get_cache_manager() -> CacheManager:
    """Get global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def is_redis_available() -> bool:
    """Check if Redis is available and connected."""
    return REDIS_AVAILABLE and get_cache_manager().is_connected()
