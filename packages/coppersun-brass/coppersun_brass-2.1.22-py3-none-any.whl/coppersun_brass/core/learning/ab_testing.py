"""
A/B Testing Framework for Learning System

General Staff G5 Function: Doctrine Testing
Tests recommendation improvements through controlled experiments
"""

import hashlib
from typing import Dict, Any, Optional, Literal, List
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path

from coppersun_brass.core.learning.models import (
    RecommendationHistory, ExperimentVariant, TaskOutcome,
    TaskStatus, init_db
)
from coppersun_brass.core.context.dcp_manager import DCPManager
from .dcp_helpers import get_dcp_section, update_dcp_section

logger = logging.getLogger(__name__)

class RecommendationExperiment:
    """
    A/B testing framework for recommendation improvements
    
    General Staff G5 Function: Doctrine Testing
    This component tests recommendation improvements through controlled experiments,
    maintaining experiment state and results in DCP for cross-session analysis.
    """
    
    def __init__(
        self,
        dcp_path: Optional[str] = None,
        enabled: bool = False,
        allocation_percentage: int = 50
    ):
        """
        Initialize A/B testing framework with MANDATORY DCP integration
        
        Args:
            dcp_path: Path to DCP context file (mandatory per CLAUDE.md)
            enabled: Whether A/B testing is enabled
            allocation_percentage: Percentage allocated to test variant
        """
        # DCP is MANDATORY - this is how the general staff coordinates
        self.dcp_manager = DCPManager(dcp_path)
        self.enabled = enabled
        self.allocation_percentage = allocation_percentage
        self.engine, self.Session = init_db()
        
        # Load experiment configuration from DCP
        self._load_experiment_from_dcp()
    
    def assign_variant(
        self,
        task_id: str,
        force_variant: Optional[ExperimentVariant] = None
    ) -> ExperimentVariant:
        """
        Assign experiment variant for a task
        
        Args:
            task_id: Unique task identifier
            force_variant: Optional forced variant for testing
            
        Returns:
            Assigned variant (control or test)
        """
        if force_variant:
            return force_variant
        
        if not self.enabled:
            return ExperimentVariant.CONTROL
        
        # Deterministic assignment based on task ID hash
        hash_value = int(hashlib.md5(task_id.encode()).hexdigest(), 16)
        assignment = hash_value % 100
        
        if assignment < self.allocation_percentage:
            return ExperimentVariant.TEST
        else:
            return ExperimentVariant.CONTROL
    
    def apply_variant_logic(
        self,
        recommendation: Dict[str, Any],
        variant: ExperimentVariant,
        learning_adjustments: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Apply variant-specific logic to recommendation
        
        Args:
            recommendation: Original recommendation
            variant: Assigned variant
            learning_adjustments: Optional learning system adjustments
            
        Returns:
            Modified recommendation based on variant
        """
        # Clone recommendation
        modified = recommendation.copy()
        modified['_experiment_variant'] = variant.value
        
        if variant == ExperimentVariant.CONTROL:
            # Control group gets original scoring
            modified['_experiment_group'] = 'control'
            return modified
        
        # Test group gets learning-enhanced scoring
        modified['_experiment_group'] = 'test'
        
        if learning_adjustments:
            # Apply learning adjustments
            original_score = modified.get('score', 0.5)
            adjustment = learning_adjustments.get('adjustment', 0.0)
            
            modified['original_score'] = original_score
            modified['adjusted_score'] = original_score * (1 + adjustment)
            modified['score'] = modified['adjusted_score']
            modified['learning_metadata'] = learning_adjustments
            
        return modified
    
    def record_recommendation(
        self,
        recommendation_id: str,
        task_id: str,
        original_score: float,
        adjusted_score: float,
        variant: ExperimentVariant,
        adjustment_reason: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record recommendation for experiment tracking
        
        Args:
            recommendation_id: Unique recommendation ID
            task_id: Associated task ID
            original_score: Original recommendation score
            adjusted_score: Adjusted score (same as original for control)
            variant: Experiment variant
            adjustment_reason: Reason for adjustment
            
        Returns:
            History record ID
        """
        session = self.Session()
        try:
            history = RecommendationHistory(
                id=f"rechist_{datetime.utcnow().timestamp()}_{recommendation_id[:8]}",
                recommendation_id=recommendation_id,
                task_id=task_id,
                original_score=original_score,
                adjusted_score=adjusted_score,
                experiment_variant=variant,
                adjustment_reason=adjustment_reason or {}
            )
            
            session.add(history)
            session.commit()
            
            logger.info(
                f"Recorded recommendation {recommendation_id} "
                f"for variant {variant.value}"
            )
            
            # Persist to DCP for experiment tracking
            self._persist_recommendation_to_dcp(
                recommendation_id,
                task_id,
                variant,
                original_score,
                adjusted_score,
                adjustment_reason
            )
            
            return history.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to record recommendation: {e}")
            raise
        finally:
            session.close()
    
    def update_outcome(
        self,
        recommendation_id: str,
        was_accepted: bool,
        outcome_status: Optional[TaskStatus] = None
    ) -> bool:
        """
        Update recommendation outcome
        
        Args:
            recommendation_id: Recommendation ID
            was_accepted: Whether recommendation was accepted
            outcome_status: Final task status
            
        Returns:
            Success boolean
        """
        session = self.Session()
        try:
            history = session.query(RecommendationHistory).filter_by(
                recommendation_id=recommendation_id
            ).first()
            
            if not history:
                logger.warning(f"No history found for recommendation {recommendation_id}")
                return False
            
            history.was_accepted = was_accepted
            if outcome_status:
                history.outcome_status = outcome_status
            
            session.commit()
            logger.info(f"Updated outcome for recommendation {recommendation_id}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update outcome: {e}")
            return False
        finally:
            session.close()
    
    def get_experiment_results(
        self,
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get experiment results comparing variants
        
        Args:
            lookback_days: Days to look back
            
        Returns:
            Results dictionary with metrics for each variant
        """
        session = self.Session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)
            
            # Get recommendations by variant
            results = {
                'control': self._get_variant_metrics(
                    session,
                    ExperimentVariant.CONTROL,
                    cutoff_date
                ),
                'test': self._get_variant_metrics(
                    session,
                    ExperimentVariant.TEST,
                    cutoff_date
                ),
                'summary': {}
            }
            
            # Calculate lift
            if results['control']['total'] > 0 and results['test']['total'] > 0:
                control_accept = results['control']['acceptance_rate']
                test_accept = results['test']['acceptance_rate']
                
                if control_accept > 0:
                    lift = ((test_accept - control_accept) / control_accept) * 100
                    results['summary']['acceptance_lift'] = round(lift, 1)
                
                control_success = results['control']['success_rate']
                test_success = results['test']['success_rate']
                
                if control_success > 0:
                    success_lift = ((test_success - control_success) / control_success) * 100
                    results['summary']['success_lift'] = round(success_lift, 1)
                
                # Statistical significance (simplified)
                results['summary']['significant'] = self._is_significant(
                    results['control'],
                    results['test']
                )
            
            results['summary']['recommendation'] = self._get_recommendation(results)
            
            return results
            
        finally:
            session.close()
    
    def _get_variant_metrics(
        self,
        session,
        variant: ExperimentVariant,
        cutoff_date: datetime
    ) -> Dict[str, Any]:
        """Get metrics for a specific variant"""
        # Get all recommendations for variant
        recommendations = session.query(RecommendationHistory).filter(
            RecommendationHistory.experiment_variant == variant,
            RecommendationHistory.created_at >= cutoff_date
        ).all()
        
        total = len(recommendations)
        accepted = sum(1 for r in recommendations if r.was_accepted)
        
        # Get outcomes for accepted recommendations
        successful = 0
        for rec in recommendations:
            if rec.was_accepted and rec.outcome_status == TaskStatus.COMPLETED:
                successful += 1
        
        metrics = {
            'total': total,
            'accepted': accepted,
            'successful': successful,
            'acceptance_rate': accepted / total if total > 0 else 0,
            'success_rate': successful / accepted if accepted > 0 else 0
        }
        
        # Score adjustments
        if variant == ExperimentVariant.TEST:
            adjustments = [
                abs(r.adjusted_score - r.original_score)
                for r in recommendations
                if r.adjusted_score != r.original_score
            ]
            if adjustments:
                metrics['avg_adjustment'] = sum(adjustments) / len(adjustments)
                metrics['adjustment_count'] = len(adjustments)
        
        return metrics
    
    def _is_significant(
        self,
        control_metrics: Dict[str, Any],
        test_metrics: Dict[str, Any]
    ) -> bool:
        """
        Simple statistical significance check
        
        In production, use proper statistical tests
        """
        # Require minimum sample size
        if control_metrics['total'] < 30 or test_metrics['total'] < 30:
            return False
        
        # Check if difference is meaningful
        control_rate = control_metrics['acceptance_rate']
        test_rate = test_metrics['acceptance_rate']
        
        if abs(test_rate - control_rate) < 0.05:  # Less than 5% difference
            return False
        
        # Simplified significance (in production, use proper stats)
        return True
    
    def _get_recommendation(self, results: Dict[str, Any]) -> str:
        """Generate recommendation based on experiment results"""
        if not results['summary'].get('significant'):
            return "Continue experiment - insufficient data for decision"
        
        acceptance_lift = results['summary'].get('acceptance_lift', 0)
        success_lift = results['summary'].get('success_lift', 0)
        
        if acceptance_lift > 10 and success_lift >= 0:
            return "Strong positive results - consider enabling learning system"
        elif acceptance_lift > 5 or success_lift > 5:
            return "Positive results - monitor for consistency"
        elif acceptance_lift < -5 or success_lift < -5:
            return "Negative results - review learning algorithm"
        else:
            return "Neutral results - continue monitoring"
    
    def export_results(
        self,
        output_path: Path,
        lookback_days: int = 30
    ) -> None:
        """Export experiment results to file"""
        results = self.get_experiment_results(lookback_days)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Exported experiment results to {output_path}")

    def _load_experiment_from_dcp(self) -> None:
        """Load experiment configuration and state from DCP"""
        try:
            learning_data = get_dcp_section(self.dcp_manager, 'learning', {})
            experiment_data = learning_data.get('experiment', {})
            
            if experiment_data:
                # Override settings from DCP if present
                self.enabled = experiment_data.get('enabled', self.enabled)
                self.allocation_percentage = experiment_data.get('allocation_percentage', self.allocation_percentage)
                self.experiment_start_date = experiment_data.get('start_date')
                logger.info(f"Loaded experiment config from DCP: enabled={self.enabled}, allocation={self.allocation_percentage}%")
        except Exception as e:
            logger.warning(f"Could not load experiment config from DCP: {e}")
            self.experiment_start_date = None
    
    def _persist_recommendation_to_dcp(
        self,
        recommendation_id: str,
        task_id: str,
        variant: ExperimentVariant,
        original_score: float,
        adjusted_score: float,
        adjustment_reason: Optional[Dict[str, Any]] = None
    ) -> None:
        """Persist recommendation to DCP for cross-session tracking"""
        # Add observation for experiment tracking
        self.dcp_manager.add_observation(
            'experiment_recommendation',
            {
                'recommendation_id': recommendation_id,
                'task_id': task_id,
                'variant': variant.value,
                'original_score': float(original_score),
                'adjusted_score': float(adjusted_score),
                'adjustment': float(adjusted_score - original_score),
                'reason': adjustment_reason
            },
            source_agent='learning_system',
            priority=65  # Medium-high priority for experiment data
        )
    
    def update_experiment_config(
        self,
        enabled: Optional[bool] = None,
        allocation_percentage: Optional[int] = None
    ) -> None:
        """Update experiment configuration and persist to DCP"""
        if enabled is not None:
            self.enabled = enabled
        if allocation_percentage is not None:
            self.allocation_percentage = allocation_percentage
        
        # Persist to DCP
        experiment_config = {
            'enabled': self.enabled,
            'allocation_percentage': self.allocation_percentage,
            'start_date': self.experiment_start_date or datetime.utcnow().isoformat(),
            'last_updated': datetime.utcnow().isoformat()
        }
        
        self.dcp_manager.update_section('learning.experiment', experiment_config)
        
        # Add observation for significant event
        self.dcp_manager.add_observation(
            'experiment_config_changed',
            {
                'enabled': self.enabled,
                'allocation_percentage': self.allocation_percentage,
                'timestamp': datetime.utcnow().isoformat()
            },
            source_agent='learning_system',
            priority=80  # High priority for config changes
        )
        
        logger.info(f"Updated experiment config in DCP: enabled={self.enabled}, allocation={self.allocation_percentage}%")
    
    def persist_results_to_dcp(self, lookback_days: int = 30) -> None:
        """Persist experiment results to DCP for future analysis"""
        results = self.get_experiment_results(lookback_days)
        
        # Update DCP with latest results
        self.dcp_manager.update_section('learning.experiment.results', {
            'timestamp': datetime.utcnow().isoformat(),
            'lookback_days': lookback_days,
            'control': results['control'],
            'test': results['test'],
            'summary': results['summary']
        })
        
        # Add observation if results are significant
        if results['summary'].get('significant'):
            self.dcp_manager.add_observation(
                'experiment_significant_results',
                {
                    'acceptance_lift': results['summary'].get('acceptance_lift', 0),
                    'success_lift': results['summary'].get('success_lift', 0),
                    'recommendation': results['summary'].get('recommendation', ''),
                    'control_total': results['control']['total'],
                    'test_total': results['test']['total']
                },
                source_agent='learning_system',
                priority=85  # Very high priority for significant results
            )
        
        logger.info("Persisted experiment results to DCP")

# Export main class
__all__ = ['RecommendationExperiment']