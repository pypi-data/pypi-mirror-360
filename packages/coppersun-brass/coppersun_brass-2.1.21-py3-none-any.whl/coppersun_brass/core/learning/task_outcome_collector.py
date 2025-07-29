"""
Task Outcome Collector

General Staff Civil Affairs Function: Feedback Collection
Collects task execution outcomes for learning system
"""

import uuid
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from pathlib import Path
import logging

from coppersun_brass.core.learning.models import (
    TaskOutcome, TaskStatus, ExperimentVariant, init_db
)
from coppersun_brass.core.learning.privacy_manager import PrivacyManager
from coppersun_brass.core.context.dcp_manager import DCPManager

logger = logging.getLogger(__name__)

class OutcomeCollector:
    """
    Collects and stores task execution outcomes
    
    General Staff Civil Affairs Function: Feedback Collection
    This component collects task execution outcomes for learning system,
    maintaining all outcomes in DCP for cross-session analysis.
    """
    
    def __init__(self, dcp_path: Optional[str] = None, project_root: Optional[Path] = None, team_id: Optional[str] = None):
        """
        Initialize outcome collector with MANDATORY DCP integration
        
        Args:
            dcp_path: Path to DCP context file (mandatory per CLAUDE.md)
            project_root: Root directory of the project
            team_id: Optional team identifier
        """
        # DCP is MANDATORY - this is how the general staff coordinates
        self.dcp_manager = DCPManager(dcp_path)
        self.project_root = project_root or Path.cwd()
        self.team_id = team_id
        
        # Initialize privacy manager with DCP
        self.privacy_manager = PrivacyManager(dcp_path, team_id)
        self.engine, self.Session = init_db()
        
        # Load outcome history from DCP
        self._load_outcomes_from_dcp()
    
    def _detect_project_context(self) -> Dict[str, Any]:
        """Detect current project context"""
        context = {
            'project_type': 'unknown',
            'language': 'unknown',
            'architecture': 'unknown',
            'codebase_size': 0
        }
        
        # Simple detection based on files
        if (self.project_root / 'package.json').exists():
            context['project_type'] = 'node'
            context['language'] = 'javascript'
        elif (self.project_root / 'requirements.txt').exists():
            context['project_type'] = 'python'
            context['language'] = 'python'
        elif (self.project_root / 'Cargo.toml').exists():
            context['project_type'] = 'rust'
            context['language'] = 'rust'
        
        # Estimate codebase size (simplified)
        try:
            file_count = sum(1 for _ in self.project_root.rglob('*.py'))
            file_count += sum(1 for _ in self.project_root.rglob('*.js'))
            context['codebase_size'] = file_count * 100  # Rough estimate
        except:
            pass
        
        return context
    
    def record_outcome(
        self,
        task_id: str,
        status: TaskStatus,
        time_taken: Optional[int] = None,
        estimated_time: Optional[int] = None,
        user_feedback: Optional[Dict[str, Any]] = None,
        recommendation_id: Optional[str] = None,
        experiment_variant: ExperimentVariant = ExperimentVariant.CONTROL
    ) -> str:
        """
        Record a task outcome
        
        Args:
            task_id: Unique task identifier
            status: Task completion status
            time_taken: Actual time in minutes
            estimated_time: Originally estimated time
            user_feedback: Optional feedback data
            recommendation_id: Associated recommendation
            experiment_variant: A/B test variant
            
        Returns:
            Outcome ID
        """
        # Generate outcome ID
        outcome_id = f"outcome_{uuid.uuid4().hex[:8]}"
        
        # Detect project context
        context = self._detect_project_context()
        
        # Sanitize feedback
        if user_feedback:
            if 'notes' in user_feedback:
                user_feedback['notes'] = self.privacy_manager.sanitize_feedback(
                    user_feedback['notes']
                )
        
        # Create outcome record
        outcome = TaskOutcome(
            id=outcome_id,
            task_id=task_id,
            recommendation_id=recommendation_id,
            status=status,
            time_taken=time_taken,
            estimated_time=estimated_time,
            user_feedback=user_feedback,
            experiment_variant=experiment_variant,
            
            # Context
            project_type=context['project_type'],
            language=context['language'],
            architecture=context['architecture'],
            codebase_size=context['codebase_size'],
            team_id=self.privacy_manager.hash_team_id(self.team_id),
            
            # Privacy
            is_shareable=self.privacy_manager.check_sharing_permission(self.team_id),
            data_expiry=self.privacy_manager.calculate_expiry_date()
        )
        
        # Store in database
        session = self.Session()
        try:
            session.add(outcome)
            session.commit()
            logger.info(f"Recorded outcome {outcome_id} for task {task_id}")
            
            # Always write to DCP for cross-session learning
            self._write_to_dcp(outcome)
            
            return outcome_id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to record outcome: {e}")
            raise
        finally:
            session.close()
    
    def _is_significant_outcome(self, outcome: TaskOutcome) -> bool:
        """Determine if outcome is significant enough for DCP"""
        # Failed tasks are always significant
        if outcome.status == TaskStatus.FAILED:
            return True
        
        # Large time overruns are significant
        if outcome.time_taken and outcome.estimated_time:
            if outcome.time_taken > outcome.estimated_time * 2:
                return True
        
        # User feedback makes it significant
        if outcome.user_feedback and outcome.user_feedback.get('rating'):
            rating = outcome.user_feedback['rating']
            if rating <= 2 or rating >= 5:  # Very bad or very good
                return True
        
        return False
    
    def _write_to_dcp(self, outcome: TaskOutcome) -> None:
        """Write ALL outcomes to DCP for comprehensive learning"""
        # Determine priority based on significance
        priority = self._calculate_outcome_priority(outcome)
        
        observation = {
            'outcome_id': outcome.id,
            'task_id': outcome.task_id,
            'status': outcome.status.value,
            'time_taken': outcome.time_taken,
            'estimated_time': outcome.estimated_time,
            'project_context': {
                'type': outcome.project_type,
                'language': outcome.language,
                'architecture': outcome.architecture,
                'codebase_size': outcome.codebase_size
            },
            'experiment_variant': outcome.experiment_variant.value,
            'team_id': outcome.team_id,
            'is_shareable': outcome.is_shareable
        }
        
        if outcome.user_feedback:
            observation['feedback_summary'] = {
                'rating': outcome.user_feedback.get('rating'),
                'has_notes': bool(outcome.user_feedback.get('notes')),
                'tags': outcome.user_feedback.get('tags', [])
            }
        
        # Add time estimation accuracy if available
        if outcome.time_taken and outcome.estimated_time:
            observation['estimation_accuracy'] = outcome.time_taken / outcome.estimated_time
        
        try:
            self.dcp_manager.add_observation(
                'task_outcome_recorded',
                observation,
                source_agent='learning_system',
                priority=priority
            )
            logger.info(f"Wrote outcome {outcome.id} to DCP with priority {priority}")
        except Exception as e:
            logger.error(f"Failed to write to DCP: {e}")
    
    def _calculate_outcome_priority(self, outcome: TaskOutcome) -> int:
        """Calculate priority for DCP observation based on outcome significance"""
        # Base priority
        priority = 50
        
        # Failed tasks are more important
        if outcome.status == TaskStatus.FAILED:
            priority += 20
        
        # Large time overruns are significant
        if outcome.time_taken and outcome.estimated_time:
            overrun_ratio = outcome.time_taken / outcome.estimated_time
            if overrun_ratio > 2:
                priority += 15
            elif overrun_ratio > 1.5:
                priority += 10
        
        # User feedback makes it more important
        if outcome.user_feedback:
            rating = outcome.user_feedback.get('rating')
            if rating:
                if rating <= 2:
                    priority += 15  # Very negative
                elif rating >= 5:
                    priority += 10  # Very positive
        
        return min(90, priority)  # Cap at 90
    
    def record_feedback(
        self,
        task_id: str,
        rating: Optional[int] = None,
        notes: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Record user feedback for a task
        
        Args:
            task_id: Task identifier
            rating: Rating 1-5
            notes: Feedback notes
            tags: Optional tags
            
        Returns:
            Success boolean
        """
        session = self.Session()
        try:
            # Find existing outcome
            outcome = session.query(TaskOutcome).filter_by(
                task_id=task_id
            ).first()
            
            if not outcome:
                logger.warning(f"No outcome found for task {task_id}")
                return False
            
            # Update feedback
            feedback = outcome.user_feedback or {}
            
            if rating is not None:
                feedback['rating'] = max(1, min(5, rating))
            
            if notes is not None:
                feedback['notes'] = self.privacy_manager.sanitize_feedback(notes)
            
            if tags:
                feedback['tags'] = tags
            
            feedback['updated_at'] = datetime.utcnow().isoformat()
            
            outcome.user_feedback = feedback
            session.commit()
            
            logger.info(f"Updated feedback for task {task_id}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to record feedback: {e}")
            return False
        finally:
            session.close()
    
    def _load_outcomes_from_dcp(self) -> None:
        """Load outcome history from DCP for continuity"""
        try:
            dcp_data = self.dcp_manager.read_dcp()
            if dcp_data and 'learning' in dcp_data:
                learning_data = dcp_data['learning']
                self.outcome_summary = learning_data.get('outcomes', {}).get('summary', {
                    'total_outcomes': 0,
                    'failed_outcomes': 0,
                    'average_estimation_accuracy': 1.0
                })
                
                if self.outcome_summary['total_outcomes'] > 0:
                    logger.info(f"Loaded outcome summary from DCP: {self.outcome_summary['total_outcomes']} total outcomes")
            else:
                self.outcome_summary = {
                    'total_outcomes': 0,
                    'failed_outcomes': 0,
                    'average_estimation_accuracy': 1.0
                }
        except Exception as e:
            logger.warning(f"Could not load outcome history from DCP: {e}")
            self.outcome_summary = {
                'total_outcomes': 0,
                'failed_outcomes': 0,
                'average_estimation_accuracy': 1.0
            }
    
    def update_outcome_summary_in_dcp(self) -> None:
        """Update outcome summary in DCP periodically"""
        session = self.Session()
        try:
            # Calculate current summary
            total = session.query(TaskOutcome).count()
            failed = session.query(TaskOutcome).filter(
                TaskOutcome.status == TaskStatus.FAILED
            ).count()
            
            # Calculate average estimation accuracy
            outcomes_with_times = session.query(TaskOutcome).filter(
                TaskOutcome.time_taken.isnot(None),
                TaskOutcome.estimated_time.isnot(None)
            ).all()
            
            if outcomes_with_times:
                accuracies = [o.time_taken / o.estimated_time for o in outcomes_with_times]
                avg_accuracy = sum(accuracies) / len(accuracies)
            else:
                avg_accuracy = 1.0
            
            self.outcome_summary = {
                'total_outcomes': total,
                'failed_outcomes': failed,
                'failure_rate': failed / total if total > 0 else 0,
                'average_estimation_accuracy': avg_accuracy,
                'last_updated': datetime.utcnow().isoformat()
            }
            
            # Update DCP
            dcp_data = self.dcp_manager.read_dcp() or {}
            if 'learning' not in dcp_data:
                dcp_data['learning'] = {}
            if 'outcomes' not in dcp_data['learning']:
                dcp_data['learning']['outcomes'] = {}
            dcp_data['learning']['outcomes']['summary'] = self.outcome_summary
            self.dcp_manager.write_dcp(dcp_data)
            
            logger.info(f"Updated outcome summary in DCP: {total} total, {failed} failed")
            
        finally:
            session.close()


def track_task(
    task_id: Optional[str] = None,
    estimated_time: Optional[int] = None,
    collector: Optional[OutcomeCollector] = None,
    dcp_path: Optional[str] = None
):
    """
    Decorator to track task execution outcomes
    
    Usage:
        @track_task(task_id="refactor_auth", estimated_time=30)
        def refactor_authentication():
            # Task implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate task ID if not provided
            actual_task_id = task_id or f"{func.__name__}_{int(time.time())}"
            
            # Use global collector if not provided (DCP is mandatory)
            outcome_collector = collector or OutcomeCollector(dcp_path=dcp_path)
            
            # Track execution time
            start_time = time.time()
            status = TaskStatus.IN_PROGRESS
            result = None
            
            try:
                # Execute task
                result = func(*args, **kwargs)
                status = TaskStatus.COMPLETED
                
            except Exception as e:
                status = TaskStatus.FAILED
                logger.error(f"Task {actual_task_id} failed: {e}")
                raise
                
            finally:
                # Calculate time taken
                elapsed = int((time.time() - start_time) / 60)  # Convert to minutes
                
                # Record outcome
                outcome_collector.record_outcome(
                    task_id=actual_task_id,
                    status=status,
                    time_taken=elapsed,
                    estimated_time=estimated_time
                )
            
            return result
            
        return wrapper
    return decorator


# Export main classes
__all__ = ['OutcomeCollector', 'track_task']