"""
Copper Alloy Brass Planning Intelligence Engine
Advanced planning algorithms for autonomous software development
"""

from .planning_algorithms import PlanningAlgorithms
from .constraint_solver import ConstraintSolver
from .adaptation_engine import AdaptationEngine          # USED: Dynamic plan modification via intelligence_coordinator
from .intelligence_coordinator import IntelligenceCoordinator

# NOTE: AdaptationEngine is actively used by intelligence_coordinator.adapt_plan()
# See docs/implementation/STRATEGIST_FEATURE_ROADMAP.md for full feature activation

__all__ = [
    'PlanningAlgorithms',
    'ConstraintSolver', 
    'AdaptationEngine',
    'IntelligenceCoordinator'
]