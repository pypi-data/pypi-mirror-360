"""
License backward compatibility layer for Copper Alloy Brass.

This module provides compatibility for old DEVMIND license formats
during the migration period.
"""

import os
from typing import Optional
from .license_manager import LicenseManager, LicenseInfo


class CompatibleLicenseManager:
    """License manager with backward compatibility for DEVMIND licenses."""
    
    @staticmethod
    def validate_license(license_key: str) -> LicenseInfo:
        """
        Validate a license key with backward compatibility.
        
        Supports both:
        - New format: BRASS-XXXX-XXXX-XXXX-XXXX
        - Old format: DEVMIND-XXXX-XXXX-XXXX-XXXX
        
        Args:
            license_key: The license key to validate
            
        Returns:
            LicenseInfo object with validation results
        """
        # First try the new format
        result = LicenseManager.validate_license(license_key)
        if result.valid:
            return result
            
        # If it starts with DEVMIND, convert and try again
        if license_key.startswith("DEVMIND-"):
            converted_key = license_key.replace("DEVMIND-", "BRASS-", 1)
            result = LicenseManager.validate_license(converted_key)
            if result.valid:
                # Add note about format conversion
                result.reason = "License validated (converted from DEVMIND format)"
            return result
            
        return result
    
    @staticmethod
    def get_license_from_env() -> Optional[str]:
        """
        Get license from environment with backward compatibility.
        
        Checks in order:
        1. BRASS_LICENSE
        2. COPPERALLOY_LICENSE  
        3. DEVMIND_LICENSE (for backward compatibility)
        
        Returns:
            License key string or None
        """
        # Check new environment variables first
        license_key = os.environ.get("BRASS_LICENSE")
        if license_key:
            return license_key
            
        license_key = os.environ.get("COPPERALLOY_LICENSE")
        if license_key:
            return license_key
            
        # Fall back to old environment variable
        license_key = os.environ.get("DEVMIND_LICENSE")
        if license_key:
            # Convert format if needed
            if license_key.startswith("DEVMIND-"):
                return license_key.replace("DEVMIND-", "BRASS-", 1)
            return license_key
            
        return None
    
    @staticmethod
    def check_dev_mode() -> bool:
        """
        Check if running in developer mode.
        
        Checks both new and old environment variables:
        - BRASS_DEV_MODE=true
        - DEVMIND_DEV_MODE=true (backward compatibility)
        
        Returns:
            True if in developer mode
        """
        return (
            os.environ.get("BRASS_DEV_MODE") == "true" or
            os.environ.get("DEVMIND_DEV_MODE") == "true"
        )


def migrate_license_file(old_path: str = "~/.devmind/license.key",
                        new_path: str = "~/.brass/license.key") -> bool:
    """
    Migrate license file from old location to new.
    
    Args:
        old_path: Path to old license file
        new_path: Path to new license file
        
    Returns:
        True if migration was performed
    """
    from pathlib import Path
    
    old_file = Path(old_path).expanduser()
    new_file = Path(new_path).expanduser()
    
    # If old file exists and new doesn't, migrate
    if old_file.exists() and not new_file.exists():
        # Create new directory if needed
        new_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Read old license
        old_content = old_file.read_text().strip()
        
        # Convert format if needed
        if old_content.startswith("DEVMIND-"):
            new_content = old_content.replace("DEVMIND-", "BRASS-", 1)
        else:
            new_content = old_content
            
        # Write to new location
        new_file.write_text(new_content)
        
        print(f"✅ Migrated license from {old_path} to {new_path}")
        return True
        
    return False