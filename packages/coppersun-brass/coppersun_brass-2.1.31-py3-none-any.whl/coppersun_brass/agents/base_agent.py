"""Fixed base class for DCP-aware agents using new storage.

This is a minimal fix that makes agents work with the new SQLite storage
while preserving their existing functionality.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
import time
import threading
from datetime import datetime, timedelta

# Use our new adapter instead of broken DCPManager
from ..core.dcp_adapter import DCPAdapter
from ..core.storage import BrassStorage
from ..config import BrassConfig

# Keep health monitor if it exists
try:
    from ..core.health_monitor import HealthMonitor
    HAS_HEALTH_MONITOR = True
except ImportError:
    HAS_HEALTH_MONITOR = False
    HealthMonitor = None

logger = logging.getLogger(__name__)


class DCPAwareAgent(ABC):
    """Base class for agents with automatic DCP integration (FIXED).
    
    Minimal changes to make existing agents work with SQLite storage.
    """
    
    def __init__(
        self,
        project_path: str,
        dcp_path: Optional[str] = None,
        dcp_adapter: Optional[DCPAdapter] = None,
        context_window_hours: int = 24,
        enable_health_monitoring: bool = True
    ):
        """Initialize agent with new storage backend.
        
        Args:
            project_path: Path to the project being analyzed
            dcp_path: Optional custom DCP file path (ignored, for compatibility)
            dcp_adapter: Optional shared DCPAdapter instance (prevents database conflicts)
            context_window_hours: How many hours of history to load on startup
            enable_health_monitoring: Whether to enable health monitoring
        """
        self.project_path = Path(project_path)
        self.context_window_hours = context_window_hours
        self._startup_context = {}
        
        # Health monitoring setup
        self.enable_health_monitoring = enable_health_monitoring and HAS_HEALTH_MONITOR
        self.health_monitor = None
        self._start_time = time.time()
        self._last_heartbeat = time.time()
        self._heartbeat_thread = None
        self._shutdown_health = threading.Event()
        
        # Initialize new storage system
        try:
            if dcp_adapter:
                # Use shared DCPAdapter (prevents database conflicts)
                self.dcp_manager = dcp_adapter
                logger.info(f"{self.agent_name} initialized with shared DCPAdapter storage")
            else:
                # Fallback: create own storage (for backward compatibility)
                config = BrassConfig(self.project_path)
                storage = BrassStorage(config.db_path)
                self.dcp_manager = DCPAdapter(storage)
                logger.info(f"{self.agent_name} initialized with SQLite storage")
            
            # Load startup context
            self._load_startup_context()
            
        except Exception as e:
            logger.warning(f"{self.agent_name} starting without DCP: {e}")
            self.dcp_manager = None
        
        # Initialize health monitoring if available
        if self.enable_health_monitoring and HAS_HEALTH_MONITOR:
            self._setup_health_monitoring()
    
    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Return the agent's identifier."""
        pass
    
    @property
    @abstractmethod
    def relevant_observation_types(self) -> List[str]:
        """Define which observation types this agent needs on startup."""
        pass
    
    def _load_startup_context(self) -> None:
        """Load relevant observations from DCP on startup."""
        if not self.dcp_manager:
            return
            
        try:
            # Calculate time window
            cutoff_time = datetime.now() - timedelta(hours=self.context_window_hours)
            
            # Get observations using adapter
            observations = self.dcp_manager.get_observations(since=cutoff_time)
            
            # Filter by relevant types
            relevant_obs = [
                obs for obs in observations
                if obs.get('type') in self.relevant_observation_types
            ]
            
            # Organize by type
            self._startup_context = {}
            for obs in relevant_obs:
                obs_type = obs['type']
                if obs_type not in self._startup_context:
                    self._startup_context[obs_type] = []
                self._startup_context[obs_type].append(obs)
            
            logger.info(
                f"{self.agent_name} loaded {len(relevant_obs)} observations "
                f"from last {self.context_window_hours} hours"
            )
            
        except Exception as e:
            logger.error(f"Failed to load startup context: {e}")
            self._startup_context = {}
    
    def get_startup_context(self, observation_type: Optional[str] = None) -> Any:
        """Get observations loaded at startup.
        
        Args:
            observation_type: Specific type to retrieve, or None for all
            
        Returns:
            Filtered observations or all startup context
        """
        if observation_type:
            return self._startup_context.get(observation_type, [])
        return self._startup_context
    
    def add_observation(
        self,
        observation_type: str,
        data: Dict[str, Any],
        priority: int = 50,
        **kwargs
    ) -> Optional[int]:
        """Add an observation to DCP.
        
        Args:
            observation_type: Type of observation
            data: Observation data
            priority: Priority level (0-100)
            **kwargs: Additional metadata
            
        Returns:
            Observation ID if successful, None otherwise
        """
        if not self.dcp_manager:
            logger.debug(f"No DCP manager available for {observation_type}")
            return None
            
        try:
            # Merge kwargs into data for compatibility
            full_data = {**data, **kwargs}
            
            # Use adapter's add_observation method
            obs_id = self.dcp_manager.add_observation(
                obs_type=observation_type,
                data=full_data,
                source_agent=self.agent_name,
                priority=priority
            )
            
            # Update heartbeat
            self._last_heartbeat = time.time()
            
            return obs_id
            
        except Exception as e:
            logger.error(f"Failed to add observation: {e}")
            return None
    
    def query_observations(
        self,
        observation_type: Optional[str] = None,
        since_hours: Optional[int] = None,
        source_agent: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Query observations from DCP.
        
        Args:
            observation_type: Filter by type
            since_hours: Only observations from last N hours
            source_agent: Filter by source agent
            
        Returns:
            List of matching observations
        """
        if not self.dcp_manager:
            return []
            
        try:
            since = None
            if since_hours:
                since = datetime.now() - timedelta(hours=since_hours)
                
            return self.dcp_manager.get_observations(
                obs_type=observation_type,
                source_agent=source_agent,
                since=since
            )
            
        except Exception as e:
            logger.error(f"Failed to query observations: {e}")
            return []
    
    def _setup_health_monitoring(self) -> None:
        """Set up health monitoring for the agent."""
        if not HAS_HEALTH_MONITOR:
            return
            
        try:
            # Create health monitor instance if we don't have one
            if not self.health_monitor:
                self.health_monitor = HealthMonitor(
                    project_path=str(self.project_path),
                    dcp_manager=self.dcp_manager
                )
            
            # Start heartbeat thread
            if not self._heartbeat_thread or not self._heartbeat_thread.is_alive():
                self._shutdown_health.clear()
                self._heartbeat_thread = threading.Thread(
                    target=self._heartbeat_loop,
                    daemon=True,
                    name=f"{self.agent_name}_heartbeat"
                )
                self._heartbeat_thread.start()
                
            logger.info(f"Health monitoring enabled for {self.agent_name}")
            
        except Exception as e:
            logger.warning(f"Failed to setup health monitoring: {e}")
            self.enable_health_monitoring = False
    
    def _heartbeat_loop(self) -> None:
        """Send regular heartbeats to health monitor."""
        while not self._shutdown_health.is_set():
            try:
                if self.health_monitor:
                    self.health_monitor.heartbeat(self.agent_name)
                time.sleep(30)  # Heartbeat every 30 seconds
            except Exception as e:
                logger.debug(f"Heartbeat error: {e}")
                
    def shutdown(self) -> None:
        """Clean shutdown of the agent."""
        logger.info(f"Shutting down {self.agent_name}")
        
        # Stop health monitoring
        if self._heartbeat_thread:
            self._shutdown_health.set()
            self._heartbeat_thread.join(timeout=2)
            
        # Any other cleanup
        self._cleanup()
        
    @abstractmethod
    def _cleanup(self) -> None:
        """Agent-specific cleanup logic."""
        pass