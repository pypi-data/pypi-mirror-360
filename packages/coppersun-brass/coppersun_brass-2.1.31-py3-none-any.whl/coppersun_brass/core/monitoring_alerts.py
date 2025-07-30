"""Basic Monitoring and Alerts System

General Staff Role: Operations Center (G3) - System Monitoring
Provides basic monitoring capabilities and alert generation for Copper Alloy Brass
system events, enabling proactive response to issues and trends.

Persistent Value: Creates monitoring history that helps identify
system patterns, performance trends, and potential issues before
they become critical problems.
"""

import json
import time
import uuid
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .constants import FilePaths, PerformanceSettings
from .health_monitor import HealthMonitor, HealthStatus

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertType(Enum):
    """Types of alerts."""
    HEALTH = "health"
    PERFORMANCE = "performance"
    ERROR = "error"
    CAPACITY = "capacity"
    TREND = "trend"
    SECURITY = "security"
    SYSTEM = "system"


@dataclass
class MonitoringAlert:
    """Represents a monitoring alert."""
    id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    source: str  # Component that generated the alert
    created_at: datetime
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    @property
    def is_active(self) -> bool:
        """Check if alert is still active."""
        return self.resolved_at is None
    
    @property
    def duration_minutes(self) -> float:
        """Get alert duration in minutes."""
        end_time = self.resolved_at or datetime.now()
        return (end_time - self.created_at).total_seconds() / 60
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'alert_type': self.alert_type.value,
            'severity': self.severity.value,
            'title': self.title,
            'description': self.description,
            'source': self.source,
            'created_at': self.created_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'is_active': self.is_active,
            'duration_minutes': self.duration_minutes,
            'metadata': self.metadata,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MonitoringAlert':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            alert_type=AlertType(data['alert_type']),
            severity=AlertSeverity(data['severity']),
            title=data['title'],
            description=data['description'],
            source=data['source'],
            created_at=datetime.fromisoformat(data['created_at']),
            resolved_at=datetime.fromisoformat(data['resolved_at']) if data.get('resolved_at') else None,
            metadata=data.get('metadata', {}),
            tags=data.get('tags', [])
        )


@dataclass
class AlertRule:
    """Defines rules for generating alerts."""
    id: str
    name: str
    description: str
    alert_type: AlertType
    severity: AlertSeverity
    condition: str  # Human-readable condition description
    threshold: Dict[str, Any]  # Threshold values
    enabled: bool = True
    cooldown_minutes: int = 15  # Minimum time between alerts of same type
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'alert_type': self.alert_type.value,
            'severity': self.severity.value,
            'condition': self.condition,
            'threshold': self.threshold,
            'enabled': self.enabled,
            'cooldown_minutes': self.cooldown_minutes,
            'tags': self.tags
        }


@dataclass
class SystemMetrics:
    """Current system metrics snapshot."""
    timestamp: datetime
    agent_count: int
    healthy_agents: int
    warning_agents: int
    critical_agents: int
    offline_agents: int
    total_observations: int
    recent_errors: int
    avg_response_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'agent_count': self.agent_count,
            'healthy_agents': self.healthy_agents,
            'warning_agents': self.warning_agents,
            'critical_agents': self.critical_agents,
            'offline_agents': self.offline_agents,
            'total_observations': self.total_observations,
            'recent_errors': self.recent_errors,
            'avg_response_time': self.avg_response_time,
            'memory_usage_mb': self.memory_usage_mb,
            'cpu_usage_percent': self.cpu_usage_percent
        }


class MonitoringAlertsSystem:
    """Basic monitoring and alerts system for Copper Alloy Brass.
    
    This system provides:
    1. Real-time system monitoring
    2. Configurable alert rules
    3. Alert generation and tracking
    4. Trend analysis and alerts
    5. System health dashboards
    """
    
    def __init__(self, project_path: str, health_monitor: Optional[HealthMonitor] = None, dcp_manager=None):
        """Initialize monitoring and alerts system.
        
        Args:
            project_path: Project root path
            health_monitor: Optional health monitor instance
            dcp_manager: Optional DCP manager for publishing alerts
        """
        self.project_path = Path(project_path)
        self.health_monitor = health_monitor
        self.dcp_manager = dcp_manager
        
        # Storage paths
        self.alerts_file = self.project_path / FilePaths.CONFIG_DIR / "monitoring_alerts.json"
        self.rules_file = self.project_path / FilePaths.CONFIG_DIR / "alert_rules.json"
        self.metrics_file = self.project_path / FilePaths.CONFIG_DIR / "system_metrics.json"
        
        # Ensure storage directory exists
        self.alerts_file.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory storage
        self.active_alerts: Dict[str, MonitoringAlert] = {}
        self.alert_history: List[MonitoringAlert] = []
        self.alert_rules: Dict[str, AlertRule] = {}
        self.metrics_history: List[SystemMetrics] = []
        
        # Alert callbacks
        self.alert_callbacks: List[Callable[[MonitoringAlert], None]] = []
        
        # Configuration
        self.max_alert_history = 1000
        self.max_metrics_history = 500
        self.metrics_retention_hours = 168  # 1 week
        
        # Threading
        self._lock = threading.RLock()
        self._monitoring_thread = None
        self._shutdown = threading.Event()
        
        # Load existing data
        self._load_data()
        
        # Setup default alert rules
        self._setup_default_rules()
        
        # Start monitoring
        self.start_monitoring()
    
    def add_alert_rule(self, rule: AlertRule) -> None:
        """Add a new alert rule.
        
        Args:
            rule: Alert rule to add
        """
        with self._lock:
            self.alert_rules[rule.id] = rule
            self._save_rules()
            logger.info(f"Added alert rule: {rule.name}")
    
    def remove_alert_rule(self, rule_id: str) -> bool:
        """Remove an alert rule.
        
        Args:
            rule_id: ID of rule to remove
            
        Returns:
            True if rule was removed
        """
        with self._lock:
            if rule_id in self.alert_rules:
                del self.alert_rules[rule_id]
                self._save_rules()
                logger.info(f"Removed alert rule: {rule_id}")
                return True
            return False
    
    def create_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        description: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """Create a new alert.
        
        Args:
            alert_type: Type of alert
            severity: Alert severity
            title: Alert title
            description: Alert description
            source: Source component
            metadata: Additional metadata
            tags: Alert tags
            
        Returns:
            Alert ID
        """
        with self._lock:
            alert_id = f"alert_{uuid.uuid4().hex[:8]}_{int(time.time())}"
            
            alert = MonitoringAlert(
                id=alert_id,
                alert_type=alert_type,
                severity=severity,
                title=title,
                description=description,
                source=source,
                created_at=datetime.now(),
                metadata=metadata or {},
                tags=tags or []
            )
            
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
            
            # Trigger callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Alert callback failed: {e}")
            
            # Publish to DCP if available
            if self.dcp_manager:
                try:
                    self.dcp_manager.add_observation({
                        'type': 'monitoring_alert',
                        'priority': self._severity_to_priority(severity),
                        'summary': f"{severity.value.upper()}: {title}",
                        'details': alert.to_dict()
                    }, source_agent='monitoring_system')
                except Exception as e:
                    logger.error(f"Failed to publish alert to DCP: {e}")
            
            self._save_alerts()
            
            logger.warning(f"🚨 {severity.value.upper()} Alert: {title} (Source: {source})")
            
            return alert_id
    
    def resolve_alert(self, alert_id: str, resolved_by: str = "system") -> bool:
        """Resolve an active alert.
        
        Args:
            alert_id: Alert ID to resolve
            resolved_by: Who/what resolved the alert
            
        Returns:
            True if alert was resolved
        """
        with self._lock:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved_at = datetime.now()
                alert.metadata['resolved_by'] = resolved_by
                
                # Remove from active alerts
                del self.active_alerts[alert_id]
                
                self._save_alerts()
                
                logger.info(f"✅ Resolved alert: {alert.title}")
                return True
            
            return False
    
    def get_active_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        alert_type: Optional[AlertType] = None,
        source: Optional[str] = None
    ) -> List[MonitoringAlert]:
        """Get active alerts with optional filtering.
        
        Args:
            severity: Filter by severity
            alert_type: Filter by alert type
            source: Filter by source
            
        Returns:
            List of matching active alerts
        """
        with self._lock:
            alerts = list(self.active_alerts.values())
            
            if severity:
                alerts = [a for a in alerts if a.severity == severity]
            
            if alert_type:
                alerts = [a for a in alerts if a.alert_type == alert_type]
            
            if source:
                alerts = [a for a in alerts if a.source == source]
            
            # Sort by severity and creation time
            severity_order = {
                AlertSeverity.EMERGENCY: 4,
                AlertSeverity.CRITICAL: 3,
                AlertSeverity.WARNING: 2,
                AlertSeverity.INFO: 1
            }
            
            alerts.sort(
                key=lambda a: (severity_order.get(a.severity, 0), a.created_at),
                reverse=True
            )
            
            return alerts
    
    def get_alert_history(
        self,
        hours: int = 24,
        severity: Optional[AlertSeverity] = None
    ) -> List[MonitoringAlert]:
        """Get alert history for specified time period.
        
        Args:
            hours: Number of hours to look back
            severity: Optional severity filter
            
        Returns:
            List of alerts from the time period
        """
        with self._lock:
            cutoff = datetime.now() - timedelta(hours=hours)
            
            alerts = [
                alert for alert in self.alert_history
                if alert.created_at > cutoff
            ]
            
            if severity:
                alerts = [a for a in alerts if a.severity == severity]
            
            return sorted(alerts, key=lambda a: a.created_at, reverse=True)
    
    def get_system_metrics(self) -> Optional[SystemMetrics]:
        """Get current system metrics.
        
        Returns:
            Current system metrics or None if unavailable
        """
        if not self.health_monitor:
            return None
        
        try:
            system_health = self.health_monitor.get_system_health()
            
            # Calculate averages
            avg_response_time = 0.0
            total_memory = 0.0
            total_cpu = 0.0
            agent_count = 0
            
            for agent_data in system_health.get('agents', {}).values():
                agent_count += 1
                avg_response_time += agent_data.get('response_time_ms', 0)
                total_memory += agent_data.get('memory_usage_mb', 0)
                total_cpu += agent_data.get('cpu_usage_percent', 0)
            
            if agent_count > 0:
                avg_response_time /= agent_count
                total_memory /= agent_count
                total_cpu /= agent_count
            
            # Count recent errors (last hour)
            recent_errors = 0
            cutoff = datetime.now() - timedelta(hours=1)
            for alert in self.alert_history:
                if (alert.created_at > cutoff and 
                    alert.alert_type == AlertType.ERROR):
                    recent_errors += 1
            
            # Get total observations from DCP
            total_observations = 0
            if self.dcp_manager:
                try:
                    dcp_data = self.dcp_manager.read_dcp()
                    total_observations = len(dcp_data.get('observations', []))
                except:
                    pass
            
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                agent_count=system_health.get('total_agents', 0),
                healthy_agents=system_health.get('healthy_agents', 0),
                warning_agents=system_health.get('warning_agents', 0),
                critical_agents=system_health.get('critical_agents', 0),
                offline_agents=system_health.get('offline_agents', 0),
                total_observations=total_observations,
                recent_errors=recent_errors,
                avg_response_time=avg_response_time,
                memory_usage_mb=total_memory,
                cpu_usage_percent=total_cpu
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return None
    
    def add_alert_callback(self, callback: Callable[[MonitoringAlert], None]) -> None:
        """Add a callback to be called when alerts are created.
        
        Args:
            callback: Function to call with new alerts
        """
        self.alert_callbacks.append(callback)
    
    def start_monitoring(self) -> None:
        """Start the monitoring background thread."""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            logger.warning("Monitoring already running")
            return
        
        self._shutdown.clear()
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="MonitoringAlerts"
        )
        self._monitoring_thread.start()
        logger.info("Monitoring and alerts started")
    
    def stop_monitoring(self) -> None:
        """Stop the monitoring background thread."""
        self._shutdown.set()
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=10)
        logger.info("Monitoring and alerts stopped")
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while not self._shutdown.is_set():
            try:
                # Collect current metrics
                metrics = self.get_system_metrics()
                if metrics:
                    with self._lock:
                        self.metrics_history.append(metrics)
                        
                        # Cleanup old metrics
                        cutoff = datetime.now() - timedelta(hours=self.metrics_retention_hours)
                        self.metrics_history = [
                            m for m in self.metrics_history
                            if m.timestamp > cutoff
                        ]
                        
                        # Limit total entries
                        if len(self.metrics_history) > self.max_metrics_history:
                            self.metrics_history = self.metrics_history[-self.max_metrics_history:]
                    
                    # Check alert rules
                    self._check_alert_rules(metrics)
                
                # Auto-resolve old alerts
                self._auto_resolve_alerts()
                
                # Save data periodically
                self._save_metrics()
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            # Wait for next check (60 seconds)
            self._shutdown.wait(60)
    
    def _check_alert_rules(self, metrics: SystemMetrics) -> None:
        """Check current metrics against alert rules."""
        with self._lock:
            for rule in self.alert_rules.values():
                if not rule.enabled:
                    continue
                
                try:
                    should_alert = self._evaluate_rule(rule, metrics)
                    
                    if should_alert:
                        # Check cooldown
                        recent_alerts = [
                            alert for alert in self.alert_history
                            if (alert.alert_type == rule.alert_type and
                                alert.source == f"rule_{rule.id}" and
                                (datetime.now() - alert.created_at).total_seconds() < rule.cooldown_minutes * 60)
                        ]
                        
                        if not recent_alerts:
                            # Create alert
                            self.create_alert(
                                alert_type=rule.alert_type,
                                severity=rule.severity,
                                title=rule.name,
                                description=f"{rule.description} (Current: {self._format_rule_values(rule, metrics)})",
                                source=f"rule_{rule.id}",
                                metadata={
                                    'rule_id': rule.id,
                                    'threshold': rule.threshold,
                                    'current_metrics': metrics.to_dict()
                                },
                                tags=rule.tags
                            )
                
                except Exception as e:
                    logger.error(f"Failed to evaluate rule {rule.id}: {e}")
    
    def _evaluate_rule(self, rule: AlertRule, metrics: SystemMetrics) -> bool:
        """Evaluate if a rule should trigger an alert.
        
        Args:
            rule: Alert rule to evaluate
            metrics: Current metrics
            
        Returns:
            True if rule should trigger
        """
        threshold = rule.threshold
        
        # Health-based rules
        if rule.alert_type == AlertType.HEALTH:
            if 'critical_agents_max' in threshold:
                return metrics.critical_agents > threshold['critical_agents_max']
            if 'offline_agents_max' in threshold:
                return metrics.offline_agents > threshold['offline_agents_max']
            if 'healthy_agents_min' in threshold:
                return metrics.healthy_agents < threshold['healthy_agents_min']
        
        # Performance-based rules
        elif rule.alert_type == AlertType.PERFORMANCE:
            if 'response_time_max' in threshold:
                return metrics.avg_response_time > threshold['response_time_max']
            if 'memory_usage_max' in threshold:
                return metrics.memory_usage_mb > threshold['memory_usage_max']
            if 'cpu_usage_max' in threshold:
                return metrics.cpu_usage_percent > threshold['cpu_usage_max']
        
        # Error-based rules
        elif rule.alert_type == AlertType.ERROR:
            if 'recent_errors_max' in threshold:
                return metrics.recent_errors > threshold['recent_errors_max']
        
        # Capacity-based rules
        elif rule.alert_type == AlertType.CAPACITY:
            if 'observations_max' in threshold:
                return metrics.total_observations > threshold['observations_max']
        
        return False
    
    def _format_rule_values(self, rule: AlertRule, metrics: SystemMetrics) -> str:
        """Format current values for rule description."""
        threshold = rule.threshold
        values = []
        
        if 'critical_agents_max' in threshold:
            values.append(f"Critical agents: {metrics.critical_agents}")
        if 'offline_agents_max' in threshold:
            values.append(f"Offline agents: {metrics.offline_agents}")
        if 'healthy_agents_min' in threshold:
            values.append(f"Healthy agents: {metrics.healthy_agents}")
        if 'response_time_max' in threshold:
            values.append(f"Response time: {metrics.avg_response_time:.1f}ms")
        if 'memory_usage_max' in threshold:
            values.append(f"Memory: {metrics.memory_usage_mb:.1f}MB")
        if 'cpu_usage_max' in threshold:
            values.append(f"CPU: {metrics.cpu_usage_percent:.1f}%")
        if 'recent_errors_max' in threshold:
            values.append(f"Recent errors: {metrics.recent_errors}")
        if 'observations_max' in threshold:
            values.append(f"Observations: {metrics.total_observations}")
        
        return ", ".join(values)
    
    def _auto_resolve_alerts(self) -> None:
        """Auto-resolve alerts that are no longer relevant."""
        with self._lock:
            current_time = datetime.now()
            to_resolve = []
            
            for alert_id, alert in self.active_alerts.items():
                # Auto-resolve old info alerts (after 1 hour)
                if (alert.severity == AlertSeverity.INFO and
                    (current_time - alert.created_at).total_seconds() > 3600):
                    to_resolve.append(alert_id)
                
                # Auto-resolve old warning alerts (after 4 hours)
                elif (alert.severity == AlertSeverity.WARNING and
                      (current_time - alert.created_at).total_seconds() > 14400):
                    to_resolve.append(alert_id)
            
            for alert_id in to_resolve:
                self.resolve_alert(alert_id, "auto_resolved")
    
    def _setup_default_rules(self) -> None:
        """Setup default alert rules."""
        default_rules = [
            AlertRule(
                id="critical_agents",
                name="Critical Agents Alert",
                description="Alert when agents are in critical state",
                alert_type=AlertType.HEALTH,
                severity=AlertSeverity.CRITICAL,
                condition="critical_agents > 0",
                threshold={'critical_agents_max': 0},
                cooldown_minutes=30,
                tags=['health', 'critical']
            ),
            AlertRule(
                id="offline_agents",
                name="Offline Agents Alert",
                description="Alert when multiple agents are offline",
                alert_type=AlertType.HEALTH,
                severity=AlertSeverity.WARNING,
                condition="offline_agents > 1",
                threshold={'offline_agents_max': 1},
                cooldown_minutes=15,
                tags=['health', 'availability']
            ),
            AlertRule(
                id="high_response_time",
                name="High Response Time Alert",
                description="Alert when average response time is high",
                alert_type=AlertType.PERFORMANCE,
                severity=AlertSeverity.WARNING,
                condition="avg_response_time > 5000ms",
                threshold={'response_time_max': 5000},
                cooldown_minutes=20,
                tags=['performance', 'latency']
            ),
            AlertRule(
                id="high_memory_usage",
                name="High Memory Usage Alert",
                description="Alert when memory usage is high",
                alert_type=AlertType.PERFORMANCE,
                severity=AlertSeverity.WARNING,
                condition="memory_usage > 512MB",
                threshold={'memory_usage_max': 512},
                cooldown_minutes=30,
                tags=['performance', 'memory']
            ),
            AlertRule(
                id="frequent_errors",
                name="Frequent Errors Alert",
                description="Alert when there are many recent errors",
                alert_type=AlertType.ERROR,
                severity=AlertSeverity.WARNING,
                condition="recent_errors > 5",
                threshold={'recent_errors_max': 5},
                cooldown_minutes=10,
                tags=['errors', 'stability']
            )
        ]
        
        with self._lock:
            for rule in default_rules:
                if rule.id not in self.alert_rules:
                    self.alert_rules[rule.id] = rule
            
            self._save_rules()
    
    def _severity_to_priority(self, severity: AlertSeverity) -> int:
        """Convert alert severity to DCP priority."""
        severity_map = {
            AlertSeverity.EMERGENCY: 100,
            AlertSeverity.CRITICAL: 90,
            AlertSeverity.WARNING: 70,
            AlertSeverity.INFO: 40
        }
        return severity_map.get(severity, 50)
    
    def _save_alerts(self) -> None:
        """Save alerts to disk."""
        try:
            data = {
                'active_alerts': [alert.to_dict() for alert in self.active_alerts.values()],
                'alert_history': [alert.to_dict() for alert in self.alert_history[-self.max_alert_history:]],
                'last_updated': datetime.now().isoformat(),
                'total_active': len(self.active_alerts),
                'total_history': len(self.alert_history)
            }
            
            with open(self.alerts_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save alerts: {e}")
    
    def _save_rules(self) -> None:
        """Save alert rules to disk."""
        try:
            data = {
                'rules': [rule.to_dict() for rule in self.alert_rules.values()],
                'last_updated': datetime.now().isoformat(),
                'total_rules': len(self.alert_rules)
            }
            
            with open(self.rules_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save rules: {e}")
    
    def _save_metrics(self) -> None:
        """Save metrics history to disk."""
        try:
            data = {
                'metrics': [m.to_dict() for m in self.metrics_history[-100:]],  # Save last 100
                'last_updated': datetime.now().isoformat(),
                'total_metrics': len(self.metrics_history)
            }
            
            with open(self.metrics_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def _load_data(self) -> None:
        """Load existing data from disk."""
        # Load alerts
        try:
            if self.alerts_file.exists():
                with open(self.alerts_file, 'r') as f:
                    data = json.load(f)
                
                # Load active alerts
                for alert_data in data.get('active_alerts', []):
                    alert = MonitoringAlert.from_dict(alert_data)
                    self.active_alerts[alert.id] = alert
                
                # Load alert history
                for alert_data in data.get('alert_history', []):
                    alert = MonitoringAlert.from_dict(alert_data)
                    self.alert_history.append(alert)
                
                logger.info(f"Loaded {len(self.active_alerts)} active alerts, {len(self.alert_history)} history")
        except Exception as e:
            logger.warning(f"Failed to load alerts: {e}")
        
        # Load rules
        try:
            if self.rules_file.exists():
                with open(self.rules_file, 'r') as f:
                    data = json.load(f)
                
                for rule_data in data.get('rules', []):
                    rule = AlertRule(
                        id=rule_data['id'],
                        name=rule_data['name'],
                        description=rule_data['description'],
                        alert_type=AlertType(rule_data['alert_type']),
                        severity=AlertSeverity(rule_data['severity']),
                        condition=rule_data['condition'],
                        threshold=rule_data['threshold'],
                        enabled=rule_data.get('enabled', True),
                        cooldown_minutes=rule_data.get('cooldown_minutes', 15),
                        tags=rule_data.get('tags', [])
                    )
                    self.alert_rules[rule.id] = rule
                
                logger.info(f"Loaded {len(self.alert_rules)} alert rules")
        except Exception as e:
            logger.warning(f"Failed to load alert rules: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            # Count alerts by severity
            severity_counts = {severity.value: 0 for severity in AlertSeverity}
            for alert in self.active_alerts.values():
                severity_counts[alert.severity.value] += 1
            
            # Count alerts by type
            type_counts = {alert_type.value: 0 for alert_type in AlertType}
            for alert in self.alert_history[-100:]:  # Last 100 alerts
                type_counts[alert.alert_type.value] += 1
            
            return {
                'active_alerts': len(self.active_alerts),
                'total_history': len(self.alert_history),
                'total_rules': len(self.alert_rules),
                'enabled_rules': sum(1 for rule in self.alert_rules.values() if rule.enabled),
                'severity_distribution': severity_counts,
                'type_distribution': type_counts,
                'metrics_history_count': len(self.metrics_history),
                'monitoring_running': self._monitoring_thread and self._monitoring_thread.is_alive()
            }


# Convenience functions
def create_monitoring_system(
    project_path: str, 
    health_monitor: Optional[HealthMonitor] = None,
    dcp_manager=None
) -> MonitoringAlertsSystem:
    """Create and start a monitoring system.
    
    Args:
        project_path: Project root path
        health_monitor: Optional health monitor
        dcp_manager: Optional DCP manager
        
    Returns:
        Configured MonitoringAlertsSystem instance
    """
    return MonitoringAlertsSystem(project_path, health_monitor, dcp_manager)


def setup_basic_monitoring(project_path: str) -> Tuple[HealthMonitor, MonitoringAlertsSystem]:
    """Setup basic monitoring with health monitor and alerts.
    
    Args:
        project_path: Project root path
        
    Returns:
        Tuple of (HealthMonitor, MonitoringAlertsSystem)
    """
    from .context.dcp_manager import DCPManager
    
    # Create DCP manager
    dcp_manager = DCPManager(project_path)
    
    # Create health monitor
    health_monitor = HealthMonitor(project_path, dcp_manager)
    
    # Create monitoring system
    monitoring_system = MonitoringAlertsSystem(project_path, health_monitor, dcp_manager)
    
    return health_monitor, monitoring_system