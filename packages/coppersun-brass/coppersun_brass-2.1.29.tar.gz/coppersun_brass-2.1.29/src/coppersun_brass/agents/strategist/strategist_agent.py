# coppersun_brass/agents/strategist/strategist_agent.py
"""
Copper Sun Brass Strategist Agent - Central DCP Orchestration Hub
Coordinates all agent activities and maintains project intelligence
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path

# Event Bus removed - using DCP coordination
from coppersun_brass.core.context.dcp_manager import DCPManager
from coppersun_brass.agents.strategist.priority_engine import PriorityEngine
from coppersun_brass.agents.strategist.duplicate_detector import DuplicateDetector
from coppersun_brass.agents.strategist.orchestration_engine import OrchestrationEngine
from coppersun_brass.agents.strategist.meta_reasoning.historical_analyzer import HistoricalAnalyzer
from coppersun_brass.agents.strategist.meta_reasoning.dcp_snapshot_manager import DCPSnapshotManager
from coppersun_brass.agents.strategist.meta_reasoning.diff_engine import DiffEngine
from coppersun_brass.agents.strategist.predictive.prediction_engine import PredictionEngine
from coppersun_brass.agents.strategist.predictive.prediction_config import PredictionConfig
from coppersun_brass.agents.strategist.planning.intelligence_coordinator import IntelligenceCoordinator
from coppersun_brass.agents.strategist.autonomous.best_practices_engine import BestPracticesEngine
from coppersun_brass.agents.strategist.autonomous.gap_detector import GapDetector
from coppersun_brass.agents.base_agent import DCPAwareAgent
from coppersun_brass.core.context.dcp_coordination import DCPCoordinator, CoordinationMessage
from coppersun_brass.core.constants import AgentNames, TimeWindows, ObservationTypes

logger = logging.getLogger(__name__)

class StrategistAgent(DCPAwareAgent):
    """
    Central coordination agent for Copper Sun Brass ecosystem.
    Orchestrates DCP updates, prioritizes observations, and routes tasks.
    """
    
    def __init__(self, project_path: str, config: Optional[Dict] = None, dcp_path: Optional[str] = None, dcp_adapter: Optional[Any] = None):
        # Initialize DCP-aware base class
        super().__init__(
            project_path=project_path,
            dcp_path=dcp_path,
            dcp_adapter=dcp_adapter,
            context_window_hours=(config or {}).get('context_window_hours', TimeWindows.STRATEGIST_CONTEXT)
        )
        
        self.config = config or {}
        self.agent_id = AgentNames.STRATEGIST
        self._previous_boot = None  # Track hot vs cold starts
        
        # Core components
        self.priority_engine = PriorityEngine(self.config.get('priority', {}))
        self.duplicate_detector = DuplicateDetector(self.config.get('duplicates', {}))
        
        # Meta-reasoning components (defer snapshot manager to avoid concurrent DB access during init)
        snapshot_dir = self.project_path / ".brass" / "snapshots"
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.snapshot_dir = snapshot_dir
        self.snapshot_manager = None  # Lazy-loaded to prevent database conflicts during init
        self.diff_engine = DiffEngine()
        self.historical_analyzer = None  # Lazy-loaded since it depends on snapshot_manager
        
        # Predictive analytics components (defer to avoid DB conflicts)
        self.prediction_config = PredictionConfig()
        self.prediction_engine = None  # Lazy-loaded since it depends on historical_analyzer
        
        # Planning intelligence components
        self.intelligence_coordinator = IntelligenceCoordinator()
        # Integrations will be set lazily when components are initialized
        
        # Autonomous analysis components
        self.best_practices_engine = BestPracticesEngine(
            dcp_path=dcp_path
        )
        # Initialize GapDetector with the shared DCP adapter instead of creating its own
        self.gap_detector = GapDetector(
            project_root=self.project_path
        )
        # Pass shared DCP manager to prevent database conflicts
        if hasattr(self.gap_detector, 'dcp_manager') and self.dcp_manager:
            self.gap_detector.dcp_manager = self.dcp_manager
        
        # Initialize orchestration engine with all components
        self.orchestration_engine = OrchestrationEngine(
            self.dcp_manager, 
            self.priority_engine,
            self.duplicate_detector,
            self.best_practices_engine,
            self.gap_detector
        )
        
        # State tracking
        self.last_orchestration = None
        self.orchestration_metrics = {
            'total_cycles': 0,
            'observations_processed': 0,
            'duplicates_detected': 0,
            'priorities_assigned': 0,
            'average_cycle_time': 0.0
        }
        
        # Context already loaded by base class
    
    def _ensure_components_initialized(self):
        """Lazy initialization of database-dependent components."""
        if self.snapshot_manager is None:
            self.snapshot_manager = DCPSnapshotManager(
                db_path=str(self.snapshot_dir / "snapshots.db"),
                storage_path=str(self.snapshot_dir)
            )
        
        if self.historical_analyzer is None:
            self.historical_analyzer = HistoricalAnalyzer(
                self.dcp_manager,
                self.snapshot_manager,
                self.diff_engine
            )
        
        if self.prediction_engine is None:
            self.prediction_engine = PredictionEngine(
                self.historical_analyzer,
                self.dcp_manager,
                None,  # Event bus being phased out
                self.prediction_config
            )
            
            # Set integrations now that components are ready
            self.intelligence_coordinator.set_historical_analyzer(self.historical_analyzer)
            self.intelligence_coordinator.set_prediction_engine(self.prediction_engine)
    
    @property
    def agent_name(self) -> str:
        """Return the agent's identifier."""
        return AgentNames.STRATEGIST
    
    @property
    def relevant_observation_types(self) -> List[str]:
        """Define which observation types this agent needs on startup."""
        return [
            'capability_assessment', 'strategic_recommendation',
            'orchestration_complete', 'priority_assignment',
            'duplicate_detection', 'gap_detection', 'best_practice'
        ]
        
        logger.info(f"Strategist Agent initialized for project: {project_path}")
    
    
    def _process_startup_context(self, context: Dict[str, List[Dict[str, Any]]]) -> None:
        """Process loaded context from base class.
        
        Args:
            context: Dict mapping observation types to lists of observations
        """
        # Extract observations by type
        capability_assessments = context.get('capability_assessment', [])
        strategic_recommendations = context.get('strategic_recommendation', [])
        orchestration_history = context.get('orchestration_complete', [])
        priority_history = context.get('priority_assignment', [])
        duplicate_history = context.get('duplicate_detection', [])
        
        # Initialize decision state from context
        self._initialize_strategy(
            capability_assessments,
            strategic_recommendations,
            orchestration_history,
            priority_history,
            duplicate_history
        )
        
        # Log what was loaded
        total_observations = sum(len(obs_list) for obs_list in context.values())
        logger.info(f"Strategist processed {total_observations} observations from startup context")
        self._previous_boot = 'hot' if total_observations > 0 else 'cold'
        
        if self.dcp_manager:
            self.dcp_manager.add_observation({
                'type': 'startup_time',
                'agent': 'strategist',
                'duration_ms': (time.time() - start_time) * 1000,
                'is_cold_start': is_cold_start,
                'observations_loaded': total_observations,
                'context_categories': ['capability_assessment', 'strategic_recommendation', 
                                     'orchestration_complete', 'priority_assignment', 'duplicate_detection'],
                'components_initialized': self._get_component_count()
            }, source_agent='strategist')
                
        logger.info(f"Strategist agent loaded context: {len(capability_assessments)} assessments, "
                   f"{len(strategic_recommendations)} recommendations, {len(orchestration_history)} orchestrations")
    
    def _initialize_strategy(self, capability_assessments, strategic_recommendations, 
                           orchestration_history, priority_history, duplicate_history):
        """Initialize decision state from loaded DCP context."""
        
        # Configure priority engine based on historical assignments
        if priority_history:
            # Extract priority patterns from history
            priority_scores = []
            for obs in priority_history[-20:]:  # Last 20 priority assignments
                if 'details' in obs and 'calculated_priority' in obs['details']:
                    priority_scores.append(obs['details']['calculated_priority'])
            
            if priority_scores:
                avg_priority = sum(priority_scores) / len(priority_scores)
                # Adjust priority thresholds based on historical patterns
                if hasattr(self.priority_engine, 'adjust_thresholds'):
                    self.priority_engine.adjust_thresholds(baseline=avg_priority)
                logger.debug(f"Adjusted priority thresholds based on avg priority: {avg_priority:.1f}")
        
        # Configure duplicate detector based on detection history
        if duplicate_history:
            # Extract duplicate patterns
            duplicate_patterns = set()
            for obs in duplicate_history[-10:]:  # Last 10 duplicate detections
                if 'details' in obs and 'duplicate_type' in obs['details']:
                    duplicate_patterns.add(obs['details']['duplicate_type'])
            
            # Update duplicate detector sensitivity
            if duplicate_patterns and hasattr(self.duplicate_detector, 'update_patterns'):
                self.duplicate_detector.update_patterns(list(duplicate_patterns))
                logger.debug(f"Updated duplicate patterns: {duplicate_patterns}")
        
        # Set orchestration timing based on history
        if orchestration_history:
            # Calculate average orchestration cycle time
            cycle_times = []
            for obs in orchestration_history[-5:]:  # Last 5 orchestrations
                if 'details' in obs and 'cycle_time' in obs['details']:
                    cycle_times.append(obs['details']['cycle_time'])
            
            if cycle_times:
                avg_cycle_time = sum(cycle_times) / len(cycle_times)
                self.orchestration_metrics['average_cycle_time'] = avg_cycle_time
                logger.debug(f"Set expected cycle time based on history: {avg_cycle_time:.2f}s")
        
        # Initialize prediction engine with historical data
        if strategic_recommendations and hasattr(self.prediction_engine, 'initialize_from_recommendations'):
            self.prediction_engine.initialize_from_recommendations(strategic_recommendations)
        
        # Track previous boot for hot start detection
        self._previous_boot = time.time()
    
    def _cold_boot_initialization(self):
        """Initialize agent without DCP context (fallback mode)."""
        logger.info("Strategist agent starting in cold boot mode")
        # Set conservative defaults
        self.orchestration_metrics['average_cycle_time'] = 5.0  # Conservative 5s estimate
        self._previous_boot = None
        
        # Initialize components with default settings
        if hasattr(self.priority_engine, 'reset_to_defaults'):
            self.priority_engine.reset_to_defaults()
        if hasattr(self.duplicate_detector, 'reset_to_defaults'):
            self.duplicate_detector.reset_to_defaults()
    
    def _get_component_count(self) -> int:
        """Get count of initialized components."""
        components = [
            self.priority_engine, self.duplicate_detector, self.orchestration_engine,
            self.snapshot_manager, self.diff_engine, self.historical_analyzer,
            self.prediction_engine, self.intelligence_coordinator,
            self.best_practices_engine, self.gap_detector
        ]
        return len([c for c in components if c is not None])
    
    async def orchestrate_dcp_updates(self, force: bool = False) -> Dict[str, Any]:
        """
        Main orchestration cycle - coordinates all DCP updates
        
        Args:
            force: Force orchestration even if no changes detected
            
        Returns:
            Dict with orchestration results and metrics
        """
        # Ensure components are initialized before use
        self._ensure_components_initialized()
        
        start_time = time.time()
        
        try:
            logger.info("Starting DCP orchestration cycle")
            
            # Load current DCP state
            current_dcp = self.dcp_manager.read_dcp()
            
            # Check if orchestration needed
            if not force and not self._needs_orchestration(current_dcp):
                logger.debug("No orchestration needed")
                return {'status': 'skipped', 'reason': 'no_changes'}
            
            # Run orchestration
            result = await self.orchestration_engine.orchestrate(current_dcp)
            
            # Update metrics
            cycle_time = time.time() - start_time
            self._update_metrics(result, cycle_time)
            
            # Dual publish during migration
            orchestration_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'result': result,
                'cycle_time': cycle_time
            }
            
            # Publish via DCP coordination
            if self.dcp_coordinator:
                self.dcp_coordinator.publish(CoordinationMessage(
                    observation_type=ObservationTypes.ORCHESTRATION_COMPLETE,
                    source_agent=self.agent_name,
                    data=orchestration_data,
                    metadata={'cycle_time': cycle_time},
                    broadcast=True
                ))
            
            self.last_orchestration = datetime.now(timezone.utc)
            
            logger.info(f"Orchestration cycle complete in {cycle_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Orchestration cycle failed: {e}", exc_info=True)
            return {'status': 'error', 'error': str(e)}
    
    def analyze_patterns(self, observations: List[Dict]) -> List[Dict]:
        """
        Analyze patterns in observations using historical data.
        
        Args:
            observations: List of observation dictionaries
            
        Returns:
            List of pattern analysis results
        """
        # Ensure components are initialized before use
        self._ensure_components_initialized()
        
        try:
            if self.historical_analyzer:
                return self.historical_analyzer.analyze_patterns(observations)
            else:
                logger.warning("Historical analyzer not available for pattern analysis")
                return []
        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
            return []
    
    def prioritize_observations(self, observations: List[Dict]) -> List[Dict]:
        """
        Score and rank observations by priority
        
        Args:
            observations: List of observation dictionaries
            
        Returns:
            Observations sorted by priority (highest first)
        """
        logger.debug(f"Prioritizing {len(observations)} observations")
        
        # Score each observation
        scored_observations = []
        for obs in observations:
            try:
                priority_score = self.priority_engine.calculate_priority(obs)
                obs_with_score = obs.copy()
                obs_with_score['calculated_priority'] = priority_score
                obs_with_score['priority_rationale'] = self.priority_engine.get_rationale(obs)
                scored_observations.append(obs_with_score)
            except Exception as e:
                logger.warning(f"Failed to score observation {obs.get('id', 'unknown')}: {e}")
                # Keep original priority or assign default
                obs_with_score = obs.copy()
                obs_with_score['calculated_priority'] = obs.get('priority', 50)
                scored_observations.append(obs_with_score)
        
        # Sort by calculated priority (descending)
        prioritized = sorted(
            scored_observations, 
            key=lambda x: x['calculated_priority'], 
            reverse=True
        )
        
        logger.info(f"Prioritized observations: {len(prioritized)} total")
        return prioritized
    
    def detect_duplicates(self, observations: List[Dict]) -> Dict[str, List[str]]:
        """
        Identify duplicate observations across agents
        
        Args:
            observations: List of observations to check
            
        Returns:
            Dict mapping canonical observation IDs to lists of duplicate IDs
        """
        return self.duplicate_detector.find_duplicates(observations)
    
    def route_tasks_to_agents(self, observations: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Route observations to appropriate agents for action
        
        Args:
            observations: Prioritized observations
            
        Returns:
            Dict mapping agent names to their assigned tasks
        """
        routing = {
            'watch': [],
            'scout': [],
            'claude': [],
            'human': []
        }
        
        for obs in observations:
            obs_type = obs.get('type', 'unknown')
            priority = obs.get('calculated_priority', obs.get('priority', 50))
            
            # Routing logic based on observation type and priority
            if obs_type in ['todo_item', 'fixme_item', 'research_needed']:
                # High priority TODOs go to Claude, others to Scout
                if priority >= 80:
                    routing['claude'].append(obs)
                else:
                    routing['scout'].append(obs)
            
            elif obs_type in ['security', 'critical_bug']:
                # Security issues always go to human review
                routing['human'].append(obs)
            
            elif obs_type in ['file_change', 'code_analysis']:
                # File changes handled by Watch agent
                routing['watch'].append(obs)
            
            elif obs_type in ['performance', 'optimization']:
                # Performance issues can be handled by Claude
                routing['claude'].append(obs)
            
            else:
                # Default routing based on priority
                if priority >= 90:
                    routing['human'].append(obs)
                elif priority >= 70:
                    routing['claude'].append(obs)
                else:
                    routing['scout'].append(obs)
        
        # Log routing decisions
        for agent, tasks in routing.items():
            if tasks:
                logger.info(f"Routed {len(tasks)} tasks to {agent}")
        
        return routing
    
    def _handle_agent_status_observation(self, observation: Dict[str, Any]):
        """Handle agent status observations from DCP."""
        metadata = observation.get('metadata', {})
        data = observation.get('data', {})
        source = metadata.get('source_agent', 'unknown')
        status = metadata.get('status', 'unknown')
        
        logger.info(f"Agent {source} status: {status}")
        
        # Could trigger orchestration if key agent comes online
        if status == 'started' and source in ['watch', 'scout']:
            self._schedule_orchestration()
    
    def _handle_analysis_result_observation(self, observation: Dict[str, Any]):
        """Handle analysis result observations from DCP."""
        # Trigger orchestration to process new analysis results
        self._schedule_orchestration()
    
    def _handle_todo_observation(self, observation: Dict[str, Any]):
        """Handle TODO observations from DCP."""
        # High priority TODOs might trigger immediate orchestration
        metadata = observation.get('metadata', {})
        priority = metadata.get('priority', 50)
        
        if priority >= 80:
            logger.info(f"High priority TODO detected, scheduling orchestration")
            self._schedule_orchestration()
    
    def _schedule_orchestration(self):
        """Schedule an orchestration cycle."""
        # This could be enhanced with debouncing/throttling
        try:
            self.orchestrate()
        except Exception as e:
            logger.error(f"Failed to schedule orchestration: {e}")
    
    def get_orchestration_status(self) -> Dict[str, Any]:
        """Get current strategist status and metrics"""
        return {
            'agent_id': self.agent_id,
            'last_orchestration': self.last_orchestration.isoformat() if self.last_orchestration else None,
            'metrics': self.orchestration_metrics.copy(),
            'dcp_coordinator_active': self.dcp_coordinator is not None,
            'dcp_status': self.dcp_manager.get_dcp_info(),
            'components': {
                'priority_engine': self.priority_engine.get_status(),
                'duplicate_detector': self.duplicate_detector.get_status(),
                'orchestration_engine': self.orchestration_engine.get_status()
            }
        }
    
    def _needs_orchestration(self, current_dcp: Dict) -> bool:
        """Determine if orchestration cycle is needed"""
        # Check for new observations since last orchestration
        if not self.last_orchestration:
            return True
        
        # Check for recent DCP modifications
        try:
            dcp_path = self.dcp_manager.dcp_file_path
            if dcp_path.exists():
                dcp_modified = datetime.fromtimestamp(dcp_path.stat().st_mtime, tz=timezone.utc)
                if dcp_modified > self.last_orchestration:
                    return True
        except Exception:
            pass
        
        # Check for unprocessed observations
        observations = current_dcp.get('current_observations', [])
        unprocessed = [obs for obs in observations if not obs.get('strategist_processed')]
        
        return len(unprocessed) > 0
    
    def _update_metrics(self, result: Dict, cycle_time: float):
        """Update orchestration metrics"""
        self.orchestration_metrics['total_cycles'] += 1
        self.orchestration_metrics['observations_processed'] += result.get('observations_processed', 0)
        self.orchestration_metrics['duplicates_detected'] += result.get('duplicates_found', 0)
        self.orchestration_metrics['priorities_assigned'] += result.get('priorities_updated', 0)
        
        # Update average cycle time
        total_cycles = self.orchestration_metrics['total_cycles']
        current_avg = self.orchestration_metrics['average_cycle_time']
        self.orchestration_metrics['average_cycle_time'] = (
            (current_avg * (total_cycles - 1) + cycle_time) / total_cycles
        )
    
    # Historical Analysis Methods
    async def capture_snapshot(self, tags: Optional[List[str]] = None) -> str:
        """Capture a DCP snapshot for historical analysis"""
        try:
            current_dcp = self.dcp_manager.read_dcp()
            snapshot_id = await self.snapshot_manager.capture_snapshot(
                project_id=str(self.project_path.name),
                dcp_data=current_dcp,
                tags=tags or []
            )
            logger.info(f"Captured DCP snapshot: {snapshot_id}")
            return snapshot_id
        except Exception as e:
            logger.error(f"Failed to capture snapshot: {e}")
            raise
    
    async def analyze_trends(self, timeframe_days: int = 30) -> Dict:
        """Analyze DCP trends over specified timeframe"""
        try:
            trends = await self.historical_analyzer.analyze_trends(
                project_id=str(self.project_path.name),
                timeframe_days=timeframe_days
            )
            return trends
        except Exception as e:
            logger.error(f"Failed to analyze trends: {e}")
            return {}
    
    async def generate_health_score(self) -> Dict:
        """Generate project health score based on historical data"""
        try:
            health = await self.historical_analyzer.generate_health_score(
                project_id=str(self.project_path.name)
            )
            return health.__dict__ if health else {}
        except Exception as e:
            logger.error(f"Failed to generate health score: {e}")
            return {}
    
    async def detect_drift(self, baseline_id: Optional[str] = None) -> Dict:
        """Detect architectural drift from baseline"""
        try:
            drift = await self.historical_analyzer.detect_drift(
                project_id=str(self.project_path.name),
                baseline_snapshot_id=baseline_id
            )
            return drift.__dict__ if drift else {}
        except Exception as e:
            logger.error(f"Failed to detect drift: {e}")
            return {}
    
    # Predictive Analytics Methods
    async def generate_predictions(self, prediction_types: Optional[List[str]] = None) -> Dict:
        """Generate predictions for the project"""
        try:
            predictions = await self.prediction_engine.generate_predictions(
                project_id=str(self.project_path.name),
                prediction_types=prediction_types
            )
            return predictions
        except Exception as e:
            logger.error(f"Failed to generate predictions: {e}")
            return {}
    
    async def predict_timeline(self, current_velocity: Optional[float] = None) -> Dict:
        """Generate timeline predictions"""
        try:
            timeline = await self.prediction_engine.predict_timeline(
                project_id=str(self.project_path.name),
                current_velocity=current_velocity
            )
            return timeline
        except Exception as e:
            logger.error(f"Failed to predict timeline: {e}")
            return {}
    
    async def get_prediction_recommendations(self) -> List[Dict]:
        """Get recommendations based on predictions"""
        try:
            recommendations = await self.prediction_engine.get_recommendations(
                project_id=str(self.project_path.name)
            )
            return recommendations
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            return []
    
    # Planning Intelligence Methods
    async def generate_intelligent_plan(
        self, 
        goals: List[str], 
        constraints: Optional[Dict] = None,
        use_learning: bool = True
    ) -> Dict:
        """Generate intelligent plan with goal decomposition and constraint solving"""
        try:
            # Create planning context
            from coppersun_brass.agents.strategist.planning.intelligence_coordinator import PlanningContext
            from coppersun_brass.agents.strategist.planning.constraint_solver import Agent
            
            # Convert constraints to planning context
            available_agents = [
                Agent(
                    id="scout", 
                    name="Scout",
                    skills=["research", "analysis", "todo_detection"],
                    max_concurrent_tasks=5,
                    hourly_capacity=8.0,
                    efficiency_rating=0.9,
                    specializations=["code_analysis", "documentation"]
                ),
                Agent(
                    id="watch",
                    name="Watch",
                    skills=["monitoring", "tracking", "file_analysis"],
                    max_concurrent_tasks=10,
                    hourly_capacity=24.0,  # Continuous monitoring
                    efficiency_rating=0.95,
                    specializations=["real_time_monitoring", "change_detection"]
                ),
                Agent(
                    id="claude",
                    name="Claude",
                    skills=["implementation", "review", "planning"],
                    max_concurrent_tasks=3,
                    hourly_capacity=6.0,
                    efficiency_rating=0.85,
                    specializations=["ai_planning", "code_generation"]
                )
            ]
            
            context = PlanningContext(
                goals=goals,
                constraints=constraints or {},
                available_agents=available_agents,
                existing_observations=self.dcp_manager.read_dcp().get('current_observations', []) if self.dcp_manager else [],
                timeline_constraints={},
                resource_constraints={},
                priority_weights={}
            )
            
            # Generate comprehensive plan
            result = await self.intelligence_coordinator.generate_comprehensive_plan(
                goals=goals,
                context=context
            )
            
            # Convert result to dictionary
            return result.__dict__ if result else {}
        except Exception as e:
            logger.error(f"Failed to generate intelligent plan: {e}")
            return {}
    
    async def adapt_plan(
        self,
        plan_id: str,
        trigger_event: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """Adapt existing plan based on new conditions"""
        try:
            adapted_plan = await self.intelligence_coordinator.adapt_plan(
                plan_id=plan_id,
                trigger_event=trigger_event,
                context=context or {}
            )
            return adapted_plan
        except Exception as e:
            logger.error(f"Failed to adapt plan: {e}")
            return {}
    
    async def get_planning_insights(self) -> Dict:
        """Get insights from planning intelligence"""
        try:
            insights = await self.intelligence_coordinator.get_planning_insights()
            return insights
        except Exception as e:
            logger.error(f"Failed to get planning insights: {e}")
            return {}
    
    # Event handlers
    async def _handle_watch_analysis(self, event_data: Dict):
        """Handle Watch agent analysis completion"""
        logger.debug("Received watch analysis event")
        await self.orchestrate_dcp_updates()
    
    async def _handle_scout_research(self, event_data: Dict):
        """Handle Scout agent research completion"""
        logger.debug("Received scout research event")
        await self.orchestrate_dcp_updates()
    
    # Best Practices and Gap Detection Methods
    async def analyze_best_practices(self, observations: Optional[List[Dict]] = None) -> List[Dict]:
        """Analyze project against best practices"""
        try:
            if observations is None:
                # Get recent observations from DCP
                observations = self.dcp_manager.get_observations()
            
            # Extract project info for best practices analysis
            project_type = self.dcp_manager.get_project_type()
            
            # Create capabilities dict from observations
            capabilities = {}
            for obs in observations:
                if obs.get('type') == 'capability_assessment':
                    details = obs.get('details', {})
                    for cap_name, score in details.items():
                        if isinstance(score, (int, float)):
                            capabilities[cap_name] = score / 100.0  # Normalize to 0-1
            
            # Get recommendations from best practices engine
            recommendations = self.best_practices_engine.get_recommendations(
                project_type=project_type,
                capabilities=capabilities,
                gaps=[],  # Will be populated when we have gap detection results
                frameworks=[]  # Could be detected from project
            )
            
            # Store recommendations in DCP
            for rec in recommendations:
                self.dcp_manager.add_observation(
                    obs_type='best_practice',
                    data=rec,
                    source_agent=self.agent_name,
                    priority=rec.get('priority', 60)
                )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Best practices analysis failed: {e}")
            return []
    
    async def detect_project_gaps(self, context: Optional[Dict] = None) -> List[Dict]:
        """Detect gaps in project capabilities and coverage"""
        try:
            # For gap detection, we need ProjectCapabilities object
            # Create a mock one from available data
            from coppersun_brass.agents.strategist.autonomous.capability_assessor import ProjectCapabilities, CapabilityScore
            from datetime import datetime
            
            # Get observations to build capabilities
            observations = self.dcp_manager.get_observations()
            project_type = self.dcp_manager.get_project_type()
            
            # Build capabilities from observations
            capabilities_dict = {}
            for obs in observations:
                if obs.get('type') == 'capability_assessment':
                    details = obs.get('details', {})
                    for cap_name, score in details.items():
                        if isinstance(score, (int, float)):
                            capabilities_dict[cap_name] = CapabilityScore(
                                name=cap_name,
                                category='general',
                                score=float(score),
                                confidence=0.7,
                                details={},
                                missing_components=[],
                                recommendations=[]
                            )
            
            # Create ProjectCapabilities object
            project_capabilities = ProjectCapabilities(
                project_type=project_type,
                assessment_time=datetime.now(),
                overall_score=70.0,  # Default
                overall_confidence=0.7,
                capabilities=capabilities_dict,
                strengths=[],
                weaknesses=[],
                critical_gaps=[]
            )
            
            # Run gap detection
            gap_analysis = await self.gap_detector.find_gaps(project_capabilities)
            
            # Convert gaps to dict format and store in DCP
            gap_dicts = []
            all_gaps = (gap_analysis.critical_gaps + gap_analysis.important_gaps + 
                       gap_analysis.recommended_gaps + gap_analysis.nice_to_have_gaps)
            
            for gap in all_gaps:
                gap_dict = {
                    'type': 'gap_detection',
                    'category': gap.category,
                    'capability_name': gap.capability_name,
                    'description': f"Gap in {gap.capability_name}: current score {gap.current_score:.1f}, target {gap.target_score:.1f}",
                    'gap_size': gap.gap_size,
                    'confidence': gap.confidence,
                    'priority': gap.risk_score,  # Use risk score as priority
                    'risk_level': 'high' if gap.risk_score >= 70 else 'medium' if gap.risk_score >= 50 else 'low',
                    'estimated_effort': gap.estimated_effort,
                    'dependencies': gap.dependencies,
                    'recommended_actions': gap.recommendations,
                    'security_related': gap.security_related,
                    'compliance_related': gap.compliance_related
                }
                
                # Store in DCP
                self.dcp_manager.add_observation(
                    obs_type='gap_detection',
                    data=gap_dict,
                    source_agent=self.agent_name,
                    priority=gap.priority
                )
                
                gap_dicts.append(gap_dict)
            
            return gap_dicts
            
        except Exception as e:
            logger.error(f"Gap detection failed: {e}")
            return []
    
    def _get_observation_type_distribution(self, observations: List[Dict]) -> Dict[str, int]:
        """Get distribution of observation types"""
        distribution = {}
        for obs in observations:
            obs_type = obs.get('type', 'unknown')
            distribution[obs_type] = distribution.get(obs_type, 0) + 1
        return distribution
    
    def _get_priority_distribution(self, observations: List[Dict]) -> Dict[str, int]:
        """Get distribution of priorities"""
        distribution = {'high': 0, 'medium': 0, 'low': 0}
        for obs in observations:
            priority = obs.get('priority', 50)
            if priority >= 80:
                distribution['high'] += 1
            elif priority >= 50:
                distribution['medium'] += 1
            else:
                distribution['low'] += 1
        return distribution
    
    # Event handlers removed - using DCP observation handlers instead
    
    async def start(self):
        """Start the strategist agent"""
        logger.info("Starting Strategist Agent")
        
        # Start DCP coordinator polling
        if self.dcp_coordinator:
            self.dcp_coordinator.start_polling()
        
        # Initial orchestration
        await self.orchestrate_dcp_updates(force=True)
        
        # Event loop removed - using DCP coordination
    
    async def stop(self):
        """Stop the strategist agent"""
        logger.info("Stopping Strategist Agent")
        
        # Stop DCP coordinator polling
        if self.dcp_coordinator:
            self.dcp_coordinator.stop_polling()
        
        # Event loop removed - using DCP coordination
    
    def _cleanup(self) -> None:
        """Clean up agent resources."""
        # Stop DCP coordinator if running
        if hasattr(self, 'dcp_coordinator') and self.dcp_coordinator:
            self.dcp_coordinator.stop_polling()
        
        # Clean up any other resources
        logger.debug("Strategist agent cleanup complete")
