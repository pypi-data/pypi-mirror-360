"""Test ML pipeline functionality."""
import pytest
import tempfile
import asyncio
from pathlib import Path

from coppersun_brass.ml import QuickHeuristicFilter, EfficientMLClassifier, MLPipeline
from coppersun_brass.core.storage import Copper Alloy BrassStorage


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing."""
    with tempfile.TemporaryDirectory() as model_dir:
        with tempfile.TemporaryDirectory() as data_dir:
            yield Path(model_dir), Path(data_dir)


@pytest.fixture
def storage(temp_dirs):
    """Create test storage."""
    _, data_dir = temp_dirs
    db_path = data_dir / 'test.db'
    return Copper Alloy BrassStorage(db_path)


@pytest.fixture
def ml_pipeline(temp_dirs, storage):
    """Create ML pipeline for testing."""
    model_dir, _ = temp_dirs
    return MLPipeline(model_dir, storage)


class TestQuickHeuristicFilter:
    """Test quick heuristic filtering."""
    
    def test_trivial_file_detection(self):
        """Test detection of trivial files."""
        filter = QuickHeuristicFilter()
        
        # Test files
        test_cases = [
            ('test_utils.py', 'trivial'),
            ('conftest.py', 'trivial'),
            ('__pycache__/module.pyc', 'trivial'),
            ('README.md', 'trivial'),
            ('package.json', 'trivial'),
            ('.gitignore', 'trivial'),
        ]
        
        for file_path, expected in test_cases:
            obs = {'data': {'file': file_path}}
            result = filter.classify(obs)
            assert result.label == expected
            assert result.confidence >= 0.9
    
    def test_critical_file_detection(self):
        """Test detection of critical files."""
        filter = QuickHeuristicFilter()
        
        # Critical files
        test_cases = [
            ('auth.py', ['critical', 'important']),
            ('authentication.js', ['critical', 'important']),
            ('password_reset.py', ['critical', 'important']),
            ('payment_processor.py', ['critical', 'important']),
            ('user_permissions.py', ['critical', 'important']),
        ]
        
        for file_path, expected_labels in test_cases:
            obs = {'data': {'file': file_path}}
            result = filter.classify(obs)
            assert result.label in expected_labels
            assert result.confidence >= 0.7
    
    def test_critical_content_detection(self):
        """Test detection of critical content patterns."""
        filter = QuickHeuristicFilter()
        
        # Critical content
        test_cases = [
            ("password = 'hardcoded123'", 'critical', 'Hardcoded credential'),
            ("api_key = 'sk-1234567890'", 'critical', 'Hardcoded credential'),
            ("eval(user_input)", 'critical', 'Eval usage'),
            ("os.system(command)", 'critical', 'Shell command execution'),
        ]
        
        for content, expected_label, expected_reason in test_cases:
            obs = {
                'data': {
                    'file': 'app.py',
                    'content': content
                }
            }
            result = filter.classify(obs)
            assert result.label == expected_label
            assert result.confidence >= 0.9
            assert expected_reason in result.reason
    
    def test_important_file_detection(self):
        """Test detection of important files."""
        filter = QuickHeuristicFilter()
        
        test_cases = [
            'config.py',
            'settings.py',
            'database.py',
            'models.py',
            'api_routes.py',
            'utils.py',
        ]
        
        for file_path in test_cases:
            obs = {'data': {'file': file_path}}
            result = filter.classify(obs)
            # Should be either important or unknown (needs ML)
            assert result.label in ['important', 'unknown']
    
    def test_code_finding_classification(self):
        """Test classification of code findings."""
        filter = QuickHeuristicFilter()
        
        # High priority finding
        obs = {
            'type': 'code_finding',
            'data': {
                'file': 'app.py',
                'priority': 85,
                'description': 'SQL injection vulnerability'
            }
        }
        result = filter.classify(obs)
        assert result.label == 'critical'
        assert result.confidence >= 0.9
        
        # Low priority finding
        obs = {
            'type': 'code_finding',
            'data': {
                'file': 'utils.py',
                'priority': 15,
                'description': 'TODO: refactor this function'
            }
        }
        result = filter.classify(obs)
        assert result.label == 'trivial'


class TestEfficientMLClassifier:
    """Test ML classifier functionality."""
    
    def test_initialization(self, temp_dirs):
        """Test classifier initialization."""
        model_dir, _ = temp_dirs
        classifier = EfficientMLClassifier(model_dir)
        
        # Should initialize even without ML dependencies
        assert classifier is not None
        assert classifier.model_dir == model_dir
    
    def test_fallback_classification(self, temp_dirs):
        """Test fallback when ML unavailable."""
        model_dir, _ = temp_dirs
        classifier = EfficientMLClassifier(model_dir)
        
        # Force fallback mode
        classifier.enabled = False
        
        # Test fallback classification
        result = classifier.classify('test_file.py', 'def test(): pass')
        assert result[0] == 'trivial'  # test file
        assert result[1] >= 0.8
        
        result = classifier.classify('auth.py', 'def authenticate(): pass')
        assert result[0] == 'critical'  # auth file
        assert result[1] >= 0.7
    
    def test_batch_classification(self, temp_dirs):
        """Test batch classification."""
        model_dir, _ = temp_dirs
        classifier = EfficientMLClassifier(model_dir)
        
        items = [
            ('test_utils.py', 'def test(): pass'),
            ('auth.py', 'def login(): pass'),
            ('app.py', 'password = "secret"'),
        ]
        
        results = classifier.classify_batch(items)
        
        assert len(results) == 3
        assert all(isinstance(r, tuple) and len(r) == 2 for r in results)
        assert all(r[0] in ['trivial', 'important', 'critical'] for r in results)
        assert all(0.0 <= r[1] <= 1.0 for r in results)
    
    def test_cache_functionality(self, temp_dirs):
        """Test classification caching."""
        model_dir, _ = temp_dirs
        classifier = EfficientMLClassifier(model_dir)
        
        # Classify same file twice
        file_path = 'test.py'
        content = 'def hello(): pass'
        
        result1 = classifier.classify(file_path, content)
        result2 = classifier.classify(file_path, content)
        
        # Should return same result (from cache)
        assert result1 == result2


@pytest.mark.asyncio
class TestMLPipeline:
    """Test ML pipeline integration."""
    
    async def test_two_tier_filtering(self, ml_pipeline):
        """Test two-tier filtering process."""
        observations = [
            # Should be quick filtered
            {
                'type': 'file_modified',
                'data': {'file': 'test_utils.py'},
                'priority': 30
            },
            {
                'type': 'file_modified', 
                'data': {'file': 'README.md'},
                'priority': 10
            },
            # Should need ML
            {
                'type': 'file_modified',
                'data': {'file': 'app.py'},
                'priority': 50
            },
            {
                'type': 'code_finding',
                'data': {
                    'file': 'utils.py',
                    'description': 'Complex function needs refactoring',
                    'priority': 60
                }
            },
        ]
        
        results = await ml_pipeline.process_observations(observations)
        
        assert len(results) == len(observations)
        
        # Check all have classification
        for result in results:
            assert 'classification' in result
            assert 'confidence' in result
            assert 'ml_used' in result
            assert result['classification'] in ['trivial', 'important', 'critical']
        
        # First two should be quick filtered
        assert results[0]['ml_used'] is False
        assert results[1]['ml_used'] is False
        
        # Check statistics
        stats = ml_pipeline.get_stats()
        assert stats['total_processed'] == 4
        assert stats['quick_filtered'] >= 2
    
    async def test_batch_processing(self, ml_pipeline):
        """Test batch processing efficiency."""
        # Create many observations
        observations = []
        for i in range(50):
            observations.append({
                'type': 'file_modified',
                'data': {'file': f'file_{i}.py'},
                'priority': 40 + (i % 30)
            })
        
        start_time = asyncio.get_event_loop().time()
        results = await ml_pipeline.process_observations(observations)
        elapsed = asyncio.get_event_loop().time() - start_time
        
        assert len(results) == 50
        
        # Should be reasonably fast even with ML
        assert elapsed < 2.0  # 2 seconds for 50 items
        
        # Check batching worked
        stats = ml_pipeline.get_stats()
        assert stats['ml_processed'] > 0  # Some should need ML
    
    async def test_ml_failure_handling(self, ml_pipeline):
        """Test handling of ML failures."""
        # Force ML to fail
        ml_pipeline.ml_classifier.enabled = False
        
        observations = [{
            'type': 'file_modified',
            'data': {'file': 'unknown.xyz'},  # Unknown file type
            'priority': 50
        }]
        
        results = await ml_pipeline.process_observations(observations)
        
        # Should still get results
        assert len(results) == 1
        assert 'classification' in results[0]
        assert results[0]['ml_used'] is False
    
    async def test_cleanup(self, ml_pipeline):
        """Test pipeline cleanup."""
        # Add some observations
        observations = [{
            'type': 'file_modified',
            'data': {'file': 'test.py'},
            'priority': 50
        }]
        
        await ml_pipeline.process_observations(observations)
        
        # Cleanup should work without errors
        await ml_pipeline.shutdown()
        
        # Check executor is shutdown
        assert ml_pipeline.executor._shutdown