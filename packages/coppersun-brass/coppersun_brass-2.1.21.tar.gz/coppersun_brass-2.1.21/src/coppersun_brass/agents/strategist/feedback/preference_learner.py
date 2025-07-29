"""
PreferenceLearner: Learns user preferences from feedback patterns.

This component implements:
- Temporal decay weighting for recent feedback
- Minimum data threshold before enabling personalization
- Preference aggregation from multiple feedback types
- Confidence scoring based on data volume
- DCP metadata updates for preference persistence
"""

import logging
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from pathlib import Path

# DCP integration
try:
    from coppersun_brass.core.context.dcp_manager import DCPManager
    DCP_AVAILABLE = True
except ImportError:
    DCP_AVAILABLE = False
    DCPManager = None

logger = logging.getLogger(__name__)


@dataclass
class UserPreferences:
    """Learned user preferences."""
    user_id: str
    
    # Capability preferences (0-1 weight for each)
    capability_weights: Dict[str, float] = field(default_factory=dict)
    
    # Practice category preferences
    practice_category_weights: Dict[str, float] = field(default_factory=dict)
    
    # Severity preferences
    severity_preferences: Dict[str, float] = field(default_factory=lambda: {
        'critical': 1.0,
        'important': 0.7,
        'recommended': 0.4
    })
    
    # Framework preferences
    framework_preferences: Dict[str, float] = field(default_factory=dict)
    
    # Effort preferences
    effort_preferences: Dict[str, float] = field(default_factory=lambda: {
        'small': 0.8,
        'medium': 0.5,
        'large': 0.3
    })
    
    # Metadata
    feedback_count: int = 0
    last_updated: Optional[datetime] = None
    confidence_score: float = 0.0
    
    # Team overrides (if set, these take precedence)
    team_overrides: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataThresholdGuard:
    """Ensures sufficient data before enabling personalization."""
    minimum_feedback_count: int = 5
    minimum_rating_count: int = 3
    minimum_adoption_count: int = 2
    confidence_growth_rate: float = 0.15  # How fast confidence grows with data
    
    def has_sufficient_data(self, feedback_count: int, 
                          rating_count: int = 0, 
                          adoption_count: int = 0) -> bool:
        """Check if we have enough data for personalization."""
        return (feedback_count >= self.minimum_feedback_count and
                (rating_count >= self.minimum_rating_count or 
                 adoption_count >= self.minimum_adoption_count))
    
    def calculate_confidence(self, feedback_count: int) -> float:
        """
        Calculate confidence score based on data volume.
        Uses logarithmic growth to cap at 1.0.
        """
        if feedback_count < self.minimum_feedback_count:
            return 0.0
        
        # Logarithmic growth: confidence = 1 - e^(-rate * count)
        confidence = 1.0 - math.exp(-self.confidence_growth_rate * feedback_count)
        return min(confidence, 1.0)


class PreferenceLearner:
    """
    Learns and updates user preferences from feedback patterns.
    
    Features:
    - Temporal decay for recent feedback emphasis
    - Minimum data requirements
    - Multi-signal aggregation (ratings, adoption, usage)
    - DCP persistence
    - Team override support
    """
    
    def __init__(self, 
                 dcp_path: Optional[str] = None,
                 decay_halflife_days: int = 30,
                 data_threshold: Optional[DataThresholdGuard] = None):
        """
        Initialize learner.
        
        Args:
            dcp_path: Path to DCP file/directory
            decay_halflife_days: Half-life for temporal decay
            data_threshold: Data requirements (default: standard thresholds)
        """
        self.dcp_manager = None
        if DCP_AVAILABLE and dcp_path:
            try:
                # DCPManager expects project root directory
                if dcp_path.endswith('.json'):
                    project_root = str(Path(dcp_path).parent)
                else:
                    project_root = dcp_path
                self.dcp_manager = DCPManager(project_root)
                logger.info("PreferenceLearner: DCP integration enabled")
            except Exception as e:
                logger.warning(f"PreferenceLearner: DCP unavailable: {e}")
        
        self.decay_halflife = timedelta(days=decay_halflife_days)
        self.data_guard = data_threshold or DataThresholdGuard()
        self._preferences_cache = {}
    
    def learn_from_feedback(self, user_id: str = "default") -> UserPreferences:
        """
        Learn preferences from all available feedback.
        
        Args:
            user_id: User identifier (default for single-user)
            
        Returns:
            Learned preferences or defaults if insufficient data
        """
        if not self.dcp_manager:
            return UserPreferences(user_id=user_id)
        
        try:
            # Load existing preferences
            preferences = self._load_preferences(user_id)
            
            # Get recent feedback
            feedback_entries = self._get_recent_feedback()
            
            if not feedback_entries:
                return preferences
            
            # Count feedback types
            rating_count = sum(1 for f in feedback_entries if f.get('rating'))
            adoption_count = sum(1 for f in feedback_entries if f.get('adoption_status'))
            
            # Check data threshold
            if not self.data_guard.has_sufficient_data(
                len(feedback_entries), rating_count, adoption_count
            ):
                logger.info(f"Insufficient data for personalization: "
                           f"{len(feedback_entries)} feedback entries")
                return preferences
            
            # Aggregate preferences from feedback
            self._aggregate_capability_preferences(preferences, feedback_entries)
            self._aggregate_category_preferences(preferences, feedback_entries)
            self._aggregate_severity_preferences(preferences, feedback_entries)
            self._aggregate_effort_preferences(preferences, feedback_entries)
            
            # Update metadata
            preferences.feedback_count = len(feedback_entries)
            preferences.last_updated = datetime.now(timezone.utc)
            preferences.confidence_score = self.data_guard.calculate_confidence(
                len(feedback_entries)
            )
            
            # Save to DCP
            self._save_preferences(preferences)
            
            return preferences
            
        except Exception as e:
            logger.error(f"Failed to learn preferences: {e}")
            return UserPreferences(user_id=user_id)
    
    def _load_preferences(self, user_id: str) -> UserPreferences:
        """Load existing preferences from DCP."""
        if not self.dcp_manager:
            return UserPreferences(user_id=user_id)
        
        try:
            dcp_data = self.dcp_manager.read_dcp()
            if not dcp_data:
                return UserPreferences(user_id=user_id)
            
            # Get user preferences from metadata
            meta = dcp_data.get('meta', {})
            user_prefs = meta.get('user_preferences', {})
            
            if not user_prefs:
                return UserPreferences(user_id=user_id)
            
            # Reconstruct preferences
            preferences = UserPreferences(
                user_id=user_id,
                capability_weights=user_prefs.get('capability_weights', {}),
                practice_category_weights=user_prefs.get('practice_category_weights', {}),
                severity_preferences=user_prefs.get('severity_preferences', {
                    'critical': 1.0,
                    'important': 0.7,
                    'recommended': 0.4
                }),
                framework_preferences=user_prefs.get('framework_preferences', {}),
                effort_preferences=user_prefs.get('effort_preferences', {
                    'small': 0.8,
                    'medium': 0.5,
                    'large': 0.3
                }),
                feedback_count=user_prefs.get('feedback_count', 0),
                confidence_score=user_prefs.get('confidence_score', 0.0),
                team_overrides=user_prefs.get('team_overrides', {})
            )
            
            if user_prefs.get('last_updated'):
                preferences.last_updated = datetime.fromisoformat(
                    user_prefs['last_updated'].replace('Z', '+00:00')
                )
            
            return preferences
            
        except Exception as e:
            logger.error(f"Failed to load preferences: {e}")
            return UserPreferences(user_id=user_id)
    
    def _save_preferences(self, preferences: UserPreferences) -> None:
        """Save preferences to DCP metadata."""
        if not self.dcp_manager:
            return
        
        try:
            # Convert to dict
            prefs_dict = {
                'capability_weights': preferences.capability_weights,
                'practice_category_weights': preferences.practice_category_weights,
                'severity_preferences': preferences.severity_preferences,
                'framework_preferences': preferences.framework_preferences,
                'effort_preferences': preferences.effort_preferences,
                'feedback_count': preferences.feedback_count,
                'confidence_score': preferences.confidence_score,
                'team_overrides': preferences.team_overrides,
                'last_updated': preferences.last_updated.isoformat() if preferences.last_updated else None
            }
            
            # Update metadata
            updates = {'user_preferences': prefs_dict}
            self.dcp_manager.update_metadata(updates)
            
            logger.info(f"Saved preferences for user {preferences.user_id}")
            
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")
    
    def _get_recent_feedback(self, days: int = 90) -> List[Dict]:
        """Get recent feedback entries from DCP."""
        if not self.dcp_manager:
            return []
        
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            
            observations = self.dcp_manager.get_observations({
                'type': 'feedback_entry',
                'since': cutoff
            })
            
            # Extract feedback details
            feedback_entries = []
            for obs in observations:
                details = obs.get('details', {})
                if details:
                    # Add creation time for decay calculation
                    details['created_at'] = obs.get('created_at')
                    feedback_entries.append(details)
            
            return feedback_entries
            
        except Exception as e:
            logger.error(f"Failed to get feedback: {e}")
            return []
    
    def _calculate_time_weight(self, feedback_time: str) -> float:
        """
        Calculate temporal decay weight for feedback.
        
        Uses exponential decay: weight = e^(-λt)
        where λ = ln(2) / half_life
        """
        try:
            feedback_dt = datetime.fromisoformat(feedback_time.replace('Z', '+00:00'))
            age = datetime.now(timezone.utc) - feedback_dt
            
            # Calculate decay constant
            decay_constant = math.log(2) / self.decay_halflife.total_seconds()
            
            # Calculate weight
            weight = math.exp(-decay_constant * age.total_seconds())
            
            return weight
            
        except Exception:
            return 0.5  # Default weight if parsing fails
    
    def _aggregate_capability_preferences(self, 
                                        preferences: UserPreferences,
                                        feedback_entries: List[Dict]) -> None:
        """Aggregate capability preferences from gap feedback."""
        capability_scores = defaultdict(list)
        
        for feedback in feedback_entries:
            if feedback.get('recommendation_type') != 'gap':
                continue
            
            capability = feedback.get('recommendation_id', '')
            if not capability:
                continue
            
            # Calculate feedback score
            score = 0.0
            weight = self._calculate_time_weight(feedback.get('created_at', ''))
            
            # Rating feedback
            if feedback.get('rating'):
                # 5-star -> 1.0, 1-star -> 0.0
                score = (feedback['rating'] - 1) / 4.0
                capability_scores[capability].append((score, weight))
            
            # Adoption feedback
            if feedback.get('adoption_status'):
                status = feedback['adoption_status']
                if status == 'adopted':
                    score = 1.0
                elif status == 'deferred':
                    score = 0.5
                elif status == 'rejected':
                    score = 0.0
                capability_scores[capability].append((score, weight))
        
        # Calculate weighted averages
        for capability, scores in capability_scores.items():
            if scores:
                weighted_sum = sum(score * weight for score, weight in scores)
                weight_sum = sum(weight for _, weight in scores)
                if weight_sum > 0:
                    preferences.capability_weights[capability] = weighted_sum / weight_sum
    
    def _aggregate_category_preferences(self,
                                      preferences: UserPreferences,
                                      feedback_entries: List[Dict]) -> None:
        """Aggregate practice category preferences."""
        category_scores = defaultdict(list)
        
        for feedback in feedback_entries:
            if feedback.get('recommendation_type') != 'practice':
                continue
            
            # Would need practice details to get category
            # For now, track by practice ID patterns
            practice_id = feedback.get('recommendation_id', '')
            
            # Extract category from practice ID if available
            # e.g., "security_auth" -> "security"
            if '_' in practice_id:
                category = practice_id.split('_')[0]
                
                score = 0.0
                weight = self._calculate_time_weight(feedback.get('created_at', ''))
                
                if feedback.get('rating'):
                    score = (feedback['rating'] - 1) / 4.0
                    category_scores[category].append((score, weight))
                
                if feedback.get('adoption_status'):
                    status = feedback['adoption_status']
                    if status == 'adopted':
                        score = 1.0
                    elif status == 'partial':
                        score = 0.7
                    elif status == 'deferred':
                        score = 0.3
                    elif status == 'rejected':
                        score = 0.0
                    category_scores[category].append((score, weight))
        
        # Calculate weighted averages
        for category, scores in category_scores.items():
            if scores:
                weighted_sum = sum(score * weight for score, weight in scores)
                weight_sum = sum(weight for _, weight in scores)
                if weight_sum > 0:
                    preferences.practice_category_weights[category] = weighted_sum / weight_sum
    
    def _aggregate_severity_preferences(self,
                                      preferences: UserPreferences,
                                      feedback_entries: List[Dict]) -> None:
        """Learn severity preferences from feedback patterns."""
        # For now, keep defaults
        # Could analyze which severity levels get higher ratings/adoption
        pass
    
    def _aggregate_effort_preferences(self,
                                    preferences: UserPreferences,
                                    feedback_entries: List[Dict]) -> None:
        """Learn effort preferences from adoption patterns."""
        # For now, keep defaults
        # Could analyze which effort levels get adopted more
        pass
    
    def get_preference_summary(self, user_id: str = "default") -> Dict[str, Any]:
        """Get human-readable preference summary."""
        preferences = self.learn_from_feedback(user_id)
        
        # Sort capabilities by weight
        top_capabilities = sorted(
            preferences.capability_weights.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Sort categories by weight
        top_categories = sorted(
            preferences.practice_category_weights.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        summary = {
            'user_id': user_id,
            'confidence_score': preferences.confidence_score,
            'feedback_count': preferences.feedback_count,
            'last_updated': preferences.last_updated.isoformat() if preferences.last_updated else None,
            'personalization_enabled': preferences.confidence_score > 0,
            'top_capability_preferences': [
                {'capability': cap, 'weight': weight}
                for cap, weight in top_capabilities
            ],
            'top_category_preferences': [
                {'category': cat, 'weight': weight}
                for cat, weight in top_categories
            ],
            'effort_preferences': preferences.effort_preferences,
            'severity_preferences': preferences.severity_preferences
        }
        
        return summary