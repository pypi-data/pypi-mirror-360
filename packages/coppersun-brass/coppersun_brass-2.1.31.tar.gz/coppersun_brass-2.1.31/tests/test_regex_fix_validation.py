#!/usr/bin/env python3
"""
Test validation for the regex fix in content safety URL encoding pattern.
Tests the corrected obfuscation_patterns.url_encoded regex pattern.
"""

import re
import sys
import os
import unittest
from typing import List, Tuple

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from coppersun_brass.integrations.content_safety import PatternLoader
    CONTENT_SAFETY_AVAILABLE = True
except ImportError:
    CONTENT_SAFETY_AVAILABLE = False


class TestURLEncodingRegexFix(unittest.TestCase):
    """Test cases for the fixed URL encoding regex pattern."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.pattern = r'(?:%[0-9A-Fa-f]{2}){3,}'
        self.compiled_pattern = re.compile(self.pattern)
    
    def test_pattern_compiles_successfully(self):
        """Test that the corrected pattern compiles without errors."""
        try:
            compiled = re.compile(self.pattern)
            self.assertIsNotNone(compiled)
        except re.error as e:
            self.fail(f"Pattern compilation failed: {e}")
    
    def test_matches_valid_url_encoded_sequences(self):
        """Test that the pattern correctly matches valid URL-encoded sequences."""
        valid_cases = [
            ('%20%3A%2F', '3 URL-encoded sequences'),
            ('%48%65%6C%6C%6F', '5 URL-encoded sequences'),
            ('%20%3A%2F%21%40%23', '6 valid sequences'),
            ('%2B%3D%26%25%24%21', '6 special character sequences'),
            ('%41%42%43%44%45', '5 uppercase letter sequences'),
            ('%61%62%63%64%65', '5 lowercase letter sequences'),
        ]
        
        for test_input, description in valid_cases:
            with self.subTest(input=test_input, desc=description):
                match = self.compiled_pattern.search(test_input)
                self.assertIsNotNone(match, f"Should match {description}: '{test_input}'")
                self.assertEqual(match.group(0), test_input, f"Should match entire string: '{test_input}'")
    
    def test_does_not_match_insufficient_sequences(self):
        """Test that the pattern does not match insufficient URL-encoded sequences."""
        invalid_cases = [
            ('%20', '1 sequence - insufficient'),
            ('%20%3A', '2 sequences - insufficient'),
            ('', 'empty string'),
            ('normal text', 'no URL encoding'),
            ('%2', 'incomplete sequence'),
            ('%', 'incomplete sequence'),
        ]
        
        for test_input, description in invalid_cases:
            with self.subTest(input=test_input, desc=description):
                match = self.compiled_pattern.search(test_input)
                self.assertIsNone(match, f"Should NOT match {description}: '{test_input}'")
    
    def test_does_not_match_invalid_hex_sequences(self):
        """Test that the pattern does not match invalid hexadecimal sequences."""
        invalid_hex_cases = [
            ('%ZZ%20%3A', 'invalid hex in first sequence'),
            ('%20%GG%3A', 'invalid hex in middle sequence'),
            ('%20%3A%ZZ', 'invalid hex in last sequence'),
            ('%2G%3A%2F', 'invalid hex character G'),
            ('%2z%3A%2F', 'invalid hex character z'),
        ]
        
        for test_input, description in invalid_hex_cases:
            with self.subTest(input=test_input, desc=description):
                match = self.compiled_pattern.search(test_input)
                self.assertIsNone(match, f"Should NOT match {description}: '{test_input}'")
    
    def test_matches_embedded_sequences(self):
        """Test that the pattern correctly matches URL-encoded sequences within larger text."""
        embedded_cases = [
            ('prefix%20%3A%2Fsuffix', 'embedded in text'),
            ('Hello%20World%21%21%40', 'mixed with normal text'),
            ('https://example.com?param=%20%3A%2F%21', 'in URL parameter'),
        ]
        
        for test_input, description in embedded_cases:
            with self.subTest(input=test_input, desc=description):
                matches = self.compiled_pattern.findall(test_input)
                self.assertGreater(len(matches), 0, f"Should find matches {description}: '{test_input}'")
    
    @unittest.skipUnless(CONTENT_SAFETY_AVAILABLE, "Content safety module not available")
    def test_pattern_loads_from_yaml_config(self):
        """Test that the corrected pattern loads successfully from YAML configuration."""
        try:
            loader = PatternLoader()
            patterns = loader.load_patterns()
            
            # Navigate to the specific pattern
            obfuscation_patterns = patterns.get('obfuscation_patterns', {})
            url_encoded = obfuscation_patterns.get('url_encoded', {})
            
            self.assertIsNotNone(url_encoded, "url_encoded pattern should exist")
            
            pattern = url_encoded.get('pattern', '')
            self.assertEqual(pattern, self.pattern, "Pattern should match expected corrected pattern")
            
            # Test that the loaded pattern compiles
            compiled = re.compile(pattern)
            self.assertIsNotNone(compiled, "Loaded pattern should compile successfully")
            
        except Exception as e:
            self.fail(f"Failed to load pattern from YAML: {e}")
    
    def test_security_detection_functionality(self):
        """Test that the pattern still effectively detects obfuscated content."""
        # Test cases that should trigger security detection
        suspicious_cases = [
            '%20%3A%2F%2F%65%78%61%6D%70%6C%65%2E%63%6F%6D',  # URL encoding of "://example.com"
            '%6A%61%76%61%73%63%72%69%70%74%3A',  # "javascript:" in URL encoding
            '%3C%73%63%72%69%70%74%3E',  # "<script>" in URL encoding
        ]
        
        for test_input in suspicious_cases:
            with self.subTest(input=test_input):
                match = self.compiled_pattern.search(test_input)
                self.assertIsNotNone(match, f"Should detect suspicious URL-encoded content: '{test_input}'")
    
    def test_performance_with_large_input(self):
        """Test that the pattern performs reasonably with large inputs."""
        # Create a large string with some URL-encoded sequences
        large_input = 'normal text ' * 1000 + '%20%3A%2F%21%40%23' + ' more text ' * 1000
        
        import time
        start_time = time.time()
        match = self.compiled_pattern.search(large_input)
        end_time = time.time()
        
        self.assertIsNotNone(match, "Should find URL-encoded sequence in large input")
        self.assertLess(end_time - start_time, 1.0, "Pattern matching should complete within 1 second")


def run_validation_tests():
    """Run all validation tests and return results."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestURLEncodingRegexFix)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    print("🧪 Testing URL Encoding Regex Fix")
    print("=" * 50)
    
    success = run_validation_tests()
    
    if success:
        print("\n✅ All tests passed! The regex fix is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please review the regex pattern.")
        sys.exit(1)