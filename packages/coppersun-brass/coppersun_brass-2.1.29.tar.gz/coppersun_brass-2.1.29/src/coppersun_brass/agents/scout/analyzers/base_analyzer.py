"""Base analyzer abstract class and data models for code analysis.

General Staff Role: G2 Intelligence Framework
Provides the foundation for all code analyzers to ensure consistent
intelligence gathering and AI-optimized data structures.

Persistent Value: Creates standardized observation formats that future
AI sessions can reliably parse and understand.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import json


@dataclass
class CodeEntity:
    """Represents a code entity for AI understanding.
    
    This structure is optimized for LLM parsing with semantic field names
    and clear relationships between code elements.
    """
    
    entity_type: str  # 'function', 'class', 'method', 'variable', 'constant'
    entity_name: str
    file_path: str
    line_start: int
    line_end: int
    complexity_score: int = 0
    docstring: Optional[str] = None
    parameters: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    parent_entity: Optional[str] = None  # Parent class for methods
    dependencies: List[str] = field(default_factory=list)  # What this entity imports/uses
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dcp_observation(self) -> Dict[str, Any]:
        """Convert to DCP observation format for AI consumption."""
        return {
            "type": "code_entity",
            "subtype": self.entity_type,
            "name": self.entity_name,
            "location": {
                "file": self.file_path,
                "start_line": self.line_start,
                "end_line": self.line_end
            },
            "complexity": self.complexity_score,
            "has_documentation": bool(self.docstring),
            "dependencies_count": len(self.dependencies),
            "metadata": self.metadata
        }


@dataclass
class CodeIssue:
    """Represents a code issue or smell for AI assessment.
    
    Structured to help AI understand the severity and context of issues,
    enabling strategic recommendations.
    """
    
    issue_type: str  # 'long_function', 'missing_docstring', 'high_complexity', etc.
    severity: str  # 'low', 'medium', 'high', 'critical'
    file_path: str
    line_number: int
    entity_name: str
    description: str
    ai_recommendation: str  # Strategic recommendation for AI commander
    fix_complexity: str  # 'trivial', 'simple', 'moderate', 'complex'
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dcp_observation(self) -> Dict[str, Any]:
        """Convert to DCP observation for strategic planning."""
        return {
            "type": "code_issue",
            "subtype": self.issue_type,
            "severity": self.severity,
            "location": {
                "file": self.file_path,
                "line": self.line_number,
                "entity": self.entity_name
            },
            "description": self.description,
            "recommendation": self.ai_recommendation,
            "fix_complexity": self.fix_complexity,
            "metadata": self.metadata
        }


@dataclass
class CodeMetrics:
    """Aggregated metrics for AI strategic assessment.
    
    Provides high-level metrics that help AI understand project health
    and make informed recommendations.
    """
    
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    total_entities: int = 0
    total_functions: int = 0
    total_classes: int = 0
    average_complexity: float = 0.0
    max_complexity: int = 0
    documentation_coverage: float = 0.0  # Percentage of entities with docs
    test_coverage: Optional[float] = None  # If available from external tools
    issues_by_severity: Dict[str, int] = field(default_factory=dict)
    language_specific_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dcp_observation(self) -> Dict[str, Any]:
        """Convert to DCP observation for project assessment."""
        return {
            "type": "code_metrics",
            "metrics": {
                "size": {
                    "total_lines": self.total_lines,
                    "code_lines": self.code_lines,
                    "comment_ratio": self.comment_lines / self.total_lines if self.total_lines > 0 else 0
                },
                "complexity": {
                    "average": self.average_complexity,
                    "maximum": self.max_complexity
                },
                "quality": {
                    "documentation_coverage": self.documentation_coverage,
                    "test_coverage": self.test_coverage,
                    "issues": self.issues_by_severity
                },
                "language_specific": self.language_specific_metrics
            }
        }


@dataclass
class AnalysisResult:
    """Complete analysis result optimized for AI consumption.
    
    This is the primary output of any analyzer, structured to provide
    comprehensive intelligence for AI decision-making.
    """
    
    file_path: str
    language: str
    analysis_timestamp: datetime
    entities: List[CodeEntity] = field(default_factory=list)
    issues: List[CodeIssue] = field(default_factory=list)
    metrics: CodeMetrics = field(default_factory=CodeMetrics)
    dependencies: List[str] = field(default_factory=list)  # External dependencies
    imports: List[str] = field(default_factory=list)  # Internal imports
    ast_fingerprint: Optional[str] = None  # For change detection
    analysis_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dcp_observations(self) -> List[Dict[str, Any]]:
        """Convert entire analysis to DCP observations for AI coordination."""
        observations = []
        
        # Add file-level observation
        observations.append({
            "type": "file_analysis",
            "file_path": self.file_path,
            "language": self.language,
            "timestamp": self.analysis_timestamp.isoformat(),
            "fingerprint": self.ast_fingerprint,
            "summary": f"File {Path(self.file_path).name}: {len(self.entities)} entities, {len(self.issues)} issues, complexity {self.metrics.average_complexity:.1f}",
            "priority": 70 if len(self.issues) > 5 else 50,
            "data": {
                "entities": len(self.entities),
                "issues": len(self.issues),
                "complexity": self.metrics.average_complexity
            }
        })
        
        # Add significant entities (high complexity or issues)
        for entity in self.entities:
            if entity.complexity_score > 10 or not entity.docstring:
                observations.append(entity.to_dcp_observation())
        
        # Add all medium+ severity issues
        for issue in self.issues:
            if issue.severity in ['medium', 'high', 'critical']:
                observations.append(issue.to_dcp_observation())
        
        # Add metrics if concerning
        if (self.metrics.average_complexity > 5 or 
            self.metrics.documentation_coverage < 0.5 or
            self.metrics.issues_by_severity.get('high', 0) > 0):
            observations.append(self.metrics.to_dcp_observation())
        
        return observations


class BaseAnalyzer(ABC):
    """Abstract base class for all code analyzers.
    
    General Staff Role: Defines the intelligence gathering contract that
    all analyzers must fulfill to support AI strategic planning.
    
    Every analyzer must:
    1. Integrate with DCP for coordination
    2. Provide AI-optimized output structures
    3. Support graceful degradation on errors
    4. Contribute to persistent strategic memory
    """
    
    def __init__(self, dcp_path: Optional[str] = None):
        """Initialize analyzer with mandatory DCP integration.
        
        Args:
            dcp_path: Path to DCP file for coordination
        """
        self.dcp_path = dcp_path
        self._supported_languages: Set[str] = set()
        
    @abstractmethod
    def analyze(self, file_path: Path) -> AnalysisResult:
        """Analyze a file and return AI-optimized results.
        
        This method must:
        1. Parse the file using appropriate techniques
        2. Extract entities, issues, and metrics
        3. Structure data for AI consumption
        4. Handle errors gracefully
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            AnalysisResult optimized for AI understanding
        """
        pass
        
    @abstractmethod
    def supports_language(self, language: str) -> bool:
        """Check if analyzer supports given language.
        
        Args:
            language: Language identifier (e.g., 'python', 'javascript')
            
        Returns:
            True if language is supported
        """
        pass
        
    def can_analyze(self, file_path: Path) -> bool:
        """Check if analyzer can handle this file.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file can be analyzed
        """
        if not file_path.exists():
            return False
            
        # Map common extensions to languages
        ext_to_lang = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.mjs': 'javascript',
            '.cjs': 'javascript'
        }
        
        language = ext_to_lang.get(file_path.suffix.lower())
        return language is not None and self.supports_language(language)
        
    def extract_language(self, file_path: Path) -> Optional[str]:
        """Extract language from file extension.
        
        Args:
            file_path: File to check
            
        Returns:
            Language identifier or None
        """
        ext_to_lang = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.mjs': 'javascript',
            '.cjs': 'javascript'
        }
        return ext_to_lang.get(file_path.suffix.lower())