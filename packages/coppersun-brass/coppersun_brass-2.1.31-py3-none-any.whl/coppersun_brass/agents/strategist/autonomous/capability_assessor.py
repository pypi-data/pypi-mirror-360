"""
CapabilityAssessor - Sprint 9 Week 2 Day 1
Assesses current project capabilities vs best practices with confidence scoring.

Part of the Autonomous Planning Engine that analyzes what a project currently has
versus what it needs based on project type and framework detection.
"""

import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import logging
from datetime import datetime

# Import from Week 1 components
from .context_analyzer import ProjectContext
from .framework_detector import FrameworkDetector
from .file_structure_analyzer import FileStructureAnalyzer

# DCP integration
try:
    from coppersun_brass.core.context.dcp_manager import DCPManager
    DCP_AVAILABLE = True
except ImportError:
    DCP_AVAILABLE = False
    DCPManager = None

logger = logging.getLogger(__name__)


@dataclass
class CapabilityScore:
    """Represents a capability assessment with confidence."""
    name: str
    category: str
    score: float  # 0-100
    confidence: float  # 0-1.0
    details: Dict[str, any]
    missing_components: List[str]
    recommendations: List[str]


@dataclass
class ProjectCapabilities:
    """Overall project capabilities assessment."""
    project_type: str
    assessment_time: datetime
    overall_score: float
    overall_confidence: float
    capabilities: Dict[str, CapabilityScore]
    strengths: List[str]
    weaknesses: List[str]
    critical_gaps: List[str]


class CapabilityAssessor:
    """Assesses project capabilities with confidence scoring."""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.framework_detector = FrameworkDetector()
        self.file_analyzer = FileStructureAnalyzer()
        self.project_root = project_root or Path.cwd()
        
        # Initialize DCP manager if available
        self.dcp_manager = None
        if DCP_AVAILABLE:
            try:
                self.dcp_manager = DCPManager(self.project_root)
                logger.info("DCP integration enabled for CapabilityAssessor")
            except Exception as e:
                logger.warning(f"DCP manager initialization failed: {e}")
        
        # Define capability categories and their checkers
        self.capability_categories = {
            'authentication': self._assess_authentication,
            'testing': self._assess_testing,
            'documentation': self._assess_documentation,
            'security': self._assess_security,
            'error_handling': self._assess_error_handling,
            'logging': self._assess_logging,
            'configuration': self._assess_configuration,
            'database': self._assess_database,
            'api_design': self._assess_api_design,
            'code_quality': self._assess_code_quality,
            'deployment': self._assess_deployment,
            'monitoring': self._assess_monitoring,
            'performance': self._assess_performance,
            'accessibility': self._assess_accessibility,
            'internationalization': self._assess_i18n
        }
        
        # Weight factors for different project types
        self.category_weights = {
            'web_app': {
                'authentication': 0.9,
                'security': 0.95,
                'api_design': 0.85,
                'accessibility': 0.7,
                'performance': 0.8
            },
            'cli_tool': {
                'error_handling': 0.9,
                'configuration': 0.85,
                'documentation': 0.9,
                'testing': 0.8
            },
            'library': {
                'documentation': 0.95,
                'testing': 0.9,
                'code_quality': 0.9,
                'api_design': 0.85
            },
            'api_service': {
                'authentication': 0.95,
                'security': 0.95,
                'api_design': 0.9,
                'monitoring': 0.85,
                'error_handling': 0.9
            }
        }
    
    def _extract_files_from_context(self, context: ProjectContext) -> List[str]:
        """Extract file paths from project context."""
        all_files = []
        
        # Try different ways to get files from context
        if hasattr(context, 'all_files'):
            return context.all_files
        
        # From file_structure
        file_structure = context.file_structure or {}
        
        # Try files_by_type
        files_by_type = file_structure.get('files_by_type', {})
        for file_list in files_by_type.values():
            if isinstance(file_list, list):
                all_files.extend(file_list)
        
        # Try file_tree
        file_tree = file_structure.get('file_tree', {})
        if file_tree:
            all_files.extend(self._extract_files_from_tree(file_tree))
        
        # Try patterns
        patterns = file_structure.get('patterns', {})
        if patterns:
            for pattern_files in patterns.values():
                if isinstance(pattern_files, list):
                    all_files.extend(pattern_files)
        
        return all_files
    
    def _extract_files_from_tree(self, tree: Dict, prefix: str = '') -> List[str]:
        """Recursively extract files from tree structure."""
        files = []
        for name, content in tree.items():
            if isinstance(content, dict):
                files.extend(self._extract_files_from_tree(content, f"{prefix}/{name}"))
            else:
                files.append(f"{prefix}/{name}")
        return files

    async def assess(self, context: ProjectContext) -> ProjectCapabilities:
        """Assess project capabilities based on context analysis."""
        logger.info(f"Assessing capabilities for {context.project_type} project")
        
        start_time = datetime.now()
        capabilities = {}
        
        # Get project-specific weights
        weights = self._get_category_weights(context.project_type)
        
        # Assess each capability category
        tasks = []
        for category, assessor_func in self.capability_categories.items():
            weight = weights.get(category, 0.5)
            if weight > 0.3:  # Only assess relevant categories
                tasks.append(self._assess_category(
                    category, assessor_func, context, weight
                ))
        
        # Run assessments concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Assessment error: {result}")
                continue
            if result:
                capabilities[result.name] = result
        
        # Calculate overall scores
        overall_score, overall_confidence = self._calculate_overall_scores(
            capabilities, weights
        )
        
        # Identify strengths and weaknesses
        strengths = self._identify_strengths(capabilities)
        weaknesses = self._identify_weaknesses(capabilities)
        critical_gaps = self._identify_critical_gaps(capabilities, context)
        
        # Create result
        result = ProjectCapabilities(
            project_type=context.project_type,
            assessment_time=start_time,
            overall_score=overall_score,
            overall_confidence=overall_confidence,
            capabilities=capabilities,
            strengths=strengths,
            weaknesses=weaknesses,
            critical_gaps=critical_gaps
        )
        
        # Write to DCP if available
        if self.dcp_manager:
            try:
                observation = {
                    'type': 'file_analysis',  # Using valid type
                    'priority': 80,  # High priority as number
                    'summary': f"Capability assessment: {len(capabilities)} capabilities for {context.project_type} project",
                    'details': {
                        'project_type': context.project_type,
                        'overall_score': overall_score,
                        'overall_confidence': overall_confidence,
                        'capability_count': len(capabilities),
                        'strength_count': len(strengths),
                        'weakness_count': len(weaknesses),
                        'critical_gap_count': len(critical_gaps),
                        'top_strengths': strengths[:3],
                        'top_weaknesses': weaknesses[:3],
                        'critical_gaps': critical_gaps,
                        'assessment_duration': (datetime.now() - start_time).total_seconds()
                    },
                    'metadata': {
                        'agent': 'capability_assessor',
                        'confidence': overall_confidence,
                        'timestamp': datetime.now().isoformat()
                    }
                }
                
                obs_id = self.dcp_manager.add_observation(
                    observation, 
                    source_agent='capability_assessor'
                )
                logger.info(f"Capability assessment written to DCP: {obs_id}")
                
            except Exception as e:
                logger.error(f"Failed to write to DCP: {e}")
        
        return result

    async def _assess_category(
        self, 
        category: str, 
        assessor_func, 
        context: ProjectContext,
        weight: float
    ) -> Optional[CapabilityScore]:
        """Assess a single capability category."""
        try:
            return await assessor_func(context, weight)
        except Exception as e:
            logger.error(f"Error assessing {category}: {e}")
            return None

    def _get_category_weights(self, project_type: str) -> Dict[str, float]:
        """Get capability weights for project type."""
        default_weights = {category: 0.5 for category in self.capability_categories}
        
        if project_type in self.category_weights:
            weights = default_weights.copy()
            weights.update(self.category_weights[project_type])
            return weights
        
        return default_weights

    async def _assess_authentication(
        self, context: ProjectContext, weight: float
    ) -> CapabilityScore:
        """Assess authentication capabilities."""
        score = 0.0
        confidence = 0.0
        details = {}
        missing = []
        recommendations = []
        
        # Check for auth-related files and patterns
        auth_indicators = {
            'auth_module': ['auth.py', 'authentication.py', 'login.py'],
            'auth_middleware': ['middleware/auth', 'authMiddleware'],
            'auth_config': ['auth.config', 'passport.js', 'jwt.config'],
            'user_model': ['user.py', 'models/user', 'User.js'],
            'session_handling': ['session', 'cookie', 'token'],
            'oauth_support': ['oauth', 'openid', 'saml']
        }
        
        found_indicators = {}
        
        # Extract file list from context
        all_files = self._extract_files_from_context(context)
        
        # Check file structure
        for indicator, patterns in auth_indicators.items():
            found = False
            for pattern in patterns:
                if any(pattern in str(f).lower() for f in all_files):
                    found = True
                    found_indicators[indicator] = True
                    break
            
            if not found and weight > 0.7:
                missing.append(f"No {indicator.replace('_', ' ')} detected")
        
        # Calculate score based on findings
        if found_indicators:
            score = len(found_indicators) / len(auth_indicators) * 100
            confidence = min(0.9, 0.3 + (len(found_indicators) * 0.1))
            
            # Framework-specific checks
            detected_frameworks = []
            if isinstance(context.framework_stack, dict):
                detected = context.framework_stack.get('detected', {})
                if isinstance(detected, dict):
                    detected_frameworks = list(detected.keys())
            
            if 'django' in detected_frameworks:
                if 'user_model' in found_indicators:
                    score += 10
                    details['django_auth'] = True
            elif 'express' in detected_frameworks:
                if 'auth_middleware' in found_indicators:
                    score += 10
                    details['express_auth'] = True
        
        # Recommendations based on project type
        if context.project_type in ['web_app', 'api_service'] and score < 70:
            recommendations.extend([
                "Implement proper authentication system",
                "Add JWT token handling for stateless auth",
                "Consider OAuth2 for third-party integration",
                "Implement rate limiting for auth endpoints"
            ])
        
        details['found_indicators'] = list(found_indicators.keys())
        
        return CapabilityScore(
            name='authentication',
            category='security',
            score=min(100, score),
            confidence=confidence,
            details=details,
            missing_components=missing,
            recommendations=recommendations
        )

    async def _assess_testing(
        self, context: ProjectContext, weight: float
    ) -> CapabilityScore:
        """Assess testing capabilities."""
        score = 0.0
        confidence = 0.0
        details = {}
        missing = []
        recommendations = []
        
        # Testing indicators
        test_indicators = {
            'test_directory': ['test/', 'tests/', '__tests__/', 'spec/'],
            'test_framework': ['pytest', 'jest', 'mocha', 'unittest', 'rspec'],
            'test_config': ['pytest.ini', 'jest.config', '.mocharc', 'karma.conf'],
            'coverage_config': ['.coveragerc', 'coverage', 'nyc.config'],
            'ci_config': ['.github/workflows', '.gitlab-ci', '.travis.yml', 'jenkinsfile'],
            'test_types': {
                'unit': ['test_*.py', '*.test.js', '*.spec.js'],
                'integration': ['integration', 'e2e'],
                'performance': ['bench', 'perf', 'load']
            }
        }
        
        found_indicators = {}
        test_file_count = 0
        
        # Extract files from context
        all_files = self._extract_files_from_context(context)
        
        # Check for test directories and files
        for indicator, patterns in test_indicators.items():
            if indicator == 'test_types':
                found_types = {}
                for test_type, type_patterns in patterns.items():
                    for pattern in type_patterns:
                        if any(pattern in str(f).lower() for f in all_files):
                            found_types[test_type] = True
                            test_file_count += sum(1 for f in all_files 
                                                 if pattern in str(f).lower())
                if found_types:
                    found_indicators['test_types'] = found_types
                    details['test_types'] = list(found_types.keys())
            else:
                for pattern in patterns:
                    if any(pattern in str(f).lower() for f in all_files):
                        found_indicators[indicator] = True
                        break
        
        # Calculate score
        base_indicators = len([k for k in found_indicators if k != 'test_types'])
        if base_indicators > 0:
            score = base_indicators / (len(test_indicators) - 1) * 50
            
            # Bonus for test types
            if 'test_types' in found_indicators:
                test_type_score = len(found_indicators['test_types']) / 3 * 30
                score += test_type_score
            
            # Bonus for test file count
            if test_file_count > 10:
                score += 20
            elif test_file_count > 5:
                score += 10
            
            confidence = min(0.9, 0.4 + (base_indicators * 0.15))
        
        # Check test-to-code ratio
        all_files = self._extract_files_from_context(context)
        src_file_count = len([f for f in all_files 
                            if any(ext in str(f) for ext in ['.py', '.js', '.ts', '.java'])])
        if src_file_count > 0:
            test_ratio = test_file_count / src_file_count
            details['test_to_code_ratio'] = round(test_ratio, 2)
            if test_ratio < 0.2:
                missing.append("Low test coverage (test-to-code ratio < 0.2)")
                recommendations.append("Increase test coverage to at least 50%")
        
        # Missing components
        if 'test_directory' not in found_indicators:
            missing.append("No dedicated test directory")
        if 'test_framework' not in found_indicators:
            missing.append("No test framework detected")
        if 'coverage_config' not in found_indicators:
            missing.append("No code coverage configuration")
            recommendations.append("Add code coverage tracking")
        
        # Framework-specific recommendations
        primary_languages = []
        if isinstance(context.framework_stack, dict):
            primary = context.framework_stack.get('primary', {})
            if isinstance(primary, dict):
                primary_languages = list(primary.keys())
            elif isinstance(primary, list):
                primary_languages = primary
        
        if 'python' in primary_languages:
            if 'pytest' not in str(all_files):
                recommendations.append("Consider using pytest for Python testing")
        elif 'javascript' in primary_languages:
            if 'jest' not in str(all_files):
                recommendations.append("Consider using Jest for JavaScript testing")
        
        details['test_file_count'] = test_file_count
        details['found_indicators'] = list(found_indicators.keys())
        
        return CapabilityScore(
            name='testing',
            category='quality',
            score=min(100, score),
            confidence=confidence,
            details=details,
            missing_components=missing,
            recommendations=recommendations
        )

    async def _assess_documentation(
        self, context: ProjectContext, weight: float
    ) -> CapabilityScore:
        """Assess documentation capabilities."""
        score = 0.0
        confidence = 0.0
        details = {}
        missing = []
        recommendations = []
        
        # Documentation indicators
        doc_indicators = {
            'readme': ['README.md', 'README.rst', 'README.txt'],
            'api_docs': ['api.md', 'openapi.yaml', 'swagger.json', 'apidoc'],
            'guides': ['guide', 'tutorial', 'getting-started', 'quickstart'],
            'architecture': ['ARCHITECTURE.md', 'DESIGN.md', 'architecture/'],
            'contributing': ['CONTRIBUTING.md', 'DEVELOPMENT.md'],
            'changelog': ['CHANGELOG.md', 'HISTORY.md', 'NEWS.md'],
            'code_docs': ['docstring', 'jsdoc', 'javadoc', 'rustdoc']
        }
        
        found_indicators = {}
        doc_quality_score = 0
        
        # Extract files from context
        all_files = self._extract_files_from_context(context)
        
        # Check for documentation files
        for indicator, patterns in doc_indicators.items():
            for pattern in patterns:
                if any(pattern.lower() in str(f).lower() for f in all_files):
                    found_indicators[indicator] = True
                    break
        
        # Calculate base score
        if found_indicators:
            score = len(found_indicators) / len(doc_indicators) * 60
            
            # Check README quality
            readme_files = [f for f in all_files 
                          if 'readme' in str(f).lower()]
            if readme_files:
                # Assume good README if it exists (would check size/content in real impl)
                doc_quality_score += 20
                details['has_readme'] = True
            
            # Check for inline documentation (simplified check)
            primary_languages = []
            if isinstance(context.framework_stack, dict):
                primary = context.framework_stack.get('primary', {})
                if isinstance(primary, dict):
                    primary_languages = list(primary.keys())
                elif isinstance(primary, list):
                    primary_languages = primary
            if primary_languages:
                if 'python' in primary_languages:
                    # Would check for docstrings in real implementation
                    doc_quality_score += 10
                elif 'javascript' in primary_languages:
                    # Would check for JSDoc in real implementation
                    doc_quality_score += 10
            
            score += doc_quality_score
            confidence = min(0.85, 0.3 + (len(found_indicators) * 0.1))
        
        # Missing components
        if 'readme' not in found_indicators:
            missing.append("No README file")
            recommendations.append("Create a comprehensive README.md")
        
        if context.project_type == 'library' and 'api_docs' not in found_indicators:
            missing.append("No API documentation")
            recommendations.append("Add API documentation for public interfaces")
        
        if 'contributing' not in found_indicators and weight > 0.6:
            missing.append("No contribution guidelines")
            recommendations.append("Add CONTRIBUTING.md for open source projects")
        
        # Project-specific recommendations
        if context.project_type == 'web_app' and 'guides' not in found_indicators:
            recommendations.append("Add user guides and tutorials")
        
        details['found_indicators'] = list(found_indicators.keys())
        details['documentation_score'] = doc_quality_score
        
        return CapabilityScore(
            name='documentation',
            category='quality',
            score=min(100, score),
            confidence=confidence,
            details=details,
            missing_components=missing,
            recommendations=recommendations
        )

    async def _assess_security(
        self, context: ProjectContext, weight: float
    ) -> CapabilityScore:
        """Assess security capabilities."""
        score = 0.0
        confidence = 0.0
        details = {}
        missing = []
        recommendations = []
        
        # Security indicators
        security_indicators = {
            'security_config': ['security.config', 'security.py', 'security.js'],
            'env_handling': ['.env.example', 'config/secrets', 'vault'],
            'input_validation': ['validate', 'sanitize', 'validator'],
            'csrf_protection': ['csrf', 'xsrf', 'anti-forgery'],
            'security_headers': ['helmet', 'security-headers', 'csp'],
            'dependency_check': ['snyk', 'safety', 'audit', 'dependabot'],
            'encryption': ['crypto', 'encrypt', 'bcrypt', 'argon2']
        }
        
        found_indicators = {}
        security_risks = []
        
        # Extract files from context
        all_files = self._extract_files_from_context(context)
        
        # Check for security patterns
        for indicator, patterns in security_indicators.items():
            for pattern in patterns:
                if any(pattern.lower() in str(f).lower() for f in all_files):
                    found_indicators[indicator] = True
                    break
        
        # Check for common security issues
        if any('.env' in str(f) and '.example' not in str(f) 
               for f in all_files):
            security_risks.append(".env file in repository")
            missing.append("Environment variables not properly handled")
        
        # Calculate score
        if found_indicators:
            score = len(found_indicators) / len(security_indicators) * 70
            
            # Bonus for no detected risks
            if not security_risks:
                score += 30
            else:
                score -= len(security_risks) * 10
            
            confidence = min(0.8, 0.3 + (len(found_indicators) * 0.1))
        
        # Web app specific checks
        if context.project_type in ['web_app', 'api_service']:
            if 'csrf_protection' not in found_indicators:
                missing.append("No CSRF protection detected")
                recommendations.append("Implement CSRF protection for forms")
            
            if 'security_headers' not in found_indicators:
                missing.append("No security headers configuration")
                recommendations.append("Add security headers (CSP, HSTS, etc.)")
            
            if 'input_validation' not in found_indicators:
                missing.append("No input validation detected")
                recommendations.append("Implement comprehensive input validation")
        
        # General recommendations
        if 'dependency_check' not in found_indicators:
            recommendations.append("Add automated dependency vulnerability scanning")
        
        if 'encryption' not in found_indicators and weight > 0.7:
            recommendations.append("Use proper encryption for sensitive data")
        
        details['found_indicators'] = list(found_indicators.keys())
        details['security_risks'] = security_risks
        
        return CapabilityScore(
            name='security',
            category='security',
            score=max(0, min(100, score)),
            confidence=confidence,
            details=details,
            missing_components=missing,
            recommendations=recommendations
        )

    async def _assess_error_handling(
        self, context: ProjectContext, weight: float
    ) -> CapabilityScore:
        """Assess error handling capabilities."""
        score = 0.0
        confidence = 0.0
        details = {}
        missing = []
        recommendations = []
        
        # Error handling indicators
        error_indicators = {
            'error_handlers': ['error_handler', 'exception_handler', 'catch'],
            'error_middleware': ['errorMiddleware', 'error-handler', 'middleware/error'],
            'error_logging': ['logger.error', 'console.error', 'log.error'],
            'custom_errors': ['CustomError', 'AppError', 'exceptions.py'],
            'error_pages': ['404', '500', 'error.html', 'error.tsx'],
            'validation_errors': ['ValidationError', 'validate', 'validator']
        }
        
        found_indicators = {}
        
        # Extract files from context
        all_files = self._extract_files_from_context(context)
        
        # Check for error handling patterns
        for indicator, patterns in error_indicators.items():
            for pattern in patterns:
                if any(pattern.lower() in str(f).lower() for f in all_files):
                    found_indicators[indicator] = True
                    break
        
        # Calculate score
        if found_indicators:
            score = len(found_indicators) / len(error_indicators) * 80
            
            # Framework-specific bonuses
            detected_frameworks = []
            if isinstance(context.framework_stack, dict):
                detected = context.framework_stack.get('detected', {})
                if isinstance(detected, dict):
                    detected_frameworks = list(detected.keys())
            if 'express' in detected_frameworks and 'error_middleware' in found_indicators:
                score += 10
            elif 'django' in detected_frameworks and 'error_handlers' in found_indicators:
                score += 10
            
            confidence = min(0.75, 0.3 + (len(found_indicators) * 0.1))
        
        # CLI tool specific requirements
        if context.project_type == 'cli_tool':
            if 'error_handlers' not in found_indicators:
                missing.append("No comprehensive error handling")
                recommendations.append("Add try-catch blocks for all user operations")
            
            if 'custom_errors' not in found_indicators:
                recommendations.append("Create custom error classes for better debugging")
        
        # Web app requirements
        if context.project_type == 'web_app':
            if 'error_pages' not in found_indicators:
                missing.append("No custom error pages")
                recommendations.append("Add user-friendly error pages (404, 500)")
        
        # General recommendations
        if 'error_logging' not in found_indicators:
            missing.append("No error logging detected")
            recommendations.append("Implement structured error logging")
        
        details['found_indicators'] = list(found_indicators.keys())
        
        return CapabilityScore(
            name='error_handling',
            category='reliability',
            score=min(100, score),
            confidence=confidence,
            details=details,
            missing_components=missing,
            recommendations=recommendations
        )

    async def _assess_logging(
        self, context: ProjectContext, weight: float
    ) -> CapabilityScore:
        """Assess logging capabilities."""
        score = 0.0
        confidence = 0.0
        details = {}
        missing = []
        recommendations = []
        
        # Logging indicators
        logging_indicators = {
            'logging_config': ['logging.conf', 'log4j', 'winston.config', 'logback.xml'],
            'logger_usage': ['logger', 'logging', 'log.info', 'console.log'],
            'structured_logging': ['json', 'structured', 'logfmt'],
            'log_levels': ['debug', 'info', 'warn', 'error', 'critical'],
            'log_rotation': ['rotate', 'daily', 'size', 'maxFiles'],
            'centralized_logging': ['elasticsearch', 'logstash', 'fluentd', 'datadog']
        }
        
        found_indicators = {}
        
        # Extract files from context
        all_files = self._extract_files_from_context(context)
        
        # Check for logging patterns
        for indicator, patterns in logging_indicators.items():
            for pattern in patterns:
                if any(pattern.lower() in str(f).lower() for f in all_files):
                    found_indicators[indicator] = True
                    break
        
        # Calculate score
        if found_indicators:
            score = len(found_indicators) / len(logging_indicators) * 70
            
            # Bonus for structured logging
            if 'structured_logging' in found_indicators:
                score += 20
            
            # Bonus for proper log levels
            if 'log_levels' in found_indicators:
                score += 10
            
            confidence = min(0.7, 0.3 + (len(found_indicators) * 0.1))
        
        # Missing components
        if 'logging_config' not in found_indicators:
            missing.append("No logging configuration file")
            recommendations.append("Add centralized logging configuration")
        
        if 'log_rotation' not in found_indicators:
            missing.append("No log rotation strategy")
            recommendations.append("Implement log rotation to prevent disk space issues")
        
        # Production recommendations
        if context.project_type in ['web_app', 'api_service']:
            if 'centralized_logging' not in found_indicators:
                recommendations.append("Consider centralized logging for production")
            
            if 'structured_logging' not in found_indicators:
                recommendations.append("Use structured logging (JSON) for better parsing")
        
        details['found_indicators'] = list(found_indicators.keys())
        
        return CapabilityScore(
            name='logging',
            category='observability',
            score=min(100, score),
            confidence=confidence,
            details=details,
            missing_components=missing,
            recommendations=recommendations
        )

    async def _assess_configuration(
        self, context: ProjectContext, weight: float
    ) -> CapabilityScore:
        """Assess configuration management capabilities."""
        score = 0.0
        confidence = 0.0
        details = {}
        missing = []
        recommendations = []
        
        # Extract files from context
        all_files = self._extract_files_from_context(context)
        
        # Configuration indicators
        config_indicators = {
            'config_files': ['config/', 'settings.py', 'config.js', 'application.yml'],
            'env_files': ['.env.example', '.env.template', 'env.sample'],
            'config_validation': ['schema', 'validate', 'config-validator'],
            'environment_handling': ['development', 'staging', 'production'],
            'secrets_management': ['vault', 'secret', 'kms', 'encrypted'],
            'config_documentation': ['config.md', 'configuration.md', 'settings.md']
        }
        
        found_indicators = {}
        
        # Check for configuration patterns
        for indicator, patterns in config_indicators.items():
            for pattern in patterns:
                if any(pattern.lower() in str(f).lower() for f in all_files):
                    found_indicators[indicator] = True
                    break
        
        # Calculate score
        if found_indicators:
            score = len(found_indicators) / len(config_indicators) * 80
            
            # Check for environment-specific configs
            env_configs = ['dev', 'test', 'staging', 'prod', 'production']
            env_count = sum(1 for env in env_configs 
                          if any(env in str(f).lower() for f in all_files))
            if env_count >= 3:
                score += 20
                details['multi_environment'] = True
            
            confidence = min(0.75, 0.3 + (len(found_indicators) * 0.1))
        
        # Missing components
        if 'env_files' not in found_indicators:
            missing.append("No environment template file")
            recommendations.append("Add .env.example with all required variables")
        
        if 'config_validation' not in found_indicators:
            missing.append("No configuration validation")
            recommendations.append("Add schema validation for configuration")
        
        # CLI tool specific
        if context.project_type == 'cli_tool':
            if 'config_files' not in found_indicators:
                recommendations.append("Support configuration files for CLI options")
        
        details['found_indicators'] = list(found_indicators.keys())
        
        return CapabilityScore(
            name='configuration',
            category='infrastructure',
            score=min(100, score),
            confidence=confidence,
            details=details,
            missing_components=missing,
            recommendations=recommendations
        )

    async def _assess_database(
        self, context: ProjectContext, weight: float
    ) -> CapabilityScore:
        """Assess database capabilities."""
        score = 0.0
        confidence = 0.0
        details = {}
        missing = []
        recommendations = []
        
        # Extract files from context
        all_files = self._extract_files_from_context(context)
        
        # Database indicators
        db_indicators = {
            'orm_models': ['models/', 'model.py', 'schema.js', 'entity/'],
            'migrations': ['migrations/', 'migrate', 'alembic', 'flyway'],
            'db_config': ['database.config', 'db.js', 'database.yml'],
            'connection_pooling': ['pool', 'connectionPool', 'datasource'],
            'query_optimization': ['index', 'optimize', 'explain', 'query-builder'],
            'backup_strategy': ['backup', 'dump', 'restore', 'snapshot']
        }
        
        found_indicators = {}
        
        # Check for database patterns
        for indicator, patterns in db_indicators.items():
            for pattern in patterns:
                if any(pattern.lower() in str(f).lower() for f in all_files):
                    found_indicators[indicator] = True
                    break
        
        # Detect database type
        db_types = {
            'postgresql': ['psycopg', 'postgres', 'pg'],
            'mysql': ['mysql', 'maria'],
            'mongodb': ['mongo', 'mongoose'],
            'sqlite': ['sqlite'],
            'redis': ['redis']
        }
        
        detected_dbs = []
        for db_type, patterns in db_types.items():
            for pattern in patterns:
                if any(pattern in str(f).lower() for f in all_files):
                    detected_dbs.append(db_type)
                    break
        
        details['detected_databases'] = detected_dbs
        
        # Calculate score
        if found_indicators or detected_dbs:
            base_score = len(found_indicators) / len(db_indicators) * 60
            
            # Bonus for migrations
            if 'migrations' in found_indicators:
                base_score += 20
            
            # Bonus for connection pooling
            if 'connection_pooling' in found_indicators:
                base_score += 10
            
            # Bonus for backup strategy
            if 'backup_strategy' in found_indicators:
                base_score += 10
            
            score = base_score
            confidence = min(0.8, 0.4 + (len(found_indicators) * 0.1))
        
        # Missing components for apps that need databases
        if context.project_type in ['web_app', 'api_service']:
            if not detected_dbs:
                details['needs_database'] = True
                if weight > 0.5:
                    recommendations.append("Consider database requirements for data persistence")
            else:
                if 'migrations' not in found_indicators:
                    missing.append("No database migration system")
                    recommendations.append("Implement database migrations for schema changes")
                
                if 'connection_pooling' not in found_indicators:
                    missing.append("No connection pooling detected")
                    recommendations.append("Add connection pooling for better performance")
        
        details['found_indicators'] = list(found_indicators.keys())
        
        return CapabilityScore(
            name='database',
            category='data',
            score=min(100, score),
            confidence=confidence,
            details=details,
            missing_components=missing,
            recommendations=recommendations
        )

    async def _assess_api_design(
        self, context: ProjectContext, weight: float
    ) -> CapabilityScore:
        """Assess API design capabilities."""
        score = 0.0
        confidence = 0.0
        details = {}
        missing = []
        recommendations = []
        
        # Extract files from context
        all_files = self._extract_files_from_context(context)
        
        # API design indicators
        api_indicators = {
            'api_routes': ['routes/', 'api/', 'endpoints/', 'controllers/'],
            'api_documentation': ['swagger', 'openapi', 'apispec', 'redoc'],
            'api_versioning': ['v1/', 'v2/', 'version', 'api-version'],
            'rate_limiting': ['rate-limit', 'throttle', 'quota'],
            'api_validation': ['joi', 'yup', 'jsonschema', 'marshmallow'],
            'api_testing': ['postman', 'insomnia', 'api-test', 'request.test']
        }
        
        found_indicators = {}
        
        # Check for API patterns
        for indicator, patterns in api_indicators.items():
            for pattern in patterns:
                if any(pattern.lower() in str(f).lower() for f in all_files):
                    found_indicators[indicator] = True
                    break
        
        # Check for RESTful patterns
        rest_methods = ['get', 'post', 'put', 'patch', 'delete']
        rest_count = sum(1 for method in rest_methods 
                        if any(method.upper() in str(f) for f in all_files))
        if rest_count >= 3:
            details['rest_api'] = True
            score += 20
        
        # Calculate score
        if found_indicators:
            score += len(found_indicators) / len(api_indicators) * 60
            
            # Bonus for API documentation
            if 'api_documentation' in found_indicators:
                score += 20
            
            confidence = min(0.85, 0.4 + (len(found_indicators) * 0.1))
        
        # API service requirements
        if context.project_type == 'api_service' or 'api_routes' in found_indicators:
            if 'api_documentation' not in found_indicators:
                missing.append("No API documentation (OpenAPI/Swagger)")
                recommendations.append("Add OpenAPI/Swagger documentation")
            
            if 'api_versioning' not in found_indicators:
                missing.append("No API versioning strategy")
                recommendations.append("Implement API versioning for backward compatibility")
            
            if 'rate_limiting' not in found_indicators:
                missing.append("No rate limiting")
                recommendations.append("Add rate limiting to prevent abuse")
            
            if 'api_validation' not in found_indicators:
                missing.append("No request validation")
                recommendations.append("Implement request validation middleware")
        
        details['found_indicators'] = list(found_indicators.keys())
        
        return CapabilityScore(
            name='api_design',
            category='architecture',
            score=min(100, score),
            confidence=confidence,
            details=details,
            missing_components=missing,
            recommendations=recommendations
        )

    async def _assess_code_quality(
        self, context: ProjectContext, weight: float
    ) -> CapabilityScore:
        """Assess code quality capabilities."""
        score = 0.0
        confidence = 0.0
        details = {}
        missing = []
        recommendations = []
        
        # Extract files and languages from context
        all_files = self._extract_files_from_context(context)
        primary_languages = []
        if isinstance(context.framework_stack, dict):
            primary = context.framework_stack.get('primary', {})
            if isinstance(primary, dict):
                primary_languages = list(primary.keys())
            elif isinstance(primary, list):
                primary_languages = primary
        
        # Code quality indicators
        quality_indicators = {
            'linting': ['.eslintrc', 'pylintrc', '.flake8', 'tslint.json'],
            'formatting': ['.prettierrc', '.black', '.rustfmt', '.editorconfig'],
            'type_checking': ['tsconfig.json', 'mypy.ini', '.flowconfig'],
            'code_review': ['.github/pull_request_template', 'reviewers'],
            'complexity_analysis': ['sonar', 'codeclimate', 'complexity'],
            'git_hooks': ['.husky/', 'pre-commit', '.git-hooks/']
        }
        
        found_indicators = {}
        
        # Check for quality patterns
        for indicator, patterns in quality_indicators.items():
            for pattern in patterns:
                if any(pattern.lower() in str(f).lower() for f in all_files):
                    found_indicators[indicator] = True
                    break
        
        # Calculate score
        if found_indicators:
            score = len(found_indicators) / len(quality_indicators) * 70
            
            # Language-specific bonuses
            if 'typescript' in primary_languages and 'type_checking' in found_indicators:
                score += 15
            elif 'python' in primary_languages and 'type_checking' in found_indicators:
                score += 15
            
            # Bonus for pre-commit hooks
            if 'git_hooks' in found_indicators:
                score += 15
            
            confidence = min(0.8, 0.4 + (len(found_indicators) * 0.1))
        
        # Missing components
        if 'linting' not in found_indicators:
            missing.append("No code linting configuration")
            recommendations.append("Add linting rules for code consistency")
        
        if 'formatting' not in found_indicators:
            missing.append("No code formatting configuration")
            recommendations.append("Add automatic code formatting")
        
        # Language-specific recommendations
        primary_languages = []
        if isinstance(context.framework_stack, dict):
            primary = context.framework_stack.get('primary', {})
            if isinstance(primary, dict):
                primary_languages = list(primary.keys())
            elif isinstance(primary, list):
                primary_languages = primary
        
        if 'javascript' in primary_languages or 'typescript' in primary_languages:
            if 'type_checking' not in found_indicators and 'typescript' not in primary_languages:
                recommendations.append("Consider TypeScript for better type safety")
        
        details['found_indicators'] = list(found_indicators.keys())
        
        return CapabilityScore(
            name='code_quality',
            category='quality',
            score=min(100, score),
            confidence=confidence,
            details=details,
            missing_components=missing,
            recommendations=recommendations
        )

    async def _assess_deployment(
        self, context: ProjectContext, weight: float
    ) -> CapabilityScore:
        """Assess deployment capabilities."""
        score = 0.0
        confidence = 0.0
        details = {}
        missing = []
        recommendations = []
        
        # Extract files from context
        all_files = self._extract_files_from_context(context)
        
        # Deployment indicators
        deployment_indicators = {
            'containerization': ['Dockerfile', 'docker-compose', '.dockerignore'],
            'ci_cd': ['.github/workflows', '.gitlab-ci', 'Jenkinsfile', '.circleci'],
            'cloud_config': ['app.yaml', 'serverless.yml', 'terraform/', '.ebextensions'],
            'build_scripts': ['build.sh', 'deploy.sh', 'Makefile', 'package.json'],
            'environment_config': ['prod.env', 'staging.env', '.env.production'],
            'monitoring_setup': ['newrelic', 'datadog', 'prometheus', 'grafana']
        }
        
        found_indicators = {}
        
        # Check for deployment patterns
        for indicator, patterns in deployment_indicators.items():
            for pattern in patterns:
                if any(pattern.lower() in str(f).lower() for f in all_files):
                    found_indicators[indicator] = True
                    break
        
        # Detect deployment platforms
        platforms = {
            'heroku': ['Procfile', 'app.json'],
            'aws': ['cloudformation', 'sam.yaml', '.ebextensions'],
            'gcp': ['app.yaml', 'cloudbuild.yaml'],
            'azure': ['azure-pipelines.yml', '.deployment'],
            'kubernetes': ['k8s/', 'helm/', '.yaml']
        }
        
        detected_platforms = []
        for platform, patterns in platforms.items():
            for pattern in patterns:
                if any(pattern in str(f).lower() for f in all_files):
                    detected_platforms.append(platform)
                    break
        
        details['deployment_platforms'] = detected_platforms
        
        # Calculate score
        if found_indicators or detected_platforms:
            score = len(found_indicators) / len(deployment_indicators) * 60
            
            # Bonus for containerization
            if 'containerization' in found_indicators:
                score += 20
            
            # Bonus for CI/CD
            if 'ci_cd' in found_indicators:
                score += 20
            
            confidence = min(0.75, 0.3 + (len(found_indicators) * 0.1))
        
        # Missing components
        if 'containerization' not in found_indicators and weight > 0.5:
            missing.append("No containerization (Docker)")
            recommendations.append("Add Dockerfile for consistent deployments")
        
        if 'ci_cd' not in found_indicators:
            missing.append("No CI/CD pipeline")
            recommendations.append("Set up CI/CD for automated testing and deployment")
        
        if context.project_type in ['web_app', 'api_service']:
            if 'monitoring_setup' not in found_indicators:
                recommendations.append("Add application monitoring for production")
        
        details['found_indicators'] = list(found_indicators.keys())
        
        return CapabilityScore(
            name='deployment',
            category='infrastructure',
            score=min(100, score),
            confidence=confidence,
            details=details,
            missing_components=missing,
            recommendations=recommendations
        )

    async def _assess_monitoring(
        self, context: ProjectContext, weight: float
    ) -> CapabilityScore:
        """Assess monitoring and observability capabilities."""
        score = 0.0
        confidence = 0.0
        details = {}
        missing = []
        recommendations = []
        
        # Extract files from context
        all_files = self._extract_files_from_context(context)
        
        # Monitoring indicators
        monitoring_indicators = {
            'apm': ['newrelic', 'datadog', 'appdynamics', 'dynatrace'],
            'metrics': ['prometheus', 'statsd', 'metrics', 'cloudwatch'],
            'tracing': ['opentelemetry', 'jaeger', 'zipkin', 'xray'],
            'health_checks': ['health', 'healthz', 'ping', 'status'],
            'alerting': ['pagerduty', 'opsgenie', 'alerts.yml'],
            'dashboards': ['grafana', 'kibana', 'dashboard']
        }
        
        found_indicators = {}
        
        # Check for monitoring patterns
        for indicator, patterns in monitoring_indicators.items():
            for pattern in patterns:
                if any(pattern.lower() in str(f).lower() for f in all_files):
                    found_indicators[indicator] = True
                    break
        
        # Calculate score
        if found_indicators:
            score = len(found_indicators) / len(monitoring_indicators) * 80
            
            # Bonus for health checks (critical)
            if 'health_checks' in found_indicators:
                score += 20
            
            confidence = min(0.7, 0.3 + (len(found_indicators) * 0.1))
        
        # Production app requirements
        if context.project_type in ['web_app', 'api_service']:
            if 'health_checks' not in found_indicators:
                missing.append("No health check endpoints")
                recommendations.append("Add health check endpoints for monitoring")
            
            if 'metrics' not in found_indicators:
                missing.append("No metrics collection")
                recommendations.append("Implement metrics collection (response times, errors)")
            
            if 'apm' not in found_indicators and weight > 0.7:
                recommendations.append("Consider APM solution for production monitoring")
        
        details['found_indicators'] = list(found_indicators.keys())
        
        return CapabilityScore(
            name='monitoring',
            category='observability',
            score=min(100, score),
            confidence=confidence,
            details=details,
            missing_components=missing,
            recommendations=recommendations
        )

    async def _assess_performance(
        self, context: ProjectContext, weight: float
    ) -> CapabilityScore:
        """Assess performance optimization capabilities."""
        score = 0.0
        confidence = 0.0
        details = {}
        missing = []
        recommendations = []
        
        # Extract files from context
        all_files = self._extract_files_from_context(context)
        
        # Performance indicators
        perf_indicators = {
            'caching': ['cache', 'redis', 'memcached', 'cdn'],
            'optimization': ['optimize', 'minify', 'compress', 'webpack'],
            'lazy_loading': ['lazy', 'defer', 'async', 'dynamic-import'],
            'database_optimization': ['index', 'query-optimization', 'connection-pool'],
            'performance_testing': ['lighthouse', 'loadtest', 'jmeter', 'k6'],
            'bundling': ['webpack', 'rollup', 'parcel', 'vite']
        }
        
        found_indicators = {}
        
        # Check for performance patterns
        for indicator, patterns in perf_indicators.items():
            for pattern in patterns:
                if any(pattern.lower() in str(f).lower() for f in all_files):
                    found_indicators[indicator] = True
                    break
        
        # Calculate score
        if found_indicators:
            score = len(found_indicators) / len(perf_indicators) * 80
            
            # Web app specific bonuses
            if context.project_type == 'web_app':
                if 'bundling' in found_indicators:
                    score += 10
                if 'lazy_loading' in found_indicators:
                    score += 10
            
            confidence = min(0.7, 0.3 + (len(found_indicators) * 0.1))
        
        # Missing components
        if context.project_type == 'web_app':
            if 'caching' not in found_indicators:
                missing.append("No caching strategy")
                recommendations.append("Implement caching (browser, CDN, application)")
            
            if 'optimization' not in found_indicators:
                missing.append("No asset optimization")
                recommendations.append("Add build-time optimization for assets")
            
            if 'bundling' not in found_indicators:
                missing.append("No module bundling")
                recommendations.append("Use module bundler for optimization")
        
        if context.project_type in ['api_service', 'web_app']:
            if 'database_optimization' not in found_indicators and 'database' in self.capability_categories:
                recommendations.append("Optimize database queries and add indexes")
        
        details['found_indicators'] = list(found_indicators.keys())
        
        return CapabilityScore(
            name='performance',
            category='optimization',
            score=min(100, score),
            confidence=confidence,
            details=details,
            missing_components=missing,
            recommendations=recommendations
        )

    async def _assess_accessibility(
        self, context: ProjectContext, weight: float
    ) -> CapabilityScore:
        """Assess accessibility capabilities."""
        score = 0.0
        confidence = 0.0
        details = {}
        missing = []
        recommendations = []
        
        # Extract files from context
        all_files = self._extract_files_from_context(context)
        
        # Accessibility indicators
        a11y_indicators = {
            'a11y_testing': ['axe', 'pa11y', 'lighthouse', 'wave'],
            'aria_usage': ['aria-', 'role=', 'accessibility'],
            'semantic_html': ['<header', '<nav', '<main', '<footer', '<article'],
            'alt_text': ['alt=', 'aria-label', 'title='],
            'focus_management': ['focus', 'tabindex', 'keyboard'],
            'a11y_config': ['.a11yrc', 'accessibility.config']
        }
        
        found_indicators = {}
        
        # Only check for web apps
        if context.project_type == 'web_app':
            # Check for accessibility patterns
            for indicator, patterns in a11y_indicators.items():
                for pattern in patterns:
                    if any(pattern.lower() in str(f).lower() for f in all_files):
                        found_indicators[indicator] = True
                        break
            
            # Calculate score
            if found_indicators:
                score = len(found_indicators) / len(a11y_indicators) * 100
                confidence = min(0.65, 0.3 + (len(found_indicators) * 0.1))
            
            # Missing components
            if 'a11y_testing' not in found_indicators:
                missing.append("No accessibility testing tools")
                recommendations.append("Add automated accessibility testing")
            
            if 'aria_usage' not in found_indicators:
                missing.append("No ARIA attributes detected")
                recommendations.append("Use ARIA attributes for screen readers")
            
            if 'semantic_html' not in found_indicators:
                recommendations.append("Use semantic HTML elements")
        else:
            # Not applicable for non-web projects
            score = 100
            confidence = 0.1
            details['not_applicable'] = True
        
        details['found_indicators'] = list(found_indicators.keys())
        
        return CapabilityScore(
            name='accessibility',
            category='user_experience',
            score=min(100, score),
            confidence=confidence,
            details=details,
            missing_components=missing,
            recommendations=recommendations
        )

    async def _assess_i18n(
        self, context: ProjectContext, weight: float
    ) -> CapabilityScore:
        """Assess internationalization capabilities."""
        score = 0.0
        confidence = 0.0
        details = {}
        missing = []
        recommendations = []
        
        # Extract files from context
        all_files = self._extract_files_from_context(context)
        
        # i18n indicators
        i18n_indicators = {
            'i18n_library': ['i18n', 'intl', 'react-i18n', 'vue-i18n', 'gettext'],
            'locale_files': ['locales/', 'lang/', 'translations/', '.po', '.json'],
            'i18n_config': ['i18n.config', 'i18next', 'locale.config'],
            'date_formatting': ['moment', 'date-fns', 'intl.dateformat'],
            'currency_handling': ['currency', 'intl.numberformat', 'money'],
            'rtl_support': ['rtl', 'direction', 'bidi']
        }
        
        found_indicators = {}
        
        # Check for i18n patterns
        for indicator, patterns in i18n_indicators.items():
            for pattern in patterns:
                if any(pattern.lower() in str(f).lower() for f in all_files):
                    found_indicators[indicator] = True
                    break
        
        # Calculate score
        if found_indicators:
            score = len(found_indicators) / len(i18n_indicators) * 100
            confidence = min(0.6, 0.3 + (len(found_indicators) * 0.1))
        elif weight < 0.5:
            # i18n might not be needed for all projects
            score = 70
            confidence = 0.2
            details['optional'] = True
        
        # Web app specific
        if context.project_type == 'web_app' and weight > 0.6:
            if 'i18n_library' not in found_indicators:
                missing.append("No i18n library detected")
                recommendations.append("Add internationalization support for global reach")
            
            if 'locale_files' not in found_indicators:
                missing.append("No translation files")
                recommendations.append("Create translation files for supported languages")
        
        details['found_indicators'] = list(found_indicators.keys())
        
        return CapabilityScore(
            name='internationalization',
            category='user_experience',
            score=min(100, score),
            confidence=confidence,
            details=details,
            missing_components=missing,
            recommendations=recommendations
        )

    def _calculate_overall_scores(
        self, 
        capabilities: Dict[str, CapabilityScore],
        weights: Dict[str, float]
    ) -> Tuple[float, float]:
        """Calculate weighted overall score and confidence."""
        if not capabilities:
            return 0.0, 0.0
        
        total_weighted_score = 0.0
        total_weight = 0.0
        confidence_sum = 0.0
        
        for name, capability in capabilities.items():
            weight = weights.get(name, 0.5)
            total_weighted_score += capability.score * weight
            total_weight += weight
            confidence_sum += capability.confidence
        
        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0
        overall_confidence = confidence_sum / len(capabilities) if capabilities else 0
        
        return round(overall_score, 2), round(overall_confidence, 2)

    def _identify_strengths(self, capabilities: Dict[str, CapabilityScore]) -> List[str]:
        """Identify project strengths (capabilities scoring > 80)."""
        strengths = []
        
        for name, capability in capabilities.items():
            if capability.score >= 80:
                strengths.append(f"{name.replace('_', ' ').title()} ({capability.score:.0f}%)")
        
        return sorted(strengths, key=lambda x: float(x.split('(')[1].strip('%)')) , reverse=True)

    def _identify_weaknesses(self, capabilities: Dict[str, CapabilityScore]) -> List[str]:
        """Identify project weaknesses (capabilities scoring < 50)."""
        weaknesses = []
        
        for name, capability in capabilities.items():
            if capability.score < 50:
                weaknesses.append(f"{name.replace('_', ' ').title()} ({capability.score:.0f}%)")
        
        return sorted(weaknesses, key=lambda x: float(x.split('(')[1].strip('%)')))

    def _identify_critical_gaps(
        self, 
        capabilities: Dict[str, CapabilityScore],
        context: ProjectContext
    ) -> List[str]:
        """Identify critical gaps based on project type and low scores."""
        critical_gaps = []
        
        # Define critical capabilities by project type
        critical_by_type = {
            'web_app': ['security', 'authentication', 'error_handling', 'testing'],
            'api_service': ['security', 'authentication', 'api_design', 'error_handling'],
            'cli_tool': ['error_handling', 'documentation', 'testing', 'configuration'],
            'library': ['documentation', 'testing', 'api_design', 'code_quality']
        }
        
        critical_for_project = critical_by_type.get(context.project_type, [])
        
        for capability_name in critical_for_project:
            if capability_name in capabilities:
                capability = capabilities[capability_name]
                if capability.score < 60:  # Critical threshold
                    gap_desc = f"{capability_name.replace('_', ' ').title()}: "
                    gap_desc += f"{capability.score:.0f}% (needs {60 - capability.score:.0f}% improvement)"
                    critical_gaps.append(gap_desc)
        
        return critical_gaps


if __name__ == "__main__":
    # Test the capability assessor
    import asyncio
    from pathlib import Path
    
    async def test():
        assessor = CapabilityAssessor()
        
        # Would need actual ProjectContext from context_analyzer
        # This is just for module testing
        print("CapabilityAssessor module loaded successfully")
    
    asyncio.run(test())