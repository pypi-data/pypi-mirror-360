"""Automated archive service for DCP management.

General Staff Role: This component maintains operational efficiency by
automatically archiving old observations, preventing DCP bloat while
preserving historical intelligence for future AI analysis.
"""
import os
import json
import gzip
import shutil
import logging
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ArchiveFormat(Enum):
    """Supported archive formats."""
    JSON = "json"
    GZIP = "gzip"
    TARBALL = "tar.gz"


@dataclass
class ArchivePolicy:
    """Configuration for archive policies."""
    # Default retention in days
    default_retention_days: int = 90
    
    # Type-specific retention
    type_retention: Dict[str, int] = None
    
    # Archive triggers
    size_threshold_mb: float = 100.0
    observation_count_threshold: int = 10000
    
    # Archive location
    archive_path: Path = None
    archive_format: ArchiveFormat = ArchiveFormat.GZIP
    
    # Scheduling
    schedule_hour: int = 2  # 2 AM by default
    schedule_minute: int = 0
    enabled: bool = True
    
    def __post_init__(self):
        if self.type_retention is None:
            self.type_retention = {
                'todo': 180,  # Keep TODOs longer
                'file_analysis': 30,  # Frequent updates
                'capability_assessment': 365,  # Keep for a year
                'security_issue': 365,  # Keep security issues
                'strategic_recommendation': 180,
                'orchestration_complete': 90
            }


class ArchiveService:
    """Automated archive service for DCP observations.
    
    This service runs in the background and automatically archives
    old observations based on configurable policies.
    """
    
    def __init__(self, 
                 dcp_manager,
                 policy: Optional[ArchivePolicy] = None,
                 dcp_path: Optional[str] = None):
        """Initialize archive service.
        
        Args:
            dcp_manager: DCP manager instance
            policy: Archive policy configuration
            dcp_path: Path to DCP file
        """
        self.dcp_manager = dcp_manager
        self.policy = policy or ArchivePolicy()
        self.dcp_path = Path(dcp_path or "coppersun_brass.context.json")
        
        # Set up archive directory
        if self.policy.archive_path is None:
            self.policy.archive_path = self.dcp_path.parent / "dcp_archives"
        self.policy.archive_path.mkdir(parents=True, exist_ok=True)
        
        # Threading
        self._archive_thread = None
        self._stop_event = threading.Event()
        self._last_archive = None
        
        # Statistics
        self.stats = {
            'total_archived': 0,
            'total_archives': 0,
            'last_archive_time': None,
            'space_saved_mb': 0.0
        }
    
    def start(self):
        """Start the archive service."""
        if not self.policy.enabled:
            logger.info("Archive service is disabled by policy")
            return
            
        if self._archive_thread and self._archive_thread.is_alive():
            logger.warning("Archive service already running")
            return
        
        self._stop_event.clear()
        self._archive_thread = threading.Thread(
            target=self._archive_loop,
            daemon=True,
            name="DCPArchiveService"
        )
        self._archive_thread.start()
        logger.info("Archive service started")
    
    def stop(self):
        """Stop the archive service."""
        self._stop_event.set()
        if self._archive_thread:
            self._archive_thread.join(timeout=10)
        logger.info("Archive service stopped")
    
    def _archive_loop(self):
        """Main archive loop that runs in background."""
        while not self._stop_event.is_set():
            try:
                # Check if it's time to archive
                if self._should_archive():
                    self.run_archive()
                
                # Sleep for a minute before checking again
                self._stop_event.wait(60)
                
            except Exception as e:
                logger.error(f"Error in archive loop: {e}", exc_info=True)
                # Wait longer on error
                self._stop_event.wait(300)
    
    def _should_archive(self) -> bool:
        """Check if archiving should run based on schedule and triggers."""
        now = datetime.now()
        
        # Check schedule
        scheduled_time = now.replace(
            hour=self.policy.schedule_hour,
            minute=self.policy.schedule_minute,
            second=0,
            microsecond=0
        )
        
        # If we haven't archived today and it's past the scheduled time
        if self._last_archive is None or self._last_archive.date() < now.date():
            if now >= scheduled_time:
                return True
        
        # Check size trigger
        if self.dcp_path.exists():
            size_mb = self.dcp_path.stat().st_size / (1024 * 1024)
            if size_mb >= self.policy.size_threshold_mb:
                logger.info(f"DCP size {size_mb:.1f}MB exceeds threshold")
                return True
        
        # Check observation count trigger
        try:
            dcp_data = self.dcp_manager.read_dcp()
            obs_count = len(dcp_data.get('observations', []))
            if obs_count >= self.policy.observation_count_threshold:
                logger.info(f"Observation count {obs_count} exceeds threshold")
                return True
        except Exception:
            pass
        
        return False
    
    def run_archive(self) -> Dict[str, Any]:
        """Run archive process.
        
        Returns:
            Archive statistics
        """
        logger.info("Starting archive process")
        start_time = time.time()
        
        try:
            # Get observations to archive
            observations_to_archive = self._get_observations_to_archive()
            
            if not observations_to_archive:
                logger.info("No observations to archive")
                return {'archived': 0, 'duration': 0}
            
            # Create archive
            archive_path = self._create_archive(observations_to_archive)
            
            # Remove archived observations from DCP
            self._remove_archived_observations(observations_to_archive)
            
            # Update statistics
            duration = time.time() - start_time
            self.stats['total_archived'] += len(observations_to_archive)
            self.stats['total_archives'] += 1
            self.stats['last_archive_time'] = datetime.now()
            
            # Calculate space saved
            if self.dcp_path.exists():
                new_size = self.dcp_path.stat().st_size / (1024 * 1024)
                archive_size = archive_path.stat().st_size / (1024 * 1024)
                space_saved = len(observations_to_archive) * 0.001  # Rough estimate
                self.stats['space_saved_mb'] += space_saved
            
            self._last_archive = datetime.now()
            
            result = {
                'archived': len(observations_to_archive),
                'archive_path': str(archive_path),
                'duration': duration,
                'space_saved_mb': space_saved
            }
            
            logger.info(
                f"Archive complete: {len(observations_to_archive)} observations "
                f"archived to {archive_path.name} in {duration:.1f}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Archive process failed: {e}", exc_info=True)
            return {'error': str(e), 'duration': time.time() - start_time}
    
    def _get_observations_to_archive(self) -> List[Dict[str, Any]]:
        """Get observations that should be archived based on retention policy.
        
        Returns:
            List of observations to archive
        """
        try:
            dcp_data = self.dcp_manager.read_dcp()
            all_observations = dcp_data.get('observations', [])
            
            observations_to_archive = []
            now = datetime.now()
            
            for obs in all_observations:
                # Get observation age
                timestamp = obs.get('timestamp', 0)
                obs_date = datetime.fromtimestamp(timestamp)
                age_days = (now - obs_date).days
                
                # Get retention for this type
                obs_type = obs.get('type', 'unknown')
                retention_days = self.policy.type_retention.get(
                    obs_type, 
                    self.policy.default_retention_days
                )
                
                # Check if should archive
                if age_days > retention_days:
                    observations_to_archive.append(obs)
            
            return observations_to_archive
            
        except Exception as e:
            logger.error(f"Failed to get observations to archive: {e}")
            return []
    
    def _create_archive(self, observations: List[Dict[str, Any]]) -> Path:
        """Create archive file with observations.
        
        Args:
            observations: Observations to archive
            
        Returns:
            Path to created archive
        """
        # Generate archive filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"dcp_archive_{timestamp}"
        
        # Create archive data
        archive_data = {
            'meta': {
                'archive_timestamp': datetime.now().isoformat(),
                'observation_count': len(observations),
                'dcp_version': 'dcp-0.7.0',
                'retention_policy': {
                    'default_days': self.policy.default_retention_days,
                    'type_specific': self.policy.type_retention
                }
            },
            'observations': observations
        }
        
        # Write archive based on format
        if self.policy.archive_format == ArchiveFormat.GZIP:
            archive_path = self.policy.archive_path / f"{base_name}.json.gz"
            with gzip.open(archive_path, 'wt', encoding='utf-8') as f:
                json.dump(archive_data, f, indent=2)
                
        elif self.policy.archive_format == ArchiveFormat.JSON:
            archive_path = self.policy.archive_path / f"{base_name}.json"
            with open(archive_path, 'w') as f:
                json.dump(archive_data, f, indent=2)
                
        else:
            raise ValueError(f"Unsupported archive format: {self.policy.archive_format}")
        
        logger.info(f"Created archive: {archive_path}")
        return archive_path
    
    def _remove_archived_observations(self, archived_obs: List[Dict[str, Any]]):
        """Remove archived observations from DCP.
        
        Args:
            archived_obs: Observations that were archived
        """
        try:
            # Get archived observation IDs
            archived_ids = {obs['id'] for obs in archived_obs}
            
            # Read current DCP
            dcp_data = self.dcp_manager.read_dcp()
            
            # Filter out archived observations
            remaining_obs = [
                obs for obs in dcp_data.get('observations', [])
                if obs['id'] not in archived_ids
            ]
            
            # Update DCP
            dcp_data['observations'] = remaining_obs
            
            # Write back
            self.dcp_manager.write_dcp(dcp_data)
            
            logger.info(f"Removed {len(archived_ids)} archived observations from DCP")
            
        except Exception as e:
            logger.error(f"Failed to remove archived observations: {e}")
            raise
    
    def restore_from_archive(self, archive_path: Path) -> int:
        """Restore observations from an archive file.
        
        Args:
            archive_path: Path to archive file
            
        Returns:
            Number of observations restored
        """
        try:
            # Read archive
            if archive_path.suffix == '.gz':
                with gzip.open(archive_path, 'rt', encoding='utf-8') as f:
                    archive_data = json.load(f)
            else:
                with open(archive_path) as f:
                    archive_data = json.load(f)
            
            # Get observations
            observations = archive_data.get('observations', [])
            
            if not observations:
                logger.warning(f"No observations found in archive: {archive_path}")
                return 0
            
            # Add observations back to DCP
            for obs in observations:
                # Remove internal fields
                obs_data = {
                    'type': obs.get('type'),
                    'priority': obs.get('priority', 50),
                    'summary': obs.get('summary', ''),
                    'details': obs.get('data', obs.get('details', {}))
                }
                
                self.dcp_manager.add_observation(
                    obs_data,
                    source_agent=obs.get('source_agent', 'archive_restore')
                )
            
            logger.info(f"Restored {len(observations)} observations from {archive_path}")
            return len(observations)
            
        except Exception as e:
            logger.error(f"Failed to restore from archive: {e}")
            raise
    
    def get_archives(self) -> List[Dict[str, Any]]:
        """Get list of available archives.
        
        Returns:
            List of archive information
        """
        archives = []
        
        for archive_file in self.policy.archive_path.glob("dcp_archive_*.json*"):
            try:
                stat = archive_file.stat()
                archives.append({
                    'filename': archive_file.name,
                    'path': str(archive_file),
                    'size_mb': stat.st_size / (1024 * 1024),
                    'created': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'format': 'gzip' if archive_file.suffix == '.gz' else 'json'
                })
            except Exception as e:
                logger.error(f"Error reading archive {archive_file}: {e}")
        
        # Sort by creation date (newest first)
        archives.sort(key=lambda x: x['created'], reverse=True)
        
        return archives
    
    def get_status(self) -> Dict[str, Any]:
        """Get archive service status.
        
        Returns:
            Service status and statistics
        """
        return {
            'enabled': self.policy.enabled,
            'running': self._archive_thread and self._archive_thread.is_alive(),
            'last_archive': self._last_archive.isoformat() if self._last_archive else None,
            'next_scheduled': self._get_next_scheduled_time().isoformat(),
            'policy': {
                'default_retention_days': self.policy.default_retention_days,
                'size_threshold_mb': self.policy.size_threshold_mb,
                'observation_threshold': self.policy.observation_count_threshold,
                'schedule': f"{self.policy.schedule_hour:02d}:{self.policy.schedule_minute:02d}"
            },
            'statistics': self.stats,
            'archives_available': len(self.get_archives())
        }
    
    def _get_next_scheduled_time(self) -> datetime:
        """Get next scheduled archive time."""
        now = datetime.now()
        scheduled = now.replace(
            hour=self.policy.schedule_hour,
            minute=self.policy.schedule_minute,
            second=0,
            microsecond=0
        )
        
        if scheduled <= now:
            # Next day
            scheduled += timedelta(days=1)
            
        return scheduled