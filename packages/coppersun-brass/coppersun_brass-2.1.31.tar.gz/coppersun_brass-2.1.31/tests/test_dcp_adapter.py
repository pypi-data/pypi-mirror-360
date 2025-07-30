"""Test DCP Adapter functionality."""
import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from coppersun_brass.core.storage import Copper Alloy BrassStorage
from coppersun_brass.core.dcp_adapter import DCPAdapter


@pytest.fixture
def storage():
    """Create temporary storage for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)
    
    storage = Copper Alloy BrassStorage(db_path)
    yield storage
    
    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def adapter(storage):
    """Create DCP adapter with test storage."""
    return DCPAdapter(storage)


def test_adapter_initialization(adapter):
    """Test adapter initializes properly."""
    assert adapter.storage is not None
    assert hasattr(adapter, 'add_observation')
    assert hasattr(adapter, 'update_metadata')


def test_add_observation_compatibility(adapter):
    """Test that add_observation works like DCPManager."""
    # This is what agents currently do
    adapter.add_observation(
        obs_type='code_finding',
        data={'file': 'test.py', 'issue': 'TODO found'},
        source_agent='scout',
        priority=70
    )
    
    # Verify it was stored
    observations = adapter.get_observations()
    assert len(observations) == 1
    assert observations[0]['type'] == 'code_finding'
    assert observations[0]['data']['file'] == 'test.py'


def test_update_metadata_compatibility(adapter):
    """Test metadata update functionality."""
    # Update metadata
    adapter.update_metadata({
        'project_type': 'django',
        'version': '2.0',
        'last_analysis': datetime.utcnow().isoformat()
    })
    
    # Retrieve via get_section
    metadata = adapter.get_section('metadata', {})
    assert metadata['project_type'] == 'django'
    assert metadata['version'] == '2.0'


def test_get_observations_filters(adapter):
    """Test observation filtering."""
    # Add various observations
    adapter.add_observation('type_a', {'data': 1}, 'agent_1', 80)
    adapter.add_observation('type_b', {'data': 2}, 'agent_1', 60)
    adapter.add_observation('type_a', {'data': 3}, 'agent_2', 70)
    
    # Test filters
    all_obs = adapter.get_observations()
    assert len(all_obs) == 3
    
    agent_1_obs = adapter.get_observations(source_agent='agent_1')
    assert len(agent_1_obs) == 2
    
    type_a_obs = adapter.get_observations(obs_type='type_a')
    assert len(type_a_obs) == 2


def test_load_context_compatibility(adapter):
    """Test context loading returns expected format."""
    # Add some data
    adapter.add_observation('test', {'foo': 'bar'}, 'test_agent')
    adapter.update_metadata({'project': 'test'})
    
    # Load context
    context = adapter.load_context()
    
    # Check structure
    assert 'observations' in context
    assert 'metadata' in context
    assert 'version' in context
    assert context['version'] == '2.0'
    
    assert len(context['observations']) == 1
    assert context['metadata']['project'] == 'test'


def test_section_operations(adapter):
    """Test get/update section methods."""
    # Update nested section
    adapter.update_section('metadata.build', {
        'version': '1.2.3',
        'commit': 'abc123'
    })
    
    # Retrieve nested section
    build_info = adapter.get_section('metadata.build', {})
    assert build_info['version'] == '1.2.3'
    
    # Test default value
    missing = adapter.get_section('nonexistent', 'default')
    assert missing == 'default'


def test_project_info_methods(adapter):
    """Test project information helper methods."""
    # Set project info
    adapter.update_section('project_info', {
        'project_type': 'flask',
        'main_language': 'python'
    })
    
    adapter.update_section('metadata', {
        'current_sprint': 'sprint-15'
    })
    
    # Test helper methods
    assert adapter.get_project_type() == 'flask'
    assert adapter.get_current_sprint() == 'sprint-15'


def test_file_change_tracking(adapter):
    """Test file change observation methods."""
    # Add file changes
    adapter.add_observation(
        'file_modified',
        {'file': 'app.py', 'action': 'modified'},
        'watch'
    )
    adapter.add_observation(
        'file_modified',
        {'file': 'config.py', 'action': 'created'},
        'watch'
    )
    
    # Get recent changes
    changes = adapter.get_recent_changes()
    assert len(changes) == 2
    assert all(c['type'] == 'file_modified' for c in changes)


def test_pattern_methods(adapter, tmp_path):
    """Test pattern-related methods."""
    test_file = tmp_path / 'test.py'
    
    # Save some patterns
    adapter.storage.save_pattern(
        'code_smell',
        {'type': 'long_function', 'lines': 100},
        str(test_file),
        0.8
    )
    
    # Get patterns for file
    patterns = adapter.get_patterns_for_file(test_file)
    assert len(patterns) == 1
    assert patterns[0]['pattern_data']['type'] == 'long_function'


def test_complexity_history(adapter):
    """Test complexity history retrieval."""
    test_file = Path('complex.py')
    
    # Update file metrics
    adapter.storage.update_file_metrics(test_file, {
        'complexity': 15,
        'todo_count': 2
    })
    
    # Get complexity history
    history = adapter.get_complexity_history(test_file)
    assert history == [15]


def test_file_change_patterns(adapter):
    """Test file change correlation detection."""
    # Add correlated file changes (within same time window)
    base_time = datetime.utcnow()
    
    # Group 1: Files that change together
    adapter.add_observation(
        'file_modified',
        {'file': 'models.py', 'timestamp': base_time.isoformat()},
        'watch'
    )
    adapter.add_observation(
        'file_modified',
        {'file': 'views.py', 'timestamp': base_time.isoformat()},
        'watch'
    )
    
    # Get patterns
    patterns = adapter.get_file_change_patterns()
    
    # Should find correlation
    assert len(patterns) > 0
    assert any(
        set(p['files']) == {'models.py', 'views.py'}
        for p in patterns
    )


def test_error_handling(adapter):
    """Test that adapter handles errors gracefully."""
    # Force an error by corrupting storage
    adapter.storage = None
    
    # These should not raise exceptions
    adapter.add_observation('test', {}, 'test')
    adapter.update_metadata({'test': 'data'})
    
    observations = adapter.get_observations()
    assert observations == []
    
    context = adapter.load_context()
    assert context['observations'] == []