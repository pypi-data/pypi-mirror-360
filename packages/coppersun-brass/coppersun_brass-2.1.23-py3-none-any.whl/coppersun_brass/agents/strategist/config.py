# coppersun_brass/agents/strategist/config.py
"""
Configuration management for Strategist Agent
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json
import logging
from ...core.constants import FilePaths, PerformanceSettings

logger = logging.getLogger(__name__)

class StrategistConfig:
    """Configuration manager for Strategist Agent"""
    
    DEFAULT_CONFIG = {
        # Priority engine settings
        'priority': {
            'time_decay_hours': 168,  # 1 week
            'max_score': 100,
            'min_score': 0,
            'type_scores': {
                # Override default type scores here
            }
        },
        
        # Duplicate detection settings
        'duplicates': {
            'content_threshold': 0.85,
            'location_threshold': 0.9,
            'time_window_hours': 24,
            'use_content_hash': True,
            'use_semantic_similarity': True,
            'use_location_matching': True,
            'use_temporal_grouping': True
        },
        
        # Orchestration settings
        'orchestration': {
            'auto_orchestrate': True,
            'orchestration_interval': PerformanceSettings.ANALYSIS_INTERVAL,  # Default analysis interval
            'batch_updates': True,
            'max_observations_per_cycle': 1000
        },
        
        # Task routing settings
        'routing': {
            'min_priority_for_routing': 70,
            'max_tasks_per_agent': 10,
            'prefer_claude_for_critical': True,
            'enable_human_escalation': True
        },
        
        # Performance settings
        'performance': {
            'enable_caching': True,
            'cache_ttl_hours': 24,
            'async_processing': True,
            'max_concurrent_operations': PerformanceSettings.MAX_WORKERS
        }
    }
    
    def __init__(self, project_path: str, config_override: Optional[Dict] = None):
        self.project_path = Path(project_path)
        self.config_file = self.project_path / FilePaths.CONFIG_DIR / 'strategist_config.json'
        
        # Load configuration
        self.config = self._load_config()
        
        # Apply override if provided
        if config_override:
            self.config = self._merge_config(self.config, config_override)
        
        logger.debug(f"Strategist config loaded from {self.config_file}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                
                # Merge with defaults
                return self._merge_config(self.DEFAULT_CONFIG.copy(), file_config)
                
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_file}: {e}")
                return self.DEFAULT_CONFIG.copy()
        
        return self.DEFAULT_CONFIG.copy()
    
    def _merge_config(self, base: Dict, override: Dict) -> Dict:
        """Recursively merge configuration dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            logger.info(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            logger.error(f"Failed to save config to {self.config_file}: {e}")
            raise
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to parent
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set value
        config[keys[-1]] = value
    
    def get_priority_config(self) -> Dict[str, Any]:
        """Get priority engine configuration"""
        return self.config.get('priority', {})
    
    def get_duplicate_config(self) -> Dict[str, Any]:
        """Get duplicate detection configuration"""
        return self.config.get('duplicates', {})
    
    def get_orchestration_config(self) -> Dict[str, Any]:
        """Get orchestration configuration"""
        return self.config.get('orchestration', {})
    
    def get_routing_config(self) -> Dict[str, Any]:
        """Get task routing configuration"""
        return self.config.get('routing', {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration"""
        return self.config.get('performance', {})
    
    def update_type_scores(self, type_scores: Dict[str, int]):
        """Update priority type scores"""
        current_scores = self.get('priority.type_scores', {})
        current_scores.update(type_scores)
        self.set('priority.type_scores', current_scores)
    
    def update_thresholds(self, content_threshold: Optional[float] = None, 
                         location_threshold: Optional[float] = None):
        """Update duplicate detection thresholds"""
        if content_threshold is not None:
            self.set('duplicates.content_threshold', content_threshold)
        
        if location_threshold is not None:
            self.set('duplicates.location_threshold', location_threshold)
    
    def enable_feature(self, feature: str, enabled: bool = True):
        """Enable or disable a feature"""
        feature_mappings = {
            'auto_orchestration': 'orchestration.auto_orchestrate',
            'caching': 'performance.enable_caching',
            'async_processing': 'performance.async_processing',
            'human_escalation': 'routing.enable_human_escalation',
            'content_hash': 'duplicates.use_content_hash',
            'semantic_similarity': 'duplicates.use_semantic_similarity',
            'location_matching': 'duplicates.use_location_matching',
            'temporal_grouping': 'duplicates.use_temporal_grouping'
        }
        
        if feature in feature_mappings:
            self.set(feature_mappings[feature], enabled)
        else:
            raise ValueError(f"Unknown feature: {feature}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get configuration status"""
        return {
            'config_file': str(self.config_file),
            'config_exists': self.config_file.exists(),
            'total_settings': self._count_settings(self.config),
            'feature_flags': {
                'auto_orchestration': self.get('orchestration.auto_orchestrate', True),
                'caching': self.get('performance.enable_caching', True),
                'async_processing': self.get('performance.async_processing', True),
                'human_escalation': self.get('routing.enable_human_escalation', True)
            }
        }
    
    def _count_settings(self, config: Dict, prefix: str = '') -> int:
        """Recursively count configuration settings"""
        count = 0
        for key, value in config.items():
            if isinstance(value, dict):
                count += self._count_settings(value, f"{prefix}.{key}" if prefix else key)
            else:
                count += 1
        return count
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return validation results"""
        issues = []
        warnings = []
        
        # Validate priority settings
        priority_config = self.get_priority_config()
        
        time_decay = priority_config.get('time_decay_hours', 168)
        if time_decay <= 0:
            issues.append("priority.time_decay_hours must be positive")
        elif time_decay < 24:
            warnings.append("priority.time_decay_hours < 24 may cause rapid priority decay")
        
        max_score = priority_config.get('max_score', 100)
        min_score = priority_config.get('min_score', 0)
        if max_score <= min_score:
            issues.append("priority.max_score must be greater than min_score")
        
        # Validate duplicate detection settings
        duplicate_config = self.get_duplicate_config()
        
        content_threshold = duplicate_config.get('content_threshold', 0.85)
        if not 0.0 <= content_threshold <= 1.0:
            issues.append("duplicates.content_threshold must be between 0.0 and 1.0")
        elif content_threshold > 0.95:
            warnings.append("duplicates.content_threshold > 0.95 may miss similar observations")
        
        # Validate orchestration settings
        orchestration_config = self.get_orchestration_config()
        
        interval = orchestration_config.get('orchestration_interval', 300)
        if interval < 60:
            warnings.append("orchestration.orchestration_interval < 60s may cause high CPU usage")
        
        max_obs = orchestration_config.get('max_observations_per_cycle', 1000)
        if max_obs > 5000:
            warnings.append("orchestration.max_observations_per_cycle > 5000 may cause memory issues")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'validation_timestamp': 'current'
        }

# Convenience function for getting strategist config
def get_strategist_config(project_path: str, config_override: Optional[Dict] = None) -> StrategistConfig:
    """Get strategist configuration for a project"""
    return StrategistConfig(project_path, config_override)