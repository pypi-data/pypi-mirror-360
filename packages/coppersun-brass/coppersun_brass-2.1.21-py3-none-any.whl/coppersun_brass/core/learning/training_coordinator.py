"""
🚨 LEGACY FILE - NO LONGER USED 🚨

Training Coordinator for Learning System

⚠️ This file is LEGACY and no longer called by any active code paths.
🩸 Pure Python ML engine (pure_python_ml.py) is now used instead.
❌ This file contains heavy dependencies and should not be used.

General Staff G3/G7 Function: Training Operations Coordination
Coordinates the model training pipeline and feedback loop integration
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

from coppersun_brass.core.learning.model_trainer import ModelTrainer
from coppersun_brass.core.learning.pattern_extractor import PatternExtractor
from coppersun_brass.core.learning.task_outcome_collector import OutcomeCollector
from coppersun_brass.core.learning.privacy_manager import PrivacyManager
from coppersun_brass.core.context.dcp_manager import DCPManager
from coppersun_brass.config import BrassConfig
from coppersun_brass.agents.strategist.feedback.feedback_collector import FeedbackCollector
from .dcp_helpers import get_dcp_section, update_dcp_section

logger = logging.getLogger(__name__)


class TrainingCoordinator:
    """
    Coordinates the entire learning pipeline
    
    General Staff G3/G7 Function: Training Operations Coordination
    This component orchestrates feedback collection, pattern extraction,
    and model training to maintain continuous learning across sessions.
    """
    
    def __init__(
        self,
        dcp_path: Optional[str] = None,
        config: Optional[BrassConfig] = None,
        team_id: Optional[str] = None
    ):
        """
        Initialize training coordinator with MANDATORY DCP integration
        
        Args:
            dcp_path: Path to DCP context file (mandatory per CLAUDE.md)
            config: Copper Alloy Brass configuration
            team_id: Team identifier
        """
        # DCP is MANDATORY - this is how the general staff coordinates
        self.dcp_manager = DCPManager(dcp_path)
        self.config = config or BrassConfig()
        self.team_id = team_id
        
        # Initialize components
        self.model_trainer = ModelTrainer(dcp_path, config, team_id)
        self.pattern_extractor = PatternExtractor(dcp_path, team_id)
        self.outcome_collector = OutcomeCollector(dcp_path, config.project_root, team_id)
        self.feedback_collector = FeedbackCollector(dcp_path)
        self.privacy_manager = PrivacyManager(dcp_path, team_id)
        
        # Training configuration
        self.auto_train_threshold = 100  # Min new outcomes before auto-training
        self.training_interval = timedelta(hours=24)
        self.last_training_time = None
        self.is_training = False
        
        # Load state from DCP
        self._load_state_from_dcp()
    
    async def run_training_cycle(self, force: bool = False) -> Dict[str, Any]:
        """
        Run a complete training cycle
        
        Args:
            force: Force training even if conditions aren't met
            
        Returns:
            Training cycle results
        """
        if self.is_training:
            return {
                'success': False,
                'reason': 'Training already in progress'
            }
        
        self.is_training = True
        start_time = datetime.utcnow()
        
        results = {
            'success': True,
            'start_time': start_time.isoformat(),
            'phases': {}
        }
        
        try:
            # Phase 1: Collect and process feedback
            logger.info("Phase 1: Collecting feedback data")
            feedback_results = await self._collect_feedback_data()
            results['phases']['feedback_collection'] = feedback_results
            
            # Phase 2: Extract patterns
            logger.info("Phase 2: Extracting patterns")
            pattern_results = self._extract_patterns()
            results['phases']['pattern_extraction'] = pattern_results
            
            # Phase 3: Check if training is needed
            should_train, train_reason = self._should_train(force)
            results['should_train'] = should_train
            results['train_reason'] = train_reason
            
            if should_train:
                # Phase 4: Train models
                logger.info("Phase 4: Training models")
                training_results = self.model_trainer.train_models(force)
                results['phases']['model_training'] = training_results
                
                if training_results.get('success'):
                    # Phase 5: Update production models
                    logger.info("Phase 5: Updating production models")
                    update_results = self.model_trainer.update_models(backup=True)
                    results['phases']['model_update'] = update_results
                    
                    # Update last training time
                    self.last_training_time = datetime.utcnow()
            
            # Phase 6: Clean up old data
            logger.info("Phase 6: Cleaning up old data")
            cleanup_results = self._cleanup_old_data()
            results['phases']['cleanup'] = cleanup_results
            
            # Calculate total time
            end_time = datetime.utcnow()
            results['end_time'] = end_time.isoformat()
            results['duration_seconds'] = (end_time - start_time).total_seconds()
            
            # Persist state to DCP
            self._persist_state_to_dcp(results)
            
            logger.info(f"Training cycle completed in {results['duration_seconds']:.1f} seconds")
            
        except Exception as e:
            logger.error(f"Training cycle failed: {e}")
            results['success'] = False
            results['error'] = str(e)
            
        finally:
            self.is_training = False
        
        return results
    
    async def _collect_feedback_data(self) -> Dict[str, Any]:
        """Collect and process feedback data"""
        results = {
            'feedback_summary': {},
            'new_feedback_count': 0
        }
        
        # Get feedback summary
        feedback_summary = self.feedback_collector.get_feedback_summary(days=30)
        results['feedback_summary'] = feedback_summary
        
        # Process feedback into outcomes
        if 'total_feedback' in feedback_summary:
            results['new_feedback_count'] = feedback_summary['total_feedback']
        
        # Update outcome summary in DCP
        self.outcome_collector.update_outcome_summary_in_dcp()
        
        return results
    
    def _extract_patterns(self) -> Dict[str, Any]:
        """Extract patterns from recent data"""
        patterns = self.pattern_extractor.extract_patterns(
            min_samples=5,
            lookback_days=90
        )
        
        return {
            'patterns_extracted': len(patterns),
            'pattern_types': list(set(p.pattern_type for p in patterns)),
            'high_confidence_patterns': len([p for p in patterns if p.confidence >= 0.8])
        }
    
    def _should_train(self, force: bool) -> tuple[bool, str]:
        """Determine if training should occur"""
        if force:
            return True, "Forced training"
        
        # Check if enough time has passed
        if self.last_training_time:
            time_since_training = datetime.utcnow() - self.last_training_time
            if time_since_training < self.training_interval:
                return False, f"Too soon since last training ({time_since_training.total_seconds() / 3600:.1f} hours ago)"
        
        # Check if we have enough new data
        ready, stats = self.model_trainer.check_training_readiness()
        
        if not ready:
            return False, f"Insufficient data: {stats['feedback_outcomes']} feedback outcomes (need {self.model_trainer.min_samples_for_training})"
        
        # Check if we have new outcomes since last training
        if self.last_training_time:
            # This is a simplified check - in production you'd query the database
            return True, f"Ready to train with {stats['feedback_outcomes']} feedback outcomes"
        
        return True, "Initial training needed"
    
    def _cleanup_old_data(self) -> Dict[str, Any]:
        """Clean up old data based on privacy settings"""
        results = {
            'privacy_purge': {},
            'feedback_pruned': 0
        }
        
        # Purge expired data
        purge_results = self.privacy_manager.purge_expired_data(dry_run=False)
        results['privacy_purge'] = purge_results
        
        # Prune old feedback
        feedback_pruned = self.feedback_collector.prune_old_feedback(days_to_keep=90)
        results['feedback_pruned'] = feedback_pruned
        
        return results
    
    def schedule_automatic_training(self) -> Dict[str, Any]:
        """
        Set up automatic training schedule
        
        Returns:
            Schedule information
        """
        schedule_info = {
            'enabled': True,
            'interval_hours': self.training_interval.total_seconds() / 3600,
            'auto_train_threshold': self.auto_train_threshold,
            'next_check': (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        # Update DCP
        self.dcp_manager.update_section('learning.automatic_training', schedule_info)
        
        logger.info(f"Automatic training scheduled every {schedule_info['interval_hours']} hours")
        return schedule_info
    
    async def check_and_train(self) -> Optional[Dict[str, Any]]:
        """
        Check if training is needed and run if so
        
        Returns:
            Training results if training occurred, None otherwise
        """
        should_train, reason = self._should_train(force=False)
        
        if should_train:
            logger.info(f"Starting automatic training: {reason}")
            return await self.run_training_cycle()
        
        logger.debug(f"Skipping training: {reason}")
        return None
    
    def get_training_status(self) -> Dict[str, Any]:
        """Get current training system status"""
        ready, stats = self.model_trainer.check_training_readiness()
        
        status = {
            'is_training': self.is_training,
            'last_training_time': self.last_training_time.isoformat() if self.last_training_time else None,
            'training_readiness': stats,
            'ready_to_train': ready,
            'automatic_training_enabled': True,
            'next_training_check': (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        # Add model information
        model_metadata_path = self.config.model_dir / 'model_metadata.json'
        if model_metadata_path.exists():
            with open(model_metadata_path, 'r') as f:
                model_metadata = json.load(f)
                status['current_models'] = model_metadata.get('model_files', {})
                status['last_model_update'] = model_metadata.get('last_update', {})
        
        return status
    
    def trigger_manual_training(self) -> Dict[str, Any]:
        """
        Trigger manual training (synchronous wrapper for async method)
        
        Returns:
            Training initiation status
        """
        if self.is_training:
            return {
                'success': False,
                'reason': 'Training already in progress'
            }
        
        # Create event loop if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run training in background
        task = loop.create_task(self.run_training_cycle(force=True))
        
        return {
            'success': True,
            'message': 'Training initiated',
            'task_id': id(task),
            'check_status_with': 'get_training_status'
        }
    
    def _load_state_from_dcp(self) -> None:
        """Load coordinator state from DCP"""
        try:
            learning_data = get_dcp_section(self.dcp_manager, 'learning', {})
            coordinator_state = learning_data.get('coordinator', {})
            
            if coordinator_state.get('last_training_time'):
                self.last_training_time = datetime.fromisoformat(
                    coordinator_state['last_training_time']
                )
            
            if coordinator_state.get('training_interval_hours'):
                self.training_interval = timedelta(
                    hours=coordinator_state['training_interval_hours']
                )
            
            logger.info(f"Loaded coordinator state from DCP")
        except Exception as e:
            logger.warning(f"Could not load coordinator state from DCP: {e}")
    
    def _persist_state_to_dcp(self, last_results: Dict[str, Any]) -> None:
        """Persist coordinator state to DCP"""
        state = {
            'last_training_time': self.last_training_time.isoformat() if self.last_training_time else None,
            'training_interval_hours': self.training_interval.total_seconds() / 3600,
            'auto_train_threshold': self.auto_train_threshold,
            'last_training_results': last_results,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Update DCP
        self.dcp_manager.update_section('learning.coordinator', state)
        
        # Add observation for significant events
        if last_results.get('success'):
            self.dcp_manager.add_observation(
                'training_cycle_completed',
                {
                    'duration_seconds': last_results.get('duration_seconds', 0),
                    'phases_completed': list(last_results.get('phases', {}).keys()),
                    'models_trained': last_results.get('phases', {}).get('model_training', {}).get('models_trained', []),
                    'patterns_extracted': last_results.get('phases', {}).get('pattern_extraction', {}).get('patterns_extracted', 0)
                },
                source_agent='training_coordinator',
                priority=90  # High priority for training completion
            )
        
        logger.info("Persisted coordinator state to DCP")


# Export main class
__all__ = ['TrainingCoordinator']