"""
Copper Alloy Brass Task Generator - Sprint 8 Implementation
Converts observations into autonomous tasks with cycle detection
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Tuple, Any
from dataclasses import dataclass
import logging

# Optional NetworkX import with fallback
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None
    logging.warning("NetworkX not available - cycle detection disabled")

# Import DCPCoordinator for event publishing
from ...core.context.dcp_coordination import DCPCoordinator, CoordinationMessage

logger = logging.getLogger(__name__)

@dataclass
class TaskGenerationConfig:
    """Configuration for task generation behavior"""
    max_tasks_per_cycle: int = 50
    default_effort_estimate: float = 2.0  # hours
    priority_boost_threshold: int = 85
    dependency_analysis_enabled: bool = True
    cycle_detection_enabled: bool = True and NETWORKX_AVAILABLE
    min_task_priority: int = 20
    agent_availability_check: bool = True
    valid_agents: List[str] = None
    
    def __post_init__(self):
        if self.valid_agents is None:
            self.valid_agents = ['human', 'scout', 'watch', 'strategist']
        
        # Disable cycle detection if NetworkX unavailable
        if self.cycle_detection_enabled and not NETWORKX_AVAILABLE:
            self.cycle_detection_enabled = False
            logger.warning("Cycle detection disabled - NetworkX not available")

@dataclass
class TaskTemplate:
    """Template for generating specific types of tasks"""
    name: str
    task_type: str
    description_template: str
    default_effort: float
    preferred_agent: str
    priority_modifier: int = 0

class TaskGenerator:
    """
    Core task generation engine for autonomous planning.
    Converts DCP observations into actionable development tasks.
    
    Features:
    - Observation → Task conversion
    - Cycle detection in task dependencies
    - Task template management
    - Effort estimation
    - Agent assignment optimization
    """
    
    def __init__(self, dcp_manager=None, config: Optional[TaskGenerationConfig] = None, learning_integration=None):
        self.dcp_manager = dcp_manager
        self.config = config or TaskGenerationConfig()
        self.task_templates = self._initialize_task_templates()
        
        # Initialize learning integration (Blood Oath compliant)
        if learning_integration is None:
            from coppersun_brass.core.learning.codebase_learning_coordinator import CodebaseLearningCoordinator
            # CodebaseLearningCoordinator expects dcp_path, compatible interface
            dcp_path = getattr(dcp_manager, 'dcp_path', None) if dcp_manager else None
            self.learning = CodebaseLearningCoordinator(dcp_path=dcp_path)
        else:
            self.learning = learning_integration
        
        # Initialize DCPCoordinator for event publishing
        self.coordinator = None
        if dcp_manager:
            self.coordinator = DCPCoordinator(
                agent_name="planner",
                dcp_manager=dcp_manager
            )
            logger.info("TaskGenerator initialized with DCPCoordinator")
        else:
            logger.debug("TaskGenerator running without DCPCoordinator")
        
        # Initialize dependency graph only if NetworkX available
        if NETWORKX_AVAILABLE:
            self.dependency_graph = nx.DiGraph()
        else:
            self.dependency_graph = None
            
        # Cache for performance optimization
        self._template_cache = {}
        self._agent_workload_cache = {}
        
        logger.info(f"TaskGenerator initialized with cycle detection: {self.config.cycle_detection_enabled}")
    
    def generate_tasks_from_observations(self, observations: List[Dict]) -> List[Dict]:
        """
        Convert DCP observations into actionable tasks.
        
        Args:
            observations: List of observation dictionaries from DCP
            
        Returns:
            List of Task dictionaries with priorities, assignments, and dependencies
        """
        # Input validation
        if not observations:
            logger.info("No observations provided for task generation")
            return []
        
        if not isinstance(observations, list):
            logger.error("Observations must be a list")
            return []
        
        tasks = []
        
        # Process observations in batches for performance
        batch_size = min(self.config.max_tasks_per_cycle, len(observations))
        
        for obs in observations[:batch_size]:
            # Validate observation structure
            if not self._validate_observation(obs):
                continue
                
            # Skip low-priority observations
            if obs.get('priority', 0) < self.config.min_task_priority:
                continue
                
            try:
                task = self._convert_observation_to_task(obs)
                if task:
                    tasks.append(task)
            except Exception as e:
                logger.error(f"Error converting observation {obs.get('id', 'unknown')}: {e}")
                continue
        
        # Analyze dependencies and detect cycles
        if self.config.dependency_analysis_enabled and tasks:
            try:
                tasks = self._analyze_task_dependencies(tasks)
            except Exception as e:
                logger.error(f"Error analyzing dependencies: {e}")
            
        if self.config.cycle_detection_enabled and tasks:
            try:
                cycles = self.detect_dependency_cycles(tasks)
                if cycles:
                    logger.warning(f"Detected {len(cycles)} dependency cycles, resolving...")
                    tasks = self._resolve_dependency_cycles(tasks, cycles)
            except Exception as e:
                logger.error(f"Error detecting cycles: {e}")
        
        # Final validation and limiting
        valid_tasks = [task for task in tasks if self._validate_task(task)]
        
        logger.info(f"Generated {len(valid_tasks)} valid tasks from {len(observations)} observations")
        return valid_tasks
    
    def _validate_observation(self, observation: Dict) -> bool:
        """Validate observation structure"""
        required_fields = ['type', 'summary', 'priority']
        
        if not isinstance(observation, dict):
            return False
        
        for field in required_fields:
            if field not in observation:
                logger.warning(f"Observation missing required field: {field}")
                return False
        
        # Validate priority range
        priority = observation.get('priority')
        if not isinstance(priority, (int, float)) or not 0 <= priority <= 100:
            logger.warning(f"Invalid priority value: {priority}")
            return False
        
        return True
    
    def _validate_task(self, task: Dict) -> bool:
        """Validate generated task structure"""
        required_fields = ['id', 'name', 'task_type', 'priority_score', 'assigned_agent']
        
        for field in required_fields:
            if field not in task:
                logger.warning(f"Generated task missing field: {field}")
                return False
        
        # Validate agent assignment
        assigned_agent = task.get('assigned_agent')
        if assigned_agent not in self.config.valid_agents:
            logger.warning(f"Invalid agent assignment: {assigned_agent}")
            return False
        
        return True
    
    def _convert_observation_to_task(self, observation: Dict) -> Optional[Dict]:
        """Convert a single observation into a Task dictionary"""
        obs_type = observation.get('type', 'unknown')
        obs_summary = observation.get('summary', '')
        obs_priority = observation.get('priority', 50)
        
        # Determine task type and template
        task_type = self._classify_observation_type(obs_type, obs_summary)
        template = self.task_templates.get(task_type)
        
        if not template:
            logger.warning(f"No template found for task type: {task_type}")
            return None
        
        # Create task from template
        task = {
            'id': str(uuid.uuid4()),
            'plan_id': None,  # Will be set when added to a plan
            'name': self._generate_task_name(observation, template),
            'description': self._generate_task_description(observation, template),
            'task_type': task_type,
            'priority_score': self._calculate_initial_priority(observation),
            'estimated_effort': self._estimate_task_effort(observation, task_type),
            'assigned_agent': self._suggest_optimal_agent(task_type, observation),
            'status': 'pending',
            'dependencies': [],
            'metadata': {
                'source_observation_id': observation.get('id'),
                'source_agent': observation.get('source', 'unknown'),
                'generation_timestamp': datetime.now().isoformat(),
                'template_used': template.name
            },
            'created_at': datetime.now().isoformat()
        }
        
        return task
    
    def _classify_observation_type(self, obs_type: str, summary: str) -> str:
        """Classify observation into task type categories"""
        
        # Type-based classification
        type_mapping = {
            'test_coverage': 'testing',
            'security': 'security_fix',
            'performance': 'optimization',
            'implementation_gap': 'implementation',
            'code_quality': 'refactoring',
            'documentation': 'documentation',
            'bug': 'bug_fix'
        }
        
        if obs_type in type_mapping:
            return type_mapping[obs_type]
        
        # Summary-based classification (keywords)
        summary_lower = summary.lower()
        
        if any(keyword in summary_lower for keyword in ['todo', 'fixme', 'hack']):
            return 'implementation'
        elif any(keyword in summary_lower for keyword in ['test', 'coverage', 'assert']):
            return 'testing'
        elif any(keyword in summary_lower for keyword in ['security', 'vulnerability', 'injection']):
            return 'security_fix'
        elif any(keyword in summary_lower for keyword in ['performance', 'slow', 'optimize']):
            return 'optimization'
        elif any(keyword in summary_lower for keyword in ['refactor', 'cleanup', 'quality']):
            return 'refactoring'
        elif any(keyword in summary_lower for keyword in ['document', 'readme', 'comment']):
            return 'documentation'
        else:
            return 'general'
    
    def _suggest_optimal_agent(self, task_type: str, observation: Dict) -> str:
        """Suggest the best agent for task execution with learning-enhanced validation"""
        
        # Agent specialization mapping
        agent_mapping = {
            'testing': 'human',  # Requires complex test design
            'security_fix': 'human',  # Critical security decisions
            'implementation': 'scout',  # Research + implementation guidance
            'optimization': 'human',  # Performance analysis required
            'refactoring': 'scout',  # Code analysis + suggestions
            'documentation': 'scout',  # Can generate documentation
            'bug_fix': 'human',  # Debugging requires human insight
            'research': 'scout',  # Information gathering
            'general': 'human'  # Default to human for unknown tasks
        }
        
        suggested_agent = agent_mapping.get(task_type, 'human')
        
        # Apply learning insights to improve agent selection
        try:
            decision_context = {
                "type": "agent_selection",
                "task_type": task_type,
                "initial_suggestion": suggested_agent,
                "observation_priority": observation.get('priority', 50)
            }
            
            learning_recommendations = self.learning.apply_learning(decision_context)
            
            # Record the decision for future learning
            if self.coordinator:
                decision_data = {
                    "id": f"agent_select_{observation.get('id', 'unknown')}",
                    "type": "agent_selection",
                    "context": decision_context,
                    "options": list(self.config.valid_agents),
                    "selected": suggested_agent,
                    "reasoning": f"Task type: {task_type}, Learning confidence adjustment: {learning_recommendations.get('confidence_adjustment', 0)}",
                    "confidence": 0.7 + learning_recommendations.get('confidence_adjustment', 0)
                }
                
                message = CoordinationMessage(
                    observation_type="planning.decision.made",
                    source_agent="planner",
                    data=decision_data,
                    target_agents=["learning_integration"],
                    priority=50,
                    requires_action=True
                )
                
                obs_id = self.coordinator.publish(message)
                if obs_id:
                    logger.debug(f"Published planning decision: {obs_id}")
                else:
                    logger.warning("Failed to publish planning decision")
            else:
                logger.debug("No coordinator available for publishing planning decision")
            
        except Exception as e:
            logger.debug(f"Learning integration not available for agent selection: {e}")
        
        # Validate agent is in allowed list
        if suggested_agent not in self.config.valid_agents:
            logger.warning(f"Suggested agent {suggested_agent} not in valid agents, defaulting to human")
            suggested_agent = 'human'
        
        return suggested_agent
    
    def _generate_task_name(self, observation: Dict, template: TaskTemplate) -> str:
        """Generate descriptive task name from observation and template"""
        obs_summary = observation.get('summary', 'Unknown issue')
        
        # Truncate long summaries for task names
        if len(obs_summary) > 60:
            obs_summary = obs_summary[:57] + "..."
        
        return f"{template.name}: {obs_summary}"
    
    def _generate_task_description(self, observation: Dict, template: TaskTemplate) -> str:
        """Generate detailed task description"""
        obs_details = observation.get('details', {})
        obs_summary = observation.get('summary', '')
        
        description = template.description_template.format(
            summary=obs_summary,
            location=obs_details.get('location', 'Unknown location'),
            source=observation.get('source', 'Unknown source')
        )
        
        # Add observation details if available
        if obs_details:
            description += f"\n\nAdditional context:\n"
            for key, value in obs_details.items():
                if key != 'location':  # Already included above
                    description += f"- {key}: {value}\n"
        
        return description
    
    def _calculate_initial_priority(self, observation: Dict) -> int:
        """Calculate initial task priority from observation"""
        base_priority = observation.get('priority', 50)
        
        # Priority modifiers based on observation characteristics
        obs_type = observation.get('type', '')
        
        # Security issues get priority boost
        if obs_type == 'security':
            base_priority = min(100, base_priority + 20)
        
        # Test coverage issues get moderate boost
        elif obs_type == 'test_coverage':
            base_priority = min(100, base_priority + 10)
        
        # Performance issues get boost if high priority
        elif obs_type == 'performance' and base_priority > 70:
            base_priority = min(100, base_priority + 15)
        
        return max(0, min(100, base_priority))
    
    def _estimate_task_effort(self, observation: Dict, task_type: str) -> float:
        """Estimate effort required for task completion"""
        
        # Base effort estimates by task type (in hours)
        effort_mapping = {
            'testing': 3.0,
            'security_fix': 4.0,
            'implementation': 2.5,
            'optimization': 3.5,
            'refactoring': 2.0,
            'documentation': 1.5,
            'bug_fix': 2.0,
            'research': 1.0,
            'general': 2.0
        }
        
        base_effort = effort_mapping.get(task_type, self.config.default_effort_estimate)
        
        # Adjust based on observation priority (higher priority may indicate complexity)
        priority = observation.get('priority', 50)
        if priority > 80:
            base_effort *= 1.3  # High priority likely means more complex
        elif priority < 30:
            base_effort *= 0.8  # Low priority might be simpler
        
        return round(base_effort, 1)
    
    def _analyze_task_dependencies(self, tasks: List[Dict]) -> List[Dict]:
        """Analyze and set task dependencies based on relationships"""
        
        # Simple dependency analysis based on task types and shared components
        for i, task in enumerate(tasks):
            dependencies = []
            
            for j, other_task in enumerate(tasks):
                if i == j:
                    continue
                
                # Dependencies based on task types
                if self._has_dependency(task, other_task):
                    dependencies.append(other_task['id'])
            
            task['dependencies'] = dependencies
        
        return tasks
    
    def _has_dependency(self, task: Dict, other_task: Dict) -> bool:
        """Determine if task depends on other_task"""
        
        # Dependency rules based on task types
        dependency_rules = {
            'testing': ['implementation', 'bug_fix'],  # Tests depend on implementation
            'documentation': ['implementation'],  # Docs depend on features
            'optimization': ['implementation'],  # Optimization comes after implementation
        }
        
        task_type = task.get('task_type', '')
        other_type = other_task.get('task_type', '')
        
        # Check if task_type depends on other_type
        depends_on = dependency_rules.get(task_type, [])
        
        return other_type in depends_on
    
    def detect_dependency_cycles(self, tasks: List[Dict]) -> List[List[str]]:
        """
        Detect circular dependencies in task list using NetworkX.
        GPT Enhancement #1: Cycle detection to avoid recursive task blocks.
        
        Args:
            tasks: List of task dictionaries with dependencies
            
        Returns:
            List of cycles (each cycle is a list of task IDs)
        """
        # Fallback if NetworkX not available
        if not NETWORKX_AVAILABLE or not self.dependency_graph:
            logger.warning("Cycle detection unavailable - NetworkX not installed")
            return []
        
        # Build dependency graph
        self.dependency_graph.clear()
        
        try:
            for task in tasks:
                task_id = task.get('id')
                if not task_id:
                    continue
                    
                self.dependency_graph.add_node(task_id)
                
                for dep_id in task.get('dependencies', []):
                    if dep_id and dep_id != task_id:  # Avoid self-loops
                        self.dependency_graph.add_edge(dep_id, task_id)
            
            # Find cycles using NetworkX
            cycles = list(nx.simple_cycles(self.dependency_graph))
            
            if cycles:
                logger.warning(f"Found {len(cycles)} dependency cycles: {cycles}")
            
            return cycles
            
        except Exception as e:
            logger.error(f"Error detecting cycles: {e}")
            return []
    
    def _resolve_dependency_cycles(self, tasks: List[Dict], cycles: List[List[str]]) -> List[Dict]:
        """Resolve dependency cycles by removing problematic dependencies"""
        
        task_dict = {task['id']: task for task in tasks}
        
        for cycle in cycles:
            if len(cycle) < 2:
                continue
            
            # Simple resolution: remove dependency from highest to lowest priority task
            cycle_tasks = [task_dict[task_id] for task_id in cycle if task_id in task_dict]
            
            if len(cycle_tasks) < 2:
                continue
            
            # Sort by priority (highest first)
            cycle_tasks.sort(key=lambda t: t.get('priority_score', 0), reverse=True)
            
            # Remove dependency from highest priority task to second highest
            highest_priority = cycle_tasks[0]
            second_highest = cycle_tasks[1]
            
            if second_highest['id'] in highest_priority['dependencies']:
                highest_priority['dependencies'].remove(second_highest['id'])
                logger.info(f"Resolved cycle: removed dependency {second_highest['id']} from {highest_priority['id']}")
        
        return tasks
    
    def create_task_templates(self, task_type: str) -> Optional[TaskTemplate]:
        """Create task template for given type with fallback"""
        templates = self._initialize_task_templates()
        template = templates.get(task_type)
        
        if not template:
            logger.warning(f"No template found for task type: {task_type}, using general template")
            template = templates.get('general')
        
        return template
    
    def _initialize_task_templates(self) -> Dict[str, TaskTemplate]:
        """Initialize standard task templates"""
        
        templates = {
            'testing': TaskTemplate(
                name="Add Tests",
                task_type="testing",
                description_template="Add test coverage for: {summary}\nLocation: {location}\nSource: {source}",
                default_effort=3.0,
                preferred_agent="human",
                priority_modifier=10
            ),
            'security_fix': TaskTemplate(
                name="Security Fix",
                task_type="security_fix", 
                description_template="Address security issue: {summary}\nLocation: {location}\nSource: {source}",
                default_effort=4.0,
                preferred_agent="human",
                priority_modifier=20
            ),
            'implementation': TaskTemplate(
                name="Implement Feature",
                task_type="implementation",
                description_template="Implement: {summary}\nLocation: {location}\nSource: {source}",
                default_effort=2.5,
                preferred_agent="scout",
                priority_modifier=0
            ),
            'optimization': TaskTemplate(
                name="Performance Optimization",
                task_type="optimization",
                description_template="Optimize performance: {summary}\nLocation: {location}\nSource: {source}",
                default_effort=3.5,
                preferred_agent="human",
                priority_modifier=5
            ),
            'refactoring': TaskTemplate(
                name="Code Refactoring",
                task_type="refactoring",
                description_template="Refactor code: {summary}\nLocation: {location}\nSource: {source}",
                default_effort=2.0,
                preferred_agent="scout",
                priority_modifier=0
            ),
            'documentation': TaskTemplate(
                name="Update Documentation",
                task_type="documentation",
                description_template="Document: {summary}\nLocation: {location}\nSource: {source}",
                default_effort=1.5,
                preferred_agent="scout",
                priority_modifier=-5
            ),
            'bug_fix': TaskTemplate(
                name="Fix Bug",
                task_type="bug_fix",
                description_template="Fix bug: {summary}\nLocation: {location}\nSource: {source}",
                default_effort=2.0,
                preferred_agent="human",
                priority_modifier=10
            ),
            'research': TaskTemplate(
                name="Research Task",
                task_type="research",
                description_template="Research: {summary}\nLocation: {location}\nSource: {source}",
                default_effort=1.0,
                preferred_agent="scout",
                priority_modifier=-10
            ),
            'general': TaskTemplate(
                name="General Task",
                task_type="general",
                description_template="Task: {summary}\nLocation: {location}\nSource: {source}",
                default_effort=2.0,
                preferred_agent="human",
                priority_modifier=0
            )
        }
        
        return templates
    
    def record_task_outcome(self, task_id: str, success: bool, metrics: Optional[Dict] = None, feedback: Optional[str] = None) -> None:
        """Record the outcome of a task for learning purposes.
        
        Args:
            task_id: ID of the completed task
            success: Whether the task was successful
            metrics: Optional performance metrics
            feedback: Optional human feedback
        """
        try:
            outcome_data = {
                "decision_id": f"task_gen_{task_id}",
                "type": "task_completion",
                "success": success,
                "metrics": metrics or {},
                "feedback": feedback or "",
                "lessons": self._extract_lessons(success, metrics, feedback)
            }
            
            if self.coordinator:
                message = CoordinationMessage(
                    observation_type="planning.outcome.recorded",
                    source_agent="planner",
                    data=outcome_data,
                    target_agents=["learning_integration"],
                    priority=60,
                    requires_action=True
                )
                
                obs_id = self.coordinator.publish(message)
                if obs_id:
                    logger.info(f"Recorded outcome for task {task_id}: {'success' if success else 'failure'}")
                    logger.debug(f"Published planning outcome: {obs_id}")
                else:
                    logger.warning(f"Failed to publish outcome for task {task_id}")
            else:
                logger.info(f"Recorded outcome for task {task_id}: {'success' if success else 'failure'}")
                logger.debug("No coordinator available for publishing planning outcome")
            
        except Exception as e:
            logger.error(f"Error recording task outcome: {e}")
    
    def _extract_lessons(self, success: bool, metrics: Optional[Dict], feedback: Optional[str]) -> List[str]:
        """Extract lessons from task outcome.
        
        Args:
            success: Whether task was successful
            metrics: Performance metrics
            feedback: Human feedback
            
        Returns:
            List of extracted lessons
        """
        lessons = []
        
        if success:
            if metrics and metrics.get("time_saved", 0) > 0:
                lessons.append("Time-efficient approach worked well")
            if metrics and metrics.get("accuracy", 0) > 0.9:
                lessons.append("High accuracy achieved with current approach")
        else:
            if feedback and "too complex" in feedback.lower():
                lessons.append("Task was too complex - consider breaking down")
            if feedback and "wrong agent" in feedback.lower():
                lessons.append("Agent assignment needs improvement")
        
        return lessons
    
    def get_learning_enhanced_config(self, task_type: str) -> Dict[str, Any]:
        """Get learning-enhanced configuration for task generation.
        
        Args:
            task_type: Type of task to generate
            
        Returns:
            Enhanced configuration based on learning
        """
        try:
            insights = self.learning.get_learning_insights(context_type=task_type)
            
            config = {
                "success_rate": insights.get("success_rate", 0.5),
                "recommended_approaches": insights.get("recommendations", []),
                "successful_patterns": insights.get("successful_patterns", []),
                "priority_adjustment": self._calculate_priority_adjustment(insights)
            }
            
            return config
            
        except Exception as e:
            logger.error(f"Error getting learning-enhanced config: {e}")
            return {}
    
    def _calculate_priority_adjustment(self, insights: Dict[str, Any]) -> int:
        """Calculate priority adjustment based on learning insights.
        
        Args:
            insights: Learning insights
            
        Returns:
            Priority adjustment value
        """
        success_rate = insights.get("success_rate", 0.5)
        
        # Higher success rate -> slightly lower priority (well-handled tasks)
        # Lower success rate -> higher priority (needs attention)
        if success_rate > 0.8:
            return -5
        elif success_rate < 0.3:
            return 10
        else:
            return 0