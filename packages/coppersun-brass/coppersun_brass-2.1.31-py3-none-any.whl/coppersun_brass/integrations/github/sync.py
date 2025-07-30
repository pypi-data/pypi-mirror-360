"""
GitHub Sync Manager

General Staff G4 Role: GitHub Data Synchronization
Manages incremental synchronization of GitHub data with DCP persistence
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
import logging

from coppersun_brass.integrations.github.client import GitHubClient
from coppersun_brass.integrations.github.models import GitHubIssue, GitHubPullRequest

logger = logging.getLogger(__name__)


class GitHubSyncManager:
    """
    Manages GitHub data synchronization
    
    General Staff G4 Role: GitHub Intelligence Gathering
    Incrementally syncs GitHub data and maintains state in DCP
    """
    
    def __init__(self, 
                 client: GitHubClient,
                 batch_size: int = 100):
        """
        Initialize sync manager
        
        Args:
            client: GitHub client instance
            batch_size: Number of items to sync per batch
        """
        self.client = client
        self.batch_size = batch_size
        self.sync_state = {}
        
        # Load sync state from client's DCP
        self._load_sync_state()
    
    def _load_sync_state(self) -> None:
        """Load sync state from DCP"""
        self.sync_state = self.client.state.get('sync_state', {})
        logger.info(f"Loaded sync state for {len(self.sync_state)} repositories")
    
    def _save_sync_state(self) -> None:
        """Save sync state to DCP"""
        self.client.state['sync_state'] = self.sync_state
        self.client._save_state_to_dcp()
    
    async def sync_repository(self, 
                            repo: str,
                            full_sync: bool = False) -> Dict[str, Any]:
        """
        Sync single repository
        
        Args:
            repo: Repository name (owner/repo)
            full_sync: Force full sync instead of incremental
            
        Returns:
            Sync statistics
        """
        logger.info(f"Starting {'full' if full_sync else 'incremental'} sync for {repo}")
        
        # Initialize repo state if needed
        if repo not in self.sync_state:
            self.sync_state[repo] = {
                'last_sync': None,
                'last_issue_sync': None,
                'last_pr_sync': None,
                'synced_issues': set(),
                'synced_prs': set()
            }
        
        repo_state = self.sync_state[repo]
        stats = {
            'repository': repo,
            'sync_type': 'full' if full_sync else 'incremental',
            'started_at': datetime.utcnow().isoformat(),
            'new_issues': 0,
            'updated_issues': 0,
            'new_prs': 0,
            'updated_prs': 0,
            'errors': []
        }
        
        try:
            # Sync issues
            issue_stats = await self._sync_issues(repo, repo_state, full_sync)
            stats.update(issue_stats)
            
            # Sync pull requests
            pr_stats = await self._sync_pull_requests(repo, repo_state, full_sync)
            stats.update(pr_stats)
            
            # Update sync times
            repo_state['last_sync'] = datetime.utcnow().isoformat()
            self._save_sync_state()
            
            # Log sync completion
            await self.client.process_event({
                'type': 'sync_completed',
                'repository': repo,
                'stats': stats
            })
            
        except Exception as e:
            logger.error(f"Sync failed for {repo}: {e}")
            stats['errors'].append(str(e))
            
            # Log sync error
            await self.client.process_event({
                'type': 'sync_failed',
                'repository': repo,
                'error': str(e),
                'partial_stats': stats
            })
        
        stats['completed_at'] = datetime.utcnow().isoformat()
        return stats
    
    async def _sync_issues(self,
                          repo: str,
                          repo_state: Dict[str, Any],
                          full_sync: bool) -> Dict[str, int]:
        """Sync repository issues"""
        stats = {
            'new_issues': 0,
            'updated_issues': 0
        }
        
        # Determine sync window
        if full_sync or not repo_state['last_issue_sync']:
            since = None
        else:
            # Sync issues updated in last sync window
            last_sync = datetime.fromisoformat(repo_state['last_issue_sync'])
            # Add small overlap to catch any missed updates
            since = last_sync - timedelta(minutes=5)
        
        # Get issues
        issues = await self.client.get_issues(
            repo,
            state='all',
            since=since,
            per_page=self.batch_size
        )
        
        # Convert synced_issues from list to set if needed
        if isinstance(repo_state.get('synced_issues'), list):
            repo_state['synced_issues'] = set(repo_state['synced_issues'])
        
        synced_issues = repo_state.get('synced_issues', set())
        
        for issue in issues:
            if issue.number in synced_issues:
                stats['updated_issues'] += 1
                
                # Log issue update
                await self.client.process_event({
                    'type': 'issue_updated',
                    'repository': repo,
                    'issue_number': issue.number,
                    'title': issue.title,
                    'state': issue.state
                })
            else:
                stats['new_issues'] += 1
                synced_issues.add(issue.number)
                
                # Log new issue
                await self.client.process_event({
                    'type': 'issue_discovered',
                    'repository': repo,
                    'issue_number': issue.number,
                    'title': issue.title,
                    'state': issue.state,
                    'author': issue.author
                })
        
        # Update state (convert set to list for JSON serialization)
        repo_state['synced_issues'] = list(synced_issues)
        repo_state['last_issue_sync'] = datetime.utcnow().isoformat()
        
        logger.info(f"Synced {len(issues)} issues for {repo} "
                   f"({stats['new_issues']} new, {stats['updated_issues']} updated)")
        
        return stats
    
    async def _sync_pull_requests(self,
                                 repo: str,
                                 repo_state: Dict[str, Any],
                                 full_sync: bool) -> Dict[str, int]:
        """Sync repository pull requests"""
        stats = {
            'new_prs': 0,
            'updated_prs': 0
        }
        
        # Get all PRs (GitHub doesn't support since parameter for PRs)
        prs = await self.client.get_pull_requests(
            repo,
            state='all',
            per_page=self.batch_size
        )
        
        # Convert synced_prs from list to set if needed
        if isinstance(repo_state.get('synced_prs'), list):
            repo_state['synced_prs'] = set(repo_state['synced_prs'])
        
        synced_prs = repo_state.get('synced_prs', set())
        
        # Filter by update time if incremental
        if not full_sync and repo_state['last_pr_sync']:
            last_sync = datetime.fromisoformat(repo_state['last_pr_sync'])
            prs = [pr for pr in prs if pr.updated_at > last_sync - timedelta(minutes=5)]
        
        for pr in prs:
            if pr.number in synced_prs:
                stats['updated_prs'] += 1
                
                # Log PR update
                await self.client.process_event({
                    'type': 'pr_updated',
                    'repository': repo,
                    'pr_number': pr.number,
                    'title': pr.title,
                    'state': pr.state,
                    'merged': pr.merged_at is not None
                })
            else:
                stats['new_prs'] += 1
                synced_prs.add(pr.number)
                
                # Log new PR
                await self.client.process_event({
                    'type': 'pr_discovered',
                    'repository': repo,
                    'pr_number': pr.number,
                    'title': pr.title,
                    'state': pr.state,
                    'author': pr.author
                })
        
        # Update state (convert set to list for JSON serialization)
        repo_state['synced_prs'] = list(synced_prs)
        repo_state['last_pr_sync'] = datetime.utcnow().isoformat()
        
        logger.info(f"Synced {len(prs)} PRs for {repo} "
                   f"({stats['new_prs']} new, {stats['updated_prs']} updated)")
        
        return stats
    
    async def sync_organization(self,
                              org: Optional[str] = None,
                              repo_filter: Optional[List[str]] = None,
                              full_sync: bool = False) -> Dict[str, Any]:
        """
        Sync all repositories in organization
        
        Args:
            org: Organization name (uses client default if not provided)
            repo_filter: Optional list of repo names to sync
            full_sync: Force full sync
            
        Returns:
            Overall sync statistics
        """
        org = org or self.client.config.get('org')
        if not org:
            raise ValueError("Organization not specified")
        
        logger.info(f"Starting organization sync for {org}")
        
        overall_stats = {
            'organization': org,
            'started_at': datetime.utcnow().isoformat(),
            'repositories_synced': 0,
            'total_new_issues': 0,
            'total_updated_issues': 0,
            'total_new_prs': 0,
            'total_updated_prs': 0,
            'failed_repos': []
        }
        
        try:
            # Get repositories
            repos = await self.client.get_repositories(org)
            
            # Apply filter if provided
            if repo_filter:
                repos = [r for r in repos if r.name in repo_filter]
            
            logger.info(f"Syncing {len(repos)} repositories")
            
            # Sync each repository
            for repo in repos:
                try:
                    stats = await self.sync_repository(
                        repo.full_name,
                        full_sync=full_sync
                    )
                    
                    overall_stats['repositories_synced'] += 1
                    overall_stats['total_new_issues'] += stats.get('new_issues', 0)
                    overall_stats['total_updated_issues'] += stats.get('updated_issues', 0)
                    overall_stats['total_new_prs'] += stats.get('new_prs', 0)
                    overall_stats['total_updated_prs'] += stats.get('updated_prs', 0)
                    
                except Exception as e:
                    logger.error(f"Failed to sync {repo.full_name}: {e}")
                    overall_stats['failed_repos'].append({
                        'repo': repo.full_name,
                        'error': str(e)
                    })
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Organization sync failed: {e}")
            raise
        
        overall_stats['completed_at'] = datetime.utcnow().isoformat()
        
        # Log organization sync completion
        await self.client.process_event({
            'type': 'org_sync_completed',
            'organization': org,
            'stats': overall_stats
        })
        
        return overall_stats
    
    async def continuous_sync(self,
                            repos: List[str],
                            interval_minutes: int = 30) -> None:
        """
        Continuously sync repositories at specified interval
        
        Args:
            repos: List of repositories to sync
            interval_minutes: Sync interval in minutes
        """
        logger.info(f"Starting continuous sync for {len(repos)} repos "
                   f"every {interval_minutes} minutes")
        
        while True:
            for repo in repos:
                try:
                    await self.sync_repository(repo, full_sync=False)
                except Exception as e:
                    logger.error(f"Continuous sync error for {repo}: {e}")
                    
                # Small delay between repos
                await asyncio.sleep(1)
            
            # Wait for next sync cycle
            logger.info(f"Waiting {interval_minutes} minutes until next sync")
            await asyncio.sleep(interval_minutes * 60)