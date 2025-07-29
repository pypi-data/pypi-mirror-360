"""
Pattern Conflict Resolver

General Staff G3 Function: Operational Conflict Resolution
Resolves contradictory patterns through weighted scoring
"""

import math
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
import logging

from coppersun_brass.core.learning.models import LearnedPattern
from coppersun_brass.core.context.dcp_manager import DCPManager
from .dcp_helpers import get_dcp_section, update_dcp_section

logger = logging.getLogger(__name__)

class PatternConflictResolver:
    """
    Resolves conflicts between contradictory patterns
    
    General Staff G3 Function: Operational Conflict Resolution
    This component resolves pattern conflicts and stores resolutions in DCP
    to maintain consistent decision-making across AI commander sessions.
    """
    
    def __init__(self, dcp_path: Optional[str] = None, half_life_days: int = 90):
        """
        Initialize conflict resolver with MANDATORY DCP integration
        
        Args:
            dcp_path: Path to DCP context file (mandatory per CLAUDE.md)
            half_life_days: Time decay half-life for pattern confidence
        """
        # DCP is MANDATORY - this is how the general staff coordinates
        self.dcp_manager = DCPManager(dcp_path)
        self.half_life_days = half_life_days
        
        # Load previous conflict resolutions
        self._load_resolutions_from_dcp()
    
    def resolve_conflicts(
        self,
        patterns: List[LearnedPattern],
        current_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve conflicts between patterns
        
        Args:
            patterns: List of potentially conflicting patterns
            current_context: Current task context
            
        Returns:
            Resolution dictionary with winning pattern and explanation
        """
        if not patterns:
            return {
                'pattern': None,
                'confidence': 0.0,
                'explanation': 'No patterns available'
            }
        
        if len(patterns) == 1:
            return {
                'pattern': patterns[0],
                'confidence': self._calculate_pattern_score(patterns[0], current_context),
                'explanation': 'Single pattern match'
            }
        
        # Detect conflict groups
        conflict_groups = self._group_conflicts(patterns)
        
        if not conflict_groups:
            # No conflicts, return highest scoring pattern
            scored_patterns = [
                (p, self._calculate_pattern_score(p, current_context))
                for p in patterns
            ]
            scored_patterns.sort(key=lambda x: x[1], reverse=True)
            
            return {
                'pattern': scored_patterns[0][0],
                'confidence': scored_patterns[0][1],
                'explanation': f'Best match from {len(patterns)} non-conflicting patterns'
            }
        
        # Resolve each conflict group
        resolutions = []
        for group in conflict_groups:
            resolution = self._resolve_conflict_group(group, current_context)
            resolutions.append(resolution)
        
        # Return the highest confidence resolution
        best_resolution = max(resolutions, key=lambda r: r['confidence'])
        
        # Store resolution in DCP for future reference
        self._persist_resolution_to_dcp(conflict_groups, best_resolution)
        
        return best_resolution
    
    def _group_conflicts(
        self,
        patterns: List[LearnedPattern]
    ) -> List[List[LearnedPattern]]:
        """Group patterns that conflict with each other"""
        groups = []
        processed = set()
        
        for pattern in patterns:
            if pattern.id in processed:
                continue
            
            # Find all patterns that conflict with this one
            group = [pattern]
            processed.add(pattern.id)
            
            if pattern.conflicts_with:
                for other in patterns:
                    if other.id in pattern.conflicts_with and other.id not in processed:
                        group.append(other)
                        processed.add(other.id)
            
            if len(group) > 1:
                groups.append(group)
        
        return groups
    
    def _resolve_conflict_group(
        self,
        group: List[LearnedPattern],
        current_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve a single conflict group"""
        # Score each pattern
        scores = []
        for pattern in group:
            score = self._calculate_pattern_score(pattern, current_context)
            scores.append((pattern, score))
        
        # Sort by score
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Generate explanation
        explanation = self._generate_explanation(scores, current_context)
        
        return {
            'pattern': scores[0][0],
            'confidence': scores[0][1],
            'explanation': explanation
        }
    
    def _calculate_pattern_score(
        self,
        pattern: LearnedPattern,
        current_context: Dict[str, Any]
    ) -> float:
        """
        Calculate weighted score for a pattern
        
        Factors:
        - Time decay
        - Sample size
        - Context relevance
        - Base confidence
        """
        # Apply time decay
        age_days = 0
        if pattern.last_updated:
            age_days = (datetime.utcnow() - pattern.last_updated).days
        
        time_score = self._time_decay(pattern.confidence, age_days)
        
        # Weight by sample size (logarithmic)
        sample_weight = min(1.0, math.log(pattern.sample_size + 1) / math.log(50))
        
        # Context relevance
        context_score = self._calculate_context_match(pattern, current_context)
        
        # Success rate factor
        success_factor = pattern.success_rate
        
        # Combine factors
        final_score = (
            time_score * 0.3 +
            sample_weight * 0.2 +
            context_score * 0.3 +
            success_factor * 0.2
        )
        
        return min(1.0, final_score)
    
    def _time_decay(
        self,
        score: float,
        age_days: int,
        half_life: Optional[int] = None
    ) -> float:
        """Apply exponential time decay"""
        half_life = half_life or self.half_life_days
        return score * math.exp(-math.log(2) * age_days / half_life)
    
    def _calculate_context_match(
        self,
        pattern: LearnedPattern,
        current_context: Dict[str, Any]
    ) -> float:
        """Calculate how well pattern matches current context"""
        if not pattern.context_dimensions:
            return 0.5  # Universal pattern gets medium score
        
        matches = 0
        total = 0
        
        # Check each dimension
        for key, value in pattern.context_dimensions.items():
            total += 1
            if key in current_context and current_context[key] == value:
                matches += 1
        
        # Additional context dimensions not in pattern reduce score
        extra_dimensions = len(current_context) - total
        if extra_dimensions > 0:
            penalty = extra_dimensions * 0.1
            match_score = (matches / total) if total > 0 else 0
            return max(0, match_score - penalty)
        
        return (matches / total) if total > 0 else 0
    
    def _generate_explanation(
        self,
        scores: List[Tuple[LearnedPattern, float]],
        current_context: Dict[str, Any]
    ) -> str:
        """Generate human-readable explanation for resolution"""
        if not scores:
            return "No patterns to resolve"
        
        winner = scores[0][0]
        winner_score = scores[0][1]
        
        explanation_parts = [
            f"Selected '{winner.pattern_name}' (confidence: {winner_score:.2f})"
        ]
        
        # Explain why it won
        if winner.sample_size > 20:
            explanation_parts.append(f"based on {winner.sample_size} samples")
        
        if winner.success_rate > 0.8:
            explanation_parts.append(f"with {winner.success_rate:.1%} success rate")
        
        # Mention runner-up if close
        if len(scores) > 1:
            runner_up = scores[1][0]
            runner_up_score = scores[1][1]
            if runner_up_score > winner_score * 0.8:
                explanation_parts.append(
                    f"(close alternative: '{runner_up.pattern_name}' at {runner_up_score:.2f})"
                )
        
        # Context match info
        context_match = self._calculate_context_match(winner, current_context)
        if context_match > 0.8:
            explanation_parts.append("with excellent context match")
        elif context_match < 0.5:
            explanation_parts.append("despite limited context match")
        
        return " ".join(explanation_parts)
    
    def get_conflict_summary(
        self,
        patterns: List[LearnedPattern]
    ) -> Dict[str, Any]:
        """
        Get summary of conflicts in pattern set
        
        Returns:
            Summary with conflict groups and resolution strategies
        """
        conflict_groups = self._group_conflicts(patterns)
        
        summary = {
            'total_patterns': len(patterns),
            'conflict_groups': len(conflict_groups),
            'conflicts': []
        }
        
        for group in conflict_groups:
            conflict_info = {
                'patterns': [
                    {
                        'id': p.id,
                        'name': p.pattern_name,
                        'success_rate': p.success_rate,
                        'confidence': p.confidence
                    }
                    for p in group
                ],
                'resolution_strategy': group[0].resolution_strategy or 'weighted'
            }
            summary['conflicts'].append(conflict_info)
        
        return summary

    def _load_resolutions_from_dcp(self) -> None:
        """Load previous conflict resolutions from DCP"""
        try:
            learning_data = get_dcp_section(self.dcp_manager, 'learning', {})
            self.resolution_history = learning_data.get('patterns', {}).get('conflict_resolutions', [])
            
            if self.resolution_history:
                logger.info(f"Loaded {len(self.resolution_history)} conflict resolutions from DCP")
        except Exception as e:
            logger.warning(f"Could not load resolutions from DCP: {e}")
            self.resolution_history = []
    
    def _persist_resolution_to_dcp(
        self,
        conflict_groups: List[List[LearnedPattern]],
        resolution: Dict[str, Any]
    ) -> None:
        """Persist conflict resolution to DCP for future AI sessions"""
        if not conflict_groups or not resolution.get('pattern'):
            return
        
        # Create resolution record
        resolution_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'winning_pattern': {
                'id': resolution['pattern'].id,
                'name': resolution['pattern'].pattern_name,
                'type': resolution['pattern'].pattern_type
            },
            'confidence': resolution['confidence'],
            'explanation': resolution['explanation'],
            'conflict_groups': [
                [{'id': p.id, 'name': p.pattern_name} for p in group]
                for group in conflict_groups
            ]
        }
        
        # Update resolution history
        self.resolution_history.append(resolution_record)
        
        # Keep only recent resolutions (last 100)
        if len(self.resolution_history) > 100:
            self.resolution_history = self.resolution_history[-100:]
        
        # Update DCP
        self.dcp_manager.update_section(
            'learning.patterns.conflict_resolutions',
            self.resolution_history
        )
        
        # Add observation for conflict resolution
        self.dcp_manager.add_observation(
            'pattern_conflict_resolved',
            {
                'winning_pattern_id': resolution['pattern'].id,
                'confidence': resolution['confidence'],
                'num_conflicts': sum(len(group) for group in conflict_groups),
                'resolution_strategy': 'weighted_scoring'
            },
            source_agent='learning_system',
            priority=70  # Important for consistency
        )
        
        logger.info(f"Persisted conflict resolution to DCP: {resolution['pattern'].pattern_name} wins")

# Export main class
__all__ = ['PatternConflictResolver']