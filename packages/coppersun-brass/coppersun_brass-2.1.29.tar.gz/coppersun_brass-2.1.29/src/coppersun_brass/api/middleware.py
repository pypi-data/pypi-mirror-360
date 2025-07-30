"""
API Middleware

General Staff G3 Role: Request Processing Pipeline
Middleware for authentication, rate limiting, and logging
"""

import time
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from collections import defaultdict
import logging

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from coppersun_brass.api.auth import JWTAuthenticator, APIKeyManager

logger = logging.getLogger(__name__)


class DCPLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log all API requests to DCP
    
    General Staff G2 Role: API Intelligence Gathering
    Tracks all API usage for analysis and learning
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log to DCP"""
        start_time = time.time()
        
        # Get DCP manager from app state
        dcp_manager = getattr(request.app.state, 'dcp_manager', None)
        
        # Generate request ID
        request_id = f"req_{int(time.time() * 1000)}"
        request.state.request_id = request_id
        
        # Process request
        response = None
        error = None
        
        try:
            response = await call_next(request)
            return response
            
        except Exception as e:
            error = str(e)
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
            return response
            
        finally:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log to DCP if available
            if dcp_manager and response:
                try:
                    observation_data = {
                        'request_id': request_id,
                        'method': request.method,
                        'path': request.url.path,
                        'status_code': response.status_code,
                        'duration_ms': duration_ms,
                        'client_host': request.client.host if request.client else None,
                        'user_agent': request.headers.get('user-agent'),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                    if error:
                        observation_data['error'] = error
                    
                    # Determine priority based on status
                    if response.status_code >= 500:
                        priority = 80
                    elif response.status_code >= 400:
                        priority = 70
                    else:
                        priority = 60
                    
                    dcp_manager.add_observation(
                        'api_request',
                        observation_data,
                        source_agent='api',
                        priority=priority
                    )
                    
                except Exception as e:
                    logger.error(f"Failed to log to DCP: {e}")


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    JWT Authentication middleware
    
    General Staff G6 Role: Access Control Enforcement
    Enforces authentication requirements
    """
    
    def __init__(self, 
                 app: ASGIApp,
                 exclude_paths: List[str] = None):
        """
        Initialize middleware
        
        Args:
            app: ASGI application
            exclude_paths: Paths to exclude from auth
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or []
        self.authenticator = JWTAuthenticator()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check authentication"""
        # Skip excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Check for authorization header
        auth_header = request.headers.get('authorization')
        api_key_header = request.headers.get('x-api-key')
        
        if not auth_header and not api_key_header:
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required"}
            )
        
        # Verify JWT token
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                payload = self.authenticator.verify_token(token)
                request.state.user = {
                    'user_id': payload['sub'],
                    'scopes': payload.get('scopes', [])
                }
            except HTTPException as e:
                return JSONResponse(
                    status_code=e.status_code,
                    content={"detail": e.detail}
                )
        
        # Verify API key
        elif api_key_header:
            api_key_manager = APIKeyManager()
            try:
                key_info = api_key_manager.verify_api_key(api_key_header)
                request.state.api_key = key_info
            except HTTPException as e:
                return JSONResponse(
                    status_code=e.status_code,
                    content={"detail": e.detail}
                )
        
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware
    
    General Staff G4 Role: Resource Protection
    Prevents API abuse through rate limiting
    """
    
    def __init__(self,
                 app: ASGIApp,
                 max_requests: int = 100,
                 window_seconds: int = 60):
        """
        Initialize rate limiter
        
        Args:
            app: ASGI application
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        
        # In-memory storage (use Redis in production)
        self.requests = defaultdict(list)
    
    def _clean_old_requests(self, client_id: str) -> None:
        """Remove old requests outside the window"""
        cutoff = time.time() - self.window_seconds
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > cutoff
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply rate limiting"""
        # Get client identifier
        client_id = None
        
        # Check authenticated user
        if hasattr(request.state, 'user'):
            client_id = f"user_{request.state.user['user_id']}"
        # Check API key
        elif hasattr(request.state, 'api_key'):
            client_id = f"service_{request.state.api_key['service_name']}"
        # Fall back to IP
        elif request.client:
            client_id = f"ip_{request.client.host}"
        else:
            # Can't identify client, allow request
            return await call_next(request)
        
        # Clean old requests
        self._clean_old_requests(client_id)
        
        # Check rate limit
        request_count = len(self.requests[client_id])
        
        if request_count >= self.max_requests:
            # Log rate limit hit to DCP
            dcp_manager = getattr(request.app.state, 'dcp_manager', None)
            if dcp_manager:
                dcp_manager.add_observation(
                    'api_rate_limited',
                    {
                        'client_id': client_id,
                        'request_count': request_count,
                        'limit': self.max_requests,
                        'window_seconds': self.window_seconds
                    },
                    source_agent='api',
                    priority=70
                )
            
            # Calculate retry after
            oldest_request = min(self.requests[client_id])
            retry_after = int(oldest_request + self.window_seconds - time.time())
            
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
                headers={"Retry-After": str(retry_after)}
            )
        
        # Record request
        self.requests[client_id].append(time.time())
        
        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(
            self.max_requests - request_count - 1
        )
        response.headers["X-RateLimit-Reset"] = str(
            int(time.time() + self.window_seconds)
        )
        
        return response


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Response compression middleware
    
    Compresses responses for better performance
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply compression if supported"""
        response = await call_next(request)
        
        # Check if client supports gzip
        accept_encoding = request.headers.get('accept-encoding', '')
        if 'gzip' not in accept_encoding:
            return response
        
        # Only compress JSON responses
        content_type = response.headers.get('content-type', '')
        if 'application/json' not in content_type:
            return response
        
        # TODO: Implement actual compression
        # For now, just add header indicating we support it
        response.headers['Vary'] = 'Accept-Encoding'
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Security headers middleware
    
    Adds security headers to all responses
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers"""
        response = await call_next(request)
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        
        return response