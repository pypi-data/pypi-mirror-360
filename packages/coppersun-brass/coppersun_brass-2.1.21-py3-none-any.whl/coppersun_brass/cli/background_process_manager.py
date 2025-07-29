"""
Background Process Manager for Copper Sun Brass
Handles simple background process spawning as fallback.
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
    """Manages simple background process spawning."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        
    def _get_correct_python_executable(self):
        """Get the correct Python executable, preferring pipx environment."""
        import shutil
        
        # First, try to use the brass executable directly if available
        brass_executable = shutil.which('brass')
        if brass_executable:
            return 'brass_direct'
            
        # Check if we're running from pipx by looking at executable path
        current_python = sys.executable
        if '.local/pipx/venvs' in current_python:
            return current_python
            
        # Try to find pipx installation of copper sun brass
        pipx_venv = Path.home() / '.local/pipx/venvs/coppersun-brass/bin/python'
        if pipx_venv.exists():
            return str(pipx_venv)
        
        # Check for __PYVENV_LAUNCHER__ environment variable (macOS)
        if '__PYVENV_LAUNCHER__' in os.environ:
            pipx_python = os.environ['__PYVENV_LAUNCHER__']
            if Path(pipx_python).exists():
                return pipx_python
        
        # Fallback to sys.executable
        return sys.executable
    
    def start_background_process(self) -> Tuple[bool, str]:
        """Start simple background process."""
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
            
            # Build command based on detected executable
            if python_exec == 'brass_direct':
                cmd = [
                    'brass', 'start',
                    '--mode', 'adaptive', 
                    '--project', str(self.project_root)
                ]
            else:
                cmd = [
                    python_exec, '-m', 'coppersun_brass', 'start',
                    '--mode', 'adaptive',
                    '--project', str(self.project_root)
                ]
            
            # Start background process with proper file handle management
            stdout_file = open(log_dir / "background.log", "w")
            stderr_file = open(log_dir / "background.error.log", "w")
            
            try:
                process = subprocess.Popen(cmd,
                stdout=stdout_file,
                stderr=stderr_file,
                stdin=subprocess.DEVNULL,
                **kwargs
                )
            except Exception:
                # Ensure files are closed if process creation fails
                stdout_file.close()
                stderr_file.close()
                raise
            
            # Give it a moment to start
            time.sleep(2)
            
            # Check if it's still running
            if process.poll() is None:
                # Store PID for later reference
                pid_file = log_dir / "background.pid"
                pid_file.write_text(str(process.pid))
                
                return True, f"Background process started (PID: {process.pid})"
            else:
                return False, "Background process failed to start"
                
        except Exception as e:
            logger.error(f"Failed to start background process: {e}")
            return False, f"Background process start failed: {str(e)}"
    
    def is_background_running(self) -> bool:
        """Check if background process is running."""
        try:
            pid_file = self.project_root / ".brass" / "background.pid"
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
        """Stop background process."""
        try:
            pid_file = self.project_root / ".brass" / "background.pid"
            if not pid_file.exists():
                return True, "No background process found"
            
            pid = int(pid_file.read_text().strip())
            
            # Kill process
            if sys.platform == "win32":
                result = subprocess.run([
                    "taskkill", "/PID", str(pid), "/F"
                ], capture_output=True, text=True)
                success = result.returncode == 0
            else:
                try:
                    os.kill(pid, 15)  # SIGTERM
                    time.sleep(2)
                    os.kill(pid, 9)   # SIGKILL if still running
                    success = True
                except OSError:
                    success = True  # Process already dead
            
            # Clean up PID file
            pid_file.unlink(missing_ok=True)
            
            return success, "Background process stopped"
            
        except Exception as e:
            return False, f"Failed to stop background process: {str(e)}"