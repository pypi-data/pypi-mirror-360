"""
GitHub Data Models

Dataclasses for GitHub API entities
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class GitHubRepository:
    """GitHub repository model"""
    id: int
    name: str
    full_name: str
    description: Optional[str]
    private: bool
    default_branch: str
    language: Optional[str]
    stars: int
    forks: int
    open_issues: int
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'full_name': self.full_name,
            'description': self.description,
            'private': self.private,
            'default_branch': self.default_branch,
            'language': self.language,
            'stars': self.stars,
            'forks': self.forks,
            'open_issues': self.open_issues,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class GitHubIssue:
    """GitHub issue model"""
    id: int
    number: int
    title: str
    body: str
    state: str  # open, closed
    author: str
    assignees: List[str]
    labels: List[str]
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime]
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'number': self.number,
            'title': self.title,
            'body': self.body,
            'state': self.state,
            'author': self.author,
            'assignees': self.assignees,
            'labels': self.labels,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'closed_at': self.closed_at.isoformat() if self.closed_at else None
        }


@dataclass
class GitHubPullRequest:
    """GitHub pull request model"""
    id: int
    number: int
    title: str
    body: str
    state: str  # open, closed
    author: str
    base_branch: str
    head_branch: str
    created_at: datetime
    updated_at: datetime
    merged_at: Optional[datetime]
    additions: int
    deletions: int
    changed_files: int
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'number': self.number,
            'title': self.title,
            'body': self.body,
            'state': self.state,
            'author': self.author,
            'base_branch': self.base_branch,
            'head_branch': self.head_branch,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'merged_at': self.merged_at.isoformat() if self.merged_at else None,
            'additions': self.additions,
            'deletions': self.deletions,
            'changed_files': self.changed_files
        }


@dataclass
class GitHubWebhookEvent:
    """GitHub webhook event model"""
    id: str
    event_type: str  # issues, pull_request, push, etc
    action: Optional[str]  # opened, closed, etc
    repository: str
    sender: str
    payload: dict
    received_at: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'action': self.action,
            'repository': self.repository,
            'sender': self.sender,
            'payload': self.payload,
            'received_at': self.received_at.isoformat()
        }