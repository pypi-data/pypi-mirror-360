"""
Learning Integration for Planner Agent

General Staff G5 Function: Doctrine Evolution
Integrates learning system with task planning and prioritization
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

from coppersun_brass.core.learning.task_outcome_collector import (
    OutcomeCollector, track_task
)
from coppersun_brass.core.learning.recommendation_scorer import RecommendationScorer
from coppersun_brass.core.learning.pattern_extractor import PatternExtractor
from coppersun_brass.core.learning.models import TaskStatus
from coppersun_brass.core.context.dcp_manager import DCPManager
# from coppersun_brass.core.event_bus import EventBus  # EventBus removed - using DCP coordination
from coppersun_brass.core.context.dcp_coordination import DCPCoordinator

logger = logging.getLogger(__name__)


class LearningIntegration:
    """
    Integrates learning system with Planner agent
    
    General Staff Role: This component enables the Planner agent to learn
    from past task outcomes and improve recommendations over time.
    """
    
    def __init__(
        self,
        dcp_path: Optional[str] = None,
        team_id: Optional[str] = None,
        enable_experiments: bool = False
    ):
        """
        Initialize learning integration
        
        Args:
            dcp_path: Path to DCP context file
            team_id: Team identifier for data isolation
            enable_experiments: Enable A/B testing
        """
        # DCP is mandatory - this is how the general staff coordinates
        self.dcp_manager = DCPManager(dcp_path)
        self.team_id = team_id
        
        # Initialize all components with DCP
        self.outcome_collector = OutcomeCollector(dcp_path, team_id=team_id)
        self.scorer = RecommendationScorer(dcp_path, team_id, enable_experiments)
        self.pattern_extractor = PatternExtractor(dcp_path, team_id)
        self._learning_cache = {}
        
        # Initialize DCPCoordinator for event subscriptions
        self.coordinator = DCPCoordinator(
            agent_name="learning_integration",
            dcp_manager=self.dcp_manager
        )
        
        # Subscribe to planning events
        self.coordinator.subscribe("planning.decision.made", self._on_planning_decision)
        self.coordinator.subscribe("planning.outcome.recorded", self._on_planning_outcome)
        
        # Start polling for events
        self.coordinator.start_polling()
        logger.info("LearningIntegration initialized with DCPCoordinator subscriptions")
        
    def _on_planning_decision(self, observation: Dict[str, Any]) -> None:
        """Handle planning decision observations from DCP.
        
        Args:
            observation: DCP observation containing decision details
        """
        try:
            # Extract data from DCP observation format
            event_data = observation.get('data', {})
            
            decision_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "decision_type": event_data.get("type", "unknown"),
                "context": event_data.get("context", {}),
                "options": event_data.get("options", []),
                "selected": event_data.get("selected"),
                "reasoning": event_data.get("reasoning", ""),
                "confidence": event_data.get("confidence", 0.5)
            }
            
            # Store in DCP for persistence
            self._store_learning_event("decision", decision_data)
            
            # Cache for quick access
            decision_id = event_data.get("id", f"decision_{datetime.utcnow().timestamp()}")
            self._learning_cache[decision_id] = decision_data
            
            logger.info(f"Recorded planning decision: {decision_id}")
            
        except Exception as e:
            logger.error(f"Error recording planning decision: {e}")
    
    def _on_planning_outcome(self, observation: Dict[str, Any]) -> None:
        """Handle planning outcome observations from DCP.
        
        Args:
            observation: DCP observation containing outcome details
        """
        try:
            # Extract data from DCP observation format
            event_data = observation.get('data', {})
            
            outcome_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "decision_id": event_data.get("decision_id"),
                "outcome_type": event_data.get("type", "unknown"),
                "success": event_data.get("success", False),
                "metrics": event_data.get("metrics", {}),
                "feedback": event_data.get("feedback", ""),
                "lessons": event_data.get("lessons", [])
            }
            
            # Store in DCP
            self._store_learning_event("outcome", outcome_data)
            
            # Extract patterns if possible
            if event_data.get("decision_id") in self._learning_cache:
                self._extract_pattern(
                    self._learning_cache[event_data.get("decision_id")],
                    outcome_data
                )
            
            logger.info(f"Recorded planning outcome for: {event_data.get('decision_id')}")
            
        except Exception as e:
            logger.error(f"Error recording planning outcome: {e}")
    
    def _store_learning_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Store learning event in DCP.
        
        Args:
            event_type: Type of learning event
            data: Event data to store
        """
        try:
            # Add to DCP observations
            observation = {
                "type": f"planner_{event_type}",
                "category": "learning",
                "summary": f"Learning event: {event_type}",
                "priority": 70 if event_type == "decision" else 80,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.dcp_manager.add_observation(
                observation=observation,
                source_agent="planner"
            )
            
        except Exception as e:
            logger.error(f"Error storing learning event: {e}")
    
    def _extract_pattern(self, decision: Dict[str, Any], outcome: Dict[str, Any]) -> None:
        """Extract patterns from decision-outcome pairs.
        
        Args:
            decision: Decision data
            outcome: Outcome data
        """
        try:
            pattern = {
                "timestamp": datetime.utcnow().isoformat(),
                "context_type": decision.get("context", {}).get("type", "unknown"),
                "decision_type": decision.get("decision_type"),
                "confidence": decision.get("confidence", 0.5),
                "success": outcome.get("success", False),
                "key_factors": self._identify_key_factors(decision, outcome),
                "recommendation": self._generate_recommendation(decision, outcome)
            }
            
            # Store pattern
            self._store_learning_event("pattern", pattern)
            
            logger.info(f"Extracted pattern from decision-outcome pair")
            
        except Exception as e:
            logger.error(f"Error extracting pattern: {e}")
    
    def _identify_key_factors(self, decision: Dict[str, Any], outcome: Dict[str, Any]) -> List[str]:
        """Identify key factors that influenced the outcome.
        
        Args:
            decision: Decision data
            outcome: Outcome data
            
        Returns:
            List of key factors
        """
        factors = []
        
        # Analyze confidence vs success
        if decision.get("confidence", 0) > 0.8 and outcome.get("success"):
            factors.append("high_confidence_accurate")
        elif decision.get("confidence", 0) < 0.3 and not outcome.get("success"):
            factors.append("low_confidence_accurate")
        
        # Analyze context factors
        context = decision.get("context", {})
        if context.get("complexity", "medium") == "high" and outcome.get("success"):
            factors.append("handled_complex_well")
        
        # Analyze metrics
        metrics = outcome.get("metrics", {})
        if metrics.get("time_saved", 0) > 0:
            factors.append("time_efficient")
        if metrics.get("accuracy", 0) > 0.9:
            factors.append("high_accuracy")
        
        return factors
    
    def _generate_recommendation(self, decision: Dict[str, Any], outcome: Dict[str, Any]) -> str:
        """Generate recommendation based on decision-outcome analysis.
        
        Args:
            decision: Decision data
            outcome: Outcome data
            
        Returns:
            Recommendation string
        """
        if outcome.get("success"):
            if decision.get("confidence", 0) > 0.7:
                return "Continue with similar approach for this context type"
            else:
                return "Consider increasing confidence threshold for similar decisions"
        else:
            if decision.get("confidence", 0) > 0.7:
                return "Re-evaluate decision criteria for this context type"
            else:
                return "Gather more information before making similar decisions"
    
    def get_learning_insights(self, context_type: Optional[str] = None) -> Dict[str, Any]:
        """Get learning insights for planning decisions.
        
        Args:
            context_type: Optional context type to filter by
            
        Returns:
            Dictionary of learning insights
        """
        try:
            # Get recent observations from DCP
            filters = {"category": "learning"}
            observations = self.dcp_manager.get_observations(filters=filters)
            
            # Filter by context type if specified
            if context_type:
                observations = [
                    obs for obs in observations
                    if obs.get("data", {}).get("data", {}).get("context_type") == context_type
                ]
            
            # Analyze patterns
            patterns = [
                obs.get("data", {}).get("data", {}) for obs in observations
                if obs.get("type") == "planner_pattern"
            ]
            
            # Calculate success rate
            outcomes = [
                obs.get("data", {}).get("data", {}) for obs in observations
                if obs.get("type") == "planner_outcome"
            ]
            
            success_rate = (
                sum(1 for o in outcomes if o.get("success", False)) / len(outcomes)
                if outcomes else 0.5  # Default to 50% if no data
            )
            
            # Find most successful patterns
            successful_patterns = [
                p for p in patterns
                if p.get("success", False)
            ]
            
            return {
                "total_decisions": len([o for o in observations if o.get("type") == "planner_decision"]),
                "total_outcomes": len(outcomes),
                "success_rate": success_rate,
                "patterns_found": len(patterns),
                "successful_patterns": successful_patterns[:5],  # Top 5
                "recommendations": self._aggregate_recommendations(patterns),
                "context_type": context_type
            }
            
        except Exception as e:
            logger.error(f"Error getting learning insights: {e}")
            return {
                "total_decisions": 0,
                "total_outcomes": 0,
                "success_rate": 0.5,
                "patterns_found": 0,
                "successful_patterns": [],
                "recommendations": [],
                "context_type": context_type
            }
    
    def _aggregate_recommendations(self, patterns: List[Dict[str, Any]]) -> List[str]:
        """Aggregate recommendations from patterns.
        
        Args:
            patterns: List of pattern dictionaries
            
        Returns:
            List of aggregated recommendations
        """
        recommendations = {}
        
        for pattern in patterns:
            rec = pattern.get("recommendation", "")
            if rec:
                recommendations[rec] = recommendations.get(rec, 0) + 1
        
        # Sort by frequency
        sorted_recs = sorted(
            recommendations.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [rec for rec, _ in sorted_recs[:5]]  # Top 5 recommendations
    
    def apply_learning(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply learned insights to improve decision making.
        
        Args:
            decision_context: Context for the current decision
            
        Returns:
            Dictionary with learning-enhanced recommendations
        """
        try:
            # Get relevant insights
            context_type = decision_context.get("type", "general")
            insights = self.get_learning_insights(context_type)
            
            # Find similar successful patterns
            similar_patterns = []
            for pattern in insights.get("successful_patterns", []):
                if self._is_similar_context(decision_context, pattern):
                    similar_patterns.append(pattern)
            
            # Generate recommendations
            recommendations = {
                "confidence_adjustment": self._calculate_confidence_adjustment(
                    insights, similar_patterns
                ),
                "suggested_approach": self._suggest_approach(similar_patterns),
                "risk_factors": self._identify_risks(insights, decision_context),
                "success_probability": insights.get("success_rate", 0.5)
            }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error applying learning: {e}")
            return {}
    
    def _is_similar_context(self, context1: Dict[str, Any], pattern: Dict[str, Any]) -> bool:
        """Check if contexts are similar.
        
        Args:
            context1: First context
            pattern: Pattern containing context
            
        Returns:
            True if contexts are similar
        """
        # Simple similarity check - can be enhanced
        return (
            context1.get("type") == pattern.get("context_type") and
            abs(context1.get("complexity", 0.5) - pattern.get("confidence", 0.5)) < 0.3
        )
    
    def _calculate_confidence_adjustment(
        self, insights: Dict[str, Any], similar_patterns: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence adjustment based on learning.
        
        Args:
            insights: Learning insights
            similar_patterns: Similar successful patterns
            
        Returns:
            Confidence adjustment factor
        """
        if not similar_patterns:
            # No similar patterns, be cautious
            return -0.1
        
        # Average confidence of successful similar patterns
        avg_confidence = sum(
            p.get("confidence", 0.5) for p in similar_patterns
        ) / len(similar_patterns)
        
        # Adjust based on overall success rate
        success_rate = insights.get("success_rate", 0.5)
        
        return (avg_confidence - 0.5) * success_rate
    
    def _suggest_approach(self, similar_patterns: List[Dict[str, Any]]) -> str:
        """Suggest approach based on similar patterns.
        
        Args:
            similar_patterns: List of similar successful patterns
            
        Returns:
            Suggested approach
        """
        if not similar_patterns:
            return "Proceed with standard approach, gather more data"
        
        # Find most common successful factors
        all_factors = []
        for pattern in similar_patterns:
            all_factors.extend(pattern.get("key_factors", []))
        
        if "high_confidence_accurate" in all_factors:
            return "Proceed with high confidence based on past success"
        elif "time_efficient" in all_factors:
            return "Optimize for speed, pattern shows time efficiency works"
        else:
            return "Follow successful pattern, focus on accuracy"
    
    def _identify_risks(self, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Identify potential risks based on learning.
        
        Args:
            insights: Learning insights
            context: Decision context
            
        Returns:
            List of identified risks
        """
        risks = []
        
        # Low overall success rate
        if insights.get("success_rate", 0.5) < 0.3:
            risks.append("Low historical success rate for this context type")
        
        # High complexity
        if context.get("complexity", 0) > 0.8:
            risks.append("High complexity detected, consider breaking down")
        
        # Few data points
        if insights.get("total_outcomes", 0) < 5:
            risks.append("Limited historical data, recommendations may be unreliable")
        
        return risks
    
    def enhance_task_recommendations(
        self,
        tasks: List[Dict[str, Any]],
        project_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Enhance task recommendations with learned patterns
        
        Args:
            tasks: List of potential tasks
            project_context: Current project context
            
        Returns:
            Enhanced tasks with adjusted priorities
        """
        # Build context for learning system
        learning_context = self._build_learning_context(project_context)
        
        # Generate task ID for experiment tracking
        task_id = f"planner_{datetime.utcnow().timestamp():.0f}"
        
        # Score recommendations
        enhanced_tasks = []
        for task in tasks:
            # Convert task to recommendation format
            recommendation = self._task_to_recommendation(task)
            
            # Apply learning-based scoring
            enhanced_rec = self.scorer.score_recommendation(
                recommendation,
                learning_context,
                task_id
            )
            
            # Convert back to task format
            enhanced_task = self._recommendation_to_task(enhanced_rec, task)
            enhanced_tasks.append(enhanced_task)
        
        # Sort by enhanced score
        enhanced_tasks.sort(key=lambda t: t.get('priority_score', 0), reverse=True)
        
        # Log learning impact
        self._log_learning_impact(tasks, enhanced_tasks)
        
        return enhanced_tasks
    
    def _build_learning_context(
        self,
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build context for learning system"""
        # Extract relevant dimensions
        context = {
            'project_type': project_context.get('project_type', 'unknown'),
            'language': project_context.get('primary_language', 'python'),
            'team_id': self.team_id
        }
        
        # Add project maturity if available
        if 'project_age_days' in project_context:
            if project_context['project_age_days'] < 30:
                context['maturity'] = 'new'
            elif project_context['project_age_days'] < 180:
                context['maturity'] = 'developing'
            else:
                context['maturity'] = 'mature'
        
        # Add complexity indicators
        if 'file_count' in project_context:
            if project_context['file_count'] < 50:
                context['complexity'] = 'simple'
            elif project_context['file_count'] < 200:
                context['complexity'] = 'moderate'
            else:
                context['complexity'] = 'complex'
        
        return context
    
    def _task_to_recommendation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Convert task to recommendation format"""
        return {
            'id': task.get('id', 'unknown'),
            'type': task.get('type', 'task'),
            'score': task.get('priority', 0.5),
            'context': {
                'category': task.get('category', 'general'),
                'urgency': task.get('urgency', 'medium'),
                'impact': task.get('impact', 'medium')
            }
        }
    
    def _recommendation_to_task(
        self,
        recommendation: Dict[str, Any],
        original_task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert enhanced recommendation back to task"""
        enhanced_task = original_task.copy()
        
        # Update priority based on enhanced score
        enhanced_task['priority_score'] = recommendation['score']
        
        # Add learning metadata
        if '_experiment_variant' in recommendation:
            enhanced_task['learning_variant'] = recommendation['_experiment_variant']
        
        if 'learning_metadata' in recommendation:
            enhanced_task['learning_applied'] = True
            enhanced_task['learning_adjustment'] = recommendation['learning_metadata'].get(
                'adjustment', 0
            )
            enhanced_task['learning_reason'] = recommendation['learning_metadata'].get(
                'reasons', []
            )
        
        return enhanced_task
    
    def _log_learning_impact(
        self,
        original_tasks: List[Dict[str, Any]],
        enhanced_tasks: List[Dict[str, Any]]
    ) -> None:
        """Log the impact of learning on task prioritization"""
        # Calculate reordering impact
        original_order = {t['id']: i for i, t in enumerate(original_tasks)}
        enhanced_order = {t['id']: i for i, t in enumerate(enhanced_tasks)}
        
        total_movement = 0
        for task_id in original_order:
            if task_id in enhanced_order:
                movement = abs(original_order[task_id] - enhanced_order[task_id])
                total_movement += movement
        
        if total_movement > 0:
            logger.info(
                f"Learning system reordered tasks with total movement: {total_movement}"
            )
    
    @track_task
    async def record_task_outcome(
        self,
        task_id: str,
        task_type: str,
        status: TaskStatus,
        time_taken: Optional[float] = None,
        estimated_time: Optional[float] = None,
        error_message: Optional[str] = None,
        user_feedback: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record outcome of a planned task
        
        This is automatically tracked by the decorator, but can be
        called directly for more control.
        
        Args:
            task_id: Unique task identifier
            task_type: Type of task
            status: Task completion status
            time_taken: Actual time in seconds
            estimated_time: Originally estimated time
            error_message: Error if failed
            user_feedback: Optional user feedback
            context: Additional context
            
        Returns:
            Outcome ID
        """
        # The decorator handles the actual recording
        # This method exists for explicit calls
        return f"outcome_{task_id}"
    
    def get_enhanced_learning_insights(
        self,
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get insights about learning system performance
        
        Args:
            lookback_days: Days to analyze
            
        Returns:
            Insights dictionary
        """
        insights = {
            'scoring_insights': self.scorer.get_scoring_insights(lookback_days),
            'active_patterns': [],
            'pattern_summary': {},
            'recommendations': []
        }
        
        # Get active patterns
        patterns = self.pattern_extractor.get_patterns_for_context({
            'team_id': self.team_id
        })
        
        for pattern in patterns[:10]:  # Top 10
            insights['active_patterns'].append({
                'name': pattern.pattern_name,
                'type': pattern.pattern_type,
                'confidence': pattern.confidence,
                'success_rate': pattern.success_rate,
                'sample_size': pattern.sample_size
            })
        
        # Summarize by type
        pattern_types = {}
        for pattern in patterns:
            if pattern.pattern_type not in pattern_types:
                pattern_types[pattern.pattern_type] = {
                    'count': 0,
                    'avg_confidence': 0,
                    'total_samples': 0
                }
            
            pt = pattern_types[pattern.pattern_type]
            pt['count'] += 1
            pt['avg_confidence'] += pattern.confidence
            pt['total_samples'] += pattern.sample_size
        
        # Calculate averages
        for pt_name, pt_data in pattern_types.items():
            if pt_data['count'] > 0:
                pt_data['avg_confidence'] /= pt_data['count']
        
        insights['pattern_summary'] = pattern_types
        
        # Generate recommendations
        if len(patterns) < 5:
            insights['recommendations'].append(
                "Insufficient patterns for effective learning - need more task history"
            )
        
        high_confidence_patterns = [p for p in patterns if p.confidence > 0.8]
        if high_confidence_patterns:
            insights['recommendations'].append(
                f"Found {len(high_confidence_patterns)} high-confidence patterns - "
                "learning system is providing reliable guidance"
            )
        
        return insights
    
    def extract_new_patterns(
        self,
        min_samples: int = 5,
        lookback_days: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Extract new patterns from recent task outcomes
        
        Args:
            min_samples: Minimum samples required
            lookback_days: Days to analyze
            
        Returns:
            List of new patterns
        """
        patterns = self.pattern_extractor.extract_patterns(
            min_samples,
            lookback_days
        )
        
        # Convert to serializable format
        pattern_list = []
        for pattern in patterns:
            pattern_list.append({
                'id': pattern.id,
                'name': pattern.pattern_name,
                'type': pattern.pattern_type,
                'description': pattern.description,
                'confidence': pattern.confidence,
                'success_rate': pattern.success_rate,
                'sample_size': pattern.sample_size,
                'context': pattern.context_dimensions
            })
        
        # Update DCP with significant patterns
        if self.dcp_manager and pattern_list:
            self.dcp_manager.add_observation(
                'learning_patterns_extracted',
                {
                    'pattern_count': len(pattern_list),
                    'high_confidence_count': len([
                        p for p in pattern_list
                        if p['confidence'] > 0.8
                    ]),
                    'extraction_time': datetime.utcnow().isoformat()
                }
            )
        
        return pattern_list
    
    def update_recommendation_outcome(
        self,
        task_id: str,
        was_accepted: bool,
        outcome_status: Optional[TaskStatus] = None
    ) -> bool:
        """
        Update outcome for a recommendation
        
        Args:
            task_id: Task identifier
            was_accepted: Whether recommendation was accepted
            outcome_status: Final task status
            
        Returns:
            Success boolean
        """
        # Convert TaskStatus enum to string if needed
        status_str = outcome_status.value if outcome_status else None
        
        return self.scorer.update_outcome(
            recommendation_id=task_id,
            was_accepted=was_accepted,
            outcome_status=status_str
        )
    
    def cleanup(self) -> None:
        """Clean up resources and stop polling."""
        if hasattr(self, 'coordinator') and self.coordinator:
            self.coordinator.stop_polling()
            logger.info("LearningIntegration coordinator stopped")