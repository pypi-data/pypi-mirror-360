"""
FeedbackCollector: Captures user feedback on recommendations and practices.

This component implements:
- Implicit feedback (command usage, time spent)
- Explicit feedback (ratings, adoption status)
- Feedback verification and validation
- DCP integration for persistence
"""

import logging
import hashlib
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path

# DCP integration
try:
    from coppersun_brass.core.context.dcp_manager import DCPManager
    DCP_AVAILABLE = True
except ImportError:
    DCP_AVAILABLE = False
    DCPManager = None

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Types of feedback that can be collected."""
    RATING = "rating"               # 1-5 star rating
    ADOPTION = "adoption"           # Adopted/rejected/deferred
    COMMAND_USAGE = "command_usage" # Implicit from CLI usage
    TIME_SPENT = "time_spent"       # Time viewing recommendation
    COMMENT = "comment"             # Free text feedback


class AdoptionStatus(Enum):
    """Status of practice adoption."""
    ADOPTED = "adopted"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    PARTIAL = "partial"


@dataclass
class FeedbackEntry:
    """A single feedback entry."""
    feedback_id: str
    recommendation_id: str          # Gap or practice ID
    recommendation_type: str        # 'gap' or 'practice'
    feedback_type: FeedbackType
    timestamp: datetime
    
    # Feedback data
    rating: Optional[int] = None                    # 1-5
    adoption_status: Optional[AdoptionStatus] = None
    time_spent_seconds: Optional[float] = None
    comment: Optional[str] = None
    
    # Context
    command_context: Optional[str] = None           # Which command generated this
    session_id: Optional[str] = None                # For grouping feedback
    
    # Metadata
    confidence: float = 1.0                         # Confidence in this feedback
    validated: bool = False                         # Has been verified
    

@dataclass 
class RecommendationRegistry:
    """Registry of valid recommendations for verification."""
    gap_hashes: Dict[str, str] = field(default_factory=dict)
    practice_hashes: Dict[str, str] = field(default_factory=dict)
    last_updated: Optional[datetime] = None
    
    def add_gap(self, gap_id: str, gap_data: Dict) -> str:
        """Add a gap to registry and return hash."""
        content = json.dumps(gap_data, sort_keys=True)
        hash_value = hashlib.sha256(content.encode()).hexdigest()[:16]
        self.gap_hashes[gap_id] = hash_value
        self.last_updated = datetime.now(timezone.utc)
        return hash_value
    
    def add_practice(self, practice_id: str, practice_data: Dict) -> str:
        """Add a practice to registry and return hash."""
        content = json.dumps(practice_data, sort_keys=True)
        hash_value = hashlib.sha256(content.encode()).hexdigest()[:16]
        self.practice_hashes[practice_id] = hash_value
        self.last_updated = datetime.now(timezone.utc)
        return hash_value
    
    def validate_recommendation(self, rec_id: str, rec_type: str) -> bool:
        """Validate that a recommendation ID exists."""
        if rec_type == "gap":
            return rec_id in self.gap_hashes
        elif rec_type == "practice":
            return rec_id in self.practice_hashes
        return False
    
    def get_hash(self, rec_id: str, rec_type: str) -> Optional[str]:
        """Get hash for a recommendation."""
        if rec_type == "gap":
            return self.gap_hashes.get(rec_id)
        elif rec_type == "practice":
            return self.practice_hashes.get(rec_id)
        return None


class FeedbackCollector:
    """
    Collects and validates user feedback on recommendations.
    
    Features:
    - Multiple feedback types (rating, adoption, usage)
    - Verification against recommendation registry
    - DCP persistence
    - Feedback aggregation
    - Old feedback pruning
    """
    
    def __init__(self, dcp_path: Optional[str] = None):
        """Initialize collector with optional DCP integration."""
        self.dcp_manager = None
        if DCP_AVAILABLE and dcp_path:
            try:
                # DCPManager expects project root directory
                dcp_path_obj = Path(dcp_path)
                if dcp_path_obj.name == '.brass':
                    # If passed .brass directory, use parent as project root
                    project_root = str(dcp_path_obj.parent)
                elif dcp_path.endswith('.json'):
                    project_root = str(dcp_path_obj.parent)
                else:
                    project_root = dcp_path
                self.dcp_manager = DCPManager(project_root)
                logger.info("FeedbackCollector: DCP integration enabled")
            except Exception as e:
                logger.warning(f"FeedbackCollector: DCP unavailable: {e}")
        
        self.registry = self._load_registry()
        self._session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _load_registry(self) -> RecommendationRegistry:
        """Load recommendation registry from DCP."""
        if not self.dcp_manager:
            return RecommendationRegistry()
        
        try:
            # Look for registry in DCP observations
            observations = self.dcp_manager.get_observations({
                'type': 'recommendation_registry'
            })
            
            if observations:
                # Get most recent registry
                latest = max(observations, key=lambda x: x.get('created_at', ''))
                details = latest.get('details', {})
                
                registry = RecommendationRegistry(
                    gap_hashes=details.get('gap_hashes', {}),
                    practice_hashes=details.get('practice_hashes', {}),
                    last_updated=datetime.fromisoformat(
                        latest.get('created_at', '').replace('Z', '+00:00')
                    )
                )
                
                logger.info(f"Loaded registry with {len(registry.gap_hashes)} gaps, "
                           f"{len(registry.practice_hashes)} practices")
                return registry
                
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
        
        return RecommendationRegistry()
    
    def update_registry_from_analysis(self, analysis_data: Dict) -> None:
        """Update registry when new analysis is run."""
        # Extract gaps
        gaps = analysis_data.get('gaps', {}).get('top_actions', [])
        for gap in gaps:
            gap_id = gap.get('capability', 'unknown')
            self.registry.add_gap(gap_id, gap)
        
        # Extract practices  
        practices = analysis_data.get('practices', {}).get('recommendations', [])
        for practice in practices:
            practice_id = practice.get('id', 'unknown')
            self.registry.add_practice(practice_id, practice)
        
        # Save registry to DCP
        if self.dcp_manager:
            self._save_registry()
    
    def _save_registry(self) -> None:
        """Save registry to DCP."""
        if not self.dcp_manager:
            return
        
        try:
            observation = {
                'type': 'recommendation_registry',
                'priority': 30,
                'summary': f"Recommendation registry: {len(self.registry.gap_hashes)} gaps, "
                          f"{len(self.registry.practice_hashes)} practices",
                'details': {
                    'gap_hashes': self.registry.gap_hashes,
                    'practice_hashes': self.registry.practice_hashes,
                    'last_updated': self.registry.last_updated.isoformat() if self.registry.last_updated else None
                }
            }
            
            self.dcp_manager.add_observation(observation, 'feedback_collector')
            logger.info("Saved recommendation registry to DCP")
            
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")
    
    def collect_rating(self, 
                      recommendation_id: str,
                      recommendation_type: str,
                      rating: int,
                      comment: Optional[str] = None,
                      command_context: Optional[str] = None) -> Tuple[bool, str]:
        """
        Collect rating feedback.
        
        Args:
            recommendation_id: ID of gap or practice
            recommendation_type: 'gap' or 'practice' 
            rating: 1-5 star rating
            comment: Optional text feedback
            command_context: Which command showed this recommendation
            
        Returns:
            Tuple of (success, message)
        """
        # Validate rating
        if not 1 <= rating <= 5:
            return False, "Rating must be between 1 and 5"
        
        # Verify recommendation exists
        if not self.registry.validate_recommendation(recommendation_id, recommendation_type):
            return False, f"Invalid {recommendation_type} ID: {recommendation_id}"
        
        # Create feedback entry
        feedback = FeedbackEntry(
            feedback_id=f"rating_{recommendation_id}_{int(datetime.now().timestamp())}",
            recommendation_id=recommendation_id,
            recommendation_type=recommendation_type,
            feedback_type=FeedbackType.RATING,
            timestamp=datetime.now(timezone.utc),
            rating=rating,
            comment=comment,
            command_context=command_context,
            session_id=self._session_id,
            validated=True
        )
        
        # Save to DCP
        if self.dcp_manager:
            self._save_feedback(feedback)
        
        return True, f"Rating {rating}/5 recorded for {recommendation_type} '{recommendation_id}'"
    
    def collect_adoption(self,
                        recommendation_id: str,
                        recommendation_type: str,
                        status: AdoptionStatus,
                        comment: Optional[str] = None) -> Tuple[bool, str]:
        """
        Collect adoption status feedback.
        
        Args:
            recommendation_id: ID of gap or practice
            recommendation_type: 'gap' or 'practice'
            status: Adoption status
            comment: Optional reason
            
        Returns:
            Tuple of (success, message)
        """
        # Verify recommendation exists
        if not self.registry.validate_recommendation(recommendation_id, recommendation_type):
            return False, f"Invalid {recommendation_type} ID: {recommendation_id}"
        
        # Create feedback entry
        feedback = FeedbackEntry(
            feedback_id=f"adoption_{recommendation_id}_{int(datetime.now().timestamp())}",
            recommendation_id=recommendation_id,
            recommendation_type=recommendation_type,
            feedback_type=FeedbackType.ADOPTION,
            timestamp=datetime.now(timezone.utc),
            adoption_status=status,
            comment=comment,
            session_id=self._session_id,
            validated=True
        )
        
        # Save to DCP
        if self.dcp_manager:
            self._save_feedback(feedback)
        
        return True, f"Adoption status '{status.value}' recorded for {recommendation_type} '{recommendation_id}'"
    
    def collect_implicit(self,
                        recommendation_id: str,
                        recommendation_type: str,
                        command: str,
                        time_spent: Optional[float] = None) -> None:
        """
        Collect implicit feedback from command usage.
        
        Args:
            recommendation_id: ID of gap or practice
            recommendation_type: 'gap' or 'practice'
            command: Command that was run
            time_spent: Time spent viewing (seconds)
        """
        # Skip if invalid recommendation
        if not self.registry.validate_recommendation(recommendation_id, recommendation_type):
            return
        
        # Create feedback entry
        feedback = FeedbackEntry(
            feedback_id=f"usage_{recommendation_id}_{int(datetime.now().timestamp())}",
            recommendation_id=recommendation_id,
            recommendation_type=recommendation_type,
            feedback_type=FeedbackType.COMMAND_USAGE,
            timestamp=datetime.now(timezone.utc),
            command_context=command,
            time_spent_seconds=time_spent,
            session_id=self._session_id,
            confidence=0.5,  # Lower confidence for implicit
            validated=True
        )
        
        # Save to DCP
        if self.dcp_manager:
            self._save_feedback(feedback)
    
    def _save_feedback(self, feedback: FeedbackEntry) -> None:
        """Save feedback entry to DCP."""
        if not self.dcp_manager:
            return
        
        try:
            # Convert feedback to dict
            feedback_dict = asdict(feedback)
            
            # Convert enums
            feedback_dict['feedback_type'] = feedback.feedback_type.value
            if feedback.adoption_status:
                feedback_dict['adoption_status'] = feedback.adoption_status.value
            
            # Convert datetime
            feedback_dict['timestamp'] = feedback.timestamp.isoformat()
            
            observation = {
                'type': 'feedback_entry',
                'priority': 50,
                'summary': f"User feedback: {feedback.feedback_type.value} for "
                          f"{feedback.recommendation_type} '{feedback.recommendation_id}'",
                'details': feedback_dict
            }
            
            self.dcp_manager.add_observation(observation, 'feedback_collector')
            logger.info(f"Saved feedback {feedback.feedback_id} to DCP")
            
        except Exception as e:
            logger.error(f"Failed to save feedback: {e}")
    
    def get_feedback_summary(self, 
                           recommendation_id: Optional[str] = None,
                           days: int = 30) -> Dict[str, Any]:
        """
        Get summary of feedback.
        
        Args:
            recommendation_id: Filter by specific recommendation
            days: Look back period
            
        Returns:
            Summary statistics
        """
        if not self.dcp_manager:
            return {"error": "DCP not available"}
        
        try:
            # Calculate cutoff time
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Get feedback observations
            observations = self.dcp_manager.get_observations({
                'type': 'feedback_entry',
                'since': cutoff
            })
            
            # Filter by recommendation if specified
            if recommendation_id:
                observations = [
                    obs for obs in observations
                    if obs.get('details', {}).get('recommendation_id') == recommendation_id
                ]
            
            # Aggregate statistics
            total = len(observations)
            ratings = []
            adoption_counts = {}
            
            for obs in observations:
                details = obs.get('details', {})
                
                # Collect ratings
                if details.get('rating'):
                    ratings.append(details['rating'])
                
                # Count adoption statuses
                if details.get('adoption_status'):
                    status = details['adoption_status']
                    adoption_counts[status] = adoption_counts.get(status, 0) + 1
            
            summary = {
                'total_feedback': total,
                'time_period_days': days,
                'ratings': {
                    'count': len(ratings),
                    'average': sum(ratings) / len(ratings) if ratings else 0,
                    'distribution': {i: ratings.count(i) for i in range(1, 6)}
                },
                'adoption': adoption_counts,
                'recommendation_id': recommendation_id
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get feedback summary: {e}")
            return {"error": str(e)}
    
    def prune_old_feedback(self, days_to_keep: int = 90) -> int:
        """
        Remove old feedback to prevent token bloat.
        
        Args:
            days_to_keep: Keep feedback newer than this
            
        Returns:
            Number of entries removed
        """
        if not self.dcp_manager:
            return 0
        
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
            
            # Get old feedback
            observations = self.dcp_manager.get_observations({'type': 'feedback_entry'})
            
            removed = 0
            for obs in observations:
                created = datetime.fromisoformat(
                    obs.get('created_at', '').replace('Z', '+00:00')
                )
                if created < cutoff:
                    if self.dcp_manager.remove_observation(obs['id']):
                        removed += 1
            
            if removed > 0:
                logger.info(f"Pruned {removed} old feedback entries")
            
            return removed
            
        except Exception as e:
            logger.error(f"Failed to prune feedback: {e}")
            return 0