"""
System Service Manager for Copper Sun Brass
Handles cross-platform system service installation and management.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
import json
import hashlib

logger = logging.getLogger(__name__)


class SystemServiceManager:
    """Manages system service installation across platforms."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.project_hash = hashlib.md5(str(self.project_root).encode()).hexdigest()[:8]
        self.service_name = f"brass-{self.project_hash}"
        
    def install_service(self) -> Tuple[bool, str]:
        """Install system service for automatic startup."""
        try:
            if sys.platform == "darwin":
                return self._install_macos_service()
            elif sys.platform.startswith("linux"):
                return self._install_linux_service()
            elif sys.platform == "win32":
                return self._install_windows_service()
            else:
                return False, f"Unsupported platform: {sys.platform}"
        except PermissionError:
            return False, "Administrator privileges required for system service installation"
        except Exception as e:
            return False, f"Service installation failed: {str(e)}"
    
    def _install_macos_service(self) -> Tuple[bool, str]:
        """Install macOS launchd service."""
        # Create service directory
        service_dir = Path.home() / "Library" / "LaunchAgents"
        service_dir.mkdir(parents=True, exist_ok=True)
        
        # Service file path
        service_file = service_dir / f"com.coppersun.brass.{self.project_hash}.plist"
        
        # Create plist content
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.coppersun.brass.{self.project_hash}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>-m</string>
        <string>coppersun_brass</string>
        <string>start</string>
        <string>--mode</string>
        <string>adaptive</string>
        <string>--project</string>
        <string>{self.project_root}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{self.project_root}/.brass/service.log</string>
    <key>StandardErrorPath</key>
    <string>{self.project_root}/.brass/service.error.log</string>
    <key>WorkingDirectory</key>
    <string>{self.project_root}</string>
</dict>
</plist>'''
        
        # Write service file
        service_file.write_text(plist_content)
        
        # Load service
        result = subprocess.run([
            "launchctl", "load", str(service_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, f"macOS service installed: {self.service_name}"
        else:
            return False, f"launchctl load failed: {result.stderr}"
    
    def _install_linux_service(self) -> Tuple[bool, str]:
        """Install Linux systemd user service."""
        # Create service directory
        service_dir = Path.home() / ".config" / "systemd" / "user"
        service_dir.mkdir(parents=True, exist_ok=True)
        
        # Service file path
        service_file = service_dir / f"{self.service_name}.service"
        
        # Create service content
        service_content = f'''[Unit]
Description=Copper Sun Brass Intelligence for {self.project_root.name}
After=network.target

[Service]
Type=simple
ExecStart={sys.executable} -m coppersun_brass start --mode adaptive --project {self.project_root}
Restart=always
RestartSec=10
WorkingDirectory={self.project_root}
StandardOutput=file:{self.project_root}/.brass/service.log
StandardError=file:{self.project_root}/.brass/service.error.log

[Install]
WantedBy=default.target'''
        
        # Write service file
        service_file.write_text(service_content)
        
        # Reload systemd and enable service
        commands = [
            ["systemctl", "--user", "daemon-reload"],
            ["systemctl", "--user", "enable", f"{self.service_name}.service"],
            ["systemctl", "--user", "start", f"{self.service_name}.service"]
        ]
        
        for cmd in commands:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return False, f"systemctl command failed: {' '.join(cmd)} - {result.stderr}"
        
        return True, f"Linux systemd service installed: {self.service_name}"
    
    def _install_windows_service(self) -> Tuple[bool, str]:
        """Install Windows service using Task Scheduler."""
        try:
            # Use schtasks to create scheduled task
            task_name = f"CopperSunBrass-{self.project_hash}"
            
            # Create XML for task definition
            xml_content = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Copper Sun Brass Intelligence Monitoring</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>3</Count>
    </RestartOnFailure>
  </Settings>
  <Actions>
    <Exec>
      <Command>{sys.executable}</Command>
      <Arguments>-m coppersun_brass start --mode adaptive --project "{self.project_root}"</Arguments>
      <WorkingDirectory>{self.project_root}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''
            
            # Write XML to temp file
            xml_file = self.project_root / ".brass" / "task.xml"
            xml_file.write_text(xml_content, encoding='utf-16')
            
            # Create task
            result = subprocess.run([
                "schtasks", "/create", "/tn", task_name, "/xml", str(xml_file)
            ], capture_output=True, text=True)
            
            # Clean up temp file
            xml_file.unlink(missing_ok=True)
            
            if result.returncode == 0:
                # Start the task
                subprocess.run([
                    "schtasks", "/run", "/tn", task_name
                ], capture_output=True, text=True)
                
                return True, f"Windows task installed: {task_name}"
            else:
                return False, f"schtasks create failed: {result.stderr}"
                
        except Exception as e:
            return False, f"Windows service installation failed: {str(e)}"
    
    def is_service_running(self) -> bool:
        """Check if service is currently running."""
        try:
            if sys.platform == "darwin":
                result = subprocess.run([
                    "launchctl", "list", f"com.coppersun.brass.{self.project_hash}"
                ], capture_output=True, text=True)
                return result.returncode == 0
                
            elif sys.platform.startswith("linux"):
                result = subprocess.run([
                    "systemctl", "--user", "is-active", f"{self.service_name}.service"
                ], capture_output=True, text=True)
                return "active" in result.stdout
                
            elif sys.platform == "win32":
                result = subprocess.run([
                    "schtasks", "/query", "/tn", f"CopperSunBrass-{self.project_hash}"
                ], capture_output=True, text=True)
                return result.returncode == 0 and "Running" in result.stdout
                
        except Exception:
            pass
        
        return False
    
    def uninstall_service(self) -> Tuple[bool, str]:
        """Uninstall system service."""
        try:
            if sys.platform == "darwin":
                service_file = Path.home() / "Library" / "LaunchAgents" / f"com.coppersun.brass.{self.project_hash}.plist"
                if service_file.exists():
                    subprocess.run(["launchctl", "unload", str(service_file)], capture_output=True)
                    service_file.unlink()
                return True, "macOS service uninstalled"
                
            elif sys.platform.startswith("linux"):
                commands = [
                    ["systemctl", "--user", "stop", f"{self.service_name}.service"],
                    ["systemctl", "--user", "disable", f"{self.service_name}.service"]
                ]
                for cmd in commands:
                    subprocess.run(cmd, capture_output=True)
                
                service_file = Path.home() / ".config" / "systemd" / "user" / f"{self.service_name}.service"
                service_file.unlink(missing_ok=True)
                subprocess.run(["systemctl", "--user", "daemon-reload"], capture_output=True)
                return True, "Linux service uninstalled"
                
            elif sys.platform == "win32":
                result = subprocess.run([
                    "schtasks", "/delete", "/tn", f"CopperSunBrass-{self.project_hash}", "/f"
                ], capture_output=True, text=True)
                return True, "Windows task uninstalled"
                
        except Exception as e:
            return False, f"Uninstall failed: {str(e)}"
        
        return False, "Platform not supported"