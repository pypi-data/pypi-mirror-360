"""
Slack Client

General Staff G6 Role: Communications Channel
Manages secure connection to Slack workspace
"""

import os
import json
import aiohttp
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from coppersun_brass.integrations.base import IntegrationAdapter
from coppersun_brass.core.context.dcp_manager import DCPManager

logger = logging.getLogger(__name__)


class SlackClient(IntegrationAdapter):
    """
    Slack API client with DCP integration
    
    General Staff G6 Function: Establishes secure communications
    channel for Copper Alloy Brass to send strategic updates to human commanders.
    """
    
    def __init__(self, 
                 dcp_path: Optional[str] = None,
                 bot_token: Optional[str] = None,
                 app_token: Optional[str] = None):
        """
        Initialize Slack client with MANDATORY DCP integration
        
        Args:
            dcp_path: Path to DCP context file (mandatory per CLAUDE.md)
            bot_token: Slack bot token (xoxb-...)
            app_token: Slack app token for socket mode (xapp-...)
        """
        # Initialize base with DCP
        super().__init__(dcp_path, service_name="slack")
        
        # Initialize Slack-specific attributes
        self.bot_token = bot_token or self._load_bot_token()
        self.app_token = app_token  # Optional for socket mode
        self.base_url = "https://slack.com/api"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Channel mappings
        self.channels: Dict[str, str] = {}  # name -> id
        self.default_channel: Optional[str] = None
        
        # Load configuration from DCP
        self._load_slack_config()
    
    def _load_bot_token(self) -> Optional[str]:
        """Load bot token from secure storage (NOT from DCP)"""
        token_file = Path.home() / '.brass' / 'slack_token.enc'
        if token_file.exists():
            try:
                # In production, this would decrypt
                with open(token_file, 'r') as f:
                    return f.read().strip()
            except Exception as e:
                logger.error(f"Failed to load Slack token: {e}")
        
        # Try environment variable
        return os.environ.get('SLACK_BOT_TOKEN')
    
    def _load_slack_config(self) -> None:
        """Load Slack configuration from DCP"""
        slack_config = self.config.get('slack', {})
        
        # Load channel mappings
        self.channels = slack_config.get('channels', {})
        self.default_channel = slack_config.get('default_channel')
        
        # Load notification preferences
        self.notify_on = slack_config.get('notify_on', {
            'analysis_complete': True,
            'high_priority_todo': True,
            'test_failure': True,
            'deployment_ready': True,
            'error_detected': True
        })
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                'Authorization': f'Bearer {self.bot_token}',
                'Content-Type': 'application/json'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def test_auth(self) -> bool:
        """Test Slack authentication"""
        try:
            response = await self._api_call('auth.test')
            if response.get('ok'):
                # Update DCP with auth status
                self.update_config({
                    'authenticated': True,
                    'team': response.get('team'),
                    'user': response.get('user'),
                    'bot_id': response.get('bot_id')
                })
                
                logger.info(f"Slack auth successful: {response.get('team')}")
                return True
            else:
                logger.error(f"Slack auth failed: {response.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"Slack auth test failed: {e}")
            return False
    
    async def _api_call(self, 
                       method: str, 
                       data: Optional[Dict[str, Any]] = None,
                       json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make Slack API call"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        url = f"{self.base_url}/{method}"
        
        try:
            if json_data:
                response = await self.session.post(url, json=json_data)
            else:
                response = await self.session.post(url, data=data)
            
            result = await response.json()
            
            # Log API call to DCP
            self.dcp_manager.add_observation(
                'slack_api_call',
                {
                    'method': method,
                    'success': result.get('ok', False),
                    'error': result.get('error'),
                    'warning': result.get('warning')
                },
                source_agent='slack_client',
                priority=40
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Slack API call failed: {e}")
            raise
    
    async def list_channels(self, types: str = "public_channel,private_channel") -> List[Dict[str, Any]]:
        """List Slack channels"""
        response = await self._api_call('conversations.list', {
            'types': types,
            'limit': 1000
        })
        
        if response.get('ok'):
            channels = response.get('channels', [])
            
            # Update channel mappings
            for channel in channels:
                self.channels[channel['name']] = channel['id']
            
            # Save to DCP
            self.update_config({
                'channels': self.channels
            })
            
            return channels
        else:
            raise ValueError(f"Failed to list channels: {response.get('error')}")
    
    async def send_message(self,
                          channel: str,
                          text: Optional[str] = None,
                          blocks: Optional[List[Dict[str, Any]]] = None,
                          thread_ts: Optional[str] = None) -> Dict[str, Any]:
        """
        Send message to Slack channel
        
        Args:
            channel: Channel name or ID
            text: Plain text message
            blocks: Rich Block Kit blocks
            thread_ts: Thread timestamp for replies
        """
        # Resolve channel name to ID
        if not channel.startswith('C') and not channel.startswith('D'):
            channel_id = self.channels.get(channel, channel)
        else:
            channel_id = channel
        
        data = {
            'channel': channel_id
        }
        
        if text:
            data['text'] = text
        
        if blocks:
            data['blocks'] = blocks
        
        if thread_ts:
            data['thread_ts'] = thread_ts
        
        response = await self._api_call('chat.postMessage', json_data=data)
        
        if response.get('ok'):
            # Log successful message
            self.dcp_manager.add_observation(
                'slack_message_sent',
                {
                    'channel': channel,
                    'has_blocks': blocks is not None,
                    'is_thread': thread_ts is not None,
                    'timestamp': response.get('ts')
                },
                source_agent='slack_client',
                priority=50
            )
            
            return response
        else:
            raise ValueError(f"Failed to send message: {response.get('error')}")
    
    async def add_reaction(self,
                          channel: str,
                          timestamp: str,
                          reaction: str) -> bool:
        """Add reaction to a message"""
        response = await self._api_call('reactions.add', {
            'channel': self.channels.get(channel, channel),
            'timestamp': timestamp,
            'name': reaction
        })
        
        return response.get('ok', False)
    
    async def create_channel(self, name: str, is_private: bool = False) -> Dict[str, Any]:
        """Create a new Slack channel"""
        response = await self._api_call('conversations.create', {
            'name': name,
            'is_private': is_private
        })
        
        if response.get('ok'):
            channel = response.get('channel', {})
            self.channels[channel['name']] = channel['id']
            
            # Update DCP
            self.update_config({
                'channels': self.channels
            })
            
            return channel
        else:
            raise ValueError(f"Failed to create channel: {response.get('error')}")
    
    async def upload_file(self,
                         channels: List[str],
                         content: str,
                         filename: str,
                         title: Optional[str] = None,
                         filetype: str = "text") -> Dict[str, Any]:
        """Upload file to Slack"""
        # Resolve channel names
        channel_ids = []
        for ch in channels:
            channel_ids.append(self.channels.get(ch, ch))
        
        response = await self._api_call('files.upload', {
            'channels': ','.join(channel_ids),
            'content': content,
            'filename': filename,
            'title': title or filename,
            'filetype': filetype
        })
        
        if response.get('ok'):
            return response.get('file', {})
        else:
            raise ValueError(f"Failed to upload file: {response.get('error')}")
    
    def should_notify(self, event_type: str) -> bool:
        """Check if notification should be sent for event type"""
        return self.notify_on.get(event_type, False)
    
    async def process_event(self, event: Dict[str, Any]) -> None:
        """Process Slack event (for socket mode)"""
        # Convert to DCP observation
        observation = self.convert_to_observation(event)
        
        # Let parent class handle routing
        await self.route_event(observation)