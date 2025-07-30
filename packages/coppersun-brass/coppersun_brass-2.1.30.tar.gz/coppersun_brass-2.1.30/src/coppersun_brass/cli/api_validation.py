"""
API key validation utilities.

Provides secure validation of API keys before storage to prevent
invalid keys from being saved in configuration.
"""

import asyncio
import logging
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)

# Try to import Anthropic client for validation
try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    logger.warning("anthropic package not available - API key validation disabled")


class APIKeyValidator:
    """Validates API keys by making test calls to their respective services."""
    
    def __init__(self):
        """Initialize API key validator."""
        self.timeout_seconds = 10  # Reasonable timeout for validation
    
    def validate_claude_api_key(self, api_key: str) -> Tuple[bool, str]:
        """Validate Claude API key by making a test call.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not api_key:
            return False, "API key is empty"
        
        # Basic format validation
        if not api_key.startswith('sk-ant-'):
            return False, "API key format invalid (should start with 'sk-ant-')"
        
        if len(api_key) < 40:
            return False, "API key too short (minimum 40 characters)"
        
        # If Anthropic client not available, only do format validation
        if not HAS_ANTHROPIC:
            logger.warning("Cannot test API key - anthropic package not installed")
            return True, "Format validation passed (network test skipped)"
        
        try:
            # Make a minimal test call to validate the key
            client = Anthropic(api_key=api_key)
            
            # Use a very short message to minimize cost and response time
            response = client.messages.create(
                model="claude-3-haiku-20240307",  # Fastest/cheapest model
                max_tokens=1,  # Minimal tokens
                messages=[{
                    "role": "user",
                    "content": "Hi"  # Minimal message
                }]
            )
            
            # If we get here, the API key works
            return True, "API key validated successfully"
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Parse common error types for better user feedback
            if 'authentication' in error_str or 'invalid' in error_str:
                return False, "API key is invalid or expired"
            elif 'quota' in error_str or 'billing' in error_str:
                return False, "API key valid but account has billing/quota issues"
            elif 'rate' in error_str or 'limit' in error_str:
                return False, "API key valid but rate limited (try again later)"
            elif 'network' in error_str or 'timeout' in error_str:
                # Network issues - assume key is valid
                logger.warning(f"Network error during validation: {e}")
                return True, "Format validation passed (network test failed)"
            else:
                logger.warning(f"Unexpected error during API validation: {e}")
                return False, f"Validation failed: {str(e)[:100]}"
    
    def validate_lemonsqueezy_api_key(self, api_key: str) -> Tuple[bool, str]:
        """Validate LemonSqueezy API key.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not api_key:
            return False, "API key is empty"
        
        # Basic format validation for LemonSqueezy keys
        if len(api_key) < 20:
            return False, "API key too short"
        
        # TODO: Add actual LemonSqueezy API validation when needed
        # For now, just do basic format validation
        return True, "Format validation passed"


def validate_api_key(key_type: str, api_key: str) -> Tuple[bool, str]:
    """Validate an API key of the specified type.
    
    Args:
        key_type: Type of API key ('claude_api_key', 'lemonsqueezy_api_key')
        api_key: The API key to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    validator = APIKeyValidator()
    
    if key_type == 'claude_api_key':
        return validator.validate_claude_api_key(api_key)
    elif key_type == 'lemonsqueezy_api_key':
        return validator.validate_lemonsqueezy_api_key(api_key)
    else:
        return False, f"Unknown API key type: {key_type}"


def validate_config_api_keys(config: Dict[str, Any]) -> Dict[str, Tuple[bool, str]]:
    """Validate all API keys in a configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dictionary mapping key names to (is_valid, message) tuples
    """
    results = {}
    
    if 'user_preferences' in config:
        prefs = config['user_preferences']
        
        # Validate each API key type
        for key_type in ['claude_api_key', 'lemonsqueezy_api_key']:
            if key_type in prefs and prefs[key_type]:
                results[key_type] = validate_api_key(key_type, prefs[key_type])
    
    return results