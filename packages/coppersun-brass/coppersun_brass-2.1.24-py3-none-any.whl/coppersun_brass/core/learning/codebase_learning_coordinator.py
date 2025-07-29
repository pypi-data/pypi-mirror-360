"""
Codebase Learning Coordinator - Replacement for TrainingCoordinator
==================================================================

🩸 BLOOD OATH COMPLIANT: Uses only Python built-ins for codebase learning
✅ Replaces LEGACY TrainingCoordinator with codebase learning functionality
✅ Maintains same interface for seamless integration with BrassRunner
✅ Restores user codebase learning without heavy ML dependencies

This coordinator manages automatic codebase learning and pattern extraction.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

from coppersun_brass.core.learning.codebase_learning_engine import CodebaseLearningEngine
from coppersun_brass.core.dcp_adapter import DCPAdapter
from coppersun_brass.config import BrassConfig

logger = logging.getLogger(__name__)

class CodebaseLearningCoordinator:
    """
    Coordinates codebase learning operations.
    
    🩸 BLOOD OATH: Uses only Python built-ins for learning
    ✅ Drop-in replacement for TrainingCoordinator
    ✅ Maintains compatible interface for BrassRunner
    ✅ Provides adaptive intelligence through codebase analysis
    """
    
    def __init__(
        self,
        dcp_adapter: Optional[DCPAdapter] = None,
        dcp_path: Optional[str] = None,
        config: Optional[BrassConfig] = None,
        team_id: Optional[str] = None
    ):
        """
        Initialize codebase learning coordinator.
        
        Args:
            dcp_adapter: DCP adapter instance (preferred)
            dcp_path: Path to DCP context file (fallback)
            config: Copper Sun Brass configuration
            team_id: Team identifier
        """
        # Use provided DCP adapter or create from path
        if dcp_adapter:
            self.dcp_manager = dcp_adapter
        else:
            # Fallback: create DCPAdapter from path
            from coppersun_brass.core.storage import BrassStorage
            if not dcp_path:
                raise ValueError("Either dcp_adapter or dcp_path must be provided")
            
            # Create storage and adapter
            storage = BrassStorage(Path(dcp_path) / "coppersun_brass.db")
            self.dcp_manager = DCPAdapter(storage, dcp_path)
        self.config = config or BrassConfig()
        self.team_id = team_id
        
        # Determine project path
        self.project_path = None
        if dcp_path:
            brass_dir = Path(dcp_path).parent if Path(dcp_path).is_file() else Path(dcp_path)
            self.project_path = brass_dir.parent
        elif config and config.project_root:
            self.project_path = config.project_root
        
        # Initialize codebase learning engine
        learning_storage_path = None
        if dcp_path:
            learning_storage_path = Path(dcp_path).parent / "learning_data.db"
        
        self.learning_engine = CodebaseLearningEngine(learning_storage_path)
        
        # Learning configuration
        self.auto_learning_threshold = timedelta(hours=6)  # Re-analyze every 6 hours
        self.learning_interval = timedelta(hours=24)       # Full analysis daily
        self.last_learning_time = None
        self.last_quick_scan_time = None
        self.is_learning = False
        
        # Load state from DCP
        self._load_state_from_dcp()
        
        logger.info("✅ Codebase Learning Coordinator initialized")
    
    async def check_and_train(self) -> Optional[Dict[str, Any]]:
        """
        Check if codebase learning is needed and run if so.
        
        This method maintains compatibility with TrainingCoordinator interface.
        
        Returns:
            Learning results if learning occurred, None otherwise
        """
        should_learn, reason = self._should_run_learning(force=False)
        
        if should_learn:
            logger.info(f"Starting automatic codebase learning: {reason}")
            return await self.run_learning_cycle()
        
        logger.debug(f"Skipping codebase learning: {reason}")
        return None
    
    async def run_learning_cycle(self, force: bool = False) -> Dict[str, Any]:
        """
        Run a complete codebase learning cycle.
        
        Args:
            force: Force learning even if conditions aren't met
            
        Returns:
            Learning cycle results
        """
        if self.is_learning:
            return {
                'success': False,
                'reason': 'Learning already in progress'
            }
        
        self.is_learning = True
        start_time = datetime.utcnow()
        
        results = {
            'success': True,
            'start_time': start_time.isoformat(),
            'phases': {}
        }
        
        try:
            # Phase 1: Check if project path is available
            if not self.project_path or not self.project_path.exists():
                return {
                    'success': False,
                    'reason': 'No valid project path for codebase learning'
                }
            
            logger.info("Phase 1: Analyzing codebase patterns")
            
            # Phase 2: Run codebase analysis
            learning_start = datetime.now()
            try:
                project_context = self.learning_engine.analyze_codebase(self.project_path)
                
                learning_results = {
                    'success': True,
                    'project_type': project_context.project_type,
                    'primary_language': project_context.primary_language,
                    'total_files': project_context.total_files,
                    'patterns_learned': len(self.learning_engine.patterns),
                    'complexity_level': project_context.complexity_level,
                    'learning_duration': (datetime.now() - learning_start).total_seconds()
                }
                
                results['phases']['codebase_analysis'] = learning_results
                
            except Exception as e:
                logger.error(f"Codebase analysis failed: {e}")
                results['phases']['codebase_analysis'] = {
                    'success': False,
                    'error': str(e)
                }
            
            # Phase 3: Update DCP with learning insights
            logger.info("Phase 3: Updating DCP with learning insights")
            
            try:
                self._update_dcp_with_insights()
                results['phases']['dcp_update'] = {'success': True}
            except Exception as e:
                logger.error(f"DCP update failed: {e}")
                results['phases']['dcp_update'] = {
                    'success': False,
                    'error': str(e)
                }
            
            # Phase 4: Store learning state
            logger.info("Phase 4: Persisting learning state")
            
            try:
                self.last_learning_time = datetime.utcnow()
                self._persist_state_to_dcp(results)
                results['phases']['state_persistence'] = {'success': True}
            except Exception as e:
                logger.error(f"State persistence failed: {e}")
                results['phases']['state_persistence'] = {
                    'success': False,
                    'error': str(e)
                }
            
            # Calculate total time
            end_time = datetime.utcnow()
            results['end_time'] = end_time.isoformat()
            results['duration_seconds'] = (end_time - start_time).total_seconds()
            
            logger.info(f"Codebase learning cycle completed in {results['duration_seconds']:.1f} seconds")
            
        except Exception as e:
            logger.error(f"Learning cycle failed: {e}")
            results['success'] = False
            results['error'] = str(e)
            
        finally:
            self.is_learning = False
        
        return results
    
    def _should_run_learning(self, force: bool) -> tuple[bool, str]:
        """Determine if codebase learning should occur."""
        if force:
            return True, "Forced learning"
        
        # Check if enough time has passed since last learning
        if self.last_learning_time:
            time_since_learning = datetime.utcnow() - self.last_learning_time
            if time_since_learning < self.learning_interval:
                return False, f"Too soon since last learning ({time_since_learning.total_seconds() / 3600:.1f} hours ago)"
        
        # Check if project path is available
        if not self.project_path or not self.project_path.exists():
            return False, "No valid project path available"
        
        # Check for code changes (simple heuristic)
        if self._has_code_changes():
            return True, "Code changes detected in project"
        
        # If we've never learned, do it now
        if not self.last_learning_time:
            return True, "Initial codebase learning needed"
        
        return False, "No learning needed at this time"
    
    def _has_code_changes(self) -> bool:
        """Check if there have been code changes since last learning (simple heuristic)."""
        if not self.project_path or not self.last_learning_time:
            return True
        
        try:
            # Check for recent file modifications
            recent_threshold = self.last_learning_time.timestamp()
            
            code_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.rs', '.go', '.java'}
            recent_changes = 0
            
            for file_path in self.project_path.rglob('*'):
                if (file_path.is_file() and 
                    file_path.suffix.lower() in code_extensions and
                    file_path.stat().st_mtime > recent_threshold):
                    recent_changes += 1
                    
                    # If we find several recent changes, learning is worth it
                    if recent_changes >= 3:
                        return True
            
            return recent_changes > 0
            
        except Exception as e:
            logger.warning(f"Could not check for code changes: {e}")
            return True  # Err on the side of learning
    
    def _update_dcp_with_insights(self):
        """Update DCP with codebase learning insights."""
        if not self.learning_engine.patterns:
            return
        
        # Summarize learning insights for DCP
        high_impact_patterns = [
            p for p in self.learning_engine.patterns.values()
            if abs(p.confidence_multiplier - 1.0) > 0.3
        ]
        
        insights_summary = {
            'patterns_learned': len(self.learning_engine.patterns),
            'high_impact_patterns': len(high_impact_patterns),
            'project_context': {
                'type': self.learning_engine.project_context.project_type if self.learning_engine.project_context else 'unknown',
                'language': self.learning_engine.project_context.primary_language if self.learning_engine.project_context else 'unknown',
                'complexity': self.learning_engine.project_context.complexity_level if self.learning_engine.project_context else 'unknown'
            },
            'learning_effectiveness': {
                'confidence_boosts': len([p for p in self.learning_engine.patterns.values() if p.confidence_multiplier > 1.2]),
                'confidence_reductions': len([p for p in self.learning_engine.patterns.values() if p.confidence_multiplier < 0.8])
            },
            'last_updated': datetime.utcnow().isoformat()
        }
        
        # Update DCP section
        self.dcp_manager.update_section('learning.codebase_insights', insights_summary)
        
        # Add observation for significant learning event
        self.dcp_manager.add_observation(
            'codebase_learning_completed',
            {
                'patterns_learned': len(self.learning_engine.patterns),
                'high_impact_count': len(high_impact_patterns),
                'project_type': insights_summary['project_context']['type'],
                'learning_duration': 'completed',
                'team_id': self.team_id
            },
            source_agent='codebase_learning_coordinator',
            priority=85  # High priority for learning events
        )
        
        logger.info("Updated DCP with codebase learning insights")
    
    def _load_state_from_dcp(self):
        """Load coordinator state from DCP."""
        try:
            learning_data = self.dcp_manager.get_section('learning.codebase_coordinator', {})
            
            if learning_data.get('last_learning_time'):
                self.last_learning_time = datetime.fromisoformat(
                    learning_data['last_learning_time']
                )
            
            if learning_data.get('learning_interval_hours'):
                self.learning_interval = timedelta(
                    hours=learning_data['learning_interval_hours']
                )
            
            logger.info("Loaded codebase learning coordinator state from DCP")
        except Exception as e:
            logger.warning(f"Could not load coordinator state from DCP: {e}")
    
    def _persist_state_to_dcp(self, last_results: Dict[str, Any]):
        """Persist coordinator state to DCP."""
        state = {
            'last_learning_time': self.last_learning_time.isoformat() if self.last_learning_time else None,
            'learning_interval_hours': self.learning_interval.total_seconds() / 3600,
            'project_path': str(self.project_path) if self.project_path else None,
            'last_learning_results': last_results,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Update DCP
        self.dcp_manager.update_section('learning.codebase_coordinator', state)
        
        logger.info("Persisted codebase learning coordinator state to DCP")
    
    def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning system status."""
        return {
            'is_learning': self.is_learning,
            'last_learning_time': self.last_learning_time.isoformat() if self.last_learning_time else None,
            'learning_readiness': {
                'project_path_available': self.project_path is not None and self.project_path.exists(),
                'patterns_learned': len(self.learning_engine.patterns),
                'ready_to_learn': self._should_run_learning(force=False)[0]
            },
            'codebase_learning_enabled': True,
            'next_learning_check': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'learning_engine_status': self.learning_engine.get_learning_status(),
            'project_info': {
                'path': str(self.project_path) if self.project_path else None,
                'type': self.learning_engine.project_context.project_type if self.learning_engine.project_context else 'unknown'
            }
        }
    
    def trigger_manual_learning(self) -> Dict[str, Any]:
        """
        Trigger manual codebase learning (synchronous wrapper for async method).
        
        Returns:
            Learning initiation status
        """
        if self.is_learning:
            return {
                'success': False,
                'reason': 'Learning already in progress'
            }
        
        # Create event loop if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run learning in background
        task = loop.create_task(self.run_learning_cycle(force=True))
        
        return {
            'success': True,
            'message': 'Codebase learning initiated',
            'task_id': id(task),
            'check_status_with': 'get_learning_status'
        }
    
    def get_confidence_adjustment(self, pattern_type: str, pattern_subtype: str) -> float:
        """
        Get confidence adjustment for a pattern type.
        
        This method provides the interface for other components to get
        codebase learning adjustments.
        """
        return self.learning_engine.get_confidence_adjustment(pattern_type, pattern_subtype)
    
    def enhance_analysis_results(self, analysis_results: List[Any]) -> List[Any]:
        """
        Enhance analysis results with codebase learning.
        
        This method provides the interface for other components to enhance
        their analysis with codebase learning insights.
        """
        return self.learning_engine.enhance_ml_analysis(analysis_results, self.project_path)


# Export main class for backward compatibility
__all__ = ['CodebaseLearningCoordinator']


# Demo and testing
if __name__ == "__main__":
    import json
    import tempfile
    
    print("🎺 Testing Codebase Learning Coordinator")
    print("=" * 50)
    
    # Create test project
    with tempfile.TemporaryDirectory() as temp_dir:
        test_project = Path(temp_dir) / "test_coordinator"
        test_project.mkdir()
        brass_dir = test_project / ".brass"
        brass_dir.mkdir()
        
        # Create test files
        (test_project / "main.py").write_text("""
# TODO: CRITICAL - Fix authentication vulnerability
def login(username, password):
    # HACK: Temporary bypass - URGENT security issue
    return True

# FIXME: Performance bottleneck in data processing
def process_data():
    # NOTE: This could be optimized
    return expensive_operation()
        """)
        
        # Initialize coordinator
        coordinator = CodebaseLearningCoordinator(
            dcp_path=str(brass_dir),
            config=None,  # Will use defaults
            team_id="test_team"
        )
        
        print(f"✅ Coordinator initialized")
        print(f"   Project path: {coordinator.project_path}")
        
        # Test learning cycle
        print("\n🔍 Running learning cycle...")
        
        async def test_learning():
            results = await coordinator.run_learning_cycle(force=True)
            return results
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(test_learning())
        
        print(f"📊 Learning Results:")
        print(f"   Success: {results['success']}")
        print(f"   Duration: {results.get('duration_seconds', 0):.1f}s")
        print(f"   Phases: {list(results.get('phases', {}).keys())}")
        
        # Test status
        print("\n⚙️  Learning Status:")
        status = coordinator.get_learning_status()
        print(f"   Patterns learned: {status['learning_readiness']['patterns_learned']}")
        print(f"   Ready to learn: {status['learning_readiness']['ready_to_learn']}")
        print(f"   Project type: {status['project_info']['type']}")
        
        # Test check_and_train interface
        print("\n🎯 Testing check_and_train interface...")
        train_result = loop.run_until_complete(coordinator.check_and_train())
        if train_result:
            print(f"   Training occurred: {train_result['success']}")
        else:
            print(f"   No training needed")
        
        print("\n✅ Codebase Learning Coordinator test completed!")
        print("🩸 Blood Oath Status: COMPLIANT - Zero heavy dependencies!")
        
        loop.close()