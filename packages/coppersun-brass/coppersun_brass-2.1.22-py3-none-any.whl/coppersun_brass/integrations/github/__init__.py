"""
GitHub Integration for Copper Alloy Brass

General Staff G4 Function: GitHub Resource Management
Manages GitHub repositories, issues, pull requests, and webhooks
"""

from coppersun_brass.integrations.github.client import GitHubClient
from coppersun_brass.integrations.github.webhooks import GitHubWebhookHandler

__all__ = ['GitHubClient', 'GitHubWebhookHandler']