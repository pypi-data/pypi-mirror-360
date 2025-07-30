"""
Dual-Purpose Content Safety System
Provides both API protection and customer-facing security analysis.

Functions:
1. API Protection: Filter sensitive content before Claude API calls
2. Customer Value: Generate actionable security audit reports

Based on ChatGPT recommendations and Phase 3 requirements.
"""
import re
import logging
import hashlib
import unicodedata
import time
import statistics
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

logger = logging.getLogger(__name__)


class PatternLoader:
    """Load and validate security patterns from YAML configuration."""
    
    def __init__(self, pattern_file: Optional[str] = None):
        """Initialize pattern loader with optional custom pattern file."""
        self.pattern_file = pattern_file or self._get_default_pattern_file()
        self._patterns = None
        self._validation_rules = None
    
    def _get_default_pattern_file(self) -> str:
        """Get the default pattern file path."""
        return os.path.join(os.path.dirname(__file__), 'patterns.yaml')
    
    def load_patterns(self) -> Dict[str, Any]:
        """Load patterns from YAML file with validation."""
        if self._patterns is None:
            try:
                if not YAML_AVAILABLE:
                    logger.warning("PyYAML not available, using fallback patterns")
                    return self._get_fallback_patterns()
                
                with open(self.pattern_file, 'r', encoding='utf-8') as f:
                    raw_patterns = yaml.safe_load(f)
                
                # Validate patterns
                self._patterns = self._validate_patterns(raw_patterns)
                logger.info(f"Loaded {len(self._patterns)} pattern categories from {self.pattern_file}")
                
            except FileNotFoundError:
                logger.warning(f"Pattern file not found: {self.pattern_file}, using fallback patterns")
                self._patterns = self._get_fallback_patterns()
            except yaml.YAMLError as e:
                logger.error(f"YAML parsing error in {self.pattern_file}: {e}")
                self._patterns = self._get_fallback_patterns()
            except Exception as e:
                logger.error(f"Error loading patterns: {e}")
                self._patterns = self._get_fallback_patterns()
        
        return self._patterns
    
    def _validate_patterns(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Validate pattern structure and content."""
        if not isinstance(patterns, dict):
            raise ValueError("Patterns must be a dictionary")
        
        validation_rules = patterns.get('validation', {})
        self._validation_rules = validation_rules
        
        validated = {}
        for category_name, category_patterns in patterns.items():
            if category_name == 'validation':
                continue  # Skip validation rules
            
            if not isinstance(category_patterns, dict):
                logger.warning(f"Skipping invalid category {category_name}: not a dictionary")
                continue
            
            validated_category = {}
            for pattern_name, pattern_config in category_patterns.items():
                try:
                    validated_pattern = self._validate_single_pattern(
                        pattern_name, pattern_config, validation_rules
                    )
                    validated_category[pattern_name] = validated_pattern
                except Exception as e:
                    logger.warning(f"Skipping invalid pattern {category_name}.{pattern_name}: {e}")
            
            if validated_category:
                validated[category_name] = validated_category
        
        return validated
    
    def _validate_single_pattern(self, name: str, config: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single pattern configuration."""
        if not isinstance(config, dict):
            raise ValueError(f"Pattern {name} must be a dictionary")
        
        # Check required fields
        required_fields = rules.get('required_fields', ['pattern', 'description', 'risk', 'fix', 'severity'])
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate pattern itself
        pattern = config['pattern']
        if not isinstance(pattern, str):
            raise ValueError("Pattern must be a string")
        
        max_length = rules.get('max_pattern_length', 1000)
        if len(pattern) > max_length:
            raise ValueError(f"Pattern too long: {len(pattern)} > {max_length}")
        
        # Test regex compilation
        try:
            re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        
        # Validate severity
        severity = config.get('severity', 'medium')
        valid_severities = rules.get('valid_severities', ['low', 'medium', 'high', 'critical'])
        if severity not in valid_severities:
            raise ValueError(f"Invalid severity '{severity}', must be one of: {valid_severities}")
        
        # Validate region if present
        if 'region' in config:
            region = config['region']
            valid_regions = rules.get('valid_regions', ['US', 'UK', 'EU', 'IN', 'SG', 'AU', 'CA', 'global'])
            if region not in valid_regions:
                logger.warning(f"Unknown region '{region}' for pattern {name}")
        
        return config
    
    def get_patterns_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """Get patterns for a specific category."""
        patterns = self.load_patterns()
        return patterns.get(category, {})
    
    def get_international_pii_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Get international PII patterns."""
        return self.get_patterns_by_category('international_pii')
    
    def get_common_pii_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Get common PII patterns."""
        return self.get_patterns_by_category('common_pii')
    
    def get_secret_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Get secret detection patterns."""
        return self.get_patterns_by_category('secret_patterns')
    
    def get_profanity_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Get profanity detection patterns."""
        return self.get_patterns_by_category('profanity_patterns')
    
    def get_obfuscation_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Get obfuscation detection patterns."""
        return self.get_patterns_by_category('obfuscation_patterns')
    
    def _get_fallback_patterns(self) -> Dict[str, Any]:
        """Fallback patterns when YAML loading fails."""
        return {
            'common_pii': {
                'email': {
                    'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                    'description': 'Email address',
                    'risk': 'Personal contact information exposure',
                    'fix': 'Move to configuration files or environment variables',
                    'severity': 'medium'
                },
                'phone': {
                    'pattern': r'\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}',
                    'description': 'Phone number',
                    'risk': 'Personal contact information',
                    'fix': 'Replace with clearly fake numbers (555-0123) or move to config',
                    'severity': 'medium'
                }
            },
            'secret_patterns': {
                'api_key_assignment': {
                    'pattern': r'(?:api[_-]?key|token|secret)["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]{20,})["\']?',
                    'description': 'Hardcoded API key or token',
                    'risk': 'Exposed API credentials can lead to unauthorized access',
                    'fix': 'Use environment variables: os.getenv("API_KEY")',
                    'severity': 'high'
                }
            },
            'profanity_patterns': {
                'hate_speech_indicators': {
                    'pattern': r'\b(?:nazi|kike|spic|chink|nigger|faggot)\b',
                    'description': 'Hate speech content',
                    'risk': 'Hate speech content violates professional standards and may create legal issues',
                    'fix': 'Remove immediately - not appropriate in any professional context',
                    'severity': 'high'
                }
            }
        }
    
    def reload_patterns(self) -> None:
        """Force reload patterns from file."""
        self._patterns = None
        self.load_patterns()
    
    def get_pattern_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded patterns."""
        patterns = self.load_patterns()
        stats = {
            'total_categories': len(patterns),
            'total_patterns': 0,
            'patterns_by_category': {},
            'patterns_by_severity': {'low': 0, 'medium': 0, 'high': 0, 'critical': 0},
            'patterns_by_region': {}
        }
        
        for category, category_patterns in patterns.items():
            count = len(category_patterns)
            stats['patterns_by_category'][category] = count
            stats['total_patterns'] += count
            
            for pattern_config in category_patterns.values():
                severity = pattern_config.get('severity', 'medium')
                stats['patterns_by_severity'][severity] += 1
                
                region = pattern_config.get('region', 'global')
                stats['patterns_by_region'][region] = stats['patterns_by_region'].get(region, 0) + 1
        
        return stats


@dataclass
class SecurityFinding:
    """Represents a security issue found in code."""
    type: str
    location: str
    description: str
    risk_explanation: str
    remediation: str
    severity: str = "medium"
    confidence: float = 0.9


class SecurityFindingBuilder:
    """Helper class for creating SecurityFinding objects with consistent formatting."""
    
    @staticmethod
    def create_pattern_finding(
        config: Dict[str, str], 
        matches: List[str], 
        file_path: str = "", 
        line_number: int = 0,
        severity_override: Optional[str] = None
    ) -> SecurityFinding:
        """Create a SecurityFinding from pattern match results."""
        return SecurityFinding(
            type=config['description'],
            location=f"{file_path}:{line_number}" if file_path else "unknown",
            description=f"Found {len(matches)} {config['description'].lower()}{'s' if len(matches) > 1 else ''}",
            risk_explanation=config['risk'],
            remediation=config['fix'],
            severity=severity_override or config.get('severity', 'medium'),
            confidence=config.get('confidence', 0.80)
        )
    
    @staticmethod
    def create_ml_finding(
        type_desc: str,
        description: str,
        risk_explanation: str,
        remediation: str,
        severity: str,
        confidence: float,
        file_path: str = "",
        line_number: int = 0
    ) -> SecurityFinding:
        """Create a SecurityFinding from ML detection results."""
        return SecurityFinding(
            type=type_desc,
            location=f"{file_path}:{line_number}" if file_path else "unknown",
            description=description,
            risk_explanation=risk_explanation,
            remediation=remediation,
            severity=severity,
            confidence=confidence
        )
    
    @staticmethod
    def create_finding(
        type_desc: str,
        location: str,
        description: str,
        risk_explanation: str,
        remediation: str,
        severity: str = "medium",
        confidence: float = 0.9
    ) -> SecurityFinding:
        """Create a SecurityFinding with all parameters specified."""
        return SecurityFinding(
            type=type_desc,
            location=location,
            description=description,
            risk_explanation=risk_explanation,
            remediation=remediation,
            severity=severity,
            confidence=confidence
        )

@dataclass
class ContentSafetyResult:
    """Result of comprehensive content safety analysis."""
    safe_for_api: bool
    sanitized_content: Optional[str]
    customer_findings: List[SecurityFinding]
    risk_score: str  # LOW, MEDIUM, HIGH
    processing_time_ms: float
    raw_detections: Dict[str, Any] = field(default_factory=dict)


class PerformanceMetrics:
    """Track performance metrics for content safety detection engines."""
    
    def __init__(self):
        """Initialize performance tracking."""
        self.detector_times = defaultdict(list)
        self.detection_counts = defaultdict(int)
        self.fallback_activations = defaultdict(int)
        self.total_processed = 0
        self.session_start = time.time()
    
    def record_detection_time(self, detector: str, duration_ms: float):
        """Record processing time for a detector."""
        self.detector_times[detector].append(duration_ms)
        self.detection_counts[detector] += 1
        self.total_processed += 1
    
    def record_fallback_activation(self, detector: str):
        """Record when a detector falls back to regex patterns."""
        self.fallback_activations[detector] += 1
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics summary."""
        summary = {
            'total_processed': self.total_processed,
            'session_duration_minutes': round((time.time() - self.session_start) / 60, 2),
            'detector_performance': {},
            'fallback_rates': {},
            'overall_performance': {}
        }
        
        # Calculate per-detector metrics
        for detector, times in self.detector_times.items():
            if times:
                summary['detector_performance'][detector] = {
                    'avg_time_ms': round(statistics.mean(times), 2),
                    'median_time_ms': round(statistics.median(times), 2),
                    'max_time_ms': round(max(times), 2),
                    'min_time_ms': round(min(times), 2),
                    'total_calls': len(times)
                }
        
        # Calculate fallback rates
        for detector in self.detection_counts.keys():
            total_calls = self.detection_counts[detector]
            fallback_count = self.fallback_activations.get(detector, 0)
            if total_calls > 0:
                summary['fallback_rates'][detector] = {
                    'fallback_percentage': round((fallback_count / total_calls) * 100, 1),
                    'fallback_count': fallback_count,
                    'total_calls': total_calls
                }
        
        # Overall system performance
        all_times = []
        for times in self.detector_times.values():
            all_times.extend(times)
        
        if all_times:
            summary['overall_performance'] = {
                'avg_processing_time_ms': round(statistics.mean(all_times), 2),
                'processing_time_p95_ms': round(statistics.quantiles(all_times, n=20)[18], 2) if len(all_times) >= 20 else round(max(all_times), 2),
                'under_50ms_percentage': round((len([t for t in all_times if t < 50]) / len(all_times)) * 100, 1),
                'total_detection_calls': len(all_times)
            }
        
        return summary
    
    def is_performance_degraded(self) -> bool:
        """Check if performance has degraded below acceptable thresholds."""
        summary = self.get_performance_summary()
        
        # Check if overall performance is acceptable
        overall = summary.get('overall_performance', {})
        avg_time = overall.get('avg_processing_time_ms', 0)
        under_50ms_pct = overall.get('under_50ms_percentage', 100)
        
        # Performance degraded if:
        # - Average time > 100ms (2x target)
        # - Less than 80% of calls under 50ms target
        return avg_time > 100 or under_50ms_pct < 80
    
    def get_alerts(self) -> List[str]:
        """Get performance alerts for monitoring."""
        alerts = []
        
        if self.is_performance_degraded():
            alerts.append("PERFORMANCE_DEGRADED: Detection times exceed target thresholds")
        
        # Check high fallback rates
        for detector, rate_info in self.get_performance_summary()['fallback_rates'].items():
            if rate_info['fallback_percentage'] > 10:  # >10% fallback rate
                alerts.append(f"HIGH_FALLBACK_RATE: {detector} fallback rate {rate_info['fallback_percentage']}%")
        
        # Check for very slow detectors
        for detector, perf in self.get_performance_summary()['detector_performance'].items():
            if perf['avg_time_ms'] > 200:  # Individual detector taking >200ms
                alerts.append(f"SLOW_DETECTOR: {detector} averaging {perf['avg_time_ms']}ms")
        
        return alerts

class PIIDetector:
    """Professional PII detection using DataFog with international coverage."""
    
    def __init__(self, metrics: Optional[PerformanceMetrics] = None, pattern_loader: Optional[PatternLoader] = None):
        """Initialize DataFog with international custom entities."""
        self.metrics = metrics or PerformanceMetrics()
        self.pattern_loader = pattern_loader or PatternLoader()
        
        # Initialize instance-level entity mapping (moved from detect method)
        self.entity_mapping = {
            'SSN': {
                'description': 'Social Security Number',
                'risk': 'Personal identifier with high identity theft risk',
                'fix': 'Move to secure environment variables or replace with test data',
                'severity': 'high'
            },
            'CREDIT_CARD': {
                'description': 'Credit card number',
                'risk': 'Financial data exposure risk',  
                'fix': 'Replace with test card numbers or environment variables',
                'severity': 'high'
            },
            'EMAIL': {
                'description': 'Email address',
                'risk': 'Personal contact information exposure',
                'fix': 'Move to configuration files or environment variables',
                'severity': 'medium'
            },
            'PHONE': {
                'description': 'Phone number',
                'risk': 'Personal contact information',
                'fix': 'Replace with clearly fake numbers (555-0123) or move to config',
                'severity': 'medium'
            },
            'aadhaar': {
                'description': 'India Aadhaar Number',
                'risk': 'Highly sensitive Indian national identifier',
                'fix': 'Replace with clearly fake test data or secure storage',
                'severity': 'high'
            },
            'uk_nhs': {
                'description': 'UK NHS Number',
                'risk': 'UK healthcare identifier (GDPR sensitive)',
                'fix': 'Remove or replace with fake NHS numbers for testing',
                'severity': 'high'
            },
            'uk_nino': {
                'description': 'UK National Insurance Number',
                'risk': 'UK personal identifier (GDPR compliance required)',
                'fix': 'Use test NINO format or environment variables',
                'severity': 'high'
            },
            'sg_nric': {
                'description': 'Singapore NRIC/FIN',
                'risk': 'Singapore national identifier (PDPA compliance required)',
                'fix': 'Use test NRIC format or environment variables',
                'severity': 'high'
            },
            'au_tfn': {
                'description': 'Australian Tax File Number',
                'risk': 'Australian personal tax identifier',
                'fix': 'Use environment variables or test TFN ranges',
                'severity': 'high'
            },
            'iban': {
                'description': 'International Bank Account Number (IBAN)',
                'risk': 'International banking information',
                'fix': 'Use environment variables for financial account data',
                'severity': 'high'
            }
        }
        
        try:
            # Use Blood Oath compliant regex PII detector
            from .regex_pii_adapter import RegexPIIAdapter
            self.regex_pii = RegexPIIAdapter()
            self.datafog_available = True  # Keep variable name for compatibility
            logger.info("Blood Oath compliant regex PII detector initialized with international coverage")
            
        except ImportError as e:
            logger.warning(f"Regex PII detector not available: {e}, falling back to basic patterns")
            self.datafog_available = False
            self._init_fallback_patterns()
    
    def _init_fallback_patterns(self):
        """Load fallback patterns from external configuration."""
        # Load patterns from YAML configuration
        common_pii_patterns = self.pattern_loader.get_common_pii_patterns()
        international_pii_patterns = self.pattern_loader.get_international_pii_patterns()
        
        # Combine common and international PII patterns
        self.patterns = {}
        self.patterns.update(common_pii_patterns)
        self.patterns.update(international_pii_patterns)
        
        # Pre-compile regex patterns for better performance
        self.compiled_patterns = {}
        for name, config in self.patterns.items():
            try:
                self.compiled_patterns[name] = re.compile(config['pattern'], re.IGNORECASE)
            except re.error as e:
                logger.warning(f"Invalid regex pattern for {name}: {e}")
                # Keep the pattern as string if compilation fails
                self.compiled_patterns[name] = None
        
        logger.info(f"Loaded {len(self.patterns)} PII fallback patterns from external configuration")
    
    def detect(self, content: str, file_path: str = "", line_number: int = 0) -> List[SecurityFinding]:
        """Detect PII using Blood Oath compliant regex detector with international coverage."""
        findings = []
        start_time = time.time()
        
        if self.datafog_available:
            try:
                # Use regex PII detector (Blood Oath compliant)
                findings = self.regex_pii.detect(content, file_path, line_number)
                
                # Record successful detection
                duration_ms = (time.time() - start_time) * 1000
                self.metrics.record_detection_time('pii', duration_ms)
                
            except Exception as e:
                logger.error(f"Regex PII detection failed: {e}")
                # Record fallback activation and processing time
                duration_ms = (time.time() - start_time) * 1000
                self.metrics.record_fallback_activation('pii')
                self.metrics.record_detection_time('pii', duration_ms)
                # Fall back to basic patterns
                return self._detect_with_fallback(content, file_path, line_number)
        else:
            # Record fallback activation for unavailable DataFog
            self.metrics.record_fallback_activation('pii')
            # Use fallback patterns
            fallback_result = self._detect_with_fallback(content, file_path, line_number)
            # Record processing time
            duration_ms = (time.time() - start_time) * 1000
            self.metrics.record_detection_time('pii', duration_ms)
            return fallback_result
        
        # Record successful DataFog processing time
        duration_ms = (time.time() - start_time) * 1000
        self.metrics.record_detection_time('pii', duration_ms)
        
        return findings
    
    def _detect_with_fallback(self, content: str, file_path: str, line_number: int) -> List[SecurityFinding]:
        """Fallback detection using pre-compiled regex patterns."""
        findings = []
        
        for pii_type, config in self.patterns.items():
            # Use pre-compiled pattern if available, otherwise fall back to re.findall
            compiled_pattern = self.compiled_patterns.get(pii_type)
            if compiled_pattern:
                matches = compiled_pattern.findall(content)
            else:
                # Fallback if pattern compilation failed
                matches = re.findall(config['pattern'], content, re.IGNORECASE)
            
            if matches:
                finding = SecurityFindingBuilder.create_pattern_finding(
                    config, matches, file_path, line_number, severity_override="medium"
                )
                findings.append(finding)
                break  # One finding per pattern type per location
        
        return findings

class SecretDetector:
    """Detect embedded secrets and API keys (ChatGPT recommendation)."""
    
    def __init__(self, pattern_loader: Optional[PatternLoader] = None):
        """Initialize secret detection patterns."""
        self.pattern_loader = pattern_loader or PatternLoader()
        
        # Load patterns from external configuration
        self.patterns = self.pattern_loader.get_secret_patterns()
        
        # Pre-compile regex patterns for better performance
        self.compiled_patterns = {}
        for name, config in self.patterns.items():
            try:
                self.compiled_patterns[name] = re.compile(config['pattern'], re.IGNORECASE)
            except re.error as e:
                logger.warning(f"Invalid regex pattern for {name}: {e}")
                self.compiled_patterns[name] = None
        
        logger.info(f"Loaded {len(self.patterns)} secret detection patterns from external configuration")
    
    def detect(self, content: str, file_path: str = "", line_number: int = 0) -> List[SecurityFinding]:
        """Detect embedded secrets."""
        findings = []
        
        for secret_type, config in self.patterns.items():
            # Use pre-compiled pattern if available
            compiled_pattern = self.compiled_patterns.get(secret_type)
            if compiled_pattern:
                matches = compiled_pattern.findall(content)
            else:
                matches = re.findall(config['pattern'], content, re.IGNORECASE)
            
            if matches:
                finding = SecurityFindingBuilder.create_ml_finding(
                    type_desc=config['description'],
                    description=f"Found {len(matches)} hardcoded secret{'s' if len(matches) > 1 else ''}",
                    risk_explanation=config['risk'],
                    remediation=config['fix'],
                    severity="high",
                    confidence=0.95,
                    file_path=file_path,
                    line_number=line_number
                )
                findings.append(finding)
        
        return findings

class ObfuscationDetector:
    """Detect obfuscation attacks (ChatGPT recommendation)."""
    
    def __init__(self, pattern_loader: Optional[PatternLoader] = None):
        """Initialize obfuscation detection."""
        self.pattern_loader = pattern_loader or PatternLoader()
        self.leet_substitutions = {'@': 'a', '3': 'e', '1': 'i', '0': 'o', '5': 's', '7': 't'}
        
        # Load patterns from external configuration
        self.patterns = self.pattern_loader.get_obfuscation_patterns()
        
        # Extract specific patterns for backward compatibility
        base64_config = self.patterns.get('base64_encoded', {})
        self.base64_pattern = base64_config.get('pattern', r'(?:[A-Za-z0-9+/]{4}){4,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?')
        
        # Pre-compile patterns for better performance
        self.compiled_patterns = {}
        for name, config in self.patterns.items():
            try:
                self.compiled_patterns[name] = re.compile(config['pattern'], re.IGNORECASE)
            except re.error as e:
                logger.warning(f"Invalid obfuscation pattern for {name}: {e}")
                self.compiled_patterns[name] = None
        
        # Maintain backward compatibility
        self.compiled_base64_pattern = self.compiled_patterns.get('base64_encoded')
        
        logger.info(f"Loaded {len(self.patterns)} obfuscation detection patterns from external configuration")
    
    def detect(self, content: str, file_path: str = "", line_number: int = 0) -> List[SecurityFinding]:
        """Detect various obfuscation techniques."""
        findings = []
        
        # Base64 encoded payloads
        if self.compiled_base64_pattern:
            base64_matches = self.compiled_base64_pattern.findall(content)
        else:
            base64_matches = re.findall(self.base64_pattern, content)
        
        if base64_matches and any(len(match) > 20 for match in base64_matches):
            finding = SecurityFindingBuilder.create_ml_finding(
                type_desc="Base64 Encoded Content",
                description=f"Found {len(base64_matches)} potential Base64 encoded payload{'s' if len(base64_matches) > 1 else ''}",
                risk_explanation="Base64 encoding may hide sensitive data or malicious content",
                remediation="Review encoded content and ensure it doesn't contain sensitive information",
                severity="medium",
                confidence=0.70,
                file_path=file_path,
                line_number=line_number
            )
            findings.append(finding)
        
        # Unicode normalization for homoglyph detection
        try:
            normalized = unicodedata.normalize('NFKD', content)
            if normalized != content:
                finding = SecurityFindingBuilder.create_ml_finding(
                    type_desc="Unicode Obfuscation",
                    description="Unicode characters that may be used for obfuscation",
                    risk_explanation="Unicode homoglyphs can hide malicious content",
                    remediation="Review unicode characters for legitimate use",
                    severity="low",
                    confidence=0.60,
                    file_path=file_path,
                    line_number=line_number
                )
                findings.append(finding)
        except Exception:
            pass  # Unicode normalization failed, skip
        
        return findings

class ContentFilter:
    """Professional content filtering using alt-profanity-check with fallback patterns."""
    
    def __init__(self, metrics: Optional[PerformanceMetrics] = None, pattern_loader: Optional[PatternLoader] = None):
        """Initialize content filtering with alt-profanity-check."""
        self.metrics = metrics or PerformanceMetrics()
        self.pattern_loader = pattern_loader or PatternLoader()
        
        # Load profanity patterns from external configuration FIRST
        profanity_patterns = self.pattern_loader.get_profanity_patterns()
        
        # Extract critical patterns (always checked regardless of ML availability)
        self.critical_patterns = {}
        self.other_patterns = {}
        
        for name, config in profanity_patterns.items():
            if config.get('severity') == 'high':
                self.critical_patterns[name] = config
            else:
                self.other_patterns[name] = config
        
        # Use Blood Oath compliant regex profanity detector
        from .regex_profanity_detector import RegexProfanityAdapter
        self.profanity_adapter = RegexProfanityAdapter()
        self.predict_prob = self.profanity_adapter.predict_prob
        self.alt_profanity_available = True  # Keep variable name for compatibility
        logger.info("Blood Oath compliant regex profanity detector initialized")
        
        # Pre-compile critical patterns for performance
        self.compiled_critical_patterns = {}
        for name, config in self.critical_patterns.items():
            try:
                self.compiled_critical_patterns[name] = re.compile(config['pattern'], re.IGNORECASE)
            except re.error as e:
                logger.warning(f"Invalid critical pattern for {name}: {e}")
                self.compiled_critical_patterns[name] = None
        
        logger.info(f"Loaded {len(profanity_patterns)} profanity patterns from external configuration")
    
    def _init_fallback_patterns(self):
        """Load fallback patterns from external configuration if alt-profanity-check unavailable."""
        # Use non-critical patterns as fallback patterns
        self.fallback_patterns = self.other_patterns.copy()
        
        # Pre-compile fallback patterns for performance
        self.compiled_fallback_patterns = {}
        for name, config in self.fallback_patterns.items():
            try:
                self.compiled_fallback_patterns[name] = re.compile(config['pattern'], re.IGNORECASE)
            except re.error as e:
                logger.warning(f"Invalid fallback pattern for {name}: {e}")
                self.compiled_fallback_patterns[name] = None
    
    def detect(self, content: str, file_path: str = "", line_number: int = 0) -> List[SecurityFinding]:
        """Detect content issues using alt-profanity-check ML model."""
        findings = []
        start_time = time.time()
        
        # Always check critical hate speech patterns first
        for pattern_type, config in self.critical_patterns.items():
            compiled_pattern = self.compiled_critical_patterns.get(pattern_type)
            if compiled_pattern:
                matches = compiled_pattern.findall(content)
            else:
                matches = re.findall(config['pattern'], content, re.IGNORECASE)
            
            if matches:
                finding = SecurityFindingBuilder.create_ml_finding(
                    type_desc=config['description'],
                    description="Critical inappropriate content detected",
                    risk_explanation="Hate speech content violates professional standards and may create legal issues",
                    remediation=config['fix'],
                    severity=config['severity'],
                    confidence=0.98,
                    file_path=file_path,
                    line_number=line_number
                )
                findings.append(finding)
        
        # Use alt-profanity-check for sophisticated ML-based detection
        if self.alt_profanity_available:
            try:
                # Get profanity probability using ML model (95% accuracy)
                profanity_score = self.predict_prob([content])[0]
                
                # Map probability to severity levels
                if profanity_score > 0.7:
                    severity = "high"
                    description = "High probability profanity detected"
                    fix = "Remove or replace with professional language immediately"
                elif profanity_score > 0.4:
                    severity = "medium" 
                    description = "Moderate probability profanity detected"
                    fix = "Review and replace with professional language"
                elif profanity_score > 0.2:
                    severity = "low"
                    description = "Low probability unprofessional language detected"
                    fix = "Consider using more professional alternatives"
                else:
                    # Content is clean
                    return findings
                
                finding = SecurityFindingBuilder.create_ml_finding(
                    type_desc="ML-detected profanity/inappropriate content",
                    description=description,
                    risk_explanation="Unprofessional language may impact team collaboration and client relationships",
                    remediation=fix,
                    severity=severity,
                    confidence=round(profanity_score, 3),
                    file_path=file_path,
                    line_number=line_number
                )
                findings.append(finding)
                
            except Exception as e:
                logger.error(f"Regex profanity analysis failed: {e}")
                # Fall back to regex patterns
                return self._detect_with_fallback(content, file_path, line_number) + findings
        else:
            # Use fallback patterns
            fallback_findings = self._detect_with_fallback(content, file_path, line_number)
            findings.extend(fallback_findings)
        
        return findings
    
    def _detect_with_fallback(self, content: str, file_path: str, line_number: int) -> List[SecurityFinding]:
        """Fallback detection using regex patterns."""
        findings = []
        
        for pattern_type, config in self.fallback_patterns.items():
            compiled_pattern = self.compiled_fallback_patterns.get(pattern_type)
            if compiled_pattern:
                matches = compiled_pattern.findall(content)
            else:
                matches = re.findall(config['pattern'], content, re.IGNORECASE)
            
            if matches:
                finding = SecurityFindingBuilder.create_ml_finding(
                    type_desc=config['description'],
                    description=f"Found {config['description'].lower()}: {', '.join(matches[:3])}{'...' if len(matches) > 3 else ''}",
                    risk_explanation="Unprofessional language may impact team collaboration and client relationships",
                    remediation=config['fix'],
                    severity=config['severity'],
                    confidence=0.80,
                    file_path=file_path,
                    line_number=line_number
                )
                findings.append(finding)
                break  # One finding per content check
        
        return findings

class SafetyConfig:
    """Configuration validation and management for content safety system."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize and validate configuration."""
        self.api_safety_threshold = self._validate_threshold(
            config.get('api_safety_threshold', 0.8), 'api_safety_threshold'
        )
        self.high_risk_threshold = self._validate_positive_int(
            config.get('high_risk_threshold', 5), 'high_risk_threshold', 5
        )
        self.medium_risk_threshold = self._validate_positive_int(
            config.get('medium_risk_threshold', 2), 'medium_risk_threshold', 2
        )
        
        # Validate logical constraints
        self._validate_threshold_relationships()
        
        logger.info(f"Safety configuration validated: API threshold={self.api_safety_threshold}, "
                   f"High risk={self.high_risk_threshold}, Medium risk={self.medium_risk_threshold}")
    
    def _validate_threshold(self, value: Any, name: str) -> float:
        """Validate threshold values are between 0.0 and 1.0."""
        if not isinstance(value, (int, float)):
            logger.warning(f"Invalid {name}: {value} (not numeric), using default 0.8")
            return 0.8
        
        float_value = float(value)
        if float_value < 0.0 or float_value > 1.0:
            logger.warning(f"Invalid {name}: {value} (not between 0.0-1.0), using default 0.8")
            return 0.8
        
        return float_value
    
    def _validate_positive_int(self, value: Any, name: str, default: int) -> int:
        """Validate positive integer values."""
        if not isinstance(value, int):
            if isinstance(value, float) and value.is_integer():
                value = int(value)
            else:
                logger.warning(f"Invalid {name}: {value} (not integer), using default {default}")
                return default
        
        if value < 0:
            logger.warning(f"Invalid {name}: {value} (negative), using default {default}")
            return default
        
        return value
    
    def _validate_threshold_relationships(self):
        """Validate logical relationships between thresholds."""
        if self.medium_risk_threshold > self.high_risk_threshold:
            logger.warning(f"Medium risk threshold ({self.medium_risk_threshold}) > "
                          f"High risk threshold ({self.high_risk_threshold}), swapping values")
            self.medium_risk_threshold, self.high_risk_threshold = self.high_risk_threshold, self.medium_risk_threshold
        
        if self.medium_risk_threshold == self.high_risk_threshold and self.medium_risk_threshold > 0:
            logger.warning("Medium and high risk thresholds are equal, adjusting high threshold")
            self.high_risk_threshold = self.medium_risk_threshold + 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return {
            'api_safety_threshold': self.api_safety_threshold,
            'high_risk_threshold': self.high_risk_threshold,
            'medium_risk_threshold': self.medium_risk_threshold
        }


class DualPurposeContentSafety:
    """Unified content safety system serving dual purposes."""
    
    def __init__(self, config: Optional[Dict] = None, pattern_loader: Optional[PatternLoader] = None):
        """Initialize dual-purpose safety system."""
        raw_config = config or {}
        
        # Validate configuration
        self.config = SafetyConfig(raw_config)
        
        # Initialize shared pattern loader
        self.pattern_loader = pattern_loader or PatternLoader()
        
        # Initialize all detectors with shared pattern loader
        self.pii_detector = PIIDetector(pattern_loader=self.pattern_loader)
        self.secret_detector = SecretDetector(pattern_loader=self.pattern_loader)
        self.obfuscation_detector = ObfuscationDetector(pattern_loader=self.pattern_loader)
        self.content_filter = ContentFilter(pattern_loader=self.pattern_loader)
        
        # Use validated configuration values
        self.api_safety_threshold = self.config.api_safety_threshold
        self.high_risk_threshold = self.config.high_risk_threshold
        self.medium_risk_threshold = self.config.medium_risk_threshold
        
        logger.info("Dual-purpose content safety system initialized with external pattern configuration")
    
    def analyze_content_comprehensive(self, content: str, file_path: str = "", line_number: int = 0) -> ContentSafetyResult:
        """Comprehensive analysis serving both API protection and customer value."""
        start_time = datetime.now()
        
        # Run all detection methods
        all_findings = []
        
        # PII detection
        pii_findings = self.pii_detector.detect(content, file_path, line_number)
        all_findings.extend(pii_findings)
        
        # Secret detection  
        secret_findings = self.secret_detector.detect(content, file_path, line_number)
        all_findings.extend(secret_findings)
        
        # Obfuscation detection
        obfuscation_findings = self.obfuscation_detector.detect(content, file_path, line_number)
        all_findings.extend(obfuscation_findings)
        
        # Content filtering
        content_findings = self.content_filter.detect(content, file_path, line_number)
        all_findings.extend(content_findings)
        
        # Calculate risk score
        high_severity_count = len([f for f in all_findings if f.severity == "high"])
        total_findings = len(all_findings)
        
        if high_severity_count > 0 or total_findings >= self.high_risk_threshold:
            risk_score = "HIGH"
        elif total_findings >= self.medium_risk_threshold:
            risk_score = "MEDIUM"
        else:
            risk_score = "LOW"
        
        # Function 1: API Safety Assessment
        # Block API calls if high-risk content detected
        safe_for_api = (high_severity_count == 0 and 
                       total_findings < self.high_risk_threshold)
        
        # Generate sanitized content for API use
        sanitized_content = self._sanitize_content_for_api(content, all_findings) if not safe_for_api else content
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return ContentSafetyResult(
            safe_for_api=safe_for_api,
            sanitized_content=sanitized_content,
            customer_findings=all_findings,  # Function 2: Customer value
            risk_score=risk_score,
            processing_time_ms=processing_time,
            raw_detections={
                'pii_count': len(pii_findings),
                'secret_count': len(secret_findings),
                'obfuscation_count': len(obfuscation_findings),
                'content_issues_count': len(content_findings)
            }
        )
    
    def _sanitize_content_for_api(self, content: str, findings: List[SecurityFinding]) -> str:
        """Sanitize content for safe API transmission."""
        sanitized = content
        
        # Replace sensitive patterns with safe placeholders
        replacements = {
            # PII replacements
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b': 'user@example.com',
            r'\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}': '555-0123',
            r'(?:api[_-]?key|token)["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]{20,})["\']?': 'api_key="[REDACTED]"',
            r'password\s*[=:]\s*["\'][^"\']+["\']': 'password="[REDACTED]"',
            
            # Remove inappropriate content entirely
            r'\b(?:fuck|shit|bitch|ass|bastard)\b': '[REDACTED]',
            r'\b(?:nazi|kike|spic|chink|nigger|faggot)\b': '[REDACTED]',
        }
        
        for pattern, replacement in replacements.items():
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def generate_customer_security_report(self, all_findings: List[SecurityFinding]) -> Dict[str, Any]:
        """Generate comprehensive customer-facing security report."""
        if not all_findings:
            return {
                'summary': "No security concerns detected in your codebase.",
                'findings_count': 0,
                'risk_level': 'LOW',
                'recommendations': ['Your code follows good security practices.']
            }
        
        # Categorize findings
        high_priority = [f for f in all_findings if f.severity == "high"]
        medium_priority = [f for f in all_findings if f.severity == "medium"]
        low_priority = [f for f in all_findings if f.severity == "low"]
        
        # Generate risk assessment
        total_count = len(all_findings)
        high_count = len(high_priority)
        
        if high_count > 0 or total_count >= 5:
            risk_level = "HIGH"
            readiness = "NEEDS_IMMEDIATE_ATTENTION"
        elif total_count >= 2:
            risk_level = "MEDIUM"
            readiness = "NEEDS_CLEANUP"
        else:
            risk_level = "LOW"
            readiness = "READY"
        
        return {
            'summary': f"Found {total_count} security items requiring attention",
            'findings_count': total_count,
            'risk_level': risk_level,
            'enterprise_readiness': readiness,
            'high_priority_count': high_count,
            'findings_by_priority': {
                'high': high_priority,
                'medium': medium_priority,
                'low': low_priority
            },
            'recommendations': self._generate_recommendations(all_findings)
        }
    
    def _generate_recommendations(self, findings: List[SecurityFinding]) -> List[str]:
        """Generate actionable recommendations based on findings."""
        recommendations = []
        
        # Count finding types
        pii_count = len([f for f in findings if 'personal' in f.risk_explanation.lower() or 'identifier' in f.risk_explanation.lower()])
        secret_count = len([f for f in findings if 'api' in f.type.lower() or 'key' in f.type.lower() or 'password' in f.type.lower()])
        content_count = len([f for f in findings if 'profanity' in f.type.lower() or 'language' in f.type.lower()])
        
        if secret_count > 0:
            recommendations.append(f"Set up environment variables for {secret_count} detected API keys/secrets")
        
        if pii_count > 0:
            recommendations.append(f"Review {pii_count} instances of personal information for GDPR/CCPA compliance")
        
        if content_count > 0:
            recommendations.append(f"Clean up {content_count} instances of unprofessional language")
        
        # General recommendations
        if len(findings) > 3:
            recommendations.append("Consider implementing a pre-commit hook for security scanning")
            recommendations.append("Schedule a comprehensive security review with your team")
        
        recommendations.append("Review test data to ensure no real personal information is used")
        
        return recommendations
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and capabilities."""
        return {
            'detectors_active': {
                'pii_detection': True,
                'secret_detection': True,
                'obfuscation_detection': True,
                'content_filtering': True
            },
            'international_coverage': {
                'us_pii': True,
                'eu_gdpr': True,
                'uk_data_protection': True,
                'india_pdpb': True,
                'australia_privacy_act': True
            },
            'api_protection': True,
            'customer_reporting': True,
            'processing_time_target': '<10ms',
            'confidence_threshold': self.api_safety_threshold,
            'pattern_configuration': {
                'external_patterns_enabled': True,
                'pattern_file': self.pattern_loader.pattern_file,
                'yaml_available': YAML_AVAILABLE
            }
        }
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded patterns."""
        return self.pattern_loader.get_pattern_stats()
    
    def reload_patterns(self) -> None:
        """Reload patterns from external configuration and reinitialize detectors."""
        logger.info("Reloading patterns from external configuration")
        
        # Reload patterns
        self.pattern_loader.reload_patterns()
        
        # Reinitialize detectors with new patterns
        self.pii_detector = PIIDetector(pattern_loader=self.pattern_loader)
        self.secret_detector = SecretDetector(pattern_loader=self.pattern_loader)
        self.obfuscation_detector = ObfuscationDetector(pattern_loader=self.pattern_loader)
        self.content_filter = ContentFilter(pattern_loader=self.pattern_loader)
        
        logger.info("Content safety system reinitialized with updated patterns")