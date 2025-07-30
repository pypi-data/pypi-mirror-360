"""
Copper Sun Brass Runner - Async orchestration without subprocess overhead

Key improvements:
- Direct imports instead of subprocess
- Async execution for better performance
- Graceful error handling
- Resource management
"""
import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
import importlib.util

from .config import BrassConfig
from .core.storage import BrassStorage
from .core.dcp_adapter import DCPAdapter
from .ml.ml_pipeline import MLPipeline

# Import agents directly - no subprocess!
from .agents.scout.scout_agent import ScoutAgent
from .agents.watch.watch_agent import WatchAgent
from .agents.strategist.strategist_agent import StrategistAgent
from .agents.planner.task_generator import TaskGenerator

# Import learning system - RESTORED with codebase learning (zero dependencies)
from .core.learning.codebase_learning_coordinator import CodebaseLearningCoordinator
from .core.output_generator import OutputGenerator

logger = logging.getLogger(__name__)


class BrassRunner:
    """Efficient async runner for Copper Sun Brass agents.
    
    Replaces subprocess-based execution with direct imports:
    - 10x faster startup
    - Shared memory/cache
    - Better error handling
    - No serialization overhead
    """
    
    def __init__(self, config: BrassConfig):
        """Initialize runner with configuration.
        
        Args:
            config: Copper Sun Brass configuration
        """
        self.config = config
        self.project_root = config.project_root
        
        # Initialize storage
        self.storage = BrassStorage(config.data_dir / "coppersun_brass.db")
        
        # Initialize DCP adapter for agents
        self.dcp = DCPAdapter(self.storage, self.project_root)
        
        # Initialize ML pipeline
        self.ml_pipeline = MLPipeline(
            config.data_dir / 'models',
            self.storage
        )
        
        # Initialize codebase learning coordinator (RESTORED functionality)
        self.training_coordinator = CodebaseLearningCoordinator(
            dcp_adapter=self.dcp,  # Pass the DCPAdapter instance
            config=config,
            team_id=None  # Can be configured later
        )
        self.last_training_check = datetime.now()
        self.training_check_interval = timedelta(hours=1)
        
        
        # Agent instances (lazy loaded)
        self.agents: Dict[str, Any] = {}
        self.running_agents: Set[asyncio.Task] = set()
        
        # Shutdown handling
        self.shutdown_event = asyncio.Event()
        self._setup_signal_handlers()
        
        # Performance tracking
        self.stats = {
            'runs': 0,
            'errors': 0,
            'total_observations': 0,
            'avg_run_time_ms': 0,
            'training_runs': 0
        }
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown handlers."""
        def signal_handler(sig, frame):
            logger.info(f"Received signal {sig}, initiating shutdown...")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def initialize_agents(self):
        """Initialize agent instances."""
        logger.info("Initializing agents...")
        
        try:
            # Scout agent - code analysis (pass shared DCPAdapter to prevent database conflicts)
            self.agents['scout'] = ScoutAgent(
                dcp_manager=self.dcp,  # Use shared DCPAdapter
                project_root=self.project_root
            )
            
            # Watch agent - file monitoring (pass shared DCPAdapter)
            self.agents['watch'] = WatchAgent(
                config_or_dcp=self.dcp,  # Use shared DCPAdapter
                config={
                    'project_path': str(self.project_root),
                    'analysis_interval': 300  # 5 minutes
                }
            )
            
            # Strategist agent - orchestration and prioritization (use shared DCPAdapter via base class)
            self.agents['strategist'] = StrategistAgent(
                project_path=str(self.project_root),
                dcp_adapter=self.dcp,  # Pass shared DCPAdapter to base class
                config={}
            )
            
            # Planner agent - task generation and planning (pass shared learning coordinator)
            self.agents['planner'] = TaskGenerator(
                dcp_manager=self.dcp,  # Keep using shared DCPAdapter
                learning_integration=self.training_coordinator  # Use shared learning coordinator
            )
            
            logger.info(f"Initialized {len(self.agents)} agents")
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            raise
    
    async def run_scout_analysis(self) -> List[Dict[str, Any]]:
        """Run Scout agent analysis.
        
        Returns:
            List of observations from Scout
        """
        start_time = asyncio.get_event_loop().time()
        observations = []
        
        try:
            scout = self.agents.get('scout')
            if not scout:
                logger.warning("Scout agent not initialized")
                return []
            
            logger.info("Running Scout analysis...")
            
            # Get files to analyze
            files_to_analyze = await self._get_changed_files()
            
            logger.info(f"Scout will analyze {len(files_to_analyze)} files")
            
            if not files_to_analyze:
                logger.info("No files to analyze")
                return []
            
            # Run analysis
            for file_path in files_to_analyze:
                try:
                    # Scout's analyze method
                    result = await asyncio.to_thread(
                        scout.analyze,
                        str(file_path),
                        deep_analysis=True   # Enable comprehensive analysis
                    )
                    
                    if result:
                        # Debug logging
                        logger.info(f"Scout analyzed {file_path}: {len(result.todo_findings)} TODOs found")
                        
                        # Convert ScoutAnalysisResult to observations
                        obs = result.to_dcp_observations()
                        observations.extend(obs)
                        
                        # Convert TODO findings to observations with ALL rich data preserved
                        for finding in result.todo_findings:
                            observations.append({
                                'type': 'todo',
                                'priority': finding.priority_score,
                                'summary': f"{finding.todo_type}: {finding.content}",
                                'confidence': finding.confidence,
                                'data': {
                                    'file_path': finding.file_path,
                                    'line_number': finding.line_number,
                                    'content': finding.content,
                                    'todo_type': finding.todo_type,              # TODO, FIXME, BUG
                                    'confidence': finding.confidence,             # 0.0-1.0 ML confidence
                                    'priority_score': finding.priority_score,    # 0-100 calculated priority
                                    'is_researchable': finding.is_researchable,  # Research opportunity flag
                                    'context_lines': finding.context_lines,      # Surrounding code context
                                    'content_hash': finding.content_hash,        # Unique tracking ID
                                    'created_at': finding.created_at.isoformat() # Timestamp for evolution
                                }
                            })
                        
                        # Convert AST analysis CodeIssue observations
                        for ast_result in result.ast_results:
                            for issue in ast_result.issues:
                                observations.append({
                                    'type': 'code_issue',
                                    'subtype': issue.issue_type,
                                    'priority': self._severity_to_priority(issue.severity),
                                    'summary': f"{issue.severity.upper()}: {issue.description}",
                                    'confidence': issue.metadata.get('confidence', 0.9),
                                    'data': {
                                        'issue_type': issue.issue_type,              # 'long_function', 'missing_docstring', etc.
                                        'severity': issue.severity,                  # 'low', 'medium', 'high', 'critical'
                                        'file_path': issue.file_path,
                                        'line_number': issue.line_number,
                                        'entity_name': issue.entity_name,
                                        'description': issue.description,
                                        'ai_recommendation': issue.ai_recommendation, # Strategic AI recommendation
                                        'fix_complexity': issue.fix_complexity,      # 'trivial', 'simple', 'moderate', 'complex'
                                        'metadata': issue.metadata                   # CWE mappings, OWASP references, etc.
                                    }
                                })

                        # Convert Pattern analysis CodeIssue observations  
                        for pattern_result in result.pattern_results:
                            for issue in pattern_result.issues:
                                observations.append({
                                    'type': 'security_issue',
                                    'subtype': issue.metadata.get('pattern_type', 'unknown'),
                                    'priority': self._severity_to_priority(issue.severity),
                                    'summary': f"Security: {issue.description}",
                                    'confidence': issue.metadata.get('confidence', 0.9),
                                    'data': {
                                        'pattern_name': issue.metadata.get('pattern_name', 'Unknown Pattern'),
                                        'cwe': issue.metadata.get('cwe', ''),
                                        'owasp': issue.metadata.get('owasp', ''),
                                        'severity': issue.severity,
                                        'file_path': issue.file_path,
                                        'line_number': issue.line_number,
                                        'entity_name': issue.entity_name,
                                        'description': issue.description,
                                        'ai_recommendation': issue.ai_recommendation,
                                        'fix_complexity': issue.fix_complexity,
                                        'metadata': issue.metadata
                                    }
                                })
                        
                        # Convert CodeEntity observations for complex or undocumented entities
                        for ast_result in result.ast_results:
                            for entity in ast_result.entities:
                                # Only store significant entities (high complexity or missing docs)
                                if entity.complexity_score > 10 or not entity.docstring:
                                    observations.append({
                                        'type': 'code_entity',
                                        'subtype': entity.entity_type,
                                        'priority': min(entity.complexity_score * 2, 100),
                                        'summary': f"{entity.entity_type.title()}: {entity.entity_name}",
                                        'confidence': 0.95,  # High confidence from AST analysis
                                        'data': {
                                            'entity_type': entity.entity_type,        # 'function', 'class', 'method', etc.
                                            'entity_name': entity.entity_name,
                                            'file_path': entity.file_path,
                                            'line_start': entity.line_start,
                                            'line_end': entity.line_end,
                                            'complexity_score': entity.complexity_score,
                                            'has_docstring': bool(entity.docstring),
                                            'docstring': entity.docstring,
                                            'parameters': entity.parameters,
                                            'decorators': entity.decorators,
                                            'parent_entity': entity.parent_entity,
                                            'dependencies': entity.dependencies,
                                            'metadata': entity.metadata
                                        }
                                    })
                        
                        # Convert CodeMetrics aggregate observations
                        for ast_result in result.ast_results:
                            if ast_result.metrics:
                                observations.append({
                                    'type': 'code_metrics',
                                    'priority': 50,
                                    'summary': f"File metrics: {ast_result.file_path}",
                                    'confidence': 0.99,
                                    'data': {
                                        'file_path': ast_result.file_path,
                                        'total_lines': ast_result.metrics.total_lines,
                                        'code_lines': ast_result.metrics.code_lines,
                                        'comment_lines': ast_result.metrics.comment_lines,
                                        'total_entities': ast_result.metrics.total_entities,
                                        'total_functions': ast_result.metrics.total_functions,
                                        'total_classes': ast_result.metrics.total_classes,
                                        'average_complexity': ast_result.metrics.average_complexity,
                                        'max_complexity': ast_result.metrics.max_complexity,
                                        'documentation_coverage': ast_result.metrics.documentation_coverage,
                                        'issues_by_severity': ast_result.metrics.issues_by_severity,
                                        'language_specific_metrics': ast_result.metrics.language_specific_metrics
                                    }
                                })

                        # Convert IssueEvolution observations for persistent issues
                        for persistent_issue in result.persistent_issues:
                            observations.append({
                                'type': 'persistent_issue',
                                'subtype': persistent_issue.issue_type,
                                'priority': min(persistent_issue.sprint_count * 20, 100),
                                'summary': f"Persistent ({persistent_issue.sprint_count} sprints): {persistent_issue.issue_type}",
                                'confidence': 0.9,
                                'data': {
                                    'issue_id': persistent_issue.issue_id,
                                    'issue_type': persistent_issue.issue_type,
                                    'file_path': persistent_issue.file_path,
                                    'line_number': persistent_issue.line_number,
                                    'first_seen': persistent_issue.first_seen.isoformat(),
                                    'last_seen': persistent_issue.last_seen.isoformat(),
                                    'occurrences': persistent_issue.occurrences,
                                    'sprint_count': persistent_issue.sprint_count,
                                    'resolution_attempts': persistent_issue.resolution_attempts,
                                    'persistence_days': (persistent_issue.last_seen - persistent_issue.first_seen).days,
                                    'strategic_importance': self._calculate_strategic_importance(persistent_issue)
                                }
                            })
                        
                except Exception as e:
                    logger.error(f"Error analyzing {file_path}: {e}")
                    self.stats['errors'] += 1
            
            # Process through ML pipeline
            if observations:
                logger.info(f"Sending {len(observations)} observations to ML pipeline")
                processed_observations = await self.ml_pipeline.process_observations(observations)
                logger.info(f"ML pipeline returned {len(processed_observations)} observations")
                observations = processed_observations
                
                # PHASE 3 CLAUDE ENHANCEMENT: Smart filtering and enhancement
                try:
                    # Select top 30% of observations for Claude enhancement
                    enhancement_candidates = await self.ml_pipeline.select_for_claude_enhancement(observations)
                    
                    if enhancement_candidates:
                        logger.info(f"Selected {len(enhancement_candidates)}/{len(observations)} observations for Claude enhancement")
                        
                        # Enhance with Claude API using optimized prompts
                        enhanced_observations = await self.ml_pipeline.enhance_observations_with_claude(enhancement_candidates)
                        
                        # Update the main observations list with enhanced data
                        enhanced_lookup = {id(obs): obs for obs in enhanced_observations}
                        for i, obs in enumerate(observations):
                            if id(obs) in enhanced_lookup:
                                observations[i] = enhanced_lookup[id(obs)]
                        
                        enhanced_count = sum(1 for obs in observations if obs.get('claude_enhanced', False))
                        logger.info(f"Phase 3 Claude enhancement completed: {enhanced_count} observations enhanced")
                    else:
                        logger.info("No observations selected for Claude enhancement")
                        
                except Exception as e:
                    logger.error(f"Phase 3 Claude enhancement failed (continuing with base analysis): {e}")
                    # Continue without enhancement - graceful degradation
            
            # Check if this is first run and trigger codebase learning
            is_first_run = self.storage.get_last_analysis_time() is None
            if is_first_run and observations:
                logger.info("First run detected - codebase learning handled by training_coordinator")
            
            # 🔧 TODO RESOLUTION DETECTION: Detect and mark resolved TODOs
            try:
                # Collect all current TODO findings from the analysis results
                current_todo_findings = []
                for file_path in files_to_analyze:
                    try:
                        # Re-run just the TODO detection to get TODOFinding objects
                        from .agents.scout.todo_detector import TODODetector
                        detector = TODODetector()
                        file_todos = detector.scan_file(str(file_path))
                        current_todo_findings.extend(file_todos)
                    except Exception as e:
                        logger.debug(f"Failed to collect TODOs from {file_path} for resolution detection: {e}")
                        continue
                
                if current_todo_findings:
                    resolved_count = self.storage.detect_resolved_todos(current_todo_findings)
                    if resolved_count > 0:
                        logger.info(f"🔄 TODO Resolution: Marked {resolved_count} TODOs as resolved")
                else:
                    logger.debug("No current TODO findings for resolution detection")
                    
            except Exception as e:
                logger.error(f"TODO resolution detection failed (continuing): {e}")
                # Continue execution - don't fail the entire analysis
            
            elapsed_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            logger.info(
                f"Scout analysis complete: {len(observations)} observations "
                f"in {elapsed_ms:.1f}ms"
            )
            
            # 🔧 CRITICAL FIX: Add missing DCP storage calls
            if observations:
                logger.info(f"Storing {len(observations)} observations in DCP...")
                for obs in observations:
                    try:
                        # Store observation in DCP database
                        data = obs.get('data', obs)
                        if 'metadata' in obs:
                            data['metadata'] = obs['metadata']
                        self.dcp.add_observation(
                            obs_type=obs.get('type', 'scout_analysis'),
                            data=data,
                            source_agent='scout',
                            priority=obs.get('priority', 50)
                        )
                    except Exception as e:
                        logger.error(f"Failed to store observation in DCP: {e}")
                
                # 🔧 CRITICAL FIX: Add missing output generation calls
                logger.info("Generating .brass intelligence files...")
                try:
                    output_generator = OutputGenerator(
                        config=self.config,
                        storage=self.storage
                    )
                    output_generator.generate_all_outputs()
                    logger.info("✅ .brass intelligence files generated successfully")
                except Exception as e:
                    logger.error(f"Failed to generate .brass files: {e}")
            
            # Update stats
            self.stats['runs'] += 1
            self.stats['total_observations'] += len(observations)
            self._update_avg_time(elapsed_ms)
            
            logger.info(f"Scout analysis complete with storage: {len(observations)} observations stored")
            return observations
            
        except Exception as e:
            logger.error(f"Scout analysis failed: {e}", exc_info=True)
            self.stats['errors'] += 1
            return []
    
    async def run_watch_monitoring(self):
        """Run Watch agent for continuous monitoring."""
        try:
            watch = self.agents.get('watch')
            if not watch:
                logger.warning("Watch agent not initialized")
                return
            
            logger.info("Starting Watch monitoring...")
            
            # Create watch task
            watch_task = asyncio.create_task(
                self._run_watch_loop(watch)
            )
            self.running_agents.add(watch_task)
            
            # Remove from set when done
            watch_task.add_done_callback(self.running_agents.discard)
            
        except Exception as e:
            logger.error(f"Failed to start Watch monitoring: {e}")
            self.stats['errors'] += 1
    
    async def _run_watch_loop(self, watch_agent):
        """Run watch agent monitoring loop."""
        while not self.shutdown_event.is_set():
            try:
                # Check for file changes
                changes = await asyncio.to_thread(
                    watch_agent.check_changes
                )
                
                if changes:
                    # Process through ML pipeline
                    processed = await self.ml_pipeline.process_observations(changes)
                    
                    # Store high-priority observations
                    for obs in processed:
                        if obs.get('classification') in ['critical', 'important']:
                            data = obs['data'].copy()
                            data['metadata'] = {
                                'classification': obs['classification'],
                                'confidence': obs['confidence']
                            }
                            self.storage.add_observation(
                                obs_type='file_change',
                                data=data,
                                source_agent='watch',
                                priority=obs.get('priority', 50)
                            )
                    
                    self.stats['total_observations'] += len(changes)
                
                # Wait before next check
                await asyncio.sleep(5.0)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Watch loop error: {e}")
                self.stats['errors'] += 1
                await asyncio.sleep(10.0)  # Back off on error
    
    async def _get_changed_files(self) -> List[Path]:
        """Get list of files that need analysis.
        
        Returns:
            List of file paths to analyze
        """
        try:
            # Get files modified since last run
            last_run = self.storage.get_last_analysis_time()
            
            # Check if file_state table is empty (indicates first run or cache cleared)
            file_state_count = None
            try:
                with self.storage.transaction() as conn:
                    file_state_count = conn.execute("SELECT COUNT(*) FROM file_state").fetchone()[0]
            except Exception as e:
                logger.warning(f"Could not check file_state count: {e}")
                file_state_count = 0
            
            if not last_run or file_state_count == 0:
                logger.info(f"First run or cache cleared - analyzing all files in {self.project_root}")
                logger.info(f"Last run time: {last_run}, File state count: {file_state_count}")
                # First run or cleared cache - analyze all Python files
                files = list(self.project_root.rglob("*.py"))
                # Add other important file types
                files.extend(self.project_root.rglob("*.js"))
                files.extend(self.project_root.rglob("*.ts"))
                logger.info(f"Found {len(files)} files before filtering")
            else:
                # Check all files but only analyze those that changed
                logger.info(f"Incremental run - checking for modified files in {self.project_root}")
                all_files = list(self.project_root.rglob("*.py"))
                all_files.extend(self.project_root.rglob("*.js"))
                all_files.extend(self.project_root.rglob("*.ts"))
                
                # Filter to only changed files
                files = []
                for f in all_files:
                    if not self._should_ignore(f) and self.storage.should_analyze_file(f):
                        files.append(f)
                
                logger.info(f"Found {len(files)} modified files out of {len(all_files)} total")
            
            # Filter out ignored paths
            files = [f for f in files if not self._should_ignore(f)]
            logger.info(f"After filtering: {len(files)} files to analyze")
            
            # Limit batch size for memory
            max_batch = 20  # Reasonable batch size
            if len(files) > max_batch:
                logger.warning(f"Limiting analysis to {max_batch} files (found {len(files)})")
                files = files[:max_batch]
            
            return files
            
        except Exception as e:
            logger.error(f"Error getting changed files: {e}")
            return []
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored."""
        path_str = str(path)
        
        # Check against config ignore patterns
        for pattern in self.config.ignored_dirs:
            if pattern in path_str:
                return True
        
        # Check file patterns
        for pattern in self.config.ignored_files:
            if path.name == pattern or path.match(pattern):
                return True
        
        # Check common ignore patterns
        ignore_dirs = {
            '__pycache__', '.git', 'node_modules', 
            '.pytest_cache', '.mypy_cache', 'venv',
            'dist', 'build', '.egg-info'
        }
        
        parts = path.parts
        return any(part in ignore_dirs for part in parts)
    
    def _update_avg_time(self, time_ms: float):
        """Update average run time."""
        current_avg = self.stats['avg_run_time_ms']
        runs = self.stats['runs']
        
        # Weighted average
        self.stats['avg_run_time_ms'] = (
            (current_avg * (runs - 1) + time_ms) / runs
        )
    
    def _severity_to_priority(self, severity: str) -> int:
        """Convert severity to priority score."""
        severity_map = {'critical': 90, 'high': 70, 'medium': 50, 'low': 30}
        return severity_map.get(severity, 40)

    def _calculate_strategic_importance(self, issue) -> str:
        """Calculate strategic importance based on persistence."""
        days = (issue.last_seen - issue.first_seen).days
        if days > 90: return 'critical'
        elif days > 30: return 'high' 
        elif days > 14: return 'medium'
        else: return 'low'
    
    async def run_once(self):
        """Run all agents once (for scheduled execution)."""
        logger.info("Starting Copper Sun Brass analysis run...")
        
        try:
            # Initialize agents if needed
            if not self.agents:
                await self.initialize_agents()
            
            # Run Scout analysis
            observations = await self.run_scout_analysis()
            
            # Pass observations through Strategist for prioritization
            if 'strategist' in self.agents and observations:
                try:
                    logger.info(f"Sending {len(observations)} observations to Strategist")
                    strategist = self.agents['strategist']
                    # Prioritize observations through Strategist
                    prioritized = await asyncio.to_thread(
                        strategist.prioritize_observations,
                        observations
                    )
                    
                    # Update observations with priority scores
                    if prioritized:
                        observations = prioritized
                        logger.info(f"Strategist prioritized {len(observations)} observations")
                    else:
                        logger.warning(f"Strategist returned no prioritized observations")
                except Exception as e:
                    logger.error(f"Strategist orchestration failed: {e}")
            
            # Generate tasks through Planner
            if 'planner' in self.agents and observations:
                try:
                    planner = self.agents['planner']
                    # Convert observations to tasks
                    tasks = await asyncio.to_thread(
                        planner.generate_tasks_from_observations,
                        observations
                    )
                    
                    if tasks:
                        logger.info(f"Planner generated {len(tasks)} tasks")
                        # Store tasks in DCP for future use
                        # TODO: Implement task storage
                except Exception as e:
                    logger.error(f"Planner task generation failed: {e}")
            
            # Store observations
            logger.info(f"About to store {len(observations)} observations")
            stored_count = 0
            for obs in observations:
                try:
                    # Extract observation data
                    obs_type = obs.get('type', 'unknown')
                    obs_data = obs.get('data', obs)  # Use whole obs if no data field
                    priority = obs.get('priority', 50)
                    
                    # Store in database
                    obs_id = self.storage.add_observation(
                        obs_type=obs_type,
                        data={
                            **obs_data,
                            'classification': obs.get('classification', 'unclassified'),
                            'ml_confidence': obs.get('confidence', 0.0)
                        },
                        source_agent='scout',
                        priority=priority
                    )
                    
                    if obs_id:
                        stored_count += 1
                    
                    # Log critical/important findings
                    if obs.get('classification') in ['critical', 'important']:
                        logger.info(
                            f"Found {obs['classification']} issue in "
                            f"{obs.get('file', 'unknown')}: "
                            f"{obs.get('content', obs.get('classification_reason', 'No details'))}"
                        )
                except Exception as e:
                    logger.error(f"Failed to store observation: {e}")
            
            logger.info(f"Stored {stored_count} of {len(observations)} observations")
            
            # Update last run time
            self.storage.update_last_analysis_time()
            
            # Generate output files for Claude Code
            if stored_count > 0:
                try:
                    output_gen = OutputGenerator(self.config, self.storage)
                    outputs = output_gen.generate_all_outputs()
                    logger.info(f"Generated {len(outputs)} output files in {self.config.output_dir}")
                except Exception as e:
                    logger.error(f"Failed to generate output files: {e}")
            
            # Generate summary
            summary = self._generate_summary(observations)
            if summary:
                logger.info(f"Run summary: {summary}")
            
            # Check if training is needed
            await self._check_and_train()
            
        except Exception as e:
            logger.error(f"Run failed: {e}")
            self.stats['errors'] += 1
    
    async def run_continuous(self):
        """Run agents continuously with Watch monitoring."""
        logger.info("Starting continuous Copper Sun Brass monitoring...")
        
        try:
            # Initialize agents
            if not self.agents:
                await self.initialize_agents()
            
            # Start Watch monitoring
            await self.run_watch_monitoring()
            
            # Run Scout periodically
            while not self.shutdown_event.is_set():
                await self.run_once()
                
                # Wait for next run (configurable)
                wait_time = self.config.get('run_interval', 300)  # Default 5 minutes
                await asyncio.sleep(wait_time)
            
        except Exception as e:
            logger.error(f"Continuous run failed: {e}")
        finally:
            await self.shutdown()
    
    async def _check_and_train(self):
        """Check if codebase learning is needed and run if so."""
        # Only check periodically
        now = datetime.now()
        if now - self.last_training_check < self.training_check_interval:
            return
        
        self.last_training_check = now
        
        try:
            # Check and learn from codebase if needed
            result = await self.training_coordinator.check_and_train()
            
            if result:
                self.stats['training_runs'] += 1
                patterns_learned = result.get('phases', {}).get('codebase_analysis', {}).get('patterns_learned', 0)
                logger.info(f"Codebase learning completed: {patterns_learned} patterns learned")
        except Exception as e:
            logger.error(f"Codebase learning check failed: {e}")
    
    def _generate_summary(self, observations: List[Dict[str, Any]]) -> str:
        """Generate run summary for logging."""
        if not observations:
            return ""
        
        # Count by classification
        counts = {'critical': 0, 'important': 0, 'trivial': 0}
        for obs in observations:
            classification = obs.get('classification', 'unknown')
            if classification in counts:
                counts[classification] += 1
        
        # Build summary
        parts = []
        if counts['critical'] > 0:
            parts.append(f"{counts['critical']} critical")
        if counts['important'] > 0:
            parts.append(f"{counts['important']} important")
        if counts['trivial'] > 0:
            parts.append(f"{counts['trivial']} trivial")
        
        return f"Found {', '.join(parts)} observations"
    
    async def shutdown(self):
        """Graceful shutdown."""
        logger.info("Shutting down Copper Sun Brass runner...")
        
        # Signal shutdown
        self.shutdown_event.set()
        
        # Cancel running tasks
        for task in self.running_agents:
            task.cancel()
        
        # Wait for tasks to complete
        if self.running_agents:
            await asyncio.gather(*self.running_agents, return_exceptions=True)
        
        # Shutdown ML pipeline
        await self.ml_pipeline.shutdown()
        
        # Log final stats
        logger.info(f"Final stats: {self.stats}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get runner statistics."""
        stats = self.stats.copy()
        
        # Add component stats
        stats['ml_pipeline'] = self.ml_pipeline.get_stats()
        stats['storage'] = {
            'total_observations': self.storage.get_observation_count()
        }
        
        # Add training stats
        stats['training'] = self.training_coordinator.get_learning_status()
        
        return stats
    
    # 🔧 SYNC INTERFACE METHODS for Main API Integration
    
    def run_scout(self) -> Dict[str, Any]:
        """
        Simple synchronous interface to run Scout analysis.
        
        Returns:
            AgentResult dict with success status and observation data
        """
        import asyncio
        from .core.models import AgentResult
        
        try:
            start_time = datetime.now()
            
            # Run async method in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Initialize if needed
                if not self.agents:
                    loop.run_until_complete(self.initialize_agents())
                
                # Run Scout analysis with DCP storage and output generation
                observations = loop.run_until_complete(self.run_scout_analysis())
                
                duration = (datetime.now() - start_time).total_seconds()
                
                # Create structured result
                result = AgentResult(
                    agent_name='scout',
                    success=True,
                    data={
                        'observations': observations,
                        'summary': {
                            'total_observations': len(observations),
                            'analysis_complete': len(observations) > 0
                        }
                    },
                    duration_seconds=duration,
                    observations_count=len(observations)
                )
                
                return result.to_dict()
                
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Scout analysis failed: {e}")
            return AgentResult(
                agent_name='scout',
                success=False,
                error=str(e),
                duration_seconds=0.0,
                observations_count=0
            ).to_dict()
    
    def run_watch(self) -> Dict[str, Any]:
        """
        Simple synchronous interface to run Watch analysis.
        
        Returns:
            AgentResult dict with success status and change data
        """
        from .core.models import AgentResult
        
        try:
            start_time = datetime.now()
            
            # Get Watch agent
            watch = self.agents.get('watch')
            if not watch:
                logger.warning("Watch agent not initialized")
                return AgentResult(
                    agent_name='watch',
                    success=False,
                    error="Watch agent not initialized"
                ).to_dict()
            
            # Check for changes
            changes = watch.check_changes()
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return AgentResult(
                agent_name='watch',
                success=True,
                data={
                    'changes': changes,
                    'status': 'monitoring',
                    'changes_detected': len(changes) if changes else 0
                },
                duration_seconds=duration,
                observations_count=len(changes) if changes else 0
            ).to_dict()
            
        except Exception as e:
            logger.error(f"Watch analysis failed: {e}")
            return AgentResult(
                agent_name='watch',
                success=False,
                error=str(e)
            ).to_dict()
    
    def run_strategist(self) -> Dict[str, Any]:
        """
        Simple synchronous interface to run Strategist analysis.
        
        Returns:
            AgentResult dict with success status and strategic recommendations
        """
        from .core.models import AgentResult
        
        try:
            start_time = datetime.now()
            
            # Get Strategist agent
            strategist = self.agents.get('strategist')
            if not strategist:
                return AgentResult(
                    agent_name='strategist',
                    success=False,
                    error="Strategist agent not initialized"
                ).to_dict()
            
            # Get recent observations for strategic analysis
            recent_observations = self.storage.get_recent_observations(limit=50)
            
            # Run strategic analysis
            recommendations = strategist.analyze_patterns(recent_observations)
            priorities = strategist.prioritize_observations(recent_observations)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return AgentResult(
                agent_name='strategist',
                success=True,
                data={
                    'recommendations': recommendations or [],
                    'priorities': priorities or [],
                    'observations_analyzed': len(recent_observations)
                },
                duration_seconds=duration,
                observations_count=len(recommendations) if recommendations else 0
            ).to_dict()
            
        except Exception as e:
            logger.error(f"Strategist analysis failed: {e}")
            return AgentResult(
                agent_name='strategist',
                success=False,
                error=str(e)
            ).to_dict()