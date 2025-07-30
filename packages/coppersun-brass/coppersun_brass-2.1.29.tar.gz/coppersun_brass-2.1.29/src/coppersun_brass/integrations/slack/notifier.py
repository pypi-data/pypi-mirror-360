"""
Slack Notifier

General Staff G6 Role: Strategic Communications
Sends intelligent notifications based on Copper Alloy Brass analysis
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from coppersun_brass.integrations.slack.client import SlackClient
from coppersun_brass.integrations.slack.formatter import MessageFormatter
from coppersun_brass.core.context.dcp_manager import DCPManager

logger = logging.getLogger(__name__)


class SlackNotifier:
    """
    Intelligent Slack notification system
    
    General Staff G6 Function: Converts Copper Alloy Brass's strategic assessments
    into actionable notifications for human commanders. Prioritizes
    signal over noise.
    """
    
    def __init__(self, 
                 dcp_path: Optional[str] = None,
                 client: Optional[SlackClient] = None):
        """
        Initialize with MANDATORY DCP integration
        
        Args:
            dcp_path: Path to DCP context file (mandatory per CLAUDE.md)
            client: Existing Slack client (optional)
        """
        # DCP is MANDATORY - this is how we know what to notify about
        self.dcp_manager = DCPManager(dcp_path)
        
        # Use provided client or create new one
        self.client = client or SlackClient(dcp_path)
        
        # Message formatter
        self.formatter = MessageFormatter()
        
        # Notification queue for batching
        self.notification_queue: List[Dict[str, Any]] = []
        self.queue_lock = asyncio.Lock()
        
        # Rate limiting
        self.last_notification_time = {}
        self.min_interval_seconds = 60  # Min 1 minute between similar notifications
        
        # Load notification preferences
        self._load_preferences()
    
    def _load_preferences(self) -> None:
        """Load notification preferences from DCP"""
        prefs = self.dcp_manager.get_section('preferences.notifications', {})
        
        self.channels = {
            'analysis': prefs.get('analysis_channel', 'brass-analysis'),
            'alerts': prefs.get('alerts_channel', 'brass-alerts'),
            'reports': prefs.get('reports_channel', 'brass-reports'),
            'default': prefs.get('default_channel', 'brass-general')
        }
        
        self.thresholds = {
            'priority_min': prefs.get('priority_threshold', 70),
            'confidence_min': prefs.get('confidence_threshold', 0.7),
            'batch_size': prefs.get('batch_size', 5),
            'batch_timeout': prefs.get('batch_timeout_seconds', 300)
        }
    
    async def notify_analysis_complete(self, 
                                     analysis_type: str,
                                     results: Dict[str, Any]) -> Optional[str]:
        """
        Notify when analysis is complete
        
        Args:
            analysis_type: Type of analysis (scout, strategist, etc)
            results: Analysis results
            
        Returns:
            Message timestamp if sent
        """
        # Check if we should notify
        if not self.client.should_notify('analysis_complete'):
            return None
        
        # Rate limit check
        if not self._should_send_now(f'analysis_{analysis_type}'):
            return None
        
        # Format message
        blocks = self.formatter.format_analysis_results(analysis_type, results)
        
        # Determine channel
        channel = self.channels.get('analysis', self.channels['default'])
        
        try:
            async with self.client:
                response = await self.client.send_message(
                    channel=channel,
                    text=f"✅ {analysis_type.title()} analysis complete",
                    blocks=blocks
                )
                
                # Log notification
                self._log_notification('analysis_complete', {
                    'type': analysis_type,
                    'channel': channel,
                    'timestamp': response.get('ts')
                })
                
                return response.get('ts')
                
        except Exception as e:
            logger.error(f"Failed to send analysis notification: {e}")
            return None
    
    async def notify_high_priority_todo(self, todo: Dict[str, Any]) -> Optional[str]:
        """Notify about high priority TODO found"""
        # Check priority threshold
        priority = todo.get('priority', 0)
        if priority < self.thresholds['priority_min']:
            return None
        
        # Check notification settings
        if not self.client.should_notify('high_priority_todo'):
            return None
        
        # Rate limit
        if not self._should_send_now('high_priority_todo'):
            # Queue for batching instead
            await self._queue_notification({
                'type': 'todo',
                'data': todo,
                'priority': priority
            })
            return None
        
        # Format message
        blocks = self.formatter.format_todo_alert(todo)
        
        channel = self.channels.get('alerts', self.channels['default'])
        
        try:
            async with self.client:
                response = await self.client.send_message(
                    channel=channel,
                    text=f"🚨 High Priority TODO: {todo.get('description', 'Unknown')}",
                    blocks=blocks
                )
                
                # Add reaction based on type
                if todo.get('type') == 'BUG':
                    await self.client.add_reaction(
                        channel=channel,
                        timestamp=response.get('ts'),
                        reaction='bug'
                    )
                
                return response.get('ts')
                
        except Exception as e:
            logger.error(f"Failed to send TODO notification: {e}")
            return None
    
    async def notify_test_results(self, 
                                results: Dict[str, Any],
                                failed: bool = False) -> Optional[str]:
        """Notify about test results"""
        if failed and not self.client.should_notify('test_failure'):
            return None
        elif not failed and not self.client.should_notify('test_success'):
            return None
        
        # Format based on results
        if failed:
            blocks = self.formatter.format_test_failure(results)
            channel = self.channels.get('alerts', self.channels['default'])
            text = f"❌ Tests Failed: {results.get('failed_count', 0)} failures"
        else:
            blocks = self.formatter.format_test_success(results)
            channel = self.channels.get('reports', self.channels['default'])
            text = f"✅ All {results.get('total_count', 0)} tests passed!"
        
        try:
            async with self.client:
                response = await self.client.send_message(
                    channel=channel,
                    text=text,
                    blocks=blocks
                )
                return response.get('ts')
                
        except Exception as e:
            logger.error(f"Failed to send test notification: {e}")
            return None
    
    async def notify_recommendation(self, 
                                  recommendation: Dict[str, Any],
                                  context: Dict[str, Any]) -> Optional[str]:
        """Notify about strategic recommendation"""
        # Check confidence threshold
        confidence = recommendation.get('confidence', 0)
        if confidence < self.thresholds['confidence_min']:
            return None
        
        # Format recommendation
        blocks = self.formatter.format_recommendation(recommendation, context)
        
        channel = self.channels.get('analysis', self.channels['default'])
        
        try:
            async with self.client:
                response = await self.client.send_message(
                    channel=channel,
                    text=f"💡 Recommendation: {recommendation.get('title', 'Strategic Insight')}",
                    blocks=blocks
                )
                
                # Add voting reactions
                await self.client.add_reaction(channel, response.get('ts'), 'thumbsup')
                await self.client.add_reaction(channel, response.get('ts'), 'thumbsdown')
                
                return response.get('ts')
                
        except Exception as e:
            logger.error(f"Failed to send recommendation: {e}")
            return None
    
    async def send_daily_report(self) -> Optional[str]:
        """Send daily Copper Alloy Brass report"""
        # Gather data from DCP
        performance = self.dcp_manager.get_section('performance', {})
        observations = self.dcp_manager.get_recent_observations(hours=24)
        
        # Analyze observations
        stats = self._analyze_daily_activity(observations)
        
        # Format report
        blocks = self.formatter.format_daily_report(stats, performance)
        
        # Upload detailed report as file
        detailed_report = self._generate_detailed_report(observations, stats)
        
        channel = self.channels.get('reports', self.channels['default'])
        
        try:
            async with self.client:
                # Send summary
                response = await self.client.send_message(
                    channel=channel,
                    text="📊 Daily Copper Alloy Brass Report",
                    blocks=blocks
                )
                
                # Upload detailed report
                if detailed_report:
                    await self.client.upload_file(
                        channels=[channel],
                        content=detailed_report,
                        filename=f"brass_report_{datetime.now().strftime('%Y%m%d')}.txt",
                        title="Detailed Daily Report"
                    )
                
                return response.get('ts')
                
        except Exception as e:
            logger.error(f"Failed to send daily report: {e}")
            return None
    
    async def _queue_notification(self, notification: Dict[str, Any]) -> None:
        """Queue notification for batching"""
        async with self.queue_lock:
            self.notification_queue.append(notification)
            
            # Check if we should flush
            if len(self.notification_queue) >= self.thresholds['batch_size']:
                await self._flush_notification_queue()
    
    async def _flush_notification_queue(self) -> None:
        """Send batched notifications"""
        if not self.notification_queue:
            return
        
        # Group by type
        grouped = {}
        for notif in self.notification_queue:
            notif_type = notif['type']
            if notif_type not in grouped:
                grouped[notif_type] = []
            grouped[notif_type].append(notif)
        
        # Format and send each group
        for notif_type, notifications in grouped.items():
            if notif_type == 'todo':
                blocks = self.formatter.format_todo_batch(
                    [n['data'] for n in notifications]
                )
                channel = self.channels.get('alerts', self.channels['default'])
                text = f"📋 {len(notifications)} TODOs found"
            else:
                continue  # Skip unknown types
            
            try:
                async with self.client:
                    await self.client.send_message(
                        channel=channel,
                        text=text,
                        blocks=blocks
                    )
            except Exception as e:
                logger.error(f"Failed to send batch notification: {e}")
        
        # Clear queue
        self.notification_queue.clear()
    
    def _should_send_now(self, notification_type: str) -> bool:
        """Check rate limiting"""
        now = datetime.now()
        last_sent = self.last_notification_time.get(notification_type)
        
        if last_sent:
            delta = (now - last_sent).total_seconds()
            if delta < self.min_interval_seconds:
                return False
        
        self.last_notification_time[notification_type] = now
        return True
    
    def _analyze_daily_activity(self, observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze daily activity from observations"""
        stats = {
            'total_observations': len(observations),
            'by_agent': {},
            'by_type': {},
            'high_priority': 0,
            'errors': 0
        }
        
        for obs in observations:
            # Count by agent
            agent = obs.get('source_agent', 'unknown')
            stats['by_agent'][agent] = stats['by_agent'].get(agent, 0) + 1
            
            # Count by type
            obs_type = obs.get('type', 'unknown')
            stats['by_type'][obs_type] = stats['by_type'].get(obs_type, 0) + 1
            
            # Count high priority
            if obs.get('priority', 0) >= 80:
                stats['high_priority'] += 1
            
            # Count errors
            if 'error' in obs.get('data', {}):
                stats['errors'] += 1
        
        return stats
    
    def _generate_detailed_report(self, 
                                observations: List[Dict[str, Any]],
                                stats: Dict[str, Any]) -> str:
        """Generate detailed text report"""
        lines = [
            "BRASS DAILY REPORT",
            "=" * 50,
            f"Generated: {datetime.now().isoformat()}",
            "",
            "SUMMARY",
            "-" * 20,
            f"Total Observations: {stats['total_observations']}",
            f"High Priority Events: {stats['high_priority']}",
            f"Errors Detected: {stats['errors']}",
            "",
            "ACTIVITY BY AGENT",
            "-" * 20
        ]
        
        for agent, count in sorted(stats['by_agent'].items(), 
                                  key=lambda x: x[1], 
                                  reverse=True):
            lines.append(f"{agent}: {count}")
        
        lines.extend([
            "",
            "ACTIVITY BY TYPE",
            "-" * 20
        ])
        
        for obs_type, count in sorted(stats['by_type'].items(), 
                                     key=lambda x: x[1], 
                                     reverse=True)[:10]:
            lines.append(f"{obs_type}: {count}")
        
        return "\n".join(lines)
    
    def _log_notification(self, notif_type: str, details: Dict[str, Any]) -> None:
        """Log notification to DCP"""
        self.dcp_manager.add_observation(
            'notification_sent',
            {
                'type': notif_type,
                'details': details,
                'timestamp': datetime.utcnow().isoformat()
            },
            source_agent='slack_notifier',
            priority=40
        )