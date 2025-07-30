"""
Metrics Collector

General Staff G4 Role: Performance Intelligence
Collects and aggregates performance metrics across Copper Alloy Brass
"""

import time
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
import statistics

from coppersun_brass.core.context.dcp_manager import DCPManager
# from coppersun_brass.core.event_bus import EventBus  # EventBus removed - using DCP coordination
from coppersun_brass.core.context.dcp_coordination import DCPCoordinator

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Centralized metrics collection system
    
    General Staff G4 Function: Aggregates performance data from all
    Copper Alloy Brass components to provide strategic performance insights.
    """
    
    def __init__(self, 
                 dcp_path: Optional[str] = None,
                 event_bus: Optional[Any] = None):  # EventBus phased out
        """
        Initialize with MANDATORY DCP integration
        
        Args:
            dcp_path: Path to DCP context file (mandatory per CLAUDE.md)
            event_bus: Event bus for metric events
        """
        # DCP is MANDATORY
        self.dcp_manager = DCPManager(dcp_path)
        
        # Initialize DCPCoordinator for event subscriptions
        self.coordinator = None
        if self.dcp_manager:
            self.coordinator = DCPCoordinator(
                agent_name="metrics_collector",
                dcp_manager=self.dcp_manager
            )
            logger.info("MetricsCollector initialized with DCPCoordinator")
        
        # Metric storage
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.timers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Metric metadata
        self.metric_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Aggregation windows
        self.windows = {
            '1m': timedelta(minutes=1),
            '5m': timedelta(minutes=5),
            '15m': timedelta(minutes=15),
            '1h': timedelta(hours=1),
            '24h': timedelta(hours=24)
        }
        
        # Time series data
        self.time_series: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        
        # Load historical metrics
        self._load_historical_metrics()
    
    def _load_historical_metrics(self) -> None:
        """Load historical metrics from DCP"""
        try:
            metrics_data = self.dcp_manager.get_section('performance.metrics', {})
            
            # Load counters
            self.counters.update(metrics_data.get('counters', {}))
            
            # Load metadata
            self.metric_metadata = metrics_data.get('metadata', {})
            
            logger.info(f"Loaded {len(self.counters)} historical metrics")
            
        except Exception as e:
            logger.warning(f"Could not load historical metrics: {e}")
    
    def increment_counter(self, 
                         name: str, 
                         value: int = 1,
                         tags: Optional[Dict[str, str]] = None) -> None:
        """
        Increment a counter metric
        
        Args:
            name: Metric name
            value: Increment value
            tags: Optional tags for grouping
        """
        metric_key = self._build_metric_key(name, tags)
        self.counters[metric_key] += value
        
        # Record time series
        self._record_time_series(metric_key, self.counters[metric_key], 'counter')
        
        # Emit event
        self.event_bus.emit('metric_updated', {
            'type': 'counter',
            'name': name,
            'value': self.counters[metric_key],
            'tags': tags
        })
    
    def set_gauge(self,
                  name: str,
                  value: float,
                  tags: Optional[Dict[str, str]] = None) -> None:
        """
        Set a gauge metric
        
        Args:
            name: Metric name
            value: Current value
            tags: Optional tags
        """
        metric_key = self._build_metric_key(name, tags)
        self.gauges[metric_key] = value
        
        # Record time series
        self._record_time_series(metric_key, value, 'gauge')
        
        # Emit event
        self.event_bus.emit('metric_updated', {
            'type': 'gauge',
            'name': name,
            'value': value,
            'tags': tags
        })
    
    def record_histogram(self,
                        name: str,
                        value: float,
                        tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record a histogram value
        
        Args:
            name: Metric name
            value: Value to record
            tags: Optional tags
        """
        metric_key = self._build_metric_key(name, tags)
        self.histograms[metric_key].append(value)
        
        # Record time series
        self._record_time_series(metric_key, value, 'histogram')
        
        # Emit event
        self.event_bus.emit('metric_updated', {
            'type': 'histogram',
            'name': name,
            'value': value,
            'tags': tags
        })
    
    def record_timer(self,
                    name: str,
                    duration_ms: float,
                    tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record a timer value
        
        Args:
            name: Metric name
            duration_ms: Duration in milliseconds
            tags: Optional tags
        """
        metric_key = self._build_metric_key(name, tags)
        self.timers[metric_key].append(duration_ms)
        
        # Record time series
        self._record_time_series(metric_key, duration_ms, 'timer')
        
        # Emit event
        self.event_bus.emit('metric_updated', {
            'type': 'timer',
            'name': name,
            'duration_ms': duration_ms,
            'tags': tags
        })
    
    def time(self, 
             name: str,
             tags: Optional[Dict[str, str]] = None) -> 'Timer':
        """
        Context manager for timing operations
        
        Usage:
            with metrics.time('operation_duration'):
                # Do something
                pass
        """
        return Timer(self, name, tags)
    
    def get_counter(self, 
                   name: str,
                   tags: Optional[Dict[str, str]] = None) -> int:
        """Get current counter value"""
        metric_key = self._build_metric_key(name, tags)
        return self.counters.get(metric_key, 0)
    
    def get_gauge(self,
                  name: str,
                  tags: Optional[Dict[str, str]] = None) -> Optional[float]:
        """Get current gauge value"""
        metric_key = self._build_metric_key(name, tags)
        return self.gauges.get(metric_key)
    
    def get_histogram_stats(self,
                           name: str,
                           tags: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get histogram statistics"""
        metric_key = self._build_metric_key(name, tags)
        values = list(self.histograms.get(metric_key, []))
        
        if not values:
            return {
                'count': 0,
                'min': 0,
                'max': 0,
                'mean': 0,
                'median': 0,
                'p75': 0,
                'p95': 0,
                'p99': 0,
                'stddev': 0
            }
        
        sorted_values = sorted(values)
        
        return {
            'count': len(values),
            'min': sorted_values[0],
            'max': sorted_values[-1],
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'p75': sorted_values[int(len(values) * 0.75)],
            'p95': sorted_values[int(len(values) * 0.95)],
            'p99': sorted_values[int(len(values) * 0.99)],
            'stddev': statistics.stdev(values) if len(values) > 1 else 0
        }
    
    def get_timer_stats(self,
                       name: str,
                       tags: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get timer statistics"""
        # Same as histogram stats but specifically for timers
        return self.get_histogram_stats(name, tags)
    
    def get_metrics_summary(self, 
                           window: str = '5m') -> Dict[str, Any]:
        """
        Get summary of all metrics for a time window
        
        Args:
            window: Time window ('1m', '5m', '15m', '1h', '24h')
        """
        if window not in self.windows:
            raise ValueError(f"Invalid window: {window}")
        
        window_delta = self.windows[window]
        cutoff_time = time.time() - window_delta.total_seconds()
        
        summary = {
            'window': window,
            'timestamp': datetime.utcnow().isoformat(),
            'counters': {},
            'gauges': dict(self.gauges),  # Current values
            'histograms': {},
            'timers': {}
        }
        
        # Aggregate time series data for window
        for metric_key, series in self.time_series.items():
            metric_type = self._get_metric_type(metric_key)
            recent_points = [(t, v) for t, v in series if t > cutoff_time]
            
            if not recent_points:
                continue
            
            if metric_type == 'counter':
                # For counters, show rate per second
                if len(recent_points) >= 2:
                    time_span = recent_points[-1][0] - recent_points[0][0]
                    value_diff = recent_points[-1][1] - recent_points[0][1]
                    rate = value_diff / time_span if time_span > 0 else 0
                    summary['counters'][metric_key] = {
                        'rate_per_second': rate,
                        'total': recent_points[-1][1]
                    }
            
            elif metric_type in ('histogram', 'timer'):
                values = [v for _, v in recent_points]
                stats_dict = self._calculate_stats(values)
                
                if metric_type == 'histogram':
                    summary['histograms'][metric_key] = stats_dict
                else:
                    summary['timers'][metric_key] = stats_dict
        
        return summary
    
    def export_metrics(self) -> Dict[str, Any]:
        """Export all metrics for external consumption"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'counters': dict(self.counters),
            'gauges': dict(self.gauges),
            'histogram_stats': {
                k: self.get_histogram_stats(k) 
                for k in self.histograms
            },
            'timer_stats': {
                k: self.get_timer_stats(k)
                for k in self.timers
            },
            'metadata': self.metric_metadata
        }
    
    def reset_metrics(self, metric_type: Optional[str] = None) -> None:
        """Reset metrics (useful for testing)"""
        if metric_type == 'counters' or metric_type is None:
            self.counters.clear()
        
        if metric_type == 'gauges' or metric_type is None:
            self.gauges.clear()
        
        if metric_type == 'histograms' or metric_type is None:
            self.histograms.clear()
        
        if metric_type == 'timers' or metric_type is None:
            self.timers.clear()
        
        if metric_type is None:
            self.time_series.clear()
    
    def _build_metric_key(self, 
                         name: str,
                         tags: Optional[Dict[str, str]] = None) -> str:
        """Build metric key with tags"""
        if not tags:
            return name
        
        # Sort tags for consistent keys
        tag_str = ','.join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name},{tag_str}"
    
    def _record_time_series(self,
                           metric_key: str,
                           value: float,
                           metric_type: str) -> None:
        """Record time series data point"""
        timestamp = time.time()
        self.time_series[metric_key].append((timestamp, value))
        
        # Update metadata
        if metric_key not in self.metric_metadata:
            self.metric_metadata[metric_key] = {
                'type': metric_type,
                'first_seen': timestamp,
                'last_updated': timestamp
            }
        else:
            self.metric_metadata[metric_key]['last_updated'] = timestamp
    
    def _get_metric_type(self, metric_key: str) -> Optional[str]:
        """Get metric type from metadata"""
        return self.metric_metadata.get(metric_key, {}).get('type')
    
    def _calculate_stats(self, values: List[float]) -> Dict[str, float]:
        """Calculate statistics for a list of values"""
        if not values:
            return {
                'count': 0,
                'min': 0,
                'max': 0,
                'mean': 0,
                'p50': 0,
                'p95': 0,
                'p99': 0
            }
        
        sorted_values = sorted(values)
        
        return {
            'count': len(values),
            'min': sorted_values[0],
            'max': sorted_values[-1],
            'mean': sum(values) / len(values),
            'p50': sorted_values[len(values) // 2],
            'p95': sorted_values[int(len(values) * 0.95)],
            'p99': sorted_values[int(len(values) * 0.99)]
        }
    
    def save_metrics(self) -> None:
        """Save metrics to DCP"""
        try:
            self.dcp_manager.update_section(
                'performance.metrics',
                {
                    'counters': dict(self.counters),
                    'metadata': self.metric_metadata,
                    'last_saved': datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")


    def subscribe_to_events(self) -> None:
        """Subscribe to relevant metric events through DCP."""
        if not self.coordinator:
            logger.warning("No coordinator available for event subscriptions")
            return
        
        # Subscribe to planning events for metrics
        self.coordinator.subscribe("planning.decision.made", self._on_planning_metric)
        self.coordinator.subscribe("planning.outcome.recorded", self._on_outcome_metric)
        
        # Start polling
        self.coordinator.start_polling()
        logger.info("MetricsCollector subscribed to events")
    
    def _on_planning_metric(self, observation: Dict[str, Any]) -> None:
        """Handle planning decision metrics."""
        try:
            self.increment("planning.decisions.total")
            data = observation.get('data', {})
            if data.get('type'):
                self.increment(f"planning.decisions.{data['type']}")
        except Exception as e:
            logger.error(f"Error processing planning metric: {e}")
    
    def _on_outcome_metric(self, observation: Dict[str, Any]) -> None:
        """Handle outcome metrics."""
        try:
            data = observation.get('data', {})
            if data.get('success'):
                self.increment("planning.outcomes.success")
            else:
                self.increment("planning.outcomes.failure")
        except Exception as e:
            logger.error(f"Error processing outcome metric: {e}")
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if hasattr(self, 'coordinator') and self.coordinator:
            self.coordinator.stop_polling()
            logger.info("MetricsCollector coordinator stopped")


class Timer:
    """Context manager for timing operations"""
    
    def __init__(self, 
                 collector: MetricsCollector,
                 name: str,
                 tags: Optional[Dict[str, str]] = None):
        self.collector = collector
        self.name = name
        self.tags = tags
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            self.collector.record_timer(self.name, duration_ms, self.tags)