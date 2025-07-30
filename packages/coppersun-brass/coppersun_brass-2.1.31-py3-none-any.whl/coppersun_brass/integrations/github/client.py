"""
GitHub API Client

General Staff G4 Role: GitHub Integration Management
Provides comprehensive GitHub API access with DCP state persistence
"""

import aiohttp
import asyncio
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import logging
import base64

from coppersun_brass.integrations.base import IntegrationAdapter
from coppersun_brass.integrations.github.models import (
    GitHubIssue, GitHubPullRequest, GitHubRepository
)

logger = logging.getLogger(__name__)


class GitHubClient(IntegrationAdapter):
    """
    GitHub API client with full DCP integration
    
    General Staff G4 Role: GitHub Integration Management
    This component enables AI commanders to interact with GitHub
    repositories, maintaining auth state and rate limits in DCP.
    """
    
    API_BASE = "https://api.github.com"
    
    def __init__(self, 
                 dcp_path: Optional[str] = None,
                 token: Optional[str] = None,
                 org: Optional[str] = None):
        """
        Initialize with MANDATORY DCP integration
        
        Args:
            dcp_path: Path to DCP context file (mandatory per CLAUDE.md)
            token: GitHub personal access token (will be stored securely)
            org: Default organization
        """
        super().__init__(dcp_path, service_name="github")
        
        # Initialize HTTP session
        self.session = None
        self.token = None
        self.org = org
        
        # Rate limiting
        self.rate_limit = {
            'limit': 5000,
            'remaining': 5000,
            'reset': datetime.utcnow() + timedelta(hours=1)
        }
        
        # Load existing config
        if self.config.get('has_token') and not token:
            # Token exists in secure storage
            self.token = self._load_token_from_secure_storage()
        elif token:
            # New token provided
            self._store_token_securely(token)
            self.token = token
            
        if org:
            self.config['org'] = org
            self._save_state_to_dcp()
    
    def _store_token_securely(self, token: str) -> None:
        """Store token in encrypted local storage (NOT in DCP)"""
        # This is a simplified version - in production use proper encryption
        secrets_path = Path.home() / '.brass' / 'secrets.json'
        secrets_path.parent.mkdir(exist_ok=True)
        
        try:
            if secrets_path.exists():
                with open(secrets_path, 'r') as f:
                    secrets = json.load(f)
            else:
                secrets = {}
                
            # Simple obfuscation (use proper encryption in production)
            encoded = base64.b64encode(token.encode()).decode()
            secrets['github_token'] = encoded
            
            with open(secrets_path, 'w') as f:
                json.dump(secrets, f)
                
            # Update DCP to indicate token exists
            self.config['has_token'] = True
            self.config['token_stored'] = datetime.utcnow().isoformat()
            self._save_state_to_dcp()
            
            logger.info("GitHub token stored securely")
            
        except Exception as e:
            logger.error(f"Failed to store token: {e}")
            raise
    
    def _load_token_from_secure_storage(self) -> Optional[str]:
        """Load token from encrypted storage"""
        secrets_path = Path.home() / '.brass' / 'secrets.json'
        
        try:
            if not secrets_path.exists():
                return None
                
            with open(secrets_path, 'r') as f:
                secrets = json.load(f)
                
            encoded = secrets.get('github_token')
            if not encoded:
                return None
                
            # Decode (use proper decryption in production)
            token = base64.b64decode(encoded.encode()).decode()
            return token
            
        except Exception as e:
            logger.error(f"Failed to load token: {e}")
            return None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with auth"""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Copper Alloy Brass/1.0'
        }
        
        if self.token:
            headers['Authorization'] = f'token {self.token}'
            
        return headers
    
    async def _request(self, 
                      method: str, 
                      endpoint: str, 
                      **kwargs) -> Tuple[Dict[str, Any], int]:
        """
        Make API request with rate limiting
        
        Returns:
            Tuple of (response_data, status_code)
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        # Check rate limit
        await self._check_rate_limit()
        
        url = f"{self.API_BASE}{endpoint}"
        headers = self._get_headers()
        
        try:
            async with self.session.request(
                method, url, headers=headers, **kwargs
            ) as response:
                # Update rate limit from headers
                self._update_rate_limit(response.headers)
                
                # Handle response
                if response.status == 204:  # No content
                    return {}, response.status
                    
                data = await response.json()
                
                if response.status >= 400:
                    error_msg = data.get('message', 'Unknown error')
                    logger.error(f"GitHub API error: {response.status} - {error_msg}")
                    
                    # Log error to DCP
                    await self.process_event({
                        'type': 'api_error',
                        'status': response.status,
                        'message': error_msg,
                        'endpoint': endpoint
                    })
                    
                return data, response.status
                
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
    
    async def _check_rate_limit(self) -> None:
        """Check and enforce rate limits"""
        if self.rate_limit['remaining'] <= 10:
            # Near limit, check if reset time passed
            if datetime.utcnow() < self.rate_limit['reset']:
                wait_seconds = (self.rate_limit['reset'] - datetime.utcnow()).total_seconds()
                logger.warning(f"Rate limit near, waiting {wait_seconds}s")
                
                # Log to DCP
                await self.process_event({
                    'type': 'rate_limit_wait',
                    'remaining': self.rate_limit['remaining'],
                    'reset_at': self.rate_limit['reset'].isoformat(),
                    'wait_seconds': wait_seconds
                })
                
                await asyncio.sleep(wait_seconds)
    
    def _update_rate_limit(self, headers: Dict[str, str]) -> None:
        """Update rate limit from response headers"""
        try:
            if 'X-RateLimit-Limit' in headers:
                self.rate_limit['limit'] = int(headers['X-RateLimit-Limit'])
            if 'X-RateLimit-Remaining' in headers:
                self.rate_limit['remaining'] = int(headers['X-RateLimit-Remaining'])
            if 'X-RateLimit-Reset' in headers:
                self.rate_limit['reset'] = datetime.fromtimestamp(
                    int(headers['X-RateLimit-Reset'])
                )
                
            # Update in DCP
            self.state['rate_limit'] = {
                'limit': self.rate_limit['limit'],
                'remaining': self.rate_limit['remaining'],
                'reset_at': self.rate_limit['reset'].isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Failed to update rate limit: {e}")
    
    def _event_to_observation(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Convert GitHub event to DCP observation"""
        event_type = event.get('type', 'unknown')
        
        # Map GitHub events to observation types
        observation_type = f"github_{event_type}"
        
        # Set priority based on event type
        priority_map = {
            'api_error': 90,
            'rate_limit_wait': 85,
            'webhook': 70,
            'issue_created': 65,
            'issue_updated': 60,
            'pr_created': 70,
            'pr_merged': 75,
            'sync_completed': 65
        }
        
        return {
            'type': observation_type,
            'data': event,
            'priority': priority_map.get(event_type, 60)
        }
    
    async def authenticate(self, token: Optional[str] = None) -> bool:
        """
        Authenticate with GitHub
        
        Args:
            token: GitHub personal access token
            
        Returns:
            Success boolean
        """
        if token:
            self._store_token_securely(token)
            self.token = token
            
        if not self.token:
            logger.error("No GitHub token available")
            return False
            
        try:
            # Test authentication
            user_data, status = await self._request('GET', '/user')
            
            if status == 200:
                self.config['authenticated'] = True
                self.config['user'] = user_data.get('login')
                self.config['auth_time'] = datetime.utcnow().isoformat()
                self._save_state_to_dcp()
                
                # Log success
                await self.process_event({
                    'type': 'authenticated',
                    'user': user_data.get('login'),
                    'name': user_data.get('name')
                })
                
                logger.info(f"Authenticated as {user_data.get('login')}")
                return True
            else:
                self.config['authenticated'] = False
                self._save_state_to_dcp()
                return False
                
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test connection to GitHub"""
        try:
            data, status = await self._request('GET', '/rate_limit')
            return status == 200
        except Exception:
            return False
    
    async def get_repositories(self, 
                             org: Optional[str] = None,
                             per_page: int = 100) -> List[GitHubRepository]:
        """
        Get repositories for organization
        
        Args:
            org: Organization name (uses default if not provided)
            per_page: Results per page
            
        Returns:
            List of repositories
        """
        org = org or self.config.get('org')
        if not org:
            raise ValueError("Organization not specified")
            
        repos = []
        page = 1
        
        while True:
            data, status = await self._request(
                'GET',
                f'/orgs/{org}/repos',
                params={'per_page': per_page, 'page': page}
            )
            
            if status != 200 or not data:
                break
                
            for repo_data in data:
                repo = GitHubRepository(
                    id=repo_data['id'],
                    name=repo_data['name'],
                    full_name=repo_data['full_name'],
                    description=repo_data.get('description'),
                    private=repo_data['private'],
                    default_branch=repo_data.get('default_branch', 'main'),
                    language=repo_data.get('language'),
                    stars=repo_data['stargazers_count'],
                    forks=repo_data['forks_count'],
                    open_issues=repo_data['open_issues_count'],
                    created_at=datetime.fromisoformat(
                        repo_data['created_at'].replace('Z', '+00:00')
                    ),
                    updated_at=datetime.fromisoformat(
                        repo_data['updated_at'].replace('Z', '+00:00')
                    )
                )
                repos.append(repo)
            
            # Check if more pages
            if len(data) < per_page:
                break
                
            page += 1
            
        logger.info(f"Retrieved {len(repos)} repositories for {org}")
        return repos
    
    async def get_issues(self,
                        repo: str,
                        state: str = 'open',
                        labels: Optional[List[str]] = None,
                        since: Optional[datetime] = None,
                        per_page: int = 100) -> List[GitHubIssue]:
        """
        Get issues for repository
        
        Args:
            repo: Repository name (owner/repo)
            state: Issue state (open, closed, all)
            labels: Filter by labels
            since: Only issues updated after this time
            per_page: Results per page
            
        Returns:
            List of issues
        """
        issues = []
        page = 1
        
        params = {
            'state': state,
            'per_page': per_page
        }
        
        if labels:
            params['labels'] = ','.join(labels)
        if since:
            params['since'] = since.isoformat()
            
        while True:
            params['page'] = page
            data, status = await self._request(
                'GET',
                f'/repos/{repo}/issues',
                params=params
            )
            
            if status != 200 or not data:
                break
                
            for issue_data in data:
                # Skip pull requests (they appear in issues endpoint)
                if 'pull_request' in issue_data:
                    continue
                    
                issue = GitHubIssue(
                    id=issue_data['id'],
                    number=issue_data['number'],
                    title=issue_data['title'],
                    body=issue_data.get('body', ''),
                    state=issue_data['state'],
                    author=issue_data['user']['login'],
                    assignees=[a['login'] for a in issue_data.get('assignees', [])],
                    labels=[l['name'] for l in issue_data.get('labels', [])],
                    created_at=datetime.fromisoformat(
                        issue_data['created_at'].replace('Z', '+00:00')
                    ),
                    updated_at=datetime.fromisoformat(
                        issue_data['updated_at'].replace('Z', '+00:00')
                    ),
                    closed_at=datetime.fromisoformat(
                        issue_data['closed_at'].replace('Z', '+00:00')
                    ) if issue_data.get('closed_at') else None
                )
                issues.append(issue)
            
            if len(data) < per_page:
                break
                
            page += 1
            
        logger.info(f"Retrieved {len(issues)} issues for {repo}")
        return issues
    
    async def get_pull_requests(self,
                              repo: str,
                              state: str = 'open',
                              per_page: int = 100) -> List[GitHubPullRequest]:
        """
        Get pull requests for repository
        
        Args:
            repo: Repository name (owner/repo)
            state: PR state (open, closed, all)
            per_page: Results per page
            
        Returns:
            List of pull requests
        """
        prs = []
        page = 1
        
        params = {
            'state': state,
            'per_page': per_page
        }
        
        while True:
            params['page'] = page
            data, status = await self._request(
                'GET',
                f'/repos/{repo}/pulls',
                params=params
            )
            
            if status != 200 or not data:
                break
                
            for pr_data in data:
                pr = GitHubPullRequest(
                    id=pr_data['id'],
                    number=pr_data['number'],
                    title=pr_data['title'],
                    body=pr_data.get('body', ''),
                    state=pr_data['state'],
                    author=pr_data['user']['login'],
                    base_branch=pr_data['base']['ref'],
                    head_branch=pr_data['head']['ref'],
                    created_at=datetime.fromisoformat(
                        pr_data['created_at'].replace('Z', '+00:00')
                    ),
                    updated_at=datetime.fromisoformat(
                        pr_data['updated_at'].replace('Z', '+00:00')
                    ),
                    merged_at=datetime.fromisoformat(
                        pr_data['merged_at'].replace('Z', '+00:00')
                    ) if pr_data.get('merged_at') else None,
                    additions=pr_data.get('additions', 0),
                    deletions=pr_data.get('deletions', 0),
                    changed_files=pr_data.get('changed_files', 0)
                )
                prs.append(pr)
            
            if len(data) < per_page:
                break
                
            page += 1
            
        logger.info(f"Retrieved {len(prs)} pull requests for {repo}")
        return prs
    
    async def sync_repository(self, repo: str) -> Dict[str, Any]:
        """
        Full sync of repository data
        
        Args:
            repo: Repository name (owner/repo)
            
        Returns:
            Sync statistics
        """
        logger.info(f"Starting sync for {repo}")
        
        # Log sync start
        await self.process_event({
            'type': 'sync_started',
            'repository': repo,
            'start_time': datetime.utcnow().isoformat()
        })
        
        try:
            # Get repository info
            repo_data, status = await self._request('GET', f'/repos/{repo}')
            if status != 200:
                raise Exception(f"Failed to get repository info: {status}")
            
            # Get issues
            issues = await self.get_issues(repo, state='all')
            
            # Get pull requests
            prs = await self.get_pull_requests(repo, state='all')
            
            # Update sync state
            self.state[f'sync_{repo}'] = {
                'last_sync': datetime.utcnow().isoformat(),
                'issue_count': len(issues),
                'pr_count': len(prs),
                'open_issues': len([i for i in issues if i.state == 'open']),
                'open_prs': len([p for p in prs if p.state == 'open'])
            }
            self._save_state_to_dcp()
            
            # Log sync completion
            await self.process_event({
                'type': 'sync_completed',
                'repository': repo,
                'stats': self.state[f'sync_{repo}']
            })
            
            return self.state[f'sync_{repo}']
            
        except Exception as e:
            logger.error(f"Sync failed for {repo}: {e}")
            
            # Log sync error
            await self.process_event({
                'type': 'sync_failed',
                'repository': repo,
                'error': str(e)
            })
            
            raise