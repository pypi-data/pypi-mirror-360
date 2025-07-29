"""
Cache Strategies

General Staff G4 Role: Resource Optimization
Different caching strategies for various use cases
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import time
import logging

logger = logging.getLogger(__name__)


class CacheStrategy(ABC):
    """Abstract base class for cache strategies"""
    
    @abstractmethod
    def should_cache(self, key: str, value: Any, context: Dict[str, Any]) -> bool:
        """Determine if a value should be cached"""
        pass
    
    @abstractmethod
    def get_ttl(self, key: str, value: Any, context: Dict[str, Any]) -> Optional[int]:
        """Get TTL (time to live) for cached value"""
        pass
    
    @abstractmethod
    def select_tier(self, key: str, value: Any, size: int, context: Dict[str, Any]) -> str:
        """Select which cache tier to use"""
        pass
    
    @abstractmethod
    def on_hit(self, key: str, tier: str) -> None:
        """Called when cache hit occurs"""
        pass
    
    @abstractmethod
    def on_miss(self, key: str) -> None:
        """Called when cache miss occurs"""
        pass
    
    @abstractmethod
    def on_eviction(self, key: str, reason: str) -> None:
        """Called when value is evicted"""
        pass


class LRUStrategy(CacheStrategy):
    """
    Least Recently Used Strategy
    
    Simple strategy that caches everything and uses LRU eviction
    """
    
    def __init__(self, default_ttl: Optional[int] = 3600):
        """
        Initialize LRU strategy
        
        Args:
            default_ttl: Default TTL in seconds (1 hour)
        """
        self.default_ttl = default_ttl
        self.access_times: Dict[str, float] = {}
    
    def should_cache(self, key: str, value: Any, context: Dict[str, Any]) -> bool:
        """Always cache in LRU strategy"""
        return True
    
    def get_ttl(self, key: str, value: Any, context: Dict[str, Any]) -> Optional[int]:
        """Return default TTL"""
        return self.default_ttl
    
    def select_tier(self, key: str, value: Any, size: int, context: Dict[str, Any]) -> str:
        """Select tier based on size"""
        # Small values in memory
        if size < 1024 * 1024:  # 1MB
            return 'memory'
        else:
            return 'disk'
    
    def on_hit(self, key: str, tier: str) -> None:
        """Update access time"""
        self.access_times[key] = time.time()
    
    def on_miss(self, key: str) -> None:
        """No special handling for misses"""
        pass
    
    def on_eviction(self, key: str, reason: str) -> None:
        """Remove from access times"""
        self.access_times.pop(key, None)


class TTLStrategy(CacheStrategy):
    """
    Time-To-Live Strategy
    
    Caches values with specific TTLs based on patterns
    """
    
    def __init__(self):
        """Initialize TTL strategy"""
        self.ttl_patterns = {
            'analysis_': 3600,      # Analysis results: 1 hour
            'scout_': 1800,         # Scout findings: 30 minutes
            'pattern_': 7200,       # Learned patterns: 2 hours
            'recommendation_': 900,  # Recommendations: 15 minutes
            'metrics_': 300,        # Metrics: 5 minutes
            'status_': 60           # Status info: 1 minute
        }
        self.hit_counts: Dict[str, int] = {}
    
    def should_cache(self, key: str, value: Any, context: Dict[str, Any]) -> bool:
        """Cache if key matches known patterns"""
        for pattern in self.ttl_patterns:
            if key.startswith(pattern):
                return True
        
        # Also cache if explicitly requested
        return context.get('force_cache', False)
    
    def get_ttl(self, key: str, value: Any, context: Dict[str, Any]) -> Optional[int]:
        """Get TTL based on key pattern"""
        # Check for explicit TTL in context
        if 'ttl' in context:
            return context['ttl']
        
        # Match patterns
        for pattern, ttl in self.ttl_patterns.items():
            if key.startswith(pattern):
                return ttl
        
        # Default TTL for unknown patterns
        return 600  # 10 minutes
    
    def select_tier(self, key: str, value: Any, size: int, context: Dict[str, Any]) -> str:
        """Select tier based on access patterns and size"""
        # Frequently accessed small items in memory
        hit_count = self.hit_counts.get(key, 0)
        
        if size < 512 * 1024 and hit_count > 5:  # 512KB and accessed >5 times
            return 'memory'
        elif size < 5 * 1024 * 1024:  # 5MB
            return 'disk'
        else:
            # Large files might go to Redis when implemented
            return 'disk'
    
    def on_hit(self, key: str, tier: str) -> None:
        """Track hit counts"""
        self.hit_counts[key] = self.hit_counts.get(key, 0) + 1
    
    def on_miss(self, key: str) -> None:
        """Reset hit count on miss"""
        self.hit_counts.pop(key, None)
    
    def on_eviction(self, key: str, reason: str) -> None:
        """Clean up hit counts"""
        self.hit_counts.pop(key, None)


class AdaptiveStrategy(CacheStrategy):
    """
    Adaptive Caching Strategy
    
    Learns from access patterns and adapts caching behavior
    """
    
    def __init__(self):
        """Initialize adaptive strategy"""
        self.access_history: Dict[str, List[float]] = {}
        self.value_sizes: Dict[str, int] = {}
        self.computation_times: Dict[str, float] = {}
        self.error_counts: Dict[str, int] = {}
        
        # Adaptive thresholds
        self.min_access_frequency = 0.1  # Accesses per minute
        self.max_error_rate = 0.2        # 20% error rate
        self.size_threshold = 10 * 1024 * 1024  # 10MB
    
    def should_cache(self, key: str, value: Any, context: Dict[str, Any]) -> bool:
        """Cache based on access patterns and computation cost"""
        # Always cache if computation was expensive
        if context.get('computation_time', 0) > 1.0:  # >1 second
            return True
        
        # Check error rate
        errors = self.error_counts.get(key, 0)
        total_accesses = len(self.access_history.get(key, []))
        if total_accesses > 0 and errors / total_accesses > self.max_error_rate:
            return False  # Too many errors
        
        # Check access frequency
        history = self.access_history.get(key, [])
        if len(history) >= 2:
            # Calculate access frequency
            time_span = history[-1] - history[0]
            if time_span > 0:
                frequency = len(history) / (time_span / 60)  # Per minute
                return frequency >= self.min_access_frequency
        
        # Cache new items optimistically
        return True
    
    def get_ttl(self, key: str, value: Any, context: Dict[str, Any]) -> Optional[int]:
        """Adaptive TTL based on access patterns"""
        history = self.access_history.get(key, [])
        
        if len(history) < 2:
            # Default TTL for new items
            return 1800  # 30 minutes
        
        # Calculate average time between accesses
        intervals = []
        for i in range(1, len(history)):
            intervals.append(history[i] - history[i-1])
        
        if intervals:
            avg_interval = sum(intervals) / len(intervals)
            # Set TTL to 3x average interval (with bounds)
            ttl = int(avg_interval * 3)
            return max(300, min(ttl, 7200))  # Between 5 min and 2 hours
        
        return 1800  # Default 30 minutes
    
    def select_tier(self, key: str, value: Any, size: int, context: Dict[str, Any]) -> str:
        """Select tier based on learned patterns"""
        # Track size
        self.value_sizes[key] = size
        
        # Hot data in memory
        history = self.access_history.get(key, [])
        if history and len(history) > 10:
            # Frequently accessed
            if size < 1024 * 1024:  # 1MB
                return 'memory'
        
        # Large or infrequent data on disk
        return 'disk'
    
    def on_hit(self, key: str, tier: str) -> None:
        """Track successful access"""
        now = time.time()
        
        # Update access history
        if key not in self.access_history:
            self.access_history[key] = []
        
        history = self.access_history[key]
        history.append(now)
        
        # Keep only recent history (last 24 hours)
        cutoff = now - 86400
        self.access_history[key] = [t for t in history if t > cutoff]
    
    def on_miss(self, key: str) -> None:
        """Track cache miss"""
        # Could indicate stale data or first access
        pass
    
    def on_eviction(self, key: str, reason: str) -> None:
        """Learn from evictions"""
        if reason == 'size_limit':
            # Might need to be more selective about what to cache
            pass
        elif reason == 'ttl_expired':
            # TTL might have been too short
            pass
        
        # Clean up tracking data
        self.access_history.pop(key, None)
        self.value_sizes.pop(key, None)
        self.computation_times.pop(key, None)
        self.error_counts.pop(key, None)
    
    def record_computation_time(self, key: str, duration: float) -> None:
        """Record how long it took to compute a value"""
        self.computation_times[key] = duration
    
    def record_error(self, key: str) -> None:
        """Record computation error"""
        self.error_counts[key] = self.error_counts.get(key, 0) + 1


class PriorityStrategy(CacheStrategy):
    """
    Priority-based Caching Strategy
    
    Caches based on explicit priorities and importance
    """
    
    def __init__(self):
        """Initialize priority strategy"""
        self.priority_patterns = {
            'critical_': 100,
            'analysis_': 80,
            'recommendation_': 70,
            'pattern_': 60,
            'metrics_': 50,
            'status_': 30
        }
        self.item_priorities: Dict[str, int] = {}
    
    def should_cache(self, key: str, value: Any, context: Dict[str, Any]) -> bool:
        """Cache based on priority threshold"""
        priority = self._get_priority(key, context)
        return priority >= 30  # Cache if priority >= 30
    
    def get_ttl(self, key: str, value: Any, context: Dict[str, Any]) -> Optional[int]:
        """TTL based on priority"""
        priority = self._get_priority(key, context)
        
        if priority >= 90:
            return 7200    # 2 hours for critical
        elif priority >= 70:
            return 3600    # 1 hour for high priority
        elif priority >= 50:
            return 1800    # 30 minutes for medium
        else:
            return 600     # 10 minutes for low
    
    def select_tier(self, key: str, value: Any, size: int, context: Dict[str, Any]) -> str:
        """High priority items go to faster tiers"""
        priority = self._get_priority(key, context)
        
        if priority >= 70 and size < 2 * 1024 * 1024:  # High priority, <2MB
            return 'memory'
        else:
            return 'disk'
    
    def on_hit(self, key: str, tier: str) -> None:
        """Could boost priority on hits"""
        current = self.item_priorities.get(key, 50)
        self.item_priorities[key] = min(current + 1, 100)  # Slight boost
    
    def on_miss(self, key: str) -> None:
        """Could reduce priority on misses"""
        if key in self.item_priorities:
            self.item_priorities[key] = max(self.item_priorities[key] - 5, 0)
    
    def on_eviction(self, key: str, reason: str) -> None:
        """Clean up priority tracking"""
        self.item_priorities.pop(key, None)
    
    def _get_priority(self, key: str, context: Dict[str, Any]) -> int:
        """Get priority for a cache key"""
        # Check explicit priority in context
        if 'priority' in context:
            return context['priority']
        
        # Check stored priority
        if key in self.item_priorities:
            return self.item_priorities[key]
        
        # Match patterns
        for pattern, priority in self.priority_patterns.items():
            if key.startswith(pattern):
                self.item_priorities[key] = priority
                return priority
        
        # Default priority
        return 50