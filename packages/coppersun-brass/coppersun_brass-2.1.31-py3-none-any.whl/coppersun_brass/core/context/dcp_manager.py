import uuid
import json
import threading
from pathlib import Path
from datetime import datetime, timezone
from contextlib import contextmanager
import shutil
from typing import Dict, List, Optional, Any
import platform
import time
from .pruning_strategy import DCPPruningStrategy
from .observation_validator import ObservationValidator, ValidationLevel, ValidationResult
from ..constants import FilePaths, TokenLimits, SystemMetadata, AgentNames
import logging

logger = logging.getLogger(__name__)

# OS-specific file locking
if platform.system() == 'Windows':
    import msvcrt
    def lock_file(f):
        """Lock file on Windows"""
        while True:
            try:
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                break
            except IOError:
                time.sleep(0.01)
    
    def unlock_file(f):
        """Unlock file on Windows"""
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
else:
    import fcntl
    def lock_file(f):
        """Lock file on Unix/Linux/Mac"""
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    
    def unlock_file(f):
        """Unlock file on Unix/Linux/Mac"""
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

class DCPManager:
    """Manages Copper Alloy Brass Context Protocol files with thread-safe operations"""
    
    def __init__(self, project_root=".", auto_prune=True, token_limit=TokenLimits.DCP_TARGET, 
                 enable_validation=True, validation_level=ValidationLevel.WARNINGS):
        self.project_root = Path(project_root)
        
        # Debug logging to find the issue
        if str(self.project_root).endswith('.db'):
            logger.debug(f"DCPManager initialized with database path: {self.project_root}")
            # Attempt to fix by using parent directory
            self.project_root = self.project_root.parent
            logger.debug(f"Corrected to parent directory: {self.project_root}")
        
        self.dcp_path = FilePaths.get_dcp_path(self.project_root)
        self.backup_dir = self.project_root / FilePaths.DCP_BACKUP_DIR
        self.backup_dir.mkdir(exist_ok=True)
        self._lock = threading.RLock()  # Reentrant lock for nested calls
        self.auto_prune = auto_prune
        self.pruning_strategy = DCPPruningStrategy(token_limit=token_limit)
        
        # Observation validation
        self.enable_validation = enable_validation
        self.validator = ObservationValidator(validation_level=validation_level) if enable_validation else None
        
        # Sprint 13: Performance optimization - in-memory cache
        self._cache = {
            'metadata': None,
            'observations': None,
            'last_modified': None,
            'cache_hits': 0,
            'cache_misses': 0
        }
        self._cache_ttl = 5.0  # 5 seconds cache TTL
        self._observation_index = None  # Lazy-loaded observation index
        
    @contextmanager
    def lock(self):
        """Context manager for safe DCP mutations"""
        self._lock.acquire()
        try:
            yield
        finally:
            self._lock.release()
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid based on file modification time and TTL."""
        if not self._cache['last_modified']:
            return False
        
        try:
            # Check file modification time
            if not self.dcp_path.exists():
                return False
                
            current_mtime = self.dcp_path.stat().st_mtime
            if current_mtime != self._cache['last_modified']:
                return False
            
            # Check TTL (time-to-live)
            cache_age = time.time() - self._cache.get('cache_time', 0)
            if cache_age > self._cache_ttl:
                return False
                
            return True
        except (OSError, IOError):
            return False
    
    def _update_cache(self, dcp_data: Dict[str, Any]):
        """Update the in-memory cache with new DCP data."""
        try:
            file_mtime = self.dcp_path.stat().st_mtime if self.dcp_path.exists() else 0
            
            self._cache.update({
                'metadata': dcp_data.get('meta', {}),
                'observations': dcp_data.get('current_observations', []),
                'last_modified': file_mtime,
                'cache_time': time.time()
            })
            
            # Clear observation index to force rebuild
            self._observation_index = None
            
        except (OSError, IOError):
            # Cache update failed, but continue operation
            pass
    
    def _invalidate_cache(self):
        """Invalidate the cache (call after writes)."""
        self._cache.update({
            'metadata': None,
            'observations': None,
            'last_modified': None,
            'cache_time': 0
        })
        self._observation_index = None
    
    def read_dcp(self) -> Optional[Dict[str, Any]]:
        """Read DCP with caching support and thread/file locking."""
        with self.lock():
            # Check cache first
            if self._is_cache_valid():
                self._cache['cache_hits'] += 1
                return {
                    'meta': self._cache['metadata'],
                    'current_observations': self._cache['observations'],
                    'project_awareness': {},  # Not cached for now
                    'strategic_recommendations': []  # Not cached for now
                }
            
            # Cache miss - read from disk
            self._cache['cache_misses'] += 1
            
            if not self.dcp_path.exists():
                return None
            
            try:
                with open(self.dcp_path, 'r') as f:
                    # OS-level file lock
                    lock_file(f)
                    try:
                        dcp_data = json.load(f)
                        # Update cache with fresh data
                        self._update_cache(dcp_data)
                        return dcp_data
                    finally:
                        unlock_file(f)
            except json.JSONDecodeError as e:
                # Graceful degradation - also lock backup read
                backup_path = self._get_latest_backup()
                if backup_path:
                    with open(backup_path, 'r') as f:
                        lock_file(f)
                        try:
                            dcp_data = json.load(f)
                            # Update cache with backup data
                            self._update_cache(dcp_data)
                            return dcp_data
                        finally:
                            unlock_file(f)
                raise ValueError(f"Corrupted DCP and no valid backup: {e}")
    
    def write_dcp(self, dcp_data: Dict[str, Any]) -> None:
        """Write DCP with locking, validation, and atomic operation"""
        with self.lock():
            # Invalidate cache before writing
            self._invalidate_cache()
            
            # Validate before writing
            if not self.validate_dcp(dcp_data):
                raise ValueError("Invalid DCP structure")
            
            # Apply auto-pruning if enabled and needed
            if self.auto_prune:
                estimated_tokens = self.estimate_tokens(dcp_data)
                if estimated_tokens > self.pruning_strategy.token_limit:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f"Auto-pruning triggered: {estimated_tokens} tokens > {self.pruning_strategy.token_limit} limit")
                    
                    pruned_dcp, archive_data = self.pruning_strategy.prune_observations(dcp_data)
                    
                    # Save archive if observations were pruned
                    if archive_data.get('observations'):
                        self.pruning_strategy.archive_observations(archive_data)
                    
                    dcp_data = pruned_dcp
            
            # Create backup first
            if self.dcp_path.exists():
                self._create_backup()
            
            # Write atomically with OS-level locking
            temp_path = self.dcp_path.with_suffix('.tmp')
            try:
                with open(temp_path, 'w') as f:
                    # OS-level exclusive lock
                    lock_file(f)
                    try:
                        json.dump(dcp_data, f, indent=2)
                        f.flush()  # Ensure all data is written
                    finally:
                        unlock_file(f)
                
                # Atomic rename (also needs lock on some systems)
                temp_path.replace(self.dcp_path)
            except Exception as e:
                # Clean up temp file on error
                if temp_path.exists():
                    temp_path.unlink()
                raise
    
    def estimate_tokens(self, data: Any) -> int:
        """Estimate token count for DCP data"""
        # Industry standard: ~4 characters per token for JSON
        json_str = json.dumps(data, separators=(',', ':'))
        
        # Adjust for JSON overhead
        base_tokens = len(json_str) // 4
        
        # Add 10% buffer for prompt wrapping
        return int(base_tokens * 1.1)
    
    def validate_dcp(self, dcp_data: Dict[str, Any]) -> bool:
        """Validate DCP structure"""
        required_keys = ["meta", "project_awareness", "current_observations", 
                        "strategic_recommendations"]
        
        if not isinstance(dcp_data, dict):
            return False
            
        for key in required_keys:
            if key not in dcp_data:
                return False
                
        # Validate meta section
        meta = dcp_data.get("meta", {})
        if not meta.get("version", "").startswith("dcp-"):
            return False
            
        return True
    
    def _create_backup(self) -> None:
        """Create timestamped backup of current DCP"""
        if not self.dcp_path.exists():
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"coppersun_brass.context.{timestamp}.json"
        
        shutil.copy2(self.dcp_path, backup_path)
        
        # Clean old backups (keep last 10)
        self._cleanup_old_backups()
    
    def _cleanup_old_backups(self, keep_count: int = 10) -> None:
        """Remove old backups keeping only the most recent ones"""
        backups = sorted(self.backup_dir.glob("coppersun_brass.context.*.json"))
        
        if len(backups) > keep_count:
            for backup in backups[:-keep_count]:
                backup.unlink()
    
    def _get_latest_backup(self) -> Optional[Path]:
        """Get path to most recent backup"""
        backups = sorted(self.backup_dir.glob("coppersun_brass.context.*.json"))
        return backups[-1] if backups else None
    
    def get_dcp_info(self) -> str:
        """Get formatted DCP information"""
        with self.lock():
            dcp_data = self.read_dcp()
            if not dcp_data:
                return "No DCP file found"
            
            meta = dcp_data.get("meta", {})
            obs_count = len(dcp_data.get("current_observations", []))
            rec_count = len(dcp_data.get("strategic_recommendations", []))
            token_count = self.estimate_tokens(dcp_data)
            
            info = f"""Copper Alloy Brass Context Protocol
Version: {meta.get('version', 'Unknown')}
Project: {meta.get('project_id', 'Unknown')}
Observations: {obs_count}
Recommendations: {rec_count}
Token Count: {token_count}
Token Status: {'⚠️  Warning' if token_count > 8000 else '✅ OK'}"""
            
            return info
    
    def get_current_version(self):
        """Get current DCP version"""
        with self.lock():
            dcp_data = self.read_dcp()
            if not dcp_data:
                return "unknown"
            return dcp_data.get("meta", {}).get("version", "unknown")

    def apply_claude_edits(self, edits, agent_id="claude"):
        """Apply Claude's edits with validation and rollback
        
        Args:
            edits: Dictionary of field paths to new values
            agent_id: Agent making the edits (default: claude)
            
        Returns:
            operation_id: Unique ID for this edit operation
            
        Raises:
            PermissionError: If agent lacks permission
            ValidationError: If edit violates rules
        """
        from coppersun_brass.core.context.agent_permissions import validate_agent_permission
        from coppersun_brass.core.context.change_tracker import DCPChangeTracker
        
        with self.lock():
            # Create backup for rollback
            backup = self.read_dcp()
            if not backup:
                raise ValueError("No DCP to edit")
            
            # Initialize change tracker
            tracker = DCPChangeTracker(self)
            operation_id = str(uuid.uuid4())
            
            try:
                current_dcp = json.loads(json.dumps(backup))  # Deep copy
                
                for field_path, new_value in edits.items():
                    # Check permissions
                    if not validate_agent_permission(agent_id, "edit", field_path):
                        raise PermissionError(f"{agent_id} cannot edit {field_path}")
                    
                    # Validate field-specific rules
                    if field_path.endswith("effectiveness_score"):
                        if not isinstance(new_value, (int, float)) or not 0 <= new_value <= 10:
                            raise ValueError(f"Score must be 0-10, got {new_value}")
                    
                    if field_path.endswith("priority"):
                        if not isinstance(new_value, int) or not 0 <= new_value <= 100:
                            raise ValueError(f"Priority must be 0-100, got {new_value}")
                    
                    # Apply edit
                    old_value = self._get_field_value(current_dcp, field_path)
                    self._set_field_value(current_dcp, field_path, new_value)
                    
                    # Log change with provenance
                    tracker.track_change(
                        "update", field_path, old_value, new_value, 
                        agent_id, operation_id
                    )
                
                # Validate final structure
                if not self.validate_dcp(current_dcp):
                    raise ValueError("Edits resulted in invalid DCP structure")
                
                # Save updated DCP
                self.write_dcp(current_dcp)
                
                return operation_id
                
            except Exception as e:
                # Rollback on any error
                self.write_dcp(backup)
                raise Exception(f"Edit failed, rolled back: {str(e)}")
    
    def _get_field_value(self, data, field_path):
        """Get value from nested dict using dot notation"""
        parts = field_path.split('.')
        current = data
        
        for part in parts:
            # Handle list indices
            if part.isdigit() and isinstance(current, list):
                index = int(part)
                if index < len(current):
                    current = current[index]
                else:
                    return None
            elif isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    def _set_field_value(self, data, field_path, value):
        """Set value in nested dict using dot notation"""
        parts = field_path.split('.')
        current = data
        
        # Navigate to parent
        for part in parts[:-1]:
            # Handle list indices
            if part.isdigit():
                part = int(part)
                if isinstance(current, list) and part < len(current):
                    current = current[part]
                else:
                    raise IndexError(f"Invalid list index: {part}")
            else:
                if part not in current:
                    current[part] = {}
                current = current[part]
        
        # Set the value
        final_key = parts[-1]
        if final_key.isdigit() and isinstance(current, list):
            current[int(final_key)] = value
        else:
            current[final_key] = value
    
    def validate_observation(self, observation: Dict) -> bool:
        """Validate observation against schema
        
        Args:
            observation: Observation to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If observation is invalid
        """
        # Valid observation types
        valid_types = [
            'todo_item', 'fixme_item', 'security_issue', 
            'performance_issue', 'code_smell', 'test_coverage', 
            'file_analysis', 'sprint_completion', 'implementation_gap',
            'feedback_entry', 'recommendation_registry'
        ]
        
        # Check required fields
        if not observation.get('type'):
            raise ValueError("Observation missing required field: 'type'")
        if not observation.get('summary'):
            raise ValueError("Observation missing required field: 'summary'")
        
        # Check type is valid
        if observation['type'] not in valid_types:
            raise ValueError(f"Invalid observation type: '{observation['type']}'. Valid types: {valid_types}")
        
        # Check priority range
        priority = observation.get('priority', 50)
        if not isinstance(priority, (int, float)) or not 0 <= priority <= 100:
            raise ValueError(f"Priority must be a number 0-100, got {priority}")
        
        # Check summary length
        if len(observation['summary']) > 500:
            raise ValueError(f"Summary too long ({len(observation['summary'])} chars), max 500")
        
        return True
    
    # New methods for agent integration
    def add_observation(self, observation: Dict, source_agent: str = None) -> str:
        """Add a single observation to the DCP.
        
        Args:
            observation: Dict containing:
                - type: str (required) - Type of observation
                - priority: int (0-100) - Priority level
                - summary: str (required) - Brief description
                - details: Dict - Additional context
                - location: str - File/line reference
            source_agent: str - Name of agent adding observation
            
        Returns:
            str: Unique ID of created observation
            
        Raises:
            ValueError: If observation format invalid
            RuntimeError: If write fails
        """
        with self.lock():
            # Validate observation format
            self.validate_observation(observation)
            
            # Validate observation data if validator enabled
            if self.validator and self.enable_validation:
                # Build full observation for validation
                temp_obs = {
                    'id': f"{source_agent or 'unknown'}/temp",
                    'type': observation.get('type', ''),
                    'source_agent': source_agent or 'unknown',
                    'timestamp': datetime.now().timestamp(),
                    'data': observation.get('details', {}),
                    'metadata': {
                        'priority': observation.get('priority', 50),
                        'summary': observation.get('summary', '')
                    }
                }
                
                validation_result = self.validator.validate_observation(temp_obs)
                
                if not validation_result.valid:
                    error_msg = f"Observation validation failed: {'; '.join(validation_result.errors)}"
                    if self.validator.validation_level == ValidationLevel.STRICT:
                        raise ValueError(error_msg)
                    else:
                        logger.warning(error_msg)
                
                if validation_result.warnings:
                    logger.warning(f"Observation validation warnings: {'; '.join(validation_result.warnings)}")
            
            # Generate unique ID with microsecond precision to avoid collisions
            obs_id = f"{source_agent or AgentNames.UNKNOWN}/{uuid.uuid4().hex[:8]}-{int(datetime.now().timestamp() * 1000000)}"
            
            # Read current DCP
            dcp_data = self.read_dcp()
            if not dcp_data:
                # Initialize empty DCP if none exists
                dcp_data = {
                    "meta": {
                        "version": "dcp-0.7.0",
                        "project_id": "coppersun_brass",
                        "last_updated": datetime.now(timezone.utc).isoformat(),
                        "update_count": 0
                    },
                    "project_awareness": {},
                    "current_observations": [],
                    "strategic_recommendations": []
                }
            
            # Create observation entry
            obs_entry = {
                "id": obs_id,
                "type": observation['type'],
                "priority": observation.get('priority', 50),
                "summary": observation['summary'],
                "details": observation.get('details', {}),
                "location": observation.get('location', ''),
                "source_agent": source_agent or 'unknown',
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "status": observation.get('status', 'new')
            }
            
            # Add to observations
            if 'current_observations' not in dcp_data:
                dcp_data['current_observations'] = []
            dcp_data['current_observations'].append(obs_entry)
            
            # Update metadata
            dcp_data['meta']['last_updated'] = datetime.now(timezone.utc).isoformat()
            dcp_data['meta']['update_count'] = dcp_data['meta'].get('update_count', 0) + 1
            
            # Note: Pruning is now handled by write_dcp() with smart strategy
            
            # Write back
            self.write_dcp(dcp_data)
            
            # Check token usage and warn if approaching limit
            current_tokens = self.estimate_tokens(dcp_data)
            warning_threshold = self.pruning_strategy.token_limit * 0.9
            if current_tokens > warning_threshold:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"DCP approaching token limit: {current_tokens}/{self.pruning_strategy.token_limit} tokens ({int(current_tokens/self.pruning_strategy.token_limit*100)}% full)")
            
            return obs_id
    
    def add_observations(self, observations: List[Dict], source_agent: str = None) -> Dict[str, Any]:
        """Batch add multiple observations.
        
        Args:
            observations: List of observation dicts
            source_agent: str - Name of agent adding observations
            
        Returns:
            Dict containing:
                - ids: List of created observation IDs
                - succeeded: Number of successful additions
                - failed: Number of failed additions
                - errors: List of validation errors
        """
        with self.lock():
            obs_ids = []
            errors = []
            succeeded = 0
            failed = 0
            
            # Read DCP once
            dcp_data = self.read_dcp()
            if not dcp_data:
                # Initialize empty DCP if none exists
                dcp_data = {
                    "meta": {
                        "version": "dcp-0.7.0",
                        "project_id": "coppersun_brass",
                        "last_updated": datetime.now(timezone.utc).isoformat(),
                        "update_count": 0
                    },
                    "project_awareness": {},
                    "current_observations": [],
                    "strategic_recommendations": []
                }
            
            # Process each observation
            for i, observation in enumerate(observations):
                # Validate
                try:
                    self.validate_observation(observation)
                except ValueError as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Skipping invalid observation in batch: {e}")
                    errors.append({
                        'index': i,
                        'error': str(e),
                        'observation': observation
                    })
                    failed += 1
                    continue  # Skip invalid observations in batch
                
                # Generate ID with microsecond precision to avoid collisions
                obs_id = f"{source_agent or AgentNames.UNKNOWN}/{uuid.uuid4().hex[:8]}-{int(datetime.now().timestamp() * 1000000)}"
                obs_ids.append(obs_id)
                
                # Create entry
                obs_entry = {
                    "id": obs_id,
                    "type": observation['type'],
                    "priority": observation.get('priority', 50),
                    "summary": observation['summary'],
                    "details": observation.get('details', {}),
                    "location": observation.get('location', ''),
                    "source_agent": source_agent or 'unknown',
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "status": observation.get('status', 'new')
                }
                
                if 'current_observations' not in dcp_data:
                    dcp_data['current_observations'] = []
                dcp_data['current_observations'].append(obs_entry)
                succeeded += 1
            
            # Update metadata
            dcp_data['meta']['last_updated'] = datetime.now(timezone.utc).isoformat()
            dcp_data['meta']['update_count'] = dcp_data['meta'].get('update_count', 0) + 1
            
            # Note: Pruning is now handled by write_dcp() with smart strategy
            
            # Write once
            self.write_dcp(dcp_data)
            
            # Return detailed results
            return {
                'ids': obs_ids,
                'succeeded': succeeded,
                'failed': failed,
                'errors': errors,
                'total': len(observations)
            }
    
    def update_observation(self, obs_id: str, updates: Dict) -> bool:
        """Update existing observation.
        
        Args:
            obs_id: Observation ID to update
            updates: Fields to update
            
        Returns:
            bool: True if updated successfully
        """
        with self.lock():
            dcp_data = self.read_dcp()
            if not dcp_data or 'current_observations' not in dcp_data:
                return False
            
            # Find observation
            for obs in dcp_data['current_observations']:
                if obs.get('id') == obs_id:
                    # Update fields
                    for key, value in updates.items():
                        if key not in ['id', 'created_at']:  # Protect immutable fields
                            obs[key] = value
                    obs['updated_at'] = datetime.now(timezone.utc).isoformat()
                    
                    # Update metadata
                    dcp_data['meta']['last_updated'] = datetime.now(timezone.utc).isoformat()
                    dcp_data['meta']['update_count'] = dcp_data['meta'].get('update_count', 0) + 1
                    
                    # Write back
                    self.write_dcp(dcp_data)
                    return True
            
            return False
    
    def remove_observation(self, obs_id: str) -> bool:
        """Remove an observation by ID.
        
        Args:
            obs_id: Observation ID to remove
            
        Returns:
            bool: True if removed successfully
        """
        with self.lock():
            dcp_data = self.read_dcp()
            if not dcp_data or 'current_observations' not in dcp_data:
                return False
            
            original_count = len(dcp_data['current_observations'])
            dcp_data['current_observations'] = [
                obs for obs in dcp_data['current_observations']
                if obs.get('id') != obs_id
            ]
            
            if len(dcp_data['current_observations']) < original_count:
                # Update metadata
                dcp_data['meta']['last_updated'] = datetime.now(timezone.utc).isoformat()
                dcp_data['meta']['update_count'] = dcp_data['meta'].get('update_count', 0) + 1
                
                # Write back
                self.write_dcp(dcp_data)
                return True
            
            return False
    
    def update_metadata(self, updates: Dict) -> bool:
        """Update DCP metadata section.
        
        Args:
            updates: Metadata fields to update
            
        Returns:
            bool: True if updated successfully
        """
        with self.lock():
            dcp_data = self.read_dcp()
            if not dcp_data:
                return False
            
            if 'meta' not in dcp_data:
                dcp_data['meta'] = {}
            
            # Update metadata fields
            for key, value in updates.items():
                if key not in ['version', 'project_id']:  # Protect core fields
                    dcp_data['meta'][key] = value
            
            dcp_data['meta']['last_updated'] = datetime.now(timezone.utc).isoformat()
            dcp_data['meta']['update_count'] = dcp_data['meta'].get('update_count', 0) + 1
            
            # Write back
            self.write_dcp(dcp_data)
            return True
    
    def annotate_observation(self, obs_id: str, annotation: Dict) -> bool:
        """Add annotation to an observation.
        
        Args:
            obs_id: Observation ID to annotate
            annotation: Annotation data to add
            
        Returns:
            bool: True if annotated successfully
        """
        with self.lock():
            dcp_data = self.read_dcp()
            if not dcp_data or 'current_observations' not in dcp_data:
                return False
            
            # Find observation
            for obs in dcp_data['current_observations']:
                if obs.get('id') == obs_id:
                    # Add annotations array if not exists
                    if 'annotations' not in obs:
                        obs['annotations'] = []
                    
                    # Add timestamp to annotation
                    annotation['annotated_at'] = datetime.now(timezone.utc).isoformat()
                    obs['annotations'].append(annotation)
                    obs['updated_at'] = datetime.now(timezone.utc).isoformat()
                    
                    # Update metadata
                    dcp_data['meta']['last_updated'] = datetime.now(timezone.utc).isoformat()
                    dcp_data['meta']['update_count'] = dcp_data['meta'].get('update_count', 0) + 1
                    
                    # Write back
                    self.write_dcp(dcp_data)
                    return True
            
            return False
    
    def get_observations(self, filters: Dict = None) -> List[Dict]:
        """Get observations with optional filtering.
        
        Args:
            filters: Optional filters:
                - type: str or List[str]
                - agent: str or List[str]
                - priority_min: int
                - since: datetime
                - limit: int
                
        Returns:
            List[Dict]: Matching observations
        """
        with self.lock():
            dcp_data = self.read_dcp()
            if not dcp_data or 'current_observations' not in dcp_data:
                return []
            
            observations = dcp_data['current_observations']
            
            if not filters:
                return observations
            
            # Apply filters
            filtered = observations
            
            # Type filter
            if 'type' in filters:
                types = filters['type']
                if isinstance(types, str):
                    types = [types]
                filtered = [obs for obs in filtered if obs.get('type') in types]
            
            # Agent filter
            if 'agent' in filters:
                agents = filters['agent']
                if isinstance(agents, str):
                    agents = [agents]
                filtered = [obs for obs in filtered if obs.get('source_agent') in agents]
            
            # Priority filter
            if 'priority_min' in filters:
                min_priority = filters['priority_min']
                filtered = [obs for obs in filtered if obs.get('priority', 0) >= min_priority]
            
            # Time filter
            if 'since' in filters:
                since_str = filters['since']
                if isinstance(since_str, datetime):
                    since_str = since_str.isoformat()
                filtered = [obs for obs in filtered if obs.get('created_at', '') >= since_str]
            
            # Limit
            if 'limit' in filters and filters['limit'] > 0:
                filtered = filtered[:filters['limit']]
            
            return filtered
    
    def get_observation_by_id(self, obs_id: str) -> Optional[Dict]:
        """Get specific observation by ID.
        
        Args:
            obs_id: Observation ID
            
        Returns:
            Dict or None if not found
        """
        with self.lock():
            dcp_data = self.read_dcp()
            if not dcp_data or 'current_observations' not in dcp_data:
                return None
            
            for obs in dcp_data['current_observations']:
                if obs.get('id') == obs_id:
                    return obs
            
            return None
    
    def get_observations_by_type(self, obs_type: str, limit: int = None) -> List[Dict]:
        """Get all observations of a specific type.
        
        Args:
            obs_type: Type of observations to retrieve
            limit: Maximum number of observations to return (most recent first)
            
        Returns:
            List[Dict]: Observations of the specified type
        """
        filters = {'type': obs_type}
        if limit:
            filters['limit'] = limit
        return self.get_observations(filters)
    
    def get_observations_by_agent(self, agent_id: str) -> List[Dict]:
        """Get all observations from a specific agent.
        
        Args:
            agent_id: Agent ID to filter by
            
        Returns:
            List[Dict]: Observations from the specified agent
        """
        return self.get_observations({'agent': agent_id})
    
    def get_cache_performance(self) -> Dict[str, Any]:
        """Get cache performance metrics.
        
        Returns:
            Dict with cache statistics
        """
        total_requests = self._cache['cache_hits'] + self._cache['cache_misses']
        hit_rate = self._cache['cache_hits'] / total_requests if total_requests > 0 else 0
        
        return {
            'cache_hits': self._cache['cache_hits'],
            'cache_misses': self._cache['cache_misses'],
            'hit_rate': hit_rate,
            'cache_valid': self._is_cache_valid(),
            'cache_ttl': self._cache_ttl,
            'observations_cached': len(self._cache.get('observations', []))
        }
    
    def add_cache_performance_observation(self):
        """Add cache performance observation to DCP."""
        try:
            perf_data = self.get_cache_performance()
            if perf_data['cache_hits'] + perf_data['cache_misses'] > 0:
                self.add_observation({
                    'type': 'cache_performance',
                    'priority': 40,
                    'summary': f"Cache hit rate: {perf_data['hit_rate']:.1%}",
                    'details': perf_data
                }, source_agent='dcp_manager')
        except Exception:
            # Don't fail if we can't record performance metrics
            pass

class ObservationIndex:
    """In-memory index for fast observation queries."""
    
    def __init__(self):
        self.by_type: Dict[str, List[str]] = {}
        self.by_agent: Dict[str, List[str]] = {}
        self.by_priority: Dict[int, List[str]] = {}
        self.observations: Dict[str, Dict] = {}
        
    def add_observation(self, obs: Dict):
        """Add observation to indexes."""
        obs_id = obs.get('id')
        if not obs_id:
            return
            
        self.observations[obs_id] = obs
        
        # Index by type
        obs_type = obs.get('type', 'unknown')
        self.by_type.setdefault(obs_type, []).append(obs_id)
        
        # Index by agent
        agent = obs.get('source_agent', 'unknown')
        self.by_agent.setdefault(agent, []).append(obs_id)
        
        # Index by priority bucket (group by tens: 0-9, 10-19, etc.)
        priority = obs.get('priority', 50)
        priority_bucket = (priority // 10) * 10
        self.by_priority.setdefault(priority_bucket, []).append(obs_id)
        
    def query_by_type(self, obs_type: str, limit: int = None) -> List[Dict]:
        """Fast query by type."""
        obs_ids = self.by_type.get(obs_type, [])
        if limit:
            obs_ids = obs_ids[-limit:]  # Most recent (assuming chronological order)
        return [self.observations[oid] for oid in obs_ids if oid in self.observations]
        
    def query_by_agent(self, agent: str, limit: int = None) -> List[Dict]:
        """Fast query by agent."""
        obs_ids = self.by_agent.get(agent, [])
        if limit:
            obs_ids = obs_ids[-limit:]
        return [self.observations[oid] for oid in obs_ids if oid in self.observations]
        
    def query_by_priority_range(self, min_priority: int, limit: int = None) -> List[Dict]:
        """Fast query by priority range."""
        matching_obs = []
        for priority_bucket, obs_ids in self.by_priority.items():
            if priority_bucket >= min_priority:
                for oid in obs_ids:
                    if oid in self.observations:
                        obs = self.observations[oid]
                        if obs.get('priority', 50) >= min_priority:
                            matching_obs.append(obs)
        
        # Sort by priority (highest first) and apply limit
        matching_obs.sort(key=lambda x: x.get('priority', 50), reverse=True)
        if limit:
            matching_obs = matching_obs[:limit]
        return matching_obs
        
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            'total_observations': len(self.observations),
            'types': list(self.by_type.keys()),
            'agents': list(self.by_agent.keys()),
            'priority_buckets': sorted(self.by_priority.keys())
        }


class DCPUpdateResult:
    """Result of a DCP update operation"""
    def __init__(self, success=True, message="", changes=None):
        self.success = success
        self.message = message
        self.changes = changes or []
