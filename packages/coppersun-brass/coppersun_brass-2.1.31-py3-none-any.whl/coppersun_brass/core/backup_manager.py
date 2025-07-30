"""Backup and restore manager for Copper Alloy Brass SQLite database.

This module provides automated backup functionality with retention policies
and point-in-time restore capabilities for production deployments.
"""

import os
import time
import shutil
import sqlite3
import logging
import threading
import gzip
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BackupInfo:
    """Information about a backup file."""
    path: Path
    timestamp: float
    size_bytes: int
    compressed: bool
    version: str
    
    @property
    def age_days(self) -> float:
        """Get age of backup in days."""
        return (time.time() - self.timestamp) / 86400
        
    @property
    def size_mb(self) -> float:
        """Get size in megabytes."""
        return self.size_bytes / (1024 * 1024)


class BackupManager:
    """Manages database backups with retention and restore capabilities."""
    
    def __init__(self, 
                 db_path: str,
                 backup_dir: str,
                 retention_days: int = 30,
                 max_backups: int = 168,
                 compress: bool = True):
        """Initialize backup manager.
        
        Args:
            db_path: Path to SQLite database
            backup_dir: Directory to store backups
            retention_days: Days to retain backups
            max_backups: Maximum number of backups to keep
            compress: Whether to compress backups
        """
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.retention_days = retention_days
        self.max_backups = max_backups
        self.compress = compress
        
        # Create backup directory if needed
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Background backup thread
        self._backup_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._backup_interval = 3600  # Default 1 hour
        
    def create_backup(self, description: str = "") -> BackupInfo:
        """Create a new backup of the database.
        
        Args:
            description: Optional description for the backup
            
        Returns:
            BackupInfo object with backup details
        """
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
            
        # Generate backup filename
        timestamp = datetime.now()
        filename = f"brass_backup_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        if description:
            # Sanitize description for filename
            safe_desc = "".join(c for c in description if c.isalnum() or c in ('-', '_'))[:50]
            filename += f"_{safe_desc}"
            
        if self.compress:
            filename += ".db.gz"
        else:
            filename += ".db"
            
        backup_path = self.backup_dir / filename
        
        try:
            # Create backup
            if self.compress:
                self._create_compressed_backup(backup_path)
            else:
                self._create_uncompressed_backup(backup_path)
                
            # Get backup info
            stat = backup_path.stat()
            info = BackupInfo(
                path=backup_path,
                timestamp=stat.st_mtime,
                size_bytes=stat.st_size,
                compressed=self.compress,
                version=self._get_db_version()
            )
            
            logger.info(f"Created backup: {backup_path.name} ({info.size_mb:.1f}MB)")
            
            # Clean old backups
            self._cleanup_old_backups()
            
            return info
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            # Clean up partial backup
            if backup_path.exists():
                backup_path.unlink()
            raise
            
    def _create_compressed_backup(self, backup_path: Path) -> None:
        """Create compressed backup using gzip."""
        # Use SQLite backup API for consistency
        source_conn = sqlite3.connect(self.db_path)
        
        # Create temporary uncompressed backup
        temp_path = backup_path.with_suffix('')
        
        try:
            # Backup to temporary file
            backup_conn = sqlite3.connect(temp_path)
            source_conn.backup(backup_conn)
            backup_conn.close()
            source_conn.close()
            
            # Compress the backup
            with open(temp_path, 'rb') as f_in:
                with gzip.open(backup_path, 'wb', compresslevel=6) as f_out:
                    shutil.copyfileobj(f_in, f_out)
                    
            # Remove temporary file
            temp_path.unlink()
            
        except Exception:
            # Clean up on error
            if temp_path.exists():
                temp_path.unlink()
            raise
            
    def _create_uncompressed_backup(self, backup_path: Path) -> None:
        """Create uncompressed backup."""
        # Use SQLite backup API for consistency
        source_conn = sqlite3.connect(self.db_path)
        backup_conn = sqlite3.connect(backup_path)
        
        try:
            source_conn.backup(backup_conn)
        finally:
            backup_conn.close()
            source_conn.close()
            
    def restore_backup(self, backup_path: Path, verify: bool = True) -> None:
        """Restore database from backup.
        
        Args:
            backup_path: Path to backup file
            verify: Whether to verify backup before restore
        """
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")
            
        # Create restore point before overwriting
        logger.info(f"Creating restore point before restoring from {backup_path.name}")
        try:
            restore_point = self.create_backup("pre_restore")
            logger.info(f"Restore point created: {restore_point.path.name}")
        except Exception as e:
            logger.warning(f"Could not create restore point: {e}")
            
        try:
            # Verify backup if requested
            if verify:
                self._verify_backup(backup_path)
                
            # Restore based on compression
            if backup_path.suffix == '.gz':
                self._restore_compressed_backup(backup_path)
            else:
                self._restore_uncompressed_backup(backup_path)
                
            logger.info(f"Successfully restored from {backup_path.name}")
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise
            
    def _restore_compressed_backup(self, backup_path: Path) -> None:
        """Restore from compressed backup."""
        # Decompress to temporary file
        temp_path = self.db_path.with_suffix('.restore_tmp')
        
        try:
            with gzip.open(backup_path, 'rb') as f_in:
                with open(temp_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                    
            # Replace database file
            shutil.move(str(temp_path), str(self.db_path))
            
        except Exception:
            # Clean up on error
            if temp_path.exists():
                temp_path.unlink()
            raise
            
    def _restore_uncompressed_backup(self, backup_path: Path) -> None:
        """Restore from uncompressed backup."""
        # Copy backup over database
        shutil.copy2(backup_path, self.db_path)
        
    def _verify_backup(self, backup_path: Path) -> None:
        """Verify backup file integrity."""
        logger.info(f"Verifying backup: {backup_path.name}")
        
        # Check if file is readable
        if not backup_path.is_file():
            raise ValueError(f"Not a file: {backup_path}")
            
        # For compressed backups, test decompression
        if backup_path.suffix == '.gz':
            try:
                with gzip.open(backup_path, 'rb') as f:
                    # Read first chunk to verify
                    f.read(1024)
            except Exception as e:
                raise ValueError(f"Corrupt compressed backup: {e}")
        
        # For uncompressed, verify SQLite format
        else:
            try:
                conn = sqlite3.connect(f"file:{backup_path}?mode=ro", uri=True)
                # Run integrity check
                cursor = conn.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                conn.close()
                
                if result[0] != 'ok':
                    raise ValueError(f"SQLite integrity check failed: {result[0]}")
                    
            except Exception as e:
                raise ValueError(f"Invalid SQLite backup: {e}")
                
        logger.info("Backup verification passed")
        
    def list_backups(self) -> List[BackupInfo]:
        """List all available backups, sorted by age (newest first)."""
        backups = []
        
        for path in self.backup_dir.glob("brass_backup_*.db*"):
            try:
                stat = path.stat()
                info = BackupInfo(
                    path=path,
                    timestamp=stat.st_mtime,
                    size_bytes=stat.st_size,
                    compressed=path.suffix == '.gz',
                    version=self._extract_version_from_backup(path)
                )
                backups.append(info)
            except Exception as e:
                logger.warning(f"Could not read backup {path}: {e}")
                
        # Sort by timestamp, newest first
        backups.sort(key=lambda b: b.timestamp, reverse=True)
        
        return backups
        
    def _cleanup_old_backups(self) -> None:
        """Remove old backups based on retention policy."""
        backups = self.list_backups()
        
        if not backups:
            return
            
        # Remove by age
        cutoff_time = time.time() - (self.retention_days * 86400)
        to_remove = [b for b in backups if b.timestamp < cutoff_time]
        
        # Remove by count (keep most recent)
        if len(backups) > self.max_backups:
            excess_count = len(backups) - self.max_backups
            to_remove.extend(backups[-excess_count:])
            
        # Remove duplicates and delete
        to_remove = list(set(to_remove))
        for backup in to_remove:
            try:
                backup.path.unlink()
                logger.info(f"Removed old backup: {backup.path.name}")
            except Exception as e:
                logger.warning(f"Could not remove backup {backup.path}: {e}")
                
    def start_automatic_backups(self, interval_seconds: int = 3600) -> None:
        """Start automatic backup thread.
        
        Args:
            interval_seconds: Seconds between backups
        """
        if self._backup_thread and self._backup_thread.is_alive():
            logger.warning("Automatic backups already running")
            return
            
        self._backup_interval = interval_seconds
        self._stop_event.clear()
        
        self._backup_thread = threading.Thread(
            target=self._backup_loop,
            name="Copper Alloy Brass-Backup",
            daemon=True
        )
        self._backup_thread.start()
        
        logger.info(f"Started automatic backups every {interval_seconds}s")
        
    def stop_automatic_backups(self) -> None:
        """Stop automatic backup thread."""
        if not self._backup_thread or not self._backup_thread.is_alive():
            return
            
        logger.info("Stopping automatic backups")
        self._stop_event.set()
        self._backup_thread.join(timeout=5)
        
    def _backup_loop(self) -> None:
        """Background backup loop."""
        while not self._stop_event.is_set():
            try:
                # Wait for interval or stop event
                if self._stop_event.wait(self._backup_interval):
                    break  # Stop requested
                    
                # Create automatic backup
                self.create_backup("auto")
                
            except Exception as e:
                logger.error(f"Automatic backup failed: {e}")
                
    def _get_db_version(self) -> str:
        """Get database schema version."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("PRAGMA user_version")
            version = cursor.fetchone()[0]
            conn.close()
            return str(version)
        except Exception:
            return "unknown"
            
    def _extract_version_from_backup(self, backup_path: Path) -> str:
        """Extract version from backup filename or metadata."""
        # For now, return unknown - could be enhanced to read from backup
        return "unknown"
        
    def get_backup_summary(self) -> Dict[str, Any]:
        """Get summary of backup status."""
        backups = self.list_backups()
        
        if not backups:
            return {
                "total_backups": 0,
                "total_size_mb": 0,
                "oldest_backup": None,
                "newest_backup": None,
                "average_size_mb": 0
            }
            
        total_size = sum(b.size_bytes for b in backups)
        
        return {
            "total_backups": len(backups),
            "total_size_mb": total_size / (1024 * 1024),
            "oldest_backup": {
                "name": backups[-1].path.name,
                "age_days": backups[-1].age_days,
                "size_mb": backups[-1].size_mb
            },
            "newest_backup": {
                "name": backups[0].path.name,
                "age_days": backups[0].age_days,
                "size_mb": backups[0].size_mb
            },
            "average_size_mb": (total_size / len(backups)) / (1024 * 1024)
        }