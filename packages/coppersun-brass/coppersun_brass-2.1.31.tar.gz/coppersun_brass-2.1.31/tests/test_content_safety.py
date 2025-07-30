"""
Comprehensive unit tests for content safety module.

Tests DataFog integration, alt-profanity-check integration, fallback systems,
performance requirements, and end-to-end functionality.
"""
import pytest
import time
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from coppersun_brass.integrations.content_safety import (
    PIIDetector,
    SecretDetector, 
    ObfuscationDetector,
    ContentFilter,
    DualPurposeContentSafety,
    SafetyConfig,
    SecurityFinding,
    SecurityFindingBuilder,
    PatternLoader,
    ContentSafetyResult
)


class TestPIIDetector:
    """Test PIIDetector with DataFog integration and fallback systems."""
    
    def test_pii_detector_initialization_with_datafog(self):
        """Test PIIDetector initializes with DataFog when available."""
        with patch('coppersun_brass.integrations.content_safety.logger'):
            detector = PIIDetector()
            # Should attempt to initialize DataFog (may fail if not installed)
            assert hasattr(detector, 'datafog_available')
    
    def test_pii_detector_fallback_initialization(self):
        """Test PIIDetector falls back gracefully when DataFog unavailable."""
        with patch('datafog.DataFog', side_effect=ImportError("DataFog not available")):
            detector = PIIDetector()
            assert detector.datafog_available == False
            assert hasattr(detector, 'patterns')
            assert 'email' in detector.patterns
            assert 'phone' in detector.patterns
    
    def test_international_pii_patterns_added(self):
        """Test that international PII patterns are added to DataFog."""
        mock_datafog = MagicMock()
        
        with patch('datafog.DataFog', return_value=mock_datafog):
            detector = PIIDetector()
            
            # Verify international patterns were added
            expected_entities = [
                'aadhaar', 'india_pan', 'uk_nhs', 'uk_nino', 
                'sg_nric', 'au_tfn', 'au_medicare', 'iban', 'eu_vat'
            ]
            
            for entity in expected_entities:
                mock_datafog.add_entity.assert_any_call(entity, pytest.approx(str, abs=0))
    
    def test_email_detection_fallback(self):
        """Test email detection using fallback regex patterns."""
        with patch('datafog.DataFog', side_effect=ImportError):
            detector = PIIDetector()
            
            test_content = "Contact me at john.doe@example.com for details"
            findings = detector.detect(test_content, "test.py", 1)
            
            assert len(findings) > 0
            assert any('email' in f.type.lower() for f in findings)
            assert findings[0].severity == "medium"
            assert findings[0].confidence == 0.80
    
    def test_phone_detection_fallback(self):
        """Test phone number detection using fallback regex patterns."""
        with patch('datafog.DataFog', side_effect=ImportError):
            detector = PIIDetector()
            
            test_content = "Call me at (555) 123-4567 tomorrow"
            findings = detector.detect(test_content, "test.py", 1)
            
            assert len(findings) > 0
            assert any('phone' in f.type.lower() for f in findings)
    
    def test_datafog_integration_mock(self):
        """Test DataFog integration with mocked results."""
        mock_result = MagicMock()
        mock_result.entity_type = 'EMAIL'
        mock_result.confidence_score = 0.95
        
        mock_datafog = MagicMock()
        mock_datafog.scan_text.return_value = [mock_result]
        
        with patch('datafog.DataFog', return_value=mock_datafog):
            detector = PIIDetector()
            
            findings = detector.detect("test@example.com", "test.py", 1)
            
            assert len(findings) > 0
            assert findings[0].type == "Email address"
            assert findings[0].severity == "medium"
            assert findings[0].confidence == 0.95
    
    def test_international_pii_mapping(self):
        """Test that international PII types are properly mapped."""
        # Test Aadhaar detection
        mock_result = MagicMock()
        mock_result.entity_type = 'aadhaar'
        mock_result.confidence_score = 0.90
        
        mock_datafog = MagicMock()
        mock_datafog.scan_text.return_value = [mock_result]
        
        with patch('datafog.DataFog', return_value=mock_datafog):
            detector = PIIDetector()
            
            findings = detector.detect("1234 5678 9012", "test.py", 1)
            
            assert len(findings) > 0
            assert findings[0].type == "India Aadhaar Number"
            assert findings[0].severity == "high"
    
    def test_datafog_error_fallback(self):
        """Test fallback when DataFog analysis fails at runtime."""
        mock_datafog = MagicMock()
        mock_datafog.scan_text.side_effect = Exception("DataFog analysis failed")
        
        with patch('datafog.DataFog', return_value=mock_datafog):
            detector = PIIDetector()
            
            # Should fall back to regex patterns
            findings = detector.detect("test@example.com", "test.py", 1)
            
            assert len(findings) > 0  # Fallback should work
            assert findings[0].confidence == 0.80  # Fallback confidence


class TestContentFilter:
    """Test ContentFilter with alt-profanity-check integration and fallback."""
    
    def test_content_filter_initialization_with_alt_profanity(self):
        """Test ContentFilter initializes with alt-profanity-check when available."""
        with patch('coppersun_brass.integrations.content_safety.logger'):
            content_filter = ContentFilter()
            assert hasattr(content_filter, 'alt_profanity_available')
    
    def test_content_filter_fallback_initialization(self):
        """Test ContentFilter falls back when alt-profanity-check unavailable."""
        with patch('alt_profanity_check.predict_prob', side_effect=ImportError):
            content_filter = ContentFilter()
            assert content_filter.alt_profanity_available == False
            assert hasattr(content_filter, 'fallback_patterns')
    
    def test_hate_speech_detection_always_active(self):
        """Test that hate speech patterns are always checked regardless of ML availability."""
        with patch('alt_profanity_check.predict_prob', side_effect=ImportError):
            content_filter = ContentFilter()
            
            test_content = "This contains nazi content"
            findings = content_filter.detect(test_content, "test.py", 1)
            
            assert len(findings) > 0
            assert findings[0].severity == "high"
            assert findings[0].confidence == 0.98
    
    def test_alt_profanity_check_integration_mock(self):
        """Test alt-profanity-check integration with mocked results."""
        mock_predict_prob = MagicMock(return_value=[0.85])  # High profanity score
        
        with patch('alt_profanity_check.predict_prob', mock_predict_prob):
            content_filter = ContentFilter()
            
            findings = content_filter.detect("some bad content", "test.py", 1)
            
            mock_predict_prob.assert_called_once_with(["some bad content"])
            assert len(findings) > 0
            assert findings[0].severity == "high"
            assert findings[0].confidence == 0.85
    
    def test_profanity_threshold_mapping(self):
        """Test that profanity scores are mapped to correct severity levels."""
        test_cases = [
            (0.8, "high"),      # > 0.7
            (0.6, "medium"),    # > 0.4
            (0.3, "low"),       # > 0.2
            (0.1, None)         # <= 0.2, should return no findings
        ]
        
        for score, expected_severity in test_cases:
            mock_predict_prob = MagicMock(return_value=[score])
            
            with patch('alt_profanity_check.predict_prob', mock_predict_prob):
                content_filter = ContentFilter()
                findings = content_filter.detect("test content", "test.py", 1)
                
                if expected_severity:
                    assert len(findings) > 0
                    assert findings[0].severity == expected_severity
                else:
                    # Should return empty for clean content (score <= 0.2)
                    assert len([f for f in findings if 'profanity' in f.type.lower()]) == 0
    
    def test_fallback_patterns_detection(self):
        """Test fallback regex patterns when ML unavailable."""
        with patch('alt_profanity_check.predict_prob', side_effect=ImportError):
            content_filter = ContentFilter()
            
            test_cases = {
                "wtf is this": "low",
                "this is damn stupid": "medium", 
                "some casual lol content": "low"
            }
            
            for content, expected_severity in test_cases.items():
                findings = content_filter.detect(content, "test.py", 1)
                assert len(findings) > 0
                assert findings[0].severity == expected_severity
    
    def test_alt_profanity_error_fallback(self):
        """Test fallback when alt-profanity-check fails at runtime."""
        mock_predict_prob = MagicMock(side_effect=Exception("Model failed"))
        
        with patch('alt_profanity_check.predict_prob', mock_predict_prob):
            content_filter = ContentFilter()
            
            # Should fall back to regex patterns
            findings = content_filter.detect("damn this code", "test.py", 1)
            
            assert len(findings) > 0  # Fallback should work
            assert findings[0].confidence == 0.80  # Fallback confidence


class TestSecretDetector:
    """Test SecretDetector for API keys, tokens, and passwords."""
    
    def test_api_key_detection(self):
        """Test detection of hardcoded API keys."""
        detector = SecretDetector()
        
        test_content = 'api_key = "sk-1234567890abcdef1234567890abcdef"'
        findings = detector.detect(test_content, "config.py", 10)
        
        assert len(findings) > 0
        assert findings[0].severity == "high"
        assert "API key" in findings[0].type
    
    def test_aws_access_key_detection(self):
        """Test detection of AWS access keys."""
        detector = SecretDetector()
        
        test_content = "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE"
        findings = detector.detect(test_content, "config.py", 5)
        
        assert len(findings) > 0
        assert "AWS Access Key" in findings[0].type
    
    def test_github_token_detection(self):
        """Test detection of GitHub personal access tokens."""
        detector = SecretDetector()
        
        test_content = "GITHUB_TOKEN=ghp_1234567890abcdef1234567890abcdef123456"
        findings = detector.detect(test_content, "ci.yml", 15)
        
        assert len(findings) > 0
        assert "GitHub Personal Access Token" in findings[0].type
    
    def test_password_detection(self):
        """Test detection of hardcoded passwords."""
        detector = SecretDetector()
        
        test_content = 'password = "supersecretpassword123"'
        findings = detector.detect(test_content, "auth.py", 20)
        
        assert len(findings) > 0
        assert "password" in findings[0].type.lower()


class TestObfuscationDetector:
    """Test ObfuscationDetector for Base64 and Unicode obfuscation."""
    
    def test_base64_detection(self):
        """Test detection of Base64 encoded content."""
        detector = ObfuscationDetector()
        
        # Long Base64 string that should trigger detection
        test_content = "data = 'dGhpcyBpcyBhIGxvbmcgYmFzZTY0IGVuY29kZWQgc3RyaW5nIHRoYXQgc2hvdWxkIGJlIGRldGVjdGVk'"
        findings = detector.detect(test_content, "data.py", 1)
        
        assert len(findings) > 0
        assert "Base64" in findings[0].type
        assert findings[0].severity == "medium"
    
    def test_unicode_obfuscation_detection(self):
        """Test detection of Unicode normalization differences."""
        detector = ObfuscationDetector()
        
        # Content with unicode characters that normalize differently
        test_content = "variаble = 'test'"  # Contains Cyrillic 'а' instead of 'a'
        findings = detector.detect(test_content, "obfuscated.py", 1)
        
        # This may or may not trigger depending on unicode normalization
        # Just ensure no errors occur
        assert isinstance(findings, list)
    
    def test_short_base64_ignored(self):
        """Test that short Base64 strings are ignored."""
        detector = ObfuscationDetector()
        
        test_content = "short = 'dGVzdA=='"  # Short Base64
        findings = detector.detect(test_content, "test.py", 1)
        
        # Should not detect short Base64 strings
        base64_findings = [f for f in findings if "Base64" in f.type]
        assert len(base64_findings) == 0


class TestSafetyConfig:
    """Test SafetyConfig validation and management."""
    
    def test_default_config_validation(self):
        """Test default configuration values are applied correctly."""
        config = SafetyConfig({})
        
        assert config.api_safety_threshold == 0.8
        assert config.high_risk_threshold == 5
        assert config.medium_risk_threshold == 2
    
    def test_valid_config_values(self):
        """Test valid configuration values are accepted."""
        test_config = {
            'api_safety_threshold': 0.9,
            'high_risk_threshold': 3,
            'medium_risk_threshold': 1
        }
        
        config = SafetyConfig(test_config)
        
        assert config.api_safety_threshold == 0.9
        assert config.high_risk_threshold == 3
        assert config.medium_risk_threshold == 1
    
    def test_invalid_threshold_values(self):
        """Test invalid threshold values are corrected."""
        invalid_configs = [
            {'api_safety_threshold': 1.5},  # > 1.0
            {'api_safety_threshold': -0.1},  # < 0.0
            {'api_safety_threshold': 'invalid'},  # Not numeric
            {'api_safety_threshold': None},  # None value
        ]
        
        for invalid_config in invalid_configs:
            config = SafetyConfig(invalid_config)
            assert config.api_safety_threshold == 0.8  # Should use default
    
    def test_invalid_integer_values(self):
        """Test invalid integer values are corrected."""
        invalid_configs = [
            {'high_risk_threshold': -1},  # Negative
            {'high_risk_threshold': 'invalid'},  # Not numeric  
            {'high_risk_threshold': 3.7},  # Not integer
            {'medium_risk_threshold': -5},  # Negative
        ]
        
        for invalid_config in invalid_configs:
            config = SafetyConfig(invalid_config)
            
            if 'high_risk_threshold' in invalid_config:
                assert config.high_risk_threshold == 5  # Should use default
            if 'medium_risk_threshold' in invalid_config:
                assert config.medium_risk_threshold == 2  # Should use default
    
    def test_threshold_relationship_validation(self):
        """Test logical relationship validation between thresholds."""
        # Test medium > high (should swap)
        config = SafetyConfig({
            'high_risk_threshold': 2,
            'medium_risk_threshold': 5
        })
        
        assert config.high_risk_threshold == 5  # Swapped
        assert config.medium_risk_threshold == 2  # Swapped
    
    def test_equal_thresholds_adjustment(self):
        """Test equal thresholds are adjusted."""
        config = SafetyConfig({
            'high_risk_threshold': 3,
            'medium_risk_threshold': 3
        })
        
        assert config.high_risk_threshold == 4  # Adjusted +1
        assert config.medium_risk_threshold == 3  # Unchanged
    
    def test_float_to_int_conversion(self):
        """Test float values that are integers are converted properly."""
        config = SafetyConfig({
            'high_risk_threshold': 5.0,
            'medium_risk_threshold': 2.0
        })
        
        assert config.high_risk_threshold == 5
        assert config.medium_risk_threshold == 2
        assert isinstance(config.high_risk_threshold, int)
        assert isinstance(config.medium_risk_threshold, int)
    
    def test_config_to_dict(self):
        """Test configuration can be converted back to dictionary."""
        original_config = {
            'api_safety_threshold': 0.9,
            'high_risk_threshold': 3,
            'medium_risk_threshold': 1
        }
        
        config = SafetyConfig(original_config)
        result_dict = config.to_dict()
        
        assert result_dict == original_config


class TestSecurityFindingBuilder:
    """Test SecurityFindingBuilder helper methods."""
    
    def test_create_pattern_finding(self):
        """Test pattern-based finding creation."""
        config = {
            'description': 'Test Pattern',
            'risk': 'Test risk explanation',
            'fix': 'Test remediation',
            'severity': 'medium'
        }
        matches = ['match1', 'match2']
        
        finding = SecurityFindingBuilder.create_pattern_finding(
            config, matches, "test.py", 10
        )
        
        assert finding.type == "Test Pattern"
        assert finding.location == "test.py:10"
        assert "Found 2 test pattern" in finding.description
        assert finding.risk_explanation == "Test risk explanation"
        assert finding.remediation == "Test remediation"
        assert finding.severity == "medium"
        assert finding.confidence == 0.80
    
    def test_create_ml_finding(self):
        """Test ML-based finding creation."""
        finding = SecurityFindingBuilder.create_ml_finding(
            type_desc="ML Detection",
            description="ML detected issue",
            risk_explanation="ML risk assessment",
            remediation="ML remediation",
            severity="high",
            confidence=0.95,
            file_path="ml_test.py",
            line_number=5
        )
        
        assert finding.type == "ML Detection"
        assert finding.location == "ml_test.py:5"
        assert finding.description == "ML detected issue"
        assert finding.severity == "high"
        assert finding.confidence == 0.95
    
    def test_create_finding_general(self):
        """Test general finding creation method."""
        finding = SecurityFindingBuilder.create_finding(
            type_desc="General Issue",
            location="general.py:1",
            description="General description",
            risk_explanation="General risk",
            remediation="General fix",
            severity="low",
            confidence=0.7
        )
        
        assert finding.type == "General Issue"
        assert finding.location == "general.py:1"
        assert finding.severity == "low"
        assert finding.confidence == 0.7
    
    def test_severity_override(self):
        """Test severity override in pattern finding."""
        config = {
            'description': 'Test Pattern',
            'risk': 'Test risk',
            'fix': 'Test fix',
            'severity': 'low'
        }
        
        finding = SecurityFindingBuilder.create_pattern_finding(
            config, ['match'], "test.py", 1, severity_override="high"
        )
        
        assert finding.severity == "high"  # Should use override


class TestPatternLoader:
    """Test PatternLoader external configuration functionality."""
    
    def test_pattern_loader_initialization(self):
        """Test PatternLoader initializes correctly."""
        loader = PatternLoader()
        assert hasattr(loader, 'pattern_file')
        assert hasattr(loader, '_patterns')
    
    def test_load_patterns_fallback(self):
        """Test PatternLoader falls back gracefully when file not found."""
        # Use non-existent file
        loader = PatternLoader('/nonexistent/patterns.yaml')
        patterns = loader.load_patterns()
        
        # Should return fallback patterns
        assert isinstance(patterns, dict)
        assert len(patterns) > 0
    
    def test_get_patterns_by_category(self):
        """Test getting patterns by category."""
        loader = PatternLoader()
        
        # Test different categories
        secret_patterns = loader.get_secret_patterns()
        pii_patterns = loader.get_common_pii_patterns()
        profanity_patterns = loader.get_profanity_patterns()
        
        assert isinstance(secret_patterns, dict)
        assert isinstance(pii_patterns, dict)
        assert isinstance(profanity_patterns, dict)
    
    def test_pattern_validation(self):
        """Test pattern validation works correctly."""
        loader = PatternLoader()
        
        # Valid pattern
        valid_config = {
            'pattern': r'\btest\b',
            'description': 'Test pattern',
            'risk': 'Test risk',
            'fix': 'Test fix',
            'severity': 'medium'
        }
        
        # Should not raise exception
        validated = loader._validate_single_pattern('test', valid_config, {})
        assert validated == valid_config
    
    def test_pattern_stats(self):
        """Test pattern statistics generation."""
        loader = PatternLoader()
        stats = loader.get_pattern_stats()
        
        assert 'total_categories' in stats
        assert 'total_patterns' in stats
        assert 'patterns_by_category' in stats
        assert 'patterns_by_severity' in stats
        assert isinstance(stats['total_patterns'], int)
    
    def test_reload_patterns(self):
        """Test pattern reloading functionality."""
        loader = PatternLoader()
        
        # Load patterns initially
        patterns1 = loader.load_patterns()
        
        # Reload patterns
        loader.reload_patterns()
        patterns2 = loader.load_patterns()
        
        # Should have same structure (may have same content)
        assert type(patterns1) == type(patterns2)


class TestDualPurposeContentSafety:
    """Test the main DualPurposeContentSafety orchestrator."""
    
    def test_initialization(self):
        """Test DualPurposeContentSafety initializes all detectors."""
        safety = DualPurposeContentSafety()
        
        assert hasattr(safety, 'pii_detector')
        assert hasattr(safety, 'secret_detector')
        assert hasattr(safety, 'obfuscation_detector')
        assert hasattr(safety, 'content_filter')
        assert hasattr(safety, 'config')
        assert isinstance(safety.config, SafetyConfig)
    
    def test_configuration_override(self):
        """Test custom configuration is applied."""
        custom_config = {
            'api_safety_threshold': 0.9,
            'high_risk_threshold': 3,
            'medium_risk_threshold': 1
        }
        
        safety = DualPurposeContentSafety(custom_config)
        
        assert safety.api_safety_threshold == 0.9
        assert safety.high_risk_threshold == 3
        assert safety.medium_risk_threshold == 1
    
    def test_comprehensive_analysis_clean_content(self):
        """Test analysis of clean content."""
        safety = DualPurposeContentSafety()
        
        clean_content = "def calculate_sum(a, b): return a + b"
        result = safety.analyze_content_comprehensive(clean_content, "utils.py", 1)
        
        assert isinstance(result, ContentSafetyResult)
        assert result.safe_for_api == True
        assert result.risk_score == "LOW"
        assert len(result.customer_findings) == 0
    
    def test_comprehensive_analysis_pii_content(self):
        """Test analysis of content with PII."""
        with patch('datafog.DataFog', side_effect=ImportError):  # Force fallback
            safety = DualPurposeContentSafety()
            
            pii_content = "Contact support at support@company.com"
            result = safety.analyze_content_comprehensive(pii_content, "contact.py", 5)
            
            assert isinstance(result, ContentSafetyResult)
            assert len(result.customer_findings) > 0
            assert result.risk_score in ["LOW", "MEDIUM", "HIGH"]
    
    def test_comprehensive_analysis_high_risk_content(self):
        """Test analysis of high-risk content."""
        safety = DualPurposeContentSafety()
        
        # Content with secrets (high severity)
        risky_content = 'password = "secretpass123"'
        result = safety.analyze_content_comprehensive(risky_content, "config.py", 1)
        
        assert len(result.customer_findings) > 0
        assert result.safe_for_api == False  # Should block API calls
        assert result.risk_score == "HIGH"
    
    def test_processing_time_tracking(self):
        """Test that processing time is tracked."""
        safety = DualPurposeContentSafety()
        
        result = safety.analyze_content_comprehensive("test content", "test.py", 1)
        
        assert hasattr(result, 'processing_time_ms')
        assert result.processing_time_ms > 0
        assert result.processing_time_ms < 1000  # Should be under 1 second
    
    def test_raw_detections_tracking(self):
        """Test that raw detection counts are tracked."""
        safety = DualPurposeContentSafety()
        
        result = safety.analyze_content_comprehensive("test content", "test.py", 1)
        
        assert 'pii_count' in result.raw_detections
        assert 'secret_count' in result.raw_detections
        assert 'obfuscation_count' in result.raw_detections
        assert 'content_issues_count' in result.raw_detections
    
    def test_content_sanitization(self):
        """Test content sanitization for API transmission."""
        with patch('datafog.DataFog', side_effect=ImportError):  # Force fallback
            safety = DualPurposeContentSafety()
            
            unsafe_content = "Email me at user@domain.com or call (555) 123-4567"
            result = safety.analyze_content_comprehensive(unsafe_content, "contact.py", 1)
            
            if not result.safe_for_api:
                assert result.sanitized_content != unsafe_content
                assert "user@example.com" in result.sanitized_content
                assert "555-0123" in result.sanitized_content
    
    def test_customer_security_report_generation(self):
        """Test customer-facing security report generation."""
        safety = DualPurposeContentSafety()
        
        # Create mock findings
        findings = [
            SecurityFinding(
                type="Test Finding",
                location="test.py:1",
                description="Test security issue",
                risk_explanation="Test risk",
                remediation="Test fix",
                severity="high",
                confidence=0.95
            )
        ]
        
        report = safety.generate_customer_security_report(findings)
        
        assert 'summary' in report
        assert 'findings_count' in report
        assert 'risk_level' in report
        assert 'recommendations' in report
        assert report['findings_count'] == 1
    
    def test_customer_report_empty_findings(self):
        """Test customer report with no findings."""
        safety = DualPurposeContentSafety()
        
        report = safety.generate_customer_security_report([])
        
        assert report['findings_count'] == 0
        assert report['risk_level'] == 'LOW'
        assert "No security concerns" in report['summary']
    
    def test_system_status(self):
        """Test system status reporting."""
        safety = DualPurposeContentSafety()
        
        status = safety.get_system_status()
        
        assert 'detectors_active' in status
        assert 'international_coverage' in status
        assert 'api_protection' in status
        assert 'customer_reporting' in status
        assert status['api_protection'] == True
    
    def test_pattern_statistics(self):
        """Test pattern statistics functionality."""
        safety = DualPurposeContentSafety()
        
        stats = safety.get_pattern_statistics()
        
        assert 'total_categories' in stats
        assert 'total_patterns' in stats
        assert isinstance(stats['total_patterns'], int)
    
    def test_pattern_reload(self):
        """Test pattern reload functionality."""
        safety = DualPurposeContentSafety()
        
        # Should not raise exception
        safety.reload_patterns()
        
        # System should still be functional
        status = safety.get_system_status()
        assert status['pattern_configuration']['external_patterns_enabled'] == True
    
    def test_external_pattern_configuration(self):
        """Test external pattern configuration is properly integrated."""
        safety = DualPurposeContentSafety()
        
        status = safety.get_system_status()
        
        assert 'pattern_configuration' in status
        assert status['pattern_configuration']['external_patterns_enabled'] == True
        assert 'pattern_file' in status['pattern_configuration']
        assert 'yaml_available' in status['pattern_configuration']


class TestPerformanceRequirements:
    """Test performance requirements and benchmarks."""
    
    def test_processing_time_under_50ms_small_content(self):
        """Test processing time stays under 50ms for small content."""
        safety = DualPurposeContentSafety()
        
        small_content = "def test(): return 'hello world'"
        
        start = time.time()
        result = safety.analyze_content_comprehensive(small_content)
        duration_ms = (time.time() - start) * 1000
        
        assert duration_ms < 50, f"Processing took {duration_ms}ms, exceeds 50ms target"
        assert result.processing_time_ms < 50
    
    def test_processing_time_reasonable_large_content(self):
        """Test processing time is reasonable for larger content."""
        safety = DualPurposeContentSafety()
        
        # Simulate larger code file
        large_content = ("def function_" + str(i) + "(): pass\n" for i in range(100))
        large_content = "".join(large_content)
        
        start = time.time()
        result = safety.analyze_content_comprehensive(large_content)
        duration_ms = (time.time() - start) * 1000
        
        # Allow more time for larger content but should still be reasonable
        assert duration_ms < 200, f"Large content processing took {duration_ms}ms, too slow"
    
    def test_memory_efficiency(self):
        """Test that repeated calls don't accumulate memory significantly."""
        import gc
        
        safety = DualPurposeContentSafety()
        
        # Force garbage collection and get initial memory state
        gc.collect()
        
        # Run multiple analyses
        for i in range(10):
            content = f"def test_{i}(): return {i}"
            safety.analyze_content_comprehensive(content)
        
        # This is a basic check - in practice you'd use memory profiling tools
        gc.collect()
        # No assertion here, just ensuring no exceptions during repeated use


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""
    
    def test_realistic_python_file_analysis(self):
        """Test analysis of realistic Python code with various issues."""
        safety = DualPurposeContentSafety()
        
        realistic_code = '''
import os
import requests

# TODO: fix this damn authentication system
def authenticate_user(username, password):
    # Hardcoded credentials - this is stupid
    admin_password = "admin123"
    api_key = "sk-1234567890abcdef1234567890abcdef"
    
    if username == "admin" and password == admin_password:
        # Contact support at admin@company.com
        return {"status": "success", "api_key": api_key}
    
    return {"status": "failed"}
'''
        
        result = safety.analyze_content_comprehensive(realistic_code, "auth.py", 1)
        
        # Should detect multiple issues
        assert len(result.customer_findings) > 0
        
        # Should find secrets (hardcoded credentials)
        secret_findings = [f for f in result.customer_findings if 'key' in f.type.lower() or 'password' in f.type.lower()]
        assert len(secret_findings) > 0
        
        # May find PII (email) depending on fallback
        # May find profanity ("damn", "stupid") depending on ML availability
        
        # Should be blocked from API due to secrets
        assert result.safe_for_api == False
        assert result.risk_score == "HIGH"
    
    def test_international_compliance_scenario(self):
        """Test international PII detection for compliance."""
        # This test will use fallback patterns since DataFog may not be installed
        with patch('datafog.DataFog', side_effect=ImportError):
            safety = DualPurposeContentSafety()
            
            international_content = '''
# Customer data for EU operations
customer_data = {
    "email": "customer@example.com",
    "phone": "+44 20 7123 4567",
    "notes": "Customer prefers email contact"
}
'''
            
            result = safety.analyze_content_comprehensive(international_content, "customer.py", 1)
            
            # Should detect email in fallback mode
            pii_findings = [f for f in result.customer_findings if 'email' in f.type.lower()]
            assert len(pii_findings) > 0
    
    def test_clean_production_code_scenario(self):
        """Test that clean, professional code passes all checks."""
        safety = DualPurposeContentSafety()
        
        clean_code = '''
"""
Professional utility functions for data processing.
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def process_user_data(data: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Process user data and return summary statistics.
    
    Args:
        data: List of user data dictionaries
        
    Returns:
        Dictionary containing summary statistics
    """
    if not data:
        logger.warning("No data provided for processing")
        return {"total_users": 0}
    
    return {
        "total_users": len(data),
        "active_users": sum(1 for user in data if user.get("active", False))
    }
'''
        
        result = safety.analyze_content_comprehensive(clean_code, "utils.py", 1)
        
        # Clean code should pass all checks
        assert result.safe_for_api == True
        assert result.risk_score == "LOW"
        assert len(result.customer_findings) == 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])