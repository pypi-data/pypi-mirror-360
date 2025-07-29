"""Health monitoring API endpoints for Copper Alloy Brass production deployment.

This module provides REST API endpoints for health monitoring, metrics,
and status reporting in production environments.
"""

import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from coppersun_brass.core.monitoring.health_monitor import ProductionHealthMonitor, HealthStatus
from coppersun_brass.core.config_loader import get_config, BrassConfig
from coppersun_brass.core.health_monitor import HealthMonitor as SystemHealthMonitor

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: float
    checks: Dict[str, Dict[str, Any]]
    message: str
    version: str = "1.0.0"


class MetricsResponse(BaseModel):
    """Metrics response model."""
    timestamp: float
    metrics: Dict[str, Any]
    period_minutes: int


class AlertResponse(BaseModel):
    """Alert response model."""
    alerts: List[Dict[str, Any]]
    total: int
    unresolved: int


# Dependency to get health monitor
_health_monitor: Optional[SystemHealthMonitor] = None
_production_monitor: Optional[ProductionHealthMonitor] = None


def get_health_monitor() -> SystemHealthMonitor:
    """Get or create health monitor instance."""
    global _health_monitor
    
    if _health_monitor is None:
        config = get_config()
        _health_monitor = SystemHealthMonitor(
            db_path=config.storage.path,
            config={
                'memory_alert_mb': config.monitoring.memory_alert_mb,
                'disk_alert_percent': config.monitoring.disk_alert_percent,
                'error_rate_alert': config.monitoring.error_rate_alert_percent / 100,
                'response_time_alert_ms': config.monitoring.response_time_alert_ms
            }
        )
        # Start background monitoring
        _health_monitor.start_monitoring(interval_seconds=config.monitoring.health_check_interval)
        
    return _health_monitor


def get_production_monitor() -> Optional[ProductionHealthMonitor]:
    """Get production monitor if available."""
    global _production_monitor
    return _production_monitor


def set_production_monitor(monitor: ProductionHealthMonitor) -> None:
    """Set production monitor instance."""
    global _production_monitor
    _production_monitor = monitor


@router.get("/", response_model=HealthResponse)
async def health_check(
    force: bool = False,
    monitor: SystemHealthMonitor = Depends(get_health_monitor)
) -> HealthResponse:
    """Main health check endpoint.
    
    Returns overall system health status and individual component checks.
    """
    try:
        # Get health status
        status = monitor.check_health(force=force)
        
        return HealthResponse(
            status=status.status,
            timestamp=status.timestamp,
            checks=status.checks,
            message=status.message
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unknown",
            timestamp=time.time(),
            checks={},
            message=f"Health check error: {str(e)}"
        )


@router.get("/live")
async def liveness_probe() -> Dict[str, str]:
    """Kubernetes liveness probe endpoint.
    
    Returns 200 if the service is alive.
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}


@router.get("/ready")
async def readiness_probe(
    monitor: SystemHealthMonitor = Depends(get_health_monitor)
) -> Dict[str, Any]:
    """Kubernetes readiness probe endpoint.
    
    Returns 200 if the service is ready to accept traffic.
    Returns 503 if the service is not ready.
    """
    try:
        status = monitor.check_health()
        
        if status.is_critical:
            raise HTTPException(
                status_code=503,
                detail={
                    "status": "not_ready",
                    "reason": status.message,
                    "checks": status.checks
                }
            )
            
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "health": status.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "reason": f"Health check error: {str(e)}"
            }
        )


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    minutes: int = 60,
    monitor: SystemHealthMonitor = Depends(get_health_monitor)
) -> MetricsResponse:
    """Get performance metrics for specified time period.
    
    Args:
        minutes: Number of minutes of history to return (max 1440/24 hours)
    """
    # Limit to 24 hours
    minutes = min(minutes, 1440)
    
    try:
        # Get metrics history
        metrics_history = monitor.get_metrics_history(minutes=minutes)
        
        if not metrics_history:
            return MetricsResponse(
                timestamp=time.time(),
                metrics={},
                period_minutes=minutes
            )
            
        # Aggregate metrics
        aggregated = {
            'cpu_percent': {
                'avg': sum(m.cpu_percent for m in metrics_history) / len(metrics_history),
                'max': max(m.cpu_percent for m in metrics_history),
                'min': min(m.cpu_percent for m in metrics_history)
            },
            'memory_mb': {
                'avg': sum(m.memory_used_mb for m in metrics_history) / len(metrics_history),
                'max': max(m.memory_used_mb for m in metrics_history),
                'min': min(m.memory_used_mb for m in metrics_history)
            },
            'response_time_ms': {
                'avg': sum(m.response_time_ms for m in metrics_history) / len(metrics_history),
                'max': max(m.response_time_ms for m in metrics_history),
                'min': min(m.response_time_ms for m in metrics_history)
            },
            'error_count': {
                'total': sum(m.error_count for m in metrics_history),
                'avg': sum(m.error_count for m in metrics_history) / len(metrics_history)
            },
            'db_size_mb': metrics_history[-1].db_size_mb if metrics_history else 0,
            'samples': len(metrics_history)
        }
        
        return MetricsResponse(
            timestamp=time.time(),
            metrics=aggregated,
            period_minutes=minutes
        )
        
    except Exception as e:
        logger.error(f"Metrics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts", response_model=AlertResponse)
async def get_alerts(
    unresolved_only: bool = False,
    prod_monitor: Optional[ProductionHealthMonitor] = Depends(get_production_monitor)
) -> AlertResponse:
    """Get active alerts from production monitor.
    
    Args:
        unresolved_only: Only return unresolved alerts
    """
    if not prod_monitor:
        return AlertResponse(alerts=[], total=0, unresolved=0)
        
    try:
        all_alerts = prod_monitor.get_alerts()
        
        if unresolved_only:
            alerts = [a for a in all_alerts if not a.resolved]
        else:
            alerts = all_alerts
            
        # Convert to dict format
        alert_dicts = [
            {
                'severity': alert.severity,
                'component': alert.component,
                'message': alert.message,
                'details': alert.details,
                'timestamp': alert.timestamp,
                'resolved': alert.resolved
            }
            for alert in alerts
        ]
        
        unresolved_count = sum(1 for a in all_alerts if not a.resolved)
        
        return AlertResponse(
            alerts=alert_dicts,
            total=len(all_alerts),
            unresolved=unresolved_count
        )
        
    except Exception as e:
        logger.error(f"Alert retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/metrics/record")
async def record_metric(
    metric_type: str,
    value: float,
    monitor: SystemHealthMonitor = Depends(get_health_monitor)
) -> Dict[str, str]:
    """Record a custom metric.
    
    Args:
        metric_type: Type of metric (response_time, error)
        value: Metric value
    """
    try:
        if metric_type == "response_time":
            monitor.record_response_time(value)
        elif metric_type == "error":
            monitor.record_error(str(value))
        else:
            raise ValueError(f"Unknown metric type: {metric_type}")
            
        return {"status": "recorded", "metric_type": metric_type, "value": value}
        
    except Exception as e:
        logger.error(f"Metric recording failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status/detailed")
async def detailed_status(
    monitor: SystemHealthMonitor = Depends(get_health_monitor),
    prod_monitor: Optional[ProductionHealthMonitor] = Depends(get_production_monitor)
) -> Dict[str, Any]:
    """Get detailed status information including all health checks and metrics."""
    try:
        # System health
        system_health = monitor.check_health(force=True)
        
        # Production health if available
        prod_health = None
        if prod_monitor:
            prod_health = prod_monitor.get_status()
            
        # Recent metrics
        recent_metrics = monitor.get_metrics_history(minutes=5)
        
        return {
            "timestamp": time.time(),
            "system_health": system_health.to_dict(),
            "production_health": prod_health,
            "recent_metrics": [m.to_dict() for m in recent_metrics[-10:]],  # Last 10 metrics
            "config": {
                "environment": get_config().environment,
                "version": get_config().version
            }
        }
        
    except Exception as e:
        logger.error(f"Detailed status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Prometheus metrics endpoint
@router.get("/metrics/prometheus")
async def prometheus_metrics(
    monitor: SystemHealthMonitor = Depends(get_health_monitor)
) -> Response:
    """Export metrics in Prometheus format."""
    try:
        # Get current health status
        status = monitor.check_health()
        
        # Get latest metrics
        metrics_history = monitor.get_metrics_history(minutes=1)
        latest_metrics = metrics_history[-1] if metrics_history else None
        
        # Build Prometheus format
        lines = []
        
        # Health status (1 = healthy, 0 = not healthy)
        health_value = 1 if status.is_healthy else 0
        lines.append(f'brass_health_status{{status="{status.status}"}} {health_value}')
        
        if latest_metrics:
            # System metrics
            lines.append(f'brass_cpu_percent {latest_metrics.cpu_percent:.2f}')
            lines.append(f'brass_memory_used_mb {latest_metrics.memory_used_mb:.2f}')
            lines.append(f'brass_memory_percent {latest_metrics.memory_percent:.2f}')
            lines.append(f'brass_disk_used_gb {latest_metrics.disk_used_gb:.2f}')
            lines.append(f'brass_disk_percent {latest_metrics.disk_percent:.2f}')
            lines.append(f'brass_active_threads {latest_metrics.active_threads}')
            lines.append(f'brass_db_size_mb {latest_metrics.db_size_mb:.2f}')
            lines.append(f'brass_response_time_ms {latest_metrics.response_time_ms:.2f}')
            lines.append(f'brass_error_count {latest_metrics.error_count}')
            
        # Component health
        for check_name, check_data in status.checks.items():
            check_health = 1 if check_data.get('status') == 'healthy' else 0
            lines.append(f'brass_component_health{{component="{check_name}"}} {check_health}')
            
        content = '\n'.join(lines)
        
        return Response(
            content=content,
            media_type="text/plain; version=0.0.4"
        )
        
    except Exception as e:
        logger.error(f"Prometheus metrics export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))