# coppersun_brass/agents/strategist/__init__.py
"""
Copper Alloy Brass Strategist Agent Module

Central coordination agent for the Copper Alloy Brass ecosystem.
Orchestrates DCP updates, prioritizes observations, and routes tasks.
"""

from .strategist_agent import StrategistAgent
from .priority_engine import PriorityEngine
from .duplicate_detector import DuplicateDetector
from .orchestration_engine import OrchestrationEngine
from .config import StrategistConfig, get_strategist_config

# Import autonomous module
from . import autonomous

__all__ = [
    'StrategistAgent',
    'PriorityEngine', 
    'DuplicateDetector',
    'OrchestrationEngine',
    'StrategistConfig',
    'get_strategist_config',
    'autonomous'
]

__version__ = '2.3.0'