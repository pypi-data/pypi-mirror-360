"""
Enhanced Cache Manager

General Staff G4 Role: Resource Optimization
Three-tier caching system with DCP persistence
"""

import os
import time
import json
import hashlib
import mmap
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, Union, Callable, Tuple
from datetime import datetime, timedelta
from collections import OrderedDict
from abc import ABC, abstractmethod
import logging

from coppersun_brass.core.context.dcp_manager import DCPManager
from coppersun_brass.core.cache.strategies import CacheStrategy, LRUStrategy

logger = logging.getLogger(__name__)


class CacheTier(ABC):
    """Abstract base class for cache tiers"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    async def put(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Put value in cache"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Clear entire cache"""
        pass
    
    @abstractmethod
    def size(self) -> int:
        """Get cache size in bytes"""
        pass


class MemoryCacheTier(CacheTier):
    """In-memory cache tier with size limits"""
    
    def __init__(self, max_size_mb: int = 100):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache: OrderedDict[str, Tuple[Any, Optional[float]]] = OrderedDict()
        self.size_map: Dict[str, int] = {}
        self.current_size = 0
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from memory cache"""
        if key in self.cache:
            value, expiry = self.cache[key]
            
            # Check expiry
            if expiry and time.time() > expiry:
                await self.delete(key)
                return None
            
            # Move to end (LRU)
            self.cache.move_to_end(key)
            return value
        
        return None
    
    async def put(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Put value in memory cache"""
        try:
            # Calculate size
            serialized = json.dumps(value)
            size = len(serialized.encode('utf-8'))
            
            # Check if we need to evict
            while self.current_size + size > self.max_size_bytes and self.cache:
                # Evict oldest
                oldest_key = next(iter(self.cache))
                await self.delete(oldest_key)
            
            # Store value
            expiry = time.time() + ttl if ttl else None
            self.cache[key] = (value, expiry)
            self.size_map[key] = size
            self.current_size += size
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache in memory: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete from memory cache"""
        if key in self.cache:
            del self.cache[key]
            size = self.size_map.pop(key, 0)
            self.current_size -= size
            return True
        return False
    
    async def clear(self) -> None:
        """Clear memory cache"""
        self.cache.clear()
        self.size_map.clear()
        self.current_size = 0
    
    def size(self) -> int:
        """Get current cache size"""
        return self.current_size


class DiskCacheTier(CacheTier):
    """Disk-based cache tier with file storage"""
    
    def __init__(self, cache_dir: Path, max_size_mb: int = 500):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.index_file = self.cache_dir / '.cache_index.json'
        self.index = self._load_index()
    
    def _load_index(self) -> Dict[str, Dict[str, Any]]:
        """Load cache index from disk"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load cache index: {e}")
        return {}
    
    def _save_index(self) -> None:
        """Save cache index to disk"""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.index, f)
        except Exception as e:
            logger.error(f"Failed to save cache index: {e}")
    
    def _get_cache_path(self, key: str) -> Path:
        """Get file path for cache key"""
        # Use hash to avoid filesystem issues
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash[:2]}" / f"{key_hash}.cache"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from disk cache"""
        if key not in self.index:
            return None
        
        entry = self.index[key]
        
        # Check expiry
        if entry.get('expiry') and time.time() > entry['expiry']:
            await self.delete(key)
            return None
        
        # Read from disk
        cache_path = self._get_cache_path(key)
        try:
            if cache_path.exists():
                with open(cache_path, 'r') as f:
                    value = json.load(f)
                
                # Update access time
                entry['last_access'] = time.time()
                self._save_index()
                
                return value
        except Exception as e:
            logger.error(f"Failed to read from disk cache: {e}")
        
        return None
    
    async def put(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Put value in disk cache"""
        try:
            # Serialize value
            serialized = json.dumps(value)
            size = len(serialized.encode('utf-8'))
            
            # Check total size
            await self._ensure_space(size)
            
            # Write to disk
            cache_path = self._get_cache_path(key)
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(cache_path, 'w') as f:
                f.write(serialized)
            
            # Update index
            self.index[key] = {
                'size': size,
                'created': time.time(),
                'last_access': time.time(),
                'expiry': time.time() + ttl if ttl else None
            }
            self._save_index()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to write to disk cache: {e}")
            return False
    
    async def _ensure_space(self, needed_size: int) -> None:
        """Ensure enough space by evicting if needed"""
        current_size = sum(entry['size'] for entry in self.index.values())
        
        while current_size + needed_size > self.max_size_bytes and self.index:
            # Evict least recently accessed
            oldest_key = min(
                self.index.keys(),
                key=lambda k: self.index[k]['last_access']
            )
            await self.delete(oldest_key)
            current_size = sum(entry['size'] for entry in self.index.values())
    
    async def delete(self, key: str) -> bool:
        """Delete from disk cache"""
        if key in self.index:
            # Delete file
            cache_path = self._get_cache_path(key)
            try:
                if cache_path.exists():
                    cache_path.unlink()
            except Exception as e:
                logger.error(f"Failed to delete cache file: {e}")
            
            # Update index
            del self.index[key]
            self._save_index()
            return True
        
        return False
    
    async def clear(self) -> None:
        """Clear disk cache"""
        # Delete all cache files
        for key in list(self.index.keys()):
            await self.delete(key)
        
        # Clear index
        self.index.clear()
        self._save_index()
    
    def size(self) -> int:
        """Get total cache size"""
        return sum(entry['size'] for entry in self.index.values())


class EnhancedCacheManager:
    """
    Three-tier cache manager with DCP integration
    
    General Staff G4 Role: Resource Optimization
    Maintains cache state across AI sessions for instant context
    """
    
    def __init__(self, 
                 dcp_path: Optional[str] = None,
                 memory_size_mb: int = 100,
                 disk_size_mb: int = 500,
                 cache_dir: Optional[Path] = None):
        """
        Initialize with MANDATORY DCP integration
        
        Args:
            dcp_path: Path to DCP context file (mandatory per CLAUDE.md)
            memory_size_mb: Memory cache size in MB
            disk_size_mb: Disk cache size in MB
            cache_dir: Directory for disk cache
        """
        # DCP is MANDATORY - this is how the general staff coordinates
        self.dcp_manager = DCPManager(dcp_path)
        
        # Initialize cache tiers
        self.memory_tier = MemoryCacheTier(memory_size_mb)
        
        cache_dir = cache_dir or Path.home() / '.brass' / 'cache'
        self.disk_tier = DiskCacheTier(cache_dir, disk_size_mb)
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'memory_hits': 0,
            'disk_hits': 0,
            'evictions': 0
        }
        
        # Load cache state from DCP
        self._load_cache_state_from_dcp()
        
        # Default strategy
        self.strategy = LRUStrategy()
    
    def _load_cache_state_from_dcp(self) -> None:
        """Load cache metadata and stats from DCP"""
        try:
            performance_data = self.dcp_manager.get_section('performance', {})
            cache_data = performance_data.get('cache', {})
            
            # Load statistics
            if 'statistics' in cache_data:
                stored_stats = cache_data['statistics']
                self.stats['hits'] = stored_stats.get('total_hits', 0)
                self.stats['misses'] = stored_stats.get('total_misses', 0)
                
            logger.info(f"Loaded cache state from DCP: {self.stats['hits']} hits, "
                       f"{self.stats['misses']} misses")
                
        except Exception as e:
            logger.warning(f"Could not load cache state from DCP: {e}")
    
    def _save_cache_state_to_dcp(self) -> None:
        """Save cache metadata and stats to DCP"""
        try:
            # Calculate hit rate
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0.0
            
            cache_metadata = {
                'metadata': {
                    'type': 'three_tier',
                    'memory_size_mb': self.memory_tier.max_size_bytes / (1024 * 1024),
                    'disk_size_mb': self.disk_tier.max_size_bytes / (1024 * 1024),
                    'memory_used_mb': self.memory_tier.size() / (1024 * 1024),
                    'disk_used_mb': self.disk_tier.size() / (1024 * 1024)
                },
                'statistics': {
                    'hit_rate': hit_rate,
                    'total_hits': self.stats['hits'],
                    'total_misses': self.stats['misses'],
                    'memory_hits': self.stats['memory_hits'],
                    'disk_hits': self.stats['disk_hits'],
                    'evictions': self.stats['evictions'],
                    'last_updated': datetime.utcnow().isoformat()
                }
            }
            
            self.dcp_manager.update_section('performance.cache', cache_metadata)
            
        except Exception as e:
            logger.error(f"Failed to save cache state to DCP: {e}")
    
    async def get(self, 
                  key: str,
                  compute_fn: Optional[Callable] = None) -> Optional[Any]:
        """
        Get value from cache with optional compute function
        
        Args:
            key: Cache key
            compute_fn: Function to compute value if not in cache
            
        Returns:
            Cached or computed value
        """
        # Try memory tier first
        value = await self.memory_tier.get(key)
        if value is not None:
            self.stats['hits'] += 1
            self.stats['memory_hits'] += 1
            self._log_cache_hit(key, 'memory')
            return value
        
        # Try disk tier
        value = await self.disk_tier.get(key)
        if value is not None:
            self.stats['hits'] += 1
            self.stats['disk_hits'] += 1
            self._log_cache_hit(key, 'disk')
            
            # Promote to memory tier
            await self.memory_tier.put(key, value)
            
            return value
        
        # Cache miss
        self.stats['misses'] += 1
        self._log_cache_miss(key)
        
        # Compute if function provided
        if compute_fn:
            try:
                value = await compute_fn() if asyncio.iscoroutinefunction(compute_fn) else compute_fn()
                if value is not None:
                    await self.put(key, value)
                return value
            except Exception as e:
                logger.error(f"Compute function failed: {e}")
        
        return None
    
    async def put(self, 
                  key: str, 
                  value: Any,
                  ttl: Optional[int] = None,
                  tier: str = 'auto') -> bool:
        """
        Put value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            tier: Target tier ('memory', 'disk', 'auto')
            
        Returns:
            Success boolean
        """
        try:
            # Determine size
            size = len(json.dumps(value).encode('utf-8'))
            
            # Auto tier selection based on size
            if tier == 'auto':
                # Small values go to memory
                if size < 1024 * 1024:  # 1MB
                    tier = 'memory'
                else:
                    tier = 'disk'
            
            success = False
            
            if tier == 'memory':
                success = await self.memory_tier.put(key, value, ttl)
            
            # Always put to disk for persistence
            disk_success = await self.disk_tier.put(key, value, ttl)
            success = success or disk_success
            
            if success:
                # Save state periodically
                if self.stats['hits'] % 100 == 0:
                    self._save_cache_state_to_dcp()
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to cache value: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from all cache tiers"""
        memory_deleted = await self.memory_tier.delete(key)
        disk_deleted = await self.disk_tier.delete(key)
        
        if memory_deleted or disk_deleted:
            self.stats['evictions'] += 1
            self._log_cache_eviction(key)
        
        return memory_deleted or disk_deleted
    
    async def clear(self, tier: Optional[str] = None) -> None:
        """
        Clear cache
        
        Args:
            tier: Specific tier to clear, or None for all
        """
        if tier == 'memory' or tier is None:
            await self.memory_tier.clear()
            logger.info("Cleared memory cache")
            
        if tier == 'disk' or tier is None:
            await self.disk_tier.clear()
            logger.info("Cleared disk cache")
        
        if tier is None:
            # Reset stats
            self.stats = {
                'hits': 0,
                'misses': 0,
                'memory_hits': 0,
                'disk_hits': 0,
                'evictions': 0
            }
            
        self._save_cache_state_to_dcp()
        
        # Log clear event
        self.dcp_manager.add_observation(
            'cache_cleared',
            {
                'tier': tier or 'all',
                'timestamp': datetime.utcnow().isoformat()
            },
            source_agent='cache_manager',
            priority=65
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0.0
        
        return {
            'hit_rate': hit_rate,
            'total_requests': total_requests,
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'memory_hits': self.stats['memory_hits'],
            'disk_hits': self.stats['disk_hits'],
            'evictions': self.stats['evictions'],
            'memory_size_mb': self.memory_tier.size() / (1024 * 1024),
            'disk_size_mb': self.disk_tier.size() / (1024 * 1024),
            'memory_capacity_mb': self.memory_tier.max_size_bytes / (1024 * 1024),
            'disk_capacity_mb': self.disk_tier.max_size_bytes / (1024 * 1024)
        }
    
    def _log_cache_hit(self, key: str, tier: str) -> None:
        """Log cache hit to DCP"""
        self.dcp_manager.add_observation(
            'cache_hit',
            {
                'key': hashlib.sha256(key.encode()).hexdigest()[:8],  # Anonymized
                'tier': tier,
                'strategy': self.strategy.__class__.__name__
            },
            source_agent='cache_manager',
            priority=50
        )
    
    def _log_cache_miss(self, key: str) -> None:
        """Log cache miss to DCP"""
        self.dcp_manager.add_observation(
            'cache_miss',
            {
                'key': hashlib.sha256(key.encode()).hexdigest()[:8],  # Anonymized
                'reason': 'not_found'
            },
            source_agent='cache_manager',
            priority=55
        )
    
    def _log_cache_eviction(self, key: str) -> None:
        """Log cache eviction to DCP"""
        self.dcp_manager.add_observation(
            'cache_eviction',
            {
                'key': hashlib.sha256(key.encode()).hexdigest()[:8],  # Anonymized
                'reason': 'explicit_delete'
            },
            source_agent='cache_manager',
            priority=60
        )