"""
Planning Intelligence Engine - Intelligence Coordinator
Orchestrates all planning intelligence components for comprehensive
autonomous planning in Copper Alloy Brass.
"""

import uuid
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json

from .planning_algorithms import PlanningAlgorithms, PlanningTask, Timeline, TaskType
from .constraint_solver import ConstraintSolver, Schedule, Agent, OptimizationObjective
from .adaptation_engine import AdaptationEngine, Plan, AdaptationTrigger

logger = logging.getLogger(__name__)


@dataclass
class PlanningContext:
    """Context for comprehensive planning"""
    goals: List[str]
    constraints: Dict[str, Any]
    available_agents: List[Agent]
    existing_observations: List[Dict]
    timeline_constraints: Dict[str, Any]
    resource_constraints: Dict[str, Any]
    priority_weights: Dict[str, float]
    
    def to_dict(self) -> Dict:
        return {
            'goals': self.goals,
            'constraints': self.constraints,
            'available_agents': [agent.to_dict() for agent in self.available_agents],
            'existing_observations': self.existing_observations,
            'timeline_constraints': self.timeline_constraints,
            'resource_constraints': self.resource_constraints,
            'priority_weights': self.priority_weights
        }


@dataclass
class PlanningResult:
    """Result of comprehensive planning cycle"""
    plan: Plan
    confidence_score: float
    generation_time: float
    components_used: List[str]
    warnings: List[str]
    recommendations: List[str]
    
    def to_dict(self) -> Dict:
        return {
            'plan': self.plan.to_dict(),
            'confidence_score': self.confidence_score,
            'generation_time': self.generation_time,
            'components_used': self.components_used,
            'warnings': self.warnings,
            'recommendations': self.recommendations
        }


class IntelligenceCoordinator:
    """
    Orchestrates all planning intelligence components to provide
    comprehensive autonomous planning capabilities.
    """
    
    def __init__(self, 
                 planning_algorithms: Optional[PlanningAlgorithms] = None,
                 constraint_solver: Optional[ConstraintSolver] = None,
                 adaptation_engine: Optional[AdaptationEngine] = None):
        """
        Initialize coordinator with planning components
        
        Args:
            planning_algorithms: Goal decomposition and timeline generation
            constraint_solver: Resource allocation optimization
            adaptation_engine: Dynamic adaptation and learning
        """
        self.planning_algorithms = planning_algorithms or PlanningAlgorithms()
        self.constraint_solver = constraint_solver or ConstraintSolver()
        self.adaptation_engine = adaptation_engine or AdaptationEngine()
        
        self.planning_cache: Dict[str, PlanningResult] = {}
        self.active_plans: Dict[str, Plan] = {}
        self.coordination_history: List[Dict] = []
        
        # Integration with prediction engine and historical analyzer
        self.prediction_engine = None
        self.historical_analyzer = None
        
        logger.info("Intelligence coordinator initialized")
    
    def set_prediction_engine(self, prediction_engine):
        """Set prediction engine for integration"""
        self.prediction_engine = prediction_engine
        logger.info("Prediction engine integrated")
    
    def set_historical_analyzer(self, historical_analyzer):
        """Set historical analyzer for integration"""
        self.historical_analyzer = historical_analyzer
        logger.info("Historical analyzer integrated")
    
    async def generate_comprehensive_plan(self, goals: List[str], context: PlanningContext) -> PlanningResult:
        """
        Generate comprehensive plan using all intelligence components
        
        Args:
            goals: List of high-level goals
            context: Planning context with constraints and resources
            
        Returns:
            Complete planning result with confidence scoring
        """
        start_time = datetime.now()
        logger.info(f"Starting comprehensive planning for {len(goals)} goals")
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(goals, context)
            if cache_key in self.planning_cache:
                cached_result = self.planning_cache[cache_key]
                if self._is_cache_valid(cached_result):
                    logger.info("Using cached planning result")
                    return cached_result
            
            # Comprehensive planning workflow
            result = await self._execute_planning_workflow(goals, context)
            
            # Cache the result
            self.planning_cache[cache_key] = result
            
            # Store in active plans
            self.active_plans[result.plan.plan_id] = result.plan
            
            # Record coordination history
            self.coordination_history.append({
                'timestamp': datetime.now().isoformat(),
                'goals': goals,
                'plan_id': result.plan.plan_id,
                'confidence_score': result.confidence_score,
                'generation_time': result.generation_time
            })
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Comprehensive planning completed in {duration:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Comprehensive planning failed: {str(e)}")
            # Return fallback plan
            return await self._create_fallback_plan(goals, context)
    
    def _generate_cache_key(self, goals: List[str], context: PlanningContext) -> str:
        """Generate cache key for planning request"""
        goals_str = '|'.join(sorted(goals))
        constraints_str = json.dumps(context.constraints, sort_keys=True)
        agents_str = '|'.join(sorted(agent.id for agent in context.available_agents))
        
        cache_content = f"{goals_str}_{constraints_str}_{agents_str}"
        return str(hash(cache_content))
    
    def _is_cache_valid(self, cached_result: PlanningResult) -> bool:
        """Check if cached result is still valid"""
        # Cache expires after 1 hour
        cache_age = datetime.now() - datetime.fromisoformat(
            self.coordination_history[-1]['timestamp'] if self.coordination_history else datetime.now().isoformat()
        )
        return cache_age < timedelta(hours=1)
    
    async def _execute_planning_workflow(self, goals: List[str], context: PlanningContext) -> PlanningResult:
        """Execute comprehensive planning workflow"""
        start_time = datetime.now()
        components_used = []
        warnings = []
        recommendations = []
        
        # Step 1: Goal Decomposition
        logger.info("Step 1: Decomposing goals into tasks")
        all_tasks = []
        
        for goal in goals:
            try:
                goal_tasks = self.planning_algorithms.decompose_goal(goal, context.constraints)
                all_tasks.extend(goal_tasks)
                components_used.append("goal_decomposition")
                logger.info(f"Decomposed '{goal}' into {len(goal_tasks)} tasks")
            except Exception as e:
                warning = f"Failed to decompose goal '{goal}': {str(e)}"
                warnings.append(warning)
                logger.warning(warning)
        
        if not all_tasks:
            raise ValueError("No tasks generated from goal decomposition")
        
        # Step 2: Timeline Generation
        logger.info("Step 2: Generating initial timeline")
        try:
            timeline = self.planning_algorithms.generate_timeline(all_tasks)
            components_used.append("timeline_generation")
            logger.info(f"Generated timeline with {len(timeline.milestones)} milestones")
        except Exception as e:
            warning = f"Timeline generation failed: {str(e)}"
            warnings.append(warning)
            logger.warning(warning)
            # Create basic timeline
            timeline = Timeline(
                tasks=all_tasks,
                milestones=[],
                critical_path=[],
                estimated_completion=datetime.now() + timedelta(hours=sum(t.estimated_hours for t in all_tasks)),
                total_hours=sum(t.estimated_hours for t in all_tasks)
            )
        
        # Step 3: Conflict Detection
        logger.info("Step 3: Detecting planning conflicts")
        try:
            conflicts = self.planning_algorithms.detect_conflicts(all_tasks)
            if conflicts:
                warnings.extend([f"Planning conflict: {c.description}" for c in conflicts[:3]])
                recommendations.extend([c.suggested_resolution for c in conflicts[:3]])
                logger.warning(f"Detected {len(conflicts)} planning conflicts")
            components_used.append("conflict_detection")
        except Exception as e:
            warning = f"Conflict detection failed: {str(e)}"
            warnings.append(warning)
            logger.warning(warning)
        
        # Step 4: Resource Allocation
        logger.info("Step 4: Optimizing resource allocation")
        try:
            # Add agents to constraint solver
            for agent in context.available_agents:
                self.constraint_solver.add_agent(agent)
            
            # Determine optimization objective
            objective = self._determine_optimization_objective(context)
            
            # Solve resource allocation
            schedule = self.constraint_solver.solve_resource_allocation(all_tasks, objective)
            components_used.append("constraint_solving")
            logger.info(f"Resource allocation completed with score {schedule.optimization_score:.2f}")
            
            if schedule.optimization_score < 0.5:
                warnings.append("Resource allocation produced suboptimal results")
                recommendations.append("Consider adding more agents or extending timeline")
                
        except Exception as e:
            warning = f"Resource allocation failed: {str(e)}"
            warnings.append(warning)
            logger.warning(warning)
            # Create fallback schedule
            schedule = self._create_fallback_schedule(all_tasks, context.available_agents)
        
        # Step 5: Prediction Integration
        if self.prediction_engine:
            logger.info("Step 5: Integrating prediction data")
            try:
                predictions = await self._get_prediction_insights(all_tasks, timeline)
                if predictions:
                    components_used.append("prediction_integration")
                    # Apply prediction insights to planning
                    timeline, warnings_pred = self._apply_prediction_insights(timeline, predictions)
                    warnings.extend(warnings_pred)
            except Exception as e:
                warning = f"Prediction integration failed: {str(e)}"
                warnings.append(warning)
                logger.warning(warning)
        
        # Step 6: Historical Analysis Integration
        if self.historical_analyzer:
            logger.info("Step 6: Applying historical insights")
            try:
                historical_insights = await self._get_historical_insights(all_tasks)
                if historical_insights:
                    components_used.append("historical_analysis")
                    recommendations.extend(historical_insights.get('recommendations', []))
            except Exception as e:
                warning = f"Historical analysis failed: {str(e)}"
                warnings.append(warning)
                logger.warning(warning)
        
        # Step 7: Plan Optimization
        logger.info("Step 7: Final plan optimization")
        try:
            optimized_tasks = self.planning_algorithms.optimize_execution_order(all_tasks)
            all_tasks = optimized_tasks
            components_used.append("execution_optimization")
        except Exception as e:
            warning = f"Execution optimization failed: {str(e)}"
            warnings.append(warning)
            logger.warning(warning)
        
        # Step 8: Create Final Plan
        plan = Plan(
            plan_id=str(uuid.uuid4()),
            tasks=all_tasks,
            schedule=schedule,
            timeline=timeline,
            status="generated",
            created_at=datetime.now(),
            last_modified=datetime.now()
        )
        
        # Step 9: Predict Plan Success
        logger.info("Step 9: Predicting plan success")
        try:
            success_probability = self.adaptation_engine.predict_plan_success(plan)
            components_used.append("success_prediction")
            
            if success_probability < 0.3:
                warnings.append(f"Low success probability ({success_probability:.1%})")
                recommendations.append("Consider simplifying goals or adding resources")
            elif success_probability > 0.8:
                recommendations.append(f"High success probability ({success_probability:.1%}) - plan looks excellent")
                
        except Exception as e:
            warning = f"Success prediction failed: {str(e)}"
            warnings.append(warning)
            logger.warning(warning)
            success_probability = 0.5  # Neutral prediction
        
        # Calculate overall confidence score
        confidence_score = self._calculate_confidence_score(
            components_used, warnings, schedule.optimization_score, success_probability
        )
        
        generation_time = (datetime.now() - start_time).total_seconds()
        
        return PlanningResult(
            plan=plan,
            confidence_score=confidence_score,
            generation_time=generation_time,
            components_used=components_used,
            warnings=warnings,
            recommendations=recommendations
        )
    
    def _determine_optimization_objective(self, context: PlanningContext) -> OptimizationObjective:
        """Determine optimization objective from context"""
        weights = context.priority_weights
        
        if weights.get('time', 0) > 0.7:
            return OptimizationObjective.MINIMIZE_TIME
        elif weights.get('cost', 0) > 0.7:
            return OptimizationObjective.MINIMIZE_COST
        elif weights.get('workload_balance', 0) > 0.7:
            return OptimizationObjective.BALANCE_WORKLOAD
        else:
            return OptimizationObjective.MINIMIZE_TIME  # Default
    
    def _create_fallback_schedule(self, tasks: List[PlanningTask], agents: List[Agent]) -> Schedule:
        """Create fallback schedule when constraint solving fails"""
        logger.warning("Creating fallback schedule")
        
        task_assignments = {}
        start_times = {}
        end_times = {}
        agent_workloads = {}
        
        if agents:
            # Simple round-robin assignment
            current_time = datetime.now()
            agent_availability = {agent.id: current_time for agent in agents}
            
            for i, task in enumerate(tasks):
                agent = agents[i % len(agents)]
                task_assignments[task.id] = agent.id
                
                start_time = agent_availability[agent.id]
                end_time = start_time + timedelta(hours=task.estimated_hours)
                
                start_times[task.id] = start_time
                end_times[task.id] = end_time
                agent_availability[agent.id] = end_time
                
                if agent.id not in agent_workloads:
                    agent_workloads[agent.id] = 0
                agent_workloads[agent.id] += task.estimated_hours
        
        return Schedule(
            task_assignments=task_assignments,
            start_times=start_times,
            end_times=end_times,
            agent_workloads=agent_workloads,
            total_cost=sum(task.estimated_hours for task in tasks),
            total_duration_hours=sum(task.estimated_hours for task in tasks),
            optimization_score=0.3,  # Low score for fallback
            conflicts_resolved=[]
        )
    
    async def _get_prediction_insights(self, tasks: List[PlanningTask], timeline: Timeline) -> Dict:
        """Get insights from prediction engine"""
        if not self.prediction_engine:
            return {}
        
        try:
            # Mock prediction integration - replace with actual prediction engine calls
            return {
                'timeline_risks': [],
                'resource_risks': [],
                'recommendations': []
            }
        except Exception as e:
            logger.error(f"Failed to get prediction insights: {str(e)}")
            return {}
    
    def _apply_prediction_insights(self, timeline: Timeline, predictions: Dict) -> Tuple[Timeline, List[str]]:
        """Apply prediction insights to timeline"""
        warnings = []
        
        # Apply timeline risk adjustments
        timeline_risks = predictions.get('timeline_risks', [])
        for risk in timeline_risks:
            if risk.get('severity') == 'high':
                # Add buffer to timeline
                timeline.estimated_completion += timedelta(hours=risk.get('buffer_hours', 4))
                warnings.append(f"Added buffer for timeline risk: {risk.get('description')}")
        
        return timeline, warnings
    
    async def _get_historical_insights(self, tasks: List[PlanningTask]) -> Dict:
        """Get insights from historical analyzer"""
        if not self.historical_analyzer:
            return {}
        
        try:
            # Mock historical integration - replace with actual historical analyzer calls
            return {
                'similar_projects': [],
                'success_factors': [],
                'recommendations': ['Consider adding code review checkpoints']
            }
        except Exception as e:
            logger.error(f"Failed to get historical insights: {str(e)}")
            return {}
    
    def _calculate_confidence_score(self, 
                                  components_used: List[str], 
                                  warnings: List[str], 
                                  optimization_score: float,
                                  success_probability: float) -> float:
        """Calculate overall confidence score for the plan"""
        # Base score from component usage
        component_score = len(components_used) / 9  # Max 9 components
        
        # Penalty for warnings
        warning_penalty = min(len(warnings) * 0.1, 0.5)  # Max 50% penalty
        
        # Integration scores
        optimization_weight = 0.3
        success_weight = 0.4
        component_weight = 0.3
        
        confidence = (
            component_weight * component_score +
            optimization_weight * optimization_score +
            success_weight * success_probability
        ) - warning_penalty
        
        return max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
    
    async def _create_fallback_plan(self, goals: List[str], context: PlanningContext) -> PlanningResult:
        """Create basic fallback plan when comprehensive planning fails"""
        logger.warning("Creating fallback plan due to comprehensive planning failure")
        
        # Create minimal tasks
        tasks = []
        for i, goal in enumerate(goals):
            task = PlanningTask(
                id=str(uuid.uuid4()),
                title=f"Implement: {goal}",
                description=f"Basic implementation task for: {goal}",
                task_type=TaskType.IMPLEMENTATION,
                estimated_hours=8.0,
                dependencies=[],
                required_skills=["implementation"],
                priority=90 - (i * 10)
            )
            tasks.append(task)
        
        # Create basic timeline
        timeline = Timeline(
            tasks=tasks,
            milestones=[],
            critical_path=[],
            estimated_completion=datetime.now() + timedelta(hours=sum(t.estimated_hours for t in tasks)),
            total_hours=sum(t.estimated_hours for t in tasks)
        )
        
        # Create basic schedule
        schedule = self._create_fallback_schedule(tasks, context.available_agents)
        
        # Create fallback plan
        plan = Plan(
            plan_id=str(uuid.uuid4()),
            tasks=tasks,
            schedule=schedule,
            timeline=timeline,
            status="fallback",
            created_at=datetime.now(),
            last_modified=datetime.now()
        )
        
        return PlanningResult(
            plan=plan,
            confidence_score=0.2,  # Low confidence for fallback
            generation_time=1.0,
            components_used=["fallback"],
            warnings=["Comprehensive planning failed, using basic fallback plan"],
            recommendations=["Review goals and constraints, ensure all components are properly configured"]
        )
    
    async def coordinate_planning_cycle(self, 
                                      observations: List[Dict], 
                                      existing_plan: Optional[Plan] = None) -> PlanningResult:
        """
        Coordinate a full planning cycle including adaptation
        
        Args:
            observations: Current observations from DCP
            existing_plan: Existing plan to adapt (if any)
            
        Returns:
            Updated or new planning result
        """
        start_time = datetime.now()
        logger.info("Starting coordinated planning cycle")
        
        try:
            if existing_plan:
                # Adaptation flow
                logger.info(f"Adapting existing plan {existing_plan.plan_id}")
                
                # Detect adaptation triggers
                triggers = self.adaptation_engine.detect_adaptation_triggers(existing_plan, observations)
                
                if triggers:
                    logger.info(f"Found {len(triggers)} adaptation triggers")
                    # Adapt the plan
                    adapted_plan = self.adaptation_engine.adapt_plan(existing_plan, triggers)
                    
                    # Update active plans
                    self.active_plans[adapted_plan.plan_id] = adapted_plan
                    
                    return PlanningResult(
                        plan=adapted_plan,
                        confidence_score=0.8,  # High confidence for adaptation
                        generation_time=(datetime.now() - start_time).total_seconds(),
                        components_used=["adaptation_engine"],
                        warnings=[],
                        recommendations=["Plan adapted based on current conditions"]
                    )
                else:
                    logger.info("No adaptation triggers found, plan is current")
                    return PlanningResult(
                        plan=existing_plan,
                        confidence_score=0.9,  # Very high confidence for current plan
                        generation_time=(datetime.now() - start_time).total_seconds(),
                        components_used=["trigger_detection"],
                        warnings=[],
                        recommendations=["Plan is current, no changes needed"]
                    )
            else:
                # New planning flow - extract goals from observations
                goals = self._extract_goals_from_observations(observations)
                
                if not goals:
                    goals = ["Address current project observations"]
                
                # Create planning context from observations
                context = self._create_context_from_observations(observations)
                
                # Generate comprehensive plan
                result = await self.generate_comprehensive_plan(goals, context)
                
                return result
                
        except Exception as e:
            logger.error(f"Planning cycle coordination failed: {str(e)}")
            # Return minimal result
            return PlanningResult(
                plan=existing_plan or Plan(
                    plan_id=str(uuid.uuid4()),
                    tasks=[],
                    schedule=Schedule({}, {}, {}, {}, 0, 0, 0, []),
                    timeline=Timeline([], [], [], datetime.now(), 0),
                    status="error",
                    created_at=datetime.now(),
                    last_modified=datetime.now()
                ),
                confidence_score=0.1,
                generation_time=(datetime.now() - start_time).total_seconds(),
                components_used=[],
                warnings=[f"Planning cycle failed: {str(e)}"],
                recommendations=["Check system configuration and try again"]
            )
    
    def _extract_goals_from_observations(self, observations: List[Dict]) -> List[str]:
        """Extract goals from observation descriptions"""
        goals = []
        
        # Look for implementation gaps and high-priority observations
        for obs in observations:
            if obs.get('type') == 'implementation_gap' and obs.get('priority', 0) > 80:
                summary = obs.get('summary', '')
                if 'missing' in summary.lower() or 'need' in summary.lower():
                    # Extract goal from summary
                    goal = self._extract_goal_from_summary(summary)
                    if goal and goal not in goals:
                        goals.append(goal)
        
        return goals[:5]  # Limit to 5 goals
    
    def _extract_goal_from_summary(self, summary: str) -> Optional[str]:
        """Extract actionable goal from observation summary"""
        # Simple goal extraction patterns
        summary_lower = summary.lower()
        
        if 'missing' in summary_lower:
            # Extract what's missing
            if 'missing' in summary_lower:
                parts = summary.split('missing', 1)
                if len(parts) > 1:
                    missing_part = parts[1].strip()
                    return f"Add {missing_part.split('.')[0].strip()}"
        
        if 'implement' in summary_lower:
            # Extract implementation requirement
            if 'implement' in summary_lower:
                parts = summary.split('implement', 1)
                if len(parts) > 1:
                    impl_part = parts[1].strip()
                    return f"Implement {impl_part.split('.')[0].strip()}"
        
        if 'need' in summary_lower:
            # Extract need
            if 'need' in summary_lower:
                parts = summary.split('need', 1)
                if len(parts) > 1:
                    need_part = parts[1].strip()
                    return f"Address {need_part.split('.')[0].strip()}"
        
        return None
    
    def _create_context_from_observations(self, observations: List[Dict]) -> PlanningContext:
        """Create planning context from observations"""
        # Default agents (would normally come from agent registry)
        default_agents = [
            Agent(
                id="claude",
                name="Claude AI",
                skills=["implementation", "testing", "documentation", "research"],
                max_concurrent_tasks=3,
                hourly_capacity=8.0,
                efficiency_rating=0.9,
                specializations=["ai", "planning", "analysis"]
            ),
            Agent(
                id="human",
                name="Human Developer",
                skills=["implementation", "review", "architecture", "deployment"],
                max_concurrent_tasks=2,
                hourly_capacity=6.0,
                efficiency_rating=0.8,
                specializations=["system_design", "integration"]
            )
        ]
        
        # Extract constraints from high-priority observations
        constraints = {}
        high_priority_obs = [obs for obs in observations if obs.get('priority', 0) > 90]
        
        if high_priority_obs:
            constraints['urgent_items'] = len(high_priority_obs)
            constraints['critical_observations'] = [obs.get('summary') for obs in high_priority_obs[:3]]
        
        # Set priority weights based on observation types
        priority_weights = {
            'time': 0.6,  # Moderate time focus
            'quality': 0.8,  # High quality focus
            'workload_balance': 0.4  # Some workload balance
        }
        
        return PlanningContext(
            goals=[],  # Will be filled by caller
            constraints=constraints,
            available_agents=default_agents,
            existing_observations=observations,
            timeline_constraints={'flexible': True},
            resource_constraints={'agent_availability': 'normal'},
            priority_weights=priority_weights
        )
    
    def integrate_prediction_data(self, predictions: Dict) -> None:
        """
        Integrate prediction data into planning intelligence
        
        Args:
            predictions: Prediction data from prediction engine
        """
        logger.info("Integrating prediction data into planning intelligence")
        
        try:
            # Store prediction data for use in planning
            if not hasattr(self, 'prediction_data'):
                self.prediction_data = {}
            
            self.prediction_data.update(predictions)
            
            # Apply prediction insights to active plans
            for plan_id, plan in self.active_plans.items():
                self._apply_predictions_to_plan(plan, predictions)
                
        except Exception as e:
            logger.error(f"Prediction data integration failed: {str(e)}")
    
    def _apply_predictions_to_plan(self, plan: Plan, predictions: Dict) -> None:
        """Apply prediction insights to a specific plan"""
        try:
            # Update task priorities based on predictions
            timeline_predictions = predictions.get('timeline', {})
            
            for task in plan.tasks:
                task_predictions = timeline_predictions.get(task.id, {})
                risk_level = task_predictions.get('risk_level', 'medium')
                
                if risk_level == 'high':
                    # Increase priority for high-risk tasks
                    task.priority = min(100, task.priority + 10)
                elif risk_level == 'low':
                    # Slightly decrease priority for low-risk tasks
                    task.priority = max(0, task.priority - 5)
            
            plan.last_modified = datetime.now()
            
        except Exception as e:
            logger.error(f"Failed to apply predictions to plan {plan.plan_id}: {str(e)}")
    
    def trigger_plan_adaptation(self, triggers: List[str], plan_id: Optional[str] = None) -> Optional[Plan]:
        """
        Trigger plan adaptation based on external triggers
        
        Args:
            triggers: List of trigger descriptions
            plan_id: Specific plan ID to adapt (optional)
            
        Returns:
            Adapted plan if successful
        """
        logger.info(f"Triggering plan adaptation with {len(triggers)} external triggers")
        
        try:
            # Find target plan
            target_plan = None
            if plan_id and plan_id in self.active_plans:
                target_plan = self.active_plans[plan_id]
            elif self.active_plans:
                # Use most recent plan
                target_plan = max(self.active_plans.values(), key=lambda p: p.last_modified)
            
            if not target_plan:
                logger.warning("No active plan found for adaptation")
                return None
            
            # Convert triggers to adaptation triggers
            adaptation_triggers = []
            for trigger_desc in triggers:
                trigger_type, context = self._parse_external_trigger(trigger_desc)
                adaptation_triggers.append((trigger_type, context))
            
            # Apply adaptation
            adapted_plan = self.adaptation_engine.adapt_plan(target_plan, adaptation_triggers)
            
            # Update active plans
            self.active_plans[adapted_plan.plan_id] = adapted_plan
            
            return adapted_plan
            
        except Exception as e:
            logger.error(f"Plan adaptation trigger failed: {str(e)}")
            return None
    
    def _parse_external_trigger(self, trigger_desc: str) -> Tuple[AdaptationTrigger, Dict]:
        """Parse external trigger description into adaptation trigger"""
        trigger_desc_lower = trigger_desc.lower()
        
        # Map keywords to trigger types
        if any(keyword in trigger_desc_lower for keyword in ['failed', 'error', 'broken']):
            return AdaptationTrigger.TASK_FAILED, {'description': trigger_desc}
        elif any(keyword in trigger_desc_lower for keyword in ['deadline', 'late', 'overdue']):
            return AdaptationTrigger.DEADLINE_MISSED, {'description': trigger_desc}
        elif any(keyword in trigger_desc_lower for keyword in ['resource', 'agent', 'unavailable']):
            return AdaptationTrigger.RESOURCE_UNAVAILABLE, {'description': trigger_desc}
        elif any(keyword in trigger_desc_lower for keyword in ['scope', 'requirement', 'change']):
            return AdaptationTrigger.SCOPE_CHANGE, {'description': trigger_desc}
        elif any(keyword in trigger_desc_lower for keyword in ['priority', 'urgent', 'critical']):
            return AdaptationTrigger.PRIORITY_SHIFT, {'description': trigger_desc}
        elif any(keyword in trigger_desc_lower for keyword in ['dependency', 'blocked', 'waiting']):
            return AdaptationTrigger.DEPENDENCY_CHANGED, {'description': trigger_desc}
        elif any(keyword in trigger_desc_lower for keyword in ['slow', 'performance', 'delayed']):
            return AdaptationTrigger.PERFORMANCE_DEGRADATION, {'description': trigger_desc}
        else:
            return AdaptationTrigger.EXTERNAL_CONSTRAINT, {'description': trigger_desc}
    
    def get_planning_status(self) -> Dict[str, Any]:
        """Get current status of planning intelligence coordinator"""
        return {
            'active_plans': len(self.active_plans),
            'cached_results': len(self.planning_cache),
            'coordination_history': len(self.coordination_history),
            'components_available': {
                'planning_algorithms': self.planning_algorithms is not None,
                'constraint_solver': self.constraint_solver is not None,
                'adaptation_engine': self.adaptation_engine is not None,
                'prediction_engine': self.prediction_engine is not None,
                'historical_analyzer': self.historical_analyzer is not None
            },
            'last_planning': self.coordination_history[-1] if self.coordination_history else None
        }
    
    def clear_cache(self) -> None:
        """Clear planning cache"""
        self.planning_cache.clear()
        logger.info("Planning cache cleared")
    
    def export_planning_data(self) -> Dict[str, Any]:
        """Export planning data for analysis or backup"""
        return {
            'active_plans': {pid: plan.to_dict() for pid, plan in self.active_plans.items()},
            'coordination_history': self.coordination_history,
            'adaptation_patterns': {
                pid: pattern.to_dict() 
                for pid, pattern in self.adaptation_engine.adaptation_patterns.items()
            },
            'export_timestamp': datetime.now().isoformat()
        }
        