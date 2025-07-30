"""
Configuration encryption utilities for secure API key storage.

Provides encryption/decryption for sensitive configuration data using
machine-specific key derivation for enhanced security.
"""

import os
import json
import base64
import hashlib
import platform
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class ConfigEncryption:
    """Handles encryption/decryption of configuration files."""
    
    def __init__(self):
        """Initialize encryption with machine-specific key."""
        self._key = None
        self._salt = self._get_machine_salt()
    
    def _get_machine_salt(self) -> bytes:
        """Generate consistent salt based on machine characteristics."""
        # Combine machine-specific information for consistent salt
        machine_info = f"{platform.node()}{platform.machine()}{platform.system()}"
        
        # Add user home directory for additional uniqueness
        user_home = str(Path.home())
        
        # Create deterministic salt from machine + user info
        salt_data = f"{machine_info}{user_home}".encode()
        return hashlib.sha256(salt_data).digest()[:16]  # 16 bytes for salt
    
    def _get_encryption_key(self) -> bytes:
        """Derive encryption key from machine characteristics."""
        if self._key is None:
            # Use PBKDF2 for key derivation
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,  # 256-bit key
                salt=self._salt,
                iterations=100000,  # Secure iteration count
            )
            
            # Create base key from machine + user info
            base_data = f"brass_config_{platform.node()}_{Path.home().name}".encode()
            key = base64.urlsafe_b64encode(kdf.derive(base_data))
            self._key = key
        
        return self._key
    
    def encrypt_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive fields in configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configuration with encrypted sensitive fields
        """
        # Create copy to avoid modifying original
        encrypted_config = json.loads(json.dumps(config))
        
        # Encrypt sensitive fields
        if 'user_preferences' in encrypted_config:
            prefs = encrypted_config['user_preferences']
            
            # Encrypt API keys
            for key in ['claude_api_key', 'lemonsqueezy_api_key']:
                if key in prefs and prefs[key]:
                    prefs[key] = self._encrypt_value(prefs[key])
        
        # Mark as encrypted for identification
        encrypted_config['_encrypted'] = True
        encrypted_config['_encryption_version'] = '1.0'
        
        return encrypted_config
    
    def decrypt_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt configuration if it contains encrypted fields.
        
        Args:
            config: Configuration dictionary (may be encrypted)
            
        Returns:
            Configuration with decrypted sensitive fields
        """
        # Check if config is encrypted
        if not config.get('_encrypted', False):
            return config  # Not encrypted, return as-is
        
        # Create copy to avoid modifying original
        decrypted_config = json.loads(json.dumps(config))
        
        # Decrypt sensitive fields
        if 'user_preferences' in decrypted_config:
            prefs = decrypted_config['user_preferences']
            
            # Decrypt API keys
            for key in ['claude_api_key', 'lemonsqueezy_api_key']:
                if key in prefs and prefs[key]:
                    try:
                        prefs[key] = self._decrypt_value(prefs[key])
                    except Exception as e:
                        # If decryption fails, treat as invalid/corrupted
                        prefs[key] = None
        
        # Remove encryption markers for clean config
        decrypted_config.pop('_encrypted', None)
        decrypted_config.pop('_encryption_version', None)
        
        return decrypted_config
    
    def _encrypt_value(self, value: str) -> str:
        """Encrypt a single value.
        
        Args:
            value: Plain text value to encrypt
            
        Returns:
            Encrypted value as base64 string
        """
        try:
            fernet = Fernet(self._get_encryption_key())
            encrypted_bytes = fernet.encrypt(value.encode())
            return base64.urlsafe_b64encode(encrypted_bytes).decode()
        except Exception:
            # If encryption fails, return None to indicate error
            return None
    
    def _decrypt_value(self, encrypted_value: str) -> Optional[str]:
        """Decrypt a single value.
        
        Args:
            encrypted_value: Base64 encrypted value
            
        Returns:
            Decrypted plain text value or None if decryption fails
        """
        try:
            fernet = Fernet(self._get_encryption_key())
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted_bytes = fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception:
            # Decryption failed - corrupted or wrong key
            return None
    
    def is_encrypted(self, config: Dict[str, Any]) -> bool:
        """Check if configuration contains encrypted data.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if config is encrypted
        """
        return config.get('_encrypted', False)
    
    def migrate_plain_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate plain text configuration to encrypted format.
        
        Args:
            config: Plain text configuration
            
        Returns:
            Encrypted configuration
        """
        if self.is_encrypted(config):
            return config  # Already encrypted
        
        # Check if there are any sensitive fields to encrypt
        has_sensitive_data = False
        if 'user_preferences' in config:
            prefs = config['user_preferences']
            for key in ['claude_api_key', 'lemonsqueezy_api_key']:
                if key in prefs and prefs[key]:
                    has_sensitive_data = True
                    break
        
        if not has_sensitive_data:
            return config  # No sensitive data to encrypt
        
        return self.encrypt_config(config)


# Global encryption instance
_encryption: Optional[ConfigEncryption] = None


def get_encryption() -> ConfigEncryption:
    """Get global encryption instance."""
    global _encryption
    if _encryption is None:
        _encryption = ConfigEncryption()
    return _encryption


def encrypt_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to encrypt configuration."""
    return get_encryption().encrypt_config(config)


def decrypt_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to decrypt configuration."""
    return get_encryption().decrypt_config(config)


def is_encrypted(config: Dict[str, Any]) -> bool:
    """Convenience function to check if config is encrypted."""
    return get_encryption().is_encrypted(config)


def migrate_plain_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to migrate plain config to encrypted."""
    return get_encryption().migrate_plain_config(config)