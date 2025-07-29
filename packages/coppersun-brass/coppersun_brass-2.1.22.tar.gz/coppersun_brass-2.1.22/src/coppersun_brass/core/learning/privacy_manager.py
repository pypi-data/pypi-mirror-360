"""
Privacy Manager for Learning System

General Staff G5 Function: Data Security and Privacy
Ensures learning data respects team boundaries and privacy requirements
"""

import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

from coppersun_brass.core.learning.models import PrivacyConfig, init_db
from coppersun_brass.core.context.dcp_manager import DCPManager
from .dcp_helpers import get_dcp_section, update_dcp_section
import logging

logger = logging.getLogger(__name__)

class PrivacyManager:
    """
    Manages privacy controls for the learning system
    
    General Staff Civil Affairs Function: Privacy Protection
    This component manages privacy settings that must persist across sessions
    to ensure consistent data handling policies for all AI commanders.
    """
    
    # Patterns to sanitize
    SANITIZATION_PATTERNS = [
        # File paths
        (r'(/[A-Za-z0-9_\-./]+)+\.(py|js|ts|java|cpp|go)', '[FILE_PATH]'),
        # Email addresses
        (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL]'),
        # IP addresses
        (r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', '[IP_ADDRESS]'),
        # API keys and tokens (common patterns)
        (r'[a-zA-Z0-9_-]{20,}', '[REDACTED_TOKEN]'),
        # URLs with potential secrets
        (r'https?://[^\s]*[?&](api_key|token|secret)=[^\s&]+', '[REDACTED_URL]'),
        # Common secret patterns
        (r'(password|secret|token|api_key)\s*[:=]\s*["\']?[^\s"\']+', '[REDACTED_SECRET]'),
    ]
    
    def __init__(self, dcp_path: Optional[str] = None, team_id: Optional[str] = None):
        """
        Initialize privacy manager with MANDATORY DCP integration
        
        Args:
            dcp_path: Path to DCP context file (mandatory per CLAUDE.md)
            team_id: Optional team identifier for config lookup
        """
        # DCP is MANDATORY - this is how the general staff coordinates
        self.dcp_manager = DCPManager(dcp_path)
        self.team_id = team_id
        self.engine, self.Session = init_db()
        
        # Load privacy settings from DCP first
        self._load_privacy_from_dcp()
        self.config = self._load_config()
    
    def _load_config(self) -> PrivacyConfig:
        """Load privacy configuration for team"""
        if not self.team_id:
            # Default config
            return PrivacyConfig(
                team_id='default',
                data_retention_days=180,
                share_with_team=False,
                share_publicly=False,
                strict_mode=True
            )
        
        session = self.Session()
        try:
            config = session.query(PrivacyConfig).filter_by(
                team_id=self.team_id
            ).first()
            
            if not config:
                # Create default config for team
                config = PrivacyConfig(
                    team_id=self.team_id,
                    data_retention_days=180,
                    share_with_team=False,
                    share_publicly=False,
                    strict_mode=True
                )
                session.add(config)
                session.commit()
            
            return config
        finally:
            session.close()
    
    def sanitize_feedback(self, feedback: str) -> str:
        """
        Sanitize user feedback to remove sensitive information
        
        Args:
            feedback: Raw feedback text
            
        Returns:
            Sanitized feedback text
        """
        if not feedback:
            return ""
        
        sanitized = feedback
        
        # Apply all sanitization patterns
        for pattern, replacement in self.SANITIZATION_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        
        # Additional strict mode sanitization
        if self.config.strict_mode:
            # Remove any remaining potential file paths
            sanitized = re.sub(r'/[^\s]+', '[PATH]', sanitized)
            # Remove potential variable names
            sanitized = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]{15,}\b', '[IDENTIFIER]', sanitized)
        
        return sanitized
    
    def sanitize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize context data for storage
        
        Args:
            context: Raw context dictionary
            
        Returns:
            Sanitized context
        """
        sanitized = {}
        
        # Whitelist of allowed context keys
        allowed_keys = {
            'project_type', 'language', 'architecture',
            'codebase_size', 'team_id'
        }
        
        for key, value in context.items():
            if key in allowed_keys:
                if isinstance(value, str):
                    # Basic sanitization for strings
                    sanitized[key] = re.sub(r'[^\w\s\-.]', '', value)[:50]
                elif isinstance(value, (int, float)):
                    sanitized[key] = value
                elif key == 'team_id':
                    # Hash team IDs for privacy
                    sanitized[key] = self.hash_team_id(value)
        
        return sanitized
    
    def hash_team_id(self, team_id: str) -> str:
        """Create anonymized team identifier"""
        if not team_id:
            return "anonymous"
        
        return hashlib.sha256(team_id.encode()).hexdigest()[:16]
    
    def check_sharing_permission(self, team_id: str) -> bool:
        """Check if team has enabled data sharing"""
        if not team_id or team_id == "anonymous":
            return False
        
        session = self.Session()
        try:
            config = session.query(PrivacyConfig).filter_by(
                team_id=team_id
            ).first()
            
            return config.share_with_team if config else False
        finally:
            session.close()
    
    def calculate_expiry_date(self) -> datetime:
        """Calculate data expiry date based on retention policy"""
        retention_days = self.config.data_retention_days
        return datetime.utcnow() + timedelta(days=retention_days)
    
    def should_expire_data(self, created_at: datetime) -> bool:
        """Check if data should be expired based on retention policy"""
        retention_days = self.config.data_retention_days
        age_days = (datetime.utcnow() - created_at).days
        return age_days > retention_days
    
    def purge_expired_data(self, dry_run: bool = True) -> Dict[str, int]:
        """
        Purge expired data based on retention policies
        
        Args:
            dry_run: If True, only report what would be deleted
            
        Returns:
            Dictionary with counts of purged items
        """
        from coppersun_brass.core.learning.models import TaskOutcome, LearnedPattern
        
        session = self.Session()
        results = {
            'task_outcomes': 0,
            'learned_patterns': 0
        }
        
        try:
            # Find expired task outcomes
            expired_outcomes = session.query(TaskOutcome).filter(
                TaskOutcome.data_expiry < datetime.utcnow()
            ).all()
            
            results['task_outcomes'] = len(expired_outcomes)
            
            if not dry_run:
                for outcome in expired_outcomes:
                    session.delete(outcome)
            
            # Find old patterns from teams that don't share
            old_patterns = session.query(LearnedPattern).filter(
                LearnedPattern.is_public == False,
                LearnedPattern.last_updated < datetime.utcnow() - timedelta(days=365)
            ).all()
            
            results['learned_patterns'] = len(old_patterns)
            
            if not dry_run:
                for pattern in old_patterns:
                    session.delete(pattern)
                session.commit()
            
            return results
            
        finally:
            session.close()
    
    def export_team_data(self, output_path: Path) -> None:
        """
        Export all data for a team (GDPR compliance)
        
        Args:
            output_path: Path to write export file
        """
        from coppersun_brass.core.learning.models import TaskOutcome, LearnedPattern
        
        if not self.team_id:
            raise ValueError("Team ID required for data export")
        
        session = self.Session()
        try:
            # Collect all team data
            data = {
                'team_id': self.team_id,
                'export_date': datetime.utcnow().isoformat(),
                'task_outcomes': [],
                'learned_patterns': []
            }
            
            # Get task outcomes
            outcomes = session.query(TaskOutcome).filter_by(
                team_id=self.team_id
            ).all()
            
            for outcome in outcomes:
                data['task_outcomes'].append({
                    'id': outcome.id,
                    'task_id': outcome.task_id,
                    'status': outcome.status.value,
                    'created_at': outcome.created_at.isoformat() if outcome.created_at else None
                })
            
            # Get patterns
            patterns = session.query(LearnedPattern).filter_by(
                team_id=self.team_id
            ).all()
            
            for pattern in patterns:
                data['learned_patterns'].append({
                    'id': pattern.id,
                    'pattern_type': pattern.pattern_type,
                    'success_rate': pattern.success_rate,
                    'confidence': pattern.confidence
                })
            
            # Write export
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        finally:
            session.close()

    def _load_privacy_from_dcp(self) -> None:
        """Load privacy settings from DCP for cross-session persistence"""
        try:
            learning_data = get_dcp_section(self.dcp_manager, 'learning', {})
            privacy_settings = learning_data.get('privacy', {})
            
            if privacy_settings:
                self.dcp_privacy_level = privacy_settings.get('level', 'private')
                self.dcp_retention_days = privacy_settings.get('data_retention_days', 90)
                logger.info(f"Loaded privacy settings from DCP: level={self.dcp_privacy_level}")
        except Exception as e:
            logger.warning(f"Could not load privacy settings from DCP: {e}")
            self.dcp_privacy_level = 'private'
            self.dcp_retention_days = 90
    
    def update_privacy_in_dcp(self, level: str, retention_days: Optional[int] = None) -> None:
        """Update privacy settings in DCP for future AI sessions"""
        privacy_data = {
            'level': level,
            'team_id': self.team_id,
            'data_retention_days': retention_days or self.config.data_retention_days,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        # Update DCP
        self.dcp_manager.update_section('learning.privacy', privacy_data)
        
        # Add observation for privacy change
        self.dcp_manager.add_observation(
            'privacy_level_changed',
            {
                'old_level': self.dcp_privacy_level,
                'new_level': level,
                'team_id': self.team_id,
                'retention_days': privacy_data['data_retention_days']
            },
            source_agent='learning_system',
            priority=90  # High priority for privacy changes
        )
        
        self.dcp_privacy_level = level
        logger.info(f"Updated privacy settings in DCP: level={level}")

# Export main class
__all__ = ['PrivacyManager']