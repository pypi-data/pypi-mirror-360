"""
Context Manager for Copper Sun Brass Pro - Handles generation and updates of context files.

This module manages the .brass/ context files that provide persistent memory
and insights across Claude Code sessions.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess
import re


class ContextManager:
    """Manages Copper Sun Brass context files for persistent memory."""
    
    def __init__(self, project_root: Path = Path.cwd()):
        self.project_root = project_root
        self.brass_dir = project_root / ".brass"
        self.config_file = self.brass_dir / "config.json"
        
        # Context file paths
        self.status_file = self.brass_dir / "STATUS.md"
        self.context_file = self.brass_dir / "CONTEXT.md"
        self.insights_file = self.brass_dir / "INSIGHTS.md"
        self.history_file = self.brass_dir / "HISTORY.md"
        
        # Load configuration
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load Copper Sun Brass configuration."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"user_preferences": {}}
    
    def update_status(self, force: bool = False):
        """Update the STATUS.md file with current project status."""
        # Ensure directory exists
        self.brass_dir.mkdir(exist_ok=True)
        
        content = ["# Copper Sun Brass Status", ""]
        
        # Active status
        content.append("## 🎺 Copper Sun Brass Active")
        content.append(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("")
        
        # Project information
        content.append("## 📊 Project Overview")
        
        # Count files by type
        file_stats = self._get_file_statistics()
        if file_stats:
            content.append("### File Statistics")
            for ext, count in sorted(file_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
                content.append(f"- {ext}: {count} files")
            content.append("")
        
        # Git status if available
        git_info = self._get_git_info()
        if git_info:
            content.append("### Git Status")
            content.append(f"- Branch: {git_info.get('branch', 'unknown')}")
            content.append(f"- Modified files: {git_info.get('modified', 0)}")
            content.append(f"- Untracked files: {git_info.get('untracked', 0)}")
            content.append("")
        
        # Recent activity
        content.append("## 📈 Recent Activity")
        content.append("- Context files are being maintained")
        content.append("- Ready to track development progress")
        content.append("")
        
        # Write status file
        with open(self.status_file, 'w') as f:
            f.write('\n'.join(content))
    
    def update_context(self, current_work: Optional[str] = None):
        """Update the CONTEXT.md file with current work context."""
        # Ensure directory exists
        self.brass_dir.mkdir(exist_ok=True)
        
        content = ["# Current Work Context", ""]
        content.append(f"*Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        content.append("")
        
        if current_work:
            content.append("## 🎯 Current Focus")
            content.append(current_work)
            content.append("")
        
        # Add project structure insight
        content.append("## 📁 Key Project Areas")
        key_dirs = self._identify_key_directories()
        for dir_path, description in key_dirs.items():
            content.append(f"- **{dir_path}**: {description}")
        content.append("")
        
        # Add technology stack
        tech_stack = self._identify_tech_stack()
        if tech_stack:
            content.append("## 🛠️ Technology Stack")
            for tech, details in tech_stack.items():
                content.append(f"- **{tech}**: {details}")
            content.append("")
        
        # Configuration reminders
        prefs = self.config.get("user_preferences", {})
        theme = prefs.get("visual_theme", "colorful")
        verbosity = prefs.get("verbosity", "balanced")
        
        content.append("## ⚙️ Copper Sun Brass Configuration")
        content.append(f"- Visual theme: {theme}")
        content.append(f"- Verbosity: {verbosity}")
        content.append("")
        
        # Write context file
        with open(self.context_file, 'w') as f:
            f.write('\n'.join(content))
    
    def generate_insights(self):
        """Generate insights based on project analysis."""
        # Ensure directory exists
        self.brass_dir.mkdir(exist_ok=True)
        
        content = ["# Copper Sun Brass Insights", ""]
        content.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        content.append("")
        
        insights = []
        
        # Check for common patterns and issues
        patterns = self._analyze_patterns()
        if patterns:
            content.append("## 💡 Detected Patterns")
            for pattern in patterns:
                content.append(f"- {pattern}")
            content.append("")
        
        # Security insights
        security_issues = self._check_security_patterns()
        if security_issues:
            content.append("## 🔒 Security Considerations")
            for issue in security_issues:
                content.append(f"- ⚠️ {issue}")
            content.append("")
        
        # Performance insights
        perf_suggestions = self._analyze_performance_patterns()
        if perf_suggestions:
            content.append("## ⚡ Performance Suggestions")
            for suggestion in perf_suggestions:
                content.append(f"- {suggestion}")
            content.append("")
        
        # Best practices
        content.append("## 📚 Best Practices Reminder")
        content.append("- Keep commits atomic and well-described")
        content.append("- Write tests for new functionality")
        content.append("- Document complex logic")
        content.append("- Review security implications of changes")
        content.append("")
        
        # Write insights file
        with open(self.insights_file, 'w') as f:
            f.write('\n'.join(content))
    
    def add_to_history(self, event: str, details: Optional[Dict[str, Any]] = None):
        """Add an event to the project history."""
        # Ensure directory exists
        self.brass_dir.mkdir(exist_ok=True)
        
        # Read existing history
        history_entries = []
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                content = f.read()
                # Parse existing entries (simple format for now)
                if "## Timeline" in content:
                    history_entries = content.split("## Timeline")[1].strip().split('\n')
                    history_entries = [e for e in history_entries if e.strip()]
        
        # Add new entry
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        new_entry = f"- **{timestamp}**: {event}"
        if details:
            for key, value in details.items():
                new_entry += f"\n  - {key}: {value}"
        
        history_entries.append(new_entry)
        
        # Keep last 50 entries
        if len(history_entries) > 50:
            history_entries = history_entries[-50:]
        
        # Write updated history
        content = ["# Project History", ""]
        content.append("*Copper Sun Brass tracks important events and decisions*")
        content.append("")
        content.append("## Timeline")
        content.extend(history_entries)
        content.append("")
        
        with open(self.history_file, 'w') as f:
            f.write('\n'.join(content))
    
    def _get_file_statistics(self) -> Dict[str, int]:
        """Get statistics about files in the project."""
        stats = {}
        ignore_dirs = {'.git', '__pycache__', 'node_modules', '.brass', 'venv', '.venv'}
        
        for root, dirs, files in os.walk(self.project_root):
            # Remove ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                ext = Path(file).suffix.lower() or 'no extension'
                stats[ext] = stats.get(ext, 0) + 1
        
        return stats
    
    def _get_git_info(self) -> Optional[Dict[str, Any]]:
        """Get git repository information."""
        try:
            # Check if it's a git repo
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                return None
            
            info = {}
            
            # Get current branch
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            info['branch'] = result.stdout.strip() if result.returncode == 0 else 'unknown'
            
            # Get status
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                info['modified'] = sum(1 for line in lines if line.startswith(' M') or line.startswith('M'))
                info['untracked'] = sum(1 for line in lines if line.startswith('??'))
            
            return info
        except Exception:
            return None
    
    def _identify_key_directories(self) -> Dict[str, str]:
        """Identify key directories in the project."""
        key_dirs = {}
        
        # Common directory patterns
        patterns = {
            'src': 'Source code',
            'tests': 'Test files',
            'docs': 'Documentation',
            'scripts': 'Utility scripts',
            'config': 'Configuration files',
            'coppersun_brass': 'Copper Sun Brass core system',
            'examples': 'Example code',
            'templates': 'Template files'
        }
        
        for dir_name, description in patterns.items():
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                key_dirs[dir_name] = description
        
        return key_dirs
    
    def _identify_tech_stack(self) -> Dict[str, str]:
        """Identify the technology stack used in the project."""
        tech_stack = {}
        
        # Check for common config files
        checks = {
            'package.json': ('Node.js', 'JavaScript/TypeScript project'),
            'requirements.txt': ('Python', 'Python dependencies'),
            'pyproject.toml': ('Python', 'Modern Python project'),
            'Cargo.toml': ('Rust', 'Rust project'),
            'go.mod': ('Go', 'Go modules'),
            'pom.xml': ('Java', 'Maven project'),
            'build.gradle': ('Java', 'Gradle project'),
            'Gemfile': ('Ruby', 'Ruby project'),
            'composer.json': ('PHP', 'PHP Composer project')
        }
        
        for filename, (tech, description) in checks.items():
            if (self.project_root / filename).exists():
                tech_stack[tech] = description
        
        return tech_stack
    
    def _safe_is_file(self, path) -> bool:
        """Safely check if path is file, handling permission errors."""
        try:
            return path.is_file()
        except (PermissionError, OSError):
            return False
    
    def _analyze_patterns(self) -> List[str]:
        """Analyze project for common patterns."""
        patterns = []
        
        # Check project size (with permission error handling)
        file_count = 0
        try:
            file_count = sum(1 for _ in self.project_root.rglob('*') if self._safe_is_file(_))
        except (PermissionError, OSError):
            file_count = 0  # Fall back to 0 if scanning fails
        if file_count > 1000:
            patterns.append("Large project detected - consider modularization")
        elif file_count < 10:
            patterns.append("Small project - good time to establish structure")
        
        # Check for test coverage
        has_tests = any(self.project_root.rglob('test_*.py')) or \
                   any(self.project_root.rglob('*.test.js')) or \
                   (self.project_root / 'tests').exists()
        
        if not has_tests:
            patterns.append("No test files detected - consider adding tests")
        
        # Check for documentation
        has_docs = (self.project_root / 'README.md').exists() or \
                  (self.project_root / 'docs').exists()
        
        if not has_docs:
            patterns.append("Limited documentation found - consider adding README.md")
        
        return patterns
    
    def _check_security_patterns(self) -> List[str]:
        """Check for security issues from Scout analysis."""
        issues = []
        
        # First, try to read from Scout analysis report
        analysis_report_path = self.brass_dir / 'analysis_report.json'
        if analysis_report_path.exists():
            try:
                with open(analysis_report_path, 'r') as f:
                    analysis_data = json.load(f)
                
                # Extract security-related TODOs and issues
                for todo in analysis_data.get('todos', []):
                    if any(keyword in todo.get('content', '').lower() for keyword in ['security', 'secret', 'password', 'key', 'token', 'auth']):
                        classification = todo.get('classification', 'unknown')
                        priority = todo.get('priority', 0)
                        file_name = os.path.basename(todo.get('file', 'unknown'))
                        line = todo.get('line', '')
                        content = todo.get('content', '')
                        issues.append(f"🔒 {classification.upper()}: {content} ({file_name}:{line})")
                
                # Extract critical issues
                for issue in analysis_data.get('issues', []):
                    if issue.get('severity') in ['critical', 'important']:
                        severity = issue.get('severity', 'unknown')
                        file_name = os.path.basename(issue.get('file', 'unknown'))
                        description = issue.get('description', '')
                        issues.append(f"⚠️ {severity.upper()}: {description} ({file_name})")
                
                if issues:
                    return issues[:5]  # Limit to 5 most important issues
                    
            except Exception as e:
                # Fall back to basic pattern checking if analysis fails
                pass
        
        # Fallback: Check for common sensitive file patterns
        sensitive_patterns = [
            '*.pem', '*.key', '*.env', '.env.*', 'secrets.*', '*_secret*'
        ]
        
        for pattern in sensitive_patterns:
            matches = list(self.project_root.rglob(pattern))
            if matches:
                gitignore_path = self.project_root / '.gitignore'
                if gitignore_path.exists():
                    with open(gitignore_path, 'r') as f:
                        gitignore_content = f.read()
                    
                    for match in matches:
                        relative_path = match.relative_to(self.project_root)
                        if str(relative_path) not in gitignore_content:
                            issues.append(f"Sensitive file '{relative_path}' may not be in .gitignore")
        
        return issues[:5]  # Limit to 5 issues
    
    def _analyze_performance_patterns(self) -> List[str]:
        """Analyze for potential performance improvements."""
        suggestions = []
        
        # Check for large files
        large_files = []
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file() and file_path.stat().st_size > 1_000_000:  # 1MB
                large_files.append(file_path)
        
        if large_files:
            suggestions.append(f"Found {len(large_files)} files over 1MB - consider optimization")
        
        # Check for common performance patterns in Python files
        py_files = list(self.project_root.rglob('*.py'))
        if py_files:
            # Simple pattern matching (would be more sophisticated in production)
            for py_file in py_files[:10]:  # Check first 10 files
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                    
                    if 'import *' in content:
                        suggestions.append(f"Avoid 'import *' for better performance")
                        break
                except Exception:
                    pass
        
        return suggestions[:5]  # Limit suggestions