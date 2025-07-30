"""Test Copper Alloy Brass runner functionality."""
import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from coppersun_brass.config import Copper Alloy BrassConfig
from coppersun_brass.runner import Copper Alloy BrassRunner
from coppersun_brass.core.storage import Copper Alloy BrassStorage


@pytest.fixture
def temp_project():
    """Create temporary project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        
        # Create some test files
        (project_dir / 'app.py').write_text("def main(): pass")
        (project_dir / 'test_app.py').write_text("def test_main(): pass")
        (project_dir / 'auth.py').write_text("password = 'secret'")
        
        yield project_dir


@pytest.fixture
def config(temp_project):
    """Create test configuration."""
    return Copper Alloy BrassConfig(temp_project)


@pytest.fixture
def runner(config):
    """Create test runner."""
    return Copper Alloy BrassRunner(config)


@pytest.mark.asyncio
class TestCopper Alloy BrassRunner:
    """Test runner functionality."""
    
    async def test_initialization(self, runner):
        """Test runner initialization."""
        assert runner.config is not None
        assert runner.storage is not None
        assert runner.ml_pipeline is not None
        assert runner.agents == {}
    
    async def test_initialize_agents(self, runner):
        """Test agent initialization."""
        # Mock agent imports
        with patch('coppersun_brass.runner.ScoutAgent') as mock_scout:
            with patch('coppersun_brass.runner.WatchAgent') as mock_watch:
                await runner.initialize_agents()
                
                assert 'scout' in runner.agents
                assert 'watch' in runner.agents
                mock_scout.assert_called_once()
                mock_watch.assert_called_once()
    
    async def test_get_changed_files(self, runner, temp_project):
        """Test file discovery."""
        # First run - should find all files
        files = await runner._get_changed_files()
        
        assert len(files) > 0
        assert any(f.name == 'app.py' for f in files)
        assert any(f.name == 'auth.py' for f in files)
    
    async def test_should_ignore(self, runner, temp_project):
        """Test ignore patterns."""
        # Create ignored directories
        ignored_paths = [
            temp_project / '__pycache__' / 'module.pyc',
            temp_project / '.git' / 'config',
            temp_project / 'node_modules' / 'package' / 'index.js',
            temp_project / 'venv' / 'lib' / 'python.py'
        ]
        
        for path in ignored_paths:
            assert runner._should_ignore(path)
        
        # Non-ignored paths
        normal_paths = [
            temp_project / 'app.py',
            temp_project / 'src' / 'main.py',
            temp_project / 'tests' / 'test_app.py'
        ]
        
        for path in normal_paths:
            assert not runner._should_ignore(path)
    
    async def test_run_scout_analysis(self, runner):
        """Test Scout analysis execution."""
        # Mock Scout agent
        mock_scout = Mock()
        mock_scout.analyze_file = Mock(return_value=[
            {
                'type': 'code_finding',
                'data': {'file': 'app.py', 'description': 'Test finding'},
                'priority': 50
            }
        ])
        
        runner.agents['scout'] = mock_scout
        
        # Mock ML pipeline
        runner.ml_pipeline.process_observations = AsyncMock(
            return_value=[{
                'type': 'code_finding',
                'data': {'file': 'app.py', 'description': 'Test finding'},
                'priority': 50,
                'classification': 'important',
                'confidence': 0.8,
                'ml_used': False
            }]
        )
        
        # Mock file discovery
        runner._get_changed_files = AsyncMock(
            return_value=[Path('app.py')]
        )
        
        # Run analysis
        observations = await runner.run_scout_analysis()
        
        assert len(observations) == 1
        assert observations[0]['classification'] == 'important'
        assert runner.stats['runs'] == 1
        assert runner.stats['total_observations'] == 1
    
    async def test_run_watch_monitoring(self, runner):
        """Test Watch monitoring startup."""
        # Mock Watch agent
        mock_watch = Mock()
        mock_watch.check_changes = Mock(return_value=[])
        
        runner.agents['watch'] = mock_watch
        
        # Start monitoring
        await runner.run_watch_monitoring()
        
        # Should have created a task
        assert len(runner.running_agents) == 1
        
        # Cancel the task
        for task in runner.running_agents:
            task.cancel()
    
    async def test_generate_summary(self, runner):
        """Test summary generation."""
        observations = [
            {'classification': 'critical'},
            {'classification': 'critical'},
            {'classification': 'important'},
            {'classification': 'important'},
            {'classification': 'important'},
            {'classification': 'trivial'},
        ]
        
        summary = runner._generate_summary(observations)
        
        assert '2 critical' in summary
        assert '3 important' in summary
        assert '1 trivial' in summary
    
    async def test_shutdown(self, runner):
        """Test graceful shutdown."""
        # Create a dummy task
        async def dummy_task():
            await asyncio.sleep(10)
        
        task = asyncio.create_task(dummy_task())
        runner.running_agents.add(task)
        
        # Shutdown
        await runner.shutdown()
        
        # Task should be cancelled
        assert task.cancelled()
        assert len(runner.running_agents) == 0
    
    async def test_error_handling(self, runner):
        """Test error handling in analysis."""
        # Mock Scout to raise error
        mock_scout = Mock()
        mock_scout.analyze_file = Mock(side_effect=Exception("Test error"))
        
        runner.agents['scout'] = mock_scout
        runner._get_changed_files = AsyncMock(return_value=[Path('app.py')])
        
        # Should not crash
        observations = await runner.run_scout_analysis()
        
        assert observations == []
        assert runner.stats['errors'] == 1
    
    async def test_stats_tracking(self, runner):
        """Test statistics tracking."""
        # Run some operations
        runner._update_avg_time(100)
        runner._update_avg_time(200)
        runner._update_avg_time(150)
        
        stats = runner.get_stats()
        
        assert stats['runs'] == 3
        assert stats['avg_run_time_ms'] == 150.0


@pytest.mark.asyncio
class TestResourceLimit:
    """Test resource limiting."""
    
    async def test_batch_size_limit(self, runner, temp_project):
        """Test batch size limiting."""
        # Create many files
        for i in range(200):
            (temp_project / f'file_{i}.py').write_text("pass")
        
        files = await runner._get_changed_files()
        
        # Should be limited to 100
        assert len(files) <= 100