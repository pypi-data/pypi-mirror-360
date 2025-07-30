"""
PersonalizationEngine: Applies learned user preferences to recommendations.

This component implements:
- Preference-based recommendation scoring
- Dynamic reranking based on user history
- Team override support
- Personalization strength control
- DCP integration for persistence
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

# ARCHIVED DEPENDENCY: preference_learner moved to archive/future-features/
# from .preference_learner import PreferenceLearner, UserPreferences

# TODO ACTIVATION: To activate this module, either:
# 1. Restore preference_learner from archive, or  
# 2. Implement simplified preference handling without ML
# See docs/implementation/STRATEGIST_FEATURE_ROADMAP.md for details

# Placeholder classes for import compatibility
class PreferenceLearner:
    """Placeholder for archived PreferenceLearner"""
    pass

class UserPreferences:
    """Placeholder for archived UserPreferences"""
    def __init__(self, **kwargs):
        pass

# DCP integration
try:
    from coppersun_brass.core.context.dcp_manager import DCPManager
    DCP_AVAILABLE = True
except ImportError:
    DCP_AVAILABLE = False
    DCPManager = None

logger = logging.getLogger(__name__)


@dataclass
class PersonalizationConfig:
    """Configuration for personalization behavior."""
    
    # How much to weight preferences vs base score (0-1)
    personalization_strength: float = 0.3
    
    # Minimum confidence required to apply personalization
    min_confidence_threshold: float = 0.2
    
    # Whether to use team overrides if available
    respect_team_overrides: bool = True
    
    # Score adjustment ranges
    max_score_boost: float = 0.3  # Max increase
    max_score_penalty: float = 0.2  # Max decrease
    
    # Feature flags
    enable_capability_personalization: bool = True
    enable_category_personalization: bool = True
    enable_effort_personalization: bool = True
    enable_severity_personalization: bool = True


class PersonalizationEngine:
    """
    Applies user preferences to recommendations.
    
    Features:
    - Reranks recommendations based on preferences
    - Adjusts scores while maintaining baseline quality
    - Provides explainable personalization
    - Supports team-level overrides
    - Gradual personalization based on confidence
    """
    
    def __init__(self,
                 preference_learner: PreferenceLearner,
                 config: Optional[PersonalizationConfig] = None,
                 dcp_path: Optional[str] = None):
        """
        Initialize engine.
        
        Args:
            preference_learner: Learner instance for preferences
            config: Personalization configuration
            dcp_path: Path to DCP file/directory
        """
        self.learner = preference_learner
        self.config = config or PersonalizationConfig()
        
        self.dcp_manager = None
        if DCP_AVAILABLE and dcp_path:
            try:
                # DCPManager expects project root directory
                if dcp_path.endswith('.json'):
                    project_root = str(Path(dcp_path).parent)
                else:
                    project_root = dcp_path
                self.dcp_manager = DCPManager(project_root)
                logger.info("PersonalizationEngine: DCP integration enabled")
            except Exception as e:
                logger.warning(f"PersonalizationEngine: DCP unavailable: {e}")
    
    def personalize_gaps(self, 
                        gaps: List[Dict[str, Any]], 
                        user_id: str = "default") -> List[Dict[str, Any]]:
        """
        Apply personalization to gap recommendations.
        
        Args:
            gaps: List of gap dictionaries
            user_id: User identifier
            
        Returns:
            Personalized list with adjusted scores and rankings
        """
        # Get user preferences
        preferences = self.learner.learn_from_feedback(user_id)
        
        # Check if personalization should be applied
        if not self._should_personalize(preferences):
            logger.info("Personalization skipped: insufficient confidence")
            return gaps
        
        # Apply personalization to each gap
        personalized_gaps = []
        for gap in gaps:
            personalized = self._personalize_gap(gap, preferences)
            personalized_gaps.append(personalized)
        
        # Re-sort by personalized score
        personalized_gaps.sort(
            key=lambda x: x.get('personalized_score', x.get('priority_score', 0)),
            reverse=True
        )
        
        # Record personalization event
        self._record_personalization_event('gaps', len(gaps), preferences.confidence_score)
        
        return personalized_gaps
    
    def personalize_practices(self,
                            practices: List[Dict[str, Any]],
                            user_id: str = "default") -> List[Dict[str, Any]]:
        """
        Apply personalization to practice recommendations.
        
        Args:
            practices: List of practice dictionaries
            user_id: User identifier
            
        Returns:
            Personalized list with adjusted scores and rankings
        """
        # Get user preferences
        preferences = self.learner.learn_from_feedback(user_id)
        
        # Check if personalization should be applied
        if not self._should_personalize(preferences):
            logger.info("Personalization skipped: insufficient confidence")
            return practices
        
        # Apply personalization to each practice
        personalized_practices = []
        for practice in practices:
            personalized = self._personalize_practice(practice, preferences)
            personalized_practices.append(personalized)
        
        # Re-sort by personalized score
        personalized_practices.sort(
            key=lambda x: x.get('personalized_score', x.get('score', 0)),
            reverse=True
        )
        
        # Record personalization event
        self._record_personalization_event('practices', len(practices), preferences.confidence_score)
        
        return personalized_practices
    
    def _should_personalize(self, preferences: UserPreferences) -> bool:
        """Check if personalization should be applied."""
        # Team overrides always apply
        if self.config.respect_team_overrides and preferences.team_overrides:
            return True
        
        # Check confidence threshold
        return preferences.confidence_score >= self.config.min_confidence_threshold
    
    def _personalize_gap(self, gap: Dict[str, Any], preferences: UserPreferences) -> Dict[str, Any]:
        """Apply personalization to a single gap."""
        # Copy gap to avoid mutation
        personalized = gap.copy()
        
        # Get base score
        base_score = gap.get('priority_score', 50)
        adjustments = []
        
        # Apply capability preference
        if self.config.enable_capability_personalization:
            capability = gap.get('capability', '')
            if capability in preferences.capability_weights:
                weight = preferences.capability_weights[capability]
                # Convert weight (0-1) to adjustment (-max_penalty to +max_boost)
                if weight > 0.5:
                    adjustment = (weight - 0.5) * 2 * self.config.max_score_boost
                else:
                    adjustment = (weight - 0.5) * 2 * self.config.max_score_penalty
                
                adjustments.append({
                    'type': 'capability_preference',
                    'value': adjustment,
                    'reason': f"User preference for {capability}: {weight:.0%}"
                })
        
        # Apply effort preference
        if self.config.enable_effort_personalization:
            effort = gap.get('effort', 'medium').lower()
            if effort in preferences.effort_preferences:
                effort_weight = preferences.effort_preferences[effort]
                # Higher weight = more preferred
                adjustment = (effort_weight - 0.5) * self.config.max_score_boost
                
                adjustments.append({
                    'type': 'effort_preference',
                    'value': adjustment,
                    'reason': f"Effort preference for {effort}: {effort_weight:.0%}"
                })
        
        # Calculate final personalized score
        total_adjustment = sum(adj['value'] for adj in adjustments)
        
        # Apply personalization strength
        weighted_adjustment = total_adjustment * self.config.personalization_strength
        
        # Apply confidence-based dampening
        confidence_factor = preferences.confidence_score
        final_adjustment = weighted_adjustment * confidence_factor
        
        # Calculate final score (bounded 0-100)
        personalized_score = max(0, min(100, base_score + final_adjustment * 100))
        
        # Add personalization metadata
        personalized['personalized_score'] = personalized_score
        personalized['personalization_applied'] = True
        personalized['personalization_adjustments'] = adjustments
        personalized['personalization_delta'] = personalized_score - base_score
        
        return personalized
    
    def _personalize_practice(self, practice: Dict[str, Any], 
                            preferences: UserPreferences) -> Dict[str, Any]:
        """Apply personalization to a single practice."""
        # Copy practice to avoid mutation
        personalized = practice.copy()
        
        # Get base score
        base_score = practice.get('score', 50)
        adjustments = []
        
        # Apply category preference
        if self.config.enable_category_personalization:
            category = practice.get('category', 'general')
            if category in preferences.practice_category_weights:
                weight = preferences.practice_category_weights[category]
                # Convert weight to adjustment
                if weight > 0.5:
                    adjustment = (weight - 0.5) * 2 * self.config.max_score_boost
                else:
                    adjustment = (weight - 0.5) * 2 * self.config.max_score_penalty
                
                adjustments.append({
                    'type': 'category_preference',
                    'value': adjustment,
                    'reason': f"Category preference for {category}: {weight:.0%}"
                })
        
        # Apply severity preference
        if self.config.enable_severity_personalization:
            severity = practice.get('severity', 'recommended')
            if severity in preferences.severity_preferences:
                severity_weight = preferences.severity_preferences[severity]
                # Higher severity weight = boost critical items more
                adjustment = (severity_weight - 0.7) * self.config.max_score_boost * 0.5
                
                adjustments.append({
                    'type': 'severity_preference', 
                    'value': adjustment,
                    'reason': f"Severity weighting for {severity}"
                })
        
        # Apply effort preference
        if self.config.enable_effort_personalization:
            effort = practice.get('effort', 'medium').lower()
            if effort in preferences.effort_preferences:
                effort_weight = preferences.effort_preferences[effort]
                adjustment = (effort_weight - 0.5) * self.config.max_score_boost
                
                adjustments.append({
                    'type': 'effort_preference',
                    'value': adjustment,
                    'reason': f"Effort preference for {effort}: {effort_weight:.0%}"
                })
        
        # Apply framework preference if available
        frameworks = practice.get('frameworks', [])
        if frameworks and preferences.framework_preferences:
            for framework in frameworks:
                if framework in preferences.framework_preferences:
                    fw_weight = preferences.framework_preferences[framework]
                    adjustment = (fw_weight - 0.5) * self.config.max_score_boost * 0.3
                    
                    adjustments.append({
                        'type': 'framework_preference',
                        'value': adjustment,
                        'reason': f"Framework preference for {framework}"
                    })
                    break  # Only apply first matching framework
        
        # Calculate final personalized score
        total_adjustment = sum(adj['value'] for adj in adjustments)
        
        # Apply personalization strength
        weighted_adjustment = total_adjustment * self.config.personalization_strength
        
        # Apply confidence-based dampening
        confidence_factor = preferences.confidence_score
        final_adjustment = weighted_adjustment * confidence_factor
        
        # Calculate final score (bounded 0-100)
        personalized_score = max(0, min(100, base_score + final_adjustment * 100))
        
        # Add personalization metadata
        personalized['personalized_score'] = personalized_score
        personalized['personalization_applied'] = True
        personalized['personalization_adjustments'] = adjustments
        personalized['personalization_delta'] = personalized_score - base_score
        
        return personalized
    
    def explain_personalization(self, recommendation: Dict[str, Any]) -> str:
        """
        Generate human-readable explanation of personalization.
        
        Args:
            recommendation: Personalized recommendation
            
        Returns:
            Explanation text
        """
        if not recommendation.get('personalization_applied'):
            return "No personalization applied."
        
        adjustments = recommendation.get('personalization_adjustments', [])
        delta = recommendation.get('personalization_delta', 0)
        
        if not adjustments:
            return "Personalized based on your preferences."
        
        explanation_parts = ["Personalization factors:"]
        
        for adj in adjustments:
            reason = adj.get('reason', '')
            value = adj.get('value', 0)
            direction = "↑" if value > 0 else "↓"
            explanation_parts.append(f"  {direction} {reason}")
        
        if delta > 0:
            explanation_parts.append(f"\nOverall: Boosted by {delta:.0f} points")
        elif delta < 0:
            explanation_parts.append(f"\nOverall: Reduced by {abs(delta):.0f} points")
        else:
            explanation_parts.append("\nOverall: No net change")
        
        return "\n".join(explanation_parts)
    
    def _record_personalization_event(self, 
                                    rec_type: str, 
                                    count: int,
                                    confidence: float) -> None:
        """Record personalization application in DCP."""
        if not self.dcp_manager:
            return
        
        try:
            observation = {
                "type": "personalization_applied",
                "priority": 30,
                "details": {
                    "recommendation_type": rec_type,
                    "recommendation_count": count,
                    "confidence_score": confidence,
                    "personalization_strength": self.config.personalization_strength,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
            self.dcp_manager.add_observation(observation)
            logger.info(f"Recorded personalization event for {count} {rec_type}")
            
        except Exception as e:
            logger.error(f"Failed to record personalization: {e}")
    
    def get_personalization_stats(self, user_id: str = "default") -> Dict[str, Any]:
        """Get statistics about personalization performance."""
        preferences = self.learner.learn_from_feedback(user_id)
        
        stats = {
            'user_id': user_id,
            'personalization_enabled': self._should_personalize(preferences),
            'confidence_score': preferences.confidence_score,
            'feedback_count': preferences.feedback_count,
            'config': {
                'strength': self.config.personalization_strength,
                'min_confidence': self.config.min_confidence_threshold,
                'max_boost': self.config.max_score_boost,
                'max_penalty': self.config.max_score_penalty
            },
            'active_preferences': {
                'capabilities': len(preferences.capability_weights),
                'categories': len(preferences.practice_category_weights),
                'frameworks': len(preferences.framework_preferences)
            }
        }
        
        return stats