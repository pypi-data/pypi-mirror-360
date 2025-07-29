"""
Cross-platform OS-level file locking for production safety
Prevents file corruption in multi-instance Copper Alloy Brass deployments
"""

import os
import time
import threading
import platform
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import contextmanager
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Platform-specific imports
if platform.system() == 'Windows':
    import msvcrt
else:
    import fcntl

class FileLockError(Exception):
    """Base exception for file locking errors"""
    pass

class FileLockTimeout(FileLockError):
    """Raised when lock acquisition times out"""
    pass

class FileLockCorrupted(FileLockError):
    """Raised when lock file appears corrupted"""
    pass

class CrossPlatformFileLock:
    """
    Cross-platform OS-level file locking for production safety.
    
    Prevents data corruption when multiple Copper Alloy Brass instances access the same files.
    Uses advisory locking on Unix and exclusive locking on Windows.
    """
    
    def __init__(self, file_path: Path, timeout: float = 30.0, 
                 lock_dir: Optional[Path] = None):
        """
        Initialize file lock.
        
        Args:
            file_path: Path to the file to lock
            timeout: Maximum time to wait for lock acquisition
            lock_dir: Directory for lock files (defaults to file's parent)
        """
        self.file_path = Path(file_path).resolve()
        self.timeout = timeout
        
        # Determine lock file location
        if lock_dir:
            self.lock_dir = Path(lock_dir)
            self.lock_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.lock_dir = self.file_path.parent
            
        # Lock file name includes file hash to avoid conflicts
        import hashlib
        file_hash = hashlib.md5(str(self.file_path).encode()).hexdigest()[:8]
        self.lock_file = self.lock_dir / f".{self.file_path.name}.{file_hash}.lock"
        
        # Lock state
        self._lock_fd: Optional[int] = None
        self._acquired = False
        self._lock_info: Optional[Dict[str, Any]] = None
        self._acquisition_time: Optional[datetime] = None
        
    def __enter__(self):
        """Context manager entry - acquire lock"""
        self.acquire()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - release lock"""
        self.release()
        
    def acquire(self, blocking: bool = True) -> bool:
        """
        Acquire the file lock.
        
        Args:
            blocking: If True, wait for lock. If False, return immediately.
            
        Returns:
            True if lock acquired, False if not (non-blocking mode only)
            
        Raises:
            FileLockTimeout: If lock cannot be acquired within timeout
            FileLockError: If lock acquisition fails
        """
        if self._acquired:
            logger.warning(f"Lock already acquired for {self.file_path}")
            return True
            
        start_time = time.time()
        
        while True:
            try:
                success = self._attempt_lock_acquisition()
                if success:
                    self._acquired = True
                    self._acquisition_time = datetime.now()
                    
                    # Write lock info for debugging
                    self._write_lock_info()
                    
                    logger.debug(f"Acquired lock for {self.file_path}")
                    return True
                    
            except Exception as e:
                if self._lock_fd is not None:
                    try:
                        os.close(self._lock_fd)
                    except OSError:
                        pass
                    self._lock_fd = None
                raise FileLockError(f"Lock acquisition failed: {e}")
            
            # Check timeout
            if not blocking:
                return False
                
            elapsed = time.time() - start_time
            if elapsed >= self.timeout:
                raise FileLockTimeout(
                    f"Could not acquire lock for {self.file_path} within {self.timeout}s"
                )
                
            # Check if lock is stale
            if self._is_lock_stale():
                logger.warning(f"Detected stale lock for {self.file_path}, attempting cleanup")
                self._cleanup_stale_lock()
            
            # Wait briefly before retry
            time.sleep(0.1)
    
    def _attempt_lock_acquisition(self) -> bool:
        """Attempt to acquire the lock (platform-specific)"""
        try:
            # Open lock file
            self._lock_fd = os.open(
                self.lock_file, 
                os.O_CREAT | os.O_WRONLY | os.O_TRUNC,
                0o600  # rw-------
            )
            
            if platform.system() == 'Windows':
                return self._acquire_windows_lock()
            else:
                return self._acquire_unix_lock()
                
        except OSError as e:
            if self._lock_fd is not None:
                try:
                    os.close(self._lock_fd)
                except OSError:
                    pass
                self._lock_fd = None
            
            # EACCES/EAGAIN means another process has the lock
            if e.errno in (13, 11):  # EACCES, EAGAIN
                return False
            raise
    
    def _acquire_windows_lock(self) -> bool:
        """Acquire lock on Windows using msvcrt"""
        try:
            msvcrt.locking(self._lock_fd, msvcrt.LK_NBLCK, 1)
            return True
        except OSError:
            return False
    
    def _acquire_unix_lock(self) -> bool:
        """Acquire lock on Unix using fcntl"""
        try:
            fcntl.flock(self._lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except (OSError, IOError):
            return False
    
    def _write_lock_info(self):
        """Write lock information to lock file for debugging"""
        if self._lock_fd is None:
            return
            
        self._lock_info = {
            'pid': os.getpid(),
            'hostname': platform.node(),
            'acquired_at': datetime.now().isoformat(),
            'file_path': str(self.file_path),
            'platform': platform.system(),
            'python_version': platform.python_version()
        }
        
        try:
            import json
            lock_data = json.dumps(self._lock_info, indent=2).encode('utf-8')
            os.write(self._lock_fd, lock_data)
            os.fsync(self._lock_fd)  # Force write to disk
        except Exception as e:
            logger.warning(f"Failed to write lock info: {e}")
    
    def _is_lock_stale(self) -> bool:
        """Check if lock file appears stale"""
        if not self.lock_file.exists():
            return False
            
        try:
            # Check file age
            lock_mtime = datetime.fromtimestamp(self.lock_file.stat().st_mtime)
            age = datetime.now() - lock_mtime
            
            # Locks older than 1 hour are suspicious
            if age > timedelta(hours=1):
                return True
                
            # Try to read lock info
            with open(self.lock_file, 'r') as f:
                content = f.read()
                
            if not content.strip():
                return True  # Empty lock file
                
            import json
            lock_info = json.loads(content)
            
            # Check if process still exists (Unix only)
            if platform.system() != 'Windows':
                pid = lock_info.get('pid')
                if pid and not self._is_process_running(pid):
                    return True
                    
            return False
            
        except Exception as e:
            logger.warning(f"Error checking lock staleness: {e}")
            return False
    
    def _is_process_running(self, pid: int) -> bool:
        """Check if process is still running (Unix only)"""
        try:
            os.kill(pid, 0)  # Send signal 0 to check if process exists
            return True
        except OSError:
            return False
    
    def _cleanup_stale_lock(self):
        """Clean up stale lock file"""
        try:
            if self.lock_file.exists():
                self.lock_file.unlink()
                logger.info(f"Cleaned up stale lock file: {self.lock_file}")
        except Exception as e:
            logger.warning(f"Failed to cleanup stale lock: {e}")
    
    def release(self):
        """Release the file lock"""
        if not self._acquired:
            return
            
        try:
            if self._lock_fd is not None:
                # Release platform-specific lock
                if platform.system() == 'Windows':
                    try:
                        msvcrt.locking(self._lock_fd, msvcrt.LK_UNLCK, 1)
                    except OSError:
                        pass
                else:
                    try:
                        fcntl.flock(self._lock_fd, fcntl.LOCK_UN)
                    except (OSError, IOError):
                        pass
                
                # Close file descriptor
                try:
                    os.close(self._lock_fd)
                except OSError:
                    pass
                    
                self._lock_fd = None
            
            # Remove lock file
            try:
                if self.lock_file.exists():
                    self.lock_file.unlink()
            except OSError as e:
                logger.warning(f"Failed to remove lock file {self.lock_file}: {e}")
            
            self._acquired = False
            self._acquisition_time = None
            logger.debug(f"Released lock for {self.file_path}")
            
        except Exception as e:
            logger.error(f"Error releasing lock for {self.file_path}: {e}")
            # Don't re-raise - best effort cleanup
    
    def is_locked(self) -> bool:
        """Check if this lock is currently held"""
        return self._acquired
    
    def get_lock_info(self) -> Optional[Dict[str, Any]]:
        """Get information about current lock"""
        if not self._acquired:
            return None
            
        info = self._lock_info.copy() if self._lock_info else {}
        if self._acquisition_time:
            info['duration_seconds'] = (datetime.now() - self._acquisition_time).total_seconds()
            
        return info


class FileLockManager:
    """
    Manager for multiple file locks with deadlock prevention.
    
    Ensures consistent lock ordering to prevent deadlocks when multiple
    files need to be locked simultaneously.
    """
    
    def __init__(self):
        self._locks: Dict[str, CrossPlatformFileLock] = {}
        self._lock_order: Dict[str, int] = {}
        self._global_lock = threading.Lock()
        
    def get_lock(self, file_path: Path, timeout: float = 30.0) -> CrossPlatformFileLock:
        """Get or create a lock for the specified file"""
        file_key = str(file_path.resolve())
        
        with self._global_lock:
            if file_key not in self._locks:
                self._locks[file_key] = CrossPlatformFileLock(file_path, timeout)
                # Assign lock order based on string sorting for consistent ordering
                self._lock_order[file_key] = hash(file_key) % (2**31)
                
            return self._locks[file_key]
    
    @contextmanager
    def lock_multiple(self, file_paths: list[Path], timeout: float = 30.0):
        """
        Lock multiple files in a consistent order to prevent deadlocks.
        
        Args:
            file_paths: List of file paths to lock
            timeout: Timeout for each individual lock
        """
        # Get locks and sort by order to prevent deadlocks
        locks_with_order = []
        for file_path in file_paths:
            lock = self.get_lock(file_path, timeout)
            file_key = str(file_path.resolve())
            order = self._lock_order[file_key]
            locks_with_order.append((order, lock))
        
        # Sort by order
        locks_with_order.sort(key=lambda x: x[0])
        sorted_locks = [lock for _, lock in locks_with_order]
        
        # Acquire locks in order
        acquired_locks = []
        try:
            for lock in sorted_locks:
                lock.acquire()
                acquired_locks.append(lock)
            
            yield
            
        finally:
            # Release in reverse order
            for lock in reversed(acquired_locks):
                try:
                    lock.release()
                except Exception as e:
                    logger.error(f"Error releasing lock: {e}")
    
    def cleanup_stale_locks(self, max_age_hours: float = 1.0):
        """Clean up stale lock files"""
        cleaned = 0
        
        for file_key, lock in self._locks.items():
            if lock.lock_file.exists():
                try:
                    lock_mtime = datetime.fromtimestamp(lock.lock_file.stat().st_mtime)
                    age = datetime.now() - lock_mtime
                    
                    if age > timedelta(hours=max_age_hours):
                        if lock._is_lock_stale():
                            lock._cleanup_stale_lock()
                            cleaned += 1
                            
                except Exception as e:
                    logger.warning(f"Error checking lock {file_key}: {e}")
        
        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} stale lock files")
        
        return cleaned
    
    def get_stats(self) -> Dict[str, Any]:
        """Get lock manager statistics"""
        active_locks = sum(1 for lock in self._locks.values() if lock.is_locked())
        
        return {
            'total_locks': len(self._locks),
            'active_locks': active_locks,
            'lock_files': [
                {
                    'file_path': str(lock.file_path),
                    'lock_file': str(lock.lock_file),
                    'is_locked': lock.is_locked(),
                    'lock_info': lock.get_lock_info()
                }
                for lock in self._locks.values()
            ]
        }


# Global lock manager instance
_global_lock_manager: Optional[FileLockManager] = None
_global_lock_manager_lock = threading.Lock()

def get_file_lock_manager() -> FileLockManager:
    """Get the global file lock manager (thread-safe singleton)"""
    global _global_lock_manager
    
    if _global_lock_manager is not None:
        return _global_lock_manager
    
    with _global_lock_manager_lock:
        if _global_lock_manager is None:
            _global_lock_manager = FileLockManager()
        return _global_lock_manager

@contextmanager
def safe_file_operation(file_path: Path, timeout: float = 30.0):
    """
    Context manager for safe file operations with OS-level locking.
    
    Usage:
        with safe_file_operation(Path("important_file.json")) as lock:
            # Perform file operations here
            # File is protected by OS-level lock
            pass
    """
    manager = get_file_lock_manager()
    lock = manager.get_lock(file_path, timeout)
    
    with lock:
        yield lock

# Export production classes
__all__ = [
    'CrossPlatformFileLock', 'FileLockManager', 'FileLockError', 
    'FileLockTimeout', 'FileLockCorrupted', 'get_file_lock_manager',
    'safe_file_operation'
]