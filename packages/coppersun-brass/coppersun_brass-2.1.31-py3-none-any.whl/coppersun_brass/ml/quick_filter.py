"""
Quick heuristic filter - Lightning-fast pre-filter to reduce ML load

This filter catches 80% of trivial/critical cases instantly using simple
rules, leaving only uncertain cases for ML classification.
"""
import re
from pathlib import Path
from typing import Dict, Any, List, NamedTuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class QuickResult:
    """Result from quick heuristic filtering."""
    label: str  # 'trivial', 'important', 'critical', 'unknown'
    confidence: float  # 0.0 to 1.0
    reason: str = ""  # Why this classification was made


class QuickHeuristicFilter:
    """Lightning-fast pre-filter using heuristics.
    
    Catches obvious cases without ML:
    - Test files → trivial
    - Auth/security files → critical
    - README/docs → trivial
    - Hardcoded secrets → critical
    """
    
    def __init__(self):
        """Initialize compiled patterns for speed."""
        # Compile regex patterns once for performance
        self.critical_patterns = [
            (re.compile(r'(password|secret|api_key|api_secret|private_key)\s*=\s*["\'][\w\d]+["\']', re.I), 
             "Hardcoded credential"),
            (re.compile(r'eval\s*\(', re.I), 
             "Eval usage - code injection risk"),
            (re.compile(r'exec\s*\(', re.I),
             "Exec usage - code injection risk"),
            (re.compile(r'os\.system\s*\(|subprocess\.\w+\(.*shell\s*=\s*True', re.I),
             "Shell command execution risk"),
            (re.compile(r'pickle\.loads?\s*\(', re.I),
             "Pickle deserialization risk"),
            (re.compile(r'TODO.*security|FIXME.*security|XXX.*security', re.I),
             "Security-related TODO"),
            (re.compile(r'# HACK|// HACK', re.I),
             "Acknowledged hack in code"),
        ]
        
        # Trivial file patterns
        self.trivial_indicators = {
            # Test files
            'test_', '_test.', '.spec.', '_spec.',
            'tests/', '/test/', 'testing/',
            
            # Build artifacts
            '__pycache__', '.pyc', '.pyo', 
            'node_modules/', 'dist/', 'build/',
            '.egg-info', '.pytest_cache',
            
            # Documentation
            'README', 'LICENSE', 'CHANGELOG',
            '.md', '.rst', '.txt',
            
            # Config files (usually)
            '.json', '.yaml', '.yml', '.toml',
            '.ini', '.cfg', '.conf',
            
            # IDE files
            '.idea/', '.vscode/', '.vs/',
            
            # Version control
            '.git/', '.gitignore', '.gitattributes'
        }
        
        # Important file patterns (need attention but not critical)
        self.important_patterns = {
            # Configuration with potential secrets
            'config', 'settings', 'env',
            
            # Database related
            'models', 'database', 'db', 'schema',
            
            # API endpoints
            'api', 'routes', 'views', 'controllers',
            
            # Core business logic
            'core', 'main', 'app', 'server',
            
            # Utilities (often have bugs)
            'utils', 'helpers', 'common'
        }
        
        # Critical file patterns
        self.critical_indicators = {
            # Security related
            'auth', 'authentication', 'authorization',
            'security', 'crypto', 'encryption',
            'password', 'secret', 'token', 'jwt',
            'permission', 'access', 'role',
            
            # Payment/money
            'payment', 'billing', 'checkout',
            'stripe', 'paypal', 'credit',
            
            # User data
            'user', 'profile', 'account',
            'personal', 'private'
        }
    
    def classify(self, observation: Dict[str, Any]) -> QuickResult:
        """Ultra-fast classification using heuristics.
        
        Args:
            observation: Observation dict with 'data' containing file info
            
        Returns:
            QuickResult with classification and confidence
        """
        try:
            data = observation.get('data', {})
            file_path = data.get('file', '')
            content = data.get('content', '')
            obs_type = observation.get('type', '')
            
            # Handle different observation types
            if obs_type == 'file_modified':
                return self._classify_file_change(file_path, data)
            elif obs_type == 'code_finding':
                return self._classify_code_finding(file_path, content, data)
            elif obs_type == 'todo':
                # TODOs need ML classification to check severity
                return QuickResult('unknown', 0.0, "TODO needs ML classification")
            else:
                # Default classification for unknown types
                return self._classify_by_path_and_content(file_path, content)
                
        except Exception as e:
            logger.error(f"Quick filter error: {e}")
            return QuickResult('unknown', 0.0, f"Error: {e}")
    
    def _classify_file_change(self, file_path: str, data: Dict) -> QuickResult:
        """Classify file modification events."""
        path_lower = file_path.lower()
        
        # Trivial changes
        if any(indicator in path_lower for indicator in self.trivial_indicators):
            return QuickResult('trivial', 0.95, "Test/build/doc file")
            
        # Critical changes
        if any(indicator in path_lower for indicator in self.critical_indicators):
            return QuickResult('critical', 0.85, "Security-sensitive file modified")
            
        # Check file size for large changes
        if 'lines_added' in data and data['lines_added'] > 500:
            return QuickResult('important', 0.7, "Large change - needs review")
            
        return QuickResult('unknown', 0.3, "Needs ML analysis")
    
    def _classify_code_finding(self, file_path: str, content: str, data: Dict) -> QuickResult:
        """Classify code findings (TODOs, issues, etc)."""
        path_lower = file_path.lower()
        description = data.get('description', '').lower()
        priority = data.get('priority', 50)
        
        # High priority findings are usually important
        if priority >= 80:
            return QuickResult('critical', 0.9, f"High priority: {priority}")
        elif priority <= 20:
            return QuickResult('trivial', 0.9, f"Low priority: {priority}")
            
        # Check finding type
        finding_type = data.get('finding_type', '').lower()
        if any(term in finding_type for term in ['security', 'vulnerability', 'injection']):
            return QuickResult('critical', 0.95, f"Security issue: {finding_type}")
        elif any(term in finding_type for term in ['todo', 'fixme', 'hack']):
            # Check content for critical keywords
            if any(term in description for term in ['security', 'auth', 'password', 'urgent']):
                return QuickResult('critical', 0.85, "Security-related TODO")
            else:
                return QuickResult('important', 0.6, "Standard TODO/FIXME")
                
        return QuickResult('unknown', 0.4, "Needs detailed analysis")
    
    def _classify_by_path_and_content(self, file_path: str, content: str) -> QuickResult:
        """Classify by file path and content analysis."""
        path_lower = file_path.lower()
        
        # Quick path-based classification
        if self._is_trivial_path(path_lower):
            return QuickResult('trivial', 0.95, "Non-code file")
            
        if self._is_critical_path(path_lower):
            # Check content for actual issues
            if content:
                result = self._check_critical_patterns(content)
                if result.label == 'critical':
                    return result
            return QuickResult('important', 0.7, "Security-related file")
            
        # Content analysis if available
        if content:
            # Check for critical patterns
            result = self._check_critical_patterns(content)
            if result.confidence > 0.8:
                return result
                
            # Check if it's just imports/comments
            if self._is_trivial_content(content):
                return QuickResult('trivial', 0.85, "Imports/comments only")
                
        # Check if it's likely important based on path
        if any(indicator in path_lower for indicator in self.important_patterns):
            return QuickResult('important', 0.6, "Core application file")
            
        # Default: uncertain, needs ML
        return QuickResult('unknown', 0.3, "Requires ML classification")
    
    def _is_trivial_path(self, path_lower: str) -> bool:
        """Check if path indicates trivial file."""
        return any(indicator in path_lower for indicator in self.trivial_indicators)
    
    def _is_critical_path(self, path_lower: str) -> bool:
        """Check if path indicates critical file."""
        return any(indicator in path_lower for indicator in self.critical_indicators)
    
    def _check_critical_patterns(self, content: str) -> QuickResult:
        """Check content for critical security patterns."""
        # Limit content size for performance
        content_sample = content[:5000] if len(content) > 5000 else content
        
        for pattern, reason in self.critical_patterns:
            if pattern.search(content_sample):
                return QuickResult('critical', 0.92, reason)
                
        return QuickResult('unknown', 0.4, "No critical patterns found")
    
    def _is_trivial_content(self, content: str) -> bool:
        """Check if content is trivial (just imports, comments, etc)."""
        lines = content.strip().split('\n')
        
        # Count meaningful lines
        meaningful_lines = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith(('#', '//', '/*', '*', 'import ', 'from ', 'using ', 'require(')):
                continue
            if line in ('{', '}', '[', ']', '(', ')'):
                continue
            meaningful_lines += 1
            
        # If less than 10% meaningful lines, it's probably trivial
        return meaningful_lines < max(1, len(lines) * 0.1)
    
    def get_stats(self) -> Dict[str, int]:
        """Get filter statistics (for monitoring)."""
        return {
            'critical_patterns': len(self.critical_patterns),
            'trivial_indicators': len(self.trivial_indicators),
            'important_patterns': len(self.important_patterns),
            'critical_indicators': len(self.critical_indicators)
        }