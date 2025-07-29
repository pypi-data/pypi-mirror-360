"""
FileStructureAnalyzer - Analyzes project file structure and patterns

Provides comprehensive analysis of project organization, file patterns,
and architectural structure for autonomous planning decisions.
"""

import asyncio
import logging
import mimetypes
import os
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Any, Set, Optional

logger = logging.getLogger(__name__)


class FileStructureAnalyzer:
    """
    Analyzes project file structure and organization patterns
    
    Provides insights into project architecture, file organization,
    and structural quality for autonomous planning decisions.
    """
    
    def __init__(self):
        """Initialize with file type classifications and patterns"""
        
        # File type classifications
        self.code_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
            '.cs', '.php', '.rb', '.go', '.rs', '.kt', '.scala', '.swift', '.m', '.mm',
            '.vue', '.svelte', '.elm', '.dart', '.clj', '.cljs', '.ex', '.exs'
        }
        
        self.config_extensions = {
            '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.xml',
            '.properties', '.env', '.config'
        }
        
        self.doc_extensions = {
            '.md', '.rst', '.txt', '.doc', '.docx', '.pdf', '.html', '.htm'
        }
        
        self.build_extensions = {
            '.dockerfile', '.yml', '.yaml'  # Build-related files
        }
        
        # Ignore patterns for analysis
        self.ignore_patterns = {
            '__pycache__', '.git', '.svn', '.hg', 'node_modules', '.npm',
            'venv', 'env', '.env', 'virtualenv', '.venv',
            'target', 'build', 'dist', '.dist', 'out',
            '.idea', '.vscode', '.vs', '.eclipse',
            'coverage', '.coverage', '.nyc_output',
            'logs', '*.log', 'tmp', 'temp', '.tmp', '.temp',
            '.DS_Store', 'Thumbs.db', '*.pyc', '*.pyo', '*.pyd',
            '*.class', '*.jar', '*.war', '*.ear',
            '*.exe', '*.dll', '*.so', '*.dylib'
        }
        
        # Common architectural patterns
        self.architecture_patterns = {
            'mvc': {
                'indicators': ['models', 'views', 'controllers', 'model', 'view', 'controller'],
                'confidence_threshold': 0.6
            },
            'layered': {
                'indicators': ['service', 'repository', 'dao', 'entity', 'dto', 'domain'],
                'confidence_threshold': 0.5
            },
            'microservices': {
                'indicators': ['services', 'api', 'gateway', 'auth', 'user', 'payment'],
                'confidence_threshold': 0.7
            },
            'monolithic': {
                'indicators': ['app', 'main', 'core', 'common', 'shared'],
                'confidence_threshold': 0.4
            },
            'component': {
                'indicators': ['components', 'widgets', 'modules', 'plugins'],
                'confidence_threshold': 0.6
            }
        }
        
        # Quality indicators
        self.quality_indicators = {
            'has_tests': ['test', 'tests', '__tests__', 'spec', 'specs'],
            'has_docs': ['doc', 'docs', 'documentation', 'README', 'readme'],
            'has_config': ['config', 'settings', 'conf', 'cfg'],
            'has_scripts': ['scripts', 'bin', 'tools', 'utils'],
            'has_build': ['build', 'make', 'cmake', 'gradle', 'maven'],
            'has_deployment': ['deploy', 'deployment', 'docker', 'k8s', 'kubernetes']
        }
    
    async def analyze(self, project_path: Path) -> Dict[str, Any]:
        """
        Analyze project file structure comprehensively
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Dict containing complete file structure analysis
        """
        if not project_path.exists() or not project_path.is_dir():
            raise ValueError(f"Invalid project path: {project_path}")
        
        try:
            logger.info(f"Analyzing file structure for: {project_path}")
            
            # Collect file information
            file_info = await self._collect_file_info(project_path)
            
            # Analyze structure patterns
            structure_analysis = await self._analyze_structure_patterns(project_path, file_info)
            
            # Analyze file organization
            organization_analysis = await self._analyze_organization(file_info)
            
            # Detect architectural patterns
            architecture_analysis = await self._detect_architecture_patterns(project_path, file_info)
            
            # Assess quality indicators
            quality_analysis = await self._assess_quality_indicators(project_path)
            
            # Calculate metrics
            metrics = await self._calculate_metrics(file_info)
            
            return {
                'total_files': len(file_info['all_files']),
                'total_directories': len(file_info['directories']),
                'file_types': file_info['file_types'],
                'structure_patterns': structure_analysis,
                'organization': organization_analysis,
                'architecture': architecture_analysis,
                'quality_indicators': quality_analysis,
                'metrics': metrics,
                'has_tests': quality_analysis.get('has_tests', False),
                'has_documentation': quality_analysis.get('has_docs', False),
                'structure_quality_score': await self._calculate_structure_quality(
                    structure_analysis, organization_analysis, quality_analysis
                )
            }
            
        except Exception as e:
            logger.error(f"File structure analysis failed: {e}")
            raise RuntimeError(f"Failed to analyze file structure: {e}")
    
    async def analyze_patterns(self, project_path: Path) -> Dict[str, Any]:
        """
        Analyze code patterns and architectural decisions
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Dict containing pattern analysis
        """
        try:
            patterns = {
                'naming_conventions': await self._analyze_naming_conventions(project_path),
                'file_organization': await self._analyze_file_organization(project_path),
                'import_patterns': await self._analyze_import_patterns(project_path),
                'architectural_style': await self._determine_architectural_style(project_path),
                'code_structure': await self._analyze_code_structure(project_path)
            }
            
            # Calculate overall pattern confidence
            confidence_scores = [
                patterns['naming_conventions'].get('confidence', 0),
                patterns['file_organization'].get('confidence', 0),
                patterns['architectural_style'].get('confidence', 0)
            ]
            
            overall_confidence = sum(confidence_scores) / len(confidence_scores)
            
            return {
                'patterns': patterns,
                'architecture_style': patterns['architectural_style'].get('style', 'unknown'),
                'confidence': overall_confidence
            }
            
        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
            return {'patterns': [], 'architecture_style': 'unknown', 'confidence': 0.0}
    
    async def _collect_file_info(self, project_path: Path) -> Dict[str, Any]:
        """Collect comprehensive file information"""
        file_info = {
            'all_files': [],
            'directories': [],
            'file_types': defaultdict(int),
            'file_sizes': [],
            'depth_distribution': defaultdict(int),
            'extension_count': Counter()
        }
        
        try:
            for item in project_path.rglob('*'):
                try:
                    # Skip ignored patterns
                    if self._should_ignore(item):
                        continue
                    
                    relative_path = item.relative_to(project_path)
                    depth = len(relative_path.parts)
                    
                    if item.is_file():
                        file_info['all_files'].append(relative_path)
                        try:
                            file_info['file_sizes'].append(item.stat().st_size)
                        except (OSError, PermissionError):
                            file_info['file_sizes'].append(0)
                        file_info['depth_distribution'][depth] += 1
                        
                        # Classify file type
                        extension = item.suffix.lower()
                        file_info['extension_count'][extension] += 1
                        
                        if extension in self.code_extensions:
                            file_info['file_types']['code'] += 1
                        elif extension in self.config_extensions:
                            file_info['file_types']['config'] += 1
                        elif extension in self.doc_extensions:
                            file_info['file_types']['documentation'] += 1
                        elif extension in self.build_extensions:
                            file_info['file_types']['build'] += 1
                        else:
                            file_info['file_types']['other'] += 1
                    
                    elif item.is_dir():
                        file_info['directories'].append(relative_path)
                        file_info['depth_distribution'][depth] += 1
                
                except (OSError, PermissionError) as e:
                    logger.debug(f"Access denied for {item}: {e}")
                    continue
                except Exception as e:
                    logger.debug(f"Error processing {item}: {e}")
                    continue
            
            return file_info
            
        except Exception as e:
            logger.error(f"Failed to collect file info: {e}")
            return file_info
    
    async def _analyze_structure_patterns(self, project_path: Path, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze structural organization patterns"""
        patterns = {
            'depth_analysis': self._analyze_depth_patterns(file_info),
            'directory_organization': await self._analyze_directory_organization(project_path),
            'file_distribution': self._analyze_file_distribution(file_info),
            'naming_consistency': await self._analyze_naming_consistency(file_info)
        }
        
        return patterns
    
    async def _analyze_organization(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze file organization quality"""
        total_files = len(file_info['all_files'])
        
        organization = {
            'file_type_distribution': dict(file_info['file_types']),
            'average_depth': self._calculate_average_depth(file_info),
            'max_depth': max(file_info['depth_distribution'].keys()) if file_info['depth_distribution'] else 0,
            'organization_score': self._calculate_organization_score(file_info),
            'size_distribution': self._analyze_size_distribution(file_info['file_sizes'])
        }
        
        return organization
    
    async def _detect_architecture_patterns(self, project_path: Path, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Detect architectural patterns from file structure"""
        detected_patterns = {}
        
        # Get directory names for pattern matching
        directory_names = [str(d).lower() for d in file_info['directories']]
        file_names = [str(f).lower() for f in file_info['all_files']]
        all_names = directory_names + file_names
        
        for pattern_name, pattern_config in self.architecture_patterns.items():
            indicators = pattern_config['indicators']
            threshold = pattern_config['confidence_threshold']
            
            # Count indicator matches
            matches = sum(1 for indicator in indicators 
                         if any(indicator in name for name in all_names))
            
            confidence = matches / len(indicators) if indicators else 0
            
            if confidence >= threshold:
                detected_patterns[pattern_name] = {
                    'confidence': confidence,
                    'matches': matches,
                    'total_indicators': len(indicators)
                }
        
        # Determine primary architecture
        if detected_patterns:
            primary_arch = max(detected_patterns.keys(), 
                             key=lambda k: detected_patterns[k]['confidence'])
            primary_confidence = detected_patterns[primary_arch]['confidence']
        else:
            primary_arch = 'unknown'
            primary_confidence = 0.0
        
        return {
            'detected_patterns': detected_patterns,
            'primary_architecture': primary_arch,
            'confidence': primary_confidence
        }
    
    async def _assess_quality_indicators(self, project_path: Path) -> Dict[str, Any]:
        """Assess project quality indicators"""
        quality = {}
        
        for indicator_name, keywords in self.quality_indicators.items():
            found = False
            
            # Check if any directory or file matches the keywords
            for item in project_path.rglob('*'):
                if self._should_ignore(item):
                    continue
                
                item_name = item.name.lower()
                if any(keyword.lower() in item_name for keyword in keywords):
                    found = True
                    break
            
            quality[indicator_name] = found
        
        return quality
    
    async def _calculate_metrics(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate structural metrics"""
        total_files = len(file_info['all_files'])
        total_dirs = len(file_info['directories'])
        
        metrics = {
            'files_per_directory': total_files / max(total_dirs, 1),
            'code_percentage': (file_info['file_types']['code'] / max(total_files, 1)) * 100,
            'config_percentage': (file_info['file_types']['config'] / max(total_files, 1)) * 100,
            'doc_percentage': (file_info['file_types']['documentation'] / max(total_files, 1)) * 100,
            'average_file_size': sum(file_info['file_sizes']) / max(len(file_info['file_sizes']), 1),
            'complexity_score': self._calculate_complexity_score(file_info)
        }
        
        return metrics
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored during analysis"""
        path_str = str(path).lower()
        
        for pattern in self.ignore_patterns:
            if pattern.startswith('*'):
                # Handle wildcard patterns
                if path_str.endswith(pattern[1:]):
                    return True
            elif pattern in path_str:
                return True
        
        return False
    
    def _analyze_depth_patterns(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze depth distribution patterns"""
        depth_dist = file_info['depth_distribution']
        
        if not depth_dist:
            return {'average_depth': 0, 'max_depth': 0, 'distribution': {}}
        
        total_items = sum(depth_dist.values())
        weighted_sum = sum(depth * count for depth, count in depth_dist.items())
        average_depth = weighted_sum / total_items
        
        return {
            'average_depth': average_depth,
            'max_depth': max(depth_dist.keys()),
            'distribution': dict(depth_dist),
            'depth_score': min(100, max(0, 100 - (average_depth - 3) * 20))  # Optimal around depth 3
        }
    
    async def _analyze_directory_organization(self, project_path: Path) -> Dict[str, Any]:
        """Analyze directory organization patterns"""
        try:
            directories = []
            for item in project_path.iterdir():
                if item.is_dir() and not self._should_ignore(item):
                    directories.append(item.name.lower())
            
            # Common organization patterns
            organization_patterns = {
                'src_based': 'src' in directories,
                'lib_based': 'lib' in directories or 'libs' in directories,
                'modular': len([d for d in directories if d not in ['src', 'lib', 'test', 'tests', 'docs']]) > 3,
                'test_separation': any(test_dir in directories for test_dir in ['test', 'tests', '__tests__']),
                'doc_separation': any(doc_dir in directories for doc_dir in ['doc', 'docs', 'documentation'])
            }
            
            organization_score = sum(organization_patterns.values()) / len(organization_patterns) * 100
            
            return {
                'top_level_directories': directories,
                'organization_patterns': organization_patterns,
                'organization_score': organization_score
            }
            
        except Exception as e:
            logger.error(f"Directory organization analysis failed: {e}")
            return {'top_level_directories': [], 'organization_patterns': {}, 'organization_score': 0}
    
    def _analyze_file_distribution(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze file distribution across directories"""
        depth_dist = file_info['depth_distribution']
        total_items = sum(depth_dist.values())
        
        if total_items == 0:
            return {'balance_score': 0, 'distribution_quality': 'poor'}
        
        # Calculate distribution balance
        expected_distribution = {1: 0.2, 2: 0.3, 3: 0.3, 4: 0.15, 5: 0.05}
        balance_score = 0
        
        for depth, expected_ratio in expected_distribution.items():
            actual_ratio = depth_dist.get(depth, 0) / total_items
            balance_score += 100 - abs(expected_ratio - actual_ratio) * 200
        
        balance_score = max(0, balance_score / len(expected_distribution))
        
        quality = 'excellent' if balance_score > 80 else \
                 'good' if balance_score > 60 else \
                 'fair' if balance_score > 40 else 'poor'
        
        return {
            'balance_score': balance_score,
            'distribution_quality': quality,
            'actual_distribution': {str(k): v for k, v in depth_dist.items()}
        }
    
    async def _analyze_naming_consistency(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze naming convention consistency"""
        if not file_info['all_files']:
            return {'consistency_score': 0, 'dominant_pattern': 'none'}
        
        naming_patterns = {
            'snake_case': 0,
            'camelCase': 0,
            'kebab-case': 0,
            'PascalCase': 0,
            'mixed': 0
        }
        
        for file_path in file_info['all_files']:
            file_name = file_path.stem  # Filename without extension
            pattern = self._detect_naming_pattern(file_name)
            naming_patterns[pattern] += 1
        
        total_files = len(file_info['all_files'])
        dominant_pattern = max(naming_patterns.keys(), key=lambda k: naming_patterns[k])
        consistency_score = (naming_patterns[dominant_pattern] / total_files) * 100
        
        return {
            'consistency_score': consistency_score,
            'dominant_pattern': dominant_pattern,
            'pattern_distribution': naming_patterns
        }
    
    def _detect_naming_pattern(self, name: str) -> str:
        """Detect naming pattern of a file/directory name"""
        if '_' in name and name.islower():
            return 'snake_case'
        elif '-' in name and name.islower():
            return 'kebab-case'
        elif name[0].isupper() and any(c.isupper() for c in name[1:]):
            return 'PascalCase'
        elif name[0].islower() and any(c.isupper() for c in name[1:]):
            return 'camelCase'
        else:
            return 'mixed'
    
    def _calculate_average_depth(self, file_info: Dict[str, Any]) -> float:
        """Calculate average depth of files and directories"""
        depth_dist = file_info['depth_distribution']
        if not depth_dist:
            return 0.0
        
        total_items = sum(depth_dist.values())
        weighted_sum = sum(depth * count for depth, count in depth_dist.items())
        return weighted_sum / total_items
    
    def _calculate_organization_score(self, file_info: Dict[str, Any]) -> float:
        """Calculate overall organization score"""
        scores = []
        
        # File type balance score
        total_files = len(file_info['all_files'])
        if total_files > 0:
            code_ratio = file_info['file_types']['code'] / total_files
            config_ratio = file_info['file_types']['config'] / total_files
            doc_ratio = file_info['file_types']['documentation'] / total_files
            
            # Ideal ratios: 60-80% code, 5-15% config, 5-20% docs
            code_score = 100 if 0.6 <= code_ratio <= 0.8 else max(0, 100 - abs(0.7 - code_ratio) * 200)
            config_score = 100 if 0.05 <= config_ratio <= 0.15 else max(0, 100 - abs(0.1 - config_ratio) * 500)
            doc_score = 100 if 0.05 <= doc_ratio <= 0.2 else max(0, 100 - abs(0.1 - doc_ratio) * 400)
            
            scores.extend([code_score, config_score, doc_score])
        
        # Depth score (prefer moderate depth)
        avg_depth = self._calculate_average_depth(file_info)
        depth_score = max(0, 100 - abs(3 - avg_depth) * 25)  # Optimal around depth 3
        scores.append(depth_score)
        
        return sum(scores) / len(scores) if scores else 0
    
    def _analyze_size_distribution(self, file_sizes: List[int]) -> Dict[str, Any]:
        """Analyze file size distribution"""
        if not file_sizes:
            return {'average_size': 0, 'size_consistency': 0}
        
        average_size = sum(file_sizes) / len(file_sizes)
        
        # Categorize sizes
        small_files = sum(1 for size in file_sizes if size < 1024)  # < 1KB
        medium_files = sum(1 for size in file_sizes if 1024 <= size < 10240)  # 1KB - 10KB
        large_files = sum(1 for size in file_sizes if 10240 <= size < 102400)  # 10KB - 100KB
        very_large_files = sum(1 for size in file_sizes if size >= 102400)  # >= 100KB
        
        total_files = len(file_sizes)
        
        return {
            'average_size': average_size,
            'size_distribution': {
                'small': small_files,
                'medium': medium_files,
                'large': large_files,
                'very_large': very_large_files
            },
            'size_percentages': {
                'small': (small_files / total_files) * 100,
                'medium': (medium_files / total_files) * 100,
                'large': (large_files / total_files) * 100,
                'very_large': (very_large_files / total_files) * 100
            }
        }
    
    def _calculate_complexity_score(self, file_info: Dict[str, Any]) -> float:
        """Calculate structural complexity score"""
        total_files = len(file_info['all_files'])
        total_dirs = len(file_info['directories'])
        
        if total_files == 0:
            return 0
        
        # Complexity factors
        size_complexity = min(100, total_files / 10)  # More files = more complex
        depth_complexity = min(100, self._calculate_average_depth(file_info) * 20)  # Deeper = more complex
        type_complexity = min(100, len(file_info['file_types']) * 20)  # More file types = more complex
        
        # Balance with organization benefits
        organization_benefit = max(0, 50 - abs(total_files / max(total_dirs, 1) - 5) * 10)  # Optimal ~5 files per dir
        
        complexity = (size_complexity + depth_complexity + type_complexity - organization_benefit) / 3
        return max(0, min(100, complexity))
    
    async def _calculate_structure_quality(self, structure: Dict[str, Any], 
                                         organization: Dict[str, Any], 
                                         quality: Dict[str, Any]) -> float:
        """Calculate overall structure quality score"""
        scores = []
        
        # Organization score
        scores.append(organization.get('organization_score', 0))
        
        # Depth score
        depth_analysis = structure.get('depth_analysis', {})
        scores.append(depth_analysis.get('depth_score', 0))
        
        # Quality indicators score
        quality_indicators = sum(quality.values())
        total_indicators = len(quality)
        quality_score = (quality_indicators / total_indicators) * 100 if total_indicators > 0 else 0
        scores.append(quality_score)
        
        # Naming consistency score
        naming = structure.get('naming_consistency', {})
        scores.append(naming.get('consistency_score', 0))
        
        return sum(scores) / len(scores) if scores else 0
    
    async def _analyze_naming_conventions(self, project_path: Path) -> Dict[str, Any]:
        """Analyze naming conventions across the project"""
        try:
            file_patterns = defaultdict(int)
            dir_patterns = defaultdict(int)
            
            for item in project_path.rglob('*'):
                if self._should_ignore(item):
                    continue
                
                name = item.stem if item.is_file() else item.name
                pattern = self._detect_naming_pattern(name)
                
                if item.is_file():
                    file_patterns[pattern] += 1
                else:
                    dir_patterns[pattern] += 1
            
            # Determine dominant patterns
            dominant_file_pattern = max(file_patterns.keys(), key=file_patterns.get) if file_patterns else 'none'
            dominant_dir_pattern = max(dir_patterns.keys(), key=dir_patterns.get) if dir_patterns else 'none'
            
            # Calculate consistency scores
            total_files = sum(file_patterns.values())
            total_dirs = sum(dir_patterns.values())
            
            file_consistency = (file_patterns[dominant_file_pattern] / total_files * 100) if total_files > 0 else 0
            dir_consistency = (dir_patterns[dominant_dir_pattern] / total_dirs * 100) if total_dirs > 0 else 0
            
            overall_consistency = (file_consistency + dir_consistency) / 2
            
            return {
                'file_patterns': dict(file_patterns),
                'directory_patterns': dict(dir_patterns),
                'dominant_file_pattern': dominant_file_pattern,
                'dominant_directory_pattern': dominant_dir_pattern,
                'file_consistency': file_consistency,
                'directory_consistency': dir_consistency,
                'confidence': overall_consistency / 100
            }
            
        except Exception as e:
            logger.error(f"Naming convention analysis failed: {e}")
            return {'confidence': 0, 'dominant_file_pattern': 'unknown'}
    
    async def _analyze_file_organization(self, project_path: Path) -> Dict[str, Any]:
        """Analyze file organization patterns"""
        try:
            organization_score = 0
            patterns_found = []
            
            # Check for standard organization patterns
            if (project_path / 'src').exists():
                organization_score += 20
                patterns_found.append('src_directory')
            
            if any((project_path / test_dir).exists() for test_dir in ['test', 'tests', '__tests__']):
                organization_score += 20
                patterns_found.append('test_separation')
            
            if any((project_path / doc_dir).exists() for doc_dir in ['doc', 'docs', 'documentation']):
                organization_score += 15
                patterns_found.append('documentation_separation')
            
            if (project_path / 'config').exists() or (project_path / 'configs').exists():
                organization_score += 10
                patterns_found.append('config_separation')
            
            if any((project_path / util_dir).exists() for util_dir in ['utils', 'utilities', 'tools']):
                organization_score += 10
                patterns_found.append('utility_separation')
            
            # Check for logical grouping
            directories = [d.name for d in project_path.iterdir() if d.is_dir() and not self._should_ignore(d)]
            if len(directories) > 2:
                organization_score += 15
                patterns_found.append('logical_grouping')
            
            return {
                'organization_score': min(100, organization_score),
                'patterns_found': patterns_found,
                'confidence': min(1.0, organization_score / 100)
            }
            
        except Exception as e:
            logger.error(f"File organization analysis failed: {e}")
            return {'organization_score': 0, 'patterns_found': [], 'confidence': 0}
    
    async def _analyze_import_patterns(self, project_path: Path) -> Dict[str, Any]:
        """Analyze import/dependency patterns in code files"""
        try:
            import_patterns = {
                'relative_imports': 0,
                'absolute_imports': 0,
                'external_imports': 0,
                'internal_imports': 0
            }
            
            files_analyzed = 0
            
            # Sample a few code files for import analysis
            for pattern in ['*.py', '*.js', '*.ts']:
                for file_path in list(project_path.rglob(pattern))[:10]:  # Limit to 10 files per type
                    if self._should_ignore(file_path) or file_path.stat().st_size > 100000:
                        continue
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            imports = self._extract_imports(content, file_path.suffix)
                            
                            for import_type, count in imports.items():
                                import_patterns[import_type] += count
                            
                            files_analyzed += 1
                            
                    except Exception as e:
                        logger.debug(f"Error analyzing imports in {file_path}: {e}")
                        continue
            
            # Calculate import quality score
            total_imports = sum(import_patterns.values())
            quality_score = 0
            
            if total_imports > 0:
                # Prefer internal imports over external
                internal_ratio = import_patterns['internal_imports'] / total_imports
                external_ratio = import_patterns['external_imports'] / total_imports
                
                quality_score = internal_ratio * 60 + (1 - external_ratio) * 40
            
            return {
                'import_patterns': import_patterns,
                'files_analyzed': files_analyzed,
                'import_quality_score': quality_score,
                'total_imports': total_imports
            }
            
        except Exception as e:
            logger.error(f"Import pattern analysis failed: {e}")
            return {'import_patterns': {}, 'files_analyzed': 0, 'import_quality_score': 0}
    
    def _extract_imports(self, content: str, file_extension: str) -> Dict[str, int]:
        """Extract import patterns from file content"""
        imports = {
            'relative_imports': 0,
            'absolute_imports': 0,
            'external_imports': 0,
            'internal_imports': 0
        }
        
        lines = content.split('\n')
        
        if file_extension == '.py':
            for line in lines:
                line = line.strip()
                if line.startswith('from .') or line.startswith('from ..'):
                    imports['relative_imports'] += 1
                    imports['internal_imports'] += 1
                elif line.startswith('import ') or line.startswith('from '):
                    if any(lib in line for lib in ['os', 'sys', 'json', 'datetime', 're']):
                        imports['absolute_imports'] += 1
                    elif '.' in line and not line.startswith('from .'):
                        imports['external_imports'] += 1
                    else:
                        imports['internal_imports'] += 1
        
        elif file_extension in ['.js', '.ts']:
            for line in lines:
                line = line.strip()
                if 'require(' in line or 'import ' in line:
                    if line.startswith('./') or line.startswith('../'):
                        imports['relative_imports'] += 1
                        imports['internal_imports'] += 1
                    elif 'node_modules' in line or not ('/' in line or '.' in line):
                        imports['external_imports'] += 1
                    else:
                        imports['internal_imports'] += 1
        
        return imports
    
    async def _determine_architectural_style(self, project_path: Path) -> Dict[str, Any]:
        """Determine overall architectural style"""
        try:
            style_indicators = {
                'monolithic': 0,
                'modular': 0,
                'layered': 0,
                'component_based': 0,
                'microservices': 0
            }
            
            # Analyze directory structure for architectural clues
            directories = [d.name.lower() for d in project_path.iterdir() if d.is_dir() and not self._should_ignore(d)]
            
            # Monolithic indicators
            if 'app' in directories or 'main' in directories or len(directories) <= 3:
                style_indicators['monolithic'] += 30
            
            # Modular indicators
            if len(directories) > 5:
                style_indicators['modular'] += 20
            
            # Layered indicators
            layered_terms = ['service', 'controller', 'model', 'view', 'repository', 'dao']
            if any(term in ' '.join(directories) for term in layered_terms):
                style_indicators['layered'] += 40
            
            # Component-based indicators
            if 'components' in directories or 'widgets' in directories:
                style_indicators['component_based'] += 50
            
            # Microservices indicators
            service_terms = ['api', 'service', 'gateway', 'auth', 'user', 'payment']
            service_matches = sum(1 for term in service_terms if term in directories)
            if service_matches >= 3:
                style_indicators['microservices'] += service_matches * 15
            
            # Determine dominant style
            dominant_style = max(style_indicators.keys(), key=style_indicators.get)
            confidence = style_indicators[dominant_style] / 100.0
            
            return {
                'style': dominant_style,
                'confidence': min(1.0, confidence),
                'style_scores': style_indicators
            }
            
        except Exception as e:
            logger.error(f"Architectural style analysis failed: {e}")
            return {'style': 'unknown', 'confidence': 0.0, 'style_scores': {}}
    
    async def _analyze_code_structure(self, project_path: Path) -> Dict[str, Any]:
        """Analyze code structure and organization"""
        try:
            structure_metrics = {
                'average_file_size': 0,
                'large_files_count': 0,
                'code_files_count': 0,
                'complexity_indicators': []
            }
            
            total_size = 0
            file_count = 0
            
            # Analyze code files
            for pattern in ['*.py', '*.js', '*.ts', '*.java', '*.cpp', '*.c']:
                for file_path in project_path.rglob(pattern):
                    if self._should_ignore(file_path):
                        continue
                    
                    file_size = file_path.stat().st_size
                    total_size += file_size
                    file_count += 1
                    
                    if file_size > 10000:  # Files larger than 10KB
                        structure_metrics['large_files_count'] += 1
                    
                    # Check for complexity indicators
                    if file_size > 50000:  # Very large files might indicate complexity issues
                        structure_metrics['complexity_indicators'].append(f"Large file: {file_path.name}")
            
            structure_metrics['code_files_count'] = file_count
            structure_metrics['average_file_size'] = total_size / file_count if file_count > 0 else 0
            
            # Calculate structure quality
            quality_score = 100
            if structure_metrics['large_files_count'] > file_count * 0.2:  # More than 20% large files
                quality_score -= 30
            
            if structure_metrics['average_file_size'] > 15000:  # Average file size > 15KB
                quality_score -= 20
            
            structure_metrics['structure_quality'] = max(0, quality_score)
            
            return structure_metrics
            
        except Exception as e:
            logger.error(f"Code structure analysis failed: {e}")
            return {'structure_quality': 0, 'code_files_count': 0}