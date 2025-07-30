"""
Performance Profiler

General Staff G4 Role: Resource Monitoring
Tracks and analyzes Copper Alloy Brass performance in real-time
"""

import time
import psutil
import asyncio
import functools
from typing import Dict, Any, Optional, Callable, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
import traceback
import threading

from coppersun_brass.core.context.dcp_manager import DCPManager

logger = logging.getLogger(__name__)


class PerformanceProfiler:
    """
    Real-time performance profiler with DCP integration
    
    General Staff G4 Function: Monitors system resources and agent
    performance to identify bottlenecks and optimization opportunities.
    Provides AI with performance insights for strategic planning.
    """
    
    def __init__(self, dcp_path: Optional[str] = None):
        """
        Initialize with MANDATORY DCP integration
        
        Args:
            dcp_path: Path to DCP context file (mandatory per CLAUDE.md)
        """
        # DCP is MANDATORY - performance data informs AI strategy
        self.dcp_manager = DCPManager(dcp_path)
        
        # Performance tracking
        self.operation_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.memory_samples: deque = deque(maxlen=100)
        self.cpu_samples: deque = deque(maxlen=100)
        
        # Real-time metrics
        self.active_operations: Dict[str, float] = {}
        self.operation_counts: Dict[str, int] = defaultdict(int)
        self.error_counts: Dict[str, int] = defaultdict(int)
        
        # Thresholds for alerts
        self.thresholds = {
            'operation_time_ms': 1000,      # 1 second
            'memory_percent': 80,           # 80% memory usage
            'cpu_percent': 90,              # 90% CPU usage
            'error_rate': 0.1               # 10% error rate
        }
        
        # Background monitoring
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        
        # Process info
        self.process = psutil.Process()
        
        # Load historical data
        self._load_performance_history()
    
    def _load_performance_history(self) -> None:
        """Load historical performance data from DCP"""
        try:
            perf_data = self.dcp_manager.get_section('performance.profiler', {})
            
            # Load thresholds
            if 'thresholds' in perf_data:
                self.thresholds.update(perf_data['thresholds'])
            
            # Load historical averages
            self.historical_averages = perf_data.get('historical_averages', {})
            
            logger.info(f"Loaded performance history with {len(self.historical_averages)} operations")
            
        except Exception as e:
            logger.warning(f"Could not load performance history: {e}")
            self.historical_averages = {}
    
    def profile(self, operation_name: str):
        """
        Decorator to profile function execution
        
        Usage:
            @profiler.profile("scout_analysis")
            async def analyze_file(path):
                ...
        """
        def decorator(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                operation_id = f"{operation_name}_{int(start_time * 1000)}"
                
                # Track active operation
                self.active_operations[operation_id] = start_time
                
                try:
                    # Execute function
                    result = await func(*args, **kwargs)
                    
                    # Record success
                    duration = (time.time() - start_time) * 1000  # milliseconds
                    self._record_operation(operation_name, duration, success=True)
                    
                    return result
                    
                except Exception as e:
                    # Record failure
                    duration = (time.time() - start_time) * 1000
                    self._record_operation(operation_name, duration, success=False, error=str(e))
                    raise
                    
                finally:
                    # Clean up
                    self.active_operations.pop(operation_id, None)
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                operation_id = f"{operation_name}_{int(start_time * 1000)}"
                
                # Track active operation
                self.active_operations[operation_id] = start_time
                
                try:
                    # Execute function
                    result = func(*args, **kwargs)
                    
                    # Record success
                    duration = (time.time() - start_time) * 1000
                    self._record_operation(operation_name, duration, success=True)
                    
                    return result
                    
                except Exception as e:
                    # Record failure
                    duration = (time.time() - start_time) * 1000
                    self._record_operation(operation_name, duration, success=False, error=str(e))
                    raise
                    
                finally:
                    # Clean up
                    self.active_operations.pop(operation_id, None)
            
            # Return appropriate wrapper
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
                
        return decorator
    
    def _record_operation(self, 
                         operation: str, 
                         duration_ms: float,
                         success: bool = True,
                         error: Optional[str] = None) -> None:
        """Record operation metrics"""
        # Update tracking
        self.operation_times[operation].append(duration_ms)
        self.operation_counts[operation] += 1
        
        if not success:
            self.error_counts[operation] += 1
        
        # Check for performance issues
        if duration_ms > self.thresholds['operation_time_ms']:
            self._log_slow_operation(operation, duration_ms)
        
        # Update DCP periodically
        if self.operation_counts[operation] % 100 == 0:
            self._update_dcp_metrics()
    
    async def start_monitoring(self, interval_seconds: int = 10) -> None:
        """Start background performance monitoring"""
        if self._monitoring:
            logger.warning("Performance monitoring already active")
            return
        
        self._monitoring = True
        self._monitor_task = asyncio.create_task(
            self._monitor_loop(interval_seconds)
        )
        
        logger.info(f"Started performance monitoring with {interval_seconds}s interval")
    
    async def stop_monitoring(self) -> None:
        """Stop background monitoring"""
        if not self._monitoring:
            return
        
        self._monitoring = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        # Save final metrics
        self._update_dcp_metrics()
        
        logger.info("Stopped performance monitoring")
    
    async def _monitor_loop(self, interval: int) -> None:
        """Background monitoring loop"""
        while self._monitoring:
            try:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Check for issues
                self._check_performance_issues()
                
                # Wait for next interval
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)
    
    def _collect_system_metrics(self) -> None:
        """Collect current system metrics"""
        try:
            # CPU usage
            cpu_percent = self.process.cpu_percent(interval=0.1)
            self.cpu_samples.append(cpu_percent)
            
            # Memory usage
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            self.memory_samples.append({
                'percent': memory_percent,
                'rss': memory_info.rss,
                'vms': memory_info.vms,
                'timestamp': time.time()
            })
            
            # Thread count
            thread_count = threading.active_count()
            
            # Log to DCP
            self.dcp_manager.add_observation(
                'performance_metrics',
                {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_percent,
                    'memory_mb': memory_info.rss / (1024 * 1024),
                    'thread_count': thread_count,
                    'active_operations': len(self.active_operations)
                },
                source_agent='performance_profiler',
                priority=40
            )
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    def _check_performance_issues(self) -> None:
        """Check for performance issues and alert"""
        issues = []
        
        # Check CPU usage
        if self.cpu_samples:
            avg_cpu = sum(self.cpu_samples) / len(self.cpu_samples)
            if avg_cpu > self.thresholds['cpu_percent']:
                issues.append(f"High CPU usage: {avg_cpu:.1f}%")
        
        # Check memory usage
        if self.memory_samples:
            current_memory = self.memory_samples[-1]['percent']
            if current_memory > self.thresholds['memory_percent']:
                issues.append(f"High memory usage: {current_memory:.1f}%")
        
        # Check error rates
        for operation, error_count in self.error_counts.items():
            total_count = self.operation_counts[operation]
            if total_count > 0:
                error_rate = error_count / total_count
                if error_rate > self.thresholds['error_rate']:
                    issues.append(f"High error rate for {operation}: {error_rate:.1%}")
        
        # Check for stuck operations
        now = time.time()
        for op_id, start_time in list(self.active_operations.items()):
            duration = (now - start_time) * 1000
            if duration > self.thresholds['operation_time_ms'] * 5:  # 5x threshold
                operation_name = op_id.split('_')[0]
                issues.append(f"Stuck operation {operation_name}: {duration:.0f}ms")
        
        # Log issues
        if issues:
            self.dcp_manager.add_observation(
                'performance_issues',
                {
                    'issues': issues,
                    'timestamp': datetime.utcnow().isoformat()
                },
                source_agent='performance_profiler',
                priority=80
            )
    
    def get_operation_stats(self, operation: str) -> Dict[str, Any]:
        """Get statistics for a specific operation"""
        times = list(self.operation_times.get(operation, []))
        
        if not times:
            return {
                'count': 0,
                'avg_ms': 0,
                'min_ms': 0,
                'max_ms': 0,
                'p50_ms': 0,
                'p95_ms': 0,
                'p99_ms': 0,
                'error_rate': 0
            }
        
        times.sort()
        count = self.operation_counts[operation]
        errors = self.error_counts[operation]
        
        return {
            'count': count,
            'avg_ms': sum(times) / len(times),
            'min_ms': times[0],
            'max_ms': times[-1],
            'p50_ms': times[len(times) // 2],
            'p95_ms': times[int(len(times) * 0.95)],
            'p99_ms': times[int(len(times) * 0.99)],
            'error_rate': errors / count if count > 0 else 0
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        # Current metrics
        cpu_current = self.cpu_samples[-1] if self.cpu_samples else 0
        memory_current = self.memory_samples[-1] if self.memory_samples else {'percent': 0, 'rss': 0}
        
        # Averages
        cpu_avg = sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0
        memory_avg = sum(m['percent'] for m in self.memory_samples) / len(self.memory_samples) if self.memory_samples else 0
        
        return {
            'cpu': {
                'current': cpu_current,
                'average': cpu_avg,
                'samples': len(self.cpu_samples)
            },
            'memory': {
                'current_percent': memory_current['percent'],
                'current_mb': memory_current.get('rss', 0) / (1024 * 1024),
                'average_percent': memory_avg,
                'samples': len(self.memory_samples)
            },
            'operations': {
                'active': len(self.active_operations),
                'total': sum(self.operation_counts.values()),
                'unique': len(self.operation_counts)
            },
            'threads': threading.active_count()
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        # Collect all operation stats
        operations = {}
        for op in self.operation_counts:
            operations[op] = self.get_operation_stats(op)
        
        # Sort by total time
        sorted_ops = sorted(
            operations.items(),
            key=lambda x: x[1]['count'] * x[1]['avg_ms'],
            reverse=True
        )
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'system': self.get_system_stats(),
            'operations': dict(sorted_ops[:20]),  # Top 20 operations
            'bottlenecks': self._identify_bottlenecks(),
            'recommendations': self._generate_recommendations()
        }
    
    def _identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        # Slow operations
        for op, times in self.operation_times.items():
            if times:
                avg_time = sum(times) / len(times)
                if avg_time > self.thresholds['operation_time_ms']:
                    bottlenecks.append({
                        'type': 'slow_operation',
                        'operation': op,
                        'avg_ms': avg_time,
                        'impact': 'high' if avg_time > 5000 else 'medium'
                    })
        
        # High error rates
        for op, errors in self.error_counts.items():
            total = self.operation_counts[op]
            if total > 10:  # Minimum sample size
                error_rate = errors / total
                if error_rate > self.thresholds['error_rate']:
                    bottlenecks.append({
                        'type': 'high_errors',
                        'operation': op,
                        'error_rate': error_rate,
                        'impact': 'high' if error_rate > 0.25 else 'medium'
                    })
        
        return bottlenecks
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # Check CPU usage
        if self.cpu_samples:
            avg_cpu = sum(self.cpu_samples) / len(self.cpu_samples)
            if avg_cpu > 80:
                recommendations.append(
                    f"High CPU usage ({avg_cpu:.1f}%). Consider optimizing compute-intensive operations."
                )
        
        # Check memory usage
        if self.memory_samples:
            avg_memory = sum(m['percent'] for m in self.memory_samples) / len(self.memory_samples)
            if avg_memory > 70:
                recommendations.append(
                    f"High memory usage ({avg_memory:.1f}%). Consider implementing memory optimization."
                )
        
        # Check for slow operations
        slow_ops = []
        for op, times in self.operation_times.items():
            if times:
                avg_time = sum(times) / len(times)
                if avg_time > 2000:  # 2 seconds
                    slow_ops.append((op, avg_time))
        
        if slow_ops:
            slowest = max(slow_ops, key=lambda x: x[1])
            recommendations.append(
                f"Operation '{slowest[0]}' averaging {slowest[1]:.0f}ms. Consider optimization or caching."
            )
        
        return recommendations
    
    def _log_slow_operation(self, operation: str, duration_ms: float) -> None:
        """Log slow operation to DCP"""
        self.dcp_manager.add_observation(
            'slow_operation',
            {
                'operation': operation,
                'duration_ms': duration_ms,
                'threshold_ms': self.thresholds['operation_time_ms']
            },
            source_agent='performance_profiler',
            priority=70
        )
    
    def _update_dcp_metrics(self) -> None:
        """Update performance metrics in DCP"""
        try:
            # Calculate operation averages
            operation_averages = {}
            for op, times in self.operation_times.items():
                if times:
                    operation_averages[op] = {
                        'avg_ms': sum(times) / len(times),
                        'count': self.operation_counts[op],
                        'error_count': self.error_counts[op]
                    }
            
            # Update DCP
            self.dcp_manager.update_section(
                'performance.profiler',
                {
                    'thresholds': self.thresholds,
                    'historical_averages': operation_averages,
                    'last_updated': datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to update DCP metrics: {e}")