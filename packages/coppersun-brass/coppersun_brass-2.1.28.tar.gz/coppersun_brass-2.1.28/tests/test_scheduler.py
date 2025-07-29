"""Test Copper Alloy Brass scheduler functionality."""
import pytest
import asyncio
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from coppersun_brass.config import Copper Alloy BrassConfig
from coppersun_brass.scheduler import AdaptiveScheduler, ResourceMonitor


@pytest.fixture
def temp_project():
    """Create temporary project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        project_dir.mkdir(exist_ok=True)
        yield project_dir


@pytest.fixture
def config(temp_project):
    """Create test configuration."""
    return Copper Alloy BrassConfig(temp_project)


@pytest.fixture
def scheduler(config):
    """Create test scheduler."""
    return AdaptiveScheduler(config)


class TestAdaptiveScheduler:
    """Test adaptive scheduler functionality."""
    
    def test_initialization(self, scheduler):
        """Test scheduler initialization."""
        assert scheduler.config is not None
        assert scheduler.runner is not None
        assert scheduler.base_interval == 300
        assert scheduler.current_interval == 300
        assert scheduler.activity_level == 0.5
    
    def test_adapt_interval_critical(self, scheduler):
        """Test interval adaptation with critical issues."""
        # Mock storage to return critical issues
        scheduler.storage.get_activity_stats = Mock(
            return_value={
                'total_observations': 5,
                'critical_count': 2
            }
        )
        
        scheduler._adapt_interval()
        
        # Should decrease interval
        assert scheduler.current_interval < scheduler.base_interval
        assert scheduler.current_interval >= scheduler.min_interval
    
    def test_adapt_interval_high_activity(self, scheduler):
        """Test interval adaptation with high activity."""
        scheduler.storage.get_activity_stats = Mock(
            return_value={
                'total_observations': 15,
                'critical_count': 0
            }
        )
        
        initial_interval = scheduler.current_interval
        scheduler._adapt_interval()
        
        # Should decrease interval
        assert scheduler.current_interval < initial_interval
    
    def test_adapt_interval_no_activity(self, scheduler):
        """Test interval adaptation with no activity."""
        scheduler.storage.get_activity_stats = Mock(
            return_value={
                'total_observations': 0,
                'critical_count': 0
            }
        )
        
        initial_interval = scheduler.current_interval
        scheduler._adapt_interval()
        
        # Should increase interval
        assert scheduler.current_interval > initial_interval
        assert scheduler.current_interval <= scheduler.max_interval
    
    def test_update_activity_level(self, scheduler):
        """Test activity level updates."""
        initial_level = scheduler.activity_level
        
        # High activity
        scheduler._update_activity_level(20)
        assert scheduler.activity_level > initial_level
        
        # Low activity
        scheduler._update_activity_level(0)
        assert scheduler.activity_level < 1.0
    
    def test_boost_activity(self, scheduler):
        """Test activity boosting."""
        scheduler._boost_activity()
        
        assert scheduler.activity_level >= 0.8
        assert scheduler.current_interval == scheduler.min_interval
    
    @pytest.mark.asyncio
    async def test_check_external_triggers(self, scheduler, temp_project):
        """Test external trigger detection."""
        trigger_file = temp_project / '.brass' / 'trigger'
        trigger_file.parent.mkdir(exist_ok=True)
        
        # No trigger
        assert await scheduler._check_external_triggers() is False
        
        # Create trigger
        trigger_file.touch()
        assert await scheduler._check_external_triggers() is True
        
        # Trigger should be removed
        assert not trigger_file.exists()
    
    def test_format_briefing(self, scheduler):
        """Test briefing formatting."""
        stats = {
            'total_observations': 10,
            'critical_count': 2,
            'files_analyzed': 5
        }
        
        critical_issues = [
            {
                'type': 'security_issue',
                'priority': 90,
                'data': {
                    'file': 'auth.py',
                    'description': 'Hardcoded password'
                },
                'timestamp': datetime.utcnow()
            }
        ]
        
        report = scheduler._format_briefing(stats, critical_issues)
        
        assert 'Copper Alloy Brass Morning Briefing' in report
        assert 'Total observations: 10' in report
        assert 'Critical issues: 2' in report
        assert 'auth.py' in report
        assert 'Hardcoded password' in report
    
    @pytest.mark.asyncio
    async def test_morning_briefing(self, scheduler, temp_project):
        """Test morning briefing generation."""
        # Mock storage
        scheduler.storage.get_activity_stats = Mock(
            return_value={'total_observations': 5}
        )
        scheduler.storage.get_observations = Mock(return_value=[])
        
        await scheduler._morning_briefing()
        
        briefing_path = temp_project / '.brass' / 'morning_briefing.md'
        assert briefing_path.exists()
        
        content = briefing_path.read_text()
        assert 'Copper Alloy Brass Morning Briefing' in content


class TestResourceMonitor:
    """Test resource monitoring."""
    
    def test_initialization(self):
        """Test monitor initialization."""
        monitor = ResourceMonitor()
        assert monitor.cpu_threshold == 80.0
        assert monitor.memory_threshold == 80.0
    
    @patch('os.getloadavg')
    @patch('os.cpu_count')
    def test_should_run_cpu_check(self, mock_cpu_count, mock_loadavg):
        """Test CPU usage checking."""
        monitor = ResourceMonitor()
        
        # Low CPU usage
        mock_loadavg.return_value = (1.0, 1.0, 1.0)
        mock_cpu_count.return_value = 4
        assert monitor.should_run() is True
        
        # High CPU usage
        mock_loadavg.return_value = (8.0, 8.0, 8.0)
        mock_cpu_count.return_value = 4
        assert monitor.should_run() is False
    
    @patch('platform.system')
    def test_windows_compatibility(self, mock_system):
        """Test Windows compatibility."""
        mock_system.return_value = 'Windows'
        monitor = ResourceMonitor()
        
        # Should always return True on Windows (no load average)
        assert monitor.should_run() is True


@pytest.mark.asyncio
class TestSchedulerIntegration:
    """Test scheduler integration."""
    
    async def test_manual_mode(self, scheduler):
        """Test manual mode execution."""
        # Mock runner
        scheduler.runner.initialize_agents = AsyncMock()
        scheduler.runner.run_once = AsyncMock()
        
        # Create task that will be cancelled
        task = asyncio.create_task(scheduler.start(mode='manual'))
        
        # Give it time to run
        await asyncio.sleep(0.1)
        
        # Should have run once
        scheduler.runner.initialize_agents.assert_called_once()
        scheduler.runner.run_once.assert_called_once()
    
    async def test_stop(self, scheduler):
        """Test scheduler stop."""
        # Mock runner shutdown
        scheduler.runner.shutdown = AsyncMock()
        
        await scheduler.stop()
        
        scheduler.runner.shutdown.assert_called_once()