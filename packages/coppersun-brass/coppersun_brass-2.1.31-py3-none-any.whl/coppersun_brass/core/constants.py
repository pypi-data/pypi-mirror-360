"""Central constants for Copper Alloy Brass system.

This module defines all system-wide constants to avoid hardcoding values
throughout the codebase. All agents and components should import from here.
"""
from pathlib import Path


# Agent Identifiers
class AgentNames:
    """Standard agent identifiers used throughout the system."""
    WATCH = "watch"
    SCOUT = "scout"
    STRATEGIST = "strategist"
    PLANNER = "planner"
    UNKNOWN = "unknown"
    
    @classmethod
    def all_agents(cls) -> list:
        """Return list of all agent names."""
        return [cls.WATCH, cls.SCOUT, cls.STRATEGIST, cls.PLANNER]
    
    @classmethod
    def is_valid_agent(cls, name: str) -> bool:
        """Check if agent name is valid."""
        return name in cls.all_agents()


# Token and Size Limits
class TokenLimits:
    """Token limits for various contexts."""
    DEFAULT = 10000
    CLAUDE_CONTEXT = 200000
    GPT4_CONTEXT = 128000
    DCP_TARGET = 8000
    DCP_MAX = 15000
    OBSERVATION_MAX = 1000000  # 1MB per observation


# File Size Limits
class FileSizeLimits:
    """File size limits in MB."""
    DCP_WARNING = 50
    DCP_MAX = 100
    ARCHIVE_TRIGGER = 75
    LOG_FILE_MAX = 10


# Time Windows
class TimeWindows:
    """Time windows in hours for various operations."""
    DEFAULT_CONTEXT = 24  # Default context window for agents
    SCOUT_CONTEXT = 168  # 7 days for Scout
    STRATEGIST_CONTEXT = 72  # 3 days for Strategist
    WATCH_CONTEXT = 24  # 1 day for Watch
    ARCHIVE_RETENTION = 2160  # 90 days default


# File Paths
class FilePaths:
    """Standard file paths and names."""
    DCP_FILENAME = "coppersun_brass.context.json"
    DCP_BACKUP_DIR = "dcp_versions"
    ARCHIVE_DIR = "dcp_archives"
    SNAPSHOTS_DIR = ".brass/snapshots"
    LOGS_DIR = ".brass/logs"
    CACHE_DIR = ".brass/cache"
    CONFIG_DIR = ".brass"
    
    @classmethod
    def get_dcp_path(cls, project_root: Path) -> Path:
        """Get full DCP path for a project."""
        return project_root / cls.DCP_FILENAME
    
    @classmethod
    def get_archive_path(cls, project_root: Path) -> Path:
        """Get archive directory path."""
        return project_root / cls.ARCHIVE_DIR


# Observation Types
class ObservationTypes:
    """Standard observation types in the system."""
    # Core observations
    TODO = "todo"
    CODE_SMELL = "code_smell"
    SECURITY_ISSUE = "security_issue"
    FILE_ANALYSIS = "file_analysis"
    FILE_CHANGE = "file_change"
    
    # Agent status
    AGENT_STATUS = "agent_status"
    AGENT_ERROR = "agent_error"
    ANALYSIS_RESULT = "analysis_result"
    
    # Strategic observations
    CAPABILITY_ASSESSMENT = "capability_assessment"
    GAP_DETECTION = "gap_detection"
    STRATEGIC_RECOMMENDATION = "strategic_recommendation"
    BEST_PRACTICE = "best_practice"
    
    # Coordination
    ORCHESTRATION_COMPLETE = "orchestration_complete"
    TASK_ASSIGNMENT = "agent_task_assignment"
    BROADCAST = "broadcast_notification"
    
    # Sprint planning
    SPRINT_PLANNING = "sprint_planning"
    SPRINT_REVIEW = "sprint_review"
    
    @classmethod
    def all_types(cls) -> list:
        """Return all observation types."""
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        ]


# Priority Levels
class PriorityLevels:
    """Standard priority levels."""
    CRITICAL = 90
    HIGH = 70
    MEDIUM = 50
    LOW = 30
    MINIMAL = 10
    
    @classmethod
    def get_label(cls, priority: int) -> str:
        """Get label for priority value."""
        if priority >= cls.CRITICAL:
            return "CRITICAL"
        elif priority >= cls.HIGH:
            return "HIGH"
        elif priority >= cls.MEDIUM:
            return "MEDIUM"
        elif priority >= cls.LOW:
            return "LOW"
        else:
            return "MINIMAL"


# Performance Settings
class PerformanceSettings:
    """Performance-related settings."""
    # Batching
    BATCH_INTERVAL_SECONDS = 1.0
    MAX_BATCH_SIZE = 100
    
    # Caching
    CACHE_TTL_SECONDS = 60
    CACHE_MAX_ENTRIES = 1000
    
    # Threading
    MAX_WORKERS = 4
    POLLING_INTERVAL = 5
    
    # Analysis
    ANALYSIS_INTERVAL = 300  # 5 minutes
    ANALYSIS_DEBOUNCE = 10  # seconds


# Validation Settings
class ValidationSettings:
    """Validation-related settings."""
    STRICT = "strict"
    WARNINGS = "warnings"
    DISABLED = "disabled"
    
    DEFAULT_LEVEL = WARNINGS


# Archive Settings
class ArchiveSettings:
    """Archive-related settings."""
    DEFAULT_RETENTION_DAYS = 90
    SCHEDULE_HOUR = 2  # 2 AM
    SCHEDULE_MINUTE = 0
    
    # Type-specific retention (days)
    TYPE_RETENTION = {
        ObservationTypes.TODO: 180,
        ObservationTypes.FILE_ANALYSIS: 30,
        ObservationTypes.CAPABILITY_ASSESSMENT: 365,
        ObservationTypes.SECURITY_ISSUE: 365,
        ObservationTypes.STRATEGIC_RECOMMENDATION: 180,
    }


# System Metadata
class SystemMetadata:
    """System-wide metadata."""
    VERSION = "0.12.0"
    DCP_VERSION = "dcp-0.7.0"
    PROJECT_ID = "coppersun_brass"
    ORGANIZATION = "Copper Alloy Brass AI"
    
    @classmethod
    def get_meta_dict(cls) -> dict:
        """Get standard metadata dictionary."""
        return {
            "version": cls.VERSION,
            "dcp_version": cls.DCP_VERSION,
            "project_id": cls.PROJECT_ID,
            "organization": cls.ORGANIZATION
        }