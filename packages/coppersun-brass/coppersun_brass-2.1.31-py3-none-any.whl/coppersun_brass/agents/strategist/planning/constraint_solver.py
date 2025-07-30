"""
Planning Intelligence Engine - Constraint Solver
Implements resource allocation optimization using pure Python heuristic algorithms
for multi-agent task scheduling and constraint satisfaction.
Blood Oath compliant - no heavy dependencies required.
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json

# Pure Python constraint solving - Blood Oath compliant
# No heavy dependencies required

from .planning_algorithms import PlanningTask, TaskType, TaskStatus

logger = logging.getLogger(__name__)


@dataclass
class Agent:
    """Agent model for constraint solving"""
    id: str
    name: str
    skills: List[str]
    max_concurrent_tasks: int
    hourly_capacity: float
    efficiency_rating: float  # 0.0 to 1.0
    specializations: List[str]
    current_workload: float = 0.0
    available_from: datetime = None
    
    def __post_init__(self):
        if self.available_from is None:
            self.available_from = datetime.now()
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['available_from'] = self.available_from.isoformat() if self.available_from else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Agent':
        data = data.copy()
        if data.get('available_from'):
            data['available_from'] = datetime.fromisoformat(data['available_from'])
        return cls(**data)


@dataclass
class Schedule:
    """Optimized schedule with resource allocations"""
    task_assignments: Dict[str, str]  # task_id -> agent_id
    start_times: Dict[str, datetime]  # task_id -> start_time
    end_times: Dict[str, datetime]    # task_id -> end_time
    agent_workloads: Dict[str, float] # agent_id -> total_hours
    total_cost: float
    total_duration_hours: float
    optimization_score: float
    conflicts_resolved: List[str]
    
    def to_dict(self) -> Dict:
        return {
            'task_assignments': self.task_assignments,
            'start_times': {k: v.isoformat() for k, v in self.start_times.items()},
            'end_times': {k: v.isoformat() for k, v in self.end_times.items()},
            'agent_workloads': self.agent_workloads,
            'total_cost': self.total_cost,
            'total_duration_hours': self.total_duration_hours,
            'optimization_score': self.optimization_score,
            'conflicts_resolved': self.conflicts_resolved
        }


@dataclass
class ConstraintViolation:
    """Represents a constraint violation"""
    violation_id: str
    constraint_type: str
    description: str
    severity: str
    affected_entities: List[str]
    suggested_fix: str


class OptimizationObjective(Enum):
    """Optimization objectives for constraint solving"""
    MINIMIZE_TIME = "minimize_time"
    MINIMIZE_COST = "minimize_cost"
    MAXIMIZE_EFFICIENCY = "maximize_efficiency"
    BALANCE_WORKLOAD = "balance_workload"


class ConstraintSolver:
    """Pure Python heuristic constraint solver for task scheduling"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.constraints: List[Dict] = []
        self.optimization_cache: Dict[str, Schedule] = {}
        
    def add_agent(self, agent: Agent) -> None:
        """Add an agent to the solver"""
        self.agents[agent.id] = agent
        logger.info(f"Added agent {agent.name} with skills: {agent.skills}")
    
    def add_constraint(self, constraint_type: str, constraint_data: Dict) -> None:
        """Add a constraint to the solver"""
        constraint = {
            'id': str(uuid.uuid4()),
            'type': constraint_type,
            'data': constraint_data,
            'created_at': datetime.now()
        }
        self.constraints.append(constraint)
        logger.info(f"Added {constraint_type} constraint")
    
    def solve_resource_allocation(
        self, 
        tasks: List[PlanningTask], 
        objective: OptimizationObjective = OptimizationObjective.MINIMIZE_TIME
    ) -> Schedule:
        """
        Solve resource allocation optimization problem
        
        Args:
            tasks: List of tasks to schedule
            objective: Optimization objective
            
        Returns:
            Optimized schedule
        """
        start_time = datetime.now()
        logger.info(f"Starting resource allocation optimization for {len(tasks)} tasks")
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(tasks, objective)
            if cache_key in self.optimization_cache:
                logger.info("Using cached optimization result")
                return self.optimization_cache[cache_key]
            
            # Use pure Python heuristic solver - Blood Oath compliant
            schedule = self._solve_with_heuristics(tasks, objective)
            
            # Cache the result
            self.optimization_cache[cache_key] = schedule
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Resource allocation completed in {duration:.2f}s")
            
            return schedule
            
        except Exception as e:
            logger.error(f"Resource allocation failed: {str(e)}")
            # Return fallback schedule
            return self._create_fallback_schedule(tasks)
    
    def _generate_cache_key(self, tasks: List[PlanningTask], objective: OptimizationObjective) -> str:
        """Generate cache key for optimization problem"""
        task_hash = hash(tuple(
            (task.id, task.estimated_hours, tuple(task.dependencies), tuple(task.required_skills))
            for task in sorted(tasks, key=lambda t: t.id)
        ))
        agent_hash = hash(tuple(
            (agent.id, agent.max_concurrent_tasks, agent.hourly_capacity, tuple(agent.skills))
            for agent in sorted(self.agents.values(), key=lambda a: a.id)
        ))
        return f"{task_hash}_{agent_hash}_{objective.value}"
    
    # All OR-Tools methods removed - using pure Python heuristic solver only
    def _solve_with_heuristics(self, tasks: List[PlanningTask], objective: OptimizationObjective) -> Schedule:
        """Pure Python heuristic constraint solver for task scheduling"""
        logger.info("Using heuristic constraint solver")
        
        # Sort tasks by priority and dependencies
        sorted_tasks = self._topological_sort_tasks(tasks)
        
        task_assignments = {}
        start_times = {}
        end_times = {}
        agent_workloads = {agent_id: 0.0 for agent_id in self.agents}
        agent_availability = {agent_id: datetime.now() for agent_id in self.agents}
        
        for task in sorted_tasks:
            # Find best agent for this task
            best_agent = self._find_best_agent(task, agent_availability, objective)
            
            if best_agent:
                task_assignments[task.id] = best_agent.id
                
                # Calculate start time (max of agent availability and dependency completion)
                start_time = agent_availability[best_agent.id]
                for dep_id in task.dependencies:
                    if dep_id in end_times:
                        start_time = max(start_time, end_times[dep_id])
                
                # Calculate end time
                duration = timedelta(hours=task.estimated_hours / best_agent.efficiency_rating)
                end_time = start_time + duration
                
                start_times[task.id] = start_time
                end_times[task.id] = end_time
                agent_workloads[best_agent.id] += task.estimated_hours
                agent_availability[best_agent.id] = end_time
        
        total_duration = (max(end_times.values()) - min(start_times.values())).total_seconds() / 3600 if end_times else 0
        
        return Schedule(
            task_assignments=task_assignments,
            start_times=start_times,
            end_times=end_times,
            agent_workloads=agent_workloads,
            total_cost=sum(agent_workloads.values()),
            total_duration_hours=total_duration,
            optimization_score=0.7,  # Lower score for heuristic solution
            conflicts_resolved=[]
        )
    
    def _topological_sort_tasks(self, tasks: List[PlanningTask]) -> List[PlanningTask]:
        """Sort tasks respecting dependencies"""
        # Simple topological sort implementation
        remaining = tasks.copy()
        sorted_tasks = []
        
        while remaining:
            # Find tasks with no unfulfilled dependencies
            ready_tasks = []
            completed_ids = {task.id for task in sorted_tasks}
            
            for task in remaining:
                if all(dep_id in completed_ids for dep_id in task.dependencies):
                    ready_tasks.append(task)
            
            if not ready_tasks:
                # Circular dependency or error - just take first remaining
                ready_tasks = [remaining[0]]
            
            # Sort ready tasks by priority
            ready_tasks.sort(key=lambda t: -t.priority)
            
            # Take highest priority task
            next_task = ready_tasks[0]
            sorted_tasks.append(next_task)
            remaining.remove(next_task)
        
        return sorted_tasks
    
    def _find_best_agent(self, task: PlanningTask, agent_availability: Dict, objective: OptimizationObjective) -> Optional[Agent]:
        """Find best agent for a task based on objective"""
        suitable_agents = []
        
        for agent in self.agents.values():
            # Check skill requirements
            if task.required_skills and not any(skill in agent.skills for skill in task.required_skills):
                continue
            
            # Check specialization bonus
            specialization_bonus = 1.0
            if any(spec in agent.specializations for spec in task.required_skills):
                specialization_bonus = 1.2
            
            suitable_agents.append((agent, specialization_bonus))
        
        if not suitable_agents:
            return None
        
        # Score agents based on objective
        if objective == OptimizationObjective.MINIMIZE_TIME:
            return max(suitable_agents, key=lambda x: x[0].efficiency_rating * x[1])[0]
        elif objective == OptimizationObjective.BALANCE_WORKLOAD:
            return min(suitable_agents, key=lambda x: x[0].current_workload)[0]
        else:
            return suitable_agents[0][0]  # Default: first suitable agent
    
    def _create_fallback_schedule(self, tasks: List[PlanningTask]) -> Schedule:
        """Create basic fallback schedule when optimization fails"""
        logger.warning("Creating fallback schedule due to optimization failure")
        
        task_assignments = {}
        start_times = {}
        end_times = {}
        agent_workloads = {}
        
        if self.agents:
            # Assign all tasks to first available agent
            first_agent = list(self.agents.values())[0]
            current_time = datetime.now()
            
            for task in tasks:
                task_assignments[task.id] = first_agent.id
                start_times[task.id] = current_time
                end_times[task.id] = current_time + timedelta(hours=task.estimated_hours)
                current_time = end_times[task.id]
            
            agent_workloads[first_agent.id] = sum(task.estimated_hours for task in tasks)
        
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
    
    def resolve_timeline_conflicts(self, schedule: Schedule, tasks: List[PlanningTask]) -> Schedule:
        """
        Resolve timeline conflicts in an existing schedule
        
        Args:
            schedule: Current schedule with potential conflicts
            tasks: List of tasks
            
        Returns:
            Updated schedule with conflicts resolved
        """
        logger.info("Resolving timeline conflicts")
        
        try:
            conflicts_resolved = []
            
            # Create task lookup
            task_lookup = {task.id: task for task in tasks}
            
            # Check for dependency violations
            for task_id, start_time in schedule.start_times.items():
                task = task_lookup.get(task_id)
                if not task:
                    continue
                
                for dep_id in task.dependencies:
                    if dep_id in schedule.end_times:
                        dep_end_time = schedule.end_times[dep_id]
                        if start_time < dep_end_time:
                            # Conflict: task starts before dependency ends
                            new_start_time = dep_end_time
                            duration = schedule.end_times[task_id] - start_time
                            
                            schedule.start_times[task_id] = new_start_time
                            schedule.end_times[task_id] = new_start_time + duration
                            
                            conflicts_resolved.append(f"Delayed task {task.title} to respect dependency")
            
            # Update optimization score based on conflicts resolved
            if conflicts_resolved:
                schedule.optimization_score *= 0.9  # Slight penalty for conflicts
                schedule.conflicts_resolved = conflicts_resolved
            
            return schedule
            
        except Exception as e:
            logger.error(f"Timeline conflict resolution failed: {str(e)}")
            return schedule
    
    def optimize_agent_workload(self, assignments: Dict[str, List[str]], tasks: List[PlanningTask]) -> Dict[str, List[str]]:
        """
        Optimize agent workload distribution
        
        Args:
            assignments: Current agent to task assignments
            tasks: List of tasks
            
        Returns:
            Optimized assignments
        """
        logger.info("Optimizing agent workload distribution")
        
        try:
            # Calculate current workloads
            task_lookup = {task.id: task for task in tasks}
            current_workloads = {}
            
            for agent_id, task_ids in assignments.items():
                workload = sum(task_lookup[task_id].estimated_hours for task_id in task_ids if task_id in task_lookup)
                current_workloads[agent_id] = workload
            
            # Find overloaded and underloaded agents
            avg_workload = sum(current_workloads.values()) / len(current_workloads) if current_workloads else 0
            overloaded = {agent_id: workload for agent_id, workload in current_workloads.items() if workload > avg_workload * 1.2}
            underloaded = {agent_id: workload for agent_id, workload in current_workloads.items() if workload < avg_workload * 0.8}
            
            # Reassign tasks from overloaded to underloaded agents
            optimized_assignments = assignments.copy()
            
            for overloaded_agent in overloaded:
                agent_tasks = optimized_assignments[overloaded_agent].copy()
                
                for task_id in agent_tasks:
                    task = task_lookup.get(task_id)
                    if not task:
                        continue
                    
                    # Find suitable underloaded agent
                    for underloaded_agent in underloaded:
                        underloaded_agent_obj = self.agents.get(underloaded_agent)
                        if (underloaded_agent_obj and 
                            any(skill in underloaded_agent_obj.skills for skill in task.required_skills)):
                            
                            # Move task
                            optimized_assignments[overloaded_agent].remove(task_id)
                            optimized_assignments[underloaded_agent].append(task_id)
                            
                            # Update workload tracking
                            current_workloads[overloaded_agent] -= task.estimated_hours
                            current_workloads[underloaded_agent] += task.estimated_hours
                            
                            break
                    
                    # Stop if workload is balanced
                    if current_workloads[overloaded_agent] <= avg_workload * 1.1:
                        break
            
            return optimized_assignments
            
        except Exception as e:
            logger.error(f"Agent workload optimization failed: {str(e)}")
            return assignments
    
    def validate_constraints(self, schedule: Schedule, tasks: List[PlanningTask]) -> List[ConstraintViolation]:
        """
        Validate schedule against all constraints
        
        Args:
            schedule: Schedule to validate
            tasks: List of tasks
            
        Returns:
            List of constraint violations
        """
        logger.info("Validating schedule constraints")
        
        violations = []
        task_lookup = {task.id: task for task in tasks}
        
        try:
            # Validate task assignments
            for task_id, agent_id in schedule.task_assignments.items():
                task = task_lookup.get(task_id)
                agent = self.agents.get(agent_id)
                
                if not task or not agent:
                    violations.append(ConstraintViolation(
                        violation_id=str(uuid.uuid4()),
                        constraint_type="assignment",
                        description=f"Invalid assignment: task {task_id} to agent {agent_id}",
                        severity="high",
                        affected_entities=[task_id, agent_id],
                        suggested_fix="Reassign to valid agent"
                    ))
                    continue
                
                # Check skill requirements
                if task.required_skills and not any(skill in agent.skills for skill in task.required_skills):
                    violations.append(ConstraintViolation(
                        violation_id=str(uuid.uuid4()),
                        constraint_type="skills",
                        description=f"Agent {agent.name} lacks required skills for task {task.title}",
                        severity="high",
                        affected_entities=[task_id, agent_id],
                        suggested_fix="Reassign to agent with required skills"
                    ))
            
            # Validate dependencies
            for task_id, start_time in schedule.start_times.items():
                task = task_lookup.get(task_id)
                if not task:
                    continue
                
                for dep_id in task.dependencies:
                    if dep_id in schedule.end_times:
                        dep_end_time = schedule.end_times[dep_id]
                        if start_time < dep_end_time:
                            violations.append(ConstraintViolation(
                                violation_id=str(uuid.uuid4()),
                                constraint_type="dependency",
                                description=f"Task {task.title} starts before dependency {dep_id} completes",
                                severity="critical",
                                affected_entities=[task_id, dep_id],
                                suggested_fix="Delay task start time"
                            ))
            
            # Validate agent capacity
            for agent_id, workload in schedule.agent_workloads.items():
                agent = self.agents.get(agent_id)
                if agent and workload > agent.hourly_capacity * 40:  # Assuming 40-hour work week
                    violations.append(ConstraintViolation(
                        violation_id=str(uuid.uuid4()),
                        constraint_type="capacity",
                        description=f"Agent {agent.name} is overallocated: {workload} hours",
                        severity="medium",
                        affected_entities=[agent_id],
                        suggested_fix="Redistribute tasks or extend timeline"
                    ))
            
            return violations
            
        except Exception as e:
            logger.error(f"Constraint validation failed: {str(e)}")
            return violations