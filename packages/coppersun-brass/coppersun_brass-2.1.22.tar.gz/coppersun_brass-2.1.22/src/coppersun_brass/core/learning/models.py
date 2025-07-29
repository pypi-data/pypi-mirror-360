"""
Learning System Database Models

General Staff G4 Function: Logistics and Resource Management
Manages persistent storage for learning data with privacy controls
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import json

# Defensive sqlalchemy import with graceful fallback
try:
    from sqlalchemy import (
        Column, String, Integer, Float, DateTime, Boolean, 
        JSON, Enum as SQLEnum, ForeignKey, Index, create_engine
    )
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import relationship, sessionmaker
    SQLALCHEMY_AVAILABLE = True
    Base = declarative_base()
except ImportError as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Advanced learning features disabled - sqlalchemy not available: {e}")
    SQLALCHEMY_AVAILABLE = False
    
    # Create mock classes for graceful degradation
    class MockBase: pass
    class MockColumn: 
        def __init__(self, *args, **kwargs): pass
    class MockRelationship:
        def __init__(self, *args, **kwargs): pass
    
    Base = MockBase
    Column = MockColumn
    String = Integer = Float = DateTime = Boolean = JSON = MockColumn
    SQLEnum = ForeignKey = Index = MockColumn
    relationship = MockRelationship
    
    def create_engine(*args, **kwargs): return None
    def sessionmaker(*args, **kwargs): return None

from pathlib import Path

class TaskStatus(Enum):
    """Task completion status types"""
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"
    IN_PROGRESS = "in_progress"

class ExperimentVariant(Enum):
    """A/B test variants"""
    CONTROL = "control"
    TEST = "test"

class TaskOutcome(Base):
    """
    General Staff G2 Function: Intelligence Storage with Context
    Stores outcomes of executed tasks for pattern analysis
    """
    __tablename__ = 'task_outcomes'
    
    id = Column(String, primary_key=True)
    task_id = Column(String, nullable=False, index=True)
    recommendation_id = Column(String, index=True)
    status = Column(SQLEnum(TaskStatus), nullable=False)
    time_taken = Column(Integer)  # minutes
    estimated_time = Column(Integer)  # minutes
    user_feedback = Column(JSON)
    
    # Context dimensions for partitioning
    project_type = Column(String, index=True)  # web, cli, library
    codebase_size = Column(Integer)  # lines of code
    language = Column(String, index=True)  # primary language
    architecture = Column(String)  # monolith, microservice
    team_id = Column(String, index=True)  # anonymized team identifier
    
    # A/B testing support
    experiment_variant = Column(SQLEnum(ExperimentVariant), default=ExperimentVariant.CONTROL)
    
    # Privacy controls
    is_shareable = Column(Boolean, default=False)
    data_expiry = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_context', 'language', 'project_type', 'codebase_size'),
        Index('idx_team_time', 'team_id', 'created_at'),
    )

class LearnedPattern(Base):
    """
    General Staff G2 Function: Pattern Recognition Storage
    Stores extracted patterns with confidence and conflict tracking
    """
    __tablename__ = 'learned_patterns'
    
    id = Column(String, primary_key=True)
    pattern_type = Column(String, nullable=False)  # task_success, time_estimation, etc
    pattern_name = Column(String, nullable=False)
    description = Column(String)
    
    # Context matching criteria
    context_dimensions = Column(JSON)  # {language: 'python', project_type: 'web'}
    
    # Pattern metrics
    success_rate = Column(Float, nullable=False)
    sample_size = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)
    
    # Time decay support
    last_updated = Column(DateTime, default=datetime.utcnow)
    decay_adjusted_confidence = Column(Float)
    half_life_days = Column(Integer, default=90)
    
    # Conflict resolution
    conflicts_with = Column(JSON)  # List of conflicting pattern IDs
    resolution_strategy = Column(String)  # weighted, context_specific, etc
    
    # Privacy
    team_id = Column(String, index=True)
    is_public = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_pattern_lookup', 'pattern_type', 'confidence'),
    )

class RecommendationHistory(Base):
    """
    General Staff G3 Function: Operations History
    Tracks recommendation adjustments for learning effectiveness
    """
    __tablename__ = 'recommendation_history'
    
    id = Column(String, primary_key=True)
    recommendation_id = Column(String, nullable=False, index=True)
    task_id = Column(String, ForeignKey('task_outcomes.id'))
    
    # Scoring history
    original_score = Column(Float, nullable=False)
    adjusted_score = Column(Float, nullable=False)
    adjustment_reason = Column(JSON)  # {pattern_id, confidence, explanation}
    
    # A/B testing
    experiment_variant = Column(SQLEnum(ExperimentVariant))
    
    # Results
    was_accepted = Column(Boolean)
    outcome_status = Column(SQLEnum(TaskStatus))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    task_outcome = relationship("TaskOutcome", backref="recommendations")

class PrivacyConfig(Base):
    """
    General Staff G5 Function: Data Governance
    Stores privacy configurations per team
    """
    __tablename__ = 'privacy_configs'
    
    team_id = Column(String, primary_key=True)
    data_retention_days = Column(Integer, default=180)
    share_with_team = Column(Boolean, default=False)
    share_publicly = Column(Boolean, default=False)
    strict_mode = Column(Boolean, default=True)
    
    # Audit trail
    last_updated = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(String)

# Database initialization with fallback
def init_db(db_path: Optional[Path] = None):
    """Initialize the learning database with graceful fallback"""
    if not SQLALCHEMY_AVAILABLE:
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Learning database unavailable - running in fallback mode")
        return None, None
    
    if db_path is None:
        db_path = Path.home() / '.brass' / 'learning.db'
    
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(engine)
        return engine, sessionmaker(bind=engine)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to initialize learning database: {e}")
        return None, None

# Export commonly used items
__all__ = [
    'Base', 'TaskOutcome', 'LearnedPattern', 'RecommendationHistory',
    'PrivacyConfig', 'TaskStatus', 'ExperimentVariant', 'init_db'
]