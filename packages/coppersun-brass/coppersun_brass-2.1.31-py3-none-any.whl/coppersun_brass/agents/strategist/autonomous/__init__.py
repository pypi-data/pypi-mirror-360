"""
Sprint 9: Autonomous Planning Components.

This module contains the autonomous planning system components:
- Week 1: Project Context Analysis
- Week 2: Capability Assessment and Gap Detection
- Week 3: Enhanced CLI and Feedback Integration
- Week 4: Intelligence Coordinator and Testing
"""

# Week 1 components
from .context_analyzer import ProjectContextAnalyzer, ProjectContext

# Week 2 components
from .capability_assessor import CapabilityAssessor, ProjectCapabilities, CapabilityScore
from .gap_detector import GapDetector, GapAnalysis, ProjectProfile
from .best_practices_engine import BestPracticesEngine, PracticeRecommendation, BestPracticesProfile

__all__ = [
    # Week 1
    'ProjectContextAnalyzer',
    'ProjectContext',
    # Week 2
    'CapabilityAssessor',
    'ProjectCapabilities',
    'CapabilityScore',
    'GapDetector',
    'GapAnalysis',
    'ProjectProfile',
    'BestPracticesEngine',
    'PracticeRecommendation',
    'BestPracticesProfile'
]