"""
Regex-Only PII Detector - Blood Oath Compliant Replacement for DataFog

This module provides comprehensive PII detection using pure regex patterns,
eliminating heavy ML dependencies while maintaining international coverage
and production-quality detection capabilities.
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class PIIMatch:
    """Represents a detected PII match."""
    pattern_name: str
    match_text: str
    start_pos: int
    end_pos: int
    confidence: float
    category: str
    region: str

class RegexOnlyPIIDetector:
    """
    Blood Oath compliant PII detector using only regex patterns.
    
    Provides international coverage for 6 PII categories across multiple regions
    while maintaining <5MB total dependency footprint.
    """
    
    def __init__(self, pattern_file: Optional[str] = None):
        """
        Initialize with regex patterns for international PII detection.
        
        Args:
            pattern_file: Optional path to custom pattern file. If None, uses built-in patterns.
        """
        self.patterns = self._load_patterns(pattern_file)
        self.compiled_patterns = self._compile_patterns()
        
        # Performance tracking
        self.detection_stats = {
            'total_scans': 0,
            'total_matches': 0,
            'avg_time_ms': 0.0
        }
    
    def _load_patterns(self, pattern_file: Optional[str]) -> Dict[str, Any]:
        """Load PII detection patterns from file or use built-in patterns."""
        if pattern_file and Path(pattern_file).exists():
            try:
                with open(pattern_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load pattern file {pattern_file}: {e}")
                
        # Built-in international PII patterns
        return {
            # Identification Documents
            "us_ssn": {
                "pattern": r"\b(?!000|666|9\d{2})\d{3}-?(?!00)\d{2}-?(?!0000)\d{4}\b",
                "confidence": 0.95,
                "category": "identification",
                "region": "US",
                "description": "US Social Security Number"
            },
            "uk_nhs": {
                "pattern": r"\b\d{3}[- ]?\d{3}[- ]?\d{4}\b",
                "confidence": 0.92,
                "category": "identification", 
                "region": "UK",
                "description": "UK NHS Number"
            },
            "uk_nino": {
                "pattern": r"\b[ABCEGHJ-PRSTW-Z][ABCEGHJ-NPRSTW-Z]\d{6}[A-D]\b",
                "confidence": 0.94,
                "category": "identification",
                "region": "UK", 
                "description": "UK National Insurance Number"
            },
            "india_aadhaar": {
                "pattern": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}\b",
                "confidence": 0.88,
                "category": "identification",
                "region": "IN",
                "description": "India Aadhaar Number"
            },
            "india_pan": {
                "pattern": r"\b[A-Z]{5}\d{4}[A-Z]\b",
                "confidence": 0.96,
                "category": "identification",
                "region": "IN",
                "description": "India PAN Number"
            },
            "singapore_nric": {
                "pattern": r"\b[STFG]\d{7}[A-Z]\b",
                "confidence": 0.98,
                "category": "identification",
                "region": "SG",
                "description": "Singapore NRIC/FIN"
            },
            "australia_tfn": {
                "pattern": r"\b\d{3}[- ]?\d{3}[- ]?\d{3}\b",
                "confidence": 0.85,
                "category": "identification",
                "region": "AU", 
                "description": "Australia Tax File Number"
            },
            "australia_medicare": {
                "pattern": r"\b\d{4}[- ]?\d{5}[- ]?\d\b",
                "confidence": 0.92,
                "category": "health",
                "region": "AU",
                "description": "Australia Medicare Number"
            },
            
            # Financial Information
            "credit_card_visa": {
                "pattern": r"\b4\d{3}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
                "confidence": 0.98,
                "category": "financial",
                "region": "Global",
                "description": "Visa Credit Card"
            },
            "credit_card_mastercard": {
                "pattern": r"\b5[1-5]\d{2}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
                "confidence": 0.98,
                "category": "financial", 
                "region": "Global",
                "description": "MasterCard Credit Card"
            },
            "credit_card_amex": {
                "pattern": r"\b3[47]\d{2}[- ]?\d{6}[- ]?\d{5}\b",
                "confidence": 0.98,
                "category": "financial",
                "region": "Global", 
                "description": "American Express Credit Card"
            },
            "iban": {
                "pattern": r"\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b",
                "confidence": 0.95,
                "category": "financial",
                "region": "EU",
                "description": "International Bank Account Number"
            },
            "eu_vat": {
                "pattern": r"\b[A-Z]{2}\d{8,12}\b",
                "confidence": 0.90,
                "category": "financial",
                "region": "EU",
                "description": "EU VAT Number"
            },
            
            # Contact Information
            "email": {
                "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                "confidence": 0.95,
                "category": "contact",
                "region": "Global",
                "description": "Email Address"
            },
            "us_phone": {
                "pattern": r"\b(\+1[- ]?)?\(?([0-9]{3})\)?[- ]?([0-9]{3})[- ]?([0-9]{4})\b",
                "confidence": 0.90,
                "category": "contact",
                "region": "US",
                "description": "US Phone Number"
            },
            "uk_phone": {
                "pattern": r"\b(\+44[- ]?)?0?[1-9]\d{8,9}\b",
                "confidence": 0.88,
                "category": "contact",
                "region": "UK", 
                "description": "UK Phone Number"
            },
            
            # Technical Identifiers
            "ipv4": {
                "pattern": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
                "confidence": 0.90,
                "category": "technical",
                "region": "Global",
                "description": "IPv4 Address"
            },
            "api_key_generic": {
                "pattern": r"\b[A-Za-z0-9]{20,}\b",
                "confidence": 0.70,
                "category": "technical",
                "region": "Global",
                "description": "Generic API Key"
            },
            "aws_access_key": {
                "pattern": r"\bAKIA[0-9A-Z]{16}\b",
                "confidence": 0.98,
                "category": "technical",
                "region": "Global",
                "description": "AWS Access Key"
            },
            "github_token": {
                "pattern": r"\bghp_[A-Za-z0-9]{36}\b",
                "confidence": 0.98,
                "category": "technical",
                "region": "Global",
                "description": "GitHub Personal Access Token"
            }
        }
    
    def _compile_patterns(self) -> Dict[str, Tuple[re.Pattern, Dict[str, Any]]]:
        """Compile regex patterns for performance."""
        compiled = {}
        for name, config in self.patterns.items():
            try:
                pattern = re.compile(config["pattern"], re.IGNORECASE)
                compiled[name] = (pattern, config)
            except re.error as e:
                logger.warning(f"Failed to compile pattern {name}: {e}")
        return compiled
    
    def scan_text(self, content: str) -> List[PIIMatch]:
        """
        Scan text content for PII patterns.
        
        Args:
            content: Text content to scan
            
        Returns:
            List of PIIMatch objects for detected PII
        """
        import time
        start_time = time.time()
        
        matches = []
        for name, (pattern, config) in self.compiled_patterns.items():
            for match in pattern.finditer(content):
                pii_match = PIIMatch(
                    pattern_name=name,
                    match_text=match.group(),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=config["confidence"],
                    category=config["category"],
                    region=config["region"]
                )
                matches.append(pii_match)
        
        # Update performance stats
        elapsed_ms = (time.time() - start_time) * 1000
        self.detection_stats['total_scans'] += 1
        self.detection_stats['total_matches'] += len(matches)
        self.detection_stats['avg_time_ms'] = (
            self.detection_stats['avg_time_ms'] * (self.detection_stats['total_scans'] - 1) + elapsed_ms
        ) / self.detection_stats['total_scans']
        
        return matches
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get detection performance statistics."""
        return self.detection_stats.copy()
    
    def get_supported_categories(self) -> List[str]:
        """Get list of supported PII categories."""
        categories = set()
        for config in self.patterns.values():
            categories.add(config["category"])
        return sorted(list(categories))
    
    def get_supported_regions(self) -> List[str]:
        """Get list of supported regions."""
        regions = set()
        for config in self.patterns.values():
            regions.add(config["region"])
        return sorted(list(regions))