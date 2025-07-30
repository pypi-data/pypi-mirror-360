"""
GapDetectorInterface - Abstract base class for gap detection
Sprint 9 Week 2 Day 2-3

Defines the interface contract for gap detection components to ensure
consistent integration across the Copper Alloy Brass multi-agent system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

# Import capability assessor types
from .capability_assessor import ProjectCapabilities


@dataclass
class ProjectProfile:
    """Project-specific configuration for gap detection."""
    project_type: str
    maturity_level: str  # early, developing, mature
    risk_tolerance: str  # low, medium, high
    
    # Project-specific capability weights (0.0-1.0)
    capability_weights: Dict[str, float]
    
    # Custom thresholds
    critical_threshold: float = 60.0
    important_threshold: float = 70.0
    recommended_threshold: float = 80.0
    
    # Special considerations
    security_first: bool = False
    compliance_required: bool = False
    performance_critical: bool = False
    
    # Override settings
    advisor_mode: bool = False  # If True, only advise, don't enforce
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'project_type': self.project_type,
            'maturity_level': self.maturity_level,
            'risk_tolerance': self.risk_tolerance,
            'capability_weights': self.capability_weights,
            'critical_threshold': self.critical_threshold,
            'important_threshold': self.important_threshold,
            'recommended_threshold': self.recommended_threshold,
            'security_first': self.security_first,
            'compliance_required': self.compliance_required,
            'performance_critical': self.performance_critical,
            'advisor_mode': self.advisor_mode
        }


@dataclass
class Gap:
    """Represents a single capability gap."""
    capability_name: str
    current_score: float
    target_score: float
    gap_size: float
    confidence: float  # 0.0-1.0
    risk_score: int  # 0-100
    category: str  # critical, important, recommended, nice-to-have
    recommendations: List[str]
    estimated_effort: str  # small, medium, large
    dependencies: List[str]
    
    # Additional metadata
    framework_specific: bool = False
    security_related: bool = False
    compliance_related: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DCP storage."""
        return {
            'capability_name': self.capability_name,
            'current_score': self.current_score,
            'target_score': self.target_score,
            'gap_size': self.gap_size,
            'confidence': self.confidence,
            'risk_score': self.risk_score,
            'category': self.category,
            'recommendations': self.recommendations,
            'estimated_effort': self.estimated_effort,
            'dependencies': self.dependencies,
            'framework_specific': self.framework_specific,
            'security_related': self.security_related,
            'compliance_related': self.compliance_related
        }


@dataclass
class GapAnalysis:
    """Complete gap analysis results."""
    # Unique identifier for this analysis
    gap_analysis_id: str
    
    # Context
    project_type: str
    project_profile: ProjectProfile
    sensitivity_level: str
    analysis_time: datetime
    
    # Results
    total_gaps: int
    critical_gaps: List[Gap]
    important_gaps: List[Gap]
    recommended_gaps: List[Gap]
    nice_to_have_gaps: List[Gap]
    
    # Aggregate metrics
    overall_risk_score: int
    overall_confidence: float
    
    # Prioritized action plan
    prioritized_actions: List[Dict[str, Any]]
    
    # Analysis metadata
    analysis_duration: float
    capabilities_analyzed: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DCP storage."""
        return {
            'gap_analysis_id': self.gap_analysis_id,
            'project_type': self.project_type,
            'project_profile': self.project_profile.to_dict(),
            'sensitivity_level': self.sensitivity_level,
            'analysis_time': self.analysis_time.isoformat(),
            'total_gaps': self.total_gaps,
            'critical_gaps': [g.to_dict() for g in self.critical_gaps],
            'important_gaps': [g.to_dict() for g in self.important_gaps],
            'recommended_gaps': [g.to_dict() for g in self.recommended_gaps],
            'nice_to_have_gaps': [g.to_dict() for g in self.nice_to_have_gaps],
            'overall_risk_score': self.overall_risk_score,
            'overall_confidence': self.overall_confidence,
            'prioritized_actions': self.prioritized_actions,
            'analysis_duration': self.analysis_duration,
            'capabilities_analyzed': self.capabilities_analyzed
        }


class GapDetectorInterface(ABC):
    """
    Abstract interface for gap detection components.
    
    This interface ensures consistent behavior across different gap detection
    implementations and enables clean integration with other Copper Alloy Brass agents.
    """
    
    @abstractmethod
    def __init__(
        self, 
        sensitivity_level: str = 'moderate',
        project_root: Optional[Path] = None
    ):
        """
        Initialize gap detector with sensitivity level and DCP integration.
        
        Args:
            sensitivity_level: One of 'strict', 'moderate', 'permissive'
            project_root: Root path for DCP manager initialization
        """
        pass
    
    @abstractmethod
    async def find_gaps(
        self,
        capabilities: ProjectCapabilities,
        project_profile: Optional[ProjectProfile] = None
    ) -> GapAnalysis:
        """
        Analyze capabilities to identify gaps.
        
        Args:
            capabilities: Assessment results from CapabilityAssessor
            project_profile: Optional project-specific configuration
            
        Returns:
            GapAnalysis with categorized and prioritized gaps
        """
        pass
    
    @abstractmethod
    def calculate_gap_confidence(
        self,
        gap: Gap,
        project_profile: ProjectProfile
    ) -> float:
        """
        Calculate confidence score for a specific gap.
        
        Args:
            gap: The gap to evaluate
            project_profile: Project context for scoring
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        pass
    
    @abstractmethod
    def assess_gap_risk(
        self,
        gap: Gap,
        project_profile: ProjectProfile
    ) -> int:
        """
        Assess risk level for a specific gap.
        
        Args:
            gap: The gap to evaluate
            project_profile: Project context for risk assessment
            
        Returns:
            Risk score between 0 and 100
        """
        pass
    
    @abstractmethod
    def prioritize_actions(
        self,
        gaps: List[Gap],
        project_profile: ProjectProfile
    ) -> List[Dict[str, Any]]:
        """
        Create prioritized action plan from identified gaps.
        
        Args:
            gaps: All identified gaps
            project_profile: Project context for prioritization
            
        Returns:
            Prioritized list of actions with metadata
        """
        pass
    
    @abstractmethod
    def estimate_effort(
        self,
        gap: Gap,
        project_profile: ProjectProfile
    ) -> str:
        """
        Estimate implementation effort for addressing a gap.
        
        Args:
            gap: The gap to evaluate
            project_profile: Project context
            
        Returns:
            Effort level: 'small', 'medium', or 'large'
        """
        pass


# Default project profiles for common project types
DEFAULT_PROFILES = {
    'web_app': ProjectProfile(
        project_type='web_app',
        maturity_level='developing',
        risk_tolerance='medium',
        capability_weights={
            'authentication': 1.0,
            'security': 1.0,
            'api_design': 0.9,
            'performance': 0.8,
            'accessibility': 0.7
        },
        security_first=True
    ),
    'cli_tool': ProjectProfile(
        project_type='cli_tool',
        maturity_level='developing',
        risk_tolerance='medium',
        capability_weights={
            'error_handling': 1.0,
            'documentation': 0.9,
            'testing': 0.9,
            'configuration': 0.8
        }
    ),
    'library': ProjectProfile(
        project_type='library',
        maturity_level='developing',
        risk_tolerance='low',
        capability_weights={
            'documentation': 1.0,
            'testing': 1.0,
            'api_design': 0.9,
            'code_quality': 0.9
        }
    ),
    'api_service': ProjectProfile(
        project_type='api_service',
        maturity_level='developing',
        risk_tolerance='low',
        capability_weights={
            'security': 1.0,
            'authentication': 1.0,
            'api_design': 1.0,
            'monitoring': 0.9,
            'error_handling': 0.9
        },
        security_first=True,
        performance_critical=True
    )
}