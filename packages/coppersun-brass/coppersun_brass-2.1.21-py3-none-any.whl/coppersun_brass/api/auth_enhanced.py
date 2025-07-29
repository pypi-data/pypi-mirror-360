"""
Enhanced API Authentication for Copper Alloy Brass v1.0
Adds rate limiting, IP restrictions, and audit logging.
"""

import jwt
import json
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import logging
from collections import defaultdict
import time

from fastapi import HTTPException, Request
from coppersun_brass.core.security import validate_string, InputValidationError

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, rate: int = 100, per: int = 3600):
        """
        Initialize rate limiter.
        
        Args:
            rate: Number of requests allowed
            per: Time period in seconds
        """
        self.rate = rate
        self.per = per
        self.allowance = defaultdict(lambda: rate)
        self.last_check = defaultdict(time.time)
    
    def is_allowed(self, key: str) -> Tuple[bool, Dict[str, int]]:
        """Check if request is allowed."""
        current = time.time()
        time_passed = current - self.last_check[key]
        self.last_check[key] = current
        
        # Refill tokens
        self.allowance[key] += time_passed * (self.rate / self.per)
        if self.allowance[key] > self.rate:
            self.allowance[key] = self.rate
        
        # Check if allowed
        if self.allowance[key] < 1.0:
            return False, {
                'limit': self.rate,
                'remaining': int(self.allowance[key]),
                'reset': int(current + self.per)
            }
        
        self.allowance[key] -= 1.0
        return True, {
            'limit': self.rate,
            'remaining': int(self.allowance[key]),
            'reset': int(current + self.per)
        }


class IPRestrictor:
    """IP-based access control."""
    
    def __init__(self):
        self.whitelist = set()
        self.blacklist = set()
        self._load_lists()
    
    def _load_lists(self):
        """Load IP lists from configuration."""
        config_path = Path.home() / '.brass' / 'ip_restrictions.json'
        if config_path.exists():
            try:
                with open(config_path) as f:
                    data = json.load(f)
                    self.whitelist = set(data.get('whitelist', []))
                    self.blacklist = set(data.get('blacklist', []))
            except Exception as e:
                logger.error(f"Failed to load IP restrictions: {e}")
    
    def is_allowed(self, ip: str) -> bool:
        """Check if IP is allowed."""
        # If whitelist exists, only allow those IPs
        if self.whitelist:
            return ip in self.whitelist
        
        # Otherwise, block blacklisted IPs
        return ip not in self.blacklist
    
    def add_to_blacklist(self, ip: str, reason: str = ""):
        """Add IP to blacklist."""
        self.blacklist.add(ip)
        self._save_lists()
        logger.warning(f"Blacklisted IP {ip}: {reason}")
    
    def _save_lists(self):
        """Save IP lists."""
        config_path = Path.home() / '.brass' / 'ip_restrictions.json'
        config_path.parent.mkdir(exist_ok=True)
        
        try:
            with open(config_path, 'w') as f:
                json.dump({
                    'whitelist': list(self.whitelist),
                    'blacklist': list(self.blacklist)
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save IP restrictions: {e}")


class AuditLogger:
    """Security audit logging."""
    
    def __init__(self):
        self.log_path = Path.home() / '.brass' / 'security_audit.log'
        self.log_path.parent.mkdir(exist_ok=True)
    
    def log_auth_attempt(self, 
                        event_type: str,
                        ip: str,
                        user_id: Optional[str] = None,
                        success: bool = True,
                        details: Optional[Dict] = None):
        """Log authentication event."""
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'ip': ip,
            'user_id': user_id,
            'success': success,
            'details': details or {}
        }
        
        try:
            with open(self.log_path, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")


class EnhancedAuthenticator:
    """Enhanced authentication with security features."""
    
    def __init__(self):
        self.jwt_secret = self._load_or_generate_jwt_secret()
        self.algorithm = "HS256"
        
        # Security components
        self.rate_limiter = RateLimiter(rate=100, per=3600)  # 100 req/hour
        self.ip_restrictor = IPRestrictor()
        self.audit_logger = AuditLogger()
        
        # Token settings with shorter expiration
        self.access_token_expire = timedelta(hours=1)  # Shorter for security
        self.refresh_token_expire = timedelta(days=7)
        
        # Failed attempt tracking
        self.failed_attempts = defaultdict(int)
        self.lockout_threshold = 5
        self.lockout_duration = timedelta(minutes=15)
        self.lockout_until = {}
    
    def _load_or_generate_jwt_secret(self) -> str:
        """Load or generate JWT secret with rotation support."""
        secrets_path = Path.home() / '.brass' / 'jwt_secrets.json'
        secrets_path.parent.mkdir(exist_ok=True)
        
        try:
            if secrets_path.exists():
                with open(secrets_path, 'r') as f:
                    secrets_data = json.load(f)
                    
                    # Support key rotation
                    if 'current' in secrets_data:
                        return secrets_data['current']
            
            # Generate new secret
            jwt_secret = secrets.token_urlsafe(64)  # Longer for security
            
            # Save with rotation support
            secrets_data = {
                'current': jwt_secret,
                'previous': None,  # For graceful rotation
                'created_at': datetime.utcnow().isoformat(),
                'rotate_after_days': 90
            }
            
            with open(secrets_path, 'w') as f:
                json.dump(secrets_data, f, indent=2)
            
            # Secure file permissions
            import os
            os.chmod(secrets_path, 0o600)
            
            logger.info("Generated new JWT secret")
            return jwt_secret
            
        except Exception as e:
            logger.error(f"Failed to load/generate JWT secret: {e}")
            raise RuntimeError("Cannot initialize authentication")
    
    def authenticate(self, 
                    request: Request,
                    token: str) -> Dict[str, Any]:
        """Authenticate request with full security checks."""
        client_ip = request.client.host
        
        # Check IP restrictions
        if not self.ip_restrictor.is_allowed(client_ip):
            self.audit_logger.log_auth_attempt(
                'ip_blocked', client_ip, success=False
            )
            raise HTTPException(status_code=403, detail="IP blocked")
        
        # Check lockout
        if client_ip in self.lockout_until:
            if datetime.utcnow() < self.lockout_until[client_ip]:
                self.audit_logger.log_auth_attempt(
                    'lockout', client_ip, success=False
                )
                raise HTTPException(status_code=429, detail="Too many failed attempts")
            else:
                # Lockout expired
                del self.lockout_until[client_ip]
                self.failed_attempts[client_ip] = 0
        
        # Check rate limit
        allowed, rate_info = self.rate_limiter.is_allowed(client_ip)
        if not allowed:
            self.audit_logger.log_auth_attempt(
                'rate_limited', client_ip, success=False, details=rate_info
            )
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded",
                headers={
                    'X-RateLimit-Limit': str(rate_info['limit']),
                    'X-RateLimit-Remaining': str(rate_info['remaining']),
                    'X-RateLimit-Reset': str(rate_info['reset'])
                }
            )
        
        # Verify token
        try:
            # Validate token format
            token = validate_string(token, max_length=500, name="JWT token")
            
            payload = jwt.decode(
                token, 
                self.jwt_secret, 
                algorithms=[self.algorithm]
            )
            
            # Check token type
            if payload.get('type') != 'access':
                raise jwt.InvalidTokenError("Invalid token type")
            
            # Success
            self.audit_logger.log_auth_attempt(
                'jwt_success', 
                client_ip, 
                user_id=payload.get('sub'),
                success=True,
                details={'scopes': payload.get('scopes', [])}
            )
            
            # Reset failed attempts
            self.failed_attempts[client_ip] = 0
            
            return payload
            
        except jwt.ExpiredSignatureError:
            self._handle_failed_auth(client_ip, 'token_expired')
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError as e:
            self._handle_failed_auth(client_ip, 'invalid_token')
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
        except InputValidationError as e:
            self._handle_failed_auth(client_ip, 'validation_failed')
            raise HTTPException(status_code=400, detail=f"Invalid input: {e}")
        except Exception as e:
            self._handle_failed_auth(client_ip, 'unknown_error')
            logger.error(f"Authentication error: {e}")
            raise HTTPException(status_code=401, detail="Authentication failed")
    
    def _handle_failed_auth(self, ip: str, reason: str):
        """Handle failed authentication attempt."""
        self.failed_attempts[ip] += 1
        
        self.audit_logger.log_auth_attempt(
            reason, ip, success=False,
            details={'attempts': self.failed_attempts[ip]}
        )
        
        # Check for lockout
        if self.failed_attempts[ip] >= self.lockout_threshold:
            self.lockout_until[ip] = datetime.utcnow() + self.lockout_duration
            self.ip_restrictor.add_to_blacklist(
                ip, f"Too many failed attempts ({self.failed_attempts[ip]})"
            )
            logger.warning(f"IP {ip} locked out after {self.failed_attempts[ip]} attempts")
    
    def generate_token(self,
                      user_id: str,
                      scopes: List[str] = None,
                      ip: str = None) -> Dict[str, str]:
        """Generate access and refresh tokens."""
        # Validate input
        try:
            user_id = validate_string(user_id, max_length=100, name="user_id")
        except InputValidationError as e:
            raise ValueError(f"Invalid user_id: {e}")
        
        # Create tokens
        access_payload = {
            'sub': user_id,
            'scopes': scopes or [],
            'exp': datetime.utcnow() + self.access_token_expire,
            'iat': datetime.utcnow(),
            'type': 'access',
            'jti': secrets.token_urlsafe(16)  # Unique token ID
        }
        
        refresh_payload = {
            'sub': user_id,
            'exp': datetime.utcnow() + self.refresh_token_expire,
            'iat': datetime.utcnow(),
            'type': 'refresh',
            'jti': secrets.token_urlsafe(16)
        }
        
        access_token = jwt.encode(access_payload, self.jwt_secret, algorithm=self.algorithm)
        refresh_token = jwt.encode(refresh_payload, self.jwt_secret, algorithm=self.algorithm)
        
        # Log token generation
        self.audit_logger.log_auth_attempt(
            'token_generated', ip or 'unknown',
            user_id=user_id, success=True,
            details={'scopes': scopes or []}
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'expires_in': int(self.access_token_expire.total_seconds())
        }
    
    def refresh_token(self, 
                     refresh_token: str,
                     ip: str = None) -> Dict[str, str]:
        """Refresh access token using refresh token."""
        try:
            payload = jwt.decode(
                refresh_token,
                self.jwt_secret,
                algorithms=[self.algorithm]
            )
            
            # Check token type
            if payload.get('type') != 'refresh':
                raise jwt.InvalidTokenError("Not a refresh token")
            
            # Generate new access token
            return self.generate_token(
                user_id=payload['sub'],
                scopes=payload.get('scopes', []),
                ip=ip
            )
            
        except Exception as e:
            self.audit_logger.log_auth_attempt(
                'refresh_failed', ip or 'unknown',
                success=False, details={'error': str(e)}
            )
            raise HTTPException(status_code=401, detail="Invalid refresh token")