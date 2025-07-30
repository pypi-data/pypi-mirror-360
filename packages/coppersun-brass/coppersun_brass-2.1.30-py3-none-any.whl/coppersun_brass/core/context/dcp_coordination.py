"""DCP-based agent coordination to replace Event Bus.

General Staff Role: This component provides the coordination infrastructure
for multi-agent communication through DCP observations. It replaces the
event bus with a more persistent and queryable system.
"""
from typing import Dict, List, Optional, Set, Callable, Any
from datetime import datetime, timedelta
import logging
import threading
import time
from dataclasses import dataclass, field
from ..constants import ObservationTypes

logger = logging.getLogger(__name__)


# ObservationType enum removed - using constants.ObservationTypes instead


@dataclass
class CoordinationMessage:
    """Message for inter-agent coordination."""
    observation_type: str
    source_agent: str
    target_agents: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 50
    requires_action: bool = False
    broadcast: bool = False


class DCPCoordinator:
    """Coordinates agent communication through DCP observations.
    
    This replaces the Event Bus with DCP-based coordination that provides:
    1. Persistent message history
    2. Query capabilities
    3. Priority-based routing
    4. Broadcast support
    """
    
    def __init__(self, agent_name: str, dcp_manager):
        """Initialize coordinator.
        
        Args:
            agent_name: Name of the agent using this coordinator
            dcp_manager: DCP manager instance
        """
        self.agent_name = agent_name
        self.dcp_manager = dcp_manager
        self.processed_observations: Set[str] = set()
        self._handlers: Dict[str, List[Callable]] = {}
        self._polling_thread = None
        self._stop_polling = threading.Event()
        self.polling_interval = 5  # seconds
        
    def publish(self, message: CoordinationMessage) -> Optional[str]:
        """Publish a coordination message as DCP observation.
        
        Args:
            message: Coordination message to publish
            
        Returns:
            Observation ID if successful
        """
        try:
            # Build observation
            observation = {
                'type': message.observation_type,
                'data': message.data,
                'metadata': {
                    **message.metadata,
                    'source_agent': message.source_agent,
                    'priority': message.priority,
                    'requires_action': message.requires_action,
                    'coordination_timestamp': datetime.now().isoformat()
                }
            }
            
            # Add routing information
            if message.broadcast:
                observation['metadata']['broadcast'] = True
            elif message.target_agents:
                observation['metadata']['target_agents'] = message.target_agents
            
            # Write to DCP
            if not self.dcp_manager:
                logger.error("No DCP manager available for publishing")
                return None
                
            obs_id = self.dcp_manager.add_observation(
                obs_type=message.observation_type,
                data=message.data,
                source_agent=message.source_agent,
                priority=message.priority
            )
            
            logger.debug(
                f"Published {message.observation_type} observation: {obs_id}"
            )
            
            return obs_id
            
        except Exception as e:
            logger.error(f"Failed to publish coordination message: {e}")
            return None
    
    def subscribe(self, obs_type: str, handler: Callable) -> None:
        """Subscribe to observations of a specific type.
        
        Args:
            obs_type: Observation type to subscribe to
            handler: Function to call when observation is found
        """
        if obs_type not in self._handlers:
            self._handlers[obs_type] = []
        self._handlers[obs_type].append(handler)
        logger.debug(f"{self.agent_name} subscribed to {obs_type}")
    
    def start_polling(self) -> None:
        """Start polling DCP for new observations."""
        if self._polling_thread and self._polling_thread.is_alive():
            logger.warning("Polling already running")
            return
            
        self._stop_polling.clear()
        self._polling_thread = threading.Thread(
            target=self._polling_loop,
            daemon=True
        )
        self._polling_thread.start()
        logger.info(f"{self.agent_name} started DCP polling")
    
    def stop_polling(self) -> None:
        """Stop polling DCP."""
        self._stop_polling.set()
        if self._polling_thread:
            self._polling_thread.join(timeout=10)
        logger.info(f"{self.agent_name} stopped DCP polling")
    
    def _polling_loop(self) -> None:
        """Main polling loop to check for new observations."""
        while not self._stop_polling.is_set():
            try:
                self._check_for_new_observations()
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
            
            # Wait for next polling interval
            self._stop_polling.wait(self.polling_interval)
    
    def _check_for_new_observations(self) -> None:
        """Check DCP for new observations to process."""
        # Get recent observations
        since_hours = self.polling_interval / 3600.0 * 2  # Look back 2x polling interval
        
        try:
            dcp_data = self.dcp_manager.read_dcp()
            if not dcp_data:
                logger.debug("No DCP data available")
                return
                
            observations = dcp_data.get('observations', [])
            
            # Filter recent observations
            cutoff = (datetime.now() - timedelta(hours=since_hours)).timestamp()
            recent_obs = [
                obs for obs in observations
                if obs.get('timestamp', 0) >= cutoff
            ]
            
            # Process each observation
            for obs in recent_obs:
                self._process_observation(obs)
                
        except Exception as e:
            logger.error(f"Failed to check for observations: {e}")
    
    def _process_observation(self, obs: Dict[str, Any]) -> None:
        """Process a single observation."""
        obs_id = obs.get('id')
        
        # Skip if already processed
        if obs_id in self.processed_observations:
            return
            
        # Check if this observation is for us
        metadata = obs.get('metadata', {})
        
        # Skip if from ourselves (unless broadcast)
        if (metadata.get('source_agent') == self.agent_name and 
            not metadata.get('broadcast', False)):
            self.processed_observations.add(obs_id)
            return
        
        # Check targeting
        is_broadcast = metadata.get('broadcast', False)
        target_agents = metadata.get('target_agents', [])
        is_targeted = self.agent_name in target_agents
        
        if not is_broadcast and not is_targeted and target_agents:
            # This observation has specific targets and we're not one
            self.processed_observations.add(obs_id)
            return
        
        # Get handlers for this observation type
        obs_type = obs.get('type')
        handlers = self._handlers.get(obs_type, [])
        
        if handlers:
            logger.debug(f"Processing {obs_type} observation: {obs_id}")
            
            # Call each handler
            for handler in handlers:
                try:
                    handler(obs)
                except Exception as e:
                    logger.error(
                        f"Handler error for {obs_type}: {e}",
                        exc_info=True
                    )
        
        # Mark as processed
        self.processed_observations.add(obs_id)
    
    def query_coordination_messages(
        self,
        obs_types: Optional[List[str]] = None,
        source_agents: Optional[List[str]] = None,
        since_hours: Optional[int] = None,
        requires_action: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Query for coordination messages.
        
        Args:
            obs_types: Filter by observation types
            source_agents: Filter by source agents
            since_hours: Only get messages from last N hours
            requires_action: Filter by action requirement
            
        Returns:
            List of matching observations
        """
        try:
            dcp_data = self.dcp_manager.read_dcp()
            if not dcp_data:
                logger.debug("No DCP data available for query")
                return []
                
            observations = dcp_data.get('observations', [])
            
            # Apply filters
            filtered = observations
            
            if obs_types:
                filtered = [
                    obs for obs in filtered
                    if obs.get('type') in obs_types
                ]
            
            if source_agents:
                filtered = [
                    obs for obs in filtered
                    if obs.get('metadata', {}).get('source_agent') in source_agents
                ]
            
            if since_hours:
                cutoff = (datetime.now() - timedelta(hours=since_hours)).timestamp()
                filtered = [
                    obs for obs in filtered
                    if obs.get('timestamp', 0) >= cutoff
                ]
            
            if requires_action is not None:
                filtered = [
                    obs for obs in filtered
                    if obs.get('metadata', {}).get('requires_action') == requires_action
                ]
            
            return filtered
            
        except Exception as e:
            logger.error(f"Failed to query coordination messages: {e}")
            return []


# EventBusCompatibilityLayer removed - migration to DCP complete