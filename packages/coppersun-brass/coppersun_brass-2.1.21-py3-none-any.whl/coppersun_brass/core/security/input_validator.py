"""
Input Validation Module for Copper Alloy Brass v1.0
Provides centralized input validation to prevent security vulnerabilities.
"""

import os
import re
from pathlib import Path
from typing import Optional, List, Union
import logging

logger = logging.getLogger(__name__)


class InputValidationError(Exception):
    """Raised when input validation fails."""
    pass


class InputValidator:
    """Centralized input validation for security."""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root).resolve() if project_root else Path.cwd().resolve()
        
        # Security constraints
        self.max_path_length = 4096
        self.max_string_length = 10000
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        
        # Allowed file extensions for analysis
        self.allowed_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', 
            '.h', '.hpp', '.cs', '.rb', '.go', '.rs', '.php', '.swift',
            '.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.ini',
            '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd'
        }
        
        # Dangerous patterns
        self.path_traversal_pattern = re.compile(r'\.\.[\\/]')
        self.null_byte_pattern = re.compile(r'\x00')
        
    def validate_path(self, 
                     path: Union[str, Path], 
                     must_exist: bool = False,
                     allow_outside_project: bool = False) -> Path:
        """
        Validate a file path for security issues.
        
        Args:
            path: Path to validate
            must_exist: Whether the path must exist
            allow_outside_project: Whether to allow paths outside project root
            
        Returns:
            Resolved, validated Path object
            
        Raises:
            InputValidationError: If validation fails
        """
        # Convert to string for initial checks
        path_str = str(path)
        
        # Check for null bytes
        if self.null_byte_pattern.search(path_str):
            raise InputValidationError("Path contains null bytes")
        
        # Check for path traversal attempts
        if self.path_traversal_pattern.search(path_str):
            raise InputValidationError("Path traversal detected")
        
        # Check length
        if len(path_str) > self.max_path_length:
            raise InputValidationError(f"Path too long: {len(path_str)} > {self.max_path_length}")
        
        # Resolve to absolute path
        try:
            resolved_path = Path(path).resolve()
        except Exception as e:
            raise InputValidationError(f"Invalid path: {e}")
        
        # Check if path exists (if required)
        if must_exist and not resolved_path.exists():
            raise InputValidationError(f"Path does not exist: {resolved_path}")
        
        # Check if path is within project root (if required)
        if not allow_outside_project:
            try:
                resolved_path.relative_to(self.project_root)
            except ValueError:
                raise InputValidationError(
                    f"Path outside project root: {resolved_path} not in {self.project_root}"
                )
        
        # Check file size if it's a file
        if resolved_path.is_file():
            file_size = resolved_path.stat().st_size
            if file_size > self.max_file_size:
                raise InputValidationError(
                    f"File too large: {file_size} > {self.max_file_size}"
                )
        
        return resolved_path
    
    def validate_string(self, 
                       value: str, 
                       max_length: Optional[int] = None,
                       allowed_chars: Optional[str] = None,
                       name: str = "string") -> str:
        """
        Validate a string input.
        
        Args:
            value: String to validate
            max_length: Maximum allowed length
            allowed_chars: Regex pattern of allowed characters
            name: Name of the field for error messages
            
        Returns:
            Validated string
            
        Raises:
            InputValidationError: If validation fails
        """
        if not isinstance(value, str):
            raise InputValidationError(f"{name} must be a string")
        
        # Check length
        max_len = max_length or self.max_string_length
        if len(value) > max_len:
            raise InputValidationError(
                f"{name} too long: {len(value)} > {max_len}"
            )
        
        # Check for null bytes
        if '\x00' in value:
            raise InputValidationError(f"{name} contains null bytes")
        
        # Check allowed characters
        if allowed_chars:
            pattern = re.compile(allowed_chars)
            if not pattern.match(value):
                raise InputValidationError(
                    f"{name} contains invalid characters"
                )
        
        return value
    
    def validate_identifier(self, value: str, name: str = "identifier") -> str:
        """
        Validate an identifier (alphanumeric + underscore).
        
        Args:
            value: Identifier to validate
            name: Name of the field
            
        Returns:
            Validated identifier
        """
        return self.validate_string(
            value,
            max_length=255,
            allowed_chars=r'^[a-zA-Z_][a-zA-Z0-9_]*$',
            name=name
        )
    
    def validate_config_value(self, key: str, value: any) -> any:
        """
        Validate a configuration value based on its key.
        
        Args:
            key: Configuration key
            value: Configuration value
            
        Returns:
            Validated value
            
        Raises:
            InputValidationError: If validation fails
        """
        # Validate the key itself
        self.validate_identifier(key, "config key")
        
        # Type-specific validation
        if isinstance(value, str):
            return self.validate_string(value, name=f"config.{key}")
        elif isinstance(value, (int, float)):
            # Check for reasonable bounds
            if abs(value) > 1e9:
                raise InputValidationError(f"config.{key} value too large")
            return value
        elif isinstance(value, bool):
            return value
        elif isinstance(value, list):
            # Validate each item
            return [self.validate_config_value(f"{key}[{i}]", item) 
                   for i, item in enumerate(value)]
        elif isinstance(value, dict):
            # Validate each key-value pair
            return {k: self.validate_config_value(f"{key}.{k}", v) 
                   for k, v in value.items()}
        else:
            raise InputValidationError(
                f"Unsupported config type for {key}: {type(value)}"
            )
    
    def validate_file_extension(self, path: Path) -> Path:
        """
        Validate that a file has an allowed extension.
        
        Args:
            path: File path to check
            
        Returns:
            The path if valid
            
        Raises:
            InputValidationError: If extension not allowed
        """
        if path.suffix.lower() not in self.allowed_extensions:
            raise InputValidationError(
                f"File type not allowed: {path.suffix}"
            )
        return path
    
    def sanitize_for_logging(self, value: str, max_length: int = 100) -> str:
        """
        Sanitize a string for safe logging.
        
        Args:
            value: String to sanitize
            max_length: Maximum length for logged value
            
        Returns:
            Sanitized string safe for logging
        """
        # Remove any control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', str(value))
        
        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "..."
        
        return sanitized
    
    def validate_api_input(self, data: dict, schema: dict) -> dict:
        """
        Validate API input against a schema.
        
        Args:
            data: Input data to validate
            schema: Expected schema with types and constraints
            
        Returns:
            Validated data
            
        Raises:
            InputValidationError: If validation fails
        """
        validated = {}
        
        for field, constraints in schema.items():
            # Check required fields
            if constraints.get('required', False) and field not in data:
                raise InputValidationError(f"Missing required field: {field}")
            
            if field in data:
                value = data[field]
                field_type = constraints.get('type')
                
                # Type validation
                if field_type == 'string':
                    validated[field] = self.validate_string(
                        value,
                        max_length=constraints.get('max_length'),
                        name=field
                    )
                elif field_type == 'path':
                    validated[field] = str(self.validate_path(
                        value,
                        must_exist=constraints.get('must_exist', False)
                    ))
                elif field_type == 'integer':
                    if not isinstance(value, int):
                        raise InputValidationError(f"{field} must be an integer")
                    min_val = constraints.get('min', float('-inf'))
                    max_val = constraints.get('max', float('inf'))
                    if not min_val <= value <= max_val:
                        raise InputValidationError(
                            f"{field} out of range: {min_val} <= {value} <= {max_val}"
                        )
                    validated[field] = value
                elif field_type == 'boolean':
                    if not isinstance(value, bool):
                        raise InputValidationError(f"{field} must be a boolean")
                    validated[field] = value
                else:
                    raise InputValidationError(f"Unknown field type: {field_type}")
        
        return validated


# Global validator instance
_validator = None


def get_validator(project_root: Optional[Path] = None) -> InputValidator:
    """Get or create the global validator instance."""
    global _validator
    if _validator is None or project_root:
        _validator = InputValidator(project_root)
    return _validator


# Convenience functions
def validate_path(path: Union[str, Path], **kwargs) -> Path:
    """Validate a path using the global validator."""
    return get_validator().validate_path(path, **kwargs)


def validate_string(value: str, **kwargs) -> str:
    """Validate a string using the global validator."""
    return get_validator().validate_string(value, **kwargs)


def validate_api_input(data: dict, schema: dict) -> dict:
    """Validate API input using the global validator."""
    return get_validator().validate_api_input(data, schema)