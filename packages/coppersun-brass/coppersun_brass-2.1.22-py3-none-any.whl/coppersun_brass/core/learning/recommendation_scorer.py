"""
Recommendation Scorer with Learning Integration

General Staff G3 Function: Operations Enhancement
Applies learned patterns to improve recommendation scoring
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from coppersun_brass.core.learning.pattern_extractor import PatternExtractor
from coppersun_brass.core.learning.pattern_conflict_resolver import PatternConflictResolver
from coppersun_brass.core.learning.ab_testing import RecommendationExperiment
from coppersun_brass.core.learning.models import (
    LearnedPattern, ExperimentVariant, init_db
)
from coppersun_brass.core.context.dcp_manager import DCPManager
from .dcp_helpers import get_dcp_section, update_dcp_section

logger = logging.getLogger(__name__)

class RecommendationScorer:
    """
    Enhances recommendation scores using learned patterns
    
    General Staff G3 Function: Operations Enhancement
    This component applies institutional learning to improve recommendation quality,
    maintaining scoring history and adjustments in DCP for cross-session learning.
    """
    
    def __init__(
        self,
        dcp_path: Optional[str] = None,
        team_id: Optional[str] = None,
        enable_experiments: bool = False,
        experiment_allocation: int = 50
    ):
        """
        Initialize recommendation scorer with MANDATORY DCP integration
        
        Args:
            dcp_path: Path to DCP context file (mandatory per CLAUDE.md)
            team_id: Team identifier for pattern filtering
            enable_experiments: Enable A/B testing
            experiment_allocation: Percentage for test variant
        """
        # DCP is MANDATORY - this is how the general staff coordinates
        self.dcp_manager = DCPManager(dcp_path)
        self.team_id = team_id
        
        # Initialize components with DCP
        self.pattern_extractor = PatternExtractor(dcp_path, team_id)
        self.conflict_resolver = PatternConflictResolver(dcp_path)
        self.experiment = RecommendationExperiment(
            dcp_path=dcp_path,
            enabled=enable_experiments,
            allocation_percentage=experiment_allocation
        )
        self.engine, self.Session = init_db()
        
        # Load scoring history from DCP
        self._load_scoring_history_from_dcp()
    
    def score_recommendation(
        self,
        recommendation: Dict[str, Any],
        context: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Score a recommendation using learned patterns
        
        Args:
            recommendation: Original recommendation
            context: Current task context
            task_id: Optional task ID for experiment tracking
            
        Returns:
            Enhanced recommendation with adjusted scoring
        """
        # Original score
        original_score = recommendation.get('score', 0.5)
        
        # Get experiment variant
        variant = ExperimentVariant.CONTROL
        if task_id and self.experiment.enabled:
            variant = self.experiment.assign_variant(task_id)
        
        # Control group gets original scoring
        if variant == ExperimentVariant.CONTROL:
            return self.experiment.apply_variant_logic(
                recommendation,
                variant
            )
        
        # Test group gets learning-enhanced scoring
        try:
            # Get relevant patterns
            patterns = self.pattern_extractor.get_patterns_for_context(context)
            
            if not patterns:
                logger.debug("No patterns found for context")
                return self.experiment.apply_variant_logic(
                    recommendation,
                    variant
                )
            
            # Resolve conflicts if any
            resolution = self.conflict_resolver.resolve_conflicts(
                patterns,
                context
            )
            
            # Apply pattern-based adjustments
            adjustments = self._calculate_adjustments(
                recommendation,
                resolution['pattern'],
                resolution['confidence']
            )
            
            # Apply adjustments
            enhanced_recommendation = self.experiment.apply_variant_logic(
                recommendation,
                variant,
                adjustments
            )
            
            # Record for experiment tracking
            if task_id:
                adjustment_reason = {
                    'pattern': resolution['pattern'].pattern_name if resolution['pattern'] else None,
                    'confidence': resolution['confidence'],
                    'explanation': resolution['explanation']
                }
                
                self.experiment.record_recommendation(
                    recommendation_id=recommendation.get('id', 'unknown'),
                    task_id=task_id,
                    original_score=original_score,
                    adjusted_score=enhanced_recommendation['score'],
                    variant=variant,
                    adjustment_reason=adjustment_reason
                )
                
                # Persist scoring to DCP for cross-session learning
                self._persist_scoring_to_dcp(
                    recommendation.get('id', 'unknown'),
                    original_score,
                    enhanced_recommendation['score'],
                    resolution['pattern'].pattern_name if resolution['pattern'] else None,
                    adjustment_reason
                )
            
            return enhanced_recommendation
            
        except Exception as e:
            logger.error(f"Failed to apply learning adjustments: {e}")
            # Fallback to original scoring
            return self.experiment.apply_variant_logic(
                recommendation,
                variant
            )
    
    def _calculate_adjustments(
        self,
        recommendation: Dict[str, Any],
        pattern: Optional[LearnedPattern],
        confidence: float
    ) -> Dict[str, Any]:
        """
        Calculate score adjustments based on pattern
        
        Args:
            recommendation: Original recommendation
            pattern: Matched pattern
            confidence: Pattern confidence
            
        Returns:
            Adjustment dictionary
        """
        if not pattern:
            return {'adjustment': 0.0}
        
        adjustments = {
            'pattern_id': pattern.id,
            'pattern_name': pattern.pattern_name,
            'pattern_confidence': confidence,
            'adjustment': 0.0,
            'reasons': []
        }
        
        # Base adjustment from pattern success rate
        base_adjustment = (pattern.success_rate - 0.5) * 0.3  # Max �15%
        
        # Confidence modifier
        confidence_modifier = confidence
        
        # Calculate final adjustment
        final_adjustment = base_adjustment * confidence_modifier
        
        # Apply bounds
        final_adjustment = max(-0.3, min(0.3, final_adjustment))
        
        adjustments['adjustment'] = final_adjustment
        
        # Add reasoning
        if final_adjustment > 0:
            adjustments['reasons'].append(
                f"Pattern '{pattern.pattern_name}' suggests higher success rate"
            )
        elif final_adjustment < 0:
            adjustments['reasons'].append(
                f"Pattern '{pattern.pattern_name}' suggests lower success rate"
            )
        
        # Type-specific adjustments
        if pattern.pattern_type == 'failure_risk' and final_adjustment < -0.1:
            adjustments['warnings'] = [
                f"High failure risk detected: {pattern.description}"
            ]
        
        return adjustments
    
    def batch_score_recommendations(
        self,
        recommendations: List[Dict[str, Any]],
        context: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Score multiple recommendations efficiently
        
        Args:
            recommendations: List of recommendations
            context: Shared context
            task_id: Optional task ID
            
        Returns:
            List of enhanced recommendations
        """
        # Get patterns once for all recommendations
        patterns = self.pattern_extractor.get_patterns_for_context(context)
        
        if not patterns:
            # No patterns, return original scores
            return [
                self.experiment.apply_variant_logic(
                    rec,
                    ExperimentVariant.CONTROL
                )
                for rec in recommendations
            ]
        
        # Resolve conflicts once
        resolution = self.conflict_resolver.resolve_conflicts(
            patterns,
            context
        )
        
        # Score each recommendation
        scored_recommendations = []
        for rec in recommendations:
            # Each recommendation might have slightly different context
            rec_context = {**context, **rec.get('context', {})}
            
            # Check if pattern still applies
            if self._pattern_applies(resolution['pattern'], rec_context):
                adjustments = self._calculate_adjustments(
                    rec,
                    resolution['pattern'],
                    resolution['confidence']
                )
                
                variant = ExperimentVariant.TEST if self.experiment.enabled else ExperimentVariant.CONTROL
                enhanced = self.experiment.apply_variant_logic(
                    rec,
                    variant,
                    adjustments
                )
            else:
                # Pattern doesn't apply to this specific recommendation
                enhanced = self.experiment.apply_variant_logic(
                    rec,
                    ExperimentVariant.CONTROL
                )
            
            scored_recommendations.append(enhanced)
        
        return scored_recommendations
    
    def _pattern_applies(
        self,
        pattern: Optional[LearnedPattern],
        context: Dict[str, Any]
    ) -> bool:
        """Check if pattern applies to specific context"""
        if not pattern or not pattern.context_dimensions:
            return True
        
        for key, value in pattern.context_dimensions.items():
            if key in context and context[key] != value:
                return False
        
        return True
    
    def get_scoring_insights(
        self,
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get insights about scoring performance
        
        Args:
            lookback_days: Days to analyze
            
        Returns:
            Insights dictionary
        """
        insights = {
            'experiment_results': {},
            'pattern_impact': [],
            'recommendations': []
        }
        
        # Get experiment results if enabled
        if self.experiment.enabled:
            insights['experiment_results'] = self.experiment.get_experiment_results(
                lookback_days
            )
        
        # Analyze pattern impact
        session = self.Session()
        try:
            # Get most impactful patterns
            patterns = session.query(LearnedPattern).filter(
                LearnedPattern.confidence >= 0.7
            ).order_by(
                LearnedPattern.sample_size.desc()
            ).limit(10).all()
            
            for pattern in patterns:
                impact = {
                    'pattern_name': pattern.pattern_name,
                    'pattern_type': pattern.pattern_type,
                    'confidence': pattern.confidence,
                    'sample_size': pattern.sample_size,
                    'success_rate': pattern.success_rate,
                    'potential_impact': self._estimate_pattern_impact(pattern)
                }
                insights['pattern_impact'].append(impact)
            
            # Generate recommendations
            if insights['experiment_results']:
                rec = insights['experiment_results'].get('summary', {}).get('recommendation')
                if rec:
                    insights['recommendations'].append(rec)
            
            # Pattern-based recommendations
            high_impact_patterns = [
                p for p in insights['pattern_impact']
                if p['potential_impact'] > 0.1
            ]
            
            if high_impact_patterns:
                insights['recommendations'].append(
                    f"Consider enabling learning system - {len(high_impact_patterns)} "
                    f"high-impact patterns detected"
                )
            
            return insights
            
        finally:
            session.close()
    
    def _estimate_pattern_impact(self, pattern: LearnedPattern) -> float:
        """Estimate potential impact of a pattern"""
        # Simple heuristic: deviation from baseline * confidence * log(samples)
        baseline = 0.5
        deviation = abs(pattern.success_rate - baseline)
        sample_factor = min(1.0, pattern.sample_size / 100)
        
        return deviation * pattern.confidence * sample_factor
    
    def update_outcome(
        self,
        recommendation_id: str,
        was_accepted: bool,
        outcome_status: Optional[str] = None
    ) -> bool:
        """
        Update recommendation outcome for learning
        
        Args:
            recommendation_id: Recommendation identifier
            was_accepted: Whether recommendation was accepted
            outcome_status: Final outcome status
            
        Returns:
            Success boolean
        """
        success = self.experiment.update_outcome(
            recommendation_id,
            was_accepted,
            outcome_status
        )
        
        # Log outcome to DCP for learning
        if success:
            self._persist_outcome_to_dcp(recommendation_id, was_accepted, outcome_status)
        
        return success

    def _load_scoring_history_from_dcp(self) -> None:
        """Load scoring adjustment history from DCP"""
        try:
            learning_data = get_dcp_section(self.dcp_manager, 'learning', {})
            self.scoring_history = learning_data.get('scoring', {}).get('history', [])
            
            if self.scoring_history:
                logger.info(f"Loaded {len(self.scoring_history)} scoring records from DCP")
        except Exception as e:
            logger.warning(f"Could not load scoring history from DCP: {e}")
            self.scoring_history = []
    
    def _persist_scoring_to_dcp(
        self,
        recommendation_id: str,
        original_score: float,
        adjusted_score: float,
        pattern_used: Optional[str] = None,
        adjustment_reason: Optional[Dict[str, Any]] = None
    ) -> None:
        """Persist scoring adjustment to DCP for future AI sessions"""
        scoring_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'recommendation_id': recommendation_id,
            'original_score': float(original_score),
            'adjusted_score': float(adjusted_score),
            'adjustment': float(adjusted_score - original_score),
            'pattern_used': pattern_used,
            'reason': adjustment_reason,
            'team_id': self.team_id
        }
        
        # Add to history
        self.scoring_history.append(scoring_record)
        
        # Keep only recent history (last 1000 records)
        if len(self.scoring_history) > 1000:
            self.scoring_history = self.scoring_history[-1000:]
        
        # Update DCP
        self.dcp_manager.update_section('learning.scoring.history', self.scoring_history)
        
        # Add observation for significant adjustments
        if abs(adjusted_score - original_score) > 0.1:
            self.dcp_manager.add_observation(
                'significant_score_adjustment',
                {
                    'recommendation_id': recommendation_id,
                    'adjustment': float(adjusted_score - original_score),
                    'pattern': pattern_used,
                    'confidence': adjustment_reason.get('confidence', 0) if adjustment_reason else 0
                },
                source_agent='learning_system',
                priority=75  # Notable for learning insights
            )
    
    def _persist_outcome_to_dcp(
        self,
        recommendation_id: str,
        was_accepted: bool,
        outcome_status: Optional[str] = None
    ) -> None:
        """Persist recommendation outcome to DCP"""
        self.dcp_manager.add_observation(
            'recommendation_outcome',
            {
                'recommendation_id': recommendation_id,
                'accepted': was_accepted,
                'outcome': outcome_status,
                'team_id': self.team_id,
                'timestamp': datetime.utcnow().isoformat()
            },
            source_agent='learning_system',
            priority=60  # Medium priority for outcome tracking
        )
        
        logger.info(f"Persisted outcome for recommendation {recommendation_id} to DCP")

# Export main class
__all__ = ['RecommendationScorer']