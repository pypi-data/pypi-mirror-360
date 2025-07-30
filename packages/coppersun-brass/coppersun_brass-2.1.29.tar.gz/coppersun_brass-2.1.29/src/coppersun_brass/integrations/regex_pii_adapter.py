"""
Regex PII Adapter - Integration bridge for SecurityFinding format

Converts RegexOnlyPIIDetector output to SecurityFinding format for
seamless integration with existing Copper Sun Brass infrastructure.
"""

from typing import List, Dict, Any
from .regex_pii_detector import RegexOnlyPIIDetector, PIIMatch
from .content_safety import SecurityFinding
import logging

logger = logging.getLogger(__name__)

class RegexPIIAdapter:
    """
    Adapter to convert regex PII detection results to SecurityFinding format.
    
    Maintains compatibility with existing DualPurposeContentSafety infrastructure
    while using Blood Oath compliant regex-only detection.
    """
    
    def __init__(self):
        """Initialize regex PII detector and entity mapping."""
        self.detector = RegexOnlyPIIDetector()
        
        # Entity mapping for detailed SecurityFinding output
        self.entity_mapping = {
            # Identification Documents
            'us_ssn': {
                'description': 'US Social Security Number',
                'risk': 'Personal identifier with high identity theft risk',
                'fix': 'Move to secure environment variables or replace with test data',
                'severity': 'high'
            },
            'uk_nhs': {
                'description': 'UK NHS Number',
                'risk': 'Healthcare identifier subject to UK data protection',
                'fix': 'Replace with test data or move to secure configuration',
                'severity': 'high'
            },
            'uk_nino': {
                'description': 'UK National Insurance Number',
                'risk': 'Government identifier requiring GDPR compliance',
                'fix': 'Use test NINO or environment variables',
                'severity': 'high'
            },
            'india_aadhaar': {
                'description': 'India Aadhaar Number',
                'risk': 'Biometric ID requiring explicit consent under PDPB',
                'fix': 'Replace with test Aadhaar or secure storage',
                'severity': 'high'
            },
            'india_pan': {
                'description': 'India PAN Number', 
                'risk': 'Tax identifier subject to data protection laws',
                'fix': 'Use test PAN format or environment variables',
                'severity': 'high'
            },
            'singapore_nric': {
                'description': 'Singapore NRIC/FIN',
                'risk': 'National identifier requiring PDPA compliance',
                'fix': 'Replace with test NRIC or secure configuration',
                'severity': 'high'
            },
            'australia_tfn': {
                'description': 'Australia Tax File Number',
                'risk': 'Protected tax identifier under Privacy Act 1988',
                'fix': 'Use test TFN or environment variables',
                'severity': 'high'
            },
            'australia_medicare': {
                'description': 'Australia Medicare Number',
                'risk': 'Healthcare identifier with privacy obligations',
                'fix': 'Replace with test Medicare number',
                'severity': 'high'
            },
            
            # Financial Information
            'credit_card_visa': {
                'description': 'Visa Credit Card Number',
                'risk': 'Financial data exposure risk, PCI DSS compliance required',
                'fix': 'Replace with test card numbers (4111111111111111)',
                'severity': 'high'
            },
            'credit_card_mastercard': {
                'description': 'MasterCard Credit Card Number',
                'risk': 'Financial data exposure risk, PCI DSS compliance required',
                'fix': 'Replace with test card numbers (5555555555554444)',
                'severity': 'high'
            },
            'credit_card_amex': {
                'description': 'American Express Credit Card Number',
                'risk': 'Financial data exposure risk, PCI DSS compliance required',
                'fix': 'Replace with test card numbers (378282246310005)',
                'severity': 'high'
            },
            'iban': {
                'description': 'International Bank Account Number',
                'risk': 'Banking information subject to financial data protection',
                'fix': 'Use test IBAN or environment variables',
                'severity': 'high'
            },
            'eu_vat': {
                'description': 'EU VAT Number',
                'risk': 'Business identifier requiring GDPR compliance',
                'fix': 'Replace with test VAT number or configuration',
                'severity': 'medium'
            },
            
            # Contact Information
            'email': {
                'description': 'Email Address',
                'risk': 'Personal contact information subject to privacy laws',
                'fix': 'Replace with example.com domains or environment variables',
                'severity': 'medium'
            },
            'us_phone': {
                'description': 'US Phone Number',
                'risk': 'Personal contact information with privacy implications',
                'fix': 'Use test numbers (555-xxx-xxxx) or configuration',
                'severity': 'medium'
            },
            'uk_phone': {
                'description': 'UK Phone Number',
                'risk': 'Personal contact information under GDPR protection',
                'fix': 'Replace with test UK numbers or environment variables',
                'severity': 'medium'
            },
            
            # Technical Identifiers
            'ipv4': {
                'description': 'IPv4 Address',
                'risk': 'Network identifier potentially revealing infrastructure',
                'fix': 'Use private IP ranges (192.168.x.x, 10.x.x.x)',
                'severity': 'low'
            },
            'api_key_generic': {
                'description': 'Generic API Key',
                'risk': 'Authentication credential exposure risk',
                'fix': 'Move to environment variables or secure secrets management',
                'severity': 'critical'
            },
            'aws_access_key': {
                'description': 'AWS Access Key',
                'risk': 'Cloud infrastructure access credential exposure',
                'fix': 'Rotate key immediately and use IAM roles or environment variables',
                'severity': 'critical'
            },
            'github_token': {
                'description': 'GitHub Personal Access Token',
                'risk': 'Source code repository access credential exposure',
                'fix': 'Revoke token and regenerate, use environment variables',
                'severity': 'critical'
            }
        }
    
    def detect(self, content: str, file_path: str = "", line_number: int = 0) -> List[SecurityFinding]:
        """
        Detect PII using regex patterns and convert to SecurityFinding format.
        
        Args:
            content: Text content to scan
            file_path: File path for location reference
            line_number: Starting line number
            
        Returns:
            List of SecurityFinding objects with detailed metadata
        """
        findings = []
        
        try:
            # Get PII matches from regex detector
            matches = self.detector.scan_text(content)
            
            # Convert to SecurityFinding format
            for match in matches:
                entity_info = self.entity_mapping.get(match.pattern_name, {
                    'description': f'Unknown PII type: {match.pattern_name}',
                    'risk': 'Potential sensitive data exposure',
                    'fix': 'Review and secure or remove sensitive content',
                    'severity': 'medium'
                })
                
                # Calculate line number for match position
                lines_before_match = content[:match.start_pos].count('\n')
                actual_line = line_number + lines_before_match
                
                finding = SecurityFinding(
                    type=entity_info['description'],
                    location=f"{file_path}:{actual_line}" if file_path else f"line:{actual_line}",
                    description=f"Detected {entity_info['description']}: {self._mask_sensitive_content(match.match_text)}",
                    risk_explanation=entity_info['risk'],
                    remediation=entity_info['fix'],
                    severity=entity_info['severity'],
                    confidence=match.confidence
                )
                findings.append(finding)
                
        except Exception as e:
            logger.error(f"Regex PII detection failed: {e}")
            # Return empty list on error - graceful degradation
            
        return findings
    
    def _mask_sensitive_content(self, content: str) -> str:
        """Mask sensitive content for safe logging/display."""
        if len(content) <= 4:
            return '*' * len(content)
        elif len(content) <= 8:
            return content[:2] + '*' * (len(content) - 4) + content[-2:]
        else:
            return content[:4] + '*' * (len(content) - 8) + content[-4:]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get detection performance statistics."""
        stats = self.detector.get_performance_stats()
        stats['detector_type'] = 'regex_only'
        stats['blood_oath_compliant'] = True
        stats['supported_categories'] = self.detector.get_supported_categories()
        stats['supported_regions'] = self.detector.get_supported_regions()
        return stats
    
    def get_supported_patterns(self) -> List[str]:
        """Get list of supported PII pattern names."""
        return list(self.entity_mapping.keys())