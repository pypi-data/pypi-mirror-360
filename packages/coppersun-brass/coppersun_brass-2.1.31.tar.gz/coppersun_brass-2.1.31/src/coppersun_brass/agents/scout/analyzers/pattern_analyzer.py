"""Pattern recognition engine for detecting code patterns and anti-patterns.

General Staff Role: G2 Intelligence - Pattern Recognition Specialist
Detects security vulnerabilities, code smells, and anti-patterns across
multiple languages using configurable pattern matching.

Persistent Value: Creates detailed pattern observations that help AI
identify security risks, technical debt, and refactoring opportunities.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import logging

from .base_analyzer import BaseAnalyzer, AnalysisResult, CodeEntity, CodeIssue, CodeMetrics

logger = logging.getLogger(__name__)


@dataclass
class PatternDefinition:
    """Definition of a code pattern to detect.
    
    Structured for AI understanding with clear severity and remediation guidance.
    """
    
    pattern_id: str
    pattern_type: str  # 'security', 'code_smell', 'anti_pattern', 'vulnerability'
    name: str
    description: str
    regex_patterns: List[str]  # List of regex patterns to match
    severity: str  # 'low', 'medium', 'high', 'critical'
    languages: List[str]  # Languages this pattern applies to
    ai_recommendation: str
    fix_complexity: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def compile_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns for efficient matching.
        
        Raises:
            ValueError: If a critical security pattern fails to compile
        """
        compiled = []
        for pattern in self.regex_patterns:
            try:
                compiled.append(re.compile(pattern, re.MULTILINE | re.IGNORECASE))
            except re.error as e:
                error_msg = f"Failed to compile pattern {pattern}: {e}"
                logger.error(error_msg)
                
                # Critical security patterns must compile successfully
                if self.pattern_type == "security" and self.severity in ["critical", "high"]:
                    raise ValueError(f"Critical security pattern {self.pattern_id} failed to compile: {e}")
                else:
                    logger.warning(f"Non-critical pattern {self.pattern_id} skipped due to regex error")
                    
        if not compiled and self.pattern_type == "security":
            raise ValueError(f"No patterns compiled for security pattern {self.pattern_id}")
            
        return compiled


class PatternAnalyzer(BaseAnalyzer):
    """Pattern recognition analyzer for security and code quality issues.
    
    This analyzer provides intelligence about code patterns, security
    vulnerabilities, and anti-patterns to support AI decision-making.
    """
    
    # Core security patterns that must be detected
    SECURITY_PATTERNS = [
        PatternDefinition(
            pattern_id="SEC001",
            pattern_type="security",
            name="Hardcoded Credentials",
            description="Potential hardcoded passwords, API keys, or secrets",
            regex_patterns=[
                r'(?i)(password|passwd|pwd|pass)\s*=\s*["\'][^"\']{4,}["\']',
                r'(?i)(api[_-]?key|apikey)\s*=\s*["\'][A-Za-z0-9+/=-]{10,}["\']',
                r'(?i)\w*(secret|token)\w*\s*=\s*["\'][A-Za-z0-9+/=-]{16,}["\']',
                r'(?i)aws[_-]?(access[_-]?key[_-]?id|secret[_-]?access[_-]?key)\s*=\s*["\'][^"\']+["\']',
                r'(?i)(private[_-]?key|priv[_-]?key)\s*=\s*["\'][^"\']+["\']'
            ],
            severity="critical",
            languages=["python", "javascript", "typescript", "java", "go"],
            ai_recommendation="Remove hardcoded credentials immediately. Use environment variables or secure credential management systems.",
            fix_complexity="simple",
            metadata={"cwe": "CWE-798", "owasp": "A3"}
        ),
        
        PatternDefinition(
            pattern_id="SEC002",
            pattern_type="security",
            name="SQL Injection Risk",
            description="String concatenation in SQL queries",
            regex_patterns=[
                r'(?i)(execute|query|cursor\.execute)\s*\(\s*["\'].*\+.*["\']',
                r'(?i)(execute|query)\s*\(\s*f["\'].*{.*}.*["\']',
                r'(?i)sql\s*=\s*["\'].*\+\s*\w+',
                r'(?i)query\s*=\s*["\'].*%s.*["\'].*%\s*\(',
                r'(?i)(SELECT|INSERT|UPDATE|DELETE).*\+\s*\w+[^;]*["\']'
            ],
            severity="high",
            languages=["python", "javascript", "java", "php"],
            ai_recommendation="Use parameterized queries or prepared statements to prevent SQL injection.",
            fix_complexity="moderate",
            metadata={"cwe": "CWE-89", "owasp": "A1"}
        ),
        
        PatternDefinition(
            pattern_id="SEC003",
            pattern_type="security",
            name="Insecure Random",
            description="Using weak random number generation for security",
            regex_patterns=[
                r'(?i)random\.(random|randint|choice)\s*\(',
                r'(?i)math\.random\s*\(',
                r'(?i)rand\s*\(\s*\)',
                r'(?i)mt_rand\s*\('
            ],
            severity="medium",
            languages=["python", "javascript", "php", "java"],
            ai_recommendation="Use cryptographically secure random number generators for security-sensitive operations.",
            fix_complexity="simple",
            metadata={"cwe": "CWE-330"}
        ),
        
        PatternDefinition(
            pattern_id="SEC004",
            pattern_type="security",
            name="Command Injection Risk",
            description="Potential command injection through shell execution",
            regex_patterns=[
                r'(?i)os\.system\s*\([^)]*\+[^)]*\)',
                r'(?i)subprocess\.(call|run|Popen)\s*\([^,)]*\+[^,)]*,?\s*shell\s*=\s*True',
                r'(?i)exec\s*\([^)]*\+[^)]*\)',
                r'(?i)eval\s*\([^)]*\+[^)]*\)'
            ],
            severity="critical",
            languages=["python", "javascript", "ruby"],
            ai_recommendation="Avoid shell=True and use subprocess with list arguments. Validate and sanitize all user input.",
            fix_complexity="moderate",
            metadata={"cwe": "CWE-78", "owasp": "A1"}
        )
    ]
    
    # Code smell patterns
    CODE_SMELL_PATTERNS = [
        PatternDefinition(
            pattern_id="CS001",
            pattern_type="code_smell",
            name="Magic Numbers",
            description="Hardcoded numeric literals without explanation",
            regex_patterns=[
                r'(?<!["\'])\b(?!0|1|2|10|100|1000|1024|60|24|365|404|200|500)\d{3,}\b(?!["\'])',
                r'(?i)if\s+.*[><=]\s*(?!0|1|2|-1)\d{2,}',
                r'(?i)for\s+.*range\s*\(\s*(?!0|1|2)\d{2,}\s*\)'
            ],
            severity="low",
            languages=["python", "javascript", "java", "c++"],
            ai_recommendation="Extract magic numbers to named constants with descriptive names.",
            fix_complexity="trivial",
            metadata={"refactoring": "extract_constant"}
        ),
        
        PatternDefinition(
            pattern_id="CS002",
            pattern_type="code_smell",
            name="Long Parameter List",
            description="Functions with too many parameters",
            regex_patterns=[
                r'(?i)def\s+\w+\s*\([^)]{100,}\)',
                r'(?i)function\s+\w+\s*\([^)]{100,}\)',
                r'(?i)(?:public|private|protected)?\s*\w+\s+\w+\s*\([^)]{100,}\)'
            ],
            severity="medium",
            languages=["python", "javascript", "java"],
            ai_recommendation="Consider using parameter objects or configuration classes to group related parameters.",
            fix_complexity="moderate",
            metadata={"refactoring": "introduce_parameter_object"}
        ),
        
        PatternDefinition(
            pattern_id="CS003",
            pattern_type="code_smell",
            name="Deeply Nested Code",
            description="Code with excessive nesting levels",
            regex_patterns=[
                r'(?:\n\s{16,}|\t{4,})(?:if|for|while|try)\s',
                r'(?:\n\s{20,}|\t{5,})\w+',
                r'(?:(?:\s{4}|\t).*\n){5,}.*(?:if|for|while)'
            ],
            severity="medium",
            languages=["python", "javascript", "java"],
            ai_recommendation="Extract nested logic into separate functions or use early returns to reduce nesting.",
            fix_complexity="moderate",
            metadata={"refactoring": "extract_method"}
        ),
        
        PatternDefinition(
            pattern_id="CS004",
            pattern_type="code_smell",
            name="TODO/FIXME Comments",
            description="Unresolved TODO or FIXME comments",
            regex_patterns=[
                r'(?i)#\s*(TODO|FIXME|HACK|XXX|BUG)\s*:?.*',
                r'(?i)//\s*(TODO|FIXME|HACK|XXX|BUG)\s*:?.*',
                r'(?i)/\*\s*(TODO|FIXME|HACK|XXX|BUG)\s*:?.*\*/'
            ],
            severity="low",
            languages=["python", "javascript", "java", "c++"],
            ai_recommendation="Address TODO items or convert them to tracked issues in the project management system.",
            fix_complexity="varies",
            metadata={"technical_debt": True}
        )
    ]
    
    # Error handling patterns
    ERROR_HANDLING_PATTERNS = [
        PatternDefinition(
            pattern_id="EH001",
            pattern_type="anti_pattern",
            name="Empty Exception Handler",
            description="Catch blocks that suppress exceptions",
            regex_patterns=[
                r'(?i)except\s*(?:\w+)?:\s*\n\s*pass',
                r'(?i)catch\s*\([^)]*\)\s*{\s*}',
                r'(?i)catch\s*\([^)]*\)\s*{\s*(?://.*)?}',
                r'(?i)except\s*(?:\w+)?:\s*\n\s*(?:pass|\.\.\.)'
            ],
            severity="high",
            languages=["python", "javascript", "java"],
            ai_recommendation="Log exceptions or handle them appropriately. Never silently suppress errors.",
            fix_complexity="simple",
            metadata={"cwe": "CWE-391"}
        ),
        
        PatternDefinition(
            pattern_id="EH002",
            pattern_type="anti_pattern",
            name="Broad Exception Catch",
            description="Catching overly broad exception types",
            regex_patterns=[
                r'(?i)except\s*(?:Exception|BaseException)\s*:',
                r'(?i)except\s*:\s*\n',
                r'(?i)catch\s*\(\s*(?:Exception|Throwable|Error)\s+\w+\s*\)'
            ],
            severity="medium",
            languages=["python", "java"],
            ai_recommendation="Catch specific exception types to handle different error conditions appropriately.",
            fix_complexity="simple",
            metadata={"best_practice": "specific_exceptions"}
        )
    ]
    
    # Resource management patterns
    RESOURCE_PATTERNS = [
        PatternDefinition(
            pattern_id="RES001",
            pattern_type="anti_pattern",
            name="Unclosed File Handle",
            description="File operations without proper closure",
            regex_patterns=[
                r'(?i)open\s*\([^)]+\)(?!\s*\.\s*__enter__|\.close\(\)|with)',
                r'(?i)(\w+)\s*=\s*open\s*\([^)]+\)(?!.*\1\.close\(\))',
                r'(?i)new\s+FileInputStream\s*\([^)]+\)(?!.*\.close\(\))'
            ],
            severity="medium",
            languages=["python", "java"],
            ai_recommendation="Use context managers (with statement) or try-finally blocks to ensure resources are closed.",
            fix_complexity="simple",
            metadata={"cwe": "CWE-404"}
        ),
        
        PatternDefinition(
            pattern_id="RES002",
            pattern_type="anti_pattern",
            name="Unclosed Database Connection",
            description="Database connections not properly closed",
            regex_patterns=[
                r'(?i)(?:connect|connection)\s*\([^)]+\)(?!.*\.close\(\)|with)',
                r'(?i)create_engine\s*\([^)]+\)(?!.*\.dispose\(\))',
                r'(?i)getConnection\s*\([^)]*\)(?!.*\.close\(\))'
            ],
            severity="high",
            languages=["python", "java", "javascript"],
            ai_recommendation="Use connection pools or ensure connections are closed in finally blocks.",
            fix_complexity="moderate",
            metadata={"performance_impact": "high"}
        )
    ]
    
    # Code duplication patterns
    DUPLICATION_PATTERNS = [
        PatternDefinition(
            pattern_id="DUP001",
            pattern_type="code_smell",
            name="Duplicated String Literals",
            description="Same string literal repeated multiple times",
            regex_patterns=[
                r'(["\'][^"\']{10,}["\'])(?=.*\1.*\1)',  # String appears 3+ times
            ],
            severity="low",
            languages=["python", "javascript", "java"],
            ai_recommendation="Extract repeated string literals to constants.",
            fix_complexity="trivial",
            metadata={"refactoring": "extract_constant"}
        )
    ]
    
    def __init__(self, dcp_path: Optional[str] = None, custom_patterns: Optional[List[PatternDefinition]] = None):
        """Initialize pattern analyzer with DCP integration.
        
        Args:
            dcp_path: Path to DCP file for coordination
            custom_patterns: Additional patterns to detect
        """
        super().__init__(dcp_path)
        self._supported_languages = {'python', 'javascript', 'typescript', 'java', 'go', 'php', 'ruby', 'c++'}
        
        # Combine all patterns
        self.patterns: List[PatternDefinition] = []
        self.patterns.extend(self.SECURITY_PATTERNS)
        self.patterns.extend(self.CODE_SMELL_PATTERNS)
        self.patterns.extend(self.ERROR_HANDLING_PATTERNS)
        self.patterns.extend(self.RESOURCE_PATTERNS)
        self.patterns.extend(self.DUPLICATION_PATTERNS)
        
        if custom_patterns:
            self.patterns.extend(custom_patterns)
            
        # Compile all patterns for efficiency
        self.compiled_patterns: Dict[str, List[Tuple[PatternDefinition, re.Pattern]]] = {}
        self._compile_all_patterns()
        
    def _compile_all_patterns(self):
        """Pre-compile all regex patterns grouped by language.
        
        Raises:
            ValueError: If critical security patterns fail to compile
        """
        failed_critical = []
        
        for pattern_def in self.patterns:
            try:
                compiled = pattern_def.compile_patterns()
                for lang in pattern_def.languages:
                    if lang not in self.compiled_patterns:
                        self.compiled_patterns[lang] = []
                    for regex in compiled:
                        self.compiled_patterns[lang].append((pattern_def, regex))
            except ValueError as e:
                # Critical pattern compilation failure
                failed_critical.append(str(e))
                logger.error(f"Critical pattern compilation failure: {e}")
        
        if failed_critical:
            raise ValueError(f"Failed to compile {len(failed_critical)} critical patterns: {'; '.join(failed_critical)}")
                    
    def supports_language(self, language: str) -> bool:
        """Check if analyzer supports given language."""
        return language.lower() in self._supported_languages
        
    def analyze(self, file_path: Path) -> AnalysisResult:
        """Analyze file for patterns and anti-patterns.
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            AnalysisResult with pattern intelligence
        """
        language = self.extract_language(file_path)
        if not language or not self.supports_language(language):
            return self._create_unsupported_result(file_path, language)
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find all pattern matches
            issues = self._find_patterns(content, file_path, language)
            
            # Calculate metrics based on patterns found
            metrics = self._calculate_pattern_metrics(content, issues)
            
            # Create result for AI consumption
            return AnalysisResult(
                file_path=str(file_path),
                language=language,
                analysis_timestamp=datetime.now(),
                entities=[],  # Pattern analyzer doesn't extract entities
                issues=issues,
                metrics=metrics,
                analysis_metadata={
                    'analyzer': 'PatternAnalyzer',
                    'version': '1.0',
                    'patterns_checked': len(self.compiled_patterns.get(language, [])),
                    'pattern_types': list(set(p.pattern_type for p in self.patterns))
                }
            )
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return self._create_error_result(file_path, str(e))
            
    def _find_patterns(self, content: str, file_path: Path, language: str) -> List[CodeIssue]:
        """Find all pattern matches in content.
        
        Args:
            content: File content to analyze
            file_path: Path to file
            language: Programming language
            
        Returns:
            List of code issues found
        """
        issues = []
        lines = content.split('\n')
        
        # Get patterns for this language
        language_patterns = self.compiled_patterns.get(language, [])
        
        for pattern_def, regex in language_patterns:
            try:
                # Find all matches
                for match in regex.finditer(content):
                    # Calculate line number
                    line_number = content[:match.start()].count('\n') + 1
                    
                    # Extract context
                    matched_text = match.group(0)
                    if len(matched_text) > 100:
                        matched_text = matched_text[:97] + "..."
                        
                    # Create issue for AI understanding
                    issue = CodeIssue(
                        issue_type=pattern_def.pattern_id,
                        severity=pattern_def.severity,
                        file_path=str(file_path),
                        line_number=line_number,
                        entity_name=f"line_{line_number}",
                        description=f"{pattern_def.description}: {matched_text}",
                        ai_recommendation=pattern_def.ai_recommendation,
                        fix_complexity=pattern_def.fix_complexity,
                        metadata={
                            'pattern_type': pattern_def.pattern_type,
                            'pattern_name': pattern_def.name,
                            'matched_text': matched_text,
                            **pattern_def.metadata
                        }
                    )
                    issues.append(issue)
                    
            except Exception as e:
                logger.warning(f"Error checking pattern {pattern_def.pattern_id}: {e}")
                
        # Deduplicate issues on same line
        unique_issues = {}
        for issue in issues:
            key = (issue.line_number, issue.issue_type)
            if key not in unique_issues or issue.severity > unique_issues[key].severity:
                unique_issues[key] = issue
                
        return list(unique_issues.values())
        
    def _calculate_pattern_metrics(self, content: str, issues: List[CodeIssue]) -> CodeMetrics:
        """Calculate metrics based on patterns found.
        
        Args:
            content: File content
            issues: Issues found
            
        Returns:
            CodeMetrics for AI assessment
        """
        lines = content.split('\n')
        
        # Count issues by severity
        issues_by_severity = {
            'low': 0,
            'medium': 0,
            'high': 0,
            'critical': 0
        }
        for issue in issues:
            issues_by_severity[issue.severity] = issues_by_severity.get(issue.severity, 0) + 1
            
        # Count by pattern type
        pattern_types = {}
        for issue in issues:
            ptype = issue.metadata.get('pattern_type', 'unknown')
            pattern_types[ptype] = pattern_types.get(ptype, 0) + 1
            
        # Calculate security score (0-100, lower is better)
        security_score = (
            issues_by_severity.get('critical', 0) * 25 +
            issues_by_severity.get('high', 0) * 10 +
            issues_by_severity.get('medium', 0) * 5 +
            issues_by_severity.get('low', 0) * 1
        )
        security_score = min(100, security_score)
        
        return CodeMetrics(
            total_lines=len(lines),
            code_lines=len([l for l in lines if l.strip() and not l.strip().startswith(('#', '//', '/*'))]),
            issues_by_severity=issues_by_severity,
            language_specific_metrics={
                'pattern_matches': len(issues),
                'security_score': security_score,
                'pattern_types': pattern_types,
                'has_security_issues': pattern_types.get('security', 0) > 0,
                'has_resource_leaks': pattern_types.get('anti_pattern', 0) > 0,
                'technical_debt_indicators': sum(1 for i in issues if i.metadata.get('technical_debt'))
            }
        )
        
    def _create_unsupported_result(self, file_path: Path, language: Optional[str]) -> AnalysisResult:
        """Create result for unsupported languages."""
        return AnalysisResult(
            file_path=str(file_path),
            language=language or 'unknown',
            analysis_timestamp=datetime.now(),
            entities=[],
            issues=[],
            metrics=CodeMetrics(),
            analysis_metadata={
                'analyzer': 'PatternAnalyzer',
                'version': '1.0',
                'supported': False,
                'reason': f"Language '{language}' not supported for pattern analysis"
            }
        )
        
    def _create_error_result(self, file_path: Path, error_message: str) -> AnalysisResult:
        """Create result for files that couldn't be analyzed."""
        return AnalysisResult(
            file_path=str(file_path),
            language='unknown',
            analysis_timestamp=datetime.now(),
            entities=[],
            issues=[
                CodeIssue(
                    issue_type='analysis_error',
                    severity='medium',
                    file_path=str(file_path),
                    line_number=1,
                    entity_name='file',
                    description=f"Pattern analysis failed: {error_message}",
                    ai_recommendation="Investigate the analysis error before proceeding",
                    fix_complexity='varies'
                )
            ],
            metrics=CodeMetrics(),
            analysis_metadata={
                'analyzer': 'PatternAnalyzer',
                'version': '1.0',
                'error': error_message
            }
        )
        
    def add_custom_pattern(self, pattern: PatternDefinition):
        """Add a custom pattern at runtime.
        
        Args:
            pattern: PatternDefinition to add
        """
        self.patterns.append(pattern)
        compiled = pattern.compile_patterns()
        for lang in pattern.languages:
            if lang not in self.compiled_patterns:
                self.compiled_patterns[lang] = []
            for regex in compiled:
                self.compiled_patterns[lang].append((pattern, regex))
                
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded patterns for AI understanding."""
        stats = {
            'total_patterns': len(self.patterns),
            'patterns_by_type': {},
            'patterns_by_severity': {},
            'supported_languages': list(self._supported_languages),
            'pattern_categories': []
        }
        
        for pattern in self.patterns:
            # Count by type
            ptype = pattern.pattern_type
            stats['patterns_by_type'][ptype] = stats['patterns_by_type'].get(ptype, 0) + 1
            
            # Count by severity
            severity = pattern.severity
            stats['patterns_by_severity'][severity] = stats['patterns_by_severity'].get(severity, 0) + 1
            
        stats['pattern_categories'] = list(stats['patterns_by_type'].keys())
        
        return stats