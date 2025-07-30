"""
FastAPI Application

General Staff G3 Role: External Operations Interface
Main API application with middleware and routing
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
from typing import Optional
import logging
import time

from coppersun_brass.api.routers import analysis, recommendations, patterns, integrations
from coppersun_brass.api.middleware import (
    JWTAuthMiddleware, RateLimitMiddleware, DCPLoggingMiddleware
)
from coppersun_brass.core.context.dcp_manager import DCPManager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    logger.info("Copper Sun Brass API starting up")
    
    # Initialize DCP manager
    app.state.dcp_manager = DCPManager()
    
    # Log startup to DCP
    app.state.dcp_manager.add_observation(
        'api_startup',
        {
            'version': app.version,
            'timestamp': time.time()
        },
        source_agent='api',
        priority=70
    )
    
    yield
    
    # Shutdown
    logger.info("Copper Sun Brass API shutting down")
    
    # Log shutdown to DCP
    app.state.dcp_manager.add_observation(
        'api_shutdown',
        {
            'timestamp': time.time()
        },
        source_agent='api',
        priority=70
    )


def create_app(
    dcp_path: Optional[str] = None,
    title: str = "Copper Sun Brass API",
    version: str = "1.0.0",
    enable_auth: bool = True,
    enable_rate_limit: bool = True
) -> FastAPI:
    """
    Create FastAPI application
    
    Args:
        dcp_path: Path to DCP context file
        title: API title
        version: API version
        enable_auth: Enable JWT authentication
        enable_rate_limit: Enable rate limiting
        
    Returns:
        Configured FastAPI application
    """
    # Create app with lifespan
    app = FastAPI(
        title=title,
        description="AI Development Intelligence Platform API",
        version=version,
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # Store DCP path
    app.state.dcp_path = dcp_path
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add custom middleware (order matters - last added is first executed)
    if enable_rate_limit:
        app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)
    
    if enable_auth:
        # Exclude docs from auth
        app.add_middleware(
            JWTAuthMiddleware,
            exclude_paths=["/api/docs", "/api/redoc", "/api/openapi.json", "/api/v1/auth"]
        )
    
    # Always add DCP logging
    app.add_middleware(DCPLoggingMiddleware)
    
    # Include routers
    app.include_router(
        analysis.router,
        prefix="/api/v1/analyze",
        tags=["analysis"]
    )
    app.include_router(
        recommendations.router,
        prefix="/api/v1/recommendations",
        tags=["recommendations"]
    )
    app.include_router(
        patterns.router,
        prefix="/api/v1/patterns",
        tags=["patterns"]
    )
    app.include_router(
        integrations.router,
        prefix="/api/v1/integrations",
        tags=["integrations"]
    )
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "name": "Copper Sun Brass API",
            "version": version,
            "status": "operational",
            "docs": "/api/docs"
        }
    
    # Health check
    @app.get("/api/v1/health")
    async def health_check(request: Request):
        """Health check endpoint"""
        dcp_manager = request.app.state.dcp_manager
        
        # Check various components
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "components": {
                "api": "operational",
                "dcp": "operational" if dcp_manager else "unavailable",
                "database": "operational",  # Would check actual DB
                "cache": "operational"  # Would check actual cache
            }
        }
        
        # Determine overall health
        if any(status != "operational" for status in health_status["components"].values()):
            health_status["status"] = "degraded"
            
        return health_status
    
    # Custom OpenAPI schema
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
            
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        
        # Add security scheme
        openapi_schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            },
            "apiKey": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key"
            }
        }
        
        # Add global security
        openapi_schema["security"] = [
            {"bearerAuth": []},
            {"apiKey": []}
        ]
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
        
    app.openapi = custom_openapi
    
    return app


# Create default app instance
app = create_app()