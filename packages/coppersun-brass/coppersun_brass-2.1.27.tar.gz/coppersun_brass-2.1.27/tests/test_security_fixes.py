"""Test security fixes for Copper Alloy Brass."""
from pathlib import Path
import tempfile
import os
import sys

# Add devmind to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from coppersun_brass.agents.scout.scout_agent import ScoutAgent
from coppersun_brass.core.storage import Copper Alloy BrassStorage
from coppersun_brass.ml.efficient_classifier import EfficientMLClassifier
from coppersun_brass.integrations.claude_api import ClaudeAnalyzer


class TestSecurityFixes:
    """Test security fixes are working."""
    
    def test_path_traversal_prevention(self):
        """Test that path traversal is prevented."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scout = ScoutAgent(dcp_path=tmpdir)
            
            # Test absolute path outside CWD
            files = scout._get_files_to_analyze("/etc/passwd")
            assert files == [], "Should block absolute paths outside CWD"
            
            # Test relative path traversal
            files = scout._get_files_to_analyze("../../etc/passwd")
            assert files == [], "Should block relative traversal"
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = Copper Alloy BrassStorage(Path(tmpdir) / "test.db")
            
            # Test non-integer IDs
            try:
                storage.mark_observations_processed([1, "2; DROP TABLE observations;"])
                assert False, "Should have raised ValueError"
            except ValueError as e:
                assert "must be integers" in str(e)
    
    def test_cache_memory_limit(self):
        """Test cache doesn't grow unbounded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            classifier = EfficientMLClassifier(Path(tmpdir))
            classifier.max_cache_size = 100  # Small limit for testing
            
            # Add more items than limit
            for i in range(200):
                classifier.cache[f"key_{i}"] = ("result", 0.5)
            
            # Cache should not exceed limit
            assert len(classifier.cache) <= 100, f"Cache size {len(classifier.cache)} exceeds limit"
    
    def test_api_key_validation(self):
        """Test API key validation."""
        # Invalid keys should not initialize client
        invalid_keys = [
            "wrong-format",
            "sk-wrong-prefix-1234567890123456789012345678901234567890",
            "sk-ant-tooshort",
        ]
        
        for key in invalid_keys:
            analyzer = ClaudeAnalyzer(api_key=key)
            assert analyzer.api_key is None, f"Key {key} should be rejected"
            assert analyzer.client is None, f"Client should not initialize with {key}"
        
        # Valid format (even if not real) should pass validation
        valid_key = "sk-ant-" + "a" * 50
        analyzer = ClaudeAnalyzer(api_key=valid_key)
        # Key is set but client may still be None if anthropic package errors
        assert analyzer.api_key == valid_key, "Valid format key should be accepted"


if __name__ == "__main__":
    # Run tests
    test = TestSecurityFixes()
    
    print("Testing path traversal prevention...")
    test.test_path_traversal_prevention()
    print("✓ Path traversal blocked")
    
    print("\nTesting SQL injection prevention...")
    test.test_sql_injection_prevention()
    print("✓ SQL injection blocked")
    
    print("\nTesting cache memory limit...")
    test.test_cache_memory_limit()
    print("✓ Cache memory limited")
    
    print("\nTesting API key validation...")
    test.test_api_key_validation()
    print("✓ API key validation working")
    
    print("\n✅ All security tests passed!")