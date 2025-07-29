"""
Planning Intelligence Engine - Core Planning Algorithms
Implements STRIPS-style planning with goal decomposition, timeline generation,
and conflict detection for Copper Alloy Brass autonomous planning.
"""

import json
import re
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import networkx as nx
import logging

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Task types for planning classification"""
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    RESEARCH = "research"
    REFACTORING = "refactoring"
    DEPLOYMENT = "deployment"
    REVIEW = "review"


class TaskStatus(Enum):
    """Task execution status"""
    PLANNED = "planned"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PlanningTask:
    """Enhanced task model for planning algorithms"""
    id: str
    title: str
    description: str
    task_type: TaskType
    estimated_hours: float
    dependencies: List[str]
    required_skills: List[str]
    priority: int
    status: TaskStatus = TaskStatus.PLANNED
    agent_assignment: Optional[str] = None
    deadline: Optional[datetime] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['task_type'] = self.task_type.value
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['deadline'] = self.deadline.isoformat() if self.deadline else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PlanningTask':
        """Create from dictionary"""
        data = data.copy()
        data['task_type'] = TaskType(data['task_type'])
        data['status'] = TaskStatus(data['status'])
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('deadline'):
            data['deadline'] = datetime.fromisoformat(data['deadline'])
        return cls(**data)


@dataclass
class Timeline:
    """Project timeline with milestones and dependencies"""
    tasks: List[PlanningTask]
    milestones: List[Dict]
    critical_path: List[str]
    estimated_completion: datetime
    total_hours: float
    
    def to_dict(self) -> Dict:
        return {
            'tasks': [task.to_dict() for task in self.tasks],
            'milestones': self.milestones,
            'critical_path': self.critical_path,
            'estimated_completion': self.estimated_completion.isoformat(),
            'total_hours': self.total_hours
        }


@dataclass
class Conflict:
    """Represents a planning conflict"""
    conflict_id: str
    conflict_type: str  # 'resource', 'dependency', 'timeline'
    description: str
    affected_tasks: List[str]
    severity: str  # 'low', 'medium', 'high', 'critical'
    suggested_resolution: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


class PlanningAlgorithms:
    """Core planning algorithms for Copper Alloy Brass intelligence engine"""
    
    def __init__(self):
        self.dependency_graph = nx.DiGraph()
        self.goal_templates = self._load_goal_templates()
        
    def _load_goal_templates(self) -> Dict:
        """Load goal decomposition templates"""
        return {
            "add_authentication": {
                "tasks": [
                    {
                        "title": "Design authentication schema",
                        "type": "implementation",
                        "estimated_hours": 2.0,
                        "skills": ["database", "security"]
                    },
                    {
                        "title": "Implement user registration",
                        "type": "implementation", 
                        "estimated_hours": 4.0,
                        "skills": ["backend", "api"]
                    },
                    {
                        "title": "Implement login/logout",
                        "type": "implementation",
                        "estimated_hours": 3.0,
                        "skills": ["backend", "api"]
                    },
                    {
                        "title": "Add password reset functionality",
                        "type": "implementation",
                        "estimated_hours": 2.5,
                        "skills": ["backend", "email"]
                    },
                    {
                        "title": "Write authentication tests",
                        "type": "testing",
                        "estimated_hours": 3.0,
                        "skills": ["testing", "security"]
                    },
                    {
                        "title": "Document authentication API",
                        "type": "documentation",
                        "estimated_hours": 1.5,
                        "skills": ["documentation"]
                    }
                ],
                "dependencies": [
                    ("Design authentication schema", "Implement user registration"),
                    ("Design authentication schema", "Implement login/logout"),
                    ("Implement user registration", "Add password reset functionality"),
                    ("Implement login/logout", "Write authentication tests"),
                    ("Write authentication tests", "Document authentication API")
                ]
            },
            "implement_feature": {
                "tasks": [
                    {
                        "title": "Research feature requirements",
                        "type": "research",
                        "estimated_hours": 1.5,
                        "skills": ["research"]
                    },
                    {
                        "title": "Design feature architecture",
                        "type": "implementation",
                        "estimated_hours": 2.0,
                        "skills": ["architecture", "design"]
                    },
                    {
                        "title": "Implement core functionality",
                        "type": "implementation",
                        "estimated_hours": 6.0,
                        "skills": ["backend", "frontend"]
                    },
                    {
                        "title": "Write feature tests",
                        "type": "testing",
                        "estimated_hours": 3.0,
                        "skills": ["testing"]
                    },
                    {
                        "title": "Update documentation",
                        "type": "documentation",
                        "estimated_hours": 1.0,
                        "skills": ["documentation"]
                    }
                ],
                "dependencies": [
                    ("Research feature requirements", "Design feature architecture"),
                    ("Design feature architecture", "Implement core functionality"),
                    ("Implement core functionality", "Write feature tests"),
                    ("Write feature tests", "Update documentation")
                ]
            }
        }
    
    def decompose_goal(self, goal: str, context: Dict = None) -> List[PlanningTask]:
        """
        Decompose a high-level goal into executable tasks
        
        Args:
            goal: Natural language goal description
            context: Additional context for decomposition
            
        Returns:
            List of planning tasks
        """
        start_time = datetime.now()
        logger.info(f"Starting goal decomposition for: {goal}")
        
        try:
            # Normalize goal for template matching
            normalized_goal = self._normalize_goal(goal)
            
            # Find matching template or use generic decomposition
            template = self._find_goal_template(normalized_goal)
            
            if template:
                tasks = self._create_tasks_from_template(template, goal, context)
            else:
                tasks = self._generic_goal_decomposition(goal, context)
            
            # Add dependencies and validate
            tasks = self._add_task_dependencies(tasks, template)
            self._validate_task_decomposition(tasks)
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Goal decomposition completed in {duration:.2f}s, generated {len(tasks)} tasks")
            
            return tasks
            
        except Exception as e:
            logger.error(f"Goal decomposition failed: {str(e)}")
            raise
    
    def _normalize_goal(self, goal: str) -> str:
        """Normalize goal text for template matching"""
        # Remove common prefixes/suffixes and normalize
        normalized = goal.lower().strip()
        normalized = re.sub(r'^(add|implement|create|build)\s+', '', normalized)
        normalized = re.sub(r'\s+(feature|functionality|system)$', '', normalized)
        return normalized
    
    def _find_goal_template(self, normalized_goal: str) -> Optional[Dict]:
        """Find matching goal template"""
        for template_key, template in self.goal_templates.items():
            if template_key in normalized_goal:
                return template
        return None
    
    def _create_tasks_from_template(self, template: Dict, original_goal: str, context: Dict) -> List[PlanningTask]:
        """Create tasks from goal template"""
        tasks = []
        
        for i, task_def in enumerate(template['tasks']):
            task = PlanningTask(
                id=str(uuid.uuid4()),
                title=task_def['title'],
                description=f"Part of goal: {original_goal}",
                task_type=TaskType(task_def['type']),
                estimated_hours=task_def['estimated_hours'],
                dependencies=[],  # Added later
                required_skills=task_def['skills'],
                priority=100 - (i * 10)  # Decreasing priority
            )
            tasks.append(task)
            
        return tasks
    
    def _generic_goal_decomposition(self, goal: str, context: Dict) -> List[PlanningTask]:
        """Generic goal decomposition when no template matches"""
        # Basic decomposition pattern
        tasks = [
            PlanningTask(
                id=str(uuid.uuid4()),
                title=f"Research requirements for: {goal}",
                description=f"Research and analyze requirements for implementing: {goal}",
                task_type=TaskType.RESEARCH,
                estimated_hours=2.0,
                dependencies=[],
                required_skills=["research"],
                priority=95
            ),
            PlanningTask(
                id=str(uuid.uuid4()),
                title=f"Design solution for: {goal}",
                description=f"Design technical solution and architecture for: {goal}",
                task_type=TaskType.IMPLEMENTATION,
                estimated_hours=3.0,
                dependencies=[],
                required_skills=["architecture", "design"],
                priority=90
            ),
            PlanningTask(
                id=str(uuid.uuid4()),
                title=f"Implement: {goal}",
                description=f"Core implementation of: {goal}",
                task_type=TaskType.IMPLEMENTATION,
                estimated_hours=8.0,
                dependencies=[],
                required_skills=["implementation"],
                priority=85
            ),
            PlanningTask(
                id=str(uuid.uuid4()),
                title=f"Test: {goal}",
                description=f"Write and execute tests for: {goal}",
                task_type=TaskType.TESTING,
                estimated_hours=4.0,
                dependencies=[],
                required_skills=["testing"],
                priority=80
            )
        ]
        
        # Add sequential dependencies
        for i in range(len(tasks) - 1):
            tasks[i + 1].dependencies.append(tasks[i].id)
            
        return tasks
    
    def _add_task_dependencies(self, tasks: List[PlanningTask], template: Optional[Dict]) -> List[PlanningTask]:
        """Add dependencies between tasks"""
        if not template or 'dependencies' not in template:
            return tasks
            
        # Create title to task mapping
        title_to_task = {task.title: task for task in tasks}
        
        # Add dependencies from template
        for dep_from, dep_to in template['dependencies']:
            if dep_from in title_to_task and dep_to in title_to_task:
                from_task = title_to_task[dep_from]
                to_task = title_to_task[dep_to]
                if from_task.id not in to_task.dependencies:
                    to_task.dependencies.append(from_task.id)
                    
        return tasks
    
    def _validate_task_decomposition(self, tasks: List[PlanningTask]) -> None:
        """Validate task decomposition for consistency"""
        if not tasks:
            raise ValueError("Goal decomposition produced no tasks")
            
        # Check for circular dependencies
        task_ids = {task.id for task in tasks}
        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    logger.warning(f"Task {task.id} has invalid dependency: {dep_id}")
        
        # Build dependency graph for cycle detection
        graph = nx.DiGraph()
        for task in tasks:
            graph.add_node(task.id)
            for dep_id in task.dependencies:
                if dep_id in task_ids:
                    graph.add_edge(dep_id, task.id)
        
        if not nx.is_directed_acyclic_graph(graph):
            raise ValueError("Task dependencies contain cycles")
    
    def generate_timeline(self, tasks: List[PlanningTask]) -> Timeline:
        """
        Generate project timeline with critical path analysis
        
        Args:
            tasks: List of planning tasks
            
        Returns:
            Timeline with critical path and milestones
        """
        start_time = datetime.now()
        logger.info(f"Generating timeline for {len(tasks)} tasks")
        
        try:
            # Build dependency graph
            graph = self._build_dependency_graph(tasks)
            
            # Calculate critical path
            critical_path = self._calculate_critical_path(graph, tasks)
            
            # Schedule tasks
            scheduled_tasks = self._schedule_tasks(tasks, graph)
            
            # Identify milestones
            milestones = self._identify_milestones(scheduled_tasks)
            
            # Calculate total duration
            total_hours = sum(task.estimated_hours for task in tasks)
            estimated_completion = self._calculate_completion_date(scheduled_tasks)
            
            timeline = Timeline(
                tasks=scheduled_tasks,
                milestones=milestones,
                critical_path=critical_path,
                estimated_completion=estimated_completion,
                total_hours=total_hours
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Timeline generation completed in {duration:.2f}s")
            
            return timeline
            
        except Exception as e:
            logger.error(f"Timeline generation failed: {str(e)}")
            raise
    
    def _build_dependency_graph(self, tasks: List[PlanningTask]) -> nx.DiGraph:
        """Build NetworkX graph from task dependencies"""
        graph = nx.DiGraph()
        
        # Add all tasks as nodes
        for task in tasks:
            graph.add_node(task.id, task=task)
            
        # Add dependency edges
        for task in tasks:
            for dep_id in task.dependencies:
                graph.add_edge(dep_id, task.id)
                
        return graph
    
    def _calculate_critical_path(self, graph: nx.DiGraph, tasks: List[PlanningTask]) -> List[str]:
        """Calculate critical path using longest path algorithm"""
        try:
            # Create task lookup
            task_lookup = {task.id: task for task in tasks}
            
            # Calculate longest path (critical path)
            if nx.is_directed_acyclic_graph(graph):
                # Find start nodes (no dependencies)
                start_nodes = [node for node in graph.nodes() if graph.in_degree(node) == 0]
                # Find end nodes (no dependents)
                end_nodes = [node for node in graph.nodes() if graph.out_degree(node) == 0]
                
                longest_path = []
                max_duration = 0
                
                for start in start_nodes:
                    for end in end_nodes:
                        try:
                            path = nx.shortest_path(graph, start, end)
                            duration = sum(task_lookup[node].estimated_hours for node in path)
                            if duration > max_duration:
                                max_duration = duration
                                longest_path = path
                        except nx.NetworkXNoPath:
                            continue
                            
                return longest_path
            else:
                logger.warning("Dependency graph contains cycles, cannot calculate critical path")
                return []
                
        except Exception as e:
            logger.error(f"Critical path calculation failed: {str(e)}")
            return []
    
    def _schedule_tasks(self, tasks: List[PlanningTask], graph: nx.DiGraph) -> List[PlanningTask]:
        """Schedule tasks using topological sort"""
        try:
            # Topological sort for scheduling order
            if nx.is_directed_acyclic_graph(graph):
                schedule_order = list(nx.topological_sort(graph))
                
                # Create task lookup
                task_lookup = {task.id: task for task in tasks}
                
                # Schedule tasks
                scheduled_tasks = []
                current_time = datetime.now()
                
                for task_id in schedule_order:
                    if task_id in task_lookup:
                        task = task_lookup[task_id]
                        
                        # Calculate earliest start time based on dependencies
                        earliest_start = current_time
                        for dep_id in task.dependencies:
                            if dep_id in task_lookup:
                                dep_task = task_lookup[dep_id]
                                if dep_task.deadline:
                                    earliest_start = max(earliest_start, dep_task.deadline)
                        
                        # Set task deadline
                        task.deadline = earliest_start + timedelta(hours=task.estimated_hours)
                        scheduled_tasks.append(task)
                        
                return scheduled_tasks
            else:
                logger.warning("Cannot schedule tasks due to circular dependencies")
                return tasks
                
        except Exception as e:
            logger.error(f"Task scheduling failed: {str(e)}")
            return tasks
    
    def _identify_milestones(self, tasks: List[PlanningTask]) -> List[Dict]:
        """Identify project milestones"""
        milestones = []
        
        # Group tasks by type for milestone identification
        task_groups = {}
        for task in tasks:
            task_type = task.task_type.value
            if task_type not in task_groups:
                task_groups[task_type] = []
            task_groups[task_type].append(task)
        
        # Create milestones for each completed task type
        for task_type, type_tasks in task_groups.items():
            if type_tasks:
                latest_deadline = max(task.deadline for task in type_tasks if task.deadline)
                milestones.append({
                    'name': f"{task_type.title()} Complete",
                    'date': latest_deadline.isoformat() if latest_deadline else None,
                    'task_count': len(type_tasks),
                    'type': task_type
                })
        
        return sorted(milestones, key=lambda m: m['date'] or '')
    
    def _calculate_completion_date(self, tasks: List[PlanningTask]) -> datetime:
        """Calculate overall project completion date"""
        if not tasks:
            return datetime.now()
            
        deadlines = [task.deadline for task in tasks if task.deadline]
        if deadlines:
            return max(deadlines)
        else:
            # Fallback: current time + total hours
            total_hours = sum(task.estimated_hours for task in tasks)
            return datetime.now() + timedelta(hours=total_hours)
    
    def detect_conflicts(self, tasks: List[PlanningTask], agent_assignments: Dict[str, List[str]] = None) -> List[Conflict]:
        """
        Detect conflicts in the planned schedule
        
        Args:
            tasks: List of planning tasks
            agent_assignments: Optional agent to task assignments
            
        Returns:
            List of detected conflicts
        """
        start_time = datetime.now()
        logger.info(f"Detecting conflicts in {len(tasks)} tasks")
        
        conflicts = []
        
        try:
            # Detect dependency conflicts
            conflicts.extend(self._detect_dependency_conflicts(tasks))
            
            # Detect timeline conflicts
            conflicts.extend(self._detect_timeline_conflicts(tasks))
            
            # Detect resource conflicts if agent assignments provided
            if agent_assignments:
                conflicts.extend(self._detect_resource_conflicts(tasks, agent_assignments))
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Conflict detection completed in {duration:.2f}s, found {len(conflicts)} conflicts")
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Conflict detection failed: {str(e)}")
            return []
    
    def _detect_dependency_conflicts(self, tasks: List[PlanningTask]) -> List[Conflict]:
        """Detect circular and invalid dependencies"""
        conflicts = []
        
        # Build dependency graph
        graph = nx.DiGraph()
        task_lookup = {task.id: task for task in tasks}
        
        for task in tasks:
            graph.add_node(task.id)
            for dep_id in task.dependencies:
                if dep_id in task_lookup:
                    graph.add_edge(dep_id, task.id)
                else:
                    # Invalid dependency
                    conflicts.append(Conflict(
                        conflict_id=str(uuid.uuid4()),
                        conflict_type="dependency",
                        description=f"Task {task.title} has invalid dependency: {dep_id}",
                        affected_tasks=[task.id],
                        severity="high",
                        suggested_resolution="Remove invalid dependency or add missing task"
                    ))
        
        # Check for circular dependencies
        if not nx.is_directed_acyclic_graph(graph):
            try:
                cycles = list(nx.simple_cycles(graph))
                for cycle in cycles:
                    cycle_tasks = [task_lookup[task_id].title for task_id in cycle]
                    conflicts.append(Conflict(
                        conflict_id=str(uuid.uuid4()),
                        conflict_type="dependency",
                        description=f"Circular dependency detected: {' -> '.join(cycle_tasks)}",
                        affected_tasks=cycle,
                        severity="critical",
                        suggested_resolution="Remove one dependency to break the cycle"
                    ))
            except Exception as e:
                logger.error(f"Error detecting cycles: {str(e)}")
        
        return conflicts
    
    def _detect_timeline_conflicts(self, tasks: List[PlanningTask]) -> List[Conflict]:
        """Detect timeline scheduling conflicts"""
        conflicts = []
        
        # Check for tasks with impossible timelines
        for task in tasks:
            if task.deadline and task.deadline < datetime.now():
                conflicts.append(Conflict(
                    conflict_id=str(uuid.uuid4()),
                    conflict_type="timeline",
                    description=f"Task {task.title} has deadline in the past",
                    affected_tasks=[task.id],
                    severity="high",
                    suggested_resolution="Update deadline or mark task as completed"
                ))
            
            # Check dependency timeline consistency
            task_lookup = {t.id: t for t in tasks}
            for dep_id in task.dependencies:
                if dep_id in task_lookup:
                    dep_task = task_lookup[dep_id]
                    if (task.deadline and dep_task.deadline and 
                        task.deadline <= dep_task.deadline):
                        conflicts.append(Conflict(
                            conflict_id=str(uuid.uuid4()),
                            conflict_type="timeline",
                            description=f"Task {task.title} deadline conflicts with dependency {dep_task.title}",
                            affected_tasks=[task.id, dep_id],
                            severity="medium",
                            suggested_resolution="Adjust task deadlines to respect dependencies"
                        ))
        
        return conflicts
    
    def _detect_resource_conflicts(self, tasks: List[PlanningTask], agent_assignments: Dict[str, List[str]]) -> List[Conflict]:
        """Detect agent resource conflicts"""
        conflicts = []
        
        # Check for overallocated agents
        for agent_id, task_ids in agent_assignments.items():
            agent_tasks = [task for task in tasks if task.id in task_ids]
            
            # Check for overlapping deadlines
            for i, task1 in enumerate(agent_tasks):
                for task2 in agent_tasks[i+1:]:
                    if (task1.deadline and task2.deadline and
                        abs((task1.deadline - task2.deadline).total_seconds()) < 3600):  # Within 1 hour
                        conflicts.append(Conflict(
                            conflict_id=str(uuid.uuid4()),
                            conflict_type="resource",
                            description=f"Agent {agent_id} has overlapping tasks: {task1.title} and {task2.title}",
                            affected_tasks=[task1.id, task2.id],
                            severity="medium",
                            suggested_resolution="Reschedule tasks or reassign to different agents"
                        ))
            
            # Check for skill mismatches
            for task in agent_tasks:
                # This would require agent skill information - placeholder logic
                if task.required_skills and "advanced" in task.required_skills:
                    # Simulate skill mismatch detection
                    pass
        
        return conflicts
    
    def optimize_execution_order(self, tasks: List[PlanningTask]) -> List[PlanningTask]:
        """
        Optimize task execution order for efficiency
        
        Args:
            tasks: List of planning tasks
            
        Returns:
            Optimized task order
        """
        start_time = datetime.now()
        logger.info(f"Optimizing execution order for {len(tasks)} tasks")
        
        try:
            # Build dependency graph
            graph = self._build_dependency_graph(tasks)
            
            # Get topological order respecting dependencies
            if nx.is_directed_acyclic_graph(graph):
                topo_order = list(nx.topological_sort(graph))
                task_lookup = {task.id: task for task in tasks}
                
                # Create optimized order
                optimized_tasks = []
                for task_id in topo_order:
                    if task_id in task_lookup:
                        optimized_tasks.append(task_lookup[task_id])
                
                # Apply optimization heuristics within dependency constraints
                optimized_tasks = self._apply_optimization_heuristics(optimized_tasks, graph)
                
                duration = (datetime.now() - start_time).total_seconds()
                logger.info(f"Execution order optimization completed in {duration:.2f}s")
                
                return optimized_tasks
            else:
                logger.warning("Cannot optimize order due to circular dependencies")
                return tasks
                
        except Exception as e:
            logger.error(f"Execution order optimization failed: {str(e)}")
            return tasks
    
    def _apply_optimization_heuristics(self, tasks: List[PlanningTask], graph: nx.DiGraph) -> List[PlanningTask]:
        """Apply heuristics to optimize task order"""
        # Priority: high priority tasks first (within dependency constraints)
        # Duration: shorter tasks first to show early progress
        # Type: group similar task types for efficiency
        
        optimized = []
        remaining = tasks.copy()
        
        while remaining:
            # Find tasks with no unfulfilled dependencies
            available_tasks = []
            completed_ids = {task.id for task in optimized}
            
            for task in remaining:
                if all(dep_id in completed_ids for dep_id in task.dependencies):
                    available_tasks.append(task)
            
            if not available_tasks:
                # Fallback: add next task (shouldn't happen with DAG)
                available_tasks = [remaining[0]]
            
            # Sort available tasks by optimization criteria
            available_tasks.sort(key=lambda t: (
                -t.priority,  # High priority first
                t.estimated_hours,  # Short tasks first
                t.task_type.value  # Group by type
            ))
            
            # Take the best available task
            next_task = available_tasks[0]
            optimized.append(next_task)
            remaining.remove(next_task)
        
        return optimized