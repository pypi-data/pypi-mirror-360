"""
Base Integration Adapter

General Staff G4 Role: External Integration Management
Provides base functionality for all external service integrations
"""

import asyncio
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
import logging

from coppersun_brass.core.context.dcp_manager import DCPManager

logger = logging.getLogger(__name__)


class IntegrationAdapter(ABC):
    """
    Base adapter for all external integrations
    
    General Staff G4 Role: External Integration Management
    Converts all external events to DCP observations before processing,
    ensuring consistent state management across AI commander sessions.
    """
    
    def __init__(self, 
                 dcp_path: Optional[str] = None,
                 service_name: str = "unknown"):
        """
        Initialize with MANDATORY DCP integration
        
        Args:
            dcp_path: Path to DCP context file (mandatory per CLAUDE.md)
            service_name: Name of the external service
        """
        # DCP is MANDATORY - this is how the general staff coordinates
        self.dcp_manager = DCPManager(dcp_path)
        self.service_name = service_name
        self.event_router = EventRouter(dcp_path)
        
        # Load existing state from DCP
        self._load_state_from_dcp()
        
        # Track integration health
        self.last_event_time = None
        self.total_events = 0
        self.failed_events = 0
        
    def _load_state_from_dcp(self) -> None:
        """Load integration state from DCP"""
        try:
            integrations = self.dcp_manager.get_section('integrations', {})
            service_data = integrations.get(self.service_name, {})
            
            self.state = service_data.get('state', {})
            self.config = service_data.get('config', {})
            self.metrics = service_data.get('metrics', {
                'total_events': 0,
                'failed_events': 0,
                'last_event': None
            })
            
            logger.info(f"Loaded {self.service_name} state from DCP")
            
        except Exception as e:
            logger.warning(f"Could not load state from DCP: {e}")
            self.state = {}
            self.config = {}
            self.metrics = {}
    
    def _save_state_to_dcp(self) -> None:
        """Save current state to DCP"""
        try:
            state_data = {
                'config': self.config,
                'state': self.state,
                'metrics': {
                    'total_events': self.total_events,
                    'failed_events': self.failed_events,
                    'last_event': self.last_event_time.isoformat() if self.last_event_time else None,
                    'health_score': self._calculate_health_score()
                }
            }
            
            self.dcp_manager.update_section(
                f'integrations.{self.service_name}',
                state_data
            )
            
        except Exception as e:
            logger.error(f"Failed to save state to DCP: {e}")
    
    async def process_event(self, event: Dict[str, Any]) -> None:
        """
        Process external event through DCP first
        
        Args:
            event: External event data
        """
        try:
            # Update metrics
            self.total_events += 1
            self.last_event_time = datetime.utcnow()
            
            # Convert to DCP observation BEFORE any logic
            observation = self._event_to_observation(event)
            
            # Add metadata
            observation['metadata'] = {
                'service': self.service_name,
                'timestamp': datetime.utcnow().isoformat(),
                'event_number': self.total_events
            }
            
            # Log to DCP
            self.dcp_manager.add_observation(
                observation['type'],
                observation['data'],
                source_agent=f'integration_{self.service_name}',
                priority=observation.get('priority', 70)
            )
            
            # Route through event bus
            await self.event_router.route(observation)
            
            # Update state
            self._save_state_to_dcp()
            
        except Exception as e:
            self.failed_events += 1
            logger.error(f"Failed to process event: {e}")
            
            # Log error to DCP
            self.dcp_manager.add_observation(
                'integration_error',
                {
                    'service': self.service_name,
                    'error': str(e),
                    'event': event
                },
                source_agent=f'integration_{self.service_name}',
                priority=90
            )
    
    @abstractmethod
    def _event_to_observation(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert external event to DCP observation format
        
        Args:
            event: External event data
            
        Returns:
            Observation dictionary with type, data, and priority
        """
        pass
    
    @abstractmethod
    async def authenticate(self, **credentials) -> bool:
        """
        Authenticate with external service
        
        Returns:
            Success boolean
        """
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """
        Test connection to external service
        
        Returns:
            Success boolean
        """
        pass
    
    def _calculate_health_score(self) -> float:
        """Calculate health score for this integration"""
        if self.total_events == 0:
            return 1.0
        
        success_rate = 1.0 - (self.failed_events / self.total_events)
        
        # Factor in recency
        if self.last_event_time:
            hours_since_event = (datetime.utcnow() - self.last_event_time).total_seconds() / 3600
            recency_factor = max(0.5, 1.0 - (hours_since_event / 24))
        else:
            recency_factor = 0.5
            
        return success_rate * recency_factor
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            'service': self.service_name,
            'configured': bool(self.config),
            'authenticated': self.config.get('authenticated', False),
            'health_score': self._calculate_health_score(),
            'total_events': self.total_events,
            'failed_events': self.failed_events,
            'last_event': self.last_event_time.isoformat() if self.last_event_time else None
        }


class EventRouter:
    """
    Unified event routing system
    
    General Staff G3 Role: Operations Coordination
    Routes all external events through common pipeline with
    full observability and testing hooks.
    """
    
    def __init__(self, dcp_path: Optional[str] = None):
        """Initialize with MANDATORY DCP integration"""
        # DCP is MANDATORY
        self.dcp_manager = DCPManager(dcp_path)
        self.handlers: Dict[str, List[Callable]] = {}
        self.middleware: List[Callable] = []
        
        # Load routing configuration from DCP
        self._load_routes_from_dcp()
        
    def _load_routes_from_dcp(self) -> None:
        """Load routing configuration from DCP"""
        try:
            config = self.dcp_manager.get_section('integrations.routing', {})
            # Routes would be loaded here if configured
            logger.info("Loaded routing configuration from DCP")
        except Exception as e:
            logger.warning(f"Could not load routes from DCP: {e}")
    
    def register_handler(self, event_type: str, handler: Callable) -> None:
        """Register event handler"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        
        logger.info(f"Registered handler for {event_type}")
    
    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware to processing pipeline"""
        self.middleware.append(middleware)
        logger.info(f"Added middleware: {middleware.__name__}")
    
    async def route(self, observation: Dict[str, Any]) -> None:
        """
        Route observation through middleware and handlers
        
        Args:
            observation: DCP observation to route
        """
        try:
            # Apply middleware
            for mw in self.middleware:
                observation = await mw(observation)
                if observation is None:
                    logger.debug("Middleware filtered out observation")
                    return
            
            # Log routing decision
            event_type = observation.get('type', 'unknown')
            handler_count = len(self.handlers.get(event_type, []))
            
            self.dcp_manager.add_observation(
                'event_routed',
                {
                    'type': event_type,
                    'handlers': handler_count,
                    'timestamp': datetime.utcnow().isoformat()
                },
                source_agent='event_router',
                priority=60
            )
            
            # Execute handlers
            handlers = self.handlers.get(event_type, [])
            if not handlers:
                logger.warning(f"No handlers registered for event type: {event_type}")
                return
                
            # Run handlers concurrently
            tasks = [handler(observation) for handler in handlers]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log any handler errors
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Handler {handlers[i].__name__} failed: {result}")
                    
        except Exception as e:
            logger.error(f"Error routing observation: {e}")
            
            # Log routing error to DCP
            self.dcp_manager.add_observation(
                'routing_error',
                {
                    'observation_type': observation.get('type', 'unknown'),
                    'error': str(e)
                },
                source_agent='event_router',
                priority=85
            )


class DCPThrottler:
    """
    Prevents DCP observation flooding during webhook bursts
    
    Buffers observations when rate limit is exceeded and
    batch writes them after burst completes.
    """
    
    def __init__(self, 
                 dcp_manager: DCPManager,
                 max_per_second: int = 10):
        """
        Initialize throttler
        
        Args:
            dcp_manager: DCP manager instance
            max_per_second: Maximum observations per second
        """
        self.dcp_manager = dcp_manager
        self.max_per_second = max_per_second
        self.buffer = []
        self.flush_task = None
        self.last_write = datetime.utcnow()
        self.write_count = 0
        
    async def add_observation(self, 
                            obs_type: str, 
                            data: Dict[str, Any], 
                            **kwargs) -> None:
        """Add observation with throttling"""
        now = datetime.utcnow()
        
        # Reset counter if new second
        if (now - self.last_write).total_seconds() >= 1:
            self.write_count = 0
            self.last_write = now
            
        if self.write_count < self.max_per_second:
            # Direct write
            self.dcp_manager.add_observation(obs_type, data, **kwargs)
            self.write_count += 1
        else:
            # Buffer for batch write
            self.buffer.append((obs_type, data, kwargs))
            if not self.flush_task:
                self.flush_task = asyncio.create_task(self._flush_buffer())
    
    async def _flush_buffer(self) -> None:
        """Batch write buffered observations"""
        await asyncio.sleep(1)  # Wait for burst to complete
        
        if not self.buffer:
            self.flush_task = None
            return
            
        logger.info(f"Flushing {len(self.buffer)} buffered observations")
        
        # Group by type for efficient writing
        from collections import defaultdict
        grouped = defaultdict(list)
        
        for obs_type, data, kwargs in self.buffer:
            grouped[obs_type].append({
                'data': data,
                'kwargs': kwargs
            })
        
        # Batch write by type
        for obs_type, items in grouped.items():
            # Write in chunks to avoid overwhelming DCP
            chunk_size = 10
            for i in range(0, len(items), chunk_size):
                chunk = items[i:i + chunk_size]
                for item in chunk:
                    self.dcp_manager.add_observation(
                        obs_type,
                        item['data'],
                        **item['kwargs']
                    )
                await asyncio.sleep(0.1)  # Small delay between chunks
        
        self.buffer.clear()
        self.flush_task = None
        
        logger.info("Buffer flush complete")