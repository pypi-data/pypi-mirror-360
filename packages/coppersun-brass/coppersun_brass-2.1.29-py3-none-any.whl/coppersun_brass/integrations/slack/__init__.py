"""
Slack Integration for Copper Alloy Brass

General Staff G6 Role: Communications
Real-time notification system for AI-human collaboration
"""

from coppersun_brass.integrations.slack.client import SlackClient
from coppersun_brass.integrations.slack.notifier import SlackNotifier
from coppersun_brass.integrations.slack.formatter import MessageFormatter

__all__ = ['SlackClient', 'SlackNotifier', 'MessageFormatter']