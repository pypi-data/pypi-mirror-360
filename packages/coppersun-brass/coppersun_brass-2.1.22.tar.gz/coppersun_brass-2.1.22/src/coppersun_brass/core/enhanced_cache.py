"""
Enhanced Cache Manager for Copper Alloy Brass
Implements file size-aware caching with better invalidation
"""

import json
import hashlib
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, asdict
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a cache entry with metadata"""
    key: str
    value: Any
    file_size: int
    file_mtime: float
    created_at: float
    access_count: int = 0
    last_accessed: float = None
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.created_at
    
    def is_valid(self, file_stat) -> bool:
        """Check if cache entry is still valid"""
        return (self.file_size == file_stat.st_size and 
                self.file_mtime == file_stat.st_mtime)
    
    def access(self):
        """Record an access to this entry"""
        self.access_count += 1
        self.last_accessed = time.time()


class EnhancedCacheManager:
    """
    Enhanced cache manager with file size-aware keys and smart invalidation.
    Replaces simple hash-based caching with comprehensive file metadata tracking.
    """
    
    def __init__(self, 
                 cache_dir: Path,
                 ttl_seconds: int = 3600,  # 1 hour default TTL
                 max_entries: int = 10000,
                 max_memory_mb: int = 100):
        """
        Initialize enhanced cache manager
        
        Args:
            cache_dir: Directory for persistent cache storage
            ttl_seconds: Time-to-live for cache entries
            max_entries: Maximum number of cache entries
            max_memory_mb: Maximum memory usage for in-memory cache
        """
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "enhanced_cache.json"
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self.max_memory_mb = max_memory_mb
        
        # In-memory cache
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.cache_lock = threading.RLock()
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'invalidations': 0
        }
        
        # Load existing cache
        self._load_cache()
        
        # Background cleanup thread
        self.cleanup_executor = ThreadPoolExecutor(max_workers=1)
        self._schedule_cleanup()
    
    def _generate_cache_key(self, file_path: Path, include_content: bool = False) -> Tuple[str, Dict[str, Any]]:
        """
        Generate comprehensive cache key including file size
        
        Args:
            file_path: Path to file
            include_content: Whether to include content hash (slower but more accurate)
            
        Returns:
            Tuple of (cache_key, metadata)
        """
        try:
            stat = file_path.stat()
            
            # Basic components
            components = [
                str(file_path.absolute()),
                str(stat.st_size),  # File size
                str(int(stat.st_mtime * 1000000))  # Microsecond precision mtime
            ]
            
            # Optional content hash for extra accuracy
            content_hash = None
            if include_content and stat.st_size < 10 * 1024 * 1024:  # Only for files < 10MB
                hasher = hashlib.sha256()
                with open(file_path, 'rb') as f:
                    # Read in chunks for memory efficiency
                    while chunk := f.read(65536):
                        hasher.update(chunk)
                content_hash = hasher.hexdigest()[:16]
                components.append(content_hash)
            
            # Generate key
            key = hashlib.md5('|'.join(components).encode()).hexdigest()
            
            metadata = {
                'file_path': str(file_path),
                'file_size': stat.st_size,
                'file_mtime': stat.st_mtime,
                'content_hash': content_hash
            }
            
            return key, metadata
            
        except Exception as e:
            logger.error(f"Error generating cache key for {file_path}: {e}")
            # Fallback key
            return hashlib.md5(str(file_path).encode()).hexdigest(), {}
    
    def get(self, file_path: Path, 
            compute_func: Optional[Callable] = None,
            include_content_hash: bool = False) -> Optional[Any]:
        """
        Get value from cache or compute if missing
        
        Args:
            file_path: Path to file
            compute_func: Function to compute value if cache miss
            include_content_hash: Whether to include content in cache key
            
        Returns:
            Cached or computed value
        """
        key, metadata = self._generate_cache_key(file_path, include_content_hash)
        
        with self.cache_lock:
            # Check memory cache
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                
                # Validate entry
                try:
                    stat = file_path.stat()
                    if entry.is_valid(stat) and self._is_entry_fresh(entry):
                        entry.access()
                        self.stats['hits'] += 1
                        return entry.value
                    else:
                        # Invalid or stale entry
                        del self.memory_cache[key]
                        self.stats['invalidations'] += 1
                except Exception:
                    # File might have been deleted
                    del self.memory_cache[key]
                    self.stats['invalidations'] += 1
            
            # Cache miss
            self.stats['misses'] += 1
            
            if compute_func:
                # Compute value
                value = compute_func(file_path)
                
                # Store in cache
                self.put(file_path, value, metadata)
                
                return value
            
            return None
    
    def put(self, file_path: Path, value: Any, metadata: Optional[Dict] = None):
        """
        Store value in cache
        
        Args:
            file_path: Path to file
            value: Value to cache
            metadata: Optional metadata (will be computed if not provided)
        """
        if metadata is None:
            key, metadata = self._generate_cache_key(file_path)
        else:
            key = hashlib.md5(
                f"{file_path}|{metadata.get('file_size', 0)}|{metadata.get('file_mtime', 0)}".encode()
            ).hexdigest()
        
        with self.cache_lock:
            # Check cache size
            if len(self.memory_cache) >= self.max_entries:
                self._evict_lru()
            
            # Create entry
            entry = CacheEntry(
                key=key,
                value=value,
                file_size=metadata.get('file_size', 0),
                file_mtime=metadata.get('file_mtime', 0),
                created_at=time.time()
            )
            
            self.memory_cache[key] = entry
            
            # Persist to disk periodically
            if len(self.memory_cache) % 100 == 0:
                self._save_cache()
    
    def invalidate(self, file_path: Path):
        """Invalidate cache entry for a file"""
        key, _ = self._generate_cache_key(file_path)
        
        with self.cache_lock:
            if key in self.memory_cache:
                del self.memory_cache[key]
                self.stats['invalidations'] += 1
    
    def _is_entry_fresh(self, entry: CacheEntry) -> bool:
        """Check if cache entry is within TTL"""
        age = time.time() - entry.created_at
        return age < self.ttl_seconds
    
    def _evict_lru(self):
        """Evict least recently used entry"""
        if not self.memory_cache:
            return
        
        # Find LRU entry
        lru_key = min(
            self.memory_cache.keys(),
            key=lambda k: self.memory_cache[k].last_accessed
        )
        
        del self.memory_cache[lru_key]
        self.stats['evictions'] += 1
    
    def _load_cache(self):
        """Load cache from disk"""
        if not self.cache_file.exists():
            return
        
        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
            
            # Reconstruct cache entries
            for key, entry_data in data.items():
                if self._is_entry_data_valid(entry_data):
                    entry = CacheEntry(
                        key=key,
                        value=entry_data['value'],
                        file_size=entry_data['file_size'],
                        file_mtime=entry_data['file_mtime'],
                        created_at=entry_data['created_at'],
                        access_count=entry_data.get('access_count', 0),
                        last_accessed=entry_data.get('last_accessed', entry_data['created_at'])
                    )
                    
                    # Only load fresh entries
                    if self._is_entry_fresh(entry):
                        self.memory_cache[key] = entry
            
            logger.info(f"Loaded {len(self.memory_cache)} cache entries")
            
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
    
    def _save_cache(self):
        """Save cache to disk"""
        try:
            # Convert entries to serializable format
            data = {}
            for key, entry in self.memory_cache.items():
                data[key] = {
                    'value': entry.value,
                    'file_size': entry.file_size,
                    'file_mtime': entry.file_mtime,
                    'created_at': entry.created_at,
                    'access_count': entry.access_count,
                    'last_accessed': entry.last_accessed
                }
            
            # Atomic write
            temp_file = self.cache_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            temp_file.replace(self.cache_file)
            
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def _is_entry_data_valid(self, entry_data: Dict) -> bool:
        """Validate entry data structure"""
        required_fields = ['value', 'file_size', 'file_mtime', 'created_at']
        return all(field in entry_data for field in required_fields)
    
    def _schedule_cleanup(self):
        """Schedule periodic cache cleanup"""
        def cleanup_task():
            while True:
                time.sleep(300)  # Run every 5 minutes
                self._cleanup_stale_entries()
        
        self.cleanup_executor.submit(cleanup_task)
    
    def _cleanup_stale_entries(self):
        """Remove stale entries from cache"""
        with self.cache_lock:
            stale_keys = []
            
            for key, entry in self.memory_cache.items():
                if not self._is_entry_fresh(entry):
                    stale_keys.append(key)
            
            for key in stale_keys:
                del self.memory_cache[key]
            
            if stale_keys:
                logger.info(f"Cleaned up {len(stale_keys)} stale cache entries")
                self._save_cache()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            'entries': len(self.memory_cache),
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'hit_rate': f"{hit_rate * 100:.1f}%",
            'evictions': self.stats['evictions'],
            'invalidations': self.stats['invalidations'],
            'memory_usage_estimate': sum(
                len(str(entry.value)) for entry in self.memory_cache.values()
            ) / (1024 * 1024)  # MB
        }
    
    def clear(self):
        """Clear all cache entries"""
        with self.cache_lock:
            self.memory_cache.clear()
            self.stats = {
                'hits': 0,
                'misses': 0,
                'evictions': 0,
                'invalidations': 0
            }
            
        # Remove cache file
        if self.cache_file.exists():
            self.cache_file.unlink()
            
        logger.info("Cache cleared")
    
    def close(self):
        """Close cache manager and save state"""
        self._save_cache()
        self.cleanup_executor.shutdown(wait=False)