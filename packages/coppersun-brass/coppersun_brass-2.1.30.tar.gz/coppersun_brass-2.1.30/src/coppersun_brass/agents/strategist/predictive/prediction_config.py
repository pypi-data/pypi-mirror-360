"""
Copper Alloy Brass Prediction Configuration - Feature flags and configuration management
Implements configurable prediction parameters with validation and defaults
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import os
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PredictionConfig:
    """
    Configuration for Copper Alloy Brass Prediction Engine with feature flags and parameters
    
    Provides configurable thresholds, feature toggles, and prediction parameters
    to support gradual rollout and customization per GPT architectural guidance.
    """
    
    # Feature flags for modular activation per GPT recommendation
    timeline_prediction_enabled: bool = True
    pattern_matching_enabled: bool = False  # Future sprint
    resource_optimization_enabled: bool = False  # Future sprint
    prediction_validation_enabled: bool = True
    
    # Prediction cycle configuration
    prediction_frequency: int = 5  # Every N orchestration cycles
    min_prediction_interval_minutes: int = 30  # Minimum time between predictions
    prediction_retention_days: int = 30  # How long to keep predictions in DCP
    
    # Timeline prediction parameters
    velocity_analysis_window_days: int = 14  # Window for velocity calculation
    trend_detection_sensitivity: float = 0.1  # Sensitivity for trend detection
    minimum_confidence_threshold: float = 0.5  # Minimum confidence for predictions
    
    # Bottleneck prediction thresholds
    priority_inflation_threshold: float = 10.0  # Percentage priority inflation threshold
    observation_accumulation_threshold: float = 2.0  # Observations per time period threshold
    
    # Performance and caching settings
    cache_ttl_minutes: int = 10  # Cache time-to-live
    max_snapshots_for_analysis: int = 50  # Maximum snapshots to analyze
    async_prediction_timeout_seconds: int = 30  # Timeout for async predictions
    
    # DCP update triggers
    change_threshold_for_predictions: int = 3  # Minimum changes to trigger predictions
    significant_priority_change_threshold: int = 5  # Priority change threshold
    
    # Validation and accuracy tracking
    validation_sample_size: int = 10  # Sample size for accuracy calculation
    accuracy_measurement_window_days: int = 7  # Window for accuracy measurement
    minimum_validation_confidence: float = 0.6  # Minimum confidence for validation
    
    # Advanced configuration for future features
    advanced_settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        self._validate_config()
        logger.info("PredictionConfig initialized and validated")
    
    def _validate_config(self):
        """Validate configuration parameters"""
        try:
            # Validate prediction frequency
            if self.prediction_frequency < 1:
                raise ValueError("prediction_frequency must be >= 1")
            
            # Validate time-based parameters
            if self.min_prediction_interval_minutes < 1:
                raise ValueError("min_prediction_interval_minutes must be >= 1")
                
            if self.velocity_analysis_window_days < 1:
                raise ValueError("velocity_analysis_window_days must be >= 1")
                
            if self.prediction_retention_days < 1:
                raise ValueError("prediction_retention_days must be >= 1")
            
            # Validate thresholds
            if not 0.0 <= self.minimum_confidence_threshold <= 1.0:
                raise ValueError("minimum_confidence_threshold must be between 0.0 and 1.0")
                
            if not 0.0 <= self.trend_detection_sensitivity <= 1.0:
                raise ValueError("trend_detection_sensitivity must be between 0.0 and 1.0")
            
            # Validate performance settings
            if self.cache_ttl_minutes < 1:
                raise ValueError("cache_ttl_minutes must be >= 1")
                
            if self.max_snapshots_for_analysis < 2:
                raise ValueError("max_snapshots_for_analysis must be >= 2")
                
            if self.async_prediction_timeout_seconds < 5:
                raise ValueError("async_prediction_timeout_seconds must be >= 5")
            
            logger.info("Configuration validation passed")
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'PredictionConfig':
        """
        Create configuration from dictionary
        
        Args:
            config_dict: Configuration parameters dictionary
            
        Returns:
            PredictionConfig instance
        """
        try:
            # Filter out unknown keys to prevent errors
            known_fields = {f.name for f in cls.__dataclass_fields__.values()}
            filtered_dict = {k: v for k, v in config_dict.items() if k in known_fields}
            
            return cls(**filtered_dict)
            
        except Exception as e:
            logger.error(f"Failed to create config from dictionary: {e}")
            return cls()  # Return default config
    
    @classmethod
    def from_file(cls, config_path: str) -> 'PredictionConfig':
        """
        Load configuration from JSON file
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            PredictionConfig instance
        """
        try:
            if not os.path.exists(config_path):
                logger.warning(f"Config file {config_path} not found, using defaults")
                return cls()
            
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            return cls.from_dict(config_data)
            
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            return cls()  # Return default config
    
    @classmethod
    def from_environment(cls) -> 'PredictionConfig':
        """
        Create configuration from environment variables
        
        Environment variables should be prefixed with BRASS_PREDICTION_
        
        Returns:
            PredictionConfig instance
        """
        try:
            config_dict = {}
            prefix = "BRASS_PREDICTION_"
            
            # Map environment variables to config fields
            env_mappings = {
                f"{prefix}TIMELINE_ENABLED": ("timeline_prediction_enabled", bool),
                f"{prefix}PATTERN_ENABLED": ("pattern_matching_enabled", bool),
                f"{prefix}RESOURCE_ENABLED": ("resource_optimization_enabled", bool),
                f"{prefix}VALIDATION_ENABLED": ("prediction_validation_enabled", bool),
                f"{prefix}FREQUENCY": ("prediction_frequency", int),
                f"{prefix}MIN_INTERVAL": ("min_prediction_interval_minutes", int),
                f"{prefix}RETENTION_DAYS": ("prediction_retention_days", int),
                f"{prefix}VELOCITY_WINDOW": ("velocity_analysis_window_days", int),
                f"{prefix}TREND_SENSITIVITY": ("trend_detection_sensitivity", float),
                f"{prefix}MIN_CONFIDENCE": ("minimum_confidence_threshold", float),
                f"{prefix}PRIORITY_THRESHOLD": ("priority_inflation_threshold", float),
                f"{prefix}ACCUMULATION_THRESHOLD": ("observation_accumulation_threshold", float),
                f"{prefix}CACHE_TTL": ("cache_ttl_minutes", int),
                f"{prefix}MAX_SNAPSHOTS": ("max_snapshots_for_analysis", int),
                f"{prefix}TIMEOUT": ("async_prediction_timeout_seconds", int),
                f"{prefix}CHANGE_THRESHOLD": ("change_threshold_for_predictions", int),
            }
            
            for env_var, (config_field, config_type) in env_mappings.items():
                env_value = os.getenv(env_var)
                if env_value is not None:
                    try:
                        if config_type == bool:
                            config_dict[config_field] = env_value.lower() in ('true', '1', 'yes', 'on')
                        else:
                            config_dict[config_field] = config_type(env_value)
                    except ValueError as e:
                        logger.warning(f"Failed to parse environment variable {env_var}: {e}")
            
            return cls.from_dict(config_dict)
            
        except Exception as e:
            logger.error(f"Failed to load config from environment: {e}")
            return cls()  # Return default config
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary
        
        Returns:
            Dictionary representation of configuration
        """
        try:
            config_dict = {}
            
            # Convert all dataclass fields to dictionary
            for field_name, field_def in self.__dataclass_fields__.items():
                value = getattr(self, field_name)
                config_dict[field_name] = value
            
            return config_dict
            
        except Exception as e:
            logger.error(f"Failed to convert config to dictionary: {e}")
            return {}
    
    def save_to_file(self, config_path: str) -> bool:
        """
        Save configuration to JSON file
        
        Args:
            config_path: Path to save configuration file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            config_dict = self.to_dict()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            logger.info(f"Configuration saved to {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save config to {config_path}: {e}")
            return False
    
    def update_from_dict(self, updates: Dict[str, Any]) -> bool:
        """
        Update configuration with new values
        
        Args:
            updates: Dictionary of field updates
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate that all update keys are valid fields
            known_fields = {f.name for f in self.__dataclass_fields__.values()}
            invalid_keys = set(updates.keys()) - known_fields
            
            if invalid_keys:
                logger.warning(f"Invalid configuration keys ignored: {invalid_keys}")
            
            # Apply valid updates
            for key, value in updates.items():
                if key in known_fields:
                    setattr(self, key, value)
            
            # Re-validate configuration
            self._validate_config()
            
            logger.info("Configuration updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False
    
    def enable_feature(self, feature_name: str) -> bool:
        """
        Enable a prediction feature
        
        Args:
            feature_name: Name of feature to enable
            
        Returns:
            True if successful, False otherwise
        """
        try:
            feature_flags = {
                'timeline': 'timeline_prediction_enabled',
                'pattern': 'pattern_matching_enabled',
                'resource': 'resource_optimization_enabled',
                'validation': 'prediction_validation_enabled'
            }
            
            if feature_name not in feature_flags:
                logger.error(f"Unknown feature: {feature_name}")
                return False
            
            setattr(self, feature_flags[feature_name], True)
            logger.info(f"Feature {feature_name} enabled")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable feature {feature_name}: {e}")
            return False
    
    def disable_feature(self, feature_name: str) -> bool:
        """
        Disable a prediction feature
        
        Args:
            feature_name: Name of feature to disable
            
        Returns:
            True if successful, False otherwise
        """
        try:
            feature_flags = {
                'timeline': 'timeline_prediction_enabled',
                'pattern': 'pattern_matching_enabled',
                'resource': 'resource_optimization_enabled',
                'validation': 'prediction_validation_enabled'
            }
            
            if feature_name not in feature_flags:
                logger.error(f"Unknown feature: {feature_name}")
                return False
            
            setattr(self, feature_flags[feature_name], False)
            logger.info(f"Feature {feature_name} disabled")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable feature {feature_name}: {e}")
            return False
    
    def get_enabled_features(self) -> Dict[str, bool]:
        """
        Get status of all prediction features
        
        Returns:
            Dictionary of feature statuses
        """
        try:
            return {
                'timeline': self.timeline_prediction_enabled,
                'pattern': self.pattern_matching_enabled,
                'resource': self.resource_optimization_enabled,
                'validation': self.prediction_validation_enabled
            }
            
        except Exception as e:
            logger.error(f"Failed to get feature status: {e}")
            return {}
    
    def get_performance_settings(self) -> Dict[str, Any]:
        """
        Get performance-related configuration settings
        
        Returns:
            Dictionary of performance settings
        """
        try:
            return {
                'cache_ttl_minutes': self.cache_ttl_minutes,
                'max_snapshots_for_analysis': self.max_snapshots_for_analysis,
                'async_prediction_timeout_seconds': self.async_prediction_timeout_seconds,
                'prediction_frequency': self.prediction_frequency,
                'min_prediction_interval_minutes': self.min_prediction_interval_minutes
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance settings: {e}")
            return {}
    
    def get_threshold_settings(self) -> Dict[str, float]:
        """
        Get threshold-related configuration settings
        
        Returns:
            Dictionary of threshold settings
        """
        try:
            return {
                'minimum_confidence_threshold': self.minimum_confidence_threshold,
                'trend_detection_sensitivity': self.trend_detection_sensitivity,
                'priority_inflation_threshold': self.priority_inflation_threshold,
                'observation_accumulation_threshold': self.observation_accumulation_threshold,
                'change_threshold_for_predictions': float(self.change_threshold_for_predictions),
                'significant_priority_change_threshold': float(self.significant_priority_change_threshold)
            }
            
        except Exception as e:
            logger.error(f"Failed to get threshold settings: {e}")
            return {}
    
    def is_feature_ready(self, feature_name: str) -> bool:
        """
        Check if a feature is enabled and ready for use
        
        Args:
            feature_name: Name of feature to check
            
        Returns:
            True if feature is ready, False otherwise
        """
        try:
            feature_checks = {
                'timeline': self.timeline_prediction_enabled,
                'pattern': self.pattern_matching_enabled and False,  # Not implemented yet
                'resource': self.resource_optimization_enabled and False,  # Not implemented yet
                'validation': self.prediction_validation_enabled
            }
            
            return feature_checks.get(feature_name, False)
            
        except Exception as e:
            logger.error(f"Failed to check feature readiness for {feature_name}: {e}")
            return False
    
    def optimize_for_performance(self) -> None:
        """Optimize configuration for better performance"""
        try:
            logger.info("Optimizing configuration for performance")
            
            # Reduce prediction frequency for better performance
            if self.prediction_frequency < 3:
                self.prediction_frequency = 3
            
            # Optimize cache settings
            if self.cache_ttl_minutes < 5:
                self.cache_ttl_minutes = 5
            
            # Limit analysis scope
            if self.max_snapshots_for_analysis > 30:
                self.max_snapshots_for_analysis = 30
            
            # Increase thresholds to reduce noise
            if self.change_threshold_for_predictions < 5:
                self.change_threshold_for_predictions = 5
            
            logger.info("Configuration optimized for performance")
            
        except Exception as e:
            logger.error(f"Failed to optimize configuration: {e}")
    
    def optimize_for_accuracy(self) -> None:
        """Optimize configuration for better prediction accuracy"""
        try:
            logger.info("Optimizing configuration for accuracy")
            
            # Increase prediction frequency for more data
            if self.prediction_frequency > 3:
                self.prediction_frequency = 3
            
            # Increase analysis window
            if self.velocity_analysis_window_days < 14:
                self.velocity_analysis_window_days = 14
            
            # Use more snapshots for analysis
            if self.max_snapshots_for_analysis < 50:
                self.max_snapshots_for_analysis = 50
            
            # Lower thresholds for more sensitive detection
            if self.minimum_confidence_threshold > 0.5:
                self.minimum_confidence_threshold = 0.5
            
            if self.trend_detection_sensitivity > 0.1:
                self.trend_detection_sensitivity = 0.1
            
            logger.info("Configuration optimized for accuracy")
            
        except Exception as e:
            logger.error(f"Failed to optimize configuration for accuracy: {e}")
    
    def get_configuration_summary(self) -> str:
        """
        Get human-readable configuration summary
        
        Returns:
            String summary of current configuration
        """
        try:
            enabled_features = [name for name, enabled in self.get_enabled_features().items() if enabled]
            
            summary_parts = [
                f"Prediction Engine Configuration:",
                f"  Enabled Features: {', '.join(enabled_features) if enabled_features else 'None'}",
                f"  Prediction Frequency: Every {self.prediction_frequency} cycles",
                f"  Velocity Analysis Window: {self.velocity_analysis_window_days} days",
                f"  Minimum Confidence: {self.minimum_confidence_threshold:.1f}",
                f"  Cache TTL: {self.cache_ttl_minutes} minutes",
                f"  Max Snapshots: {self.max_snapshots_for_analysis}",
                f"  Retention Period: {self.prediction_retention_days} days"
            ]
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Failed to generate configuration summary: {e}")
            return "Configuration summary unavailable"


# Factory functions for common configurations

def create_development_config() -> PredictionConfig:
    """Create configuration optimized for development"""
    config = PredictionConfig()
    config.prediction_frequency = 2  # More frequent for testing
    config.cache_ttl_minutes = 5  # Shorter cache for development
    config.velocity_analysis_window_days = 7  # Shorter window for faster feedback
    config.minimum_confidence_threshold = 0.3  # Lower threshold for testing
    return config

def create_production_config() -> PredictionConfig:
    """Create configuration optimized for production"""
    config = PredictionConfig()
    config.optimize_for_performance()
    config.prediction_retention_days = 60  # Longer retention for production
    config.async_prediction_timeout_seconds = 45  # Longer timeout for stability
    return config

def create_high_accuracy_config() -> PredictionConfig:
    """Create configuration optimized for maximum accuracy"""
    config = PredictionConfig()
    config.optimize_for_accuracy()
    return config

def load_config(config_source: Optional[str] = None) -> PredictionConfig:
    """
    Load configuration from various sources
    
    Args:
        config_source: Path to config file, 'env' for environment, or None for defaults
        
    Returns:
        PredictionConfig instance
    """
    try:
        if config_source == 'env':
            return PredictionConfig.from_environment()
        elif config_source and os.path.exists(config_source):
            return PredictionConfig.from_file(config_source)
        else:
            logger.info("Using default prediction configuration")
            return PredictionConfig()
            
    except Exception as e:
        logger.error(f"Failed to load configuration from {config_source}: {e}")
        return PredictionConfig()  # Return default config as fallback