"""
Pattern Extractor for Learning System

General Staff G2 Function: Intelligence Analysis
Extracts actionable patterns from task outcome data
"""

import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import json
import logging
import uuid

from sqlalchemy import func, and_, or_

from coppersun_brass.core.learning.models import (
    TaskOutcome, LearnedPattern, TaskStatus, init_db
)
from coppersun_brass.core.context.dcp_manager import DCPManager
from .dcp_helpers import get_dcp_section, update_dcp_section

logger = logging.getLogger(__name__)

class PatternExtractor:
    """
    Extracts patterns from task outcomes
    
    General Staff G2 Function: Intelligence Analysis
    This component extracts patterns that must persist across AI commander sessions
    to build institutional memory and enable continuous learning.
    """
    
    # Minimum samples required for pattern extraction
    MIN_SAMPLES = 5
    
    # Confidence thresholds
    MIN_CONFIDENCE = 0.6
    HIGH_CONFIDENCE = 0.8
    
    def __init__(self, dcp_path: Optional[str] = None, team_id: Optional[str] = None):
        """
        Initialize pattern extractor with MANDATORY DCP integration
        
        Args:
            dcp_path: Path to DCP context file (mandatory per CLAUDE.md)
            team_id: Optional team identifier for filtering
        """
        # DCP is MANDATORY - this is how the general staff coordinates
        self.dcp_manager = DCPManager(dcp_path)
        self.team_id = team_id
        self.engine, self.Session = init_db()
        
        # Check if database is available
        self.db_available = self.engine is not None and self.Session is not None
        if not self.db_available:
            logger.warning("Pattern extraction running without database - using DCP-only mode")
        
        # Load existing patterns from DCP
        self._load_patterns_from_dcp()
    
    def extract_patterns(
        self,
        min_samples: int = None,
        lookback_days: int = 90
    ) -> List[LearnedPattern]:
        """
        Extract patterns from recent task outcomes
        
        Args:
            min_samples: Minimum samples required (default: MIN_SAMPLES)
            lookback_days: How many days to look back
            
        Returns:
            List of extracted patterns
        """
        min_samples = min_samples or self.MIN_SAMPLES
        patterns = []
        
        # Extract different types of patterns
        patterns.extend(self._extract_success_patterns(min_samples, lookback_days))
        patterns.extend(self._extract_time_estimation_patterns(min_samples, lookback_days))
        patterns.extend(self._extract_context_patterns(min_samples, lookback_days))
        
        # Detect conflicts between patterns
        self._detect_pattern_conflicts(patterns)
        
        # Store patterns in database
        self._store_patterns(patterns)
        
        # Store significant patterns in DCP for cross-session persistence
        self._persist_patterns_to_dcp(patterns)
        
        return patterns
    
    def _extract_success_patterns(
        self,
        min_samples: int,
        lookback_days: int
    ) -> List[LearnedPattern]:
        """Extract patterns related to task success rates"""
        if not self.db_available:
            logger.info("Database unavailable - skipping success pattern extraction")
            return []
        
        session = self.Session()
        patterns = []
        
        try:
            # Get recent outcomes
            cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)
            
            # Group by context dimensions
            query = session.query(
                TaskOutcome.project_type,
                TaskOutcome.language,
                TaskOutcome.status,
                func.count(TaskOutcome.id).label('count')
            ).filter(
                TaskOutcome.created_at >= cutoff_date
            )
            
            if self.team_id:
                query = query.filter(TaskOutcome.team_id == self.team_id)
            
            results = query.group_by(
                TaskOutcome.project_type,
                TaskOutcome.language,
                TaskOutcome.status
            ).all()
            
            # Process results by context
            context_stats = defaultdict(lambda: {'total': 0, 'completed': 0})
            
            for project_type, language, status, count in results:
                key = (project_type, language)
                context_stats[key]['total'] += count
                if status == TaskStatus.COMPLETED:
                    context_stats[key]['completed'] += count
            
            # Create patterns for contexts with enough samples
            for (project_type, language), stats in context_stats.items():
                if stats['total'] >= min_samples:
                    success_rate = stats['completed'] / stats['total']
                    confidence = self._calculate_confidence(
                        stats['total'],
                        success_rate
                    )
                    
                    if confidence >= self.MIN_CONFIDENCE:
                        pattern = LearnedPattern(
                            id=f"pattern_success_{uuid.uuid4().hex[:8]}",
                            pattern_type='task_success',
                            pattern_name=f"Success rate for {language} {project_type}",
                            description=f"Tasks in {language} {project_type} projects have {success_rate:.1%} success rate",
                            context_dimensions={
                                'project_type': project_type,
                                'language': language
                            },
                            success_rate=success_rate,
                            sample_size=stats['total'],
                            confidence=confidence,
                            team_id=self.team_id
                        )
                        patterns.append(pattern)
            
            return patterns
            
        finally:
            session.close()
    
    def _extract_time_estimation_patterns(
        self,
        min_samples: int,
        lookback_days: int
    ) -> List[LearnedPattern]:
        """Extract patterns related to time estimation accuracy"""
        if not self.db_available:
            logger.info("Database unavailable - skipping time estimation pattern extraction")
            return []
        
        session = self.Session()
        patterns = []
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)
            
            # Get outcomes with time data
            query = session.query(TaskOutcome).filter(
                and_(
                    TaskOutcome.created_at >= cutoff_date,
                    TaskOutcome.time_taken.isnot(None),
                    TaskOutcome.estimated_time.isnot(None),
                    TaskOutcome.status == TaskStatus.COMPLETED
                )
            )
            
            if self.team_id:
                query = query.filter(TaskOutcome.team_id == self.team_id)
            
            outcomes = query.all()
            
            if len(outcomes) >= min_samples:
                # Calculate estimation accuracy
                estimation_ratios = []
                overrun_count = 0
                
                for outcome in outcomes:
                    ratio = outcome.time_taken / outcome.estimated_time
                    estimation_ratios.append(ratio)
                    if ratio > 1.2:  # 20% overrun
                        overrun_count += 1
                
                avg_ratio = sum(estimation_ratios) / len(estimation_ratios)
                overrun_rate = overrun_count / len(outcomes)
                
                # Create estimation accuracy pattern
                confidence = self._calculate_confidence(
                    len(outcomes),
                    1 - abs(1 - avg_ratio)  # Closer to 1.0 is better
                )
                
                if confidence >= self.MIN_CONFIDENCE:
                    pattern = LearnedPattern(
                        id=f"pattern_time_{uuid.uuid4().hex[:8]}",
                        pattern_type='time_estimation',
                        pattern_name='Time estimation accuracy',
                        description=f"Time estimates are {avg_ratio:.1f}x actual time, {overrun_rate:.1%} overrun rate",
                        context_dimensions={
                            'team_id': self.team_id
                        },
                        success_rate=1 - abs(1 - avg_ratio),
                        sample_size=len(outcomes),
                        confidence=confidence,
                        team_id=self.team_id
                    )
                    patterns.append(pattern)
            
            return patterns
            
        finally:
            session.close()
    
    def _extract_context_patterns(
        self,
        min_samples: int,
        lookback_days: int
    ) -> List[LearnedPattern]:
        """Extract patterns based on specific contexts"""
        if not self.db_available:
            logger.info("Database unavailable - skipping context pattern extraction")
            return []
        
        session = self.Session()
        patterns = []
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)
            
            # Look for patterns in failed tasks
            failed_query = session.query(
                TaskOutcome.language,
                TaskOutcome.user_feedback,
                func.count(TaskOutcome.id).label('count')
            ).filter(
                and_(
                    TaskOutcome.created_at >= cutoff_date,
                    TaskOutcome.status == TaskStatus.FAILED
                )
            )
            
            if self.team_id:
                failed_query = failed_query.filter(TaskOutcome.team_id == self.team_id)
            
            failed_results = failed_query.group_by(
                TaskOutcome.language
            ).having(
                func.count(TaskOutcome.id) >= min_samples
            ).all()
            
            # Analyze failure patterns
            for language, feedback, count in failed_results:
                # Simple pattern: high failure rate in specific language
                total_in_language = session.query(
                    func.count(TaskOutcome.id)
                ).filter(
                    and_(
                        TaskOutcome.language == language,
                        TaskOutcome.created_at >= cutoff_date
                    )
                ).scalar()
                
                failure_rate = count / total_in_language if total_in_language > 0 else 0
                
                if failure_rate > 0.3:  # High failure rate
                    confidence = self._calculate_confidence(
                        total_in_language,
                        1 - failure_rate
                    )
                    
                    pattern = LearnedPattern(
                        id=f"pattern_failure_{uuid.uuid4().hex[:8]}",
                        pattern_type='failure_risk',
                        pattern_name=f"High failure risk in {language}",
                        description=f"{language} tasks have {failure_rate:.1%} failure rate",
                        context_dimensions={
                            'language': language
                        },
                        success_rate=1 - failure_rate,
                        sample_size=total_in_language,
                        confidence=confidence,
                        team_id=self.team_id
                    )
                    patterns.append(pattern)
            
            return patterns
            
        finally:
            session.close()
    
    def _calculate_confidence(
        self,
        sample_size: int,
        success_rate: float
    ) -> float:
        """
        Calculate confidence score for a pattern
        
        Uses Wilson score interval for binomial proportion
        """
        if sample_size == 0:
            return 0.0
        
        # Wilson score parameters
        z = 1.96  # 95% confidence interval
        
        # Wilson score calculation
        p = success_rate
        n = sample_size
        
        denominator = 1 + z**2 / n
        center = p + z**2 / (2 * n)
        spread = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n)
        
        # Lower bound of confidence interval
        lower_bound = (center - spread) / denominator
        
        # Adjust for sample size (more samples = higher confidence)
        size_factor = min(1.0, math.log(sample_size + 1) / math.log(50))
        
        # Final confidence
        confidence = lower_bound * size_factor
        
        return max(0.0, min(1.0, confidence))
    
    def _detect_pattern_conflicts(
        self,
        patterns: List[LearnedPattern]
    ) -> None:
        """Detect conflicts between patterns"""
        for i, pattern1 in enumerate(patterns):
            conflicts = []
            
            for j, pattern2 in enumerate(patterns):
                if i >= j:
                    continue
                
                # Check if patterns conflict
                if self._patterns_conflict(pattern1, pattern2):
                    conflicts.append(pattern2.id)
            
            if conflicts:
                pattern1.conflicts_with = conflicts
                pattern1.resolution_strategy = 'context_specific'
    
    def _patterns_conflict(
        self,
        pattern1: LearnedPattern,
        pattern2: LearnedPattern
    ) -> bool:
        """Check if two patterns conflict"""
        # Same type patterns with overlapping context
        if pattern1.pattern_type != pattern2.pattern_type:
            return False
        
        # Check context overlap
        ctx1 = pattern1.context_dimensions or {}
        ctx2 = pattern2.context_dimensions or {}
        
        # If contexts are disjoint, no conflict
        for key in ctx1:
            if key in ctx2 and ctx1[key] != ctx2[key]:
                return False
        
        # Conflicting success rates
        if abs(pattern1.success_rate - pattern2.success_rate) > 0.3:
            return True
        
        return False
    
    def _store_patterns(self, patterns: List[LearnedPattern]) -> None:
        """Store patterns in database"""
        if not patterns:
            return
        
        if not self.db_available:
            logger.info("Database unavailable - patterns stored in DCP only")
            return
        
        session = self.Session()
        try:
            for pattern in patterns:
                # Check if similar pattern exists
                existing = session.query(LearnedPattern).filter(
                    and_(
                        LearnedPattern.pattern_type == pattern.pattern_type,
                        LearnedPattern.context_dimensions == pattern.context_dimensions
                    )
                ).first()
                
                if existing:
                    # Update existing pattern
                    existing.success_rate = pattern.success_rate
                    existing.sample_size = pattern.sample_size
                    existing.confidence = pattern.confidence
                    existing.last_updated = datetime.utcnow()
                    existing.decay_adjusted_confidence = pattern.confidence
                else:
                    # Add new pattern
                    session.add(pattern)
            
            session.commit()
            logger.info(f"Stored {len(patterns)} patterns")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to store patterns: {e}")
            raise
        finally:
            session.close()
    
    def get_patterns_for_context(
        self,
        context: Dict[str, Any]
    ) -> List[LearnedPattern]:
        """
        Get patterns matching a specific context
        
        Args:
            context: Context dictionary to match
            
        Returns:
            List of matching patterns
        """
        if not self.db_available:
            logger.info("Database unavailable - returning patterns from DCP only")
            return self._get_patterns_from_dcp(context)
        
        session = self.Session()
        try:
            # Start with all patterns
            query = session.query(LearnedPattern).filter(
                LearnedPattern.confidence >= self.MIN_CONFIDENCE
            )
            
            # Filter by team if specified
            if self.team_id:
                query = query.filter(
                    or_(
                        LearnedPattern.team_id == self.team_id,
                        LearnedPattern.is_public == True
                    )
                )
            
            patterns = query.all()
            
            # Filter by context match
            matching_patterns = []
            for pattern in patterns:
                if self._context_matches(pattern.context_dimensions, context):
                    # Apply time decay to confidence
                    pattern.decay_adjusted_confidence = self._apply_time_decay(pattern)
                    matching_patterns.append(pattern)
            
            # Sort by confidence
            matching_patterns.sort(
                key=lambda p: p.decay_adjusted_confidence,
                reverse=True
            )
            
            return matching_patterns
            
        finally:
            session.close()
    
    def _context_matches(
        self,
        pattern_context: Dict[str, Any],
        target_context: Dict[str, Any]
    ) -> bool:
        """Check if pattern context matches target context"""
        if not pattern_context:
            return True  # Universal pattern
        
        for key, value in pattern_context.items():
            if key in target_context and target_context[key] != value:
                return False
        
        return True
    
    def _apply_time_decay(self, pattern: LearnedPattern) -> float:
        """Apply time decay to pattern confidence"""
        if not pattern.last_updated:
            return pattern.confidence
        
        age_days = (datetime.utcnow() - pattern.last_updated).days
        half_life = pattern.half_life_days or 90
        
        # Exponential decay
        decay_factor = math.exp(-math.log(2) * age_days / half_life)
        
        return pattern.confidence * decay_factor

    def _load_patterns_from_dcp(self) -> None:
        """Load existing patterns from DCP for continuity across sessions"""
        try:
            learning_data = get_dcp_section(self.dcp_manager, 'learning', {})
            stored_patterns = learning_data.get('patterns', {}).get('extracted', [])
            
            if stored_patterns:
                logger.info(f"Loaded {len(stored_patterns)} patterns from DCP")
                # Patterns are stored in DCP for reference but primary storage is DB
                # This ensures AI commanders know what patterns exist
        except Exception as e:
            logger.warning(f"Could not load patterns from DCP: {e}")
    
    def _persist_patterns_to_dcp(self, patterns: List[LearnedPattern]) -> None:
        """Persist significant patterns to DCP for future AI sessions"""
        if not patterns:
            return
        
        # Only persist high-confidence patterns to DCP
        significant_patterns = [p for p in patterns if p.confidence >= self.HIGH_CONFIDENCE]
        
        if significant_patterns:
            # Convert to DCP-friendly format
            pattern_data = [
                {
                    'id': p.id,
                    'type': p.pattern_type,
                    'name': p.pattern_name,
                    'description': p.description,
                    'confidence': float(p.confidence),
                    'success_rate': float(p.success_rate),
                    'sample_size': p.sample_size,
                    'context': p.context_dimensions,
                    'conflicts_with': p.conflicts_with,
                    'last_updated': p.last_updated.isoformat() if p.last_updated else None,
                    'team_id': p.team_id
                }
                for p in significant_patterns
            ]
            
            # Update DCP
            self.dcp_manager.update_section('learning.patterns.extracted', pattern_data)
            
            # Add observation for significant event
            self.dcp_manager.add_observation(
                'pattern_extracted',
                {
                    'count': len(significant_patterns),
                    'types': list(set(p.pattern_type for p in significant_patterns)),
                    'avg_confidence': sum(p.confidence for p in significant_patterns) / len(significant_patterns),
                    'team_id': self.team_id
                },
                source_agent='learning_system',
                priority=80  # High priority for learning insights
            )
            
            logger.info(f"Persisted {len(significant_patterns)} high-confidence patterns to DCP")
    
    def _get_patterns_from_dcp(self, context: Dict[str, Any]) -> List[LearnedPattern]:
        """Fallback method to get patterns from DCP when database unavailable"""
        try:
            learning_data = get_dcp_section(self.dcp_manager, 'learning', {})
            stored_patterns = learning_data.get('patterns', {}).get('extracted', [])
            
            # Convert stored patterns back to LearnedPattern objects (simplified)
            patterns = []
            for pattern_data in stored_patterns:
                # Create a simplified pattern object for compatibility
                pattern = type('LearnedPattern', (), {
                    'id': pattern_data.get('id', ''),
                    'pattern_type': pattern_data.get('type', ''),
                    'pattern_name': pattern_data.get('name', ''),
                    'description': pattern_data.get('description', ''),
                    'confidence': pattern_data.get('confidence', 0.0),
                    'success_rate': pattern_data.get('success_rate', 0.0),
                    'sample_size': pattern_data.get('sample_size', 0),
                    'context_dimensions': pattern_data.get('context', {}),
                    'decay_adjusted_confidence': pattern_data.get('confidence', 0.0)
                })()
                
                # Check if pattern matches context
                if self._context_matches(pattern.context_dimensions, context):
                    patterns.append(pattern)
            
            return patterns
        except Exception as e:
            logger.warning(f"Could not load patterns from DCP: {e}")
            return []

# Export main class
__all__ = ['PatternExtractor']