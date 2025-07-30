"""
Copper Sun Brass main API class

Provides programmatic access to all Copper Sun Brass functionality.
This is the primary integration point for external tools and scripts.
"""
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Union

from ..config import BrassConfig
from .storage import BrassStorage
from .dcp_adapter import DCPAdapter

logger = logging.getLogger(__name__)


class Brass:
    """Main Copper Sun Brass API class
    
    This class provides programmatic access to all Copper Sun Brass functionality,
    including file analysis, project insights, and monitoring capabilities.
    
    Example:
        >>> from coppersun_brass.core.brass import Brass
        >>> brass = Brass("/path/to/project")
        >>> analysis = brass.analyze_project()
        >>> insights = brass.get_insights()
    """
    
    def __init__(self, project_path: Optional[Union[str, Path]] = None, config: Optional[BrassConfig] = None):
        """
        Initialize Copper Sun Brass
        
        Args:
            project_path: Path to project to analyze (defaults to current directory)
            config: Optional configuration object
        """
        self.project_path = Path(project_path or ".").resolve()
        self.config = config or BrassConfig(self.project_path)
        
        # Initialize storage - use CopperSun's storage system
        storage_path = self.project_path / ".brass" / "coppersun_brass.db"
        self.storage = BrassStorage(storage_path)
        
        # Initialize DCP adapter - connect to CopperSun's DCP system
        self.dcp = DCPAdapter(self.storage, self.project_path)
        
        # Lazy load agents and systems
        self._scout = None
        self._watch = None
        self._strategist = None
        self._planner = None
        self._runner = None
        self._ml_pipeline = None
        
        logger.info(f"Initialized Copper Sun Brass API for project: {self.project_path}")
    
    def analyze_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Analyze a single file for security issues, TODOs, and patterns
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            Analysis results including findings, patterns, and metadata
        """
        file_path = Path(file_path)
        logger.info(f"Analyzing file: {file_path}")
        
        try:
            # Lazy load Scout agent using CopperSun's implementation
            if self._scout is None:
                from ..agents.scout.scout_agent import ScoutAgent
                self._scout = ScoutAgent(
                    dcp_path=str(self.project_path / ".brass"),
                    project_root=self.project_path
                )
            
            # Run Scout analysis
            result = self._scout.analyze(str(file_path))
            
            if result and hasattr(result, 'todo_findings'):
                return {
                    'success': True,
                    'file': str(file_path),
                    'findings': {
                        'todos': [
                            {
                                'line': finding.line_number,
                                'content': finding.content,
                                'type': finding.type,
                                'priority': getattr(finding, 'priority', 'medium')
                            }
                            for finding in result.data.get('todo_findings', [])
                        ],
                        'patterns': result.data.get('pattern_findings', []),
                        'security_issues': result.data.get('security_issues', [])
                    },
                    'metadata': {
                        'file_size': file_path.stat().st_size if file_path.exists() else 0,
                        'analysis_time': result.data.get('analysis_time', 0),
                        'ml_enabled': result.data.get('ml_enabled', False)
                    },
                    'metrics': result.data.get('metrics', {})
                }
            else:
                error_msg = result.error if result else "Analysis failed"
                logger.warning(f"File analysis failed for {file_path}: {error_msg}")
                return {
                    'success': False,
                    'file': str(file_path),
                    'error': error_msg,
                    'findings': {'todos': [], 'patterns': [], 'security_issues': []},
                    'metadata': {},
                    'metrics': {}
                }
                
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return {
                'success': False,
                'file': str(file_path),
                'error': str(e),
                'findings': {'todos': [], 'patterns': [], 'security_issues': []},
                'metadata': {},
                'metrics': {}
            }
    
    def analyze_project(self) -> Dict[str, Any]:
        """
        Analyze entire project using all available agents
        
        Returns:
            Comprehensive project analysis results
        """
        logger.info(f"Starting project analysis for: {self.project_path}")
        
        try:
            # Lazy load the BrassRunner for full project analysis
            if self._runner is None:
                from ..runner import BrassRunner
                self._runner = BrassRunner(self.project_path)
            
            # Run comprehensive analysis using all agents
            results = {
                'success': True,
                'project': str(self.project_path),
                'agents': {},
                'summary': {},
                'recommendations': []
            }
            
            # Run Scout analysis
            logger.info("Running Scout analysis...")
            scout_result = self._runner.run_scout()
            if scout_result.success:
                results['agents']['scout'] = {
                    'success': True,
                    'observations': len(scout_result.data.get('observations', [])),
                    'findings': scout_result.data.get('summary', {})
                }
            else:
                results['agents']['scout'] = {
                    'success': False,
                    'error': scout_result.error
                }
            
            # Run Watch analysis
            logger.info("Running Watch analysis...")
            watch_result = self._runner.run_watch()
            if watch_result.success:
                results['agents']['watch'] = {
                    'success': True,
                    'changes_detected': len(watch_result.data.get('changes', [])),
                    'status': watch_result.data.get('status', 'unknown')
                }
            else:
                results['agents']['watch'] = {
                    'success': False,
                    'error': watch_result.error
                }
            
            # Run Strategist analysis
            logger.info("Running Strategist analysis...")
            strategist_result = self._runner.run_strategist()
            if strategist_result.success:
                results['agents']['strategist'] = {
                    'success': True,
                    'recommendations': strategist_result.data.get('recommendations', []),
                    'priorities': strategist_result.data.get('priorities', [])
                }
                # Add strategist recommendations to main recommendations
                results['recommendations'].extend(strategist_result.data.get('recommendations', []))
            else:
                results['agents']['strategist'] = {
                    'success': False,
                    'error': strategist_result.error
                }
            
            # Generate summary
            total_observations = sum(
                agent.get('observations', 0) 
                for agent in results['agents'].values() 
                if agent.get('success', False)
            )
            
            results['summary'] = {
                'total_observations': total_observations,
                'successful_agents': sum(1 for agent in results['agents'].values() if agent.get('success', False)),
                'total_agents': len(results['agents']),
                'analysis_complete': total_observations > 0
            }
            
            logger.info(f"Project analysis complete: {total_observations} observations generated")
            return results
            
        except Exception as e:
            logger.error(f"Error during project analysis: {e}")
            return {
                'success': False,
                'project': str(self.project_path),
                'error': str(e),
                'agents': {},
                'summary': {},
                'recommendations': []
            }
    
    def get_insights(self) -> List[Dict[str, Any]]:
        """
        Get AI-powered insights for the project based on recent observations
        
        Returns:
            List of insights with priorities and recommendations
        """
        logger.info("Generating insights from stored observations...")
        
        try:
            # Get recent observations from storage
            observations = self.storage.get_observations(limit=100)
            
            insights = []
            
            # Process observations into insights
            for obs in observations:
                obs_data = obs if isinstance(obs, dict) else obs.__dict__
                
                priority = obs_data.get('priority', 50)
                if priority > 70:  # High priority items
                    insight = {
                        'type': obs_data.get('type', 'unknown'),
                        'summary': obs_data.get('summary', 'No summary available'),
                        'priority': priority,
                        'category': obs_data.get('category', 'general'),
                        'recommendation': self._generate_recommendation(obs_data),
                        'timestamp': obs_data.get('timestamp'),
                        'source_file': obs_data.get('file_path')
                    }
                    insights.append(insight)
            
            # Sort by priority (highest first)
            insights.sort(key=lambda x: x['priority'], reverse=True)
            
            logger.info(f"Generated {len(insights)} insights from {len(observations)} observations")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return []
    
    def start_monitoring(self) -> bool:
        """
        Start real-time file monitoring and automatic analysis using subprocess
        
        This prevents brass init from hanging by running monitoring in a separate process.
        
        Returns:
            True if monitoring started successfully
        """
        logger.info("Starting automatic monitoring...")
        
        try:
            # Use BackgroundProcessManager to prevent hanging
            from ..cli.background_process_manager import BackgroundProcessManager
            from pathlib import Path
            
            logger.info("Creating background process manager...")
            # Create background process manager
            process_manager = BackgroundProcessManager(Path(self.project_path))
            logger.info("BackgroundProcessManager created successfully!")
            
            logger.info("Calling start_background_process...")
            # Start background monitoring process (non-blocking)
            success, message = process_manager.start_background_process()
            
            logger.info(f"Background process manager returned: success={success}, message={message}")
            
            if success:
                logger.info(f"Automatic monitoring started successfully: {message}")
                return True
            else:
                logger.error(f"Failed to start monitoring: {message}")
                
                # Fallback: Try the old blocking method if subprocess fails
                logger.info("Attempting fallback to direct scheduler start...")
                return self._start_monitoring_fallback()
            
        except ImportError as e:
            logger.error(f"Import error in start_monitoring: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Try fallback method
            logger.info("Attempting fallback to direct scheduler start...")
            return self._start_monitoring_fallback()
        except Exception as e:
            logger.error(f"Exception in start_monitoring: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Try fallback method
            logger.info("Attempting fallback to direct scheduler start...")
            return self._start_monitoring_fallback()
    
    def _start_monitoring_fallback(self) -> bool:
        """
        Fallback method using direct scheduler start (blocking)
        
        This is the original implementation kept as emergency fallback.
        """
        try:
            # Use CopperSun's AdaptiveScheduler for background monitoring
            from ..scheduler import AdaptiveScheduler
            from ..config import BrassConfig
            
            config = BrassConfig(self.project_path)
            scheduler = AdaptiveScheduler(config)
            
            # Start the scheduler (handle async/sync properly)
            import asyncio
            if asyncio.iscoroutinefunction(scheduler.start):
                # Use asyncio.run() for cleaner async handling (Python 3.7+)
                try:
                    asyncio.run(scheduler.start())
                except RuntimeError as e:
                    if "cannot be called from a running event loop" in str(e):
                        # Fallback for nested event loop contexts
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            loop.run_until_complete(scheduler.start())
                        finally:
                            loop.close()
                    else:
                        raise
            else:
                # Call sync method directly
                scheduler.start()
            
            logger.info("Fallback monitoring started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start fallback monitoring: {e}")
            return False
    
    def stop_monitoring(self) -> bool:
        """
        Stop real-time file monitoring
        
        Returns:
            True if monitoring stopped successfully  
        """
        logger.info("Stopping automatic monitoring...")
        
        try:
            # Use BackgroundProcessManager to stop monitoring
            from ..cli.background_process_manager import BackgroundProcessManager
            from pathlib import Path
            
            # Create background process manager
            process_manager = BackgroundProcessManager(Path(self.project_path))
            
            # Stop background monitoring process
            success, message = process_manager.stop_background_process()
            
            if success:
                logger.info(f"Monitoring stopped successfully: {message}")
                return True
            else:
                logger.error(f"Failed to stop monitoring: {message}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {e}")
            return False
    
    def is_monitoring_running(self) -> bool:
        """
        Check if background monitoring is currently running
        
        Returns:
            True if monitoring is active
        """
        try:
            from ..cli.background_process_manager import BackgroundProcessManager
            from pathlib import Path
            
            process_manager = BackgroundProcessManager(Path(self.project_path))
            return process_manager.is_background_running()
            
        except Exception as e:
            logger.error(f"Failed to check monitoring status: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current system status and health information
        
        Returns:
            System status including agents, storage, and configuration
        """
        try:
            # Check .brass directory exists
            brass_dir = self.project_path / ".brass"
            brass_exists = brass_dir.exists()
            
            # Check agent health if available
            agent_health = {}
            health_file = brass_dir / "agent_health.json"
            if health_file.exists():
                import json
                with open(health_file, 'r') as f:
                    health_data = json.load(f)
                    agent_health = health_data.get('agents', {})
            
            # Check storage status
            storage_status = {
                'database_exists': self.storage.db_path.exists() if hasattr(self.storage, 'db_path') else False,
                'recent_observations': len(self.storage.get_observations(limit=10))
            }
            
            # Check ML models
            ml_status = {}
            models_dir = brass_dir / "models"
            if models_dir.exists():
                ml_status = {
                    'models_directory_exists': True,
                    'onnx_model_exists': (models_dir / "codebert_small_quantized.onnx").exists(),
                    'tokenizer_exists': (models_dir / "code_tokenizer.json").exists(),
                    'patterns_exist': (models_dir / "critical_patterns.json").exists()
                }
            else:
                ml_status = {'models_directory_exists': False}
            
            return {
                'success': True,
                'project_path': str(self.project_path),
                'brass_initialized': brass_exists,
                'agent_health': agent_health,
                'storage_status': storage_status,
                'ml_status': ml_status,
                'config': {
                    'data_dir': str(self.config.data_dir),
                    'monitoring_enabled': getattr(self.config, 'monitoring_enabled', False)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                'success': False,
                'error': str(e),
                'project_path': str(self.project_path)
            }
    
    def generate_files(self) -> Dict[str, Any]:
        """
        Generate .brass intelligence files from stored observations
        
        Returns:
            Result indicating success and files generated
        """
        try:
            from ..core.output_generator import OutputGenerator
            
            logger.info("Generating .brass intelligence files...")
            
            # Create output generator
            output_generator = OutputGenerator(
                config=self.config,
                storage=self.storage
            )
            
            # Generate all files
            outputs = output_generator.generate_all_outputs()
            
            # Return the actual files created
            files_created = [Path(path).name for path in outputs.values()]
            
            return {
                'success': True,
                'files_generated': files_created,
                'output_directory': str(self.config.output_dir),
                'file_paths': {name: str(path) for name, path in outputs.items()}
            }
            
        except Exception as e:
            logger.error(f"Failed to generate files: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_recommendation(self, observation: Dict[str, Any]) -> str:
        """Generate a recommendation based on observation data"""
        obs_type = observation.get('type', '').lower()
        priority = observation.get('priority', 50)
        
        if 'security' in obs_type or priority > 90:
            return "URGENT: Address this security issue immediately"
        elif 'todo' in obs_type or 'fixme' in obs_type:
            return "Consider addressing this TODO item in the next development cycle"
        elif priority > 80:
            return "High priority: Schedule for resolution soon"
        elif priority > 60:
            return "Medium priority: Include in upcoming planning"
        else:
            return "Low priority: Address when convenient"