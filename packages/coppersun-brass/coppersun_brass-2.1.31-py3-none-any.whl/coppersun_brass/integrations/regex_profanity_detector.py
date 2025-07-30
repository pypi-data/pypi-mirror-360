"""
Blood Oath Compliant Profanity Detection System

Replaces alt-profanity-check with lightweight regex-based detection.
Maintains same interface (predict_prob) for drop-in compatibility.
Zero external dependencies, pure Python implementation.
"""

import re
from typing import List, Dict, Any, Tuple


class RegexProfanityDetector:
    """Blood Oath compliant profanity detector using regex patterns."""
    
    def __init__(self):
        """Initialize profanity detector with comprehensive pattern database."""
        self.patterns = self._build_pattern_database()
        self.compiled_patterns = self._compile_patterns()
    
    def _build_pattern_database(self) -> Dict[str, Dict[str, Any]]:
        """Build comprehensive profanity pattern database with confidence scoring."""
        return {
            # High confidence patterns (0.8-0.95) - Explicit profanity
            'explicit_high': {
                'patterns': [
                    r'\bf+u+c+k+\b', r'\bs+h+i+t+\b', r'\bb+i+t+c+h+\b',
                    r'\ba+s+s+h+o+l+e+\b', r'\bc+u+n+t+\b', r'\bb+a+s+t+a+r+d+\b',
                    r'\bd+a+m+n+\b', r'\bh+e+l+l+\b', r'\bc+r+a+p+\b',
                ],
                'confidence_base': 0.90,
                'severity': 'high'
            },
            
            # Medium confidence patterns (0.6-0.8) - Obfuscated/leetspeak
            'obfuscated_medium': {
                'patterns': [
                    r'\bf[\*@#$]*u[\*@#$]*c[\*@#$]*k\b',
                    r'\bs[\*@#$]*h[\*@#$]*i[\*@#$]*t\b',
                    r'\bb[\*@#$1]*tch\b', r'\bf\*{2,}\b',
                    r'\b[f]+[u]*[c]*[k]*\b', r'\b[s]+[h]*[i]*[t]*\b',
                    r'\bf+u+\*+k+\b', r'\bs+h+\*+t+\b',
                ],
                'confidence_base': 0.75,
                'severity': 'medium'
            },
            
            # Low confidence patterns (0.3-0.6) - Mild/contextual
            'mild_low': {
                'patterns': [
                    r'\bdumb\s*(ass|butt)\b', r'\bpiss\s*off\b',
                    r'\bshut\s*up\b', r'\bstupid\s*(ass|idiot)\b',
                    r'\bgo\s*to\s*hell\b', r'\bwhat\s*the\s*hell\b',
                ],
                'confidence_base': 0.45,
                'severity': 'low'
            },
            
            # Professional inappropriateness (0.2-0.4)
            'unprofessional_low': {
                'patterns': [
                    r'\bidiot\b', r'\bstupid\b', r'\bmoron\b',
                    r'\bdumbass\b', r'\bwhatever\b', r'\bshutup\b',
                ],
                'confidence_base': 0.30,
                'severity': 'low'
            }
        }
    
    def _compile_patterns(self) -> Dict[str, List[Tuple[re.Pattern, float, str]]]:
        """Compile regex patterns for efficient matching."""
        compiled = {}
        
        for category, config in self.patterns.items():
            compiled[category] = []
            for pattern in config['patterns']:
                compiled_pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                confidence = config['confidence_base']
                severity = config['severity']
                compiled[category].append((compiled_pattern, confidence, severity))
        
        return compiled
    
    def predict_prob(self, texts: List[str]) -> List[float]:
        """
        Predict profanity probability for texts.
        
        Compatible with alt-profanity-check interface:
        - Takes list of strings
        - Returns list of probability scores (0.0-1.0)
        """
        results = []
        
        for text in texts:
            if not text or not isinstance(text, str):
                results.append(0.0)
                continue
            
            max_confidence = 0.0
            
            # Check all pattern categories
            for category, patterns in self.compiled_patterns.items():
                for pattern, base_confidence, severity in patterns:
                    matches = pattern.findall(text)
                    
                    if matches:
                        # Calculate confidence based on matches and context
                        match_confidence = self._calculate_match_confidence(
                            matches, text, base_confidence
                        )
                        max_confidence = max(max_confidence, match_confidence)
            
            # Cap at 0.95 to maintain realistic ML-like scoring
            results.append(min(max_confidence, 0.95))
        
        return results
    
    def _calculate_match_confidence(self, matches: List[str], text: str, base_confidence: float) -> float:
        """Calculate confidence score based on match context."""
        # Base confidence from pattern type
        confidence = base_confidence
        
        # Boost confidence for multiple matches
        if len(matches) > 1:
            confidence = min(confidence * 1.2, 0.95)
        
        # Consider text length - shorter texts with profanity are more impactful
        words = len(text.split())
        if words <= 5 and matches:
            confidence = min(confidence * 1.1, 0.95)
        
        # Boost for ALL CAPS (indicates strong emotion)
        if any(match.isupper() for match in matches if len(match) > 2):
            confidence = min(confidence * 1.15, 0.95)
        
        # Reduce confidence for very long texts (profanity might be incidental)
        if words > 50:
            confidence *= 0.9
        
        return confidence
    
    def analyze_detailed(self, text: str) -> Dict[str, Any]:
        """
        Detailed analysis for debugging and validation.
        Returns breakdown of matches and confidence calculation.
        """
        analysis = {
            'text': text,
            'overall_score': self.predict_prob([text])[0],
            'matches': [],
            'categories_triggered': set()
        }
        
        for category, patterns in self.compiled_patterns.items():
            for pattern, base_confidence, severity in patterns:
                matches = pattern.findall(text)
                if matches:
                    analysis['matches'].extend(matches)
                    analysis['categories_triggered'].add(category)
        
        return analysis


class RegexProfanityAdapter:
    """Adapter to integrate regex profanity detector with existing content safety system."""
    
    def __init__(self):
        """Initialize adapter with regex detector."""
        self.detector = RegexProfanityDetector()
    
    def predict_prob(self, texts: List[str]) -> List[float]:
        """Direct passthrough to maintain alt-profanity-check compatibility."""
        return self.detector.predict_prob(texts)
    
    def is_available(self) -> bool:
        """Always available - no external dependencies."""
        return True
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Return performance statistics for monitoring."""
        return {
            'detector_type': 'regex_based',
            'pattern_categories': len(self.detector.patterns),
            'total_patterns': sum(len(cat['patterns']) for cat in self.detector.patterns.values()),
            'dependencies': 'none',
            'blood_oath_compliant': True
        }