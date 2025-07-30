"""
Planning Intelligence Engine - Adaptation Engine
Implements dynamic plan modification and learning integration for Copper Alloy Brass
autonomous planning with real-time adaptation capabilities.
"""

import uuid
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import re

from .planning_algorithms import PlanningTask, TaskType, TaskStatus, Timeline
from .constraint_solver import Schedule, Agent

logger = logging.getLogger(__name__)

# Blood oath compliance: Use pure Python implementations only
SKLEARN_AVAILABLE = False
logger.info("Using pure Python adaptation algorithms for blood oath compliance")


class AdaptationTrigger(Enum):
    """Types of adaptation triggers"""
    TASK_FAILED = "task_failed"
    DEADLINE_MISSED = "deadline_missed" 
    RESOURCE_UNAVAILABLE = "resource_unavailable"
    SCOPE_CHANGE = "scope_change"
    PRIORITY_SHIFT = "priority_shift"
    DEPENDENCY_CHANGED = "dependency_changed"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    EXTERNAL_CONSTRAINT = "external_constraint"


class AdaptationStrategy(Enum):
    """Adaptation strategies"""
    RESCHEDULE = "reschedule"
    REASSIGN = "reassign"
    REPLANNING = "replanning"
    RESOURCE_REALLOCATION = "resource_reallocation"
    SCOPE_REDUCTION = "scope_reduction"
    TIMELINE_EXTENSION = "timeline_extension"
    PARALLEL_EXECUTION = "parallel_execution"


@dataclass
class AdaptationPattern:
    """Learned adaptation pattern"""
    pattern_id: str
    trigger_type: AdaptationTrigger
    context_features: Dict[str, Any]
    successful_strategies: List[AdaptationStrategy]
    success_rate: float
    usage_count: int
    confidence_score: float
    learned_from_plans: List[str]
    created_at: datetime
    last_used: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['trigger_type'] = self.trigger_type.value
        data['successful_strategies'] = [s.value for s in self.successful_strategies]
        data['created_at'] = self.created_at.isoformat()
        data['last_used'] = self.last_used.isoformat() if self.last_used else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AdaptationPattern':
        data = data.copy()
        data['trigger_type'] = AdaptationTrigger(data['trigger_type'])
        data['successful_strategies'] = [AdaptationStrategy(s) for s in data['successful_strategies']]
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('last_used'):
            data['last_used'] = datetime.fromisoformat(data['last_used'])
        return cls(**data)


@dataclass
class AdaptationAction:
    """Specific adaptation action to execute"""
    action_id: str
    strategy: AdaptationStrategy
    description: str
    affected_tasks: List[str]
    affected_agents: List[str]
    estimated_impact: str  # 'low', 'medium', 'high'
    confidence: float
    parameters: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['strategy'] = self.strategy.value
        return data


@dataclass
class Plan:
    """Complete project plan"""
    plan_id: str
    tasks: List[PlanningTask]
    schedule: Schedule
    timeline: Timeline
    status: str
    created_at: datetime
    last_modified: datetime
    adaptation_history: List[Dict] = None
    
    def __post_init__(self):
        if self.adaptation_history is None:
            self.adaptation_history = []
    
    def to_dict(self) -> Dict:
        return {
            'plan_id': self.plan_id,
            'tasks': [task.to_dict() for task in self.tasks],
            'schedule': self.schedule.to_dict(),
            'timeline': self.timeline.to_dict(),
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'last_modified': self.last_modified.isoformat(),
            'adaptation_history': self.adaptation_history
        }


class AdaptationEngine:
    """Dynamic plan adaptation and learning engine"""
    
    def __init__(self):
        self.adaptation_patterns: Dict[str, AdaptationPattern] = {}
        self.completed_plans: List[Plan] = []
        self.adaptation_cache: Dict[str, List[AdaptationAction]] = {}
        self.learning_enabled = True
        
    def detect_adaptation_triggers(self, plan: Plan, observations: List[Dict]) -> List[Tuple[AdaptationTrigger, Dict]]:
        """
        Detect adaptation triggers from plan status and observations
        
        Args:
            plan: Current plan
            observations: List of observations from DCP
            
        Returns:
            List of (trigger_type, context) tuples
        """
        start_time = datetime.now()
        logger.info(f"Detecting adaptation triggers for plan {plan.plan_id}")
        
        triggers = []
        
        try:
            # Check task failures
            triggers.extend(self._detect_task_failures(plan))
            
            # Check deadline misses
            triggers.extend(self._detect_deadline_misses(plan))
            
            # Check resource availability
            triggers.extend(self._detect_resource_issues(plan, observations))
            
            # Check scope changes
            triggers.extend(self._detect_scope_changes(plan, observations))
            
            # Check priority shifts
            triggers.extend(self._detect_priority_changes(observations))
            
            # Check dependency changes
            triggers.extend(self._detect_dependency_changes(plan, observations))
            
            # Check performance degradation
            triggers.extend(self._detect_performance_issues(plan, observations))
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Trigger detection completed in {duration:.2f}s, found {len(triggers)} triggers")
            
            return triggers
            
        except Exception as e:
            logger.error(f"Trigger detection failed: {str(e)}")
            return []
    
    def _detect_task_failures(self, plan: Plan) -> List[Tuple[AdaptationTrigger, Dict]]:
        """Detect failed tasks"""
        triggers = []
        
        for task in plan.tasks:
            if task.status == TaskStatus.FAILED:
                triggers.append((AdaptationTrigger.TASK_FAILED, {
                    'task_id': task.id,
                    'task_type': task.task_type.value,
                    'failure_time': datetime.now(),
                    'estimated_hours': task.estimated_hours,
                    'dependencies': task.dependencies
                }))
        
        return triggers
    
    def _detect_deadline_misses(self, plan: Plan) -> List[Tuple[AdaptationTrigger, Dict]]:
        """Detect missed deadlines"""
        triggers = []
        current_time = datetime.now()
        
        for task in plan.tasks:
            if (task.deadline and 
                task.deadline < current_time and 
                task.status != TaskStatus.COMPLETED):
                
                triggers.append((AdaptationTrigger.DEADLINE_MISSED, {
                    'task_id': task.id,
                    'deadline': task.deadline,
                    'delay_hours': (current_time - task.deadline).total_seconds() / 3600,
                    'task_type': task.task_type.value
                }))
        
        return triggers
    
    def _detect_resource_issues(self, plan: Plan, observations: List[Dict]) -> List[Tuple[AdaptationTrigger, Dict]]:
        """Detect resource unavailability"""
        triggers = []
        
        # Check for agent unavailability mentions in observations
        for obs in observations:
            summary = obs.get('summary', '').lower()
            if any(keyword in summary for keyword in ['agent unavailable', 'resource conflict', 'blocked']):
                triggers.append((AdaptationTrigger.RESOURCE_UNAVAILABLE, {
                    'observation_id': obs.get('id'),
                    'description': obs.get('summary'),
                    'priority': obs.get('priority', 50),
                    'detected_at': datetime.now()
                }))
        
        return triggers
    
    def _detect_scope_changes(self, plan: Plan, observations: List[Dict]) -> List[Tuple[AdaptationTrigger, Dict]]:
        """Detect scope changes"""
        triggers = []
        
        scope_keywords = ['new requirement', 'scope change', 'additional feature', 'requirement update']
        
        for obs in observations:
            summary = obs.get('summary', '').lower()
            if any(keyword in summary for keyword in scope_keywords):
                triggers.append((AdaptationTrigger.SCOPE_CHANGE, {
                    'observation_id': obs.get('id'),
                    'description': obs.get('summary'),
                    'priority': obs.get('priority', 50),
                    'change_type': 'requirement_addition'
                }))
        
        return triggers
    
    def _detect_priority_changes(self, observations: List[Dict]) -> List[Tuple[AdaptationTrigger, Dict]]:
        """Detect priority shifts"""
        triggers = []
        
        high_priority_obs = [obs for obs in observations if obs.get('priority', 0) > 90]
        
        if len(high_priority_obs) > 5:  # Threshold for priority shift
            triggers.append((AdaptationTrigger.PRIORITY_SHIFT, {
                'high_priority_count': len(high_priority_obs),
                'observations': [obs.get('id') for obs in high_priority_obs[:3]],
                'shift_detected_at': datetime.now()
            }))
        
        return triggers
    
    def _detect_dependency_changes(self, plan: Plan, observations: List[Dict]) -> List[Tuple[AdaptationTrigger, Dict]]:
        """Detect dependency changes"""
        triggers = []
        
        dependency_keywords = ['dependency', 'blocked by', 'waiting for', 'prerequisite']
        
        for obs in observations:
            summary = obs.get('summary', '').lower()
            if any(keyword in summary for keyword in dependency_keywords):
                triggers.append((AdaptationTrigger.DEPENDENCY_CHANGED, {
                    'observation_id': obs.get('id'),
                    'description': obs.get('summary'),
                    'affected_tasks': self._extract_task_references(summary)
                }))
        
        return triggers
    
    def _detect_performance_issues(self, plan: Plan, observations: List[Dict]) -> List[Tuple[AdaptationTrigger, Dict]]:
        """Detect performance degradation"""
        triggers = []
        
        performance_keywords = ['slow', 'delayed', 'behind schedule', 'performance issue']
        
        for obs in observations:
            summary = obs.get('summary', '').lower()
            if any(keyword in summary for keyword in performance_keywords):
                triggers.append((AdaptationTrigger.PERFORMANCE_DEGRADATION, {
                    'observation_id': obs.get('id'),
                    'description': obs.get('summary'),
                    'severity': self._assess_performance_severity(summary)
                }))
        
        return triggers
    
    def _extract_task_references(self, text: str) -> List[str]:
        """Extract task references from text"""
        # Simple regex to find task-like references
        task_patterns = [
            r'task[:\s]+([a-zA-Z0-9\-_]+)',
            r'feature[:\s]+([a-zA-Z0-9\-_\s]+)',
            r'implement[:\s]+([a-zA-Z0-9\-_\s]+)'
        ]
        
        references = []
        for pattern in task_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            references.extend(matches)
        
        return references[:3]  # Limit to first 3 references
    
    def _assess_performance_severity(self, text: str) -> str:
        """Assess severity of performance issue"""
        if any(word in text.lower() for word in ['critical', 'severe', 'major']):
            return 'high'
        elif any(word in text.lower() for word in ['moderate', 'medium']):
            return 'medium'
        else:
            return 'low'
    
    def adapt_plan(self, plan: Plan, triggers: List[Tuple[AdaptationTrigger, Dict]]) -> Plan:
        """
        Adapt plan based on detected triggers
        
        Args:
            plan: Current plan to adapt
            triggers: List of adaptation triggers
            
        Returns:
            Adapted plan
        """
        start_time = datetime.now()
        logger.info(f"Adapting plan {plan.plan_id} with {len(triggers)} triggers")
        
        try:
            adapted_plan = self._copy_plan(plan)
            adaptation_actions = []
            
            for trigger_type, context in triggers:
                # Find applicable adaptation patterns
                pattern = self._find_adaptation_pattern(trigger_type, context)
                
                # Generate adaptation actions
                actions = self._generate_adaptation_actions(trigger_type, context, pattern, adapted_plan)
                adaptation_actions.extend(actions)
            
            # Apply adaptation actions
            for action in adaptation_actions:
                adapted_plan = self._apply_adaptation_action(adapted_plan, action)
            
            # Update plan metadata
            adapted_plan.last_modified = datetime.now()
            adapted_plan.adaptation_history.append({
                'timestamp': datetime.now().isoformat(),
                'triggers': [(t.value, c) for t, c in triggers],
                'actions_applied': len(adaptation_actions),
                'actions': [action.to_dict() for action in adaptation_actions]
            })
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Plan adaptation completed in {duration:.2f}s, applied {len(adaptation_actions)} actions")
            
            return adapted_plan
            
        except Exception as e:
            logger.error(f"Plan adaptation failed: {str(e)}")
            return plan
    
    def _copy_plan(self, plan: Plan) -> Plan:
        """Create a copy of the plan for modification"""
        return Plan(
            plan_id=plan.plan_id,
            tasks=[task for task in plan.tasks],  # Shallow copy of tasks
            schedule=plan.schedule,
            timeline=plan.timeline,
            status=plan.status,
            created_at=plan.created_at,
            last_modified=plan.last_modified,
            adaptation_history=plan.adaptation_history.copy()
        )
    
    def _find_adaptation_pattern(self, trigger_type: AdaptationTrigger, context: Dict) -> Optional[AdaptationPattern]:
        """Find best matching adaptation pattern"""
        matching_patterns = [
            pattern for pattern in self.adaptation_patterns.values()
            if pattern.trigger_type == trigger_type
        ]
        
        if not matching_patterns:
            return None
        
        # Score patterns based on context similarity and success rate
        if SKLEARN_AVAILABLE and len(matching_patterns) > 1:
            return self._score_patterns_with_ml(matching_patterns, context)
        else:
            # Simple scoring: highest success rate with recent usage
            return max(matching_patterns, key=lambda p: (
                p.success_rate,
                p.usage_count,
                -((datetime.now() - (p.last_used or p.created_at)).days)
            ))
    
    def _score_patterns_with_ml(self, patterns: List[AdaptationPattern], context: Dict) -> AdaptationPattern:
        """Score patterns using machine learning similarity"""
        try:
            # Convert contexts to feature vectors
            context_features = self._extract_features(context)
            pattern_features = [self._extract_features(p.context_features) for p in patterns]
            
            # Calculate similarity scores
            similarities = []
            for pf in pattern_features:
                sim = self._calculate_feature_similarity(context_features, pf)
                similarities.append(sim)
            
            # Combine similarity with success rate
            scores = [
                (similarities[i] * 0.7 + patterns[i].success_rate * 0.3)
                for i in range(len(patterns))
            ]
            
            best_idx = max(range(len(scores)), key=lambda i: scores[i])
            return patterns[best_idx]
            
        except Exception as e:
            logger.error(f"ML pattern scoring failed: {str(e)}")
            return patterns[0]  # Fallback to first pattern
    
    def _extract_features(self, context: Dict) -> Dict[str, float]:
        """Extract numerical features from context"""
        features = {}
        
        for key, value in context.items():
            if isinstance(value, (int, float)):
                features[key] = float(value)
            elif isinstance(value, str):
                # Simple text features
                features[f"{key}_length"] = len(value)
                features[f"{key}_word_count"] = len(value.split())
            elif isinstance(value, list):
                features[f"{key}_count"] = len(value)
        
        return features
    
    def _calculate_feature_similarity(self, features1: Dict, features2: Dict) -> float:
        """Calculate similarity between feature vectors"""
        # Get common features
        common_keys = set(features1.keys()) & set(features2.keys())
        
        if not common_keys:
            return 0.0
        
        # Simple cosine similarity
        vec1 = [features1.get(key, 0.0) for key in common_keys]
        vec2 = [features2.get(key, 0.0) for key in common_keys]
        
        if SKLEARN_AVAILABLE:
            similarity = cosine_similarity([vec1], [vec2])[0][0]
            return max(0.0, similarity)  # Ensure non-negative
        else:
            # Manual cosine similarity
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = sum(a * a for a in vec1) ** 0.5
            magnitude2 = sum(b * b for b in vec2) ** 0.5
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            return dot_product / (magnitude1 * magnitude2)
    
    def _generate_adaptation_actions(
        self, 
        trigger_type: AdaptationTrigger, 
        context: Dict, 
        pattern: Optional[AdaptationPattern],
        plan: Plan
    ) -> List[AdaptationAction]:
        """Generate specific adaptation actions"""
        actions = []
        
        if pattern:
            # Use learned pattern strategies
            for strategy in pattern.successful_strategies:
                action = self._create_action_from_strategy(strategy, trigger_type, context, plan)
                if action:
                    actions.append(action)
        else:
            # Use default strategies for trigger type
            default_strategies = self._get_default_strategies(trigger_type)
            for strategy in default_strategies:
                action = self._create_action_from_strategy(strategy, trigger_type, context, plan)
                if action:
                    actions.append(action)
        
        return actions
    
    def _get_default_strategies(self, trigger_type: AdaptationTrigger) -> List[AdaptationStrategy]:
        """Get default strategies for trigger type"""
        strategy_map = {
            AdaptationTrigger.TASK_FAILED: [AdaptationStrategy.REASSIGN, AdaptationStrategy.REPLANNING],
            AdaptationTrigger.DEADLINE_MISSED: [AdaptationStrategy.RESCHEDULE, AdaptationStrategy.PARALLEL_EXECUTION],
            AdaptationTrigger.RESOURCE_UNAVAILABLE: [AdaptationStrategy.REASSIGN, AdaptationStrategy.RESOURCE_REALLOCATION],
            AdaptationTrigger.SCOPE_CHANGE: [AdaptationStrategy.REPLANNING, AdaptationStrategy.TIMELINE_EXTENSION],
            AdaptationTrigger.PRIORITY_SHIFT: [AdaptationStrategy.RESCHEDULE, AdaptationStrategy.REPLANNING],
            AdaptationTrigger.DEPENDENCY_CHANGED: [AdaptationStrategy.RESCHEDULE, AdaptationStrategy.REPLANNING],
            AdaptationTrigger.PERFORMANCE_DEGRADATION: [AdaptationStrategy.REASSIGN, AdaptationStrategy.PARALLEL_EXECUTION],
            AdaptationTrigger.EXTERNAL_CONSTRAINT: [AdaptationStrategy.TIMELINE_EXTENSION, AdaptationStrategy.SCOPE_REDUCTION]
        }
        
        return strategy_map.get(trigger_type, [AdaptationStrategy.RESCHEDULE])
    
    def _create_action_from_strategy(
        self, 
        strategy: AdaptationStrategy, 
        trigger_type: AdaptationTrigger, 
        context: Dict, 
        plan: Plan
    ) -> Optional[AdaptationAction]:
        """Create specific action from strategy"""
        action_id = str(uuid.uuid4())
        
        if strategy == AdaptationStrategy.RESCHEDULE:
            return AdaptationAction(
                action_id=action_id,
                strategy=strategy,
                description=f"Reschedule tasks affected by {trigger_type.value}",
                affected_tasks=self._get_affected_tasks(context, plan),
                affected_agents=[],
                estimated_impact="medium",
                confidence=0.8,
                parameters={'delay_hours': 2, 'reschedule_type': 'sequential'}
            )
        
        elif strategy == AdaptationStrategy.REASSIGN:
            return AdaptationAction(
                action_id=action_id,
                strategy=strategy,
                description=f"Reassign tasks due to {trigger_type.value}",
                affected_tasks=self._get_affected_tasks(context, plan),
                affected_agents=[context.get('agent_id', 'unknown')],
                estimated_impact="high",
                confidence=0.7,
                parameters={'reassignment_criteria': 'skills_and_availability'}
            )
        
        elif strategy == AdaptationStrategy.PARALLEL_EXECUTION:
            return AdaptationAction(
                action_id=action_id,
                strategy=strategy,
                description=f"Execute tasks in parallel to recover from {trigger_type.value}",
                affected_tasks=self._get_affected_tasks(context, plan),
                affected_agents=[],
                estimated_impact="medium",
                confidence=0.6,
                parameters={'max_parallel_tasks': 3}
            )
        
        elif strategy == AdaptationStrategy.TIMELINE_EXTENSION:
            return AdaptationAction(
                action_id=action_id,
                strategy=strategy,
                description=f"Extend timeline due to {trigger_type.value}",
                affected_tasks=[],
                affected_agents=[],
                estimated_impact="low",
                confidence=0.9,
                parameters={'extension_hours': context.get('delay_hours', 8)}
            )
        
        # Add other strategies as needed
        return None
    
    def _get_affected_tasks(self, context: Dict, plan: Plan) -> List[str]:
        """Get list of affected task IDs from context"""
        task_id = context.get('task_id')
        if task_id:
            return [task_id]
        
        # Look for task references in description
        description = context.get('description', '')
        task_refs = self._extract_task_references(description)
        
        # Match with actual task IDs (simplified)
        task_ids = []
        for task in plan.tasks:
            if any(ref.lower() in task.title.lower() for ref in task_refs):
                task_ids.append(task.id)
        
        return task_ids[:3]  # Limit to 3 tasks
    
    def _apply_adaptation_action(self, plan: Plan, action: AdaptationAction) -> Plan:
        """Apply adaptation action to plan"""
        try:
            if action.strategy == AdaptationStrategy.RESCHEDULE:
                return self._apply_reschedule(plan, action)
            elif action.strategy == AdaptationStrategy.REASSIGN:
                return self._apply_reassign(plan, action)
            elif action.strategy == AdaptationStrategy.TIMELINE_EXTENSION:
                return self._apply_timeline_extension(plan, action)
            elif action.strategy == AdaptationStrategy.PARALLEL_EXECUTION:
                return self._apply_parallel_execution(plan, action)
            else:
                logger.warning(f"Unknown adaptation strategy: {action.strategy}")
                return plan
                
        except Exception as e:
            logger.error(f"Failed to apply adaptation action {action.action_id}: {str(e)}")
            return plan
    
    def _apply_reschedule(self, plan: Plan, action: AdaptationAction) -> Plan:
        """Apply rescheduling action"""
        delay_hours = action.parameters.get('delay_hours', 2)
        
        for task_id in action.affected_tasks:
            # Find task in plan
            for task in plan.tasks:
                if task.id == task_id and task.deadline:
                    # Delay the task
                    task.deadline = task.deadline + timedelta(hours=delay_hours)
                    
                    # Update schedule if present
                    if task_id in plan.schedule.start_times:
                        original_start = plan.schedule.start_times[task_id]
                        plan.schedule.start_times[task_id] = original_start + timedelta(hours=delay_hours)
                        plan.schedule.end_times[task_id] = plan.schedule.end_times[task_id] + timedelta(hours=delay_hours)
        
        return plan
    
    def _apply_reassign(self, plan: Plan, action: AdaptationAction) -> Plan:
        """Apply reassignment action"""
        # Simplified reassignment - would need access to ConstraintSolver
        for task_id in action.affected_tasks:
            if task_id in plan.schedule.task_assignments:
                # For now, just mark for reassignment
                logger.info(f"Task {task_id} marked for reassignment")
        
        return plan
    
    def _apply_timeline_extension(self, plan: Plan, action: AdaptationAction) -> Plan:
        """Apply timeline extension"""
        extension_hours = action.parameters.get('extension_hours', 8)
        
        # Extend overall timeline
        if plan.timeline.estimated_completion:
            plan.timeline.estimated_completion += timedelta(hours=extension_hours)
        
        return plan
    
    def _apply_parallel_execution(self, plan: Plan, action: AdaptationAction) -> Plan:
        """Apply parallel execution strategy"""
        max_parallel = action.parameters.get('max_parallel_tasks', 3)
        
        # Remove dependencies between affected tasks to enable parallel execution
        affected_set = set(action.affected_tasks)
        
        for task in plan.tasks:
            if task.id in affected_set:
                # Remove dependencies to other affected tasks
                task.dependencies = [dep for dep in task.dependencies if dep not in affected_set]
        
        return plan
    
    def learn_from_completed_plans(self, plans: List[Plan]) -> Dict[str, Any]:
        """
        Learn adaptation patterns from completed plans
        
        Args:
            plans: List of completed plans
            
        Returns:
            Learning statistics
        """
        start_time = datetime.now()
        logger.info(f"Learning from {len(plans)} completed plans")
        
        if not self.learning_enabled:
            logger.info("Learning disabled, skipping pattern extraction")
            return {'patterns_learned': 0, 'reason': 'learning_disabled'}
        
        try:
            patterns_learned = 0
            
            for plan in plans:
                if plan.adaptation_history:
                    patterns_learned += self._extract_patterns_from_plan(plan)
            
            # Consolidate similar patterns
            if SKLEARN_AVAILABLE and len(self.adaptation_patterns) > 10:
                consolidated = self._consolidate_patterns()
                patterns_learned += consolidated
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Learning completed in {duration:.2f}s, learned {patterns_learned} patterns")
            
            return {
                'patterns_learned': patterns_learned,
                'total_patterns': len(self.adaptation_patterns),
                'learning_duration': duration,
                'plans_processed': len(plans)
            }
            
        except Exception as e:
            logger.error(f"Learning from plans failed: {str(e)}")
            return {'patterns_learned': 0, 'error': str(e)}
    
    def _extract_patterns_from_plan(self, plan: Plan) -> int:
        """Extract adaptation patterns from a single plan"""
        patterns_extracted = 0
        
        for adaptation in plan.adaptation_history:
            triggers = adaptation.get('triggers', [])
            actions = adaptation.get('actions', [])
            
            for trigger_type_str, context in triggers:
                try:
                    trigger_type = AdaptationTrigger(trigger_type_str)
                    
                    # Find successful strategies (simplified - assume all actions were successful)
                    successful_strategies = []
                    for action_dict in actions:
                        strategy_str = action_dict.get('strategy')
                        if strategy_str:
                            successful_strategies.append(AdaptationStrategy(strategy_str))
                    
                    if successful_strategies:
                        pattern = self._create_adaptation_pattern(
                            trigger_type, context, successful_strategies, plan.plan_id
                        )
                        self.adaptation_patterns[pattern.pattern_id] = pattern
                        patterns_extracted += 1
                        
                except (ValueError, KeyError) as e:
                    logger.warning(f"Failed to extract pattern from trigger {trigger_type_str}: {str(e)}")
        
        return patterns_extracted
    
    def _create_adaptation_pattern(
        self, 
        trigger_type: AdaptationTrigger, 
        context: Dict, 
        strategies: List[AdaptationStrategy],
        plan_id: str
    ) -> AdaptationPattern:
        """Create new adaptation pattern"""
        pattern_id = str(uuid.uuid4())
        
        return AdaptationPattern(
            pattern_id=pattern_id,
            trigger_type=trigger_type,
            context_features=context,
            successful_strategies=strategies,
            success_rate=1.0,  # Initial success rate
            usage_count=1,
            confidence_score=0.7,  # Initial confidence
            learned_from_plans=[plan_id],
            created_at=datetime.now()
        )
    
    def _consolidate_patterns(self) -> int:
        """Consolidate similar patterns using clustering"""
        if not SKLEARN_AVAILABLE:
            return 0
        
        try:
            # Group patterns by trigger type
            pattern_groups = {}
            for pattern in self.adaptation_patterns.values():
                trigger = pattern.trigger_type
                if trigger not in pattern_groups:
                    pattern_groups[trigger] = []
                pattern_groups[trigger].append(pattern)
            
            consolidated_count = 0
            
            for trigger_type, patterns in pattern_groups.items():
                if len(patterns) < 3:
                    continue  # Need at least 3 patterns to cluster
                
                # Extract features for clustering
                features = []
                for pattern in patterns:
                    feature_vector = self._pattern_to_feature_vector(pattern)
                    features.append(feature_vector)
                
                # Simple pure Python clustering - group similar patterns
                cluster_labels = self._simple_cluster_patterns(features, min(len(patterns) // 2, 5))
                
                # Merge patterns in same cluster
                clusters = {}
                for i, label in enumerate(cluster_labels):
                    if label not in clusters:
                        clusters[label] = []
                    clusters[label].append(patterns[i])
                
                for cluster_patterns in clusters.values():
                    if len(cluster_patterns) > 1:
                        merged_pattern = self._merge_patterns(cluster_patterns)
                        
                        # Remove old patterns and add merged one
                        for old_pattern in cluster_patterns:
                            del self.adaptation_patterns[old_pattern.pattern_id]
                        
                        self.adaptation_patterns[merged_pattern.pattern_id] = merged_pattern
                        consolidated_count += 1
            
            return consolidated_count
            
        except Exception as e:
            logger.error(f"Pattern consolidation failed: {str(e)}")
            return 0
    
    def _simple_cluster_patterns(self, features: List[List[float]], max_clusters: int) -> List[int]:
        """Simple pure Python clustering using distance-based grouping"""
        if not features or len(features) <= 1:
            return [0] * len(features)
        
        # Start with each point as its own cluster
        clusters = [[i] for i in range(len(features))]
        
        # Merge closest clusters until we have max_clusters or less
        while len(clusters) > max_clusters:
            min_distance = float('inf')
            merge_idx = (0, 1)
            
            # Find two closest clusters
            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    # Calculate average distance between clusters
                    total_distance = 0
                    count = 0
                    for idx1 in clusters[i]:
                        for idx2 in clusters[j]:
                            distance = self._euclidean_distance(features[idx1], features[idx2])
                            total_distance += distance
                            count += 1
                    
                    avg_distance = total_distance / count if count > 0 else float('inf')
                    if avg_distance < min_distance:
                        min_distance = avg_distance
                        merge_idx = (i, j)
            
            # Merge the two closest clusters
            i, j = merge_idx
            clusters[i].extend(clusters[j])
            clusters.pop(j)
        
        # Convert cluster assignments to labels
        labels = [0] * len(features)
        for cluster_id, cluster in enumerate(clusters):
            for point_idx in cluster:
                labels[point_idx] = cluster_id
        
        return labels
    
    def _euclidean_distance(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate Euclidean distance between two vectors"""
        if len(vec1) != len(vec2):
            return float('inf')
        return sum((a - b) ** 2 for a, b in zip(vec1, vec2)) ** 0.5

    def _pattern_to_feature_vector(self, pattern: AdaptationPattern) -> List[float]:
        """Convert pattern to feature vector for clustering"""
        features = []
        
        # Context features
        context_features = self._extract_features(pattern.context_features)
        feature_keys = sorted(context_features.keys())
        features.extend([context_features.get(key, 0.0) for key in feature_keys])
        
        # Strategy features (one-hot encoding)
        all_strategies = list(AdaptationStrategy)
        for strategy in all_strategies:
            features.append(1.0 if strategy in pattern.successful_strategies else 0.0)
        
        # Performance features
        features.extend([
            pattern.success_rate,
            pattern.confidence_score,
            min(pattern.usage_count / 10.0, 1.0)  # Normalized usage count
        ])
        
        return features
    
    def _merge_patterns(self, patterns: List[AdaptationPattern]) -> AdaptationPattern:
        """Merge multiple similar patterns into one"""
        # Use the pattern with highest success rate as base
        base_pattern = max(patterns, key=lambda p: p.success_rate)
        
        # Combine strategies
        all_strategies = set()
        for pattern in patterns:
            all_strategies.update(pattern.successful_strategies)
        
        # Calculate combined metrics
        total_usage = sum(p.usage_count for p in patterns)
        weighted_success_rate = sum(p.success_rate * p.usage_count for p in patterns) / total_usage
        avg_confidence = sum(p.confidence_score for p in patterns) / len(patterns)
        
        # Combine learned_from_plans
        all_plans = set()
        for pattern in patterns:
            all_plans.update(pattern.learned_from_plans)
        
        return AdaptationPattern(
            pattern_id=str(uuid.uuid4()),
            trigger_type=base_pattern.trigger_type,
            context_features=base_pattern.context_features,  # Use base context
            successful_strategies=list(all_strategies),
            success_rate=weighted_success_rate,
            usage_count=total_usage,
            confidence_score=avg_confidence,
            learned_from_plans=list(all_plans),
            created_at=min(p.created_at for p in patterns),
            last_used=max((p.last_used for p in patterns if p.last_used), default=None)
        )
    
    def predict_plan_success(self, plan: Plan) -> float:
        """
        Predict likelihood of plan success based on learned patterns
        
        Args:
            plan: Plan to evaluate
            
        Returns:
            Success probability (0.0 to 1.0)
        """
        try:
            if not self.adaptation_patterns:
                return 0.5  # Neutral prediction with no patterns
            
            # Extract plan features
            plan_features = self._extract_plan_features(plan)
            
            # Calculate similarity to successful patterns
            success_scores = []
            
            for pattern in self.adaptation_patterns.values():
                if pattern.success_rate > 0.7:  # Only consider successful patterns
                    pattern_features = self._extract_features(pattern.context_features)
                    similarity = self._calculate_feature_similarity(plan_features, pattern_features)
                    weighted_score = similarity * pattern.success_rate * (pattern.confidence_score)
                    success_scores.append(weighted_score)
            
            if success_scores:
                # Average of top 3 similar successful patterns
                top_scores = sorted(success_scores, reverse=True)[:3]
                prediction = sum(top_scores) / len(top_scores)
                return max(0.0, min(1.0, prediction))  # Clamp to [0, 1]
            else:
                return 0.5  # Neutral prediction
                
        except Exception as e:
            logger.error(f"Plan success prediction failed: {str(e)}")
            return 0.5
    
    def _extract_plan_features(self, plan: Plan) -> Dict[str, float]:
        """Extract features from plan for prediction"""
        features = {}
        
        # Task count features
        features['total_tasks'] = len(plan.tasks)
        features['avg_estimated_hours'] = sum(t.estimated_hours for t in plan.tasks) / len(plan.tasks) if plan.tasks else 0
        
        # Task type distribution
        task_types = {}
        for task in plan.tasks:
            task_type = task.task_type.value
            task_types[task_type] = task_types.get(task_type, 0) + 1
        
        for task_type in TaskType:
            features[f'tasks_{task_type.value}'] = task_types.get(task_type.value, 0)
        
        # Dependency complexity
        total_dependencies = sum(len(task.dependencies) for task in plan.tasks)
        features['avg_dependencies'] = total_dependencies / len(plan.tasks) if plan.tasks else 0
        
        # Timeline features
        if plan.timeline:
            features['total_hours'] = plan.timeline.total_hours
            features['critical_path_length'] = len(plan.timeline.critical_path)
        
        # Schedule features
        if plan.schedule:
            features['agent_count'] = len(set(plan.schedule.task_assignments.values()))
            features['avg_agent_workload'] = (
                sum(plan.schedule.agent_workloads.values()) / len(plan.schedule.agent_workloads)
                if plan.schedule.agent_workloads else 0
            )
        
        return features