"""
Integrations API Router

General Staff G4 Role: External Integration Interface
Endpoints for managing external service integrations
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from coppersun_brass.api.auth import get_current_user
from coppersun_brass.integrations.github import GitHubClient
from coppersun_brass.integrations.github.sync import GitHubSyncManager
from coppersun_brass.core.context.dcp_manager import DCPManager

logger = logging.getLogger(__name__)

router = APIRouter()


class IntegrationConfig(BaseModel):
    """Integration configuration model"""
    service: str = Field(..., description="Service name (github, gitlab, slack)")
    config: Dict[str, Any] = Field(..., description="Service-specific configuration")
    
    class Config:
        schema_extra = {
            "example": {
                "service": "github",
                "config": {
                    "token": "ghp_xxxxxxxxxxxx",
                    "org": "my-organization"
                }
            }
        }


class IntegrationStatus(BaseModel):
    """Integration status model"""
    service: str
    configured: bool
    authenticated: bool
    health_score: float
    last_sync: Optional[str]
    total_events: int
    failed_events: int
    
    class Config:
        schema_extra = {
            "example": {
                "service": "github",
                "configured": True,
                "authenticated": True,
                "health_score": 0.95,
                "last_sync": "2025-06-11T10:00:00Z",
                "total_events": 1523,
                "failed_events": 3
            }
        }


class SyncRequest(BaseModel):
    """Sync request model"""
    repositories: Optional[List[str]] = Field(None, description="Specific repos to sync")
    full_sync: bool = Field(False, description="Force full sync")
    
    class Config:
        schema_extra = {
            "example": {
                "repositories": ["org/repo1", "org/repo2"],
                "full_sync": False
            }
        }


@router.get("/",
           response_model=List[IntegrationStatus],
           summary="List integrations",
           description="Get status of all configured integrations")
async def list_integrations(
    auth: Dict = Depends(get_current_user)
) -> List[IntegrationStatus]:
    """
    List all configured integrations
    
    Requires authentication with 'integrations' scope.
    """
    # Check scope
    if 'integrations' not in auth.get('scopes', []) and 'admin' not in auth.get('scopes', []):
        raise HTTPException(
            status_code=403,
            detail="Requires 'integrations' scope"
        )
    
    # Get integration status from DCP
    dcp_manager = DCPManager()
    integrations_data = dcp_manager.get_section('integrations', {})
    
    statuses = []
    for service, data in integrations_data.items():
        if service == 'routing':  # Skip routing config
            continue
            
        status = IntegrationStatus(
            service=service,
            configured=data.get('config', {}).get('configured', False),
            authenticated=data.get('config', {}).get('authenticated', False),
            health_score=data.get('metrics', {}).get('health_score', 0.0),
            last_sync=data.get('state', {}).get('last_sync'),
            total_events=data.get('metrics', {}).get('total_events', 0),
            failed_events=data.get('metrics', {}).get('failed_events', 0)
        )
        statuses.append(status)
    
    return statuses


@router.post("/configure",
            summary="Configure integration",
            description="Configure a new integration")
async def configure_integration(
    config: IntegrationConfig,
    auth: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Configure an external integration
    
    Requires 'admin' scope.
    """
    # Check admin scope
    if 'admin' not in auth.get('scopes', []):
        raise HTTPException(
            status_code=403,
            detail="Requires 'admin' scope"
        )
    
    try:
        if config.service == "github":
            # Configure GitHub
            client = GitHubClient(
                token=config.config.get('token'),
                org=config.config.get('org')
            )
            
            # Test authentication
            async with client:
                success = await client.authenticate()
                
            if not success:
                raise HTTPException(
                    status_code=400,
                    detail="GitHub authentication failed"
                )
            
            # Log configuration
            dcp_manager = DCPManager()
            dcp_manager.add_observation(
                'integration_configured',
                {
                    'service': 'github',
                    'user_id': auth['user_id'],
                    'org': config.config.get('org')
                },
                source_agent='api',
                priority=80
            )
            
            return {
                "status": "success",
                "service": "github",
                "message": "GitHub integration configured successfully"
            }
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported service: {config.service}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Integration configuration failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Configuration failed: {str(e)}"
        )


@router.post("/github/sync",
            summary="Sync GitHub data",
            description="Trigger GitHub repository synchronization")
async def sync_github(
    request: SyncRequest,
    background_tasks: BackgroundTasks,
    auth: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Sync GitHub repositories
    
    Requires 'integrations' scope.
    """
    # Check scope
    if 'integrations' not in auth.get('scopes', []) and 'admin' not in auth.get('scopes', []):
        raise HTTPException(
            status_code=403,
            detail="Requires 'integrations' scope"
        )
    
    try:
        # Initialize GitHub client
        client = GitHubClient()
        
        # Check if configured
        if not client.config.get('configured'):
            raise HTTPException(
                status_code=400,
                detail="GitHub integration not configured"
            )
        
        # Initialize sync manager
        sync_manager = GitHubSyncManager(client)
        
        # Start sync in background
        background_tasks.add_task(
            _perform_github_sync,
            sync_manager,
            request.repositories,
            request.full_sync,
            auth['user_id']
        )
        
        return {
            "status": "started",
            "message": "GitHub sync started in background",
            "repositories": request.repositories or ["all configured repos"],
            "sync_type": "full" if request.full_sync else "incremental"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GitHub sync failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Sync failed: {str(e)}"
        )


@router.post("/github/webhook",
            summary="GitHub webhook endpoint",
            description="Receive GitHub webhook events")
async def github_webhook(
    request: Dict[str, Any],
    x_hub_signature_256: Optional[str] = None,
    x_github_event: Optional[str] = None,
    x_github_delivery: Optional[str] = None
) -> Dict[str, Any]:
    """
    Handle GitHub webhook events
    
    No authentication required - uses webhook signature verification.
    """
    if not x_hub_signature_256:
        raise HTTPException(
            status_code=401,
            detail="Missing webhook signature"
        )
    
    try:
        from coppersun_brass.integrations.github import GitHubWebhookHandler
        
        # Initialize webhook handler
        handler = GitHubWebhookHandler()
        
        # Process webhook
        headers = {
            'X-Hub-Signature-256': x_hub_signature_256,
            'X-GitHub-Event': x_github_event or 'unknown',
            'X-GitHub-Delivery': x_github_delivery or 'unknown'
        }
        
        # Convert request to bytes (FastAPI parsed it as JSON)
        import json
        body = json.dumps(request).encode('utf-8')
        
        event = await handler.process_webhook(headers, body)
        
        return {
            "status": "success",
            "event_id": event.id,
            "event_type": event.event_type,
            "message": "Webhook processed successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Webhook processing failed: {str(e)}"
        )


@router.delete("/{service}",
              summary="Remove integration",
              description="Remove an integration configuration")
async def remove_integration(
    service: str,
    auth: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Remove integration configuration
    
    Requires 'admin' scope.
    """
    # Check admin scope
    if 'admin' not in auth.get('scopes', []):
        raise HTTPException(
            status_code=403,
            detail="Requires 'admin' scope"
        )
    
    # Update DCP
    dcp_manager = DCPManager()
    integrations = dcp_manager.get_section('integrations', {})
    
    if service not in integrations:
        raise HTTPException(
            status_code=404,
            detail=f"Integration not found: {service}"
        )
    
    # Remove from DCP
    del integrations[service]
    dcp_manager.update_section('integrations', integrations)
    
    # Log removal
    dcp_manager.add_observation(
        'integration_removed',
        {
            'service': service,
            'user_id': auth['user_id']
        },
        source_agent='api',
        priority=80
    )
    
    return {
        "status": "success",
        "service": service,
        "message": f"{service} integration removed"
    }


async def _perform_github_sync(
    sync_manager: GitHubSyncManager,
    repositories: Optional[List[str]],
    full_sync: bool,
    user_id: str
) -> None:
    """Perform GitHub sync in background"""
    try:
        async with sync_manager.client:
            if repositories:
                # Sync specific repositories
                for repo in repositories:
                    await sync_manager.sync_repository(repo, full_sync)
            else:
                # Sync all repositories in org
                await sync_manager.sync_organization(full_sync=full_sync)
                
        logger.info(f"GitHub sync completed for user {user_id}")
        
    except Exception as e:
        logger.error(f"Background sync failed: {e}")
        
        # Log failure to DCP
        dcp_manager = DCPManager()
        dcp_manager.add_observation(
            'integration_sync_failed',
            {
                'service': 'github',
                'user_id': user_id,
                'error': str(e)
            },
            source_agent='api',
            priority=85
        )