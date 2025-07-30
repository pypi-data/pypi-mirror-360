"""Test Copper Alloy Brass SQLite storage functionality."""
import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta

from coppersun_brass.core.storage import Copper Alloy BrassStorage


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)
    
    yield db_path
    
    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def storage(temp_db):
    """Create storage instance with temporary database."""
    return Copper Alloy BrassStorage(temp_db)


def test_storage_initialization(storage):
    """Test that storage initializes with proper schema."""
    # Check that we can perform basic operations
    obs_id = storage.add_observation(
        obs_type='test',
        data={'message': 'test'},
        source_agent='test_agent'
    )
    assert obs_id > 0


def test_add_and_get_observations(storage):
    """Test adding and retrieving observations."""
    # Add observations
    obs1_id = storage.add_observation(
        obs_type='code_finding',
        data={'file': 'test.py', 'issue': 'TODO found'},
        source_agent='scout',
        priority=60
    )
    
    obs2_id = storage.add_observation(
        obs_type='file_modified',
        data={'file': 'main.py', 'action': 'created'},
        source_agent='watch',
        priority=40
    )
    
    assert obs1_id > 0
    assert obs2_id > obs1_id
    
    # Get all observations
    all_obs = storage.get_observations()
    assert len(all_obs) == 2
    
    # Filter by agent
    scout_obs = storage.get_observations(source_agent='scout')
    assert len(scout_obs) == 1
    assert scout_obs[0]['data']['file'] == 'test.py'
    
    # Filter by type
    file_obs = storage.get_observations(obs_type='file_modified')
    assert len(file_obs) == 1
    assert file_obs[0]['source_agent'] == 'watch'
    
    # Check priority ordering
    assert all_obs[0]['priority'] == 60  # Higher priority first


def test_file_state_tracking(storage, tmp_path):
    """Test file change detection."""
    # Create a test file
    test_file = tmp_path / 'test.py'
    test_file.write_text('print("hello")')
    
    # First check should require analysis
    assert storage.should_analyze_file(test_file) is True
    
    # Second check should not (same content)
    assert storage.should_analyze_file(test_file) is False
    
    # Modify file
    test_file.write_text('print("hello world")')
    
    # Should require analysis again
    assert storage.should_analyze_file(test_file) is True


def test_file_metrics(storage):
    """Test file metrics storage and retrieval."""
    file_path = Path('test.py')
    
    # Update metrics
    storage.update_file_metrics(file_path, {
        'complexity': 10,
        'todo_count': 3,
        'issues': [
            {'type': 'complexity', 'line': 45, 'description': 'Function too complex'}
        ]
    })
    
    # Get metrics
    metrics = storage.get_file_metrics()
    assert len(metrics) == 1
    assert metrics[0]['complexity'] == 10
    assert metrics[0]['todo_count'] == 3
    assert len(metrics[0]['issues']) == 1


def test_pattern_tracking(storage):
    """Test pattern learning functionality."""
    # Save patterns
    storage.save_pattern(
        pattern_type='code_smell',
        pattern_data={'type': 'long_function', 'lines': 150},
        file_path='utils.py',
        confidence=0.8
    )
    
    # Save same pattern again (should update occurrences)
    storage.save_pattern(
        pattern_type='code_smell',
        pattern_data={'type': 'long_function', 'lines': 150},
        file_path='helpers.py',
        confidence=0.9
    )
    
    # Get patterns
    patterns = storage.get_patterns()
    assert len(patterns) == 1
    assert patterns[0]['occurrences'] == 2
    assert patterns[0]['confidence'] == 0.9  # Updated confidence
    
    # Filter by type
    code_smells = storage.get_patterns(pattern_type='code_smell')
    assert len(code_smells) == 1


def test_ml_usage_tracking(storage):
    """Test ML usage statistics."""
    # Track some usage
    storage.track_ml_usage(
        batch_size=32,
        model_version='codebert-small-v1',
        processing_time_ms=150,
        cache_hits=25,
        cache_misses=7
    )
    
    storage.track_ml_usage(
        batch_size=16,
        model_version='codebert-small-v1',
        processing_time_ms=80,
        cache_hits=14,
        cache_misses=2
    )
    
    # Get stats
    stats = storage.get_ml_stats()
    assert stats['total_batches'] == 2
    assert stats['total_items'] == 48
    assert stats['avg_batch_size'] == 24
    assert stats['cache_hit_rate'] == (25 + 14) / (25 + 14 + 7 + 2)
    assert stats['total_time_ms'] == 230


def test_context_snapshots(storage):
    """Test context snapshot functionality."""
    # Save snapshots
    storage.save_context_snapshot('project_state', {
        'project_type': 'django',
        'frameworks': ['django', 'react'],
        'team_size': 5
    })
    
    storage.save_context_snapshot('session_summary', {
        'files_analyzed': 150,
        'issues_found': 23,
        'duration_minutes': 45
    })
    
    # Get latest snapshots
    project = storage.get_latest_context_snapshot('project_state')
    assert project['project_type'] == 'django'
    assert len(project['frameworks']) == 2
    
    session = storage.get_latest_context_snapshot('session_summary')
    assert session['files_analyzed'] == 150


def test_cleanup_old_data(storage):
    """Test data cleanup functionality."""
    # Add old observations
    old_time = datetime.utcnow() - timedelta(days=35)
    
    # Add observations with different timestamps
    with storage.transaction() as conn:
        # Old processed observation (should be deleted)
        conn.execute(
            """INSERT INTO observations 
               (type, source_agent, data, created_at, processed)
               VALUES (?, ?, ?, ?, ?)""",
            ('old_type', 'test', '{}', old_time.isoformat(), True)
        )
        
        # Old unprocessed observation (should be kept)
        conn.execute(
            """INSERT INTO observations 
               (type, source_agent, data, created_at, processed)
               VALUES (?, ?, ?, ?, ?)""",
            ('old_type', 'test', '{}', old_time.isoformat(), False)
        )
    
    # Recent observation
    storage.add_observation('recent_type', {}, 'test')
    
    # Run cleanup
    storage.cleanup_old_data(days=30)
    
    # Check results
    all_obs = storage.get_observations()
    assert len(all_obs) == 2  # Recent + old unprocessed
    assert all(obs['type'] != 'old_type' or not obs['processed'] for obs in all_obs)


def test_concurrent_access(storage):
    """Test that storage handles concurrent access properly."""
    import threading
    import time
    
    results = []
    errors = []
    
    def add_observations(thread_id):
        try:
            for i in range(10):
                obs_id = storage.add_observation(
                    obs_type=f'thread_{thread_id}',
                    data={'index': i},
                    source_agent=f'thread_{thread_id}'
                )
                results.append(obs_id)
                time.sleep(0.01)  # Small delay to encourage contention
        except Exception as e:
            errors.append(e)
    
    # Run multiple threads
    threads = []
    for i in range(3):
        t = threading.Thread(target=add_observations, args=(i,))
        threads.append(t)
        t.start()
    
    # Wait for completion
    for t in threads:
        t.join()
    
    # Check results
    assert len(errors) == 0
    assert len(results) == 30
    assert len(set(results)) == 30  # All IDs unique