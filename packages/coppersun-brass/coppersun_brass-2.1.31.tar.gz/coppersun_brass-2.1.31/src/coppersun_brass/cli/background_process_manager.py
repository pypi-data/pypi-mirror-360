"""
Background Process Manager for Copper Sun Brass
Handles subprocess-based background monitoring to prevent CLI hanging.
"""

import subprocess
import sys
import os
import logging
import time
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)


class BackgroundProcessManager:
    """Manages subprocess-based background monitoring to prevent CLI hanging.
    
    This solves the critical issue where brass init hangs indefinitely due to
    blocking infinite loops in the scheduler. Uses subprocess.Popen() to run
    monitoring in a separate process, allowing brass init to return immediately.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        
    def _get_correct_python_executable(self):
        """Get the correct Python executable with coppersun_brass module available."""
        import shutil
        
        # First priority: Try to find pipx installation of coppersun-brass
        pipx_venv = Path.home() / '.local/pipx/venvs/coppersun-brass/bin/python'
        if pipx_venv.exists():
            return str(pipx_venv)
            
        # Second priority: Check if we're running from pipx environment
        current_python = sys.executable
        if '.local/pipx/venvs' in current_python:
            return current_python
        
        # Third priority: Check for __PYVENV_LAUNCHER__ environment variable (macOS)
        if '__PYVENV_LAUNCHER__' in os.environ:
            pipx_python = os.environ['__PYVENV_LAUNCHER__']
            if Path(pipx_python).exists():
                return pipx_python
        
        # Fourth priority: Try current sys.executable if it has the module
        try:
            result = subprocess.run([
                current_python, '-c', 'import coppersun_brass'
            ], capture_output=True, timeout=5)
            if result.returncode == 0:
                return current_python
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Last resort: Fallback to sys.executable (might not work but better than nothing)
        return sys.executable
    
    def _cleanup_stale_pid_files(self):
        """Clean up stale PID files from dead processes."""
        try:
            pid_file = self.project_root / ".brass" / "monitoring.pid"
            if pid_file.exists():
                pid = int(pid_file.read_text().strip())
                
                # Check if process is actually running
                running = False
                if sys.platform == "win32":
                    result = subprocess.run([
                        "tasklist", "/FI", f"PID eq {pid}"
                    ], capture_output=True, text=True)
                    running = str(pid) in result.stdout
                else:
                    try:
                        os.kill(pid, 0)  # Send signal 0 to check if process exists
                        running = True
                    except OSError:
                        running = False
                
                # If process is not running, remove stale PID file
                if not running:
                    pid_file.unlink(missing_ok=True)
                    logger.info(f"Cleaned up stale PID file for process {pid}")
                    
        except (ValueError, FileNotFoundError, PermissionError) as e:
            # If we can't read/parse PID file, just remove it
            pid_file = self.project_root / ".brass" / "monitoring.pid"
            pid_file.unlink(missing_ok=True)
            logger.warning(f"Removed invalid PID file: {e}")
        except Exception as e:
            logger.warning(f"Error cleaning up PID files: {e}")
    
    def start_background_process(self) -> Tuple[bool, str]:
        """Start background monitoring process if not already running."""
        # Check if already running first (idempotent behavior)
        if self.is_background_running():
            pid_file = self.project_root / ".brass" / "monitoring.pid"
            pid = pid_file.read_text().strip() if pid_file.exists() else "unknown"
            return True, f"Background monitoring already running (PID: {pid})"
        
        # Clean up any stale PID files
        self._cleanup_stale_pid_files()
        
        try:
            # Cross-platform process creation
            kwargs = {}
            
            if sys.platform == "win32":
                # Windows: Create detached process
                kwargs['creationflags'] = subprocess.DETACHED_PROCESS
            else:
                # Unix: New session
                kwargs['start_new_session'] = True
            
            # Ensure log directory exists
            log_dir = self.project_root / ".brass"
            log_dir.mkdir(exist_ok=True)
            
            # Get the correct Python executable
            python_exec = self._get_correct_python_executable()
            
            # Build command to start background monitoring
            # The brass CLI doesn't have a 'start' command, so always use python -m coppersun_brass
            cmd = [
                python_exec, '-m', 'coppersun_brass', 'start',
                '--mode', 'adaptive',
                '--daemon',
                '--project', str(self.project_root)
            ]
            
            # Start background process with proper file handle management
            # Separate log files for monitoring vs background process management
            stdout_file = None
            stderr_file = None
            
            try:
                stdout_file = open(log_dir / "monitoring.log", "w")
                stderr_file = open(log_dir / "monitoring.error.log", "w")
                
                process = subprocess.Popen(cmd,
                    stdout=stdout_file,
                    stderr=stderr_file,
                    stdin=subprocess.DEVNULL,
                    **kwargs
                )
            except Exception as e:
                # Ensure files are closed if process creation fails
                if stdout_file:
                    stdout_file.close()
                if stderr_file:
                    stderr_file.close()
                raise e
            
            # Give it time to start (with timeout)
            max_wait = 10
            wait_time = 0.5
            for _ in range(int(max_wait / wait_time)):
                time.sleep(wait_time)
                if process.poll() is None:
                    break
                if process.poll() is not None:
                    # Process died early, check logs
                    break
            
            # Check if it's still running
            if process.poll() is None:
                # Store PID for later reference
                pid_file = log_dir / "monitoring.pid"
                pid_file.write_text(str(process.pid))
                
                return True, f"Background monitoring started (PID: {process.pid})"
            else:
                # Process failed to start, get error details
                if stderr_file:
                    stderr_file.close()
                if stdout_file:
                    stdout_file.close()
                    
                error_log = log_dir / "monitoring.error.log"
                if error_log.exists() and error_log.stat().st_size > 0:
                    error_msg = error_log.read_text()[:200]  # First 200 chars
                    return False, f"Background monitoring failed to start: {error_msg}"
                return False, "Background monitoring failed to start (check logs)"
                
        except FileNotFoundError as e:
            logger.error(f"Python executable not found: {e}")
            return False, f"Python executable not found: {str(e)}"
        except PermissionError as e:
            logger.error(f"Permission denied: {e}")
            return False, f"Permission denied: {str(e)}"
        except Exception as e:
            logger.error(f"Failed to start background process: {e}")
            return False, f"Background process start failed: {str(e)}"
    
    def is_background_running(self) -> bool:
        """Check if background process is running."""
        try:
            pid_file = self.project_root / ".brass" / "monitoring.pid"
            if not pid_file.exists():
                return False
            
            pid = int(pid_file.read_text().strip())
            
            # Check if process is still running
            if sys.platform == "win32":
                result = subprocess.run([
                    "tasklist", "/FI", f"PID eq {pid}"
                ], capture_output=True, text=True)
                return str(pid) in result.stdout
            else:
                try:
                    os.kill(pid, 0)  # Send signal 0 to check if process exists
                    return True
                except OSError:
                    return False
                    
        except Exception:
            return False
    
    def stop_background_process(self) -> Tuple[bool, str]:
        """Stop background process with enhanced error handling."""
        try:
            pid_file = self.project_root / ".brass" / "monitoring.pid"
            if not pid_file.exists():
                return True, "No background process found"
            
            try:
                pid = int(pid_file.read_text().strip())
            except (ValueError, FileNotFoundError):
                # Invalid or missing PID file
                pid_file.unlink(missing_ok=True)
                return True, "Removed invalid PID file"
            
            # Check if process is actually running first
            process_running = False
            if sys.platform == "win32":
                result = subprocess.run([
                    "tasklist", "/FI", f"PID eq {pid}"
                ], capture_output=True, text=True)
                process_running = str(pid) in result.stdout
            else:
                try:
                    os.kill(pid, 0)  # Send signal 0 to check if process exists
                    process_running = True
                except OSError:
                    process_running = False
            
            if not process_running:
                # Process already dead, just clean up PID file
                pid_file.unlink(missing_ok=True)
                return True, f"Process {pid} already stopped, cleaned up PID file"
            
            # Attempt graceful shutdown first, then force kill
            success = False
            if sys.platform == "win32":
                # Try graceful shutdown first
                result = subprocess.run([
                    "taskkill", "/PID", str(pid)
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    # Force kill if graceful shutdown failed
                    result = subprocess.run([
                        "taskkill", "/PID", str(pid), "/F"
                    ], capture_output=True, text=True)
                
                success = result.returncode == 0
                if not success:
                    logger.warning(f"Windows taskkill failed: {result.stderr}")
            else:
                try:
                    # Try SIGTERM first (graceful)
                    os.kill(pid, 15)  # SIGTERM
                    
                    # Wait up to 5 seconds for graceful shutdown
                    for _ in range(10):
                        time.sleep(0.5)
                        try:
                            os.kill(pid, 0)  # Check if still running
                        except OSError:
                            # Process is dead
                            success = True
                            break
                    
                    # If still running, force kill
                    if not success:
                        os.kill(pid, 9)   # SIGKILL
                        success = True
                        
                except OSError as e:
                    if e.errno == 3:  # No such process
                        success = True
                    else:
                        logger.warning(f"Failed to kill process {pid}: {e}")
                        success = False
            
            # Clean up PID file regardless of kill success
            pid_file.unlink(missing_ok=True)
            
            if success:
                return True, f"Background process {pid} stopped"
            else:
                return False, f"Failed to stop process {pid} (cleaned up PID file)"
            
        except PermissionError as e:
            logger.error(f"Permission denied stopping process: {e}")
            return False, f"Permission denied: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error stopping process: {e}")
            return False, f"Failed to stop background process: {str(e)}"