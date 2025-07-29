"""
GapDetector - Identifies gaps between capabilities and best practices
Sprint 9 Week 2 Day 2-3

Analyzes CapabilityAssessor output to identify actionable gaps with
confidence scoring, risk assessment, and configurable sensitivity levels.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import logging

# Import interfaces and types
from .gap_detector_interface import (
    GapDetectorInterface, Gap, GapAnalysis, ProjectProfile, DEFAULT_PROFILES
)
from .capability_assessor import ProjectCapabilities, CapabilityScore

# DCP integration (MANDATORY)
try:
    from coppersun_brass.core.context.dcp_manager import DCPManager
    DCP_AVAILABLE = True
except ImportError:
    DCP_AVAILABLE = False
    DCPManager = None

logger = logging.getLogger(__name__)


class GapDetector(GapDetectorInterface):
    """
    Identifies gaps between current capabilities and best practices.
    
    Key features:
    - Multi-factor confidence scoring
    - Risk-based prioritization
    - Configurable sensitivity levels
    - Project-specific gap detection
    - Historical feedback infrastructure
    - Full DCP integration for multi-agent coordination
    """
    
    def __init__(
        self,
        sensitivity_level: str = 'moderate',
        project_root: Optional[Path] = None
    ):
        """Initialize gap detector with sensitivity level and DCP integration."""
        self.sensitivity_level = sensitivity_level
        self.project_root = project_root or Path.cwd()
        
        # Initialize DCP manager if available
        self.dcp_manager = None
        if DCP_AVAILABLE:
            try:
                self.dcp_manager = DCPManager(self.project_root)
                logger.info("DCP integration enabled for GapDetector")
                # Read historical gap analyses on startup
                self._load_historical_analyses()
            except Exception as e:
                logger.warning(f"DCP manager initialization failed: {e}")
        
        # Sensitivity level configurations
        self.sensitivity_configs = {
            'strict': {
                'min_confidence': 0.9,
                'capability_threshold': 80,
                'best_practices_weight': 1.0,
                'risk_tolerance': 'low',
                'gap_threshold': 10  # Even small gaps matter
            },
            'moderate': {
                'min_confidence': 0.7,
                'capability_threshold': 60,
                'best_practices_weight': 0.8,
                'risk_tolerance': 'medium',
                'gap_threshold': 20  # Moderate gaps
            },
            'permissive': {
                'min_confidence': 0.5,
                'capability_threshold': 40,
                'best_practices_weight': 0.6,
                'risk_tolerance': 'high',
                'gap_threshold': 30  # Only large gaps
            }
        }
        
        # Validate sensitivity level
        if sensitivity_level not in self.sensitivity_configs:
            logger.warning(f"Invalid sensitivity level: {sensitivity_level}, using 'moderate'")
            self.sensitivity_level = 'moderate'
        
        self.config = self.sensitivity_configs[self.sensitivity_level]
        
        # Historical analyses for learning
        self.historical_analyses: List[Dict] = []
        
        # Best practice targets by capability
        self.best_practice_targets = {
            'authentication': {'web_app': 90, 'api_service': 95, 'cli_tool': 70, 'library': 60},
            'testing': {'web_app': 80, 'api_service': 85, 'cli_tool': 75, 'library': 90},
            'documentation': {'web_app': 70, 'api_service': 75, 'cli_tool': 85, 'library': 95},
            'security': {'web_app': 85, 'api_service': 90, 'cli_tool': 70, 'library': 75},
            'error_handling': {'web_app': 80, 'api_service': 85, 'cli_tool': 90, 'library': 80},
            'logging': {'web_app': 75, 'api_service': 80, 'cli_tool': 80, 'library': 70},
            'configuration': {'web_app': 75, 'api_service': 80, 'cli_tool': 85, 'library': 70},
            'database': {'web_app': 80, 'api_service': 85, 'cli_tool': 60, 'library': 50},
            'api_design': {'web_app': 75, 'api_service': 90, 'cli_tool': 60, 'library': 85},
            'code_quality': {'web_app': 75, 'api_service': 80, 'cli_tool': 80, 'library': 85},
            'deployment': {'web_app': 80, 'api_service': 85, 'cli_tool': 70, 'library': 75},
            'monitoring': {'web_app': 75, 'api_service': 85, 'cli_tool': 60, 'library': 60},
            'performance': {'web_app': 80, 'api_service': 85, 'cli_tool': 75, 'library': 80},
            'accessibility': {'web_app': 70, 'api_service': 50, 'cli_tool': 30, 'library': 30},
            'internationalization': {'web_app': 60, 'api_service': 50, 'cli_tool': 40, 'library': 50}
        }

    def _load_historical_analyses(self):
        """Load historical gap analyses from DCP for learning."""
        if not self.dcp_manager:
            return
        
        try:
            dcp_data = self.dcp_manager.read_dcp()
            if dcp_data and 'observations' in dcp_data:
                for obs in dcp_data['observations'].values():
                    if obs.get('type') == 'file_analysis' and 'gap_analysis' in obs.get('summary', '').lower():
                        self.historical_analyses.append(obs)
                
                logger.info(f"Loaded {len(self.historical_analyses)} historical gap analyses")
        except Exception as e:
            logger.error(f"Failed to load historical analyses: {e}")

    async def find_gaps(
        self,
        capabilities: ProjectCapabilities,
        project_profile: Optional[ProjectProfile] = None
    ) -> GapAnalysis:
        """Analyze capabilities to identify gaps with confidence and risk scoring."""
        start_time = datetime.now()
        logger.info(f"Starting gap analysis for {capabilities.project_type} project")
        
        # Use default profile if not provided
        if not project_profile:
            if capabilities.project_type in DEFAULT_PROFILES:
                project_profile = DEFAULT_PROFILES[capabilities.project_type]
            else:
                # Generic profile for unknown project types
                project_profile = ProjectProfile(
                    project_type=capabilities.project_type,
                    maturity_level='developing',
                    risk_tolerance='medium',
                    capability_weights={}
                )
        
        # Generate unique analysis ID
        gap_analysis_id = f"gap_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
        
        # Identify all gaps
        all_gaps = []
        
        for cap_name, capability in capabilities.capabilities.items():
            gap = await self._analyze_capability_gap(
                cap_name, capability, capabilities.project_type, project_profile
            )
            if gap:
                all_gaps.append(gap)
        
        # Categorize gaps
        critical_gaps = []
        important_gaps = []
        recommended_gaps = []
        nice_to_have_gaps = []
        
        for gap in all_gaps:
            if gap.category == 'critical':
                critical_gaps.append(gap)
            elif gap.category == 'important':
                important_gaps.append(gap)
            elif gap.category == 'recommended':
                recommended_gaps.append(gap)
            else:
                nice_to_have_gaps.append(gap)
        
        # Calculate aggregate metrics
        overall_risk_score = self._calculate_overall_risk(all_gaps)
        overall_confidence = self._calculate_overall_confidence(all_gaps)
        
        # Create prioritized action plan
        prioritized_actions = self.prioritize_actions(all_gaps, project_profile)
        
        # Create analysis result
        analysis = GapAnalysis(
            gap_analysis_id=gap_analysis_id,
            project_type=capabilities.project_type,
            project_profile=project_profile,
            sensitivity_level=self.sensitivity_level,
            analysis_time=start_time,
            total_gaps=len(all_gaps),
            critical_gaps=critical_gaps,
            important_gaps=important_gaps,
            recommended_gaps=recommended_gaps,
            nice_to_have_gaps=nice_to_have_gaps,
            overall_risk_score=overall_risk_score,
            overall_confidence=overall_confidence,
            prioritized_actions=prioritized_actions,
            analysis_duration=(datetime.now() - start_time).total_seconds(),
            capabilities_analyzed=len(capabilities.capabilities)
        )
        
        # Write to DCP
        await self._write_analysis_to_dcp(analysis)
        
        return analysis

    async def _analyze_capability_gap(
        self,
        capability_name: str,
        capability: CapabilityScore,
        project_type: str,
        project_profile: ProjectProfile
    ) -> Optional[Gap]:
        """Analyze a single capability for gaps."""
        # Get target score
        target_score = self._get_target_score(
            capability_name, project_type, project_profile
        )
        
        # Calculate gap
        gap_size = target_score - capability.score
        
        # Apply sensitivity threshold
        if gap_size < self.config['gap_threshold']:
            return None
        
        # Create gap object
        gap = Gap(
            capability_name=capability_name,
            current_score=capability.score,
            target_score=target_score,
            gap_size=gap_size,
            confidence=0.0,  # Will be calculated
            risk_score=0,    # Will be calculated
            category='',     # Will be determined
            recommendations=capability.recommendations[:3],  # Top 3
            estimated_effort='',  # Will be estimated
            dependencies=self._identify_dependencies(capability_name),
            framework_specific=False,  # Could be enhanced
            security_related=capability_name in ['authentication', 'security'],
            compliance_related=capability_name in ['security', 'logging', 'monitoring']
        )
        
        # Calculate confidence
        gap.confidence = self.calculate_gap_confidence(gap, project_profile)
        
        # Skip if confidence too low (unless advisor mode)
        if not project_profile.advisor_mode and gap.confidence < self.config['min_confidence']:
            return None
        
        # Assess risk
        gap.risk_score = self.assess_gap_risk(gap, project_profile)
        
        # Categorize
        gap.category = self._categorize_gap(gap, project_profile)
        
        # Estimate effort
        gap.estimated_effort = self.estimate_effort(gap, project_profile)
        
        return gap

    def _get_target_score(
        self,
        capability_name: str,
        project_type: str,
        project_profile: ProjectProfile
    ) -> float:
        """Get target score for a capability based on project type and profile."""
        # Base target from best practices
        base_target = 75.0  # Default
        
        if capability_name in self.best_practice_targets:
            targets = self.best_practice_targets[capability_name]
            if project_type in targets:
                base_target = targets[project_type]
        
        # Apply profile adjustments
        weight = project_profile.capability_weights.get(capability_name, 1.0)
        adjusted_target = base_target * weight
        
        # Apply security-first mode
        if project_profile.security_first and capability_name in ['security', 'authentication']:
            adjusted_target = max(adjusted_target, 90.0)
        
        # Apply compliance requirements
        if project_profile.compliance_required and capability_name in ['logging', 'monitoring', 'security']:
            adjusted_target = max(adjusted_target, 85.0)
        
        # Apply performance critical
        if project_profile.performance_critical and capability_name == 'performance':
            adjusted_target = max(adjusted_target, 85.0)
        
        # Apply best practices weight from sensitivity
        final_target = adjusted_target * self.config['best_practices_weight']
        
        return min(100.0, final_target)

    def calculate_gap_confidence(
        self,
        gap: Gap,
        project_profile: ProjectProfile
    ) -> float:
        """Calculate multi-factor confidence score for a gap."""
        confidence_factors = []
        
        # Factor 1: Gap size significance
        gap_significance = min(1.0, gap.gap_size / 50.0)
        confidence_factors.append(gap_significance * 0.3)
        
        # Factor 2: Project maturity alignment
        maturity_scores = {
            'early': 0.6,      # Less confident for early projects
            'developing': 0.8,  # More confident for developing
            'mature': 0.9      # High confidence for mature
        }
        maturity_confidence = maturity_scores.get(project_profile.maturity_level, 0.7)
        confidence_factors.append(maturity_confidence * 0.2)
        
        # Factor 3: Capability criticality
        weight = project_profile.capability_weights.get(gap.capability_name, 0.5)
        confidence_factors.append(weight * 0.3)
        
        # Factor 4: Historical accuracy (if available)
        historical_confidence = self._get_historical_confidence(gap.capability_name)
        confidence_factors.append(historical_confidence * 0.2)
        
        # Combine factors
        overall_confidence = sum(confidence_factors)
        
        # Apply advisor mode penalty
        if project_profile.advisor_mode:
            overall_confidence *= 0.8
        
        return round(min(1.0, overall_confidence), 2)

    def _get_historical_confidence(self, capability_name: str) -> float:
        """Get historical confidence based on past analyses."""
        if not self.historical_analyses:
            return 0.7  # Default
        
        # Simple implementation - could be enhanced
        relevant_analyses = [
            a for a in self.historical_analyses
            if capability_name in str(a.get('details', {}))
        ]
        
        if not relevant_analyses:
            return 0.7
        
        # Average confidence from past analyses
        confidences = []
        for analysis in relevant_analyses[-5:]:  # Last 5
            if 'confidence' in analysis.get('metadata', {}):
                confidences.append(analysis['metadata']['confidence'])
        
        return sum(confidences) / len(confidences) if confidences else 0.7

    def assess_gap_risk(
        self,
        gap: Gap,
        project_profile: ProjectProfile
    ) -> int:
        """Assess risk level for a specific gap."""
        risk_score = 0
        
        # Base risk from gap size
        risk_score += min(40, int(gap.gap_size * 0.4))
        
        # Security risk multiplier
        if gap.security_related:
            risk_score += 30
            if project_profile.security_first:
                risk_score += 10
        
        # Compliance risk
        if gap.compliance_related and project_profile.compliance_required:
            risk_score += 25
        
        # Project type specific risks
        risk_multipliers = {
            'web_app': 1.1,      # Higher risk for public-facing
            'api_service': 1.2,  # Highest risk for APIs
            'cli_tool': 0.9,     # Lower risk for CLI tools
            'library': 1.0       # Standard risk for libraries
        }
        multiplier = risk_multipliers.get(project_profile.project_type, 1.0)
        risk_score = int(risk_score * multiplier)
        
        # Critical capability boost
        if gap.capability_name in ['authentication', 'security', 'error_handling']:
            risk_score = max(risk_score, 70)
        
        # Apply risk tolerance
        tolerance_modifiers = {
            'low': 1.2,      # Low tolerance = higher risk scores
            'medium': 1.0,   # No modification
            'high': 0.8      # High tolerance = lower risk scores
        }
        tolerance_mod = tolerance_modifiers.get(project_profile.risk_tolerance, 1.0)
        risk_score = int(risk_score * tolerance_mod)
        
        return min(100, risk_score)

    def _categorize_gap(self, gap: Gap, project_profile: ProjectProfile) -> str:
        """Categorize gap based on score, risk, and thresholds."""
        # Critical: High risk OR security/compliance OR below critical threshold
        if (gap.risk_score >= 70 or 
            (gap.security_related and project_profile.security_first) or
            (gap.compliance_related and project_profile.compliance_required) or
            gap.current_score < project_profile.critical_threshold):
            return 'critical'
        
        # Important: Moderate risk OR below important threshold
        elif (gap.risk_score >= 50 or 
              gap.current_score < project_profile.important_threshold):
            return 'important'
        
        # Recommended: Low risk but below recommended threshold
        elif gap.current_score < project_profile.recommended_threshold:
            return 'recommended'
        
        # Nice-to-have: Everything else
        else:
            return 'nice-to-have'

    def estimate_effort(
        self,
        gap: Gap,
        project_profile: ProjectProfile
    ) -> str:
        """Estimate implementation effort for addressing a gap."""
        # Base effort on gap size
        if gap.gap_size < 20:
            base_effort = 'small'
        elif gap.gap_size < 40:
            base_effort = 'medium'
        else:
            base_effort = 'large'
        
        # Adjust for capability complexity
        complex_capabilities = [
            'authentication', 'security', 'database', 
            'deployment', 'monitoring', 'performance'
        ]
        
        if gap.capability_name in complex_capabilities:
            # Increase effort level
            if base_effort == 'small':
                return 'medium'
            else:
                return 'large'
        
        # Adjust for dependencies
        if len(gap.dependencies) > 2:
            if base_effort == 'small':
                return 'medium'
            else:
                return 'large'
        
        return base_effort

    def _identify_dependencies(self, capability_name: str) -> List[str]:
        """Identify dependencies for a capability."""
        dependencies = {
            'authentication': ['security', 'database', 'configuration'],
            'security': ['configuration', 'logging'],
            'database': ['configuration', 'error_handling'],
            'deployment': ['testing', 'configuration', 'documentation'],
            'monitoring': ['logging', 'configuration'],
            'api_design': ['documentation', 'testing', 'security'],
            'performance': ['monitoring', 'testing']
        }
        
        return dependencies.get(capability_name, [])

    def prioritize_actions(
        self,
        gaps: List[Gap],
        project_profile: ProjectProfile
    ) -> List[Dict[str, Any]]:
        """Create prioritized action plan from identified gaps."""
        # Sort by priority: risk > confidence > gap size
        sorted_gaps = sorted(
            gaps,
            key=lambda g: (
                -g.risk_score,
                -g.confidence,
                -g.gap_size
            )
        )
        
        actions = []
        for i, gap in enumerate(sorted_gaps):
            action = {
                'priority': i + 1,
                'capability': gap.capability_name,
                'action': f"Improve {gap.capability_name} from {gap.current_score:.0f}% to {gap.target_score:.0f}%",
                'risk_score': gap.risk_score,
                'confidence': gap.confidence,
                'effort': gap.estimated_effort,
                'category': gap.category,
                'recommendations': gap.recommendations,
                'dependencies': gap.dependencies,
                'expected_impact': {
                    'risk_reduction': min(30, gap.risk_score * 0.4),
                    'compliance': gap.compliance_related,
                    'security': gap.security_related
                }
            }
            actions.append(action)
        
        return actions

    def _calculate_overall_risk(self, gaps: List[Gap]) -> int:
        """Calculate aggregate risk score."""
        if not gaps:
            return 0
        
        # Weighted average with emphasis on critical gaps
        total_weighted_risk = 0
        total_weight = 0
        
        weights = {
            'critical': 3.0,
            'important': 2.0,
            'recommended': 1.0,
            'nice-to-have': 0.5
        }
        
        for gap in gaps:
            weight = weights.get(gap.category, 1.0)
            total_weighted_risk += gap.risk_score * weight
            total_weight += weight
        
        return int(total_weighted_risk / total_weight) if total_weight > 0 else 0

    def _calculate_overall_confidence(self, gaps: List[Gap]) -> float:
        """Calculate aggregate confidence score."""
        if not gaps:
            return 0.0
        
        # Average confidence weighted by risk
        total_weighted_confidence = 0
        total_weight = 0
        
        for gap in gaps:
            weight = gap.risk_score / 100.0
            total_weighted_confidence += gap.confidence * weight
            total_weight += weight
        
        return round(total_weighted_confidence / total_weight, 2) if total_weight > 0 else 0.0

    async def _write_analysis_to_dcp(self, analysis: GapAnalysis):
        """Write gap analysis results to DCP."""
        if not self.dcp_manager:
            return
        
        try:
            observation = {
                'type': 'file_analysis',
                'priority': max(50, analysis.overall_risk_score),
                'summary': f"Gap analysis: {analysis.total_gaps} gaps identified for {analysis.project_type} project",
                'details': {
                    'gap_analysis_id': analysis.gap_analysis_id,
                    'project_type': analysis.project_type,
                    'sensitivity_level': analysis.sensitivity_level,
                    'total_gaps': analysis.total_gaps,
                    'critical_gaps': len(analysis.critical_gaps),
                    'important_gaps': len(analysis.important_gaps),
                    'recommended_gaps': len(analysis.recommended_gaps),
                    'overall_risk_score': analysis.overall_risk_score,
                    'overall_confidence': analysis.overall_confidence,
                    'top_actions': analysis.prioritized_actions[:5],
                    'analysis_duration': analysis.analysis_duration
                },
                'metadata': {
                    'agent': 'gap_detector',
                    'confidence': analysis.overall_confidence,
                    'timestamp': datetime.now().isoformat(),
                    'gap_analysis_id': analysis.gap_analysis_id
                }
            }
            
            obs_id = self.dcp_manager.add_observation(
                observation,
                source_agent='gap_detector'
            )
            logger.info(f"Gap analysis written to DCP: {obs_id}")
            
        except Exception as e:
            logger.error(f"Failed to write gap analysis to DCP: {e}")


if __name__ == "__main__":
    # Module test
    import asyncio
    
    async def test():
        detector = GapDetector(sensitivity_level='moderate')
        print("GapDetector module loaded successfully")
        print(f"Sensitivity level: {detector.sensitivity_level}")
        print(f"DCP integration: {'Enabled' if detector.dcp_manager else 'Disabled'}")
    
    asyncio.run(test())