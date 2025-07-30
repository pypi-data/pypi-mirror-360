"""Core data models for Copper Sun Brass.

This module provides structured data models for representing analysis results,
issues, patterns, and recommendations. These models ensure type safety and 
consistent data handling throughout the system.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path


class IssueType(Enum):
    """Types of code issues that can be detected."""
    SYNTAX_ERROR = "syntax_error"
    LOGIC_ERROR = "logic_error"
    PERFORMANCE = "performance"
    SECURITY = "security"
    STYLE = "style"
    BEST_PRACTICE = "best_practice"
    DOCUMENTATION = "documentation"
    DEPRECATED = "deprecated"
    COMPLEXITY = "complexity"
    DUPLICATION = "duplication"
    TODO = "todo"
    FIXME = "fixme"
    VULNERABILITY = "vulnerability"


class IssueSeverity(Enum):
    """Severity levels for issues."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class PatternType(Enum):
    """Types of code patterns that can be detected."""
    SECURITY_PATTERN = "security_pattern"
    DESIGN_PATTERN = "design_pattern"
    ANTI_PATTERN = "anti_pattern"
    CODE_SMELL = "code_smell"
    BEST_PRACTICE = "best_practice"
    NAMING_CONVENTION = "naming_convention"


@dataclass
class Issue:
    """Represents a code issue found during analysis.
    
    This class encapsulates all information about a specific issue,
    including its location, severity, and suggested remediation.
    """
    type: IssueType
    severity: IssueSeverity
    message: str
    file_path: Path
    line_number: int
    column_number: Optional[int] = None
    end_line: Optional[int] = None
    end_column: Optional[int] = None
    rule_id: Optional[str] = None
    suggestion: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "type": self.type.value,
            "severity": self.severity.value,
            "message": self.message,
            "file_path": str(self.file_path),
            "line_number": self.line_number,
            "column_number": self.column_number,
            "end_line": self.end_line,
            "end_column": self.end_column,
            "rule_id": self.rule_id,
            "suggestion": self.suggestion,
            "context": self.context,
            "confidence": self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Issue':
        """Create Issue from dictionary."""
        return cls(
            type=IssueType(data['type']),
            severity=IssueSeverity(data['severity']),
            message=data['message'],
            file_path=Path(data['file_path']),
            line_number=data['line_number'],
            column_number=data.get('column_number'),
            end_line=data.get('end_line'),
            end_column=data.get('end_column'),
            rule_id=data.get('rule_id'),
            suggestion=data.get('suggestion'),
            context=data.get('context', {}),
            confidence=data.get('confidence', 1.0)
        )
    
    @property
    def is_security_related(self) -> bool:
        """Check if this is a security-related issue."""
        return self.type in [IssueType.SECURITY, IssueType.VULNERABILITY]
    
    @property
    def is_high_priority(self) -> bool:
        """Check if this is a high priority issue."""
        return self.severity in [IssueSeverity.CRITICAL, IssueSeverity.HIGH]


@dataclass
class FileAnalysis:
    """Analysis results for a single file.
    
    Contains all issues, patterns, and metrics discovered during
    analysis of a specific file.
    """
    file_path: Path
    language: str
    size_bytes: int
    line_count: int
    issues: List[Issue] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    patterns: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    analysis_duration: float = 0.0  # seconds
    ml_enabled: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "file_path": str(self.file_path),
            "language": self.language,
            "size_bytes": self.size_bytes,
            "line_count": self.line_count,
            "issues": [issue.to_dict() for issue in self.issues],
            "metrics": self.metrics,
            "patterns": self.patterns,
            "timestamp": self.timestamp.isoformat(),
            "analysis_duration": self.analysis_duration,
            "ml_enabled": self.ml_enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileAnalysis':
        """Create FileAnalysis from dictionary."""
        return cls(
            file_path=Path(data['file_path']),
            language=data['language'],
            size_bytes=data['size_bytes'],
            line_count=data['line_count'],
            issues=[Issue.from_dict(issue) for issue in data.get('issues', [])],
            metrics=data.get('metrics', {}),
            patterns=data.get('patterns', []),
            timestamp=datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else datetime.utcnow(),
            analysis_duration=data.get('analysis_duration', 0.0),
            ml_enabled=data.get('ml_enabled', False)
        )
    
    @property
    def has_issues(self) -> bool:
        """Check if file has any issues."""
        return len(self.issues) > 0
    
    @property
    def critical_issues(self) -> List[Issue]:
        """Get critical issues."""
        return [i for i in self.issues if i.severity == IssueSeverity.CRITICAL]
    
    @property
    def high_priority_issues(self) -> List[Issue]:
        """Get high priority issues."""
        return [i for i in self.issues if i.severity in [IssueSeverity.CRITICAL, IssueSeverity.HIGH]]
    
    @property
    def security_issues(self) -> List[Issue]:
        """Get security-related issues."""
        return [i for i in self.issues if i.is_security_related]
    
    @property
    def issue_count_by_severity(self) -> Dict[str, int]:
        """Get count of issues by severity."""
        counts = {severity.value: 0 for severity in IssueSeverity}
        for issue in self.issues:
            counts[issue.severity.value] += 1
        return counts


@dataclass
class ProjectAnalysis:
    """Analysis results for an entire project.
    
    Aggregates results from multiple file analyses and provides
    project-level insights and metrics.
    """
    project_path: Path
    total_files: int
    analyzed_files: int
    file_analyses: List[FileAnalysis] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_seconds: float = 0.0
    agent_results: Dict[str, Any] = field(default_factory=dict)  # Results from different agents
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "project_path": str(self.project_path),
            "total_files": self.total_files,
            "analyzed_files": self.analyzed_files,
            "file_analyses": [fa.to_dict() for fa in self.file_analyses],
            "summary": self.summary,
            "timestamp": self.timestamp.isoformat(),
            "duration_seconds": self.duration_seconds,
            "agent_results": self.agent_results
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectAnalysis':
        """Create ProjectAnalysis from dictionary."""
        return cls(
            project_path=Path(data['project_path']),
            total_files=data['total_files'],
            analyzed_files=data['analyzed_files'],
            file_analyses=[FileAnalysis.from_dict(fa) for fa in data.get('file_analyses', [])],
            summary=data.get('summary', {}),
            timestamp=datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else datetime.utcnow(),
            duration_seconds=data.get('duration_seconds', 0.0),
            agent_results=data.get('agent_results', {})
        )
    
    @property
    def total_issues(self) -> int:
        """Get total number of issues across all files."""
        return sum(len(fa.issues) for fa in self.file_analyses)
    
    @property
    def issues_by_severity(self) -> Dict[str, int]:
        """Get issue count by severity across all files."""
        counts = {severity.value: 0 for severity in IssueSeverity}
        for fa in self.file_analyses:
            for issue in fa.issues:
                counts[issue.severity.value] += 1
        return counts
    
    @property
    def issues_by_type(self) -> Dict[str, int]:
        """Get issue count by type across all files."""
        counts = {issue_type.value: 0 for issue_type in IssueType}
        for fa in self.file_analyses:
            for issue in fa.issues:
                counts[issue.type.value] += 1
        return counts
    
    @property
    def security_issues(self) -> List[Issue]:
        """Get all security issues across all files."""
        security_issues = []
        for fa in self.file_analyses:
            security_issues.extend(fa.security_issues)
        return security_issues
    
    @property
    def critical_issues(self) -> List[Issue]:
        """Get all critical issues across all files."""
        critical_issues = []
        for fa in self.file_analyses:
            critical_issues.extend(fa.critical_issues)
        return critical_issues


@dataclass
class Pattern:
    """Represents a code pattern detected during analysis.
    
    Patterns can be design patterns, anti-patterns, code smells,
    or other recurring structures in the codebase.
    """
    name: str
    description: str
    pattern_type: PatternType
    confidence: float  # 0.0 to 1.0
    occurrences: int
    examples: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    severity: IssueSeverity = IssueSeverity.INFO
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "pattern_type": self.pattern_type.value,
            "confidence": self.confidence,
            "occurrences": self.occurrences,
            "examples": self.examples,
            "metadata": self.metadata,
            "severity": self.severity.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pattern':
        """Create Pattern from dictionary."""
        return cls(
            name=data['name'],
            description=data['description'],
            pattern_type=PatternType(data['pattern_type']),
            confidence=data['confidence'],
            occurrences=data['occurrences'],
            examples=data.get('examples', []),
            metadata=data.get('metadata', {}),
            severity=IssueSeverity(data.get('severity', 'info'))
        )


@dataclass
class Recommendation:
    """Represents a code improvement recommendation.
    
    Recommendations are generated based on analysis results and
    provide actionable advice for improving code quality.
    """
    title: str
    description: str
    priority: float  # 0.0 to 1.0
    impact: str  # high, medium, low
    effort: str  # high, medium, low
    category: str
    file_paths: List[Path] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    related_issues: List[Issue] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "impact": self.impact,
            "effort": self.effort,
            "category": self.category,
            "file_paths": [str(p) for p in self.file_paths],
            "details": self.details,
            "related_issues": [issue.to_dict() for issue in self.related_issues]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Recommendation':
        """Create Recommendation from dictionary."""
        return cls(
            title=data['title'],
            description=data['description'],
            priority=data['priority'],
            impact=data['impact'],
            effort=data['effort'],
            category=data['category'],
            file_paths=[Path(p) for p in data.get('file_paths', [])],
            details=data.get('details', {}),
            related_issues=[Issue.from_dict(issue) for issue in data.get('related_issues', [])]
        )


@dataclass
class AgentResult:
    """Represents the result of an agent's analysis.
    
    Used to standardize results from different agents (Scout, Watch, etc.)
    and provide consistent success/error handling.
    """
    agent_name: str
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_seconds: float = 0.0
    observations_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "agent_name": self.agent_name,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
            "duration_seconds": self.duration_seconds,
            "observations_count": self.observations_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentResult':
        """Create AgentResult from dictionary."""
        return cls(
            agent_name=data['agent_name'],
            success=data['success'],
            data=data.get('data', {}),
            error=data.get('error'),
            timestamp=datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else datetime.utcnow(),
            duration_seconds=data.get('duration_seconds', 0.0),
            observations_count=data.get('observations_count', 0)
        )


# Utility functions for model conversion
def convert_dict_to_models(data: Dict[str, Any]) -> Union[Issue, FileAnalysis, ProjectAnalysis, Pattern, Recommendation, AgentResult]:
    """Convert a dictionary to the appropriate model based on its structure."""
    if 'agent_name' in data:
        return AgentResult.from_dict(data)
    elif 'file_path' in data and 'issues' in data:
        return FileAnalysis.from_dict(data)
    elif 'project_path' in data and 'file_analyses' in data:
        return ProjectAnalysis.from_dict(data)
    elif 'pattern_type' in data:
        return Pattern.from_dict(data)
    elif 'impact' in data and 'effort' in data:
        return Recommendation.from_dict(data)
    elif 'severity' in data and 'line_number' in data:
        return Issue.from_dict(data)
    else:
        raise ValueError(f"Unknown model type for data: {data}")


def validate_model_data(model_instance: Any) -> bool:
    """Validate that a model instance has all required fields."""
    try:
        model_instance.to_dict()
        return True
    except Exception:
        return False