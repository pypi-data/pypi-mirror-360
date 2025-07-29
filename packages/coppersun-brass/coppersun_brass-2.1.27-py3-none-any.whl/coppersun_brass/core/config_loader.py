"""Production configuration loader for Copper Alloy Brass.

This module handles loading and validating configuration from YAML files
and environment variables, with support for environment-specific overrides.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


@dataclass
class StorageConfig:
    """Storage configuration."""
    type: str = "sqlite"
    path: str = ".brass/coppersun_brass.db"
    backup_enabled: bool = True
    backup_interval: int = 3600
    backup_retention_days: int = 30
    backup_path: str = ".brass/backups"
    max_backups: int = 168
    connection_pool_size: int = 10
    connection_pool_overflow: int = 20
    connection_timeout: int = 30


@dataclass
class MonitoringConfig:
    """Monitoring configuration."""
    enabled: bool = True
    metrics_port: int = 9090
    health_check_interval: int = 60
    memory_alert_mb: int = 1024
    disk_alert_percent: int = 90
    error_rate_alert_percent: int = 5
    response_time_alert_ms: int = 1000
    metrics_retention_days: int = 7


@dataclass
class SecurityConfig:
    """Security configuration."""
    api_authentication: bool = True
    api_key_header: str = "X-Copper Alloy Brass-API-Key"
    rate_limiting_enabled: bool = True
    rate_limit_rpm: int = 60
    rate_limit_burst: int = 10
    max_path_length: int = 4096
    max_file_size_mb: int = 50


@dataclass
class BrassConfig:
    """Main Copper Alloy Brass configuration."""
    version: str = "1.0.0"
    environment: str = "development"
    project_root: str = "."
    log_level: str = "INFO"
    max_workers: int = 4
    thread_pool_size: int = 8
    
    # Sub-configurations
    storage: StorageConfig = field(default_factory=StorageConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Feature flags
    features: Dict[str, bool] = field(default_factory=lambda: {
        "experimental_semantic_analysis": False,
        "advanced_pattern_detection": True,
        "real_time_collaboration": False,
        "distributed_processing": False
    })


class ConfigLoader:
    """Loads and manages Copper Alloy Brass configuration."""
    
    def __init__(self, config_path: Optional[str] = None, env_file: Optional[str] = None):
        """Initialize configuration loader.
        
        Args:
            config_path: Path to YAML configuration file
            env_file: Path to environment file (defaults to .env)
        """
        self.config_path = config_path
        self.env_file = env_file or ".env"
        self._config: Optional[BrassConfig] = None
        
    def load(self) -> BrassConfig:
        """Load configuration from all sources.
        
        Order of precedence (highest to lowest):
        1. Environment variables
        2. Environment-specific YAML config
        3. Main YAML config
        4. Defaults
        """
        if self._config is not None:
            return self._config
            
        # Load environment variables
        if os.path.exists(self.env_file):
            load_dotenv(self.env_file)
            
        # Start with defaults
        config = BrassConfig()
        
        # Load YAML config if provided
        if self.config_path and os.path.exists(self.config_path):
            yaml_config = self._load_yaml(self.config_path)
            config = self._merge_config(config, yaml_config)
            
        # Apply environment variable overrides
        config = self._apply_env_overrides(config)
        
        # Validate configuration
        self._validate_config(config)
        
        self._config = config
        logger.info(f"Loaded configuration for environment: {config.environment}")
        
        return config
        
    def _load_yaml(self, path: str) -> Dict[str, Any]:
        """Load YAML configuration file."""
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                
            # Get base config
            base_config = data.get('coppersun_brass', {})
            
            # Apply environment-specific overrides
            env = os.getenv('BRASS_ENV', 'development')
            env_overrides = data.get('environments', {}).get(env, {})
            
            # Merge environment overrides
            if env_overrides:
                base_config = self._deep_merge(base_config, env_overrides.get('coppersun_brass', {}))
                
            return base_config
            
        except Exception as e:
            logger.error(f"Failed to load YAML config from {path}: {e}")
            return {}
            
    def _merge_config(self, config: BrassConfig, yaml_data: Dict[str, Any]) -> BrassConfig:
        """Merge YAML data into configuration object."""
        # Core settings
        config.version = yaml_data.get('version', config.version)
        config.environment = yaml_data.get('environment', config.environment)
        
        core = yaml_data.get('core', {})
        config.project_root = core.get('project_root', config.project_root)
        config.log_level = core.get('log_level', config.log_level)
        config.max_workers = core.get('max_workers', config.max_workers)
        config.thread_pool_size = core.get('thread_pool_size', config.thread_pool_size)
        
        # Storage settings
        storage = yaml_data.get('storage', {})
        if storage:
            backup = storage.get('backup', {})
            pool = storage.get('connection_pool', {})
            
            config.storage.type = storage.get('type', config.storage.type)
            config.storage.path = storage.get('path', config.storage.path)
            config.storage.backup_enabled = backup.get('enabled', config.storage.backup_enabled)
            config.storage.backup_interval = backup.get('interval', config.storage.backup_interval)
            config.storage.backup_retention_days = backup.get('retention_days', config.storage.backup_retention_days)
            config.storage.backup_path = backup.get('backup_path', config.storage.backup_path)
            config.storage.max_backups = backup.get('max_backups', config.storage.max_backups)
            config.storage.connection_pool_size = pool.get('size', config.storage.connection_pool_size)
            config.storage.connection_pool_overflow = pool.get('max_overflow', config.storage.connection_pool_overflow)
            config.storage.connection_timeout = pool.get('timeout', config.storage.connection_timeout)
            
        # Monitoring settings
        monitoring = yaml_data.get('monitoring', {})
        if monitoring:
            alerts = monitoring.get('alerts', {})
            metrics = monitoring.get('metrics', {})
            
            config.monitoring.enabled = monitoring.get('enabled', config.monitoring.enabled)
            config.monitoring.metrics_port = monitoring.get('metrics_port', config.monitoring.metrics_port)
            config.monitoring.health_check_interval = monitoring.get('health_check_interval', config.monitoring.health_check_interval)
            config.monitoring.memory_alert_mb = alerts.get('memory_usage_mb', config.monitoring.memory_alert_mb)
            config.monitoring.disk_alert_percent = alerts.get('disk_usage_percent', config.monitoring.disk_alert_percent)
            config.monitoring.error_rate_alert_percent = alerts.get('error_rate_percent', config.monitoring.error_rate_alert_percent)
            config.monitoring.response_time_alert_ms = alerts.get('response_time_ms', config.monitoring.response_time_alert_ms)
            config.monitoring.metrics_retention_days = metrics.get('retention_days', config.monitoring.metrics_retention_days)
            
        # Security settings
        security = yaml_data.get('security', {})
        if security:
            rate_limiting = security.get('rate_limiting', {})
            validation = security.get('validation', {})
            
            config.security.api_authentication = security.get('api_authentication', config.security.api_authentication)
            config.security.api_key_header = security.get('api_key_header', config.security.api_key_header)
            config.security.rate_limiting_enabled = rate_limiting.get('enabled', config.security.rate_limiting_enabled)
            config.security.rate_limit_rpm = rate_limiting.get('requests_per_minute', config.security.rate_limit_rpm)
            config.security.rate_limit_burst = rate_limiting.get('burst_size', config.security.rate_limit_burst)
            config.security.max_path_length = validation.get('max_path_length', config.security.max_path_length)
            config.security.max_file_size_mb = validation.get('max_file_size_mb', config.security.max_file_size_mb)
            
        # Feature flags
        features = yaml_data.get('features', {})
        if features:
            config.features.update(features)
            
        return config
        
    def _apply_env_overrides(self, config: BrassConfig) -> BrassConfig:
        """Apply environment variable overrides to configuration."""
        # Core settings
        config.environment = os.getenv('BRASS_ENV', config.environment)
        config.log_level = os.getenv('BRASS_LOG_LEVEL', config.log_level)
        config.max_workers = int(os.getenv('BRASS_MAX_WORKERS', str(config.max_workers)))
        config.thread_pool_size = int(os.getenv('BRASS_THREAD_POOL_SIZE', str(config.thread_pool_size)))
        
        # Storage settings
        config.storage.path = os.getenv('BRASS_DB_PATH', config.storage.path)
        config.storage.backup_path = os.getenv('BRASS_BACKUP_PATH', config.storage.backup_path)
        config.storage.backup_retention_days = int(os.getenv('BRASS_DCP_BACKUP_RETENTION', str(config.storage.backup_retention_days)))
        
        # Monitoring settings
        config.monitoring.enabled = os.getenv('BRASS_MONITORING_ENABLED', 'true').lower() == 'true'
        config.monitoring.metrics_port = int(os.getenv('BRASS_METRICS_PORT', str(config.monitoring.metrics_port)))
        config.monitoring.health_check_interval = int(os.getenv('BRASS_HEALTH_CHECK_INTERVAL', str(config.monitoring.health_check_interval)))
        
        # Security settings
        config.security.api_authentication = os.getenv('BRASS_API_AUTH_ENABLED', 'true').lower() == 'true'
        config.security.rate_limiting_enabled = os.getenv('BRASS_CIRCUIT_BREAKER_ENABLED', 'true').lower() == 'true'
        config.security.rate_limit_rpm = int(os.getenv('BRASS_RATE_LIMIT_RPM', str(config.security.rate_limit_rpm)))
        
        return config
        
    def _validate_config(self, config: BrassConfig) -> None:
        """Validate configuration values."""
        # Validate paths exist or can be created
        project_root = Path(config.project_root)
        if not project_root.exists():
            raise ValueError(f"Project root does not exist: {config.project_root}")
            
        # Validate numeric ranges
        if config.max_workers < 1:
            raise ValueError("max_workers must be at least 1")
            
        if config.thread_pool_size < 1:
            raise ValueError("thread_pool_size must be at least 1")
            
        if config.monitoring.metrics_port < 1024 or config.monitoring.metrics_port > 65535:
            raise ValueError("metrics_port must be between 1024 and 65535")
            
        if config.security.rate_limit_rpm < 1:
            raise ValueError("rate_limit_rpm must be at least 1")
            
        # Log validation success
        logger.info("Configuration validation successful")
        
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result
        
    def get_config(self) -> BrassConfig:
        """Get loaded configuration, loading if necessary."""
        if self._config is None:
            self.load()
        return self._config
        
    def reload(self) -> BrassConfig:
        """Reload configuration from sources."""
        self._config = None
        return self.load()


# Global configuration instance
_config_loader: Optional[ConfigLoader] = None


def get_config() -> BrassConfig:
    """Get global configuration instance."""
    global _config_loader
    
    if _config_loader is None:
        # Check for config path in environment
        config_path = os.getenv('BRASS_CONFIG_PATH')
        env_file = os.getenv('BRASS_ENV_FILE', '.env')
        
        _config_loader = ConfigLoader(config_path=config_path, env_file=env_file)
        
    return _config_loader.get_config()


def init_config(config_path: Optional[str] = None, env_file: Optional[str] = None) -> BrassConfig:
    """Initialize global configuration with specific paths."""
    global _config_loader
    
    _config_loader = ConfigLoader(config_path=config_path, env_file=env_file)
    return _config_loader.load()