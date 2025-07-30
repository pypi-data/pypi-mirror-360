"""
Copper Sun Brass Configuration - Central configuration for all components

This module provides the core configuration that all other components depend on.
It handles project-specific storage paths, settings, and ignored patterns.
"""
from pathlib import Path
import hashlib
import os
from typing import Set


class BrassConfig:
    """Central configuration for Copper Sun Brass project analysis.
    
    Creates a unique storage directory for each project based on its path hash,
    ensuring multiple projects can be analyzed without conflicts.
    """
    
    def __init__(self, project_root: Path = None):
        """Initialize configuration for a specific project.
        
        Args:
            project_root: Root directory of the project to analyze.
                         Defaults to current working directory.
        """
        self.project_root = Path(project_root or os.getcwd()).resolve()
        
        # Create unique project identifier
        project_hash = hashlib.md5(str(self.project_root).encode()).hexdigest()[:8]
        
        # User-specific storage (survives project deletion)
        self.data_dir = Path.home() / '.brass' / 'projects' / project_hash
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Key paths
        self.db_path = self.data_dir / 'coppersun_brass.db'
        self.model_dir = self.data_dir / 'models'
        self.cache_dir = self.data_dir / 'cache'
        self.logs_dir = self.data_dir / 'logs'
        
        # Project-specific output (for Claude Code to read)
        self.output_dir = self.project_root / '.brass'
        self.output_dir.mkdir(exist_ok=True)
        
        # Create all directories
        for dir_path in [self.model_dir, self.cache_dir, self.logs_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Analysis settings
        self.max_file_size = 1024 * 1024  # 1MB - skip larger files
        self.max_files_per_batch = 100     # Process in chunks
        
        # Ignored patterns
        self.ignored_dirs: Set[str] = {
            '.git', '__pycache__', 'node_modules', '.venv', 'venv',
            'dist', 'build', '.pytest_cache', '.mypy_cache', 
            'htmlcov', '.tox', 'egg-info', '.idea', '.vscode'
        }
        
        self.ignored_files: Set[str] = {
            '.DS_Store', 'Thumbs.db', '*.pyc', '*.pyo', 
            '*.so', '*.dylib', '*.dll', '*.class'
        }
        
        # Target file extensions for analysis
        self.target_extensions: Set[str] = {
            '.py', '.js', '.ts', '.jsx', '.tsx',  # Main languages
            '.java', '.go', '.rs', '.cpp', '.c',  # Additional
            '.rb', '.php', '.swift', '.kt'        # More languages
        }
        
        # Schedule intervals (seconds)
        self.schedule = {
            'watch': 300,      # 5 minutes
            'scout': 3600,     # 1 hour  
            'strategist': 21600,  # 6 hours
            'claude': 7200,    # 2 hours
            'output': 900      # 15 minutes
        }
        
        # ML settings
        self.ml_batch_size = 32
        self.ml_cache_size = 10000
        self.ml_confidence_threshold = 0.7
        
        # Claude settings
        self.claude_max_issues_per_batch = 5
        self.claude_rate_limit_rpm = 50
        self.claude_max_tokens = 1000
        
        # Add to gitignore if needed
        self._update_gitignore()
        
        # Check for bootstrap on first run
        self._check_auto_bootstrap()
    
    def _update_gitignore(self):
        """Add .brass/ to .gitignore if not already present."""
        gitignore_path = self.project_root / '.gitignore'
        
        if gitignore_path.exists():
            content = gitignore_path.read_text()
            if '.brass/' not in content:
                with open(gitignore_path, 'a') as f:
                    f.write('\n# Copper Sun Brass output\n.brass/\n')
        else:
            # Create .gitignore with Copper Sun Brass entry
            gitignore_path.write_text('# Copper Sun Brass output\n.brass/\n')
    
    def should_analyze_file(self, file_path: Path) -> bool:
        """Check if a file should be analyzed based on configuration.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file should be analyzed
        """
        # Check if file exists and is a file
        if not file_path.is_file():
            return False
            
        # Check size
        if file_path.stat().st_size > self.max_file_size:
            return False
            
        # Check extension
        if file_path.suffix not in self.target_extensions:
            return False
            
        # Check ignored patterns
        for part in file_path.parts:
            if part in self.ignored_dirs:
                return False
                
        return True
    
    def _check_auto_bootstrap(self):
        """Legacy bootstrap check - disabled since system now uses pure Python ML"""
        # Only check if this is a new installation
        bootstrap_check_file = self.data_dir / '.bootstrap_checked'
        if bootstrap_check_file.exists():
            return
        
        # Mark that we've checked (bootstrap no longer needed with pure Python ML)
        bootstrap_check_file.touch()
        
        # Pure Python ML system requires no additional downloads or models
        # System is ready to use immediately with built-in 2.5MB ML engine
    
    def get_info(self) -> dict:
        """Get configuration info for logging/debugging.
        
        Returns:
            Dictionary of configuration settings
        """
        return {
            'project_root': str(self.project_root),
            'data_dir': str(self.data_dir),
            'db_path': str(self.db_path),
            'output_dir': str(self.output_dir),
            'target_extensions': list(self.target_extensions),
            'ignored_dirs': list(self.ignored_dirs),
            'schedule': self.schedule
        }