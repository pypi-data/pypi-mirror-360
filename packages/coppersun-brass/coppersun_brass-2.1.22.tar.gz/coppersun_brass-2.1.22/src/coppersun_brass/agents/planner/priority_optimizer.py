"""
Copper Alloy Brass Priority Optimizer - Sprint 8 Implementation
Dynamic priority scoring with agent availability checks
GPT Enhancement #2: Agent availability check before task assignment
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
import logging
import threading
from collections import defaultdict, deque

# Optional NetworkX import with fallback
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None

logger = logging.getLogger(__name__)

@dataclass
class PriorityConfig:
    """Configuration for priority optimization behavior"""
    max_priority: int = 100
    min_priority: int = 0
    decay_rate: float = 0.95  # Priority decay over time
    boost_multiplier: float = 1.2  # Priority boost factor
    dependency_weight: float = 0.3  # How much dependencies affect priority
    agent_workload_weight: float = 0.2  # How much agent load affects assignment
    time_sensitivity_threshold: int = 80  # Priority threshold for time-sensitive tasks
    max_agent_concurrent_tasks: int = 5  # Max tasks per agent
    priority_update_interval: int = 3600  # Seconds between priority updates

@dataclass
class AgentAvailability:
    """Agent availability and workload information"""
    agent_id: str
    current_tasks: int = 0
    max_capacity: int = 5
    specialization_bonus: Dict[str, float] = None
    availability_score: float = 1.0  # 0.0 = unavailable, 1.0 = fully available
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.specialization_bonus is None:
            self.specialization_bonus = {}
        if self.last_updated is None:
            self.last_updated = datetime.now()

class PriorityOptimizer:
    """
    Advanced priority optimization engine with agent availability checks.
    
    Features:
    - Dynamic priority scoring with decay and boost
    - Agent workload analysis and availability checks
    - Dependency-aware priority calculation
    - Time-sensitive task prioritization
    - Multi-agent load balancing
    - Thread-safe operations
    """
    
    def __init__(self, config: Optional[PriorityConfig] = None):
        self.config = config or PriorityConfig()
        self.agent_availability = {}
        self.task_history = defaultdict(list)
        self.priority_cache = {}
        self._lock = threading.RLock()
        
        # Initialize default agents
        self._initialize_agent_availability()
        
        logger.info("PriorityOptimizer initialized with agent availability checking")
    
    def calculate_priority_score(self, task: Dict, context: Optional[Dict] = None) -> int:
        """
        Calculate optimized priority score for a task.
        
        Args:
            task: Task dictionary with metadata
            context: Additional context (dependencies, deadlines, etc.)
            
        Returns:
            Priority score (0-100)
        """
        with self._lock:
            try:
                # Validate input
                if not self._validate_task_for_priority(task):
                    return self.config.min_priority
                
                base_priority = task.get('priority_score', 50)
                task_type = task.get('task_type', 'general')
                created_at = self._parse_datetime(task.get('created_at'))
                
                # Start with base priority
                final_priority = float(base_priority)
                
                # Apply time decay
                if created_at:
                    final_priority = self._apply_time_decay(final_priority, created_at)
                
                # Apply type-based modifiers
                final_priority = self._apply_type_modifiers(final_priority, task_type)
                
                # Apply dependency boost
                if context and 'dependencies' in context:
                    final_priority = self._apply_dependency_boost(final_priority, task, context['dependencies'])
                
                # Apply urgency boost for time-sensitive tasks
                if final_priority >= self.config.time_sensitivity_threshold:
                    final_priority *= self.config.boost_multiplier
                
                # Ensure priority is within bounds
                final_priority = max(self.config.min_priority, min(self.config.max_priority, int(final_priority)))
                
                # Cache result
                task_id = task.get('id')
                if task_id:
                    self.priority_cache[task_id] = {
                        'priority': final_priority,
                        'calculated_at': datetime.now(),
                        'factors': self._get_priority_factors(task, final_priority, base_priority)
                    }
                
                return int(final_priority)
                
            except Exception as e:
                logger.error(f"Error calculating priority for task {task.get('id', 'unknown')}: {e}")
                return task.get('priority_score', self.config.min_priority)
    
    def analyze_dependencies(self, tasks: List[Dict]) -> Dict[str, List[str]]:
        """
        Analyze task dependencies and create dependency graph.
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            Dictionary mapping task IDs to their dependency lists
        """
        try:
            dependency_map = {}
            
            for task in tasks:
                task_id = task.get('id')
                if not task_id:
                    continue
                
                dependencies = task.get('dependencies', [])
                
                # Validate dependencies exist in task list
                valid_deps = []
                task_ids = {t.get('id') for t in tasks if t.get('id')}
                
                for dep_id in dependencies:
                    if dep_id in task_ids:
                        valid_deps.append(dep_id)
                    else:
                        logger.warning(f"Task {task_id} has invalid dependency: {dep_id}")
                
                dependency_map[task_id] = valid_deps
            
            return dependency_map
            
        except Exception as e:
            logger.error(f"Error analyzing dependencies: {e}")
            return {}
    
    def optimize_priority_order(self, tasks: List[Dict]) -> List[Dict]:
        """
        Optimize task execution order based on priorities and dependencies.
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            Reordered list of tasks optimized for execution
        """
        try:
            if not tasks:
                return []
            
            # Validate tasks
            valid_tasks = [task for task in tasks if self._validate_task_for_priority(task)]
            
            if not valid_tasks:
                logger.warning("No valid tasks for priority optimization")
                return []
            
            # Build dependency context
            dependencies = self.analyze_dependencies(valid_tasks)
            context = {'dependencies': dependencies}
            
            # Calculate optimized priorities
            for task in valid_tasks:
                new_priority = self.calculate_priority_score(task, context)
                task['optimized_priority'] = new_priority
            
            # Sort by optimized priority and dependencies
            if NETWORKX_AVAILABLE:
                ordered_tasks = self._topological_sort_with_priority(valid_tasks, dependencies)
            else:
                # Fallback: simple priority sort
                ordered_tasks = sorted(valid_tasks, 
                                     key=lambda t: t.get('optimized_priority', 0), 
                                     reverse=True)
            
            logger.info(f"Optimized priority order for {len(ordered_tasks)} tasks")
            return ordered_tasks
            
        except Exception as e:
            logger.error(f"Error optimizing priority order: {e}")
            return tasks  # Return original order on error
    
    def assign_optimal_agent(self, task: Dict) -> str:
        """
        Assign optimal agent based on availability and specialization.
        GPT Enhancement #2: Agent availability check before task assignment.
        
        Args:
            task: Task dictionary
            
        Returns:
            Agent ID for optimal assignment
        """
        with self._lock:
            try:
                task_type = task.get('task_type', 'general')
                current_assignment = task.get('assigned_agent', 'human')
                
                # Update agent availability
                self._update_agent_availability()
                
                # Get available agents for this task type
                suitable_agents = self._get_suitable_agents(task_type)
                
                if not suitable_agents:
                    logger.warning(f"No suitable agents for task type: {task_type}")
                    return 'human'  # Fallback to human
                
                # Calculate agent scores
                agent_scores = {}
                for agent_id in suitable_agents:
                    score = self._calculate_agent_score(agent_id, task_type, task)
                    agent_scores[agent_id] = score
                
                # Select best available agent
                best_agent = max(agent_scores.keys(), key=lambda a: agent_scores[a])
                
                # Verify agent has capacity
                if not self._agent_has_capacity(best_agent):
                    # Find next best available agent
                    available_agents = [a for a in agent_scores.keys() if self._agent_has_capacity(a)]
                    if available_agents:
                        best_agent = max(available_agents, key=lambda a: agent_scores[a])
                    else:
                        logger.warning("All agents at capacity, assigning to least loaded")
                        best_agent = self._get_least_loaded_agent()
                
                # Update agent workload
                self._assign_task_to_agent(best_agent, task.get('id'))
                
                logger.debug(f"Assigned task {task.get('id')} to agent {best_agent} (score: {agent_scores.get(best_agent, 0)})")
                return best_agent
                
            except Exception as e:
                logger.error(f"Error assigning optimal agent: {e}")
                return task.get('assigned_agent', 'human')  # Return current or default
    
    def get_agent_workload(self, agent_id: str) -> Dict:
        """Get current workload information for an agent"""
        with self._lock:
            if agent_id not in self.agent_availability:
                return {'current_tasks': 0, 'capacity': 0, 'availability': 0.0}
            
            agent = self.agent_availability[agent_id]
            return {
                'current_tasks': agent.current_tasks,
                'capacity': agent.max_capacity,
                'availability': agent.availability_score,
                'utilization': agent.current_tasks / max(agent.max_capacity, 1),
                'last_updated': agent.last_updated.isoformat()
            }
    
    def update_agent_availability(self, agent_id: str, availability_data: Dict):
        """Update agent availability information"""
        with self._lock:
            try:
                if agent_id not in self.agent_availability:
                    self.agent_availability[agent_id] = AgentAvailability(agent_id=agent_id)
                
                agent = self.agent_availability[agent_id]
                
                # Update fields if provided
                if 'current_tasks' in availability_data:
                    agent.current_tasks = max(0, int(availability_data['current_tasks']))
                
                if 'max_capacity' in availability_data:
                    agent.max_capacity = max(1, int(availability_data['max_capacity']))
                
                if 'availability_score' in availability_data:
                    score = float(availability_data['availability_score'])
                    agent.availability_score = max(0.0, min(1.0, score))
                
                if 'specialization_bonus' in availability_data:
                    agent.specialization_bonus.update(availability_data['specialization_bonus'])
                
                agent.last_updated = datetime.now()
                
                logger.debug(f"Updated availability for agent {agent_id}")
                
            except Exception as e:
                logger.error(f"Error updating agent availability: {e}")
    
    def _validate_task_for_priority(self, task: Dict) -> bool:
        """Validate task has required fields for priority calculation"""
        if not isinstance(task, dict):
            return False
        
        required_fields = ['id', 'task_type']
        for field in required_fields:
            if field not in task:
                logger.warning(f"Task missing required field for priority calculation: {field}")
                return False
        
        return True
    
    def _parse_datetime(self, dt_str) -> Optional[datetime]:
        """Safely parse datetime string"""
        if not dt_str:
            return None
        
        try:
            if isinstance(dt_str, str):
                return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            elif isinstance(dt_str, datetime):
                return dt_str
            else:
                return None
        except Exception:
            return None
    
    def _apply_time_decay(self, priority: float, created_at: datetime) -> float:
        """Apply time-based priority decay"""
        try:
            age_hours = (datetime.now() - created_at).total_seconds() / 3600
            
            # Apply decay for tasks older than 24 hours
            if age_hours > 24:
                decay_factor = self.config.decay_rate ** (age_hours / 24)
                priority *= decay_factor
            
            return priority
            
        except Exception as e:
            logger.error(f"Error applying time decay: {e}")
            return priority
    
    def _apply_type_modifiers(self, priority: float, task_type: str) -> float:
        """Apply task type-based priority modifiers"""
        type_modifiers = {
            'security_fix': 1.3,  # Security issues get high priority
            'bug_fix': 1.2,       # Bugs get priority boost
            'testing': 1.1,       # Tests get moderate boost
            'optimization': 1.0,   # Neutral
            'refactoring': 0.9,   # Lower priority
            'documentation': 0.8, # Lower priority
            'research': 0.7,      # Lower priority
            'general': 1.0        # Neutral
        }
        
        modifier = type_modifiers.get(task_type, 1.0)
        return priority * modifier
    
    def _apply_dependency_boost(self, priority: float, task: Dict, dependencies: Dict) -> float:
        """Apply priority boost based on dependencies"""
        try:
            task_id = task.get('id')
            if not task_id or task_id not in dependencies:
                return priority
            
            # Count tasks that depend on this task
            dependent_count = sum(1 for deps in dependencies.values() if task_id in deps)
            
            # Boost priority based on how many tasks depend on this one
            if dependent_count > 0:
                boost = 1 + (dependent_count * self.config.dependency_weight)
                priority *= boost
            
            return priority
            
        except Exception as e:
            logger.error(f"Error applying dependency boost: {e}")
            return priority
    
    def _get_priority_factors(self, task: Dict, final_priority: float, base_priority: float) -> Dict:
        """Get factors that influenced priority calculation"""
        return {
            'base_priority': base_priority,
            'final_priority': final_priority,
            'task_type': task.get('task_type'),
            'age_hours': self._get_task_age_hours(task),
            'has_dependencies': bool(task.get('dependencies')),
            'calculation_method': 'optimized'
        }
    
    def _get_task_age_hours(self, task: Dict) -> float:
        """Get task age in hours"""
        created_at = self._parse_datetime(task.get('created_at'))
        if created_at:
            return (datetime.now() - created_at).total_seconds() / 3600
        return 0.0
    
    def _topological_sort_with_priority(self, tasks: List[Dict], dependencies: Dict) -> List[Dict]:
        """Perform topological sort considering priorities"""
        try:
            # Create graph
            graph = nx.DiGraph()
            
            # Add nodes with priority as weight
            for task in tasks:
                task_id = task.get('id')
                priority = task.get('optimized_priority', 0)
                graph.add_node(task_id, priority=priority, task=task)
            
            # Add edges for dependencies
            for task_id, deps in dependencies.items():
                for dep_id in deps:
                    if graph.has_node(dep_id) and graph.has_node(task_id):
                        graph.add_edge(dep_id, task_id)
            
            # Topological sort with priority consideration
            sorted_ids = list(nx.topological_sort(graph))
            
            # Sort nodes at same dependency level by priority
            result = []
            for task_id in sorted_ids:
                task_data = graph.nodes[task_id]['task']
                result.append(task_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in topological sort: {e}")
            # Fallback to priority sort
            return sorted(tasks, key=lambda t: t.get('optimized_priority', 0), reverse=True)
    
    def _initialize_agent_availability(self):
        """Initialize default agent availability"""
        default_agents = {
            'human': AgentAvailability(
                agent_id='human',
                max_capacity=10,  # Humans can handle more complex tasks
                specialization_bonus={
                    'security_fix': 0.3,
                    'bug_fix': 0.2,
                    'optimization': 0.2,
                    'testing': 0.1
                }
            ),
            'scout': AgentAvailability(
                agent_id='scout',
                max_capacity=8,
                specialization_bonus={
                    'research': 0.4,
                    'documentation': 0.3,
                    'implementation': 0.2,
                    'refactoring': 0.2
                }
            ),
            'watch': AgentAvailability(
                agent_id='watch',
                max_capacity=5,
                specialization_bonus={
                    'monitoring': 0.4,
                    'analysis': 0.3
                }
            ),
            'strategist': AgentAvailability(
                agent_id='strategist',
                max_capacity=3,  # Strategist handles fewer but more complex tasks
                specialization_bonus={
                    'planning': 0.4,
                    'coordination': 0.3,
                    'optimization': 0.2
                }
            )
        }
        
        self.agent_availability.update(default_agents)
    
    def _update_agent_availability(self):
        """Update agent availability based on current system state"""
        # This would integrate with actual agent status in production
        # For now, we simulate availability updates
        current_time = datetime.now()
        
        for agent_id, agent in self.agent_availability.items():
            # Simulate availability fluctuation based on time
            if (current_time - agent.last_updated).total_seconds() > self.config.priority_update_interval:
                # Refresh availability (in production, this would query actual agent status)
                agent.last_updated = current_time
    
    def _get_suitable_agents(self, task_type: str) -> List[str]:
        """Get list of agents suitable for task type"""
        suitable = []
        
        for agent_id, agent in self.agent_availability.items():
            # Check if agent has specialization in this task type
            if (task_type in agent.specialization_bonus or 
                agent_id == 'human'):  # Human is suitable for all tasks
                suitable.append(agent_id)
        
        return suitable
    
    def _calculate_agent_score(self, agent_id: str, task_type: str, task: Dict) -> float:
        """Calculate suitability score for agent"""
        if agent_id not in self.agent_availability:
            return 0.0
        
        agent = self.agent_availability[agent_id]
        
        # Base score from availability
        score = agent.availability_score
        
        # Add specialization bonus
        specialization_bonus = agent.specialization_bonus.get(task_type, 0.0)
        score += specialization_bonus
        
        # Penalty for high workload
        utilization = agent.current_tasks / max(agent.max_capacity, 1)
        workload_penalty = utilization * self.config.agent_workload_weight
        score -= workload_penalty
        
        return max(0.0, score)
    
    def _agent_has_capacity(self, agent_id: str) -> bool:
        """Check if agent has capacity for additional tasks"""
        if agent_id not in self.agent_availability:
            return False
        
        agent = self.agent_availability[agent_id]
        return agent.current_tasks < agent.max_capacity
    
    def _get_least_loaded_agent(self) -> str:
        """Get the agent with lowest current workload"""
        min_utilization = float('inf')
        least_loaded = 'human'  # Default fallback
        
        for agent_id, agent in self.agent_availability.items():
            utilization = agent.current_tasks / max(agent.max_capacity, 1)
            if utilization < min_utilization:
                min_utilization = utilization
                least_loaded = agent_id
        
        return least_loaded
    
    def _assign_task_to_agent(self, agent_id: str, task_id: str):
        """Update agent workload when task is assigned"""
        if agent_id in self.agent_availability and task_id:
            self.agent_availability[agent_id].current_tasks += 1
            self.task_history[agent_id].append({
                'task_id': task_id,
                'assigned_at': datetime.now()
            })
    
    def complete_task(self, agent_id: str, task_id: str):
        """Update agent workload when task is completed"""
        with self._lock:
            if agent_id in self.agent_availability:
                self.agent_availability[agent_id].current_tasks = max(
                    0, self.agent_availability[agent_id].current_tasks - 1
                )
                logger.debug(f"Task {task_id} completed by agent {agent_id}")
