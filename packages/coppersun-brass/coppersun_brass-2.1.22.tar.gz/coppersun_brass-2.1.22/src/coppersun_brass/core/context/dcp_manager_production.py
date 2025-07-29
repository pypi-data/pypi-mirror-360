"""Production-ready DCP manager with performance optimizations."""
import json
import time
import queue
import threading
import concurrent.futures
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from contextlib import contextmanager
import logging

from ..file_locking import safe_file_operation, CrossPlatformFileLock, FileLockTimeout
from .archive_service import ArchiveService, ArchivePolicy
from .observation_validator import ObservationValidator, ValidationLevel
from ..constants import FilePaths, FileSizeLimits, PerformanceSettings, ArchiveSettings, AgentNames

logger = logging.getLogger(__name__)

@dataclass
class DCPWriteRequest:
    """Queued write request."""
    operation: str  # 'add_observation', 'update_metadata', etc.
    data: Dict[str, Any]
    source_agent: str
    timestamp: float
    future: 'concurrent.futures.Future'

class ProductionDCPManager:
    """
    Production-ready DCP manager with performance optimizations.
    
    Features:
    - Thread-safe operations with proper locking
    - Write batching for performance
    - Read caching with TTL
    - Automatic backup management
    - Size monitoring and alerts
    """
    
    def __init__(self, project_path: str, config: Optional[Dict] = None):
        self.project_path = Path(project_path)
        self.config = config or {}
        
        # File paths
        self.dcp_file = FilePaths.get_dcp_path(self.project_path)
        self.backup_dir = self.project_path / FilePaths.DCP_BACKUP_DIR
        
        # Performance settings
        self.max_file_size_mb = self.config.get('max_file_size_mb', FileSizeLimits.DCP_WARNING)
        self.cache_ttl_seconds = self.config.get('cache_ttl', PerformanceSettings.CACHE_TTL_SECONDS)
        self.batch_interval_seconds = self.config.get('batch_interval', PerformanceSettings.BATCH_INTERVAL_SECONDS)
        self.max_batch_size = self.config.get('max_batch_size', PerformanceSettings.MAX_BATCH_SIZE)
        
        # Validation
        self.enable_validation = self.config.get('enable_validation', True)
        validation_level = ValidationLevel(self.config.get('validation_level', 'warnings'))
        self.validator = ObservationValidator(validation_level=validation_level) if self.enable_validation else None
        
        # Archive service
        archive_config = self.config.get('archive', {})
        if archive_config.get('enabled', True):
            self.archive_policy = ArchivePolicy(
                default_retention_days=archive_config.get('default_retention_days', ArchiveSettings.DEFAULT_RETENTION_DAYS),
                size_threshold_mb=archive_config.get('size_threshold_mb', FileSizeLimits.DCP_MAX),
                observation_count_threshold=archive_config.get('observation_threshold', 10000),
                schedule_hour=archive_config.get('schedule_hour', ArchiveSettings.SCHEDULE_HOUR),
                enabled=True
            )
            # Pass self as the dcp_manager argument
            self.archive_service = ArchiveService(self, self.archive_policy, str(self.dcp_file))
        else:
            self.archive_service = None
        
        # Cache
        self._cache = None
        self._cache_timestamp = 0
        self._cache_lock = threading.RLock()
        
        # Write queue for batching
        self._write_queue = queue.Queue()
        self._write_thread = None
        self._shutdown = threading.Event()
        
        # Metrics
        self._metrics = {
            'reads': 0,
            'writes': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'batch_writes': 0,
            'avg_read_ms': 0,
            'avg_write_ms': 0
        }
        
        # Initialize
        self._ensure_dcp_exists()
        self._start_write_thread()
        
        # Start archive service if enabled
        if self.archive_service:
            self.archive_service.start()
    
    def _ensure_dcp_exists(self):
        """Ensure DCP file exists with valid structure."""
        if not self.dcp_file.exists():
            initial_dcp = {
                "version": "1.0.0",
                "metadata": {
                    "created_at": time.time(),
                    "last_modified": time.time(),
                    "project_path": str(self.project_path)
                },
                "observations": [],
                "archive_info": []
            }
            
            with safe_file_operation(self.dcp_file) as lock:
                self.dcp_file.write_text(json.dumps(initial_dcp, indent=2))
                
            logger.info(f"Created new DCP file at {self.dcp_file}")
    
    def _start_write_thread(self):
        """Start background thread for batched writes."""
        self._write_thread = threading.Thread(
            target=self._write_worker,
            daemon=True,
            name="DCP-Write-Worker"
        )
        self._write_thread.start()
        logger.debug("Started DCP write worker thread")
    
    def _write_worker(self):
        """Background worker for batched writes."""
        while not self._shutdown.is_set():
            batch = []
            deadline = time.time() + self.batch_interval_seconds
            
            # Collect batch
            while time.time() < deadline and len(batch) < self.max_batch_size:
                timeout = deadline - time.time()
                if timeout <= 0:
                    break
                    
                try:
                    request = self._write_queue.get(timeout=timeout)
                    batch.append(request)
                except queue.Empty:
                    break
            
            # Process batch
            if batch:
                self._process_write_batch(batch)
    
    def _process_write_batch(self, batch: List[DCPWriteRequest]):
        """Process a batch of write requests."""
        start_time = time.time()
        
        try:
            # Read current DCP with lock
            with safe_file_operation(self.dcp_file, timeout=10) as lock:
                dcp_data = self._read_dcp_direct()
                
                # Apply all operations
                for request in batch:
                    try:
                        if request.operation == 'add_observation':
                            dcp_data['observations'].append(request.data)
                        elif request.operation == 'update_metadata':
                            dcp_data['metadata'].update(request.data)
                        elif request.operation == 'remove_observations':
                            # Remove observations by IDs
                            ids_to_remove = set(request.data.get('ids', []))
                            dcp_data['observations'] = [
                                obs for obs in dcp_data['observations']
                                if obs.get('id') not in ids_to_remove
                            ]
                        
                        request.future.set_result(True)
                    except Exception as e:
                        request.future.set_exception(e)
                
                # Update last modified
                dcp_data['metadata']['last_modified'] = time.time()
                
                # Write once for entire batch
                self._write_dcp_direct(dcp_data)
            
            # Invalidate cache
            with self._cache_lock:
                self._cache = None
            
            # Update metrics
            duration_ms = (time.time() - start_time) * 1000
            self._metrics['batch_writes'] += 1
            self._metrics['writes'] += len(batch)
            self._update_avg_metric('avg_write_ms', duration_ms)
            
            # Check file size
            self._check_file_size()
            
            logger.debug(f"Processed batch of {len(batch)} writes in {duration_ms:.1f}ms")
            
        except Exception as e:
            logger.error(f"Batch write failed: {e}")
            # Fail all requests in batch
            for request in batch:
                if not request.future.done():
                    request.future.set_exception(e)
    
    def _update_avg_metric(self, metric_name: str, value: float):
        """Update average metric with exponential moving average."""
        if self._metrics[metric_name] == 0:
            self._metrics[metric_name] = value
        else:
            # Exponential moving average with alpha=0.1
            self._metrics[metric_name] = (
                0.9 * self._metrics[metric_name] + 0.1 * value
            )
    
    def read_dcp(self) -> Dict[str, Any]:
        """Read DCP with caching."""
        start_time = time.time()
        
        with self._cache_lock:
            # Check cache
            if self._cache and time.time() - self._cache_timestamp < self.cache_ttl_seconds:
                self._metrics['cache_hits'] += 1
                duration_ms = (time.time() - start_time) * 1000
                self._update_avg_metric('avg_read_ms', duration_ms)
                return self._cache.copy()
            
            # Cache miss - read from file
            self._metrics['cache_misses'] += 1
            
            try:
                with safe_file_operation(self.dcp_file, timeout=5) as lock:
                    self._cache = self._read_dcp_direct()
                    self._cache_timestamp = time.time()
                    
                self._metrics['reads'] += 1
                duration_ms = (time.time() - start_time) * 1000
                self._update_avg_metric('avg_read_ms', duration_ms)
                
                return self._cache.copy()
                
            except FileLockTimeout:
                logger.warning("DCP read timed out, returning cached version if available")
                if self._cache:
                    return self._cache.copy()
                raise
    
    def _read_dcp_direct(self) -> Dict[str, Any]:
        """Read DCP directly from file (must be called within lock)."""
        try:
            content = self.dcp_file.read_text()
            return json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"DCP read error: {e}")
            # Return valid empty structure
            return {
                "version": "1.0.0",
                "metadata": {
                    "project_path": str(self.project_path)
                },
                "observations": [],
                "archive_info": []
            }
    
    def _write_dcp_direct(self, data: Dict[str, Any]):
        """Write DCP directly to file (must be called within lock)."""
        # Atomic write using temporary file
        temp_file = self.dcp_file.with_suffix('.tmp')
        temp_file.write_text(json.dumps(data, indent=2))
        temp_file.replace(self.dcp_file)
    
    def add_observation(self, observation: Dict[str, Any], source_agent: str) -> str:
        """Add observation with batching and validation."""
        # Generate ID
        obs_id = f"{source_agent}-{int(time.time() * 1000)}-{self._metrics['writes']}"
        
        # Prepare observation
        obs_data = {
            "id": obs_id,
            "timestamp": time.time(),
            "source_agent": source_agent,
            **observation
        }
        
        # Validate observation if enabled
        if self.validator and self.enable_validation:
            validation_result = self.validator.validate_observation(obs_data)
            
            if not validation_result.valid:
                if self.validator.validation_level == ValidationLevel.STRICT:
                    raise ValueError(f"Observation validation failed: {'; '.join(validation_result.errors)}")
                else:
                    logger.warning(f"Observation validation errors: {'; '.join(validation_result.errors)}")
            
            if validation_result.warnings:
                logger.debug(f"Observation validation warnings: {'; '.join(validation_result.warnings)}")
        
        # Queue for batched write
        future = threading.Future()
        request = DCPWriteRequest(
            operation='add_observation',
            data=obs_data,
            source_agent=source_agent,
            timestamp=time.time(),
            future=future
        )
        
        self._write_queue.put(request)
        
        # Wait for completion (with timeout)
        try:
            future.result(timeout=30)
            return obs_id
        except TimeoutError:
            raise TimeoutError("DCP write timed out")
    
    def get_observations(self, agent_name: Optional[str] = None, 
                        observation_type: Optional[str] = None,
                        limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get observations with filtering."""
        dcp_data = self.read_dcp()
        observations = dcp_data.get('observations', [])
        
        # Filter by agent
        if agent_name:
            observations = [o for o in observations if o.get('source_agent') == agent_name]
        
        # Filter by type
        if observation_type:
            observations = [o for o in observations if o.get('type') == observation_type]
        
        # Sort by timestamp (newest first)
        observations.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        
        # Apply limit
        if limit:
            observations = observations[:limit]
        
        return observations
    
    def _check_file_size(self):
        """Check and alert on file size."""
        try:
            size_mb = self.dcp_file.stat().st_size / (1024 * 1024)
            if size_mb > self.max_file_size_mb:
                logger.warning(
                    f"DCP file size ({size_mb:.1f}MB) exceeds limit ({self.max_file_size_mb}MB)"
                )
                # In future: trigger archive process
        except:
            pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        with self._cache_lock:
            cache_hit_rate = 0
            total_cache_attempts = self._metrics['cache_hits'] + self._metrics['cache_misses']
            if total_cache_attempts > 0:
                cache_hit_rate = self._metrics['cache_hits'] / total_cache_attempts
            
            return {
                **self._metrics,
                'cache_hit_rate': cache_hit_rate,
                'queue_size': self._write_queue.qsize(),
                'file_size_mb': self._get_file_size_mb()
            }
    
    def _get_file_size_mb(self) -> float:
        """Get DCP file size in MB."""
        try:
            return self.dcp_file.stat().st_size / (1024 * 1024)
        except:
            return 0.0
    
    def archive_old_observations(self, days_old: int = 30) -> int:
        """Archive observations older than specified days.
        
        Args:
            days_old: Archive observations older than this many days
            
        Returns:
            Number of observations archived
        """
        if not self.archive_service:
            logger.warning("Archive service not configured")
            return 0
        
        # Temporarily override policy
        original_retention = self.archive_service.policy.default_retention_days
        self.archive_service.policy.default_retention_days = days_old
        
        try:
            result = self.archive_service.run_archive()
            return result.get('archived', 0)
        finally:
            # Restore original policy
            self.archive_service.policy.default_retention_days = original_retention
    
    def get_archive_status(self) -> Dict[str, Any]:
        """Get archive service status."""
        if not self.archive_service:
            return {'enabled': False, 'message': 'Archive service not configured'}
        
        return self.archive_service.get_status()
    
    def shutdown(self):
        """Graceful shutdown."""
        logger.info("Shutting down DCP manager...")
        
        # Stop archive service first
        if self.archive_service:
            self.archive_service.stop()
        
        # Signal shutdown
        self._shutdown.set()
        
        # Process remaining queue
        remaining = []
        try:
            while True:
                remaining.append(self._write_queue.get_nowait())
        except queue.Empty:
            pass
        
        if remaining:
            logger.info(f"Processing {len(remaining)} remaining writes...")
            self._process_write_batch(remaining)
        
        # Wait for thread
        if self._write_thread:
            self._write_thread.join(timeout=5)
            
        logger.info("DCP manager shutdown complete")
    
    def create_backup(self, reason: str = "manual") -> Path:
        """Create a backup of current DCP file."""
        self.backup_dir.mkdir(exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"coppersun_brass.context.{timestamp}.{reason}.json"
        
        with safe_file_operation(self.dcp_file) as lock:
            import shutil
            shutil.copy2(self.dcp_file, backup_file)
        
        logger.info(f"Created DCP backup: {backup_file}")
        return backup_file
    
    def archive_old_observations(self, days_old: int = 30) -> int:
        """Archive observations older than specified days."""
        cutoff_timestamp = time.time() - (days_old * 24 * 60 * 60)
        
        with safe_file_operation(self.dcp_file) as lock:
            dcp_data = self._read_dcp_direct()
            
            old_observations = [
                obs for obs in dcp_data['observations']
                if obs.get('timestamp', 0) < cutoff_timestamp
            ]
            
            if not old_observations:
                return 0
            
            # Create archive
            archive_timestamp = time.strftime("%Y%m%d_%H%M%S")
            archive_file = self.backup_dir / f"archive_{archive_timestamp}.json"
            archive_file.write_text(json.dumps({
                'archived_at': time.time(),
                'cutoff_timestamp': cutoff_timestamp,
                'observations': old_observations
            }, indent=2))
            
            # Remove from main DCP
            dcp_data['observations'] = [
                obs for obs in dcp_data['observations']
                if obs.get('timestamp', 0) >= cutoff_timestamp
            ]
            
            # Add archive info
            dcp_data['archive_info'].append({
                'archive_file': str(archive_file),
                'archived_at': time.time(),
                'observation_count': len(old_observations)
            })
            
            self._write_dcp_direct(dcp_data)
        
        # Invalidate cache
        with self._cache_lock:
            self._cache = None
        
        logger.info(f"Archived {len(old_observations)} old observations to {archive_file}")
        return len(old_observations)

# Export classes
__all__ = ['ProductionDCPManager', 'DCPWriteRequest']