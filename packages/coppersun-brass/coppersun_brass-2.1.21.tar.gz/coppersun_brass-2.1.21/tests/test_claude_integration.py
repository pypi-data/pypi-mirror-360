"""Test Claude Code integration functionality."""
import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from coppersun_brass.config import Copper Alloy BrassConfig
from coppersun_brass.core.storage import Copper Alloy BrassStorage
from coppersun_brass.claude_integration import ClaudeIntegration, ClaudeInsight


@pytest.fixture
def temp_project():
    """Create temporary project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def config(temp_project):
    """Create test configuration."""
    return Copper Alloy BrassConfig(temp_project)


@pytest.fixture
def storage(config):
    """Create test storage."""
    db_path = config.project_root / '.brass' / 'test.db'
    return Copper Alloy BrassStorage(db_path)


@pytest.fixture
def integration(config, storage):
    """Create test Claude integration."""
    return ClaudeIntegration(config, storage)


class TestClaudeInsight:
    """Test ClaudeInsight dataclass."""
    
    def test_creation(self):
        """Test insight creation."""
        insight = ClaudeInsight(
            type='critical',
            title='Security Issue',
            description='Hardcoded password found',
            file_path='auth.py',
            line_number=42
        )
        
        assert insight.type == 'critical'
        assert insight.title == 'Security Issue'
        assert insight.file_path == 'auth.py'
        assert insight.line_number == 42
        assert insight.timestamp  # Should be set automatically


class TestClaudeIntegration:
    """Test Claude integration functionality."""
    
    def test_initialization(self, integration, temp_project):
        """Test integration initialization."""
        assert integration.config is not None
        assert integration.storage is not None
        assert integration.claude_dir.exists()
        
        # Check file paths
        assert integration.insights_path.name == 'insights.json'
        assert integration.context_path.name == 'context.md'
        assert integration.alerts_path.name == 'alerts.json'
    
    def test_session_state(self, integration):
        """Test session state management."""
        # Initial state
        assert integration.session_state['last_update'] is None
        assert len(integration.session_state['seen_insights']) == 0
        
        # Add seen insight
        integration.session_state['seen_insights'].add('test123')
        integration._save_session_state()
        
        # Reload and verify
        integration._load_session_state()
        assert 'test123' in integration.session_state['seen_insights']
    
    def test_observation_to_insight(self, integration):
        """Test observation conversion."""
        # Security observation
        obs = {
            'type': 'security_issue',
            'classification': 'critical',
            'priority': 90,
            'data': {
                'file': 'auth.py',
                'line': 42,
                'issue_type': 'Hardcoded Password',
                'description': 'Password stored in plain text'
            },
            'confidence': 0.95,
            'source_agent': 'scout'
        }
        
        insight = integration._observation_to_insight(obs)
        
        assert insight is not None
        assert insight.type == 'critical'
        assert 'Hardcoded Password' in insight.title
        assert insight.file_path == 'auth.py'
        assert insight.line_number == 42
        assert insight.priority == 90
    
    def test_skip_trivial_observations(self, integration):
        """Test that trivial observations are skipped."""
        obs = {
            'type': 'file_change',
            'classification': 'trivial',
            'data': {'file': 'README.md'}
        }
        
        insight = integration._observation_to_insight(obs)
        assert insight is None
    
    def test_insight_id_generation(self, integration):
        """Test unique insight ID generation."""
        insight1 = ClaudeInsight(
            type='critical',
            title='Issue 1',
            description='Description',
            file_path='file.py',
            line_number=10
        )
        
        insight2 = ClaudeInsight(
            type='critical',
            title='Issue 1',
            description='Different description',  # Different content
            file_path='file.py',
            line_number=10
        )
        
        id1 = integration._get_insight_id(insight1)
        id2 = integration._get_insight_id(insight2)
        
        # Same title/file/line should give same ID
        assert id1 == id2
        assert len(id1) == 8  # MD5 truncated
    
    def test_write_insights(self, integration):
        """Test writing insights to JSON."""
        insights = [
            ClaudeInsight(
                type='critical',
                title='Security Issue',
                description='Test issue'
            ),
            ClaudeInsight(
                type='warning',
                title='Code Quality',
                description='Test warning'
            )
        ]
        
        integration._write_insights(insights)
        
        # Verify file created
        assert integration.insights_path.exists()
        
        # Read and verify content
        with open(integration.insights_path, 'r') as f:
            data = json.load(f)
        
        assert len(data) == 2
        assert data[0]['type'] == 'critical'
        assert data[1]['type'] == 'warning'
    
    def test_write_context(self, integration):
        """Test context generation."""
        insights = [
            ClaudeInsight(
                type='critical',
                title='Security: Hardcoded Password',
                description='Password stored in plain text',
                file_path='auth.py',
                line_number=42,
                priority=95
            )
        ]
        
        observations = [
            {'data': {'file': 'auth.py'}},
            {'data': {'file': 'auth.py'}},
            {'data': {'file': 'app.py'}}
        ]
        
        integration._write_context(insights, observations)
        
        # Verify file created
        assert integration.context_path.exists()
        
        # Check content
        content = integration.context_path.read_text()
        assert 'Copper Alloy Brass Context for Claude Code' in content
        assert 'Critical Issues' in content
        assert 'Hardcoded Password' in content
        assert 'auth.py' in content
        assert 'File Activity' in content
    
    def test_update_insights(self, integration, storage):
        """Test full insight update flow."""
        # Add test observations
        storage.add_observation(
            obs_type='security_issue',
            data={
                'file': 'auth.py',
                'description': 'Test security issue'
            },
            source_agent='scout',
            priority=90,
            metadata={'classification': 'critical'}
        )
        
        # Update insights
        stats = integration.update_insights()
        
        assert stats['total_observations'] >= 1
        assert integration.insights_path.exists()
        assert integration.context_path.exists()
        assert integration.session_state['last_update'] is not None
    
    def test_duplicate_insight_filtering(self, integration, storage):
        """Test that duplicate insights are filtered."""
        # Add same observation twice
        for _ in range(2):
            storage.add_observation(
                obs_type='security_issue',
                data={'file': 'auth.py', 'issue_type': 'Same Issue'},
                source_agent='scout',
                priority=90,
                metadata={'classification': 'critical'}
            )
        
        # First update
        stats1 = integration.update_insights()
        
        # Second update (should filter duplicates)
        stats2 = integration.update_insights()
        
        assert stats2['new_insights'] == 0  # No new insights
    
    def test_clear_session(self, integration):
        """Test session clearing."""
        # Add some state
        integration.session_state['seen_insights'].add('test123')
        integration.session_state['active_alerts'] = ['alert1']
        
        # Clear
        integration.clear_session()
        
        assert len(integration.session_state['seen_insights']) == 0
        assert len(integration.session_state['active_alerts']) == 0
    
    def test_mark_insight_addressed(self, integration):
        """Test marking insights as addressed."""
        # Add active alert
        integration.session_state['active_alerts'] = ['alert1', 'alert2']
        
        # Mark as addressed
        integration.mark_insight_addressed('alert1')
        
        assert 'alert1' not in integration.session_state['active_alerts']
        assert 'alert2' in integration.session_state['active_alerts']