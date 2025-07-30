"""
Pure Python security utilities using only stdlib.

This module provides encryption and API validation using only Python standard library,
eliminating external dependencies while maintaining security.

Blood Oath Compliant: Zero external dependencies.
"""

import hashlib
import hmac
import base64
import secrets
import os
import platform
from typing import Dict, Any, Tuple, Optional


class PurePythonEncryption:
    """
    Pure Python encryption using stdlib only.
    
    Uses PBKDF2 for key derivation, XOR cipher with HMAC authentication.
    Machine-specific key derivation for security.
    """
    
    def __init__(self):
        """Initialize with machine-specific parameters."""
        self.salt_size = 32
        self.key_size = 32
        self.hmac_size = 32
        self.iterations = 100000  # PBKDF2 iterations
    
    def _get_machine_seed(self) -> bytes:
        """Generate machine-specific seed for key derivation."""
        # Combine multiple machine-specific values
        machine_data = [
            platform.node(),           # Machine hostname
            platform.machine(),        # Machine type
            platform.processor(),      # Processor info
            str(os.getuid() if hasattr(os, 'getuid') else 'windows'),  # User ID
        ]
        
        # Join and encode
        machine_string = "|".join(machine_data)
        return machine_string.encode('utf-8')
    
    def _derive_key(self, salt: bytes) -> bytes:
        """Derive encryption key using PBKDF2 with machine-specific seed."""
        machine_seed = self._get_machine_seed()
        
        # Use PBKDF2 with machine-specific seed as password
        key = hashlib.pbkdf2_hmac(
            'sha256',
            machine_seed,
            salt,
            self.iterations,
            self.key_size
        )
        
        return key
    
    def _xor_encrypt_decrypt(self, data: bytes, key: bytes) -> bytes:
        """XOR cipher for encryption/decryption."""
        # Extend key to match data length
        key_extended = (key * ((len(data) // len(key)) + 1))[:len(data)]
        
        # XOR operation
        result = bytes(a ^ b for a, b in zip(data, key_extended))
        return result
    
    def _compute_hmac(self, data: bytes, key: bytes) -> bytes:
        """Compute HMAC for authentication."""
        return hmac.new(key, data, hashlib.sha256).digest()
    
    def encrypt_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt sensitive configuration data.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Encrypted configuration with metadata
        """
        # Create a deep copy to avoid modifying original
        import copy
        encrypted_config = copy.deepcopy(config)
        
        # Find sensitive data to encrypt
        sensitive_data = {}
        if 'user_preferences' in config:
            prefs = config['user_preferences']
            for key in ['claude_api_key', 'lemonsqueezy_api_key']:
                if key in prefs and prefs[key]:
                    sensitive_data[key] = prefs[key]
        
        if not sensitive_data:
            # No sensitive data to encrypt
            return encrypted_config
        
        # Generate random salt
        salt = secrets.token_bytes(self.salt_size)
        
        # Derive encryption key
        encryption_key = self._derive_key(salt)
        
        # Serialize sensitive data
        import json
        sensitive_json = json.dumps(sensitive_data).encode('utf-8')
        
        # Encrypt sensitive data
        encrypted_data = self._xor_encrypt_decrypt(sensitive_json, encryption_key)
        
        # Compute HMAC for authentication
        auth_key = self._derive_key(salt + b'auth')
        hmac_tag = self._compute_hmac(encrypted_data, auth_key)
        
        # Encode for JSON storage
        encrypted_payload = {
            'salt': base64.b64encode(salt).decode('ascii'),
            'data': base64.b64encode(encrypted_data).decode('ascii'),
            'hmac': base64.b64encode(hmac_tag).decode('ascii')
        }
        
        # Replace sensitive data with encrypted payload
        encrypted_config['_encrypted'] = True
        encrypted_config['_encrypted_data'] = encrypted_payload
        
        # Remove sensitive data from main config
        if 'user_preferences' in encrypted_config:
            for key in sensitive_data.keys():
                encrypted_config['user_preferences'][key] = '[ENCRYPTED]'
        
        return encrypted_config
    
    def decrypt_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt configuration data.
        
        Args:
            config: Potentially encrypted configuration
            
        Returns:
            Decrypted configuration
        """
        # Check if config is encrypted
        if not config.get('_encrypted') or '_encrypted_data' not in config:
            return config
        
        try:
            # Extract encrypted data
            encrypted_payload = config['_encrypted_data']
            
            # Decode from base64
            salt = base64.b64decode(encrypted_payload['salt'])
            encrypted_data = base64.b64decode(encrypted_payload['data'])
            stored_hmac = base64.b64decode(encrypted_payload['hmac'])
            
            # Derive keys
            encryption_key = self._derive_key(salt)
            auth_key = self._derive_key(salt + b'auth')
            
            # Verify HMAC
            computed_hmac = self._compute_hmac(encrypted_data, auth_key)
            if not hmac.compare_digest(computed_hmac, stored_hmac):
                raise ValueError("HMAC verification failed - data may be corrupted or tampered with")
            
            # Decrypt data
            decrypted_bytes = self._xor_encrypt_decrypt(encrypted_data, encryption_key)
            
            # Parse JSON
            import json
            sensitive_data = json.loads(decrypted_bytes.decode('utf-8'))
            
            # Create decrypted config
            decrypted_config = config.copy()
            
            # Remove encryption metadata
            decrypted_config.pop('_encrypted', None)
            decrypted_config.pop('_encrypted_data', None)
            
            # Restore sensitive data
            if 'user_preferences' not in decrypted_config:
                decrypted_config['user_preferences'] = {}
            
            decrypted_config['user_preferences'].update(sensitive_data)
            
            return decrypted_config
            
        except Exception as e:
            # If decryption fails, return original config
            print(f"Warning: Could not decrypt config: {e}")
            return config


class PurePythonAPIValidator:
    """
    Pure Python API key validation using format checks only.
    
    No external dependencies - validates format and provides helpful guidance.
    """
    
    def validate_claude_api_key(self, api_key: str) -> Tuple[bool, str]:
        """
        Validate Claude API key format.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not api_key:
            return False, "API key is empty"
        
        # Format validation
        if not api_key.startswith('sk-ant-'):
            return False, "API key format invalid (should start with 'sk-ant-')"
        
        if len(api_key) < 40:
            return False, "API key too short (minimum 40 characters)"
        
        # Check for obvious test/invalid patterns
        if 'test' in api_key.lower() or 'fake' in api_key.lower():
            return False, "API key appears to be a test/fake key"
        
        # Format is valid
        return True, "API key format is valid (network validation disabled for security)"
    
    def validate_lemonsqueezy_api_key(self, api_key: str) -> Tuple[bool, str]:
        """
        Validate LemonSqueezy API key format.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not api_key:
            return False, "API key is empty"
        
        if len(api_key) < 20:
            return False, "API key too short"
        
        return True, "API key format is valid"


def validate_api_key(key_type: str, api_key: str) -> Tuple[bool, str]:
    """
    Validate an API key of the specified type.
    
    Args:
        key_type: Type of API key ('claude_api_key', 'lemonsqueezy_api_key')
        api_key: The API key to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    validator = PurePythonAPIValidator()
    
    if key_type == 'claude_api_key':
        return validator.validate_claude_api_key(api_key)
    elif key_type == 'lemonsqueezy_api_key':
        return validator.validate_lemonsqueezy_api_key(api_key)
    else:
        return False, f"Unknown API key type: {key_type}"