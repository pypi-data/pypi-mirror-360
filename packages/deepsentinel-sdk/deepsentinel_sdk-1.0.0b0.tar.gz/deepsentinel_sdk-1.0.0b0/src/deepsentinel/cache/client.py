"""Response caching client with LRU eviction and TTL support.

This module provides a comprehensive caching system with LRU eviction,
TTL-based expiration, and performance metrics tracking.
"""

import asyncio
import hashlib
import json
import time
from typing import Any, Dict, Optional, Tuple

import structlog


class CacheEntry:
    """Represents a cached entry with TTL and metadata.
    
    Attributes:
        value: The cached value
        created_at: Timestamp when the entry was created
        ttl: Time-to-live in seconds
        access_count: Number of times this entry has been accessed
        last_accessed: Timestamp of last access
        metadata: Additional metadata about the cached entry
    """
    
    def __init__(
        self,
        value: Any,
        ttl: int = 3600,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a cache entry.
        
        Args:
            value: The value to cache
            ttl: Time-to-live in seconds
            metadata: Additional metadata
        """
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.access_count = 0
        self.last_accessed = self.created_at
        self.metadata = metadata or {}
    
    @property
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return time.time() - self.created_at > self.ttl
    
    @property
    def age(self) -> float:
        """Get the age of the cache entry in seconds."""
        return time.time() - self.created_at
    
    def access(self) -> Any:
        """Access the cached value and update access statistics.
        
        Returns:
            The cached value
        """
        self.access_count += 1
        self.last_accessed = time.time()
        return self.value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert cache entry to dictionary.
        
        Returns:
            Dictionary representation of the cache entry
        """
        return {
            "created_at": self.created_at,
            "ttl": self.ttl,
            "age": self.age,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "is_expired": self.is_expired,
            "metadata": self.metadata,
        }


class CacheStats:
    """Cache performance statistics.
    
    Attributes:
        hits: Number of cache hits
        misses: Number of cache misses
        evictions: Number of cache evictions
        expired: Number of expired entries removed
    """
    
    def __init__(self) -> None:
        """Initialize cache statistics."""
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.expired = 0
        self.start_time = time.time()
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate."""
        return 1.0 - self.hit_rate
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary.
        
        Returns:
            Dictionary representation of cache statistics
        """
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "expired": self.expired,
            "hit_rate": self.hit_rate,
            "miss_rate": self.miss_rate,
            "uptime": time.time() - self.start_time,
        }


class CacheClient:
    """LRU cache client with TTL support and performance tracking.
    
    This cache implementation provides:
    - LRU (Least Recently Used) eviction policy
    - TTL (Time To Live) based expiration
    - Performance metrics tracking
    - Async/await support
    - Key generation based on request parameters
    
    Attributes:
        max_size: Maximum number of entries in the cache
        default_ttl: Default TTL for cache entries
        stats: Cache performance statistics
        logger: Structured logger
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 3600,
        cleanup_interval: int = 300,
    ) -> None:
        """Initialize the cache client.
        
        Args:
            max_size: Maximum number of entries to store
            default_ttl: Default TTL in seconds
            cleanup_interval: Interval for cleanup tasks in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cleanup_interval = cleanup_interval
        
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: Dict[str, float] = {}  # Key -> last access time
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        
        self.stats = CacheStats()
        self.logger = structlog.get_logger(__name__)
        
        # Start cleanup task
        self._start_cleanup_task()
    
    def _start_cleanup_task(self) -> None:
        """Start the background cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_expired())
    
    async def _cleanup_expired(self) -> None:
        """Background task to clean up expired entries."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._remove_expired_entries()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(
                    "Cache cleanup error", error=str(e)
                )
    
    async def _remove_expired_entries(self) -> None:
        """Remove expired entries from the cache."""
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired
            ]
            
            for key in expired_keys:
                del self._cache[key]
                self._access_order.pop(key, None)
                self.stats.expired += 1
            
            if expired_keys:
                self.logger.debug(
                    "Removed expired cache entries",
                    count=len(expired_keys)
                )
    
    def generate_cache_key(
        self,
        request_data: Dict[str, Any],
        provider_name: str = "",
        operation: str = "",
    ) -> str:
        """Generate a cache key from request parameters.
        
        Args:
            request_data: Request parameters
            provider_name: Name of the provider
            operation: Operation being cached
            
        Returns:
            Cache key string
        """
        # Create a normalized representation for consistent hashing
        key_components = {
            "provider": provider_name,
            "operation": operation,
            "data": request_data,
        }
        
        # Sort keys for consistent ordering
        normalized = json.dumps(
            key_components, sort_keys=True, default=str
        )
        
        # Generate hash
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:32]
    
    async def get(
        self, key: str, default: Any = None
    ) -> Tuple[Optional[Any], bool]:
        """Get a value from the cache.
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Tuple of (value, cache_hit_boolean)
        """
        async with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self.stats.misses += 1
                return default, False
            
            if entry.is_expired:
                # Remove expired entry
                del self._cache[key]
                self._access_order.pop(key, None)
                self.stats.expired += 1
                self.stats.misses += 1
                return default, False
            
            # Update access order
            self._access_order[key] = time.time()
            self.stats.hits += 1
            
            return entry.access(), True
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
            metadata: Additional metadata
        """
        async with self._lock:
            # Check if we need to evict entries
            if len(self._cache) >= self.max_size and key not in self._cache:
                await self._evict_lru()
            
            # Create cache entry
            entry_ttl = ttl if ttl is not None else self.default_ttl
            entry = CacheEntry(value, entry_ttl, metadata)
            
            # Store entry and update access order
            self._cache[key] = entry
            self._access_order[key] = time.time()
            
            self.logger.debug(
                "Cache entry stored",
                key=key[:16] + "...",
                ttl=entry_ttl,
                cache_size=len(self._cache)
            )
    
    async def _evict_lru(self) -> None:
        """Evict the least recently used entry."""
        if not self._access_order:
            return
        
        # Find the least recently used key
        lru_key = min(
            self._access_order.items(),
            key=lambda x: x[1]
        )[0]
        
        # Remove from cache and access order
        del self._cache[lru_key]
        del self._access_order[lru_key]
        self.stats.evictions += 1
        
        self.logger.debug("Evicted LRU cache entry", key=lru_key[:16] + "...")
    
    async def delete(self, key: str) -> bool:
        """Delete a key from the cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key existed and was deleted, False otherwise
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._access_order.pop(key, None)
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all entries from the cache."""
        async with self._lock:
            self._cache.clear()
            self._access_order.clear()
            self.logger.info("Cache cleared")
    
    async def size(self) -> int:
        """Get the current size of the cache.
        
        Returns:
            Number of entries in the cache
        """
        return len(self._cache)
    
    async def get_stats(self) -> CacheStats:
        """Get cache performance statistics.
        
        Returns:
            CacheStats object with performance metrics
        """
        return self.stats
    
    async def get_info(self) -> Dict[str, Any]:
        """Get detailed cache information.
        
        Returns:
            Dictionary containing cache information
        """
        async with self._lock:
            total_age = sum(entry.age for entry in self._cache.values())
            avg_age = total_age / len(self._cache) if self._cache else 0
            
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "default_ttl": self.default_ttl,
                "stats": self.stats.to_dict(),
                "average_age": avg_age,
                "cleanup_interval": self.cleanup_interval,
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the cache.
        
        Returns:
            Health check results
        """
        try:
            # Test basic operations
            test_key = "__health_check__"
            test_value = {"timestamp": time.time()}
            
            await self.set(test_key, test_value, ttl=1)
            retrieved_value, hit = await self.get(test_key)
            await self.delete(test_key)
            
            return {
                "status": "healthy",
                "test_passed": hit and retrieved_value == test_value,
                "cache_size": await self.size(),
                "stats": self.stats.to_dict(),
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "cache_size": await self.size(),
            }
    
    async def close(self) -> None:
        """Close the cache client and cleanup resources."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        await self.clear()
        self.logger.info("Cache client closed")