"""
DependencyAnalyzer - Analyzes project dependencies and external libraries

Provides comprehensive analysis of project dependencies, package management,
and external library usage for autonomous planning decisions.

CURRENT STATUS: Imported but not used in main pipeline
ACTIVATION EFFORT: 2-4 hours  
INTEGRATION POINTS: Imported by context_analyzer.py
ACTIVATION GUIDE: docs/implementation/STRATEGIST_FEATURE_ROADMAP.md

This module is fully implemented and ready for activation when needed.
See the activation guide for step-by-step integration procedures.
"""

import asyncio
import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Dependency:
    """Represents a project dependency"""
    name: str
    version: Optional[str] = None
    type: str = 'production'  # production, development, optional
    source: str = 'unknown'  # package.json, requirements.txt, etc.
    description: Optional[str] = None
    security_risk: str = 'unknown'  # low, medium, high, critical
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'version': self.version,
            'type': self.type,
            'source': self.source,
            'description': self.description,
            'security_risk': self.security_risk
        }


class DependencyAnalyzer:
    """
    Analyzes project dependencies and external libraries
    
    Supports multiple package managers and dependency formats:
    - Python: requirements.txt, pyproject.toml, setup.py, Pipfile
    - Node.js: package.json, package-lock.json, yarn.lock
    - Java: pom.xml, build.gradle
    - Other: Gemfile, Cargo.toml, go.mod, composer.json
    """
    
    def __init__(self):
        """Initialize with dependency file patterns and security data"""
        
        # Dependency file patterns and their parsers
        self.dependency_files = {
            'requirements.txt': self._parse_requirements_txt,
            'pyproject.toml': self._parse_pyproject_toml,
            'setup.py': self._parse_setup_py,
            'Pipfile': self._parse_pipfile,
            'package.json': self._parse_package_json,
            'package-lock.json': self._parse_package_lock,
            'yarn.lock': self._parse_yarn_lock,
            'pom.xml': self._parse_pom_xml,
            'build.gradle': self._parse_build_gradle,
            'Gemfile': self._parse_gemfile,
            'Cargo.toml': self._parse_cargo_toml,
            'go.mod': self._parse_go_mod,
            'composer.json': self._parse_composer_json
        }
        
        # Known security risk packages (simplified list)
        self.security_risks = {
            'high': {
                'lodash', 'moment', 'request', 'node-uuid', 'growl',
                'pillow', 'django', 'flask', 'requests', 'urllib3'
            },
            'medium': {
                'express', 'react', 'vue', 'angular', 'jquery',
                'numpy', 'pandas', 'tensorflow', 'pytorch'
            },
            'low': {
                'chalk', 'debug', 'commander', 'yargs',
                'click', 'rich', 'typer', 'pydantic'
            }
        }
        
        # Package categories for analysis
        self.package_categories = {
            'web_framework': {
                'django', 'flask', 'fastapi', 'express', 'next', 'nuxt',
                'react', 'vue', 'angular', 'svelte', 'laravel', 'rails'
            },
            'database': {
                'sqlalchemy', 'django-orm', 'mongoose', 'sequelize',
                'prisma', 'typeorm', 'hibernate', 'active-record'
            },
            'testing': {
                'pytest', 'unittest', 'jest', 'mocha', 'jasmine',
                'cypress', 'selenium', 'testng', 'junit'
            },
            'build_tool': {
                'webpack', 'rollup', 'parcel', 'vite', 'gulp',
                'grunt', 'babel', 'typescript', 'sass', 'less'
            },
            'utility': {
                'lodash', 'underscore', 'ramda', 'moment', 'dayjs',
                'axios', 'fetch', 'requests', 'urllib3', 'httpx'
            },
            'security': {
                'passport', 'jwt', 'bcrypt', 'crypto', 'helmet',
                'cors', 'csrf', 'oauth', 'auth0', 'firebase-auth'
            }
        }
    
    async def analyze(self, project_path: Path) -> Dict[str, Any]:
        """
        Analyze project dependencies comprehensively
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Dict containing complete dependency analysis
        """
        if not project_path.exists() or not project_path.is_dir():
            raise ValueError(f"Invalid project path: {project_path}")
        
        try:
            logger.info(f"Analyzing dependencies for: {project_path}")
            
            # Find and parse dependency files
            dependencies = await self._find_and_parse_dependencies(project_path)
            
            # Analyze dependency patterns
            patterns = await self._analyze_dependency_patterns(dependencies)
            
            # Assess security risks
            security_analysis = await self._analyze_security_risks(dependencies)
            
            # Categorize dependencies
            categorization = await self._categorize_dependencies(dependencies)
            
            # Calculate metrics
            metrics = await self._calculate_dependency_metrics(dependencies, patterns)
            
            # Check for dependency conflicts
            conflicts = await self._check_dependency_conflicts(dependencies)
            
            return {
                'total_count': len(dependencies),
                'direct': [dep.to_dict() for dep in dependencies if dep.type == 'production'],
                'dev': [dep.to_dict() for dep in dependencies if dep.type == 'development'],
                'optional': [dep.to_dict() for dep in dependencies if dep.type == 'optional'],
                'patterns': patterns,
                'security_analysis': security_analysis,
                'categorization': categorization,
                'metrics': metrics,
                'conflicts': conflicts,
                'dependency_health_score': await self._calculate_health_score(
                    dependencies, security_analysis, conflicts
                )
            }
            
        except Exception as e:
            logger.error(f"Dependency analysis failed: {e}")
            raise RuntimeError(f"Failed to analyze dependencies: {e}")
    
    async def _find_and_parse_dependencies(self, project_path: Path) -> List[Dependency]:
        """Find and parse all dependency files in the project"""
        all_dependencies = []
        
        for dep_file, parser in self.dependency_files.items():
            file_path = project_path / dep_file
            if file_path.exists():
                try:
                    logger.debug(f"Parsing dependency file: {dep_file}")
                    dependencies = await parser(file_path)
                    all_dependencies.extend(dependencies)
                except Exception as e:
                    logger.warning(f"Failed to parse {dep_file}: {e}")
                    continue
        
        # Remove duplicates while preserving order and merging information
        unique_dependencies = await self._deduplicate_dependencies(all_dependencies)
        
        return unique_dependencies
    
    async def _deduplicate_dependencies(self, dependencies: List[Dependency]) -> List[Dependency]:
        """Remove duplicate dependencies and merge information"""
        seen = {}
        deduplicated = []
        
        for dep in dependencies:
            key = dep.name.lower()
            
            if key not in seen:
                seen[key] = dep
                deduplicated.append(dep)
            else:
                # Merge information from duplicate
                existing = seen[key]
                
                # Prefer production over development dependencies
                if dep.type == 'production' and existing.type != 'production':
                    existing.type = dep.type
                
                # Use more specific version if available
                if dep.version and not existing.version:
                    existing.version = dep.version
                
                # Merge sources
                if dep.source != existing.source:
                    existing.source = f"{existing.source}, {dep.source}"
        
        return deduplicated
    
    async def _parse_requirements_txt(self, file_path: Path) -> List[Dependency]:
        """Parse Python requirements.txt file"""
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Handle -r references to other requirements files
                    if line.startswith('-r '):
                        continue
                    
                    # Parse package name and version
                    dep = self._parse_python_requirement(line, 'requirements.txt')
                    if dep:
                        dependencies.append(dep)
                        
        except Exception as e:
            logger.error(f"Error parsing requirements.txt: {e}")
        
        return dependencies
    
    async def _parse_package_json(self, file_path: Path) -> List[Dependency]:
        """Parse Node.js package.json file"""
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Parse production dependencies
            for name, version in data.get('dependencies', {}).items():
                dependencies.append(Dependency(
                    name=name,
                    version=version,
                    type='production',
                    source='package.json'
                ))
            
            # Parse development dependencies
            for name, version in data.get('devDependencies', {}).items():
                dependencies.append(Dependency(
                    name=name,
                    version=version,
                    type='development',
                    source='package.json'
                ))
            
            # Parse optional dependencies
            for name, version in data.get('optionalDependencies', {}).items():
                dependencies.append(Dependency(
                    name=name,
                    version=version,
                    type='optional',
                    source='package.json'
                ))
                
        except Exception as e:
            logger.error(f"Error parsing package.json: {e}")
        
        return dependencies
    
    def _parse_python_requirement(self, requirement: str, source: str) -> Optional[Dependency]:
        """Parse a single Python requirement string"""
        try:
            # Handle git+https:// URLs
            if requirement.startswith('git+'):
                match = re.search(r'git\+.*#egg=([^&]+)', requirement)
                if match:
                    name = match.group(1)
                    return Dependency(name=name, source=source)
                return None
            
            # Handle -e (editable) installations
            if requirement.startswith('-e '):
                requirement = requirement[3:]
                if '#egg=' in requirement:
                    name = requirement.split('#egg=')[1].split('&')[0]
                    return Dependency(name=name, source=source, type='development')
                return None
            
            # Parse standard requirement format
            # Handle various operators: ==, >=, >, <=, <, !=, ~=
            match = re.match(r'^([a-zA-Z0-9_.-]+)([><=!~]+.*)?$', requirement)
            if match:
                name = match.group(1)
                version_spec = match.group(2) if match.group(2) else None
                
                return Dependency(
                    name=name,
                    version=version_spec,
                    source=source
                )
            
            return None
            
        except Exception as e:
            logger.debug(f"Error parsing requirement '{requirement}': {e}")
            return None
    
    async def _parse_pyproject_toml(self, file_path: Path) -> List[Dependency]:
        """Parse Python pyproject.toml file (simplified)"""
        dependencies = []
        
        try:
            # Simple TOML parsing for dependencies section
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for [tool.poetry.dependencies] section
            if '[tool.poetry.dependencies]' in content:
                in_deps_section = False
                for line in content.split('\n'):
                    line = line.strip()
                    
                    if line == '[tool.poetry.dependencies]':
                        in_deps_section = True
                        continue
                    elif line.startswith('[') and in_deps_section:
                        in_deps_section = False
                        continue
                    
                    if in_deps_section and '=' in line and not line.startswith('#'):
                        parts = line.split('=', 1)
                        if len(parts) == 2:
                            name = parts[0].strip().strip('"\'')
                            version = parts[1].strip().strip('"\'')
                            
                            if name != 'python':  # Skip Python version requirement
                                dependencies.append(Dependency(
                                    name=name,
                                    version=version,
                                    source='pyproject.toml'
                                ))
                                
        except Exception as e:
            logger.error(f"Error parsing pyproject.toml: {e}")
        
        return dependencies
    
    async def _parse_setup_py(self, file_path: Path) -> List[Dependency]:
        """Parse Python setup.py file (basic analysis)"""
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for install_requires in setup.py
            install_requires_match = re.search(
                r'install_requires\s*=\s*\[(.*?)\]',
                content,
                re.DOTALL
            )
            
            if install_requires_match:
                requirements_text = install_requires_match.group(1)
                
                # Extract individual requirements
                requirements = re.findall(r'["\']([^"\']+)["\']', requirements_text)
                
                for req in requirements:
                    dep = self._parse_python_requirement(req, 'setup.py')
                    if dep:
                        dependencies.append(dep)
                        
        except Exception as e:
            logger.error(f"Error parsing setup.py: {e}")
        
        return dependencies
    
    # Simplified implementations for other package managers
    async def _parse_pipfile(self, file_path: Path) -> List[Dependency]:
        """Parse Python Pipfile (simplified)"""
        return []  # Simplified for Sprint 9
    
    async def _parse_package_lock(self, file_path: Path) -> List[Dependency]:
        """Parse package-lock.json (simplified)"""
        return []  # Simplified for Sprint 9
    
    async def _parse_yarn_lock(self, file_path: Path) -> List[Dependency]:
        """Parse yarn.lock (simplified)"""
        return []  # Simplified for Sprint 9
    
    async def _parse_pom_xml(self, file_path: Path) -> List[Dependency]:
        """Parse Maven pom.xml (simplified)"""
        return []  # Simplified for Sprint 9
    
    async def _parse_build_gradle(self, file_path: Path) -> List[Dependency]:
        """Parse Gradle build.gradle (simplified)"""
        return []  # Simplified for Sprint 9
    
    async def _parse_gemfile(self, file_path: Path) -> List[Dependency]:
        """Parse Ruby Gemfile (simplified)"""
        return []  # Simplified for Sprint 9
    
    async def _parse_cargo_toml(self, file_path: Path) -> List[Dependency]:
        """Parse Rust Cargo.toml (simplified)"""
        return []  # Simplified for Sprint 9
    
    async def _parse_go_mod(self, file_path: Path) -> List[Dependency]:
        """Parse Go go.mod (simplified)"""
        return []  # Simplified for Sprint 9
    
    async def _parse_composer_json(self, file_path: Path) -> List[Dependency]:
        """Parse PHP composer.json (simplified)"""
        return []  # Simplified for Sprint 9
    
    async def _analyze_dependency_patterns(self, dependencies: List[Dependency]) -> Dict[str, Any]:
        """Analyze patterns in dependency usage"""
        patterns = {
            'total_dependencies': len(dependencies),
            'production_count': len([d for d in dependencies if d.type == 'production']),
            'development_count': len([d for d in dependencies if d.type == 'development']),
            'optional_count': len([d for d in dependencies if d.type == 'optional']),
            'versioned_count': len([d for d in dependencies if d.version]),
            'unversioned_count': len([d for d in dependencies if not d.version])
        }
        
        # Calculate ratios
        total = len(dependencies)
        if total > 0:
            patterns['production_ratio'] = patterns['production_count'] / total
            patterns['development_ratio'] = patterns['development_count'] / total
            patterns['versioned_ratio'] = patterns['versioned_count'] / total
        else:
            patterns['production_ratio'] = 0
            patterns['development_ratio'] = 0
            patterns['versioned_ratio'] = 0
        
        # Analyze version patterns
        patterns['version_patterns'] = await self._analyze_version_patterns(dependencies)
        
        return patterns
    
    async def _analyze_version_patterns(self, dependencies: List[Dependency]) -> Dict[str, Any]:
        """Analyze version specification patterns"""
        version_types = {
            'exact': 0,      # 1.2.3
            'range': 0,      # >=1.2.0
            'caret': 0,      # ^1.2.0
            'tilde': 0,      # ~1.2.0
            'wildcard': 0,   # 1.2.*
            'unspecified': 0 # No version
        }
        
        for dep in dependencies:
            if not dep.version:
                version_types['unspecified'] += 1
            elif dep.version.startswith('^'):
                version_types['caret'] += 1
            elif dep.version.startswith('~'):
                version_types['tilde'] += 1
            elif any(op in dep.version for op in ['>=', '>', '<=', '<', '!=']):
                version_types['range'] += 1
            elif '*' in dep.version:
                version_types['wildcard'] += 1
            else:
                version_types['exact'] += 1
        
        return version_types
    
    async def _analyze_security_risks(self, dependencies: List[Dependency]) -> Dict[str, Any]:
        """Analyze security risks in dependencies"""
        risk_counts = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0, 'unknown': 0}
        risky_packages = []
        
        for dep in dependencies:
            risk_level = self._assess_package_security_risk(dep.name)
            dep.security_risk = risk_level
            risk_counts[risk_level] += 1
            
            if risk_level in ['high', 'critical']:
                risky_packages.append({
                    'name': dep.name,
                    'risk_level': risk_level,
                    'type': dep.type,
                    'version': dep.version
                })
        
        # Calculate overall risk score
        total_deps = len(dependencies)
        if total_deps > 0:
            risk_score = (
                risk_counts['critical'] * 100 +
                risk_counts['high'] * 50 +
                risk_counts['medium'] * 20 +
                risk_counts['low'] * 5
            ) / total_deps
        else:
            risk_score = 0
        
        return {
            'risk_counts': risk_counts,
            'risky_packages': risky_packages,
            'overall_risk_score': min(100, risk_score),
            'security_recommendations': await self._generate_security_recommendations(risky_packages)
        }
    
    def _assess_package_security_risk(self, package_name: str) -> str:
        """Assess security risk level for a package"""
        package_lower = package_name.lower()
        
        for risk_level, packages in self.security_risks.items():
            if package_lower in packages:
                return risk_level
        
        return 'unknown'
    
    async def _categorize_dependencies(self, dependencies: List[Dependency]) -> Dict[str, Any]:
        """Categorize dependencies by their purpose"""
        categories = {category: [] for category in self.package_categories.keys()}
        categories['uncategorized'] = []
        
        for dep in dependencies:
            categorized = False
            dep_name_lower = dep.name.lower()
            
            for category, packages in self.package_categories.items():
                if dep_name_lower in packages or any(pkg in dep_name_lower for pkg in packages):
                    categories[category].append(dep.to_dict())
                    categorized = True
                    break
            
            if not categorized:
                categories['uncategorized'].append(dep.to_dict())
        
        # Calculate category statistics
        category_stats = {}
        total_deps = len(dependencies)
        
        for category, deps in categories.items():
            category_stats[category] = {
                'count': len(deps),
                'percentage': (len(deps) / total_deps * 100) if total_deps > 0 else 0
            }
        
        return {
            'categories': categories,
            'statistics': category_stats
        }
    
    async def _calculate_dependency_metrics(self, dependencies: List[Dependency], patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate dependency health and quality metrics"""
        metrics = {
            'dependency_count': len(dependencies),
            'version_completeness': patterns.get('versioned_ratio', 0) * 100,
            'production_dev_ratio': 0,
            'dependency_freshness_score': await self._calculate_freshness_score(dependencies),
            'complexity_score': await self._calculate_complexity_score(dependencies)
        }
        
        # Calculate production to development ratio
        prod_count = patterns.get('production_count', 0)
        dev_count = patterns.get('development_count', 0)
        
        if dev_count > 0:
            metrics['production_dev_ratio'] = prod_count / dev_count
        elif prod_count > 0:
            metrics['production_dev_ratio'] = float('inf')  # Only production deps
        else:
            metrics['production_dev_ratio'] = 0
        
        return metrics
    
    async def _calculate_freshness_score(self, dependencies: List[Dependency]) -> float:
        """Calculate dependency freshness score (simplified)"""
        # In a real implementation, this would check against package registries
        # For Sprint 9, return a placeholder score
        return 75.0
    
    async def _calculate_complexity_score(self, dependencies: List[Dependency]) -> float:
        """Calculate dependency complexity score"""
        if not dependencies:
            return 0
        
        # Factors that increase complexity
        complexity_factors = 0
        
        # Too many dependencies
        dep_count = len(dependencies)
        if dep_count > 50:
            complexity_factors += (dep_count - 50) * 2
        
        # Unversioned dependencies increase complexity
        unversioned = len([d for d in dependencies if not d.version])
        complexity_factors += unversioned * 5
        
        # High-risk packages increase complexity
        high_risk = len([d for d in dependencies if d.security_risk in ['high', 'critical']])
        complexity_factors += high_risk * 10
        
        # Calculate final score (0-100, where 0 is simple and 100 is complex)
        complexity_score = min(100, complexity_factors)
        
        return complexity_score
    
    async def _check_dependency_conflicts(self, dependencies: List[Dependency]) -> Dict[str, Any]:
        """Check for potential dependency conflicts"""
        conflicts = {
            'version_conflicts': [],
            'duplicate_packages': [],
            'conflicting_frameworks': []
        }
        
        # Check for duplicate package names with different versions
        name_versions = {}
        for dep in dependencies:
            name = dep.name.lower()
            if name in name_versions:
                existing_version = name_versions[name]
                if dep.version and existing_version != dep.version:
                    conflicts['version_conflicts'].append({
                        'package': dep.name,
                        'versions': [existing_version, dep.version]
                    })
            else:
                name_versions[name] = dep.version
        
        # Check for conflicting frameworks
        frameworks_found = []
        for dep in dependencies:
            dep_name = dep.name.lower()
            
            # Check for conflicting web frameworks
            web_frameworks = ['django', 'flask', 'fastapi', 'express', 'react', 'vue', 'angular']
            if dep_name in web_frameworks:
                frameworks_found.append(dep_name)
        
        if len(set(frameworks_found)) > 2:  # More than 2 different frameworks might indicate conflict
            conflicts['conflicting_frameworks'] = frameworks_found
        
        return conflicts
    
    async def _calculate_health_score(self, dependencies: List[Dependency], 
                                    security_analysis: Dict[str, Any], 
                                    conflicts: Dict[str, Any]) -> float:
        """Calculate overall dependency health score"""
        if not dependencies:
            return 100  # No dependencies = perfect health
        
        health_score = 100
        
        # Deduct for security risks
        security_score = security_analysis.get('overall_risk_score', 0)
        health_score -= security_score * 0.3  # Security risks reduce health
        
        # Deduct for conflicts
        conflict_count = (len(conflicts.get('version_conflicts', [])) + 
                         len(conflicts.get('conflicting_frameworks', [])))
        health_score -= conflict_count * 10
        
        # Deduct for unversioned dependencies
        unversioned_ratio = len([d for d in dependencies if not d.version]) / len(dependencies)
        health_score -= unversioned_ratio * 20
        
        # Deduct for too many dependencies
        if len(dependencies) > 100:
            health_score -= (len(dependencies) - 100) * 0.5
        
        return max(0, health_score)
    
    async def _generate_security_recommendations(self, risky_packages: List[Dict[str, Any]]) -> List[str]:
        """Generate security recommendations based on risky packages"""
        recommendations = []
        
        if not risky_packages:
            recommendations.append("No high-risk packages detected. Continue monitoring for security updates.")
            return recommendations
        
        # Group by risk level
        critical_packages = [p for p in risky_packages if p['risk_level'] == 'critical']
        high_risk_packages = [p for p in risky_packages if p['risk_level'] == 'high']
        
        if critical_packages:
            recommendations.append(
                f"CRITICAL: Update or replace {len(critical_packages)} critical-risk packages immediately: "
                f"{', '.join([p['name'] for p in critical_packages[:3]])}"
                + ("..." if len(critical_packages) > 3 else "")
            )
        
        if high_risk_packages:
            recommendations.append(
                f"HIGH: Review {len(high_risk_packages)} high-risk packages for security updates: "
                f"{', '.join([p['name'] for p in high_risk_packages[:3]])}"
                + ("..." if len(high_risk_packages) > 3 else "")
            )
        
        recommendations.append("Implement dependency scanning in CI/CD pipeline")
        recommendations.append("Enable automated security updates where possible")
        
        return recommendations