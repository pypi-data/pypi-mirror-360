"""
Copper Sun Brass - AI Advisory System for Software Development

This package provides AI-powered project analysis, monitoring, and advisory capabilities.
"""

__version__ = "2.1.4"

# Export main classes for easy import
from .config import BrassConfig
from .core.models import Issue, IssueType, IssueSeverity, FileAnalysis, AgentResult

# Optional imports that may require additional dependencies
try:
    from .core.brass import Brass
    _BRASS_AVAILABLE = True
except ImportError:
    _BRASS_AVAILABLE = False

try:
    from .runner import BrassRunner
    _RUNNER_AVAILABLE = True
except ImportError:
    _RUNNER_AVAILABLE = False

__all__ = [
    'BrassConfig',
    'Issue',
    'IssueType', 
    'IssueSeverity',
    'FileAnalysis',
    'AgentResult'
]

# Add optional exports if available
if _BRASS_AVAILABLE:
    __all__.append('Brass')
if _RUNNER_AVAILABLE:
    __all__.append('BrassRunner')