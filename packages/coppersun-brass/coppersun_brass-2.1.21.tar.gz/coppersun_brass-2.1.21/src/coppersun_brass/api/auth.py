"""
API Authentication

General Staff G6 Role: Access Control
JWT and API key authentication for the REST API
"""

import jwt
import json
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader

from coppersun_brass.core.context.dcp_manager import DCPManager

logger = logging.getLogger(__name__)

# Security schemes
bearer_scheme = HTTPBearer()
api_key_scheme = APIKeyHeader(name="X-API-Key")


class JWTAuthenticator:
    """
    JWT authentication with rotating keys
    
    General Staff G6 Role: Secure Access Management
    Manages JWT tokens with DCP-tracked usage patterns
    """
    
    def __init__(self, dcp_path: Optional[str] = None):
        """Initialize with MANDATORY DCP integration"""
        # DCP is MANDATORY
        self.dcp_manager = DCPManager(dcp_path)
        
        # Load or generate JWT secret
        self.jwt_secret = self._load_or_generate_jwt_secret()
        self.algorithm = "HS256"
        
        # Token settings
        self.access_token_expire = timedelta(hours=24)
        self.refresh_token_expire = timedelta(days=30)
    
    def _load_or_generate_jwt_secret(self) -> str:
        """Load or generate JWT secret (stored securely, not in DCP)"""
        secrets_path = Path.home() / '.brass' / 'secrets.json'
        secrets_path.parent.mkdir(exist_ok=True)
        
        try:
            if secrets_path.exists():
                with open(secrets_path, 'r') as f:
                    secrets_data = json.load(f)
                    if 'jwt_secret' in secrets_data:
                        return secrets_data['jwt_secret']
            
            # Generate new secret
            jwt_secret = secrets.token_urlsafe(32)
            
            # Save it
            secrets_data = {}
            if secrets_path.exists():
                with open(secrets_path, 'r') as f:
                    secrets_data = json.load(f)
                    
            secrets_data['jwt_secret'] = jwt_secret
            
            with open(secrets_path, 'w') as f:
                json.dump(secrets_data, f)
                
            logger.info("Generated new JWT secret")
            return jwt_secret
            
        except Exception as e:
            logger.error(f"Failed to load/generate JWT secret: {e}")
            # Fallback to random secret (not persistent)
            return secrets.token_urlsafe(32)
    
    def generate_access_token(self, 
                            user_id: str, 
                            scopes: List[str] = None) -> str:
        """Generate access token"""
        payload = {
            'sub': user_id,
            'scopes': scopes or [],
            'exp': datetime.utcnow() + self.access_token_expire,
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.algorithm)
        
        # Log token generation to DCP
        self.dcp_manager.add_observation(
            'auth_token_generated',
            {
                'user_id': user_id,
                'token_type': 'access',
                'scopes': scopes or [],
                'expires_in': self.access_token_expire.total_seconds()
            },
            source_agent='api_auth',
            priority=65
        )
        
        return token
    
    def generate_refresh_token(self, user_id: str) -> str:
        """Generate refresh token"""
        payload = {
            'sub': user_id,
            'exp': datetime.utcnow() + self.refresh_token_expire,
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.algorithm)
        
        # Log to DCP
        self.dcp_manager.add_observation(
            'auth_token_generated',
            {
                'user_id': user_id,
                'token_type': 'refresh',
                'expires_in': self.refresh_token_expire.total_seconds()
            },
            source_agent='api_auth',
            priority=65
        )
        
        return token
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode token"""
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.algorithm]
            )
            
            # Log successful verification
            self.dcp_manager.add_observation(
                'auth_token_verified',
                {
                    'user_id': payload.get('sub'),
                    'token_type': payload.get('type', 'unknown')
                },
                source_agent='api_auth',
                priority=60
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            # Log expired token
            self.dcp_manager.add_observation(
                'auth_token_expired',
                {},
                source_agent='api_auth',
                priority=70
            )
            raise HTTPException(status_code=401, detail="Token expired")
            
        except jwt.InvalidTokenError as e:
            # Log invalid token
            self.dcp_manager.add_observation(
                'auth_token_invalid',
                {'error': str(e)},
                source_agent='api_auth',
                priority=75
            )
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """Refresh access token using refresh token"""
        payload = self.verify_token(refresh_token)
        
        if payload.get('type') != 'refresh':
            raise HTTPException(
                status_code=401,
                detail="Invalid token type for refresh"
            )
        
        # Generate new access token
        return self.generate_access_token(
            payload['sub'],
            payload.get('scopes', [])
        )


class APIKeyManager:
    """
    API Key management
    
    General Staff G6 Role: Service Account Access
    Manages API keys for service-to-service authentication
    """
    
    def __init__(self, dcp_path: Optional[str] = None):
        """Initialize with MANDATORY DCP integration"""
        # DCP is MANDATORY
        self.dcp_manager = DCPManager(dcp_path)
        
        # Load API keys from secure storage
        self.api_keys = self._load_api_keys()
    
    def _load_api_keys(self) -> Dict[str, Dict[str, Any]]:
        """Load API keys from secure storage"""
        secrets_path = Path.home() / '.brass' / 'api_keys.json'
        
        try:
            if secrets_path.exists():
                with open(secrets_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Failed to load API keys: {e}")
            return {}
    
    def generate_api_key(self, 
                        service_name: str,
                        scopes: List[str] = None) -> str:
        """Generate new API key"""
        api_key = f"brass_{secrets.token_urlsafe(32)}"
        
        # Store key info
        self.api_keys[api_key] = {
            'service_name': service_name,
            'scopes': scopes or [],
            'created_at': datetime.utcnow().isoformat(),
            'active': True
        }
        
        # Save to secure storage
        self._save_api_keys()
        
        # Log to DCP
        self.dcp_manager.add_observation(
            'api_key_generated',
            {
                'service_name': service_name,
                'scopes': scopes or []
            },
            source_agent='api_auth',
            priority=70
        )
        
        return api_key
    
    def _save_api_keys(self) -> None:
        """Save API keys to secure storage"""
        secrets_path = Path.home() / '.brass' / 'api_keys.json'
        secrets_path.parent.mkdir(exist_ok=True)
        
        try:
            with open(secrets_path, 'w') as f:
                json.dump(self.api_keys, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save API keys: {e}")
    
    def verify_api_key(self, api_key: str) -> Dict[str, Any]:
        """Verify API key"""
        key_info = self.api_keys.get(api_key)
        
        if not key_info:
            # Log invalid attempt
            self.dcp_manager.add_observation(
                'api_key_invalid',
                {},
                source_agent='api_auth',
                priority=75
            )
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        if not key_info.get('active', True):
            # Log inactive key usage
            self.dcp_manager.add_observation(
                'api_key_inactive',
                {'service_name': key_info.get('service_name')},
                source_agent='api_auth',
                priority=70
            )
            raise HTTPException(status_code=401, detail="API key inactive")
        
        # Log successful verification
        self.dcp_manager.add_observation(
            'api_key_verified',
            {
                'service_name': key_info.get('service_name'),
                'scopes': key_info.get('scopes', [])
            },
            source_agent='api_auth',
            priority=60
        )
        
        return key_info
    
    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke API key"""
        if api_key in self.api_keys:
            self.api_keys[api_key]['active'] = False
            self.api_keys[api_key]['revoked_at'] = datetime.utcnow().isoformat()
            self._save_api_keys()
            
            # Log revocation
            self.dcp_manager.add_observation(
                'api_key_revoked',
                {
                    'service_name': self.api_keys[api_key].get('service_name')
                },
                source_agent='api_auth',
                priority=70
            )
            
            return True
        return False


# Dependency functions for FastAPI
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
) -> Dict[str, Any]:
    """Get current user from JWT token"""
    authenticator = JWTAuthenticator()
    payload = authenticator.verify_token(credentials.credentials)
    
    return {
        'user_id': payload['sub'],
        'scopes': payload.get('scopes', [])
    }


async def get_api_key_info(
    api_key: str = Security(api_key_scheme)
) -> Dict[str, Any]:
    """Get API key info"""
    manager = APIKeyManager()
    return manager.verify_api_key(api_key)


class AuthenticationRequired:
    """Dependency for routes requiring authentication"""
    
    def __init__(self, required_scopes: List[str] = None):
        self.required_scopes = required_scopes or []
    
    async def __call__(self, 
                      user: Optional[Dict] = None,
                      api_key: Optional[Dict] = None) -> Dict[str, Any]:
        """Verify authentication and scopes"""
        # Try JWT first
        if user:
            auth_info = user
        # Try API key
        elif api_key:
            auth_info = api_key
        else:
            raise HTTPException(
                status_code=401,
                detail="Authentication required"
            )
        
        # Check scopes
        user_scopes = set(auth_info.get('scopes', []))
        required_scopes = set(self.required_scopes)
        
        if required_scopes and not required_scopes.issubset(user_scopes):
            raise HTTPException(
                status_code=403,
                detail=f"Required scopes: {self.required_scopes}"
            )
        
        return auth_info