"""Scout Agent - Comprehensive code intelligence gathering.

General Staff Role: G2 Intelligence
Provides multi-layered code analysis including TODO detection,
AST analysis, pattern recognition, and evolution tracking.
"""

from .scout_agent import ScoutAgent, ScoutAnalysisResult, create_scout_agent, run_scout_analysis
from .todo_detector import TODODetector, TODOFinding
from .dcp_integrator import ScoutDCPIntegrator
from .research_generator import ResearchQueryGenerator, ResearchQuery, ResearchType

# Enhanced analyzers
from .analyzers import (
    BaseAnalyzer, AnalysisResult, CodeEntity, CodeIssue, CodeMetrics,
    PythonAnalyzer, PatternAnalyzer, PatternDefinition
)
from .analyzers.evolution_tracker import EvolutionTracker, IssueEvolution

__all__ = [
    # Main agent
    'ScoutAgent', 'ScoutAnalysisResult', 'create_scout_agent', 'run_scout_analysis',
    
    # Core components
    'TODODetector', 'TODOFinding',
    'ScoutDCPIntegrator',
    'ResearchQueryGenerator', 'ResearchQuery', 'ResearchType',
    
    # Enhanced analyzers
    'BaseAnalyzer', 'AnalysisResult', 'CodeEntity', 'CodeIssue', 'CodeMetrics',
    'PythonAnalyzer', 'PatternAnalyzer', 'PatternDefinition',
    'EvolutionTracker', 'IssueEvolution'
]