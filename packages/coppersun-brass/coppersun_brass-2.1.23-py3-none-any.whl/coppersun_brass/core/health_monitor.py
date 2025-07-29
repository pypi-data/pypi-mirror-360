"""Agent Health Monitoring System

General Staff Role: System Health Intelligence (G6-equivalent)
Provides comprehensive health monitoring for all Copper Alloy Brass agents,
enabling AI commanders to understand system status and reliability.

Persistent Value: Creates health history that helps identify
patterns, degradation, and reliability trends across agents.
"""

import time
import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .constants import AgentNames, FilePaths, PerformanceSettings, SystemMetadata

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Agent health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


@dataclass
class HealthMetric:
    """Individual health metric."""
    name: str
    value: Union[float, int, str, bool]
    unit: str = ""
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def status(self) -> HealthStatus:
        """Calculate status based on thresholds."""
        if not isinstance(self.value, (int, float)):
            return HealthStatus.UNKNOWN
        
        if self.threshold_critical and self.value >= self.threshold_critical:
            return HealthStatus.CRITICAL
        elif self.threshold_warning and self.value >= self.threshold_warning:
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY


@dataclass
class AgentHealth:
    """Complete health status for an agent."""
    agent_name: str
    status: HealthStatus
    last_heartbeat: datetime
    metrics: Dict[str, HealthMetric] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    uptime_seconds: float = 0.0
    response_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    
    @property
    def is_healthy(self) -> bool:
        """Check if agent is considered healthy."""
        return self.status in [HealthStatus.HEALTHY, HealthStatus.WARNING]
    
    @property
    def needs_attention(self) -> bool:
        """Check if agent needs immediate attention."""
        return self.status in [HealthStatus.CRITICAL, HealthStatus.OFFLINE]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'agent_name': self.agent_name,
            'status': self.status.value,
            'last_heartbeat': self.last_heartbeat.isoformat(),
            'metrics': {
                name: {
                    'name': metric.name,
                    'value': metric.value,
                    'unit': metric.unit,
                    'status': metric.status.value,
                    'timestamp': metric.timestamp.isoformat()
                }
                for name, metric in self.metrics.items()
            },
            'errors': self.errors,
            'warnings': self.warnings,
            'uptime_seconds': self.uptime_seconds,
            'response_time_ms': self.response_time_ms,
            'memory_usage_mb': self.memory_usage_mb,
            'cpu_usage_percent': self.cpu_usage_percent
        }


class HealthMonitor:
    """Central health monitoring system for all Copper Alloy Brass agents.
    
    This system provides:
    1. Real-time health status tracking
    2. Performance metrics collection
    3. Historical health data storage
    4. Alert generation for critical issues
    5. Health trends analysis
    """
    
    def __init__(self, project_path: str, dcp_manager=None):
        """Initialize health monitor.
        
        Args:
            project_path: Project root path
            dcp_manager: Optional DCP manager for health observations
        """
        self.project_path = Path(project_path)
        self.dcp_manager = dcp_manager
        
        # Health data storage
        self.health_file = self.project_path / FilePaths.CONFIG_DIR / "agent_health.json"
        self.health_file.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory health tracking
        self.agent_health: Dict[str, AgentHealth] = {}
        self.health_history: List[Dict[str, Any]] = []
        
        # Monitoring configuration
        self.heartbeat_timeout = 300  # 5 minutes
        self.history_retention_hours = 168  # 1 week
        self.max_history_entries = 10000
        
        # Threading
        self._lock = threading.RLock()
        self._monitoring_thread = None
        self._shutdown = threading.Event()
        
        # Load existing health data
        self._load_health_data()
        
        # Start monitoring
        self.start_monitoring()
    
    def register_agent(self, agent_name: str) -> None:
        """Register an agent for health monitoring.
        
        Args:
            agent_name: Name of the agent to monitor
        """
        with self._lock:
            if agent_name not in self.agent_health:
                self.agent_health[agent_name] = AgentHealth(
                    agent_name=agent_name,
                    status=HealthStatus.UNKNOWN,
                    last_heartbeat=datetime.now()
                )
                logger.info(f"Registered agent for health monitoring: {agent_name}")
    
    def heartbeat(self, agent_name: str, metrics: Optional[Dict[str, Any]] = None) -> None:
        """Record agent heartbeat with optional metrics.
        
        Args:
            agent_name: Name of the agent
            metrics: Optional performance metrics
        """
        with self._lock:
            # Register agent if not already registered
            if agent_name not in self.agent_health:
                self.register_agent(agent_name)
            
            agent_health = self.agent_health[agent_name]
            current_time = datetime.now()
            
            # Update basic health info
            agent_health.last_heartbeat = current_time
            agent_health.status = HealthStatus.HEALTHY
            
            # Update metrics if provided
            if metrics:
                self._update_agent_metrics(agent_health, metrics)
            
            # Calculate overall status based on metrics
            agent_health.status = self._calculate_agent_status(agent_health)
            
            logger.debug(f"Heartbeat received from {agent_name}: {agent_health.status.value}")
    
    def report_error(self, agent_name: str, error: str, is_critical: bool = False) -> None:
        """Report an error from an agent.
        
        Args:
            agent_name: Name of the agent
            error: Error description
            is_critical: Whether the error is critical
        """
        with self._lock:
            if agent_name not in self.agent_health:
                self.register_agent(agent_name)
            
            agent_health = self.agent_health[agent_name]
            
            if is_critical:
                agent_health.errors.append(f"{datetime.now().isoformat()}: {error}")
                agent_health.status = HealthStatus.CRITICAL
                # Keep only last 10 errors
                agent_health.errors = agent_health.errors[-10:]
            else:
                agent_health.warnings.append(f"{datetime.now().isoformat()}: {error}")
                if agent_health.status == HealthStatus.HEALTHY:
                    agent_health.status = HealthStatus.WARNING
                # Keep only last 20 warnings
                agent_health.warnings = agent_health.warnings[-20:]
            
            logger.warning(f"Error reported by {agent_name}: {error}")
            
            # Publish to DCP if available
            if self.dcp_manager:
                try:
                    self.dcp_manager.add_observation({
                        'type': 'agent_error' if is_critical else 'agent_warning',
                        'priority': 90 if is_critical else 60,
                        'summary': f"{agent_name}: {error}",
                        'details': {
                            'agent_name': agent_name,
                            'error_message': error,
                            'is_critical': is_critical,
                            'timestamp': datetime.now().isoformat()
                        }
                    }, source_agent='health_monitor')
                except Exception as e:
                    logger.error(f"Failed to publish error to DCP: {e}")
    
    def get_agent_health(self, agent_name: str) -> Optional[AgentHealth]:
        """Get health status for a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            AgentHealth object or None if not found
        """
        with self._lock:
            return self.agent_health.get(agent_name)
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health summary.
        
        Returns:
            Dictionary with system health information
        """
        with self._lock:
            now = datetime.now()
            healthy_agents = 0
            warning_agents = 0
            critical_agents = 0
            offline_agents = 0
            
            for agent_health in self.agent_health.values():
                # Check if agent is offline (no heartbeat in timeout period)
                if (now - agent_health.last_heartbeat).total_seconds() > self.heartbeat_timeout:
                    agent_health.status = HealthStatus.OFFLINE
                
                if agent_health.status == HealthStatus.HEALTHY:
                    healthy_agents += 1
                elif agent_health.status == HealthStatus.WARNING:
                    warning_agents += 1
                elif agent_health.status == HealthStatus.CRITICAL:
                    critical_agents += 1
                elif agent_health.status == HealthStatus.OFFLINE:
                    offline_agents += 1
            
            total_agents = len(self.agent_health)
            
            # Determine overall system status
            if critical_agents > 0 or offline_agents > total_agents // 2:
                system_status = HealthStatus.CRITICAL
            elif warning_agents > 0 or offline_agents > 0:
                system_status = HealthStatus.WARNING
            else:
                system_status = HealthStatus.HEALTHY
            
            return {
                'system_status': system_status.value,
                'total_agents': total_agents,
                'healthy_agents': healthy_agents,
                'warning_agents': warning_agents,
                'critical_agents': critical_agents,
                'offline_agents': offline_agents,
                'last_updated': now.isoformat(),
                'agents': {
                    name: health.to_dict()
                    for name, health in self.agent_health.items()
                }
            }
    
    def get_health_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get health trends over specified time period.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dictionary with trend analysis
        """
        with self._lock:
            cutoff = datetime.now() - timedelta(hours=hours)
            
            # Filter recent history
            recent_history = [
                entry for entry in self.health_history
                if datetime.fromisoformat(entry['timestamp']) > cutoff
            ]
            
            if not recent_history:
                return {'trends': 'insufficient_data', 'period_hours': hours}
            
            # Analyze trends for each agent
            agent_trends = {}
            for agent_name in self.agent_health.keys():
                agent_entries = [
                    entry for entry in recent_history
                    if entry.get('agent_name') == agent_name
                ]
                
                if agent_entries:
                    # Calculate availability
                    healthy_count = sum(
                        1 for entry in agent_entries
                        if entry.get('status') == HealthStatus.HEALTHY.value
                    )
                    availability = healthy_count / len(agent_entries) * 100
                    
                    # Calculate average response time
                    response_times = [
                        entry.get('response_time_ms', 0)
                        for entry in agent_entries
                        if entry.get('response_time_ms')
                    ]
                    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
                    
                    agent_trends[agent_name] = {
                        'availability_percent': availability,
                        'avg_response_time_ms': avg_response_time,
                        'total_errors': sum(len(entry.get('errors', [])) for entry in agent_entries),
                        'total_warnings': sum(len(entry.get('warnings', [])) for entry in agent_entries)
                    }
            
            return {
                'period_hours': hours,
                'analysis_timestamp': datetime.now().isoformat(),
                'agent_trends': agent_trends,
                'total_data_points': len(recent_history)
            }
    
    def start_monitoring(self) -> None:
        """Start the health monitoring background thread."""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            logger.warning("Health monitoring already running")
            return
        
        self._shutdown.clear()
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="HealthMonitor"
        )
        self._monitoring_thread.start()
        logger.info("Health monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop the health monitoring background thread."""
        self._shutdown.set()
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=10)
        logger.info("Health monitoring stopped")
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while not self._shutdown.is_set():
            try:
                with self._lock:
                    # Update agent statuses based on heartbeat timeouts
                    self._check_heartbeat_timeouts()
                    
                    # Save health snapshot to history
                    self._save_health_snapshot()
                    
                    # Cleanup old history
                    self._cleanup_old_history()
                    
                    # Save to disk
                    self._save_health_data()
                
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
            
            # Wait for next check
            self._shutdown.wait(60)  # Check every minute
    
    def _update_agent_metrics(self, agent_health: AgentHealth, metrics: Dict[str, Any]) -> None:
        """Update agent metrics from heartbeat data."""
        # Standard performance metrics
        if 'response_time_ms' in metrics:
            agent_health.response_time_ms = float(metrics['response_time_ms'])
            agent_health.metrics['response_time'] = HealthMetric(
                name='response_time',
                value=agent_health.response_time_ms,
                unit='ms',
                threshold_warning=1000.0,  # 1 second
                threshold_critical=5000.0  # 5 seconds
            )
        
        if 'memory_usage_mb' in metrics:
            agent_health.memory_usage_mb = float(metrics['memory_usage_mb'])
            agent_health.metrics['memory_usage'] = HealthMetric(
                name='memory_usage',
                value=agent_health.memory_usage_mb,
                unit='MB',
                threshold_warning=512.0,
                threshold_critical=1024.0
            )
        
        if 'cpu_usage_percent' in metrics:
            agent_health.cpu_usage_percent = float(metrics['cpu_usage_percent'])
            agent_health.metrics['cpu_usage'] = HealthMetric(
                name='cpu_usage',
                value=agent_health.cpu_usage_percent,
                unit='%',
                threshold_warning=70.0,
                threshold_critical=90.0
            )
        
        if 'uptime_seconds' in metrics:
            agent_health.uptime_seconds = float(metrics['uptime_seconds'])
        
        # Agent-specific metrics
        for key, value in metrics.items():
            if key not in ['response_time_ms', 'memory_usage_mb', 'cpu_usage_percent', 'uptime_seconds']:
                if isinstance(value, (int, float, str, bool)):
                    agent_health.metrics[key] = HealthMetric(
                        name=key,
                        value=value
                    )
    
    def _calculate_agent_status(self, agent_health: AgentHealth) -> HealthStatus:
        """Calculate overall agent status based on metrics."""
        # If there are recent critical errors, mark as critical
        if agent_health.errors:
            return HealthStatus.CRITICAL
        
        # Check if any metrics are in critical state
        critical_metrics = [
            metric for metric in agent_health.metrics.values()
            if metric.status == HealthStatus.CRITICAL
        ]
        if critical_metrics:
            return HealthStatus.CRITICAL
        
        # Check if any metrics are in warning state
        warning_metrics = [
            metric for metric in agent_health.metrics.values()
            if metric.status == HealthStatus.WARNING
        ]
        if warning_metrics or agent_health.warnings:
            return HealthStatus.WARNING
        
        return HealthStatus.HEALTHY
    
    def _check_heartbeat_timeouts(self) -> None:
        """Check for agents that haven't sent heartbeats recently."""
        now = datetime.now()
        
        for agent_health in self.agent_health.values():
            time_since_heartbeat = (now - agent_health.last_heartbeat).total_seconds()
            
            if time_since_heartbeat > self.heartbeat_timeout:
                if agent_health.status != HealthStatus.OFFLINE:
                    agent_health.status = HealthStatus.OFFLINE
                    logger.warning(
                        f"Agent {agent_health.agent_name} marked offline: "
                        f"no heartbeat for {time_since_heartbeat:.1f}s"
                    )
    
    def _save_health_snapshot(self) -> None:
        """Save current health status to history."""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'agents': {
                name: health.to_dict()
                for name, health in self.agent_health.items()
            }
        }
        
        self.health_history.append(snapshot)
    
    def _cleanup_old_history(self) -> None:
        """Remove old history entries."""
        # Remove entries older than retention period
        cutoff = datetime.now() - timedelta(hours=self.history_retention_hours)
        self.health_history = [
            entry for entry in self.health_history
            if datetime.fromisoformat(entry['timestamp']) > cutoff
        ]
        
        # Limit total entries
        if len(self.health_history) > self.max_history_entries:
            self.health_history = self.health_history[-self.max_history_entries:]
    
    def _save_health_data(self) -> None:
        """Save health data to disk."""
        try:
            health_data = {
                'agents': {
                    name: health.to_dict()
                    for name, health in self.agent_health.items()
                },
                'last_updated': datetime.now().isoformat(),
                'monitoring_config': {
                    'heartbeat_timeout': self.heartbeat_timeout,
                    'history_retention_hours': self.history_retention_hours
                }
            }
            
            with open(self.health_file, 'w') as f:
                json.dump(health_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save health data: {e}")
    
    def _load_health_data(self) -> None:
        """Load health data from disk."""
        try:
            if self.health_file.exists():
                with open(self.health_file, 'r') as f:
                    health_data = json.load(f)
                
                # Restore agent health
                for agent_name, agent_data in health_data.get('agents', {}).items():
                    agent_health = AgentHealth(
                        agent_name=agent_data['agent_name'],
                        status=HealthStatus(agent_data['status']),
                        last_heartbeat=datetime.fromisoformat(agent_data['last_heartbeat']),
                        errors=agent_data.get('errors', []),
                        warnings=agent_data.get('warnings', []),
                        uptime_seconds=agent_data.get('uptime_seconds', 0.0),
                        response_time_ms=agent_data.get('response_time_ms', 0.0),
                        memory_usage_mb=agent_data.get('memory_usage_mb', 0.0),
                        cpu_usage_percent=agent_data.get('cpu_usage_percent', 0.0)
                    )
                    
                    # Restore metrics
                    for metric_name, metric_data in agent_data.get('metrics', {}).items():
                        agent_health.metrics[metric_name] = HealthMetric(
                            name=metric_data['name'],
                            value=metric_data['value'],
                            unit=metric_data.get('unit', ''),
                            timestamp=datetime.fromisoformat(metric_data['timestamp'])
                        )
                    
                    self.agent_health[agent_name] = agent_health
                
                logger.info(f"Loaded health data for {len(self.agent_health)} agents")
                
        except Exception as e:
            logger.warning(f"Failed to load health data: {e}")


# Convenience functions
def create_health_monitor(project_path: str, dcp_manager=None) -> HealthMonitor:
    """Create and start a health monitor.
    
    Args:
        project_path: Project root path
        dcp_manager: Optional DCP manager
        
    Returns:
        Configured HealthMonitor instance
    """
    return HealthMonitor(project_path, dcp_manager)


def get_system_health_summary(monitor: HealthMonitor) -> str:
    """Get a human-readable system health summary.
    
    Args:
        monitor: HealthMonitor instance
        
    Returns:
        Formatted health summary string
    """
    health = monitor.get_system_health()
    
    status_emoji = {
        'healthy': '✅',
        'warning': '⚠️',
        'critical': '🚨',
        'offline': '📴'
    }
    
    emoji = status_emoji.get(health['system_status'], '❓')
    
    summary = f"{emoji} System Status: {health['system_status'].upper()}\n"
    summary += f"Agents: {health['healthy_agents']} healthy, "
    summary += f"{health['warning_agents']} warning, "
    summary += f"{health['critical_agents']} critical, "
    summary += f"{health['offline_agents']} offline\n"
    summary += f"Total: {health['total_agents']} agents\n"
    summary += f"Last Updated: {health['last_updated']}"
    
    return summary