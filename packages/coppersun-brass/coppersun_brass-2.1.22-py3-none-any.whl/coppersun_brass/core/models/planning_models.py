"""
Copper Alloy Brass Planning Models - Sprint 8 Implementation
Data models for autonomous planning with validation and QA improvements
"""

import uuid
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Union, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================

class PlanType(Enum):
    """Types of autonomous plans"""
    REACTIVE = "reactive"          # Generated in response to observations
    PROACTIVE = "proactive"        # Generated from predictions
    ADAPTIVE = "adaptive"          # Modified based on changing conditions
    EMERGENCY = "emergency"        # Created for critical issues

class PlanStatus(Enum):
    """Plan execution status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    FAILED = "failed"

class TaskType(Enum):
    """Types of autonomous tasks"""
    OBSERVATION = "observation"
    RESEARCH = "research"
    IMPLEMENTATION = "implementation"
    VALIDATION = "validation"
    TESTING = "testing"
    SECURITY_FIX = "security_fix"
    OPTIMIZATION = "optimization"
    REFACTORING = "refactoring"
    DOCUMENTATION = "documentation"
    BUG_FIX = "bug_fix"
    GENERAL = "general"

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    FAILED = "failed"

class AgentType(Enum):
    """Available agent types"""
    HUMAN = "human"
    SCOUT = "scout"
    WATCH = "watch"
    STRATEGIST = "strategist"

class DependencyType(Enum):
    """Types of task dependencies"""
    STANDARD = "standard"          # Regular dependency
    HARD = "hard"                  # Must complete before starting
    SOFT = "soft"                  # Preferred but not required
    PREFERRED = "preferred"        # Nice to have sequencing

class EventType(Enum):
    """Planning event types"""
    PLAN_CREATED = "plan_created"
    PLAN_STARTED = "plan_started"
    PLAN_COMPLETED = "plan_completed"
    PLAN_FAILED = "plan_failed"
    TASK_ASSIGNED = "task_assigned"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_BLOCKED = "task_blocked"
    MILESTONE_REACHED = "milestone_reached"
    PRIORITY_UPDATED = "priority_updated"

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_uuid() -> str:
    """Generate a unique identifier"""
    return str(uuid.uuid4())

def validate_priority(priority: int) -> int:
    """Validate and clamp priority to valid range (0-100)"""
    if not isinstance(priority, (int, float)):
        logger.warning(f"Invalid priority type: {type(priority)}, defaulting to 50")
        return 50
    return max(0, min(100, int(priority)))

def validate_confidence(confidence: float) -> float:
    """Validate and clamp confidence to valid range (0.0-1.0)"""
    if not isinstance(confidence, (int, float)):
        logger.warning(f"Invalid confidence type: {type(confidence)}, defaulting to 0.5")
        return 0.5
    return max(0.0, min(1.0, float(confidence)))

def validate_effort(effort: float) -> float:
    """Validate effort estimate (minimum 0.1 hours)"""
    if not isinstance(effort, (int, float)):
        logger.warning(f"Invalid effort type: {type(effort)}, defaulting to 1.0")
        return 1.0
    return max(0.1, float(effort))

def safe_datetime_parse(dt_input: Union[str, datetime, None]) -> Optional[datetime]:
    """Safely parse datetime input with error handling"""
    if dt_input is None:
        return None
    
    if isinstance(dt_input, datetime):
        return dt_input
    
    if isinstance(dt_input, str):
        try:
            # Handle ISO format with Z suffix
            if dt_input.endswith('Z'):
                dt_input = dt_input[:-1] + '+00:00'
            return datetime.fromisoformat(dt_input)
        except ValueError:
            try:
                # Fallback to standard datetime parsing
                return datetime.strptime(dt_input, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                logger.warning(f"Unable to parse datetime: {dt_input}")
                return None
    
    logger.warning(f"Invalid datetime input type: {type(dt_input)}")
    return None

def validate_json_serializable(data: Any) -> Any:
    """Validate that data is JSON serializable"""
    try:
        json.dumps(data)
        return data
    except (TypeError, ValueError) as e:
        logger.warning(f"Data not JSON serializable: {e}, converting to string")
        return str(data)

# ============================================================================
# CORE DATA MODELS
# ============================================================================

@dataclass
class TaskTemplate:
    """Template for generating specific types of tasks"""
    name: str
    task_type: TaskType
    description_template: str
    default_effort: float = 2.0
    preferred_agent: AgentType = AgentType.HUMAN
    priority_modifier: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate fields after initialization"""
        if not self.name:
            raise ValueError("TaskTemplate name cannot be empty")
        
        if not isinstance(self.task_type, TaskType):
            if isinstance(self.task_type, str):
                try:
                    self.task_type = TaskType(self.task_type)
                except ValueError:
                    raise ValueError(f"Invalid task_type: {self.task_type}")
            else:
                raise ValueError(f"task_type must be TaskType or string, got {type(self.task_type)}")
        
        if not isinstance(self.preferred_agent, AgentType):
            if isinstance(self.preferred_agent, str):
                try:
                    self.preferred_agent = AgentType(self.preferred_agent)
                except ValueError:
                    raise ValueError(f"Invalid preferred_agent: {self.preferred_agent}")
            else:
                raise ValueError(f"preferred_agent must be AgentType or string, got {type(self.preferred_agent)}")
        
        self.default_effort = validate_effort(self.default_effort)
        self.priority_modifier = validate_priority(self.priority_modifier + 50) - 50  # Allow negative values
        self.metadata = validate_json_serializable(self.metadata)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'name': self.name,
            'task_type': self.task_type.value,
            'description_template': self.description_template,
            'default_effort': self.default_effort,
            'preferred_agent': self.preferred_agent.value,
            'priority_modifier': self.priority_modifier,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskTemplate':
        """Create from dictionary"""
        return cls(
            name=data['name'],
            task_type=TaskType(data['task_type']),
            description_template=data['description_template'],
            default_effort=data.get('default_effort', 2.0),
            preferred_agent=AgentType(data.get('preferred_agent', 'human')),
            priority_modifier=data.get('priority_modifier', 0),
            metadata=data.get('metadata', {})
        )

@dataclass
class Task:
    """Individual autonomous task with validation and tracking"""
    id: str = field(default_factory=generate_uuid)
    plan_id: Optional[str] = None
    parent_task_id: Optional[str] = None
    name: str = ""
    description: str = ""
    task_type: TaskType = TaskType.GENERAL
    priority_score: int = 50
    optimized_priority: Optional[int] = None
    estimated_effort: float = 2.0
    actual_effort: Optional[float] = None
    assigned_agent: AgentType = AgentType.HUMAN
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    progress_percentage: int = 0
    blocking_reason: Optional[str] = None
    completion_notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    source_observation_id: Optional[str] = None
    source_agent: Optional[str] = None
    generation_method: str = "automated"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate fields after initialization"""
        if not self.name:
            self.name = f"Task {self.id[:8]}"
        
        # Validate enums
        if not isinstance(self.task_type, TaskType):
            if isinstance(self.task_type, str):
                try:
                    self.task_type = TaskType(self.task_type)
                except ValueError:
                    logger.warning(f"Invalid task_type: {self.task_type}, defaulting to GENERAL")
                    self.task_type = TaskType.GENERAL
            else:
                self.task_type = TaskType.GENERAL
        
        if not isinstance(self.assigned_agent, AgentType):
            if isinstance(self.assigned_agent, str):
                try:
                    self.assigned_agent = AgentType(self.assigned_agent)
                except ValueError:
                    logger.warning(f"Invalid assigned_agent: {self.assigned_agent}, defaulting to HUMAN")
                    self.assigned_agent = AgentType.HUMAN
            else:
                self.assigned_agent = AgentType.HUMAN
        
        if not isinstance(self.status, TaskStatus):
            if isinstance(self.status, str):
                try:
                    self.status = TaskStatus(self.status)
                except ValueError:
                    logger.warning(f"Invalid status: {self.status}, defaulting to PENDING")
                    self.status = TaskStatus.PENDING
            else:
                self.status = TaskStatus.PENDING
        
        # Validate numeric fields
        self.priority_score = validate_priority(self.priority_score)
        if self.optimized_priority is not None:
            self.optimized_priority = validate_priority(self.optimized_priority)
        self.estimated_effort = validate_effort(self.estimated_effort)
        if self.actual_effort is not None:
            self.actual_effort = validate_effort(self.actual_effort)
        self.progress_percentage = max(0, min(100, int(self.progress_percentage or 0)))
        
        # Validate dependencies
        if not isinstance(self.dependencies, list):
            logger.warning(f"Dependencies must be list, got {type(self.dependencies)}")
            self.dependencies = []
        
        # Remove self-dependencies
        if self.id in self.dependencies:
            self.dependencies.remove(self.id)
            logger.warning(f"Removed self-dependency from task {self.id}")
        
        # Validate datetime fields
        if isinstance(self.created_at, str):
            self.created_at = safe_datetime_parse(self.created_at) or datetime.now()
        if isinstance(self.started_at, str):
            self.started_at = safe_datetime_parse(self.started_at)
        if isinstance(self.completed_at, str):
            self.completed_at = safe_datetime_parse(self.completed_at)
        if isinstance(self.due_date, str):
            self.due_date = safe_datetime_parse(self.due_date)
        
        # Validate metadata
        self.metadata = validate_json_serializable(self.metadata)
    
    def start_task(self) -> bool:
        """Mark task as started"""
        if self.status != TaskStatus.PENDING:
            logger.warning(f"Cannot start task {self.id} - current status: {self.status}")
            return False
        
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()
        logger.info(f"Task {self.id} started")
        return True
    
    def complete_task(self, completion_notes: Optional[str] = None, actual_effort: Optional[float] = None) -> bool:
        """Mark task as completed"""
        if self.status not in [TaskStatus.IN_PROGRESS, TaskStatus.PENDING]:
            logger.warning(f"Cannot complete task {self.id} - current status: {self.status}")
            return False
        
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.progress_percentage = 100
        
        if completion_notes:
            self.completion_notes = completion_notes
        if actual_effort is not None:
            self.actual_effort = validate_effort(actual_effort)
        
        logger.info(f"Task {self.id} completed")
        return True
    
    def block_task(self, reason: str) -> bool:
        """Mark task as blocked"""
        if self.status not in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
            logger.warning(f"Cannot block task {self.id} - current status: {self.status}")
            return False
        
        self.status = TaskStatus.BLOCKED
        self.blocking_reason = reason
        logger.info(f"Task {self.id} blocked: {reason}")
        return True
    
    def unblock_task(self) -> bool:
        """Unblock task"""
        if self.status != TaskStatus.BLOCKED:
            logger.warning(f"Cannot unblock task {self.id} - not currently blocked")
            return False
        
        self.status = TaskStatus.PENDING
        self.blocking_reason = None
        logger.info(f"Task {self.id} unblocked")
        return True
    
    def update_progress(self, percentage: int) -> bool:
        """Update task progress"""
        if self.status not in [TaskStatus.IN_PROGRESS, TaskStatus.PENDING]:
            logger.warning(f"Cannot update progress for task {self.id} - current status: {self.status}")
            return False
        
        self.progress_percentage = max(0, min(100, int(percentage)))
        
        # Auto-complete if 100%
        if self.progress_percentage == 100 and self.status != TaskStatus.COMPLETED:
            self.complete_task()
        
        return True
    
    def get_duration(self) -> Optional[timedelta]:
        """Get task duration if completed"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if not self.due_date or self.status == TaskStatus.COMPLETED:
            return False
        return datetime.now() > self.due_date
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'parent_task_id': self.parent_task_id,
            'name': self.name,
            'description': self.description,
            'task_type': self.task_type.value,
            'priority_score': self.priority_score,
            'optimized_priority': self.optimized_priority,
            'estimated_effort': self.estimated_effort,
            'actual_effort': self.actual_effort,
            'assigned_agent': self.assigned_agent.value,
            'dependencies': self.dependencies,
            'status': self.status.value,
            'progress_percentage': self.progress_percentage,
            'blocking_reason': self.blocking_reason,
            'completion_notes': self.completion_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'source_observation_id': self.source_observation_id,
            'source_agent': self.source_agent,
            'generation_method': self.generation_method,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create from dictionary"""
        return cls(
            id=data.get('id', generate_uuid()),
            plan_id=data.get('plan_id'),
            parent_task_id=data.get('parent_task_id'),
            name=data.get('name', ''),
            description=data.get('description', ''),
            task_type=data.get('task_type', TaskType.GENERAL),
            priority_score=data.get('priority_score', 50),
            optimized_priority=data.get('optimized_priority'),
            estimated_effort=data.get('estimated_effort', 2.0),
            actual_effort=data.get('actual_effort'),
            assigned_agent=data.get('assigned_agent', AgentType.HUMAN),
            dependencies=data.get('dependencies', []),
            status=data.get('status', TaskStatus.PENDING),
            progress_percentage=data.get('progress_percentage', 0),
            blocking_reason=data.get('blocking_reason'),
            completion_notes=data.get('completion_notes'),
            created_at=safe_datetime_parse(data.get('created_at')) or datetime.now(),
            started_at=safe_datetime_parse(data.get('started_at')),
            completed_at=safe_datetime_parse(data.get('completed_at')),
            due_date=safe_datetime_parse(data.get('due_date')),
            source_observation_id=data.get('source_observation_id'),
            source_agent=data.get('source_agent'),
            generation_method=data.get('generation_method', 'automated'),
            metadata=data.get('metadata', {})
        )

@dataclass
class Plan:
    """Autonomous development plan with goals and constraints"""
    id: str = field(default_factory=generate_uuid)
    project_id: str = ""
    plan_name: str = ""
    plan_type: PlanType = PlanType.REACTIVE
    plan_data: Dict[str, Any] = field(default_factory=dict)
    goals: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    status: PlanStatus = PlanStatus.ACTIVE
    confidence_score: float = 0.5
    priority_level: int = 50
    estimated_duration_hours: Optional[float] = None
    actual_duration_hours: Optional[float] = None
    success_metrics: Dict[str, Any] = field(default_factory=dict)
    failure_conditions: Dict[str, Any] = field(default_factory=dict)
    tasks: List[Task] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate fields after initialization"""
        if not self.plan_name:
            self.plan_name = f"Plan {self.id[:8]}"
        
        # Validate enums
        if not isinstance(self.plan_type, PlanType):
            if isinstance(self.plan_type, str):
                try:
                    self.plan_type = PlanType(self.plan_type)
                except ValueError:
                    logger.warning(f"Invalid plan_type: {self.plan_type}, defaulting to REACTIVE")
                    self.plan_type = PlanType.REACTIVE
            else:
                self.plan_type = PlanType.REACTIVE
        
        if not isinstance(self.status, PlanStatus):
            if isinstance(self.status, str):
                try:
                    self.status = PlanStatus(self.status)
                except ValueError:
                    logger.warning(f"Invalid status: {self.status}, defaulting to ACTIVE")
                    self.status = PlanStatus.ACTIVE
            else:
                self.status = PlanStatus.ACTIVE
        
        # Validate numeric fields
        self.confidence_score = validate_confidence(self.confidence_score)
        self.priority_level = validate_priority(self.priority_level)
        if self.estimated_duration_hours is not None:
            self.estimated_duration_hours = validate_effort(self.estimated_duration_hours)
        if self.actual_duration_hours is not None:
            self.actual_duration_hours = validate_effort(self.actual_duration_hours)
        
        # Validate lists and dicts
        if not isinstance(self.goals, list):
            logger.warning(f"Goals must be list, got {type(self.goals)}")
            self.goals = []
        
        self.plan_data = validate_json_serializable(self.plan_data)
        self.constraints = validate_json_serializable(self.constraints)
        self.success_metrics = validate_json_serializable(self.success_metrics)
        self.failure_conditions = validate_json_serializable(self.failure_conditions)
        self.metadata = validate_json_serializable(self.metadata)
        
        # Validate datetime fields
        if isinstance(self.created_at, str):
            self.created_at = safe_datetime_parse(self.created_at) or datetime.now()
        if isinstance(self.updated_at, str):
            self.updated_at = safe_datetime_parse(self.updated_at) or datetime.now()
        if isinstance(self.started_at, str):
            self.started_at = safe_datetime_parse(self.started_at)
        if isinstance(self.completed_at, str):
            self.completed_at = safe_datetime_parse(self.completed_at)
        
        # Validate tasks
        if not isinstance(self.tasks, list):
            logger.warning(f"Tasks must be list, got {type(self.tasks)}")
            self.tasks = []
        
        # Ensure all tasks have this plan's ID
        for task in self.tasks:
            if isinstance(task, Task):
                task.plan_id = self.id
            elif isinstance(task, dict):
                task['plan_id'] = self.id
    
    def add_task(self, task: Task) -> bool:
        """Add task to plan"""
        if not isinstance(task, Task):
            logger.error(f"Cannot add non-Task object to plan: {type(task)}")
            return False
        
        task.plan_id = self.id
        self.tasks.append(task)
        self.updated_at = datetime.now()
        logger.info(f"Added task {task.id} to plan {self.id}")
        return True
    
    def remove_task(self, task_id: str) -> bool:
        """Remove task from plan"""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks.pop(i)
                self.updated_at = datetime.now()
                logger.info(f"Removed task {task_id} from plan {self.id}")
                return True
        
        logger.warning(f"Task {task_id} not found in plan {self.id}")
        return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def start_plan(self) -> bool:
        """Start plan execution"""
        if self.status != PlanStatus.ACTIVE:
            logger.warning(f"Cannot start plan {self.id} - current status: {self.status}")
            return False
        
        self.started_at = datetime.now()
        self.updated_at = datetime.now()
        logger.info(f"Plan {self.id} started")
        return True
    
    def complete_plan(self) -> bool:
        """Mark plan as completed"""
        if self.status not in [PlanStatus.ACTIVE]:
            logger.warning(f"Cannot complete plan {self.id} - current status: {self.status}")
            return False
        
        # Check if all tasks are completed
        incomplete_tasks = [task for task in self.tasks if task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]]
        if incomplete_tasks:
            logger.warning(f"Cannot complete plan {self.id} - {len(incomplete_tasks)} tasks still incomplete")
            return False
        
        self.status = PlanStatus.COMPLETED
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Calculate actual duration
        if self.started_at:
            self.actual_duration_hours = (self.completed_at - self.started_at).total_seconds() / 3600
        
        logger.info(f"Plan {self.id} completed")
        return True
    
    def get_completion_percentage(self) -> float:
        """Calculate plan completion percentage"""
        if not self.tasks:
            return 0.0
        
        total_progress = sum(task.progress_percentage for task in self.tasks)
        return total_progress / len(self.tasks)
    
    def get_active_tasks(self) -> List[Task]:
        """Get currently active tasks"""
        return [task for task in self.tasks if task.status == TaskStatus.IN_PROGRESS]
    
    def get_blocked_tasks(self) -> List[Task]:
        """Get blocked tasks"""
        return [task for task in self.tasks if task.status == TaskStatus.BLOCKED]
    
    def get_pending_tasks(self) -> List[Task]:
        """Get pending tasks (ready to start)"""
        return [task for task in self.tasks if task.status == TaskStatus.PENDING]
    
    def get_duration(self) -> Optional[timedelta]:
        """Get plan duration if completed"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'plan_name': self.plan_name,
            'plan_type': self.plan_type.value,
            'plan_data': self.plan_data,
            'goals': self.goals,
            'constraints': self.constraints,
            'status': self.status.value,
            'confidence_score': self.confidence_score,
            'priority_level': self.priority_level,
            'estimated_duration_hours': self.estimated_duration_hours,
            'actual_duration_hours': self.actual_duration_hours,
            'success_metrics': self.success_metrics,
            'failure_conditions': self.failure_conditions,
            'tasks': [task.to_dict() for task in self.tasks],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_by': self.created_by,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Plan':
        """Create from dictionary"""
        # Parse tasks
        tasks = []
        for task_data in data.get('tasks', []):
            if isinstance(task_data, dict):
                tasks.append(Task.from_dict(task_data))
            elif isinstance(task_data, Task):
                tasks.append(task_data)
        
        return cls(
            id=data.get('id', generate_uuid()),
            project_id=data.get('project_id', ''),
            plan_name=data.get('plan_name', ''),
            plan_type=data.get('plan_type', PlanType.REACTIVE),
            plan_data=data.get('plan_data', {}),
            goals=data.get('goals', []),
            constraints=data.get('constraints', {}),
            status=data.get('status', PlanStatus.ACTIVE),
            confidence_score=data.get('confidence_score', 0.5),
            priority_level=data.get('priority_level', 50),
            estimated_duration_hours=data.get('estimated_duration_hours'),
            actual_duration_hours=data.get('actual_duration_hours'),
            success_metrics=data.get('success_metrics', {}),
            failure_conditions=data.get('failure_conditions', {}),
            tasks=tasks,
            created_at=safe_datetime_parse(data.get('created_at')) or datetime.now(),
            updated_at=safe_datetime_parse(data.get('updated_at')) or datetime.now(),
            started_at=safe_datetime_parse(data.get('started_at')),
            completed_at=safe_datetime_parse(data.get('completed_at')),
            created_by=data.get('created_by', 'system'),
            metadata=data.get('metadata', {})
        )

@dataclass
class TaskDependency:
    """Task dependency relationship"""
    id: str = field(default_factory=generate_uuid)
    task_id: str = ""
    depends_on_task_id: str = ""
    dependency_type: DependencyType = DependencyType.STANDARD
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate fields after initialization"""
        if not self.task_id:
            raise ValueError("task_id cannot be empty")
        if not self.depends_on_task_id:
            raise ValueError("depends_on_task_id cannot be empty")
        if self.task_id == self.depends_on_task_id:
            raise ValueError("Task cannot depend on itself")
        
        if not isinstance(self.dependency_type, DependencyType):
            if isinstance(self.dependency_type, str):
                try:
                    self.dependency_type = DependencyType(self.dependency_type)
                except ValueError:
                    logger.warning(f"Invalid dependency_type: {self.dependency_type}, defaulting to STANDARD")
                    self.dependency_type = DependencyType.STANDARD
            else:
                self.dependency_type = DependencyType.STANDARD
        
        if isinstance(self.created_at, str):
            self.created_at = safe_datetime_parse(self.created_at) or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'depends_on_task_id': self.depends_on_task_id,
            'dependency_type': self.dependency_type.value,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskDependency':
        """Create from dictionary"""
        return cls(
            id=data.get('id', generate_uuid()),
            task_id=data['task_id'],
            depends_on_task_id=data['depends_on_task_id'],
            dependency_type=data.get('dependency_type', DependencyType.STANDARD),
            created_at=safe_datetime_parse(data.get('created_at')) or datetime.now()
        )

@dataclass
class PlanningEvent:
    """Planning execution event for audit trail"""
    id: str = field(default_factory=generate_uuid)
    plan_id: Optional[str] = None
    task_id: Optional[str] = None
    event_type: EventType = EventType.PLAN_CREATED
    event_data: Dict[str, Any] = field(default_factory=dict)
    event_message: Optional[str] = None
    severity: str = "info"
    triggered_by: str = "system"
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    
    def __post_init__(self):
        """Validate fields after initialization"""
        if not isinstance(self.event_type, EventType):
            if isinstance(self.event_type, str):
                try:
                    self.event_type = EventType(self.event_type)
                except ValueError:
                    logger.warning(f"Invalid event_type: {self.event_type}, defaulting to PLAN_CREATED")
                    self.event_type = EventType.PLAN_CREATED
            else:
                self.event_type = EventType.PLAN_CREATED
        
        if self.severity not in ['debug', 'info', 'warning', 'error', 'critical']:
            logger.warning(f"Invalid severity: {self.severity}, defaulting to info")
            self.severity = 'info'
        
        self.event_data = validate_json_serializable(self.event_data)
        
        if isinstance(self.timestamp, str):
            self.timestamp = safe_datetime_parse(self.timestamp) or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'task_id': self.task_id,
            'event_type': self.event_type.value,
            'event_data': self.event_data,
            'event_message': self.event_message,
            'severity': self.severity,
            'triggered_by': self.triggered_by,
            'timestamp': self.timestamp.isoformat(),
            'correlation_id': self.correlation_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlanningEvent':
        """Create from dictionary"""
        return cls(
            id=data.get('id', generate_uuid()),
            plan_id=data.get('plan_id'),
            task_id=data.get('task_id'),
            event_type=data.get('event_type', EventType.PLAN_CREATED),
            event_data=data.get('event_data', {}),
            event_message=data.get('event_message'),
            severity=data.get('severity', 'info'),
            triggered_by=data.get('triggered_by', 'system'),
            timestamp=safe_datetime_parse(data.get('timestamp')) or datetime.now(),
            correlation_id=data.get('correlation_id')
        )

@dataclass 
class DependencyGraph:
    """Graph representation of task dependencies"""
    nodes: Dict[str, Task] = field(default_factory=dict)
    edges: List[TaskDependency] = field(default_factory=list)
    
    def add_task(self, task: Task) -> bool:
        """Add task to dependency graph"""
        if not isinstance(task, Task):
            logger.error(f"Cannot add non-Task to dependency graph: {type(task)}")
            return False
        
        self.nodes[task.id] = task
        return True
    
    def add_dependency(self, dependency: TaskDependency) -> bool:
        """Add dependency to graph"""
        if not isinstance(dependency, TaskDependency):
            logger.error(f"Cannot add non-TaskDependency to graph: {type(dependency)}")
            return False
        
        # Validate both tasks exist
        if dependency.task_id not in self.nodes:
            logger.error(f"Task {dependency.task_id} not found in graph")
            return False
        
        if dependency.depends_on_task_id not in self.nodes:
            logger.error(f"Dependency task {dependency.depends_on_task_id} not found in graph")
            return False
        
        # Check for cycles (simple check)
        if self._would_create_cycle(dependency):
            logger.error(f"Dependency would create cycle: {dependency.task_id} -> {dependency.depends_on_task_id}")
            return False
        
        self.edges.append(dependency)
        return True
    
    def _would_create_cycle(self, new_dependency: TaskDependency) -> bool:
        """Check if adding dependency would create cycle (simplified)"""
        # Simple cycle detection - check if depends_on_task_id eventually depends on task_id
        visited = set()
        
        def has_path(from_task: str, to_task: str) -> bool:
            if from_task == to_task:
                return True
            
            if from_task in visited:
                return False
            
            visited.add(from_task)
            
            # Find dependencies of from_task
            for edge in self.edges:
                if edge.task_id == from_task:
                    if has_path(edge.depends_on_task_id, to_task):
                        return True
            
            return False
        
        return has_path(new_dependency.depends_on_task_id, new_dependency.task_id)
    
    def get_dependencies(self, task_id: str) -> List[str]:
        """Get list of task IDs this task depends on"""
        dependencies = []
        for edge in self.edges:
            if edge.task_id == task_id:
                dependencies.append(edge.depends_on_task_id)
        return dependencies
    
    def get_dependents(self, task_id: str) -> List[str]:
        """Get list of task IDs that depend on this task"""
        dependents = []
        for edge in self.edges:
            if edge.depends_on_task_id == task_id:
                dependents.append(edge.task_id)
        return dependents
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'nodes': {task_id: task.to_dict() for task_id, task in self.nodes.items()},
            'edges': [edge.to_dict() for edge in self.edges]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DependencyGraph':
        """Create from dictionary"""
        graph = cls()
        
        # Add nodes
        for task_id, task_data in data.get('nodes', {}).items():
            task = Task.from_dict(task_data)
            graph.nodes[task_id] = task
        
        # Add edges
        for edge_data in data.get('edges', []):
            edge = TaskDependency.from_dict(edge_data)
            graph.edges.append(edge)
        
        return graph

# ============================================================================
# UTILITY CLASSES
# ============================================================================

class PlanningModelValidator:
    """Validator for planning models with comprehensive checks"""
    
    @staticmethod
    def validate_task(task: Task) -> List[str]:
        """Validate task model and return list of errors"""
        errors = []
        
        if not task.id:
            errors.append("Task ID cannot be empty")
        
        if not task.name:
            errors.append("Task name cannot be empty")
        
        if task.priority_score < 0 or task.priority_score > 100:
            errors.append(f"Priority score must be 0-100, got {task.priority_score}")
        
        if task.progress_percentage < 0 or task.progress_percentage > 100:
            errors.append(f"Progress percentage must be 0-100, got {task.progress_percentage}")
        
        if task.estimated_effort <= 0:
            errors.append(f"Estimated effort must be positive, got {task.estimated_effort}")
        
        if task.id in task.dependencies:
            errors.append("Task cannot depend on itself")
        
        if task.status == TaskStatus.COMPLETED and task.progress_percentage != 100:
            errors.append("Completed tasks must have 100% progress")
        
        if task.status == TaskStatus.BLOCKED and not task.blocking_reason:
            errors.append("Blocked tasks must have blocking reason")
        
        if task.completed_at and task.started_at and task.completed_at < task.started_at:
            errors.append("Completion time cannot be before start time")
        
        return errors
    
    @staticmethod
    def validate_plan(plan: Plan) -> List[str]:
        """Validate plan model and return list of errors"""
        errors = []
        
        if not plan.id:
            errors.append("Plan ID cannot be empty")
        
        if not plan.plan_name:
            errors.append("Plan name cannot be empty")
        
        if plan.confidence_score < 0 or plan.confidence_score > 1:
            errors.append(f"Confidence score must be 0-1, got {plan.confidence_score}")
        
        if plan.priority_level < 0 or plan.priority_level > 100:
            errors.append(f"Priority level must be 0-100, got {plan.priority_level}")
        
        if plan.estimated_duration_hours is not None and plan.estimated_duration_hours <= 0:
            errors.append(f"Estimated duration must be positive, got {plan.estimated_duration_hours}")
        
        if plan.completed_at and plan.started_at and plan.completed_at < plan.started_at:
            errors.append("Completion time cannot be before start time")
        
        # Validate all tasks
        for i, task in enumerate(plan.tasks):
            task_errors = PlanningModelValidator.validate_task(task)
            for error in task_errors:
                errors.append(f"Task {i} ({task.id}): {error}")
        
        # Check for duplicate task IDs
        task_ids = [task.id for task in plan.tasks]
        if len(task_ids) != len(set(task_ids)):
            errors.append("Plan contains duplicate task IDs")
        
        return errors

# ============================================================================
# MODEL FACTORY
# ============================================================================

class PlanningModelFactory:
    """Factory for creating planning models with defaults"""
    
    @staticmethod
    def create_task(
        name: str,
        task_type: Union[TaskType, str] = TaskType.GENERAL,
        priority: int = 50,
        assigned_agent: Union[AgentType, str] = AgentType.HUMAN,
        **kwargs
    ) -> Task:
        """Create task with validation"""
        return Task(
            name=name,
            task_type=task_type,
            priority_score=priority,
            assigned_agent=assigned_agent,
            **kwargs
        )
    
    @staticmethod
    def create_plan(
        name: str,
        project_id: str = "",
        plan_type: Union[PlanType, str] = PlanType.REACTIVE,
        goals: Optional[List[str]] = None,
        **kwargs
    ) -> Plan:
        """Create plan with validation"""
        return Plan(
            plan_name=name,
            project_id=project_id,
            plan_type=plan_type,
            goals=goals or [],
            **kwargs
        )
    
    @staticmethod
    def create_dependency(
        task_id: str,
        depends_on_task_id: str,
        dependency_type: Union[DependencyType, str] = DependencyType.STANDARD
    ) -> TaskDependency:
        """Create task dependency with validation"""
        return TaskDependency(
            task_id=task_id,
            depends_on_task_id=depends_on_task_id,
            dependency_type=dependency_type
        )
    
    @staticmethod
    def create_event(
        event_type: Union[EventType, str],
        plan_id: Optional[str] = None,
        task_id: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs
    ) -> PlanningEvent:
        """Create planning event with validation"""
        return PlanningEvent(
            event_type=event_type,
            plan_id=plan_id,
            task_id=task_id,
            event_message=message,
            **kwargs
        )
