"""Observation validation using JSON schemas.

General Staff Role: This component ensures data integrity for the
intelligence system by validating all observations against formal
schemas before they enter the DCP.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from jsonschema import validate, ValidationError, Draft7Validator, RefResolver
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    ValidationError = Exception

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation strictness levels."""
    STRICT = "strict"      # Fail on any validation error
    WARNINGS = "warnings"  # Log warnings but allow
    DISABLED = "disabled"  # No validation


@dataclass
class ValidationResult:
    """Result of observation validation."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    observation_type: str
    schema_used: Optional[str] = None


class ObservationValidator:
    """Validates observations against JSON schemas.
    
    This ensures data quality and consistency across all agents,
    preventing corrupted or malformed data from entering the DCP.
    """
    
    def __init__(self, 
                 schemas_dir: Optional[Path] = None,
                 validation_level: ValidationLevel = ValidationLevel.WARNINGS):
        """Initialize validator.
        
        Args:
            schemas_dir: Directory containing JSON schemas
            validation_level: How strict to be with validation
        """
        self.validation_level = validation_level
        self.schemas: Dict[str, Dict] = {}
        self.validators: Dict[str, Any] = {}
        
        if not HAS_JSONSCHEMA:
            logger.warning(
                "jsonschema not installed. Observation validation disabled. "
                "Install with: pip install jsonschema"
            )
            self.validation_level = ValidationLevel.DISABLED
            return
        
        # Load schemas
        if schemas_dir is None:
            schemas_dir = Path(__file__).parent / "schemas" / "observations"
        
        self.schemas_dir = schemas_dir
        self._load_schemas()
    
    def _load_schemas(self):
        """Load all JSON schemas from directory."""
        if not self.schemas_dir.exists():
            logger.warning(f"Schemas directory not found: {self.schemas_dir}")
            return
        
        # Load base schema first
        base_schema_path = self.schemas_dir / "base_schema.json"
        if base_schema_path.exists():
            try:
                with open(base_schema_path) as f:
                    base_schema = json.load(f)
                    self.schemas['base'] = base_schema
            except Exception as e:
                logger.error(f"Failed to load base schema: {e}")
        
        # Load observation type schemas
        schema_files = {
            'todo': 'todo_schema.json',
            'security_issue': 'security_schema.json',
            'file_analysis': 'file_analysis_schema.json',
            'code_smell': 'code_smell_schema.json',
            'capability_assessment': 'capability_schema.json',
            'agent_status': 'agent_status_schema.json'
        }
        
        for obs_type, filename in schema_files.items():
            schema_path = self.schemas_dir / filename
            if schema_path.exists():
                try:
                    with open(schema_path) as f:
                        schema = json.load(f)
                        self.schemas[obs_type] = schema
                        
                        # Create validator with resolver for $ref
                        resolver = RefResolver(
                            base_uri=f"file://{self.schemas_dir}/",
                            referrer=schema
                        )
                        self.validators[obs_type] = Draft7Validator(
                            schema, 
                            resolver=resolver
                        )
                        
                except Exception as e:
                    logger.error(f"Failed to load schema {filename}: {e}")
        
        logger.info(f"Loaded {len(self.schemas)} observation schemas")
    
    def validate_observation(self, observation: Dict[str, Any]) -> ValidationResult:
        """Validate a single observation.
        
        Args:
            observation: Observation to validate
            
        Returns:
            ValidationResult with errors and warnings
        """
        if self.validation_level == ValidationLevel.DISABLED:
            return ValidationResult(
                valid=True,
                errors=[],
                warnings=[],
                observation_type=observation.get('type', 'unknown')
            )
        
        obs_type = observation.get('type', '')
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = ['id', 'type', 'source_agent', 'timestamp', 'data']
        for field in required_fields:
            if field not in observation:
                errors.append(f"Missing required field: {field}")
        
        if not obs_type:
            errors.append("Observation type cannot be empty")
            return ValidationResult(
                valid=False,
                errors=errors,
                warnings=warnings,
                observation_type='unknown'
            )
        
        # Get validator for this type
        validator = self.validators.get(obs_type)
        
        if not validator:
            # No specific schema for this type, use base schema
            if 'base' in self.validators:
                validator = self.validators['base']
                warnings.append(f"No specific schema for type '{obs_type}', using base schema")
            else:
                warnings.append(f"No schema available for type '{obs_type}'")
                return ValidationResult(
                    valid=self.validation_level != ValidationLevel.STRICT,
                    errors=errors,
                    warnings=warnings,
                    observation_type=obs_type
                )
        
        # Validate against schema
        try:
            validator.validate(observation)
        except ValidationError as e:
            if self.validation_level == ValidationLevel.STRICT:
                errors.append(f"Schema validation failed: {e.message}")
            else:
                warnings.append(f"Schema validation warning: {e.message}")
        
        # Additional semantic validation
        semantic_errors, semantic_warnings = self._semantic_validation(observation)
        errors.extend(semantic_errors)
        warnings.extend(semantic_warnings)
        
        # Determine if valid based on validation level
        if self.validation_level == ValidationLevel.STRICT:
            valid = len(errors) == 0
        else:
            valid = len([e for e in errors if "Missing required field" in e]) == 0
        
        return ValidationResult(
            valid=valid,
            errors=errors,
            warnings=warnings,
            observation_type=obs_type,
            schema_used=f"{obs_type}_schema.json" if validator else None
        )
    
    def _semantic_validation(self, observation: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Perform semantic validation beyond schema.
        
        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []
        
        obs_type = observation.get('type')
        data = observation.get('data', {})
        metadata = observation.get('metadata', {})
        
        # Type-specific semantic validation
        if obs_type == 'todo':
            # Check if priority matches keywords
            text = data.get('text', '').upper()
            priority = metadata.get('priority', 50)
            
            if 'CRITICAL' in text and priority < 80:
                warnings.append("TODO contains 'CRITICAL' but priority is low")
            elif 'ASAP' in text and priority < 70:
                warnings.append("TODO contains 'ASAP' but priority is moderate")
        
        elif obs_type == 'security_issue':
            # Ensure critical security issues have high priority
            severity = metadata.get('severity')
            priority = metadata.get('priority', 50)
            
            if severity == 'critical' and priority < 90:
                warnings.append("Critical security issue should have priority >= 90")
            elif severity == 'high' and priority < 70:
                warnings.append("High security issue should have priority >= 70")
        
        elif obs_type == 'file_analysis':
            # Check metrics consistency
            metrics = data.get('metrics', {})
            loc = metrics.get('lines_of_code', 0)
            functions = metrics.get('functions', 0)
            
            if functions > 0 and loc == 0:
                warnings.append("File has functions but no lines of code")
        
        # General semantic checks
        timestamp = observation.get('timestamp', 0)
        if timestamp > 2000000000:  # Year 2033
            warnings.append("Timestamp appears to be in the future")
        elif timestamp < 1000000000:  # Year 2001
            warnings.append("Timestamp appears to be too old")
        
        return errors, warnings
    
    def validate_batch(self, observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a batch of observations.
        
        Args:
            observations: List of observations to validate
            
        Returns:
            Summary of validation results
        """
        results = []
        type_counts = {}
        error_counts = {}
        
        for obs in observations:
            result = self.validate_observation(obs)
            results.append(result)
            
            # Count by type
            obs_type = result.observation_type
            type_counts[obs_type] = type_counts.get(obs_type, 0) + 1
            
            # Count errors
            if not result.valid:
                error_counts[obs_type] = error_counts.get(obs_type, 0) + 1
        
        # Calculate summary
        total_valid = sum(1 for r in results if r.valid)
        total_errors = sum(len(r.errors) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)
        
        return {
            'total_observations': len(observations),
            'valid_observations': total_valid,
            'invalid_observations': len(observations) - total_valid,
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'type_counts': type_counts,
            'error_counts': error_counts,
            'validation_level': self.validation_level.value,
            'results': results
        }
    
    def get_schema_for_type(self, obs_type: str) -> Optional[Dict[str, Any]]:
        """Get the schema for a specific observation type.
        
        Args:
            obs_type: Observation type
            
        Returns:
            Schema dict or None if not found
        """
        return self.schemas.get(obs_type)
    
    def list_supported_types(self) -> List[str]:
        """List all observation types with schemas.
        
        Returns:
            List of supported observation types
        """
        return list(self.validators.keys())
    
    def add_custom_schema(self, obs_type: str, schema: Dict[str, Any]):
        """Add a custom schema for validation.
        
        Args:
            obs_type: Observation type
            schema: JSON schema dict
        """
        try:
            # Create validator
            validator = Draft7Validator(schema)
            self.validators[obs_type] = validator
            self.schemas[obs_type] = schema
            
            logger.info(f"Added custom schema for type: {obs_type}")
        except Exception as e:
            logger.error(f"Failed to add custom schema: {e}")
            raise