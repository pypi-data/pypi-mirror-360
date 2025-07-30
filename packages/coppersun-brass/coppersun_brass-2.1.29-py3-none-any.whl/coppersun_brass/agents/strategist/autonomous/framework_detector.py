"""
FrameworkDetector - Multi-signal framework and project type detection

Implements robust project type detection using weighted signals with confidence scoring
as specified in the Sprint 9 handoff document.
"""

import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

logger = logging.getLogger(__name__)


class FrameworkDetector:
    """
    Multi-signal framework and project type detection with confidence scoring
    
    Uses weighted signals to robustly classify projects and detect frameworks
    with minimum threshold confidence requirements.
    """
    
    def __init__(self):
        """Initialize with project type signals and framework patterns"""
        
        # Project type detection signals with weights
        self.project_signals = {
            'package.json': {'weight': 0.8, 'indicates': 'web_app'},
            'requirements.txt': {'weight': 0.7, 'indicates': 'python_app'},
            'pyproject.toml': {'weight': 0.8, 'indicates': 'python_app'},
            'setup.py': {'weight': 0.6, 'indicates': 'python_app'},
            'Pipfile': {'weight': 0.7, 'indicates': 'python_app'},
            'Dockerfile': {'weight': 0.6, 'indicates': 'containerized_app'},
            'docker-compose.yml': {'weight': 0.7, 'indicates': 'containerized_app'},
            'pom.xml': {'weight': 0.9, 'indicates': 'java_app'},
            'build.gradle': {'weight': 0.8, 'indicates': 'java_app'},
            'Cargo.toml': {'weight': 0.9, 'indicates': 'rust_app'},
            'go.mod': {'weight': 0.9, 'indicates': 'go_app'},
            'composer.json': {'weight': 0.8, 'indicates': 'php_app'},
            'Gemfile': {'weight': 0.8, 'indicates': 'ruby_app'},
            'mix.exs': {'weight': 0.9, 'indicates': 'elixir_app'},
            'pubspec.yaml': {'weight': 0.9, 'indicates': 'dart_app'},
            'project.clj': {'weight': 0.9, 'indicates': 'clojure_app'},
            '.sln': {'weight': 0.8, 'indicates': 'dotnet_app'},
            'Package.swift': {'weight': 0.9, 'indicates': 'swift_app'}
        }
        
        # Content-based signals for additional classification
        self.content_signals = {
            'api_routes_detected': {'weight': 0.7, 'indicates': 'backend_api'},
            'react_components': {'weight': 0.8, 'indicates': 'frontend_spa'},
            'vue_components': {'weight': 0.8, 'indicates': 'frontend_spa'},
            'angular_components': {'weight': 0.8, 'indicates': 'frontend_spa'},
            'cli_patterns': {'weight': 0.9, 'indicates': 'cli_tool'},
            'ml_patterns': {'weight': 0.8, 'indicates': 'ml_project'},
            'test_patterns': {'weight': 0.6, 'indicates': 'library'},
            'desktop_patterns': {'weight': 0.7, 'indicates': 'desktop_app'},
            'mobile_patterns': {'weight': 0.8, 'indicates': 'mobile_app'}
        }
        
        # Framework detection patterns
        self.framework_patterns = {
            # Python frameworks
            'django': {
                'files': ['manage.py', 'settings.py', 'urls.py'],
                'imports': ['django', 'from django'],
                'weight': 0.9
            },
            'flask': {
                'files': ['app.py', 'wsgi.py'],
                'imports': ['flask', 'from flask'],
                'weight': 0.8
            },
            'fastapi': {
                'files': ['main.py'],
                'imports': ['fastapi', 'from fastapi'],
                'weight': 0.9
            },
            'streamlit': {
                'files': ['streamlit_app.py'],
                'imports': ['streamlit'],
                'weight': 0.9
            },
            'pytest': {
                'files': ['pytest.ini', 'conftest.py'],
                'imports': ['pytest'],
                'weight': 0.7
            },
            
            # JavaScript/Node.js frameworks
            'react': {
                'files': ['src/App.js', 'src/App.jsx', 'src/App.tsx'],
                'package_deps': ['react', 'react-dom'],
                'weight': 0.9
            },
            'vue': {
                'files': ['src/App.vue', 'vue.config.js'],
                'package_deps': ['vue'],
                'weight': 0.9
            },
            'angular': {
                'files': ['angular.json', 'src/app/app.component.ts'],
                'package_deps': ['@angular/core'],
                'weight': 0.9
            },
            'next': {
                'files': ['next.config.js', 'pages/index.js'],
                'package_deps': ['next'],
                'weight': 0.9
            },
            'express': {
                'files': ['server.js', 'app.js'],
                'package_deps': ['express'],
                'weight': 0.8
            },
            'nuxt': {
                'files': ['nuxt.config.js'],
                'package_deps': ['nuxt'],
                'weight': 0.9
            },
            
            # Other frameworks
            'spring': {
                'files': ['pom.xml', 'application.properties'],
                'content_patterns': ['@SpringBootApplication', 'org.springframework'],
                'weight': 0.9
            },
            'rails': {
                'files': ['Gemfile', 'config/application.rb'],
                'content_patterns': ['Rails.application'],
                'weight': 0.9
            },
            'laravel': {
                'files': ['artisan', 'composer.json'],
                'content_patterns': ['Illuminate\\\\'],
                'weight': 0.9
            }
        }
        
        # Minimum confidence threshold for classification
        self.min_confidence_threshold = 0.6
        
    async def detect_project_type(self, project_path: Path) -> Dict[str, Any]:
        """
        Detect project type using multi-signal analysis with confidence scoring
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Dict with 'type' and 'confidence' keys
        """
        if not project_path.exists() or not project_path.is_dir():
            return {'type': 'unknown', 'confidence': 0.0}
        
        try:
            confidence_scores = {}
            
            # Check file-based signals
            for signal_file, config in self.project_signals.items():
                if await self._detect_file_signal(project_path, signal_file):
                    project_type = config['indicates']
                    weight = config['weight']
                    confidence_scores[project_type] = confidence_scores.get(project_type, 0) + weight
            
            # Check content-based signals
            content_signals = await self._detect_content_signals(project_path)
            for signal_name, detected in content_signals.items():
                if detected and signal_name in self.content_signals:
                    config = self.content_signals[signal_name]
                    project_type = config['indicates']
                    weight = config['weight']
                    confidence_scores[project_type] = confidence_scores.get(project_type, 0) + weight
            
            # Find best match above threshold
            if confidence_scores:
                best_match = max(confidence_scores.items(), key=lambda x: x[1])
                project_type, confidence = best_match
                
                # Normalize confidence to 0-1 scale
                normalized_confidence = min(confidence / 2.0, 1.0)  # Assuming max possible score is ~2.0
                
                if normalized_confidence >= self.min_confidence_threshold:
                    return {
                        'type': project_type,
                        'confidence': normalized_confidence,
                        'all_scores': confidence_scores
                    }
            
            # Fallback to directory-based heuristics
            fallback_type = await self._detect_fallback_type(project_path)
            return {
                'type': fallback_type,
                'confidence': 0.3,  # Low confidence for fallback
                'all_scores': confidence_scores
            }
            
        except Exception as e:
            logger.error(f"Project type detection failed: {e}")
            return {'type': 'unknown', 'confidence': 0.0}
    
    async def detect_frameworks(self, project_path: Path) -> Dict[str, Any]:
        """
        Detect frameworks and technologies used in the project
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Dict with primary and secondary frameworks
        """
        if not project_path.exists() or not project_path.is_dir():
            return {'primary': [], 'secondary': [], 'confidence': 0.0}
        
        try:
            detected_frameworks = {}
            
            # Analyze each framework pattern
            for framework_name, patterns in self.framework_patterns.items():
                confidence = await self._analyze_framework_patterns(project_path, patterns)
                if confidence > 0.3:  # Minimum threshold for framework detection
                    detected_frameworks[framework_name] = confidence
            
            # Sort by confidence
            sorted_frameworks = sorted(detected_frameworks.items(), key=lambda x: x[1], reverse=True)
            
            # Classify as primary (high confidence) and secondary (medium confidence)
            primary_frameworks = [name for name, conf in sorted_frameworks if conf >= 0.7]
            secondary_frameworks = [name for name, conf in sorted_frameworks if 0.3 <= conf < 0.7]
            
            overall_confidence = max(detected_frameworks.values()) if detected_frameworks else 0.0
            
            return {
                'primary': primary_frameworks,
                'secondary': secondary_frameworks,
                'all_detected': detected_frameworks,
                'confidence': overall_confidence
            }
            
        except Exception as e:
            logger.error(f"Framework detection failed: {e}")
            return {'primary': [], 'secondary': [], 'confidence': 0.0}
    
    async def _detect_file_signal(self, project_path: Path, signal_file: str) -> bool:
        """Check if a specific file signal exists"""
        try:
            # Handle different file extensions
            base_name = signal_file.split('.')[0]
            possible_files = [
                project_path / signal_file,
                project_path / f"{base_name}.yml",
                project_path / f"{base_name}.yaml",
                project_path / f"{base_name}.toml",
                project_path / f"{base_name}.json"
            ]
            
            return any(file_path.exists() for file_path in possible_files)
            
        except Exception as e:
            logger.debug(f"Error checking file signal {signal_file}: {e}")
            return False
    
    async def _detect_content_signals(self, project_path: Path) -> Dict[str, bool]:
        """Detect content-based signals by analyzing file contents"""
        signals = {
            'api_routes_detected': False,
            'react_components': False,
            'vue_components': False,
            'angular_components': False,
            'cli_patterns': False,
            'ml_patterns': False,
            'test_patterns': False,
            'desktop_patterns': False,
            'mobile_patterns': False
        }
        
        try:
            # Sample files for content analysis (avoid reading entire large projects)
            sample_files = []
            for pattern in ['*.py', '*.js', '*.jsx', '*.ts', '*.tsx', '*.vue', '*.java', '*.go']:
                sample_files.extend(list(project_path.glob(pattern))[:5])  # Limit to 5 files per type
                sample_files.extend(list(project_path.glob(f"src/**/{pattern}"))[:5])
            
            # Limit total files analyzed
            sample_files = sample_files[:20]
            
            for file_path in sample_files:
                if file_path.is_file() and file_path.stat().st_size < 100000:  # Skip files > 100KB
                    try:
                        content = await self._read_file_safely(file_path)
                        if content:
                            await self._analyze_content_for_signals(content, signals)
                    except Exception as e:
                        logger.debug(f"Error reading file {file_path}: {e}")
                        continue
            
            return signals
            
        except Exception as e:
            logger.error(f"Content signal detection failed: {e}")
            return signals
    
    async def _read_file_safely(self, file_path: Path) -> Optional[str]:
        """Safely read file content with encoding detection"""
        try:
            # Try common encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
                except (OSError, PermissionError):
                    return None
            return None
        except Exception as e:
            logger.debug(f"Error reading file {file_path}: {e}")
            return None
    
    async def _analyze_content_for_signals(self, content: str, signals: Dict[str, bool]) -> None:
        """Analyze file content for framework and pattern signals"""
        content_lower = content.lower()
        
        # API route patterns
        api_patterns = [
            r'@app\.route', r'@router\.',  # Flask/FastAPI
            r'app\.get\(', r'app\.post\(',  # Express
            r'@GetMapping', r'@PostMapping',  # Spring
            r'Route::', r'->get\(', r'->post\('  # Laravel/Rails
        ]
        if any(re.search(pattern, content) for pattern in api_patterns):
            signals['api_routes_detected'] = True
        
        # React patterns
        react_patterns = [
            r'import.*react', r'from [\'"]react[\'"]',
            r'useState\(', r'useEffect\(',
            r'class.*extends.*Component', r'React\.Component'
        ]
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in react_patterns):
            signals['react_components'] = True
        
        # Vue patterns
        if re.search(r'<template>|<script>|Vue\.component|new Vue\(', content, re.IGNORECASE):
            signals['vue_components'] = True
        
        # Angular patterns
        angular_patterns = [
            r'@Component\(', r'@Injectable\(', r'@NgModule\(',
            r'import.*@angular'
        ]
        if any(re.search(pattern, content) for pattern in angular_patterns):
            signals['angular_components'] = True
        
        # CLI patterns
        cli_patterns = [
            r'argparse\.ArgumentParser', r'click\.command',
            r'commander\.program', r'yargs\.argv',
            r'if __name__ == [\'"]__main__[\'"]'
        ]
        if any(re.search(pattern, content) for pattern in cli_patterns):
            signals['cli_patterns'] = True
        
        # ML patterns
        ml_patterns = [
            r'import (numpy|pandas|sklearn|tensorflow|torch|keras)',
            r'from (numpy|pandas|sklearn|tensorflow|torch|keras)',
            r'\.fit\(', r'\.predict\(', r'\.train\('
        ]
        if any(re.search(pattern, content) for pattern in ml_patterns):
            signals['ml_patterns'] = True
        
        # Test patterns
        test_patterns = [
            r'import (unittest|pytest|jest|mocha)',
            r'describe\(', r'it\(', r'test_.*\(',
            r'@Test', r'class.*Test.*:'
        ]
        if any(re.search(pattern, content) for pattern in test_patterns):
            signals['test_patterns'] = True
        
        # Desktop patterns
        desktop_patterns = [
            r'import (tkinter|PyQt|wxPython|kivy)',
            r'from (electron|tauri)',
            r'System\.Windows\.Forms', r'javafx\.'
        ]
        if any(re.search(pattern, content) for pattern in desktop_patterns):
            signals['desktop_patterns'] = True
        
        # Mobile patterns
        mobile_patterns = [
            r'import (react-native|expo)',
            r'from [\'"]react-native[\'"]',
            r'import.*flutter', r'Android|iOS|UIKit|SwiftUI'
        ]
        if any(re.search(pattern, content) for pattern in mobile_patterns):
            signals['mobile_patterns'] = True
    
    async def _analyze_framework_patterns(self, project_path: Path, patterns: Dict[str, Any]) -> float:
        """Analyze project for specific framework patterns"""
        confidence = 0.0
        max_confidence = patterns.get('weight', 1.0)
        
        try:
            # Check for specific files
            if 'files' in patterns:
                file_matches = 0
                for file_pattern in patterns['files']:
                    if (project_path / file_pattern).exists():
                        file_matches += 1
                
                if file_matches > 0:
                    confidence += (file_matches / len(patterns['files'])) * max_confidence * 0.4
            
            # Check package dependencies
            if 'package_deps' in patterns:
                dep_confidence = await self._check_package_dependencies(project_path, patterns['package_deps'])
                confidence += dep_confidence * max_confidence * 0.4
            
            # Check imports in code
            if 'imports' in patterns:
                import_confidence = await self._check_imports(project_path, patterns['imports'])
                confidence += import_confidence * max_confidence * 0.3
            
            # Check content patterns
            if 'content_patterns' in patterns:
                content_confidence = await self._check_content_patterns(project_path, patterns['content_patterns'])
                confidence += content_confidence * max_confidence * 0.3
            
            return min(confidence, max_confidence)
            
        except Exception as e:
            logger.debug(f"Framework pattern analysis failed: {e}")
            return 0.0
    
    async def _check_package_dependencies(self, project_path: Path, dependencies: List[str]) -> float:
        """Check if package dependencies are present"""
        try:
            # Check package.json
            package_json = project_path / 'package.json'
            if package_json.exists():
                with open(package_json, 'r') as f:
                    package_data = json.load(f)
                    all_deps = {**package_data.get('dependencies', {}), 
                               **package_data.get('devDependencies', {})}
                    
                    matches = sum(1 for dep in dependencies if dep in all_deps)
                    return matches / len(dependencies) if dependencies else 0
            
            # Check requirements.txt
            requirements_txt = project_path / 'requirements.txt'
            if requirements_txt.exists():
                with open(requirements_txt, 'r') as f:
                    requirements = f.read().lower()
                    matches = sum(1 for dep in dependencies if dep.lower() in requirements)
                    return matches / len(dependencies) if dependencies else 0
            
            return 0.0
            
        except Exception as e:
            logger.debug(f"Package dependency check failed: {e}")
            return 0.0
    
    async def _check_imports(self, project_path: Path, import_patterns: List[str]) -> float:
        """Check for import patterns in code files"""
        try:
            matches = 0
            total_files_checked = 0
            
            # Sample a few files to check imports
            for pattern in ['*.py', '*.js', '*.ts']:
                files = list(project_path.glob(pattern))[:3]  # Check up to 3 files per type
                for file_path in files:
                    if file_path.stat().st_size < 50000:  # Skip large files
                        try:
                            content = await self._read_file_safely(file_path)
                            if content:
                                total_files_checked += 1
                                if any(import_pattern in content.lower() for import_pattern in import_patterns):
                                    matches += 1
                        except Exception:
                            continue
            
            return matches / total_files_checked if total_files_checked > 0 else 0.0
            
        except Exception as e:
            logger.debug(f"Import check failed: {e}")
            return 0.0
    
    async def _check_content_patterns(self, project_path: Path, content_patterns: List[str]) -> float:
        """Check for specific content patterns in files"""
        try:
            matches = 0
            total_files_checked = 0
            
            # Sample files for content analysis
            for pattern in ['*.py', '*.java', '*.js', '*.php', '*.rb']:
                files = list(project_path.glob(pattern))[:2]  # Check up to 2 files per type
                for file_path in files:
                    if file_path.stat().st_size < 50000:  # Skip large files
                        try:
                            content = await self._read_file_safely(file_path)
                            if content:
                                total_files_checked += 1
                                if any(pattern in content for pattern in content_patterns):
                                    matches += 1
                        except Exception:
                            continue
            
            return matches / total_files_checked if total_files_checked > 0 else 0.0
            
        except Exception as e:
            logger.debug(f"Content pattern check failed: {e}")
            return 0.0
    
    async def _detect_fallback_type(self, project_path: Path) -> str:
        """Fallback project type detection based on directory structure"""
        try:
            # Check for common directories that indicate project type
            directories = [d.name for d in project_path.iterdir() if d.is_dir()]
            
            if 'src' in directories or 'lib' in directories:
                return 'library'
            elif 'tests' in directories or 'test' in directories:
                return 'library'
            elif 'docs' in directories or 'documentation' in directories:
                return 'documentation'
            elif any(d.startswith('.') for d in directories):
                return 'development_project'
            else:
                return 'unknown'
                
        except Exception:
            return 'unknown'