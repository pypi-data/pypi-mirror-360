"""Main API server for Copper Sun Brass production deployment.

This module provides the FastAPI application with all endpoints
for health monitoring, metrics, and Copper Sun Brass operations.
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from coppersun_brass.core.config_loader import get_config
from coppersun_brass.api.health_endpoint import router as health_router, set_production_monitor
from coppersun_brass.core.context.dcp_manager import DCPManager
from coppersun_brass.core.monitoring.health_monitor import ProductionHealthMonitor
from coppersun_brass.core.event_bus import EventBus

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    logger.info("Starting Copper Sun Brass API server...")
    
    # Initialize configuration
    config = get_config()
    
    # Initialize core components
    dcp_manager = DCPManager(str(config.project_root))
    event_bus = EventBus()
    
    # Initialize production health monitor
    prod_monitor = ProductionHealthMonitor(
        dcp_manager=dcp_manager,
        event_bus=event_bus,
        config={
            'check_interval': config.monitoring.health_check_interval,
            'thresholds': {
                'memory_usage_mb': config.monitoring.memory_alert_mb,
                'disk_usage_percent': config.monitoring.disk_alert_percent,
                'error_rate_percent': config.monitoring.error_rate_alert_percent
            }
        }
    )
    
    # Start monitoring
    prod_monitor.start()
    set_production_monitor(prod_monitor)
    
    # Store in app state
    app.state.dcp_manager = dcp_manager
    app.state.event_bus = event_bus
    app.state.prod_monitor = prod_monitor
    app.state.config = config
    
    logger.info("Copper Sun Brass API server started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Copper Sun Brass API server...")
    prod_monitor.stop()
    logger.info("Copper Sun Brass API server stopped")


# Create FastAPI app
app = FastAPI(
    title="Copper Sun Brass API",
    description="Production API for Copper Sun Brass Development Intelligence",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if get_config().environment == "development" else "An error occurred"
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Copper Sun Brass API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "metrics": "/health/metrics",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }


# Include routers
app.include_router(health_router)


# Additional API endpoints can be added here
@app.get("/api/v1/status")
async def api_status(request: Request) -> Dict[str, Any]:
    """Get Copper Sun Brass operational status."""
    config = request.app.state.config
    
    return {
        "environment": config.environment,
        "version": config.version,
        "project_root": str(config.project_root),
        "features": config.features,
        "monitoring": {
            "enabled": config.monitoring.enabled,
            "metrics_port": config.monitoring.metrics_port
        }
    }


@app.post("/api/v1/analyze")
async def trigger_analysis(request: Request) -> Dict[str, Any]:
    """Trigger a Copper Sun Brass analysis run."""
    # This would integrate with the Copper Sun Brass runner
    # For now, return a placeholder response
    return {
        "status": "accepted",
        "message": "Analysis triggered",
        "job_id": "placeholder-job-id"
    }


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    return app


def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the API server."""
    config = get_config()
    
    # Configure logging
    log_level = "debug" if config.log_level == "DEBUG" else "info"
    
    # Use configured metrics port if available
    if config.monitoring.enabled:
        port = config.monitoring.metrics_port
    
    logger.info(f"Starting API server on {host}:{port}")
    
    uvicorn.run(
        "coppersun_brass.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level
    )


if __name__ == "__main__":
    run_server()