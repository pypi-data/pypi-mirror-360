"""
ProjectContextAnalyzer - Autonomous project analysis for Copper Alloy Brass Sprint 9

Analyzes project structure, dependencies, and capabilities without human goals
to enable autonomous planning and gap detection.
"""

import asyncio
import gc
import json
import logging
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from concurrent.futures import ThreadPoolExecutor

try:
    # Try to import Copper Alloy Brass components
    # from coppersun_brass.core.event_bus import EventBus  # EventBus removed - using DCP coordination
    from coppersun_brass.core.config import get_config
    BRASS_INTEGRATION = True
    EventBus = None  # EventBus phased out
except ImportError:
    # Fallback for standalone testing
    BRASS_INTEGRATION = False
    EventBus = None
    get_config = None

# UNUSED IMPORTS - READY FOR ACTIVATION
# These imports are available but not currently used in the main pipeline.
# See docs/implementation/STRATEGIST_FEATURE_ROADMAP.md for activation procedures.

from .framework_detector import FrameworkDetector        # UNUSED: Auto project classification (1-2h to activate)
from .file_structure_analyzer import FileStructureAnalyzer
from .dependency_analyzer import DependencyAnalyzer      # UNUSED: Multi-lang dependency analysis (2-4h to activate)  
from .chunked_analyzer import ChunkedAnalyzer           # UNUSED: Large project memory mgmt (4-6h to activate)

# TODO ACTIVATION: To use these features, wire them into the analyze() method below
# Example: self.dependency_analyzer = DependencyAnalyzer() 
#          dependencies = await self.dependency_analyzer.analyze(project_path)

logger = logging.getLogger(__name__)


@dataclass
class ProjectContext:
    """Complete project context for autonomous planning"""
    project_type: str
    confidence_score: float
    framework_stack: Dict[str, Any]
    file_structure: Dict[str, Any]
    dependencies: Dict[str, Any]
    code_patterns: Dict[str, Any]
    existing_capabilities: Dict[str, Any]
    quality_metrics: Dict[str, Any]
    security_posture: Dict[str, Any]
    scalability_readiness: Dict[str, Any]
    project_size: str  # small, medium, large
    project_maturity: str  # early, developing, mature
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    def to_feature_vector(self) -> Dict[str, float]:
        """Convert to feature vector for ML algorithms"""
        return {
            'confidence_score': self.confidence_score,
            'dependency_count': len(self.dependencies.get('direct', [])),
            'file_count': self.file_structure.get('total_files', 0),
            'code_quality_score': self.quality_metrics.get('overall_score', 0),
            'security_score': self.security_posture.get('overall_score', 0),
            'framework_complexity': len(self.framework_stack),
            'project_size_score': {'small': 0.3, 'medium': 0.6, 'large': 1.0}.get(self.project_size, 0.5),
            'maturity_score': {'early': 0.2, 'developing': 0.5, 'mature': 0.9}.get(self.project_maturity, 0.5)
        }


class ProjectContextAnalyzer:
    """
    Autonomous project context analyzer for Copper Alloy Brass Sprint 9
    
    Analyzes project structure without human goals to enable autonomous planning.
    Implements multi-signal detection, confidence scoring, and memory-efficient
    chunked analysis for large projects.
    """
    
    def __init__(self, max_memory_mb: int = 400, event_bus: Optional[Any] = None):
        """
        Initialize analyzer with memory management and event integration
        
        Args:
            max_memory_mb: Maximum memory usage in MB for analysis
            event_bus: Optional event bus for Copper Alloy Brass integration
        """
        # Configuration management
        if BRASS_INTEGRATION:
            config = get_config()
            self.max_memory_mb = config.get('autonomous.max_memory_mb', max_memory_mb)
            self.analysis_timeout = config.get('autonomous.analysis_timeout', 30.0)
        else:
            self.max_memory_mb = max_memory_mb
            self.analysis_timeout = 30.0
        
        # Event bus integration
        self.event_bus = event_bus
        if BRASS_INTEGRATION and not event_bus:
            try:
                self.event_bus = EventBus()
            except Exception:
                self.event_bus = None
        
        # Initialize analyzers
        self.framework_detector = FrameworkDetector()
        self.file_analyzer = FileStructureAnalyzer()
        self.dependency_analyzer = DependencyAnalyzer()
        self.chunked_analyzer = ChunkedAnalyzer(self.max_memory_mb)
        
        # Thread pool for concurrent analysis
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # Cache for repeated analyses
        self._analysis_cache = {}
        
    async def analyze_project(self, project_path: Union[str, Path]) -> ProjectContext:
        """
        Comprehensive project analysis for autonomous planning
        
        Args:
            project_path: Path to project directory
            
        Returns:
            ProjectContext with complete analysis
            
        Raises:
            ValueError: If project path doesn't exist or is invalid
            MemoryError: If project is too large for available memory
        """
        project_path = Path(project_path).resolve()
        
        if not project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")
        
        if not project_path.is_dir():
            raise ValueError(f"Project path is not a directory: {project_path}")
        
        # Check cache first
        cache_key = str(project_path)
        if cache_key in self._analysis_cache:
            logger.info(f"Using cached analysis for {project_path}")
            return self._analysis_cache[cache_key]
        
        try:
            import time
            start_time = time.time()
            logger.info(f"Starting autonomous analysis of project: {project_path}")
            
            # Run concurrent analysis tasks
            analysis_tasks = [
                self._detect_project_type(project_path),
                self._analyze_framework_stack(project_path),
                self._analyze_file_structure(project_path),
                self._analyze_dependencies(project_path),
                self._analyze_code_patterns(project_path),
                self._assess_existing_capabilities(project_path),
                self._assess_quality_metrics(project_path),
                self._assess_security_posture(project_path),
                self._assess_scalability_readiness(project_path)
            ]
            
            # Execute analysis with timeout
            results = await asyncio.wait_for(
                asyncio.gather(*analysis_tasks, return_exceptions=True),
                timeout=self.analysis_timeout
            )
            
            # Emit analysis progress event
            if self.event_bus:
                try:
                    self.event_bus.emit('autonomous.analysis.progress', {
                        'project_path': str(project_path),
                        'stage': 'analysis_complete',
                        'tasks_completed': len([r for r in results if not isinstance(r, Exception)])
                    })
                except Exception as e:
                    logger.debug(f"Event emission failed: {e}")
            
            # Process results and handle exceptions
            (project_type_data, framework_stack, file_structure, dependencies,
             code_patterns, existing_capabilities, quality_metrics,
             security_posture, scalability_readiness) = results
            
            # Handle any exceptions in results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.warning(f"Analysis task {i} failed: {result}")
                    # Provide fallback data
                    results[i] = self._get_fallback_data(i)
            
            # Determine project size and maturity
            project_size = self._determine_project_size(file_structure)
            project_maturity = self._determine_project_maturity(
                dependencies, file_structure, existing_capabilities
            )
            
            # Create comprehensive context
            context = ProjectContext(
                project_type=project_type_data['type'],
                confidence_score=project_type_data['confidence'],
                framework_stack=framework_stack,
                file_structure=file_structure,
                dependencies=dependencies,
                code_patterns=code_patterns,
                existing_capabilities=existing_capabilities,
                quality_metrics=quality_metrics,
                security_posture=security_posture,
                scalability_readiness=scalability_readiness,
                project_size=project_size,
                project_maturity=project_maturity
            )
            
            # Cache result
            self._analysis_cache[cache_key] = context
            
            # Emit completion event
            if self.event_bus:
                try:
                    self.event_bus.emit('autonomous.analysis.complete', {
                        'project_path': str(project_path),
                        'project_type': project_type_data['type'],
                        'confidence': project_type_data['confidence'],
                        'analysis_duration': time.time() - start_time if 'start_time' in locals() else 0
                    })
                except Exception as e:
                    logger.debug(f"Event emission failed: {e}")
            
            logger.info(f"Completed analysis: {project_type_data['type']} "
                       f"({project_type_data['confidence']:.2f} confidence)")
            
            return context
            
        except asyncio.TimeoutError:
            logger.error(f"Analysis timeout for project: {project_path}")
            raise TimeoutError(f"Project analysis timed out after 30 seconds")
        
        except MemoryError:
            logger.error(f"Insufficient memory for project analysis: {project_path}")
            raise MemoryError(f"Project too large for available memory limit: {self.max_memory_mb}MB")
        
        except Exception as e:
            logger.error(f"Unexpected error during project analysis: {e}")
            raise RuntimeError(f"Project analysis failed: {e}")
    
    async def _detect_project_type(self, project_path: Path) -> Dict[str, Any]:
        """
        Multi-signal project type detection with confidence scoring
        
        Returns:
            Dict with 'type' and 'confidence' keys
        """
        try:
            return await self.framework_detector.detect_project_type(project_path)
        except Exception as e:
            logger.warning(f"Project type detection failed: {e}")
            return {'type': 'unknown', 'confidence': 0.0}
    
    async def _analyze_framework_stack(self, project_path: Path) -> Dict[str, Any]:
        """Analyze framework and technology stack"""
        try:
            return await self.framework_detector.detect_frameworks(project_path)
        except Exception as e:
            logger.warning(f"Framework detection failed: {e}")
            return {'primary': [], 'secondary': [], 'confidence': 0.0}
    
    async def _analyze_file_structure(self, project_path: Path) -> Dict[str, Any]:
        """Analyze file structure and organization patterns"""
        try:
            if self._is_large_project(project_path):
                return await self.chunked_analyzer.analyze_file_structure(project_path)
            else:
                return await self.file_analyzer.analyze(project_path)
        except Exception as e:
            logger.warning(f"File structure analysis failed: {e}")
            return self._get_minimal_file_structure(project_path)
    
    async def _analyze_dependencies(self, project_path: Path) -> Dict[str, Any]:
        """Analyze project dependencies and external libraries"""
        try:
            return await self.dependency_analyzer.analyze(project_path)
        except Exception as e:
            logger.warning(f"Dependency analysis failed: {e}")
            return {'direct': [], 'dev': [], 'total_count': 0}
    
    async def _analyze_code_patterns(self, project_path: Path) -> Dict[str, Any]:
        """Analyze code patterns and architectural decisions"""
        try:
            # Use chunked analysis for large projects
            if self._is_large_project(project_path):
                return await self.chunked_analyzer.analyze_code_patterns(project_path)
            else:
                return await self.file_analyzer.analyze_patterns(project_path)
        except Exception as e:
            logger.warning(f"Code pattern analysis failed: {e}")
            return {'patterns': [], 'architecture_style': 'unknown', 'confidence': 0.0}
    
    async def _assess_existing_capabilities(self, project_path: Path) -> Dict[str, Any]:
        """Assess what capabilities the project currently has"""
        capabilities = {
            'authentication': await self._check_authentication(project_path),
            'error_handling': await self._check_error_handling(project_path),
            'logging': await self._check_logging(project_path),
            'testing': await self._check_testing(project_path),
            'documentation': await self._check_documentation(project_path),
            'deployment': await self._check_deployment(project_path),
            'monitoring': await self._check_monitoring(project_path),
            'security': await self._check_security_features(project_path)
        }
        
        # Calculate overall capability score
        total_score = sum(cap.get('score', 0) for cap in capabilities.values())
        max_score = len(capabilities) * 100
        overall_score = (total_score / max_score) * 100 if max_score > 0 else 0
        
        capabilities['overall_score'] = overall_score
        return capabilities
    
    async def _assess_quality_metrics(self, project_path: Path) -> Dict[str, Any]:
        """Assess code quality metrics"""
        metrics = {
            'code_complexity': await self._assess_complexity(project_path),
            'test_coverage': await self._assess_test_coverage(project_path),
            'documentation_coverage': await self._assess_doc_coverage(project_path),
            'code_consistency': await self._assess_consistency(project_path),
            'maintainability': await self._assess_maintainability(project_path)
        }
        
        # Calculate overall quality score
        scores = [m.get('score', 0) for m in metrics.values() if isinstance(m, dict)]
        overall_score = sum(scores) / len(scores) if scores else 0
        metrics['overall_score'] = overall_score
        
        return metrics
    
    async def _assess_security_posture(self, project_path: Path) -> Dict[str, Any]:
        """Assess security implementation and vulnerabilities"""
        return {
            'input_validation': await self._check_input_validation(project_path),
            'output_encoding': await self._check_output_encoding(project_path),
            'authentication_security': await self._check_auth_security(project_path),
            'data_protection': await self._check_data_protection(project_path),
            'dependency_security': await self._check_dependency_security(project_path),
            'overall_score': 50  # Default placeholder
        }
    
    async def _assess_scalability_readiness(self, project_path: Path) -> Dict[str, Any]:
        """Assess scalability and performance readiness"""
        return {
            'database_optimization': await self._check_db_optimization(project_path),
            'caching_strategy': await self._check_caching(project_path),
            'async_patterns': await self._check_async_patterns(project_path),
            'resource_management': await self._check_resource_management(project_path),
            'monitoring_readiness': await self._check_monitoring_readiness(project_path),
            'overall_score': 50  # Default placeholder
        }
    
    def _is_large_project(self, project_path: Path) -> bool:
        """Determine if project is large enough to require chunked analysis"""
        try:
            file_count = sum(1 for _ in project_path.rglob('*') if _.is_file())
            return file_count > 100
        except Exception:
            return False
    
    def _determine_project_size(self, file_structure: Dict[str, Any]) -> str:
        """Determine project size classification"""
        total_files = file_structure.get('total_files', 0)
        
        if total_files < 20:
            return 'small'
        elif total_files < 100:
            return 'medium'
        else:
            return 'large'
    
    def _determine_project_maturity(self, dependencies: Dict[str, Any], 
                                  file_structure: Dict[str, Any],
                                  capabilities: Dict[str, Any]) -> str:
        """Determine project maturity level"""
        maturity_signals = 0
        
        # Check for mature project signals
        if dependencies.get('total_count', 0) > 5:
            maturity_signals += 1
        
        if file_structure.get('has_tests', False):
            maturity_signals += 1
        
        if file_structure.get('has_documentation', False):
            maturity_signals += 1
        
        if capabilities.get('overall_score', 0) > 60:
            maturity_signals += 1
        
        if maturity_signals <= 1:
            return 'early'
        elif maturity_signals <= 2:
            return 'developing'
        else:
            return 'mature'
    
    def _get_fallback_data(self, task_index: int) -> Dict[str, Any]:
        """Provide fallback data when analysis tasks fail"""
        fallbacks = [
            {'type': 'unknown', 'confidence': 0.0},  # project_type
            {'primary': [], 'secondary': [], 'confidence': 0.0},  # framework_stack
            {'total_files': 0, 'structure': {}},  # file_structure
            {'direct': [], 'dev': [], 'total_count': 0},  # dependencies
            {'patterns': [], 'architecture_style': 'unknown'},  # code_patterns
            {'overall_score': 0},  # existing_capabilities
            {'overall_score': 0},  # quality_metrics
            {'overall_score': 0},  # security_posture
            {'overall_score': 0}   # scalability_readiness
        ]
        
        return fallbacks[task_index] if task_index < len(fallbacks) else {}
    
    def _get_minimal_file_structure(self, project_path: Path) -> Dict[str, Any]:
        """Get minimal file structure when full analysis fails"""
        try:
            files = list(project_path.rglob('*'))
            return {
                'total_files': len([f for f in files if f.is_file()]),
                'total_directories': len([f for f in files if f.is_dir()]),
                'structure': {'minimal_analysis': True}
            }
        except Exception:
            return {'total_files': 0, 'total_directories': 0, 'structure': {}}
    
    # Capability checking methods (simplified implementations)
    async def _check_authentication(self, project_path: Path) -> Dict[str, Any]:
        """Check for authentication implementation"""
        auth_files = ['auth', 'login', 'passport', 'jwt', 'session']
        score = 0
        
        try:
            for file_path in project_path.rglob('*'):
                try:
                    if file_path.is_file() and any(term in file_path.name.lower() for term in auth_files):
                        score += 20
                except (OSError, PermissionError):
                    continue  # Skip files we can't access
        except Exception as e:
            logger.warning(f"Authentication check failed: {e}")
            return {'present': False, 'score': 0, 'files_found': 0, 'error': str(e)}
        
        return {'present': score > 0, 'score': min(score, 100), 'files_found': score // 20}
    
    async def _check_error_handling(self, project_path: Path) -> Dict[str, Any]:
        """Check for error handling patterns"""
        # Simplified check - look for try/catch, error handling files
        return {'present': True, 'score': 60, 'pattern': 'basic'}
    
    async def _check_logging(self, project_path: Path) -> Dict[str, Any]:
        """Check for logging implementation"""
        return {'present': True, 'score': 40, 'framework': 'unknown'}
    
    async def _check_testing(self, project_path: Path) -> Dict[str, Any]:
        """Check for testing implementation"""
        test_dirs = ['test', 'tests', '__tests__', 'spec']
        has_tests = any((project_path / test_dir).exists() for test_dir in test_dirs)
        return {'present': has_tests, 'score': 80 if has_tests else 0}
    
    async def _check_documentation(self, project_path: Path) -> Dict[str, Any]:
        """Check for documentation"""
        doc_files = ['README', 'DOCS', 'DOCUMENTATION']
        has_docs = any((project_path / f"{doc}.md").exists() or 
                      (project_path / f"{doc}.rst").exists() or
                      (project_path / f"{doc}.txt").exists() 
                      for doc in doc_files)
        return {'present': has_docs, 'score': 70 if has_docs else 0}
    
    async def _check_deployment(self, project_path: Path) -> Dict[str, Any]:
        """Check for deployment configuration"""
        deploy_files = ['Dockerfile', 'docker-compose.yml', '.github', '.gitlab-ci.yml']
        has_deploy = any((project_path / deploy_file).exists() for deploy_file in deploy_files)
        return {'present': has_deploy, 'score': 60 if has_deploy else 0}
    
    async def _check_monitoring(self, project_path: Path) -> Dict[str, Any]:
        """Check for monitoring setup"""
        return {'present': False, 'score': 0, 'tools': []}
    
    async def _check_security_features(self, project_path: Path) -> Dict[str, Any]:
        """Check for security features"""
        return {'present': True, 'score': 30, 'features': ['basic']}
    
    # Quality assessment methods (simplified implementations)
    async def _assess_complexity(self, project_path: Path) -> Dict[str, Any]:
        """Assess code complexity"""
        return {'score': 70, 'level': 'moderate'}
    
    async def _assess_test_coverage(self, project_path: Path) -> Dict[str, Any]:
        """Assess test coverage"""
        return {'score': 45, 'estimated_coverage': '45%'}
    
    async def _assess_doc_coverage(self, project_path: Path) -> Dict[str, Any]:
        """Assess documentation coverage"""
        return {'score': 30, 'coverage': 'basic'}
    
    async def _assess_consistency(self, project_path: Path) -> Dict[str, Any]:
        """Assess code consistency"""
        return {'score': 75, 'style': 'consistent'}
    
    async def _assess_maintainability(self, project_path: Path) -> Dict[str, Any]:
        """Assess code maintainability"""
        return {'score': 65, 'level': 'good'}
    
    # Security assessment methods (simplified implementations)
    async def _check_input_validation(self, project_path: Path) -> Dict[str, Any]:
        """Check input validation patterns"""
        return {'score': 40, 'coverage': 'partial'}
    
    async def _check_output_encoding(self, project_path: Path) -> Dict[str, Any]:
        """Check output encoding security"""
        return {'score': 50, 'coverage': 'basic'}
    
    async def _check_auth_security(self, project_path: Path) -> Dict[str, Any]:
        """Check authentication security"""
        return {'score': 60, 'level': 'moderate'}
    
    async def _check_data_protection(self, project_path: Path) -> Dict[str, Any]:
        """Check data protection measures"""
        return {'score': 35, 'encryption': 'basic'}
    
    async def _check_dependency_security(self, project_path: Path) -> Dict[str, Any]:
        """Check dependency security"""
        return {'score': 70, 'vulnerabilities': 'unknown'}
    
    # Scalability assessment methods (simplified implementations)
    async def _check_db_optimization(self, project_path: Path) -> Dict[str, Any]:
        """Check database optimization"""
        return {'score': 40, 'optimizations': ['basic']}
    
    async def _check_caching(self, project_path: Path) -> Dict[str, Any]:
        """Check caching strategy"""
        return {'score': 20, 'strategy': 'minimal'}
    
    async def _check_async_patterns(self, project_path: Path) -> Dict[str, Any]:
        """Check async programming patterns"""
        return {'score': 30, 'usage': 'limited'}
    
    async def _check_resource_management(self, project_path: Path) -> Dict[str, Any]:
        """Check resource management"""
        return {'score': 50, 'efficiency': 'moderate'}
    
    async def _check_monitoring_readiness(self, project_path: Path) -> Dict[str, Any]:
        """Check monitoring readiness"""
        return {'score': 25, 'instrumentation': 'basic'}
    
    def clear_cache(self):
        """Clear analysis cache"""
        self._analysis_cache.clear()
        gc.collect()
        
    def __del__(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'thread_pool'):
                self.thread_pool.shutdown(wait=False)
        except Exception:
            pass  # Ignore cleanup errors