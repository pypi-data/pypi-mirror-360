"""
GitHub Webhook Handler

General Staff G4 Role: GitHub Event Processing
Handles incoming GitHub webhooks with security verification
"""

import hmac
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional
import logging

from coppersun_brass.integrations.base import IntegrationAdapter
from coppersun_brass.integrations.github.models import GitHubWebhookEvent

logger = logging.getLogger(__name__)


class GitHubWebhookHandler(IntegrationAdapter):
    """
    Handles GitHub webhooks with HMAC verification
    
    General Staff G4 Role: Real-time GitHub Event Processing
    Securely processes GitHub webhooks and converts them to DCP observations
    """
    
    def __init__(self, 
                 dcp_path: Optional[str] = None,
                 webhook_secret: Optional[str] = None):
        """
        Initialize with MANDATORY DCP integration
        
        Args:
            dcp_path: Path to DCP context file (mandatory per CLAUDE.md)
            webhook_secret: GitHub webhook secret for HMAC verification
        """
        super().__init__(dcp_path, service_name="github_webhook")
        
        self.webhook_secret = webhook_secret
        if webhook_secret:
            self._store_webhook_secret(webhook_secret)
    
    def _store_webhook_secret(self, secret: str) -> None:
        """Store webhook secret securely (not in DCP)"""
        # Similar to token storage
        import base64
        from pathlib import Path
        
        secrets_path = Path.home() / '.brass' / 'secrets.json'
        secrets_path.parent.mkdir(exist_ok=True)
        
        try:
            if secrets_path.exists():
                with open(secrets_path, 'r') as f:
                    secrets = json.load(f)
            else:
                secrets = {}
                
            # Simple obfuscation (use proper encryption in production)
            encoded = base64.b64encode(secret.encode()).decode()
            secrets['github_webhook_secret'] = encoded
            
            with open(secrets_path, 'w') as f:
                json.dump(secrets, f)
                
            # Update DCP to indicate secret exists
            self.config['has_webhook_secret'] = True
            self._save_state_to_dcp()
            
        except Exception as e:
            logger.error(f"Failed to store webhook secret: {e}")
    
    def _load_webhook_secret(self) -> Optional[str]:
        """Load webhook secret from secure storage"""
        import base64
        from pathlib import Path
        
        secrets_path = Path.home() / '.brass' / 'secrets.json'
        
        try:
            if not secrets_path.exists():
                return None
                
            with open(secrets_path, 'r') as f:
                secrets = json.load(f)
                
            encoded = secrets.get('github_webhook_secret')
            if not encoded:
                return None
                
            # Decode (use proper decryption in production)
            secret = base64.b64decode(encoded.encode()).decode()
            return secret
            
        except Exception as e:
            logger.error(f"Failed to load webhook secret: {e}")
            return None
    
    def verify_webhook_signature(self, 
                               body: bytes, 
                               signature: str) -> bool:
        """
        Verify GitHub webhook signature using HMAC-SHA256
        
        Args:
            body: Raw request body
            signature: X-Hub-Signature-256 header value
            
        Returns:
            True if signature is valid
        """
        if not signature or not signature.startswith('sha256='):
            logger.warning("Invalid signature format")
            return False
            
        # Load secret if not in memory
        if not self.webhook_secret:
            self.webhook_secret = self._load_webhook_secret()
            
        if not self.webhook_secret:
            logger.error("No webhook secret available")
            return False
            
        # Calculate expected signature
        expected = hmac.new(
            self.webhook_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures (timing-safe)
        provided = signature.split('=', 1)[1]
        is_valid = hmac.compare_digest(expected, provided)
        
        if not is_valid:
            logger.warning("Webhook signature verification failed")
            
        return is_valid
    
    async def process_webhook(self, 
                            headers: Dict[str, str],
                            body: bytes) -> GitHubWebhookEvent:
        """
        Process incoming webhook
        
        Args:
            headers: Request headers
            body: Raw request body
            
        Returns:
            Processed webhook event
        """
        # Verify signature
        signature = headers.get('X-Hub-Signature-256', '')
        if not self.verify_webhook_signature(body, signature):
            raise ValueError("Invalid webhook signature")
            
        # Parse webhook data
        try:
            payload = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse webhook body: {e}")
            raise
            
        # Extract event info
        event_type = headers.get('X-GitHub-Event', 'unknown')
        event_id = headers.get('X-GitHub-Delivery', 'unknown')
        
        # Create event object
        event = GitHubWebhookEvent(
            id=event_id,
            event_type=event_type,
            action=payload.get('action'),
            repository=payload.get('repository', {}).get('full_name', 'unknown'),
            sender=payload.get('sender', {}).get('login', 'unknown'),
            payload=payload,
            received_at=datetime.utcnow()
        )
        
        # Process through base adapter
        await self.process_event({
            'type': 'webhook_received',
            'event_id': event.id,
            'event_type': event.event_type,
            'action': event.action,
            'repository': event.repository,
            'sender': event.sender
        })
        
        # Handle specific event types
        await self._handle_event_type(event)
        
        return event
    
    async def _handle_event_type(self, event: GitHubWebhookEvent) -> None:
        """Route event to specific handler based on type"""
        handlers = {
            'issues': self._handle_issue_event,
            'pull_request': self._handle_pr_event,
            'push': self._handle_push_event,
            'release': self._handle_release_event,
            'star': self._handle_star_event
        }
        
        handler = handlers.get(event.event_type)
        if handler:
            await handler(event)
        else:
            logger.info(f"No specific handler for event type: {event.event_type}")
    
    async def _handle_issue_event(self, event: GitHubWebhookEvent) -> None:
        """Handle issue events"""
        payload = event.payload
        issue = payload.get('issue', {})
        
        # Create specific observation
        observation_data = {
            'repository': event.repository,
            'issue_number': issue.get('number'),
            'issue_title': issue.get('title'),
            'action': event.action,
            'author': issue.get('user', {}).get('login'),
            'state': issue.get('state')
        }
        
        # Map actions to observation types
        if event.action == 'opened':
            obs_type = 'issue_created'
            priority = 70
        elif event.action == 'closed':
            obs_type = 'issue_closed'
            priority = 65
        else:
            obs_type = f'issue_{event.action}'
            priority = 60
            
        await self.process_event({
            'type': obs_type,
            **observation_data,
            'priority': priority
        })
    
    async def _handle_pr_event(self, event: GitHubWebhookEvent) -> None:
        """Handle pull request events"""
        payload = event.payload
        pr = payload.get('pull_request', {})
        
        observation_data = {
            'repository': event.repository,
            'pr_number': pr.get('number'),
            'pr_title': pr.get('title'),
            'action': event.action,
            'author': pr.get('user', {}).get('login'),
            'state': pr.get('state'),
            'base_branch': pr.get('base', {}).get('ref'),
            'head_branch': pr.get('head', {}).get('ref')
        }
        
        # Map actions to observation types
        if event.action == 'opened':
            obs_type = 'pr_created'
            priority = 75
        elif event.action == 'closed' and pr.get('merged'):
            obs_type = 'pr_merged'
            priority = 80
        elif event.action == 'closed':
            obs_type = 'pr_closed'
            priority = 70
        else:
            obs_type = f'pr_{event.action}'
            priority = 65
            
        await self.process_event({
            'type': obs_type,
            **observation_data,
            'priority': priority
        })
    
    async def _handle_push_event(self, event: GitHubWebhookEvent) -> None:
        """Handle push events"""
        payload = event.payload
        
        observation_data = {
            'repository': event.repository,
            'ref': payload.get('ref'),
            'commits': len(payload.get('commits', [])),
            'pusher': payload.get('pusher', {}).get('name'),
            'branch': payload.get('ref', '').split('/')[-1]
        }
        
        await self.process_event({
            'type': 'code_pushed',
            **observation_data,
            'priority': 65
        })
    
    async def _handle_release_event(self, event: GitHubWebhookEvent) -> None:
        """Handle release events"""
        payload = event.payload
        release = payload.get('release', {})
        
        observation_data = {
            'repository': event.repository,
            'release_name': release.get('name'),
            'tag_name': release.get('tag_name'),
            'action': event.action,
            'author': release.get('author', {}).get('login'),
            'prerelease': release.get('prerelease', False)
        }
        
        await self.process_event({
            'type': 'release_published',
            **observation_data,
            'priority': 75
        })
    
    async def _handle_star_event(self, event: GitHubWebhookEvent) -> None:
        """Handle star events"""
        payload = event.payload
        
        observation_data = {
            'repository': event.repository,
            'action': event.action,
            'starred_at': payload.get('starred_at'),
            'stars': payload.get('repository', {}).get('stargazers_count')
        }
        
        await self.process_event({
            'type': 'repository_starred',
            **observation_data,
            'priority': 50
        })
    
    def _event_to_observation(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Convert webhook event to DCP observation"""
        return {
            'type': f"github_{event.get('type', 'unknown')}",
            'data': event,
            'priority': event.get('priority', 60)
        }
    
    async def authenticate(self, **credentials) -> bool:
        """Webhooks don't need authentication"""
        return True
        
    async def test_connection(self) -> bool:
        """Test webhook configuration"""
        return self.config.get('has_webhook_secret', False)