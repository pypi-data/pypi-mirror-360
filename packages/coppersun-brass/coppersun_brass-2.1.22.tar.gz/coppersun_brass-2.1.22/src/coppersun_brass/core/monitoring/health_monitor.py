"""Production health monitoring and alerting for Copper Alloy Brass."""
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"

@dataclass
class HealthCheck:
    """Individual health check result."""
    name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any]
    duration_ms: float
    timestamp: float

@dataclass
class Alert:
    """Health alert."""
    severity: str  # info, warning, error, critical
    component: str
    message: str
    details: Dict[str, Any]
    timestamp: float
    resolved: bool = False

class ProductionHealthMonitor:
    """
    Comprehensive health monitoring for production.
    
    Features:
    - Component health checks
    - Performance monitoring
    - Alert management
    - Metric aggregation
    - Historical tracking
    """
    
    def __init__(self, dcp_manager, event_bus, config: Optional[Dict] = None):
        self.dcp_manager = dcp_manager
        self.event_bus = event_bus
        self.config = config or {}
        
        # Configuration
        self.check_interval = self.config.get('check_interval', 60)  # seconds
        self.history_size = self.config.get('history_size', 1000)
        self.alert_cooldown = self.config.get('alert_cooldown', 300)  # 5 minutes
        
        # State
        self._checks: Dict[str, HealthCheck] = {}
        self._alerts: List[Alert] = []
        self._metrics_history: List[Dict] = []
        self._last_check = 0
        self._running = False
        self._check_thread = None
        self._lock = threading.RLock()
        
        # Thresholds
        self.thresholds = {
            'dcp_read_ms': 500,
            'dcp_write_ms': 1000,
            'dcp_size_mb': 50,
            'event_latency_ms': 100,
            'memory_usage_mb': 1024,
            'error_rate_percent': 5,
            'disk_usage_percent': 90,
            'cache_hit_rate': 0.7
        }
        
        # Update with custom thresholds
        self.thresholds.update(self.config.get('thresholds', {}))
        
        # Alert callbacks
        self._alert_handlers: List[Callable] = []
    
    def start(self):
        """Start health monitoring."""
        with self._lock:
            if self._running:
                return
            
            self._running = True
            self._check_thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True,
                name="Health-Monitor"
            )
            self._check_thread.start()
            logger.info("Health monitoring started")
    
    def stop(self):
        """Stop health monitoring."""
        with self._lock:
            self._running = False
            if self._check_thread:
                self._check_thread.join(timeout=5)
            logger.info("Health monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self._running:
            try:
                self._run_health_checks()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Health check error: {e}", exc_info=True)
                time.sleep(10)  # Brief pause on error
    
    def _run_health_checks(self):
        """Run all health checks."""
        start_time = time.time()
        checks = []
        
        # DCP Health
        checks.append(self._check_dcp_health())
        
        # Event Bus Health
        checks.append(self._check_event_bus_health())
        
        # System Resources
        checks.append(self._check_system_resources())
        
        # Application Performance
        checks.append(self._check_performance())
        
        # Store results
        with self._lock:
            for check in checks:
                self._checks[check.name] = check
                
                # Check for alerts
                self._evaluate_alerts(check)
            
            self._last_check = time.time()
            
            # Store metrics history
            self._store_metrics({
                'timestamp': self._last_check,
                'checks': [asdict(c) for c in checks],
                'overall_status': self._calculate_overall_status().value
            })
    
    def _check_dcp_health(self) -> HealthCheck:
        """Check DCP health."""
        start = time.time()
        status = HealthStatus.HEALTHY
        message = "DCP operating normally"
        details = {}
        
        try:
            # Get DCP metrics
            metrics = self.dcp_manager.get_metrics()
            details['metrics'] = metrics
            
            # Test read performance
            read_start = time.time()
            dcp_data = self.dcp_manager.read_dcp()
            read_ms = (time.time() - read_start) * 1000
            
            details['read_latency_ms'] = read_ms
            details['observation_count'] = len(dcp_data.get('observations', []))
            
            # Check file size
            dcp_size_mb = metrics.get('file_size_mb', 0)
            details['file_size_mb'] = dcp_size_mb
            
            # Check cache performance
            cache_hit_rate = metrics.get('cache_hit_rate', 0)
            details['cache_hit_rate'] = cache_hit_rate
            
            # Evaluate health
            if read_ms > self.thresholds['dcp_read_ms']:
                status = HealthStatus.DEGRADED
                message = f"DCP read slow: {read_ms:.0f}ms"
            
            if dcp_size_mb > self.thresholds['dcp_size_mb']:
                status = HealthStatus.UNHEALTHY
                message = f"DCP file too large: {dcp_size_mb:.1f}MB"
            
            if cache_hit_rate < self.thresholds['cache_hit_rate']:
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.DEGRADED
                message = f"Low cache hit rate: {cache_hit_rate:.1%}"
            
            # Check write queue
            queue_size = metrics.get('queue_size', 0)
            if queue_size > 100:
                status = HealthStatus.DEGRADED
                message = f"Write queue backed up: {queue_size} pending"
            
        except Exception as e:
            status = HealthStatus.CRITICAL
            message = f"DCP check failed: {e}"
            details['error'] = str(e)
        
        duration_ms = (time.time() - start) * 1000
        return HealthCheck(
            name="dcp",
            status=status,
            message=message,
            details=details,
            duration_ms=duration_ms,
            timestamp=time.time()
        )
    
    def _check_event_bus_health(self) -> HealthCheck:
        """Check Event Bus health."""
        start = time.time()
        
        try:
            # Get event bus health
            eb_health = self.event_bus.get_health_status()
            
            # Map status
            status_map = {
                'healthy': HealthStatus.HEALTHY,
                'degraded': HealthStatus.DEGRADED,
                'critical': HealthStatus.UNHEALTHY,
                'dead': HealthStatus.CRITICAL
            }
            
            status = status_map.get(eb_health['status'], HealthStatus.UNHEALTHY)
            message = f"Event bus: {eb_health['status']}"
            
            # Check circuit breaker
            if eb_health.get('circuit_breaker') == 'open':
                status = HealthStatus.CRITICAL
                message = "Event bus circuit breaker OPEN"
            
            # Check metrics
            metrics = eb_health.get('metrics', {})
            failure_rate = metrics.get('failure_rate', 0)
            
            if failure_rate > self.thresholds['error_rate_percent']:
                status = HealthStatus.UNHEALTHY
                message = f"High failure rate: {failure_rate:.1f}%"
            
            details = eb_health
            
        except Exception as e:
            status = HealthStatus.CRITICAL
            message = f"Event bus check failed: {e}"
            details = {'error': str(e)}
        
        duration_ms = (time.time() - start) * 1000
        return HealthCheck(
            name="event_bus",
            status=status,
            message=message,
            details=details,
            duration_ms=duration_ms,
            timestamp=time.time()
        )
    
    def _check_system_resources(self) -> HealthCheck:
        """Check system resources."""
        start = time.time()
        status = HealthStatus.HEALTHY
        message = "System resources normal"
        details = {}
        
        try:
            import psutil
            
            # Memory usage
            memory = psutil.virtual_memory()
            details['memory_percent'] = memory.percent
            details['memory_available_mb'] = memory.available / (1024 * 1024)
            
            # Process memory
            process = psutil.Process()
            process_memory_mb = process.memory_info().rss / (1024 * 1024)
            details['process_memory_mb'] = process_memory_mb
            
            # Disk usage
            disk = psutil.disk_usage(str(self.dcp_manager.project_path))
            details['disk_percent'] = disk.percent
            details['disk_free_gb'] = disk.free / (1024 * 1024 * 1024)
            
            # CPU usage (average over 0.1 second)
            details['cpu_percent'] = psutil.cpu_percent(interval=0.1)
            
            # Evaluate health
            if memory.percent > 90:
                status = HealthStatus.UNHEALTHY
                message = f"High memory usage: {memory.percent}%"
            elif memory.percent > 80:
                status = HealthStatus.DEGRADED
                message = f"Elevated memory usage: {memory.percent}%"
            
            if process_memory_mb > self.thresholds['memory_usage_mb']:
                status = HealthStatus.UNHEALTHY
                message = f"Process using too much memory: {process_memory_mb:.0f}MB"
            
            if disk.percent > self.thresholds['disk_usage_percent']:
                status = HealthStatus.UNHEALTHY
                message = f"Low disk space: {disk.percent}% used"
            
        except Exception as e:
            status = HealthStatus.DEGRADED
            message = f"Resource check partial: {e}"
            details['error'] = str(e)
        
        duration_ms = (time.time() - start) * 1000
        return HealthCheck(
            name="system_resources",
            status=status,
            message=message,
            details=details,
            duration_ms=duration_ms,
            timestamp=time.time()
        )
    
    def _check_performance(self) -> HealthCheck:
        """Check application performance."""
        start = time.time()
        status = HealthStatus.HEALTHY
        message = "Performance normal"
        details = {}
        
        try:
            # Aggregate recent performance metrics
            if self._metrics_history:
                recent_metrics = self._metrics_history[-10:]
                
                # Average check durations
                avg_durations = {}
                for metric in recent_metrics:
                    for check in metric.get('checks', []):
                        name = check['name']
                        duration = check['duration_ms']
                        if name not in avg_durations:
                            avg_durations[name] = []
                        avg_durations[name].append(duration)
                
                for name, durations in avg_durations.items():
                    avg = sum(durations) / len(durations)
                    details[f'{name}_avg_ms'] = avg
                
                # Check for degradation
                if any(avg > 1000 for avg in details.values()):
                    status = HealthStatus.DEGRADED
                    message = "Some operations are slow"
                
                # Count recent failures
                degraded_count = sum(
                    1 for m in recent_metrics 
                    if m.get('overall_status') in ['degraded', 'unhealthy', 'critical']
                )
                
                if degraded_count > 3:
                    status = HealthStatus.DEGRADED
                    message = f"Frequent health issues: {degraded_count} in last 10 checks"
            
        except Exception as e:
            details['error'] = str(e)
        
        duration_ms = (time.time() - start) * 1000
        return HealthCheck(
            name="performance",
            status=status,
            message=message,
            details=details,
            duration_ms=duration_ms,
            timestamp=time.time()
        )
    
    def _calculate_overall_status(self) -> HealthStatus:
        """Calculate overall system health."""
        with self._lock:
            if not self._checks:
                return HealthStatus.HEALTHY
            
            statuses = [check.status for check in self._checks.values()]
            
            if HealthStatus.CRITICAL in statuses:
                return HealthStatus.CRITICAL
            elif HealthStatus.UNHEALTHY in statuses:
                return HealthStatus.UNHEALTHY
            elif HealthStatus.DEGRADED in statuses:
                return HealthStatus.DEGRADED
            else:
                return HealthStatus.HEALTHY
    
    def get_status(self) -> Dict[str, Any]:
        """Get current health status."""
        with self._lock:
            overall = self._calculate_overall_status()
            
            return {
                'overall_status': overall.value,
                'last_check': self._last_check,
                'checks': {
                    name: asdict(check)
                    for name, check in self._checks.items()
                },
                'active_alerts': [
                    asdict(alert) for alert in self._alerts
                    if not alert.resolved
                ]
            }
    
    def _evaluate_alerts(self, check: HealthCheck):
        """Evaluate if check should trigger alerts."""
        # Check if we should alert
        if check.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
            # Check cooldown
            recent_alert = any(
                alert.component == check.name and 
                not alert.resolved and
                time.time() - alert.timestamp < self.alert_cooldown
                for alert in self._alerts
            )
            
            if not recent_alert:
                alert = Alert(
                    severity='critical' if check.status == HealthStatus.CRITICAL else 'error',
                    component=check.name,
                    message=check.message,
                    details=check.details,
                    timestamp=time.time()
                )
                
                self._alerts.append(alert)
                self._trigger_alert(alert)
                
                # Keep only recent alerts
                cutoff = time.time() - (24 * 60 * 60)  # 24 hours
                self._alerts = [a for a in self._alerts if a.timestamp > cutoff]
    
    def _trigger_alert(self, alert: Alert):
        """Trigger alert handlers."""
        for handler in self._alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler error: {e}")
    
    def add_alert_handler(self, handler: Callable):
        """Add alert handler callback."""
        self._alert_handlers.append(handler)
    
    def _store_metrics(self, metrics: Dict):
        """Store metrics in history."""
        with self._lock:
            self._metrics_history.append(metrics)
            
            # Trim history
            if len(self._metrics_history) > self.history_size:
                self._metrics_history = self._metrics_history[-self.history_size:]
    
    def get_metrics_history(self, hours: int = 1) -> List[Dict]:
        """Get metrics history for specified hours."""
        with self._lock:
            cutoff = time.time() - (hours * 60 * 60)
            return [
                m for m in self._metrics_history
                if m['timestamp'] > cutoff
            ]
    
    def resolve_alert(self, component: str):
        """Manually resolve alerts for a component."""
        with self._lock:
            for alert in self._alerts:
                if alert.component == component and not alert.resolved:
                    alert.resolved = True
                    logger.info(f"Resolved alert for component: {component}")

# Export classes
__all__ = ['ProductionHealthMonitor', 'HealthStatus', 'HealthCheck', 'Alert']