"""CLI commands for API server management."""

import click
import sys
from typing import Optional

from coppersun_brass.core.config_loader import get_config


@click.group()
def api():
    """API server management commands."""
    pass


@api.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', type=int, help='Port to bind to (default from config)')
@click.option('--reload', is_flag=True, help='Enable auto-reload for development')
def start(host: str, port: Optional[int], reload: bool):
    """Start the Copper Alloy Brass API server."""
    config = get_config()
    
    # Use configured port if not specified
    if port is None:
        port = config.monitoring.metrics_port
        
    click.echo(f"Starting Copper Alloy Brass API server...")
    click.echo(f"Host: {host}")
    click.echo(f"Port: {port}")
    click.echo(f"Environment: {config.environment}")
    
    if reload and config.environment == 'production':
        click.echo("⚠️  Warning: Auto-reload enabled in production environment")
        
    try:
        from coppersun_brass.api import run_server
        run_server(host=host, port=port, reload=reload)
    except ImportError as e:
        click.echo(f"❌ Failed to import API server: {e}", err=True)
        click.echo("Make sure FastAPI is installed: pip install fastapi uvicorn", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Failed to start API server: {e}", err=True)
        sys.exit(1)


@api.command()
@click.option('--format', type=click.Choice(['json', 'yaml']), default='json', help='Output format')
def openapi(format: str):
    """Export OpenAPI specification."""
    try:
        from coppersun_brass.api import app
        import json
        import yaml
        
        # Get OpenAPI schema
        schema = app.openapi()
        
        if format == 'json':
            click.echo(json.dumps(schema, indent=2))
        else:
            click.echo(yaml.dump(schema, default_flow_style=False))
            
    except ImportError:
        click.echo("❌ FastAPI not installed. Run: pip install fastapi", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Failed to export OpenAPI spec: {e}", err=True)
        sys.exit(1)


@api.command()
def routes():
    """List all API routes."""
    try:
        from coppersun_brass.api import app
        
        click.echo("Copper Alloy Brass API Routes:")
        click.echo("=" * 50)
        
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                methods = ', '.join(route.methods)
                click.echo(f"{methods:<10} {route.path}")
                
    except ImportError:
        click.echo("❌ FastAPI not installed. Run: pip install fastapi", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Failed to list routes: {e}", err=True)
        sys.exit(1)