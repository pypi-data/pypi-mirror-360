"""
Caching System for Copper Alloy Brass v1.0
Implements in-memory caching with TTL for performance optimization.
"""

import time
import hashlib
import json
from typing import Any, Dict, Optional, Callable
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching for Copper Alloy Brass components."""
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize cache manager.
        
        Args:
            default_ttl: Default time-to-live in seconds (1 hour)
        """
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
        
    def _make_key(self, namespace: str, key: str) -> str:
        """Create a cache key from namespace and key."""
        return f"{namespace}:{key}"
        
    def get(self, namespace: str, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            namespace: Cache namespace (e.g., 'file_analysis')
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        cache_key = self._make_key(namespace, key)
        
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            
            # Check if expired
            if time.time() < entry['expires_at']:
                self._stats['hits'] += 1
                logger.debug(f"Cache hit: {cache_key}")
                return entry['value']
            else:
                # Expired, remove it
                del self._cache[cache_key]
                self._stats['evictions'] += 1
                
        self._stats['misses'] += 1
        return None
        
    def set(self, namespace: str, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in cache.
        
        Args:
            namespace: Cache namespace
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        cache_key = self._make_key(namespace, key)
        ttl = ttl or self.default_ttl
        
        self._cache[cache_key] = {
            'value': value,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }
        
        logger.debug(f"Cache set: {cache_key} (TTL: {ttl}s)")
        
    def invalidate(self, namespace: str, key: Optional[str] = None):
        """
        Invalidate cache entries.
        
        Args:
            namespace: Cache namespace
            key: Specific key to invalidate (all in namespace if None)
        """
        if key:
            cache_key = self._make_key(namespace, key)
            if cache_key in self._cache:
                del self._cache[cache_key]
                logger.debug(f"Cache invalidated: {cache_key}")
        else:
            # Invalidate entire namespace
            to_delete = [k for k in self._cache if k.startswith(f"{namespace}:")]
            for k in to_delete:
                del self._cache[k]
            logger.debug(f"Cache namespace invalidated: {namespace} ({len(to_delete)} entries)")
            
    def get_or_compute(self, 
                      namespace: str, 
                      key: str, 
                      compute_fn: Callable[[], Any],
                      ttl: Optional[int] = None) -> Any:
        """
        Get from cache or compute and cache.
        
        Args:
            namespace: Cache namespace
            key: Cache key
            compute_fn: Function to compute value if not cached
            ttl: Time-to-live in seconds
            
        Returns:
            Cached or computed value
        """
        value = self.get(namespace, key)
        
        if value is None:
            value = compute_fn()
            self.set(namespace, key, value, ttl)
            
        return value
        
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = self._stats['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'evictions': self._stats['evictions'],
            'hit_rate': hit_rate,
            'size': len(self._cache),
            'memory_estimate_mb': self._estimate_memory_usage() / 1024 / 1024
        }
        
    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage in bytes."""
        # Rough estimation - serialize and measure
        try:
            return len(json.dumps(self._cache).encode())
        except:
            return 0
            
    def clear(self):
        """Clear all cache entries."""
        self._cache.clear()
        logger.info("Cache cleared")


class FileCache:
    """Specialized cache for file analysis results."""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.namespace = 'file_analysis'
        
    def get_file_key(self, file_path: Path) -> str:
        """Generate cache key for file."""
        try:
            # Include file modification time in key
            stat = file_path.stat()
            content_hash = hashlib.md5(f"{file_path}:{stat.st_mtime}".encode()).hexdigest()
            return content_hash
        except:
            return str(file_path)
            
    def get(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Get cached file analysis."""
        key = self.get_file_key(file_path)
        return self.cache.get(self.namespace, key)
        
    def set(self, file_path: Path, analysis: Dict[str, Any], ttl: int = 3600):
        """Cache file analysis."""
        key = self.get_file_key(file_path)
        self.cache.set(self.namespace, key, analysis, ttl)
        
    def invalidate(self, file_path: Path):
        """Invalidate cached file analysis."""
        key = self.get_file_key(file_path)
        self.cache.invalidate(self.namespace, key)


# Global cache instance
_global_cache = None

def get_cache() -> CacheManager:
    """Get global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager()
    return _global_cache