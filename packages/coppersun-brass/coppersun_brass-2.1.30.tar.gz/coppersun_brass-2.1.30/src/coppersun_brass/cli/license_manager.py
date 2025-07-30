"""
License management for Copper Alloy Brass Pro.

This module handles license validation, generation, and management.
For v1.0, we use a simple but effective approach with checksums.
"""

import base64
import hashlib
import json
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

# Secret for v1.0 (in production, this would be properly secured)
LICENSE_SECRET = "brass-v1-secret-2025-change-in-production"

# Developer licenses that never expire
DEVELOPER_LICENSES = [
    "BRASS-DEVL-SCOTT-INTERNAL-2025",
    "BRASS-DEVL-DEMO-SHOWS-ONLY-2025",
    "BRASS-DEVL-TEST-SUITE-RUNNER-2025",
]


class LicenseInfo:
    """Container for license information."""
    
    def __init__(self, valid: bool, reason: str = "", **kwargs):
        self.valid = valid
        self.reason = reason
        self.type = kwargs.get("type", "unknown")
        self.email = kwargs.get("email", "")
        self.expires = kwargs.get("expires")
        self.features = kwargs.get("features", [])
        self.days_remaining = kwargs.get("days_remaining", 0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "valid": self.valid,
            "type": self.type,
            "email": self.email,
            "expires": self.expires,
            "features": self.features,
            "days_remaining": self.days_remaining
        }


class LicenseManager:
    """Manages Copper Alloy Brass Pro licenses."""
    
    @staticmethod
    def activate_lemonsqueezy_license(license_key: str, api_key: str = None) -> LicenseInfo:
        """
        Activate a LemonSqueezy license key via API.
        
        Args:
            license_key: The LemonSqueezy license key to activate
            
        Returns:
            LicenseInfo object with activation results
        """
        try:
            # Build headers for LemonSqueezy API
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # Live mode authentication
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            # LemonSqueezy license activation API
            response = requests.post(
                "https://api.lemonsqueezy.com/v1/licenses/activate",
                headers=headers,
                data={
                    "license_key": license_key,
                    "instance_name": "Brass CLI"
                },
                timeout=10
            )
            
            if response.status_code != 200:
                # Handle specific LemonSqueezy API error codes
                if response.status_code == 400:
                    return LicenseInfo(valid=False, reason="Invalid request parameters")
                elif response.status_code == 404:
                    return LicenseInfo(valid=False, reason="License key not found")
                elif response.status_code == 422:
                    return LicenseInfo(valid=False, reason="Validation failed")
                elif response.status_code == 429:
                    return LicenseInfo(valid=False, reason="Rate limit exceeded (60/min)")
                else:
                    return LicenseInfo(valid=False, reason=f"API error: {response.status_code}")
            
            data = response.json()
            
            # Check if activation was successful
            if not data.get("activated", False):
                error_msg = data.get("error", "Unknown activation error")
                return LicenseInfo(valid=False, reason=error_msg)
            
            # Extract license information
            license_data = data.get("license_key", {})
            meta_data = data.get("meta", {})
            
            # Verify this is for our product (security check)
            store_id = meta_data.get("store_id")
            product_id = meta_data.get("product_id")
            
            # These should match our LemonSqueezy store/product IDs
            expected_store_id = 193336  # Your live store ID
            expected_product_id = 561184  # Your live product ID
            
            if store_id != expected_store_id or product_id != expected_product_id:
                return LicenseInfo(valid=False, reason="License from wrong product")
            
            # Check license status
            status = license_data.get("status", "").lower()
            if status not in ["active", "enabled"]:
                return LicenseInfo(valid=False, reason=f"License status: {status}")
            
            # Extract customer info
            customer_email = meta_data.get("customer_email", "")
            customer_name = meta_data.get("customer_name", "")
            
            # Check activation limits
            activation_usage = license_data.get("activation_usage", 0)
            activation_limit = license_data.get("activation_limit", 1)
            
            # Calculate expiry (if applicable)
            expires_at = license_data.get("expires_at")
            expires_date = None
            days_remaining = None
            
            if expires_at:
                try:
                    expires_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    days_remaining = (expires_date - datetime.now()).days
                    
                    if days_remaining <= 0:
                        return LicenseInfo(valid=False, reason="License expired")
                except Exception:
                    pass  # Handle expiry parsing errors gracefully
            
            return LicenseInfo(
                valid=True,
                type="customer",
                email=customer_email,
                expires=expires_date.isoformat() if expires_date else None,
                days_remaining=days_remaining if days_remaining else 9999,
                features=["all"]  # LemonSqueezy customers get full access
            )
            
        except requests.exceptions.RequestException as e:
            return LicenseInfo(valid=False, reason=f"Network error: {str(e)}")
        except Exception as e:
            return LicenseInfo(valid=False, reason=f"Activation error: {str(e)}")

    @staticmethod
    def validate_lemonsqueezy_license(license_key: str, api_key: str = None) -> LicenseInfo:
        """
        Validate a LemonSqueezy license key via API (without activation).
        
        Note: This is used for checking already-activated licenses.
        For new licenses, use activate_lemonsqueezy_license() instead.
        
        Args:
            license_key: The LemonSqueezy license key to validate
            
        Returns:
            LicenseInfo object with validation results
        """
        try:
            # Build headers for LemonSqueezy API
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # Live mode authentication
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            # LemonSqueezy license validation API
            response = requests.post(
                "https://api.lemonsqueezy.com/v1/licenses/validate",
                headers=headers,
                data={"license_key": license_key},
                timeout=10
            )
            
            if response.status_code != 200:
                # Handle specific LemonSqueezy API error codes
                if response.status_code == 400:
                    return LicenseInfo(valid=False, reason="Invalid request parameters")
                elif response.status_code == 404:
                    return LicenseInfo(valid=False, reason="License key not found")
                elif response.status_code == 422:
                    return LicenseInfo(valid=False, reason="Validation failed")
                elif response.status_code == 429:
                    return LicenseInfo(valid=False, reason="Rate limit exceeded (60/min)")
                else:
                    return LicenseInfo(valid=False, reason=f"API error: {response.status_code}")
            
            data = response.json()
            
            # Check if license is valid
            if not data.get("valid", False):
                error_msg = data.get("error", "Unknown validation error")
                return LicenseInfo(valid=False, reason=error_msg)
            
            # Extract license information
            license_data = data.get("license_key", {})
            meta_data = data.get("meta", {})
            
            # Verify this is for our product (security check)
            store_id = meta_data.get("store_id")
            product_id = meta_data.get("variant_id") or meta_data.get("product_id")
            
            # These should match our LemonSqueezy store/product IDs
            expected_store_id = 193336  # Your live store ID
            expected_product_id = 561184  # Your live product ID
            
            if store_id != expected_store_id:
                return LicenseInfo(valid=False, reason="License from wrong store")
            
            # Check license status
            status = license_data.get("status", "").lower()
            if status not in ["active", "enabled"]:
                return LicenseInfo(valid=False, reason=f"License status: {status}")
            
            # Extract customer info
            customer_email = meta_data.get("customer_email", "")
            customer_name = meta_data.get("customer_name", "")
            
            # Check activation limits
            activation_usage = license_data.get("activation_usage", 0)
            activation_limit = license_data.get("activation_limit", 1)
            
            if activation_limit > 0 and activation_usage >= activation_limit:
                return LicenseInfo(valid=False, reason="Activation limit exceeded")
            
            # Calculate expiry (if applicable)
            expires_at = license_data.get("expires_at")
            expires_date = None
            days_remaining = None
            
            if expires_at:
                try:
                    expires_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    days_remaining = (expires_date - datetime.now()).days
                    
                    if days_remaining <= 0:
                        return LicenseInfo(valid=False, reason="License expired")
                except Exception:
                    pass  # Handle expiry parsing errors gracefully
            
            return LicenseInfo(
                valid=True,
                type="customer",
                email=customer_email,
                expires=expires_date.isoformat() if expires_date else None,
                days_remaining=days_remaining if days_remaining else 9999,
                features=["all"]  # LemonSqueezy customers get full access
            )
            
        except requests.exceptions.RequestException as e:
            return LicenseInfo(valid=False, reason=f"Network error: {str(e)}")
        except Exception as e:
            return LicenseInfo(valid=False, reason=f"Validation error: {str(e)}")
    
    @staticmethod
    def validate_license(license_key: str) -> LicenseInfo:
        """
        Validate a license key and return license information.
        
        Args:
            license_key: The license key to validate
            
        Returns:
            LicenseInfo object with validation results
        """
        # Check environment variable for developer override
        if os.environ.get("BRASS_DEV_MODE") == "true":
            return LicenseInfo(
                valid=True,
                type="developer",
                email="dev@coppersun_brass.local",
                features=["all"],
                expires=None
            )
        
        # Check developer licenses
        if license_key in DEVELOPER_LICENSES:
            return LicenseInfo(
                valid=True,
                type="developer",
                email="internal@coppersun_brass.ai",
                features=["all"],
                expires=None
            )
        
        # Check if this is a LemonSqueezy license (UUID format, not BRASS- prefix)
        # LemonSqueezy licenses are typically UUIDs like: 38b1460a-5104-4067-a91d-77b872934d51
        if not license_key.startswith("BRASS-") and len(license_key) >= 30:
            # Use live API key for LemonSqueezy validation
            api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI5NGQ1OWNlZi1kYmI4LTRlYTUtYjE3OC1kMjU0MGZjZDY5MTkiLCJqdGkiOiI2MzY3MzZiMWY4ZDc1NTJkZWRmNmZkMTgyYzk0ZjZjN2EwYjkyMTg2ZDUyMmY1NjlhYmE2NzQ2MWFlYWMyYWY4NjBhYjk2OWVjMmUzZDg0MSIsImlhdCI6MTc1MTc0MzY5MS43NTc1MjYsIm5iZiI6MTc1MTc0MzY5MS43NTc1MjksImV4cCI6MjA2NzI3NjQ5MS43MDg4NjMsInN1YiI6IjUwODczMDAiLCJzY29wZXMiOltdfQ.i-kMW1a06zzuGWM-rU4b6e3ArFSDuhBT7CFGmbMGAb7kuucX_JNOjgM4kPhtYM47B5MkLqKNcLdrrO0PJ7_LuP5DjRPasWYrXS4Z3EV8R5tTq93xeyNN12cgpEyCtHaIYeTsbni-Kua1XyikBd3XJ4XNxklOcS6V38se1rhQmQUDi27CbWUcBkOTPA2TrOCo1Tfvh2km9gKMAaYC_SJ28R0LAVFZdbenhO-428SH6n7u73-8sb65-lAwdUtOILcFUK2SyrgE3O2AuK8RYjPw7qO66S61fxgZKYzGs5-ld1C1EZktm1l188Ymvn_fOop536mjdD1aT0lAJdUGTlLhCRF2GINlJEr1vP2mvhnMZj6GD2X_916RG_rmHWPy-bfE_HsHGcmtHdJixdfY2rSgDjfPG_o4FCKI6QgjqoT4m6wiRtowiKZXNz4YWXZIBZOpFzE37sctZz-7FlGywXydT0uAlprUX-fQzeMHJd85EnH-8IZy-a1PIpQIo8hzOtXk"
            return LicenseManager.activate_lemonsqueezy_license(license_key, api_key)
        
        # Validate our BRASS format
        parts = license_key.split('-')
        if len(parts) != 5 or parts[0] != "BRASS":
            return LicenseInfo(valid=False, reason="Invalid license format")
        
        license_type = parts[1]
        
        # Handle different license types
        if license_type == "CUST":
            return LicenseManager._validate_customer_license(parts)
        elif license_type == "TRIAL":
            return LicenseManager._validate_trial_license(parts)
        else:
            return LicenseInfo(valid=False, reason="Unknown license type")
    
    @staticmethod
    def _validate_customer_license(parts: list) -> LicenseInfo:
        """Validate a customer license."""
        try:
            # Reconstruct data from parts
            data_str = f"{parts[2]}-{parts[3]}"
            checksum = parts[4]
            
            # Verify checksum
            expected_checksum = hashlib.sha256(
                f"{data_str}{LICENSE_SECRET}".encode()
            ).hexdigest()[:8].upper()
            
            if checksum != expected_checksum:
                return LicenseInfo(valid=False, reason="Invalid license checksum")
            
            # For v1.0, use simple encoding
            # Format: email_hash(8)-expiry_days(4)
            email_hash = data_str[:8]
            expiry_encoded = data_str[9:13]
            
            # Decode expiry (days since 2025-01-01)
            base_date = datetime(2025, 1, 1)
            try:
                days_offset = int(expiry_encoded, 16)
                expiry_date = base_date + timedelta(days=days_offset)
            except ValueError:
                return LicenseInfo(valid=False, reason="Invalid expiry encoding")
            
            # Check if expired
            now = datetime.now()
            if expiry_date < now:
                return LicenseInfo(valid=False, reason="License expired")
            
            days_remaining = (expiry_date - now).days
            
            return LicenseInfo(
                valid=True,
                type="customer",
                email=f"user_{email_hash}@customer",  # Obfuscated
                expires=expiry_date.isoformat(),
                days_remaining=days_remaining,
                features=["standard"]
            )
            
        except Exception as e:
            return LicenseInfo(valid=False, reason=f"License validation error: {str(e)}")
    
    @staticmethod
    def _validate_trial_license(parts: list) -> LicenseInfo:
        """Validate a trial license."""
        try:
            # Trial format: TRIAL-startdate(4)-duration(2)
            start_encoded = parts[2]
            duration_encoded = parts[3]
            checksum = parts[4]
            
            # Verify checksum
            data_str = f"{start_encoded}-{duration_encoded}"
            expected_checksum = hashlib.sha256(
                f"{data_str}{LICENSE_SECRET}".encode()
            ).hexdigest()[:8].upper()
            
            if checksum != expected_checksum:
                return LicenseInfo(valid=False, reason="Invalid trial license")
            
            # Decode start date and duration
            base_date = datetime(2025, 1, 1)
            start_offset = int(start_encoded, 16)
            start_date = base_date + timedelta(days=start_offset)
            duration_days = int(duration_encoded, 16)
            
            expiry_date = start_date + timedelta(days=duration_days)
            
            # Check if expired
            now = datetime.now()
            if expiry_date < now:
                return LicenseInfo(valid=False, reason="Trial expired")
            
            days_remaining = (expiry_date - now).days
            
            return LicenseInfo(
                valid=True,
                type="trial",
                email="trial@user",
                expires=expiry_date.isoformat(),
                days_remaining=days_remaining,
                features=["standard"]
            )
            
        except Exception as e:
            return LicenseInfo(valid=False, reason=f"Trial validation error: {str(e)}")
    
    @staticmethod
    def generate_customer_license(email: str, days: int = 365) -> str:
        """
        Generate a customer license key.
        
        Args:
            email: Customer email
            days: License duration in days
            
        Returns:
            License key string
        """
        # Generate email hash (first 8 chars of sha256)
        email_hash = hashlib.sha256(email.encode()).hexdigest()[:8].upper()
        
        # Calculate expiry as days since 2025-01-01
        base_date = datetime(2025, 1, 1)
        expiry_date = datetime.now() + timedelta(days=days)
        days_offset = (expiry_date - base_date).days
        
        # Encode as hex (4 chars)
        expiry_encoded = f"{days_offset:04X}"
        
        # Create data string
        data_str = f"{email_hash}-{expiry_encoded}"
        
        # Generate checksum
        checksum = hashlib.sha256(
            f"{data_str}{LICENSE_SECRET}".encode()
        ).hexdigest()[:8].upper()
        
        return f"BRASS-CUST-{email_hash}-{expiry_encoded}-{checksum}"
    
    @staticmethod
    def generate_trial_license(days: int = 30) -> str:
        """
        Generate a trial license key.
        
        Args:
            days: Trial duration in days (default 30)
            
        Returns:
            License key string
        """
        # Calculate start date as days since 2025-01-01
        base_date = datetime(2025, 1, 1)
        start_date = datetime.now()
        start_offset = (start_date - base_date).days
        
        # Encode start and duration as hex
        start_encoded = f"{start_offset:04X}"
        duration_encoded = f"{days:02X}"
        
        # Create data string
        data_str = f"{start_encoded}-{duration_encoded}"
        
        # Generate checksum
        checksum = hashlib.sha256(
            f"{data_str}{LICENSE_SECRET}".encode()
        ).hexdigest()[:8].upper()
        
        return f"BRASS-TRIAL-{start_encoded}-{duration_encoded}-{checksum}"


def generate_developer_license(identifier: str) -> str:
    """
    Generate a developer license that never expires.
    
    Args:
        identifier: Unique identifier for this dev license
        
    Returns:
        Developer license key
    """
    clean_id = identifier.upper().replace(' ', '-')[:16]
    return f"BRASS-DEVL-{clean_id}-2025"


if __name__ == "__main__":
    # Test license generation and validation
    print("Copper Alloy Brass License Manager Test\n")
    
    # Test developer license
    dev_license = DEVELOPER_LICENSES[0]
    print(f"Developer License: {dev_license}")
    result = LicenseManager.validate_license(dev_license)
    print(f"Valid: {result.valid}, Type: {result.type}\n")
    
    # Generate and test customer license
    customer_license = LicenseManager.generate_customer_license("test@example.com", 365)
    print(f"Customer License: {customer_license}")
    result = LicenseManager.validate_license(customer_license)
    print(f"Valid: {result.valid}, Days remaining: {result.days_remaining}\n")
    
    # Generate and test trial license
    trial_license = LicenseManager.generate_trial_license(30)
    print(f"Trial License: {trial_license}")
    result = LicenseManager.validate_license(trial_license)
    print(f"Valid: {result.valid}, Days remaining: {result.days_remaining}")