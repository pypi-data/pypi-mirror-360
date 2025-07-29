"""
BestPracticesEngine: Industry standards and recommendations engine.

This component provides industry-standard best practices for various project types
and frameworks. It includes mandatory DCP integration for multi-agent coordination.
"""

import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
import json
import yaml
from pathlib import Path

# DCP integration (MANDATORY)
try:
    from coppersun_brass.core.context.dcp_manager import DCPManager
    DCP_AVAILABLE = True
except ImportError:
    DCP_AVAILABLE = False
    DCPManager = None

logger = logging.getLogger(__name__)


@dataclass
class PracticeRecommendation:
    """A single best practice recommendation."""
    id: str
    title: str
    description: str
    category: str  # security, testing, documentation, etc.
    severity: str  # critical, important, recommended
    source: str  # industry_standard, framework_specific, community
    applies_to: List[str]  # project types this applies to
    frameworks: List[str] = field(default_factory=list)  # specific frameworks
    rationale: str = ""
    implementation_guide: str = ""
    references: List[str] = field(default_factory=list)
    confidence: float = 0.8
    effort: str = "medium"  # small, medium, large
    
    # Traceability fields for linking to gaps and capabilities
    linked_gap_id: Optional[str] = None
    linked_capability: Optional[str] = None
    linked_assessment_id: Optional[str] = None


@dataclass
class BestPracticesProfile:
    """Profile for customizing best practices to team preferences."""
    strictness_level: str = "moderate"  # relaxed, moderate, strict
    include_sources: List[str] = field(default_factory=lambda: ["industry_standard", "framework_specific"])
    exclude_categories: List[str] = field(default_factory=list)
    custom_practices_path: Optional[str] = None
    team_overrides: Dict[str, bool] = field(default_factory=dict)  # practice_id -> enabled


class BestPracticesEngine:
    """
    Engine for providing industry-standard best practices recommendations.
    
    Features:
    - Industry standards database (OWASP, NIST, etc.)
    - Framework-specific practices
    - Community practices extension
    - Team preference overrides
    - DCP integration for multi-agent coordination
    """
    
    def __init__(self, dcp_path: Optional[str] = None):
        """Initialize the engine with optional DCP path."""
        self.dcp_manager = None
        if DCP_AVAILABLE and dcp_path:
            try:
                # DCPManager expects project root directory, not file path
                if dcp_path.endswith('.json'):
                    project_root = str(Path(dcp_path).parent)
                else:
                    project_root = dcp_path
                self.dcp_manager = DCPManager(project_root)
                logger.info("BestPracticesEngine: DCP integration enabled")
                # Read historical practice data on startup
                self._load_historical_practices()
            except Exception as e:
                logger.warning(f"BestPracticesEngine: DCP unavailable: {e}")
        
        # Initialize practices database
        self._industry_standards = self._load_industry_standards()
        self._framework_practices = self._load_framework_practices()
        self._community_practices = {}
        
        logger.info("BestPracticesEngine initialized with %d industry standards, %d framework practices",
                   len(self._industry_standards), len(self._framework_practices))
    
    def _load_historical_practices(self) -> None:
        """Load historical practice recommendations from DCP."""
        if not self.dcp_manager:
            return
            
        try:
            dcp_data = self.dcp_manager.read_dcp()
            observations = dcp_data.get("current_observations", [])
            
            practice_count = 0
            for obs in observations:
                if obs.get("type") == "best_practice" and obs.get("source_agent") == "best_practices_engine":
                    practice_count += 1
                    # Could analyze historical recommendations here
            
            if practice_count > 0:
                logger.info(f"Loaded {practice_count} historical practice recommendations from DCP")
        except Exception as e:
            logger.debug(f"Could not load historical practices (this is normal on first run): {e}")
    
    def _load_industry_standards(self) -> Dict[str, PracticeRecommendation]:
        """Load industry standard best practices."""
        standards = {}
        
        # Security practices (OWASP Top 10, NIST)
        standards["sec_input_validation"] = PracticeRecommendation(
            id="sec_input_validation",
            title="Input Validation",
            description="Validate all input data on the server side",
            category="security",
            severity="critical",
            source="industry_standard",
            applies_to=["web_app", "api", "backend"],
            rationale="Prevents injection attacks and data corruption (OWASP Top 10)",
            implementation_guide="Use allow-lists, validate data types, lengths, formats, and ranges",
            references=["https://owasp.org/www-project-top-ten/"],
            confidence=0.95
        )
        
        standards["sec_auth_secure"] = PracticeRecommendation(
            id="sec_auth_secure",
            title="Secure Authentication",
            description="Implement secure authentication with proper session management",
            category="security",
            severity="critical",
            source="industry_standard",
            applies_to=["web_app", "api", "backend"],
            rationale="Prevents unauthorized access (OWASP A07)",
            implementation_guide="Use strong password policies, MFA, secure session tokens",
            references=["https://owasp.org/www-project-top-ten/"],
            confidence=0.95
        )
        
        # Testing practices
        standards["test_coverage_target"] = PracticeRecommendation(
            id="test_coverage_target",
            title="Code Coverage Target",
            description="Maintain at least 80% code coverage",
            category="testing",
            severity="important",
            source="industry_standard",
            applies_to=["library", "web_app", "api", "backend", "cli_tool"],
            rationale="Industry standard for quality assurance",
            implementation_guide="Use coverage tools, focus on critical paths first",
            confidence=0.85,
            effort="large"
        )
        
        standards["test_types_pyramid"] = PracticeRecommendation(
            id="test_types_pyramid",
            title="Test Pyramid",
            description="Follow test pyramid: many unit tests, some integration, few E2E",
            category="testing",
            severity="important",
            source="industry_standard",
            applies_to=["web_app", "api", "backend"],
            rationale="Balances test speed, reliability, and coverage",
            implementation_guide="70% unit, 20% integration, 10% E2E tests",
            confidence=0.9,
            effort="large"
        )
        
        # Documentation practices
        standards["doc_readme_comprehensive"] = PracticeRecommendation(
            id="doc_readme_comprehensive",
            title="Comprehensive README",
            description="Maintain comprehensive README with setup, usage, and contribution guide",
            category="documentation",
            severity="critical",
            source="industry_standard",
            applies_to=["library", "web_app", "api", "cli_tool", "backend"],
            rationale="Essential for onboarding and maintenance",
            implementation_guide="Include: description, installation, usage, API reference, contributing",
            confidence=0.95,
            effort="medium"
        )
        
        standards["doc_api_complete"] = PracticeRecommendation(
            id="doc_api_complete",
            title="API Documentation",
            description="Document all public APIs with examples",
            category="documentation",
            severity="critical",
            source="industry_standard",
            applies_to=["library", "api"],
            rationale="Required for API usability and adoption",
            implementation_guide="Use OpenAPI/Swagger for REST, document all endpoints",
            confidence=0.95,
            effort="large"
        )
        
        # Code quality practices
        standards["quality_linting"] = PracticeRecommendation(
            id="quality_linting",
            title="Code Linting",
            description="Use automated linting with strict rules",
            category="code_quality",
            severity="important",
            source="industry_standard",
            applies_to=["library", "web_app", "api", "cli_tool", "backend"],
            rationale="Ensures consistent code style and catches common errors",
            implementation_guide="Configure ESLint, Pylint, or language-specific linters",
            confidence=0.9,
            effort="small"
        )
        
        # Performance practices
        standards["perf_monitoring"] = PracticeRecommendation(
            id="perf_monitoring",
            title="Performance Monitoring",
            description="Implement performance monitoring and alerting",
            category="performance",
            severity="important",
            source="industry_standard",
            applies_to=["web_app", "api", "backend"],
            rationale="Proactive performance management",
            implementation_guide="Use APM tools, set up alerts for response times and errors",
            confidence=0.85,
            effort="medium"
        )
        
        # Error handling practices
        standards["error_structured_logging"] = PracticeRecommendation(
            id="error_structured_logging",
            title="Structured Error Logging",
            description="Implement structured logging with proper error levels",
            category="error_handling",
            severity="critical",
            source="industry_standard",
            applies_to=["web_app", "api", "backend", "cli_tool"],
            rationale="Essential for debugging and monitoring",
            implementation_guide="Use structured logging libraries, include context and stack traces",
            confidence=0.95,
            effort="medium"
        )
        
        # CI/CD practices
        standards["cicd_automated_pipeline"] = PracticeRecommendation(
            id="cicd_automated_pipeline",
            title="Automated CI/CD Pipeline",
            description="Set up automated build, test, and deployment pipeline",
            category="infrastructure",
            severity="important",
            source="industry_standard",
            applies_to=["web_app", "api", "backend", "library"],
            rationale="Ensures consistent quality and rapid deployment",
            implementation_guide="Use GitHub Actions, GitLab CI, or similar",
            confidence=0.9,
            effort="large"
        )
        
        return standards
    
    def _load_framework_practices(self) -> Dict[str, PracticeRecommendation]:
        """Load framework-specific best practices."""
        practices = {}
        
        # React practices
        practices["react_hooks_rules"] = PracticeRecommendation(
            id="react_hooks_rules",
            title="React Hooks Rules",
            description="Follow Rules of Hooks and use ESLint plugin",
            category="code_quality",
            severity="critical",
            source="framework_specific",
            applies_to=["web_app"],
            frameworks=["react"],
            rationale="Prevents subtle bugs in React applications",
            implementation_guide="Install eslint-plugin-react-hooks, enable recommended rules",
            references=["https://react.dev/warnings/invalid-hook-call-warning"],
            confidence=0.95,
            effort="small"
        )
        
        practices["react_testing_library"] = PracticeRecommendation(
            id="react_testing_library",
            title="React Testing Library",
            description="Use React Testing Library for component tests",
            category="testing",
            severity="important",
            source="framework_specific",
            applies_to=["web_app"],
            frameworks=["react"],
            rationale="Tests user behavior rather than implementation details",
            implementation_guide="Test what users see and do, not component internals",
            confidence=0.9,
            effort="medium"
        )
        
        # Django practices
        practices["django_security_middleware"] = PracticeRecommendation(
            id="django_security_middleware",
            title="Django Security Middleware",
            description="Enable all Django security middleware",
            category="security",
            severity="critical",
            source="framework_specific",
            applies_to=["web_app", "backend"],
            frameworks=["django"],
            rationale="Provides built-in protection against common attacks",
            implementation_guide="Enable SecurityMiddleware, configure SECURE_* settings",
            references=["https://docs.djangoproject.com/en/stable/topics/security/"],
            confidence=0.95,
            effort="small"
        )
        
        # Express.js practices
        practices["express_helmet"] = PracticeRecommendation(
            id="express_helmet",
            title="Express Helmet Middleware",
            description="Use Helmet.js for security headers",
            category="security",
            severity="critical",
            source="framework_specific",
            applies_to=["api", "backend"],
            frameworks=["express"],
            rationale="Sets various HTTP headers to secure Express apps",
            implementation_guide="npm install helmet, app.use(helmet())",
            confidence=0.95,
            effort="small"
        )
        
        # FastAPI practices
        practices["fastapi_async_patterns"] = PracticeRecommendation(
            id="fastapi_async_patterns",
            title="FastAPI Async Best Practices",
            description="Use async/await properly in FastAPI endpoints",
            category="performance",
            severity="important",
            source="framework_specific",
            applies_to=["api"],
            frameworks=["fastapi"],
            rationale="Maximizes FastAPI's async performance benefits",
            implementation_guide="Use async def for I/O operations, avoid blocking calls",
            confidence=0.9,
            effort="medium"
        )
        
        return practices
    
    def load_community_practices(self, practices_path: str) -> None:
        """Load community-contributed practices from YAML/JSON files."""
        path = Path(practices_path)
        if not path.exists():
            logger.warning(f"Community practices path not found: {practices_path}")
            return
        
        loaded = 0
        for file in path.glob("*.yaml") + path.glob("*.yml") + path.glob("*.json"):
            try:
                with open(file, 'r') as f:
                    if file.suffix == '.json':
                        data = json.load(f)
                    else:
                        data = yaml.safe_load(f)
                
                for practice_data in data.get("practices", []):
                    practice = PracticeRecommendation(**practice_data)
                    self._community_practices[practice.id] = practice
                    loaded += 1
            except Exception as e:
                logger.error(f"Failed to load community practices from {file}: {e}")
        
        logger.info(f"Loaded {loaded} community practices")
    
    def get_recommendations(self,
                          project_type: str,
                          capabilities: Dict[str, float],
                          gaps: List[Dict[str, Any]],
                          frameworks: List[str],
                          profile: Optional[BestPracticesProfile] = None) -> List[PracticeRecommendation]:
        """
        Get best practice recommendations based on project analysis.
        
        Args:
            project_type: Type of project (web_app, api, library, etc.)
            capabilities: Current capability scores
            gaps: Identified gaps from GapDetector
            frameworks: Detected frameworks
            profile: Optional profile for customization
            
        Returns:
            List of applicable practice recommendations
        """
        if profile is None:
            profile = BestPracticesProfile()
        
        recommendations = []
        all_practices = {}
        
        # Collect practices from enabled sources
        if "industry_standard" in profile.include_sources:
            all_practices.update(self._industry_standards)
        if "framework_specific" in profile.include_sources:
            all_practices.update(self._framework_practices)
        if "community" in profile.include_sources:
            all_practices.update(self._community_practices)
        
        # Filter applicable practices
        for practice_id, practice in all_practices.items():
            # Check team overrides
            if practice_id in profile.team_overrides:
                if not profile.team_overrides[practice_id]:
                    continue
            
            # Check if practice applies to project type
            if project_type not in practice.applies_to:
                continue
            
            # Check if practice category is excluded
            if practice.category in profile.exclude_categories:
                continue
            
            # Check framework-specific practices
            if practice.frameworks:
                if not any(fw in frameworks for fw in practice.frameworks):
                    continue
            
            # Link to gaps if applicable
            for gap in gaps:
                if gap.get("capability") == practice.category or \
                   gap.get("capability") in practice.category:
                    practice.linked_gap_id = gap.get("id")
                    practice.linked_capability = gap.get("capability")
                    break
            
            # Adjust based on strictness level
            if profile.strictness_level == "relaxed" and practice.severity == "recommended":
                continue
            elif profile.strictness_level == "strict":
                # Include all practices in strict mode
                pass
            
            recommendations.append(practice)
        
        # Sort by severity and confidence
        severity_order = {"critical": 0, "important": 1, "recommended": 2}
        recommendations.sort(
            key=lambda p: (severity_order.get(p.severity, 3), -p.confidence)
        )
        
        # Write recommendations to DCP
        if self.dcp_manager and recommendations:
            self._write_recommendations_to_dcp(project_type, recommendations, gaps)
        
        return recommendations
    
    def _write_recommendations_to_dcp(self,
                                    project_type: str,
                                    recommendations: List[PracticeRecommendation],
                                    gaps: List[Dict[str, Any]]) -> None:
        """Write practice recommendations to DCP for other agents."""
        if not self.dcp_manager:
            return
        
        try:
            # Group recommendations by severity
            critical = [r for r in recommendations if r.severity == "critical"]
            important = [r for r in recommendations if r.severity == "important"]
            
            observation = {
                "type": "file_analysis",
                "priority": 70,
                "summary": f"Best practices: {len(recommendations)} recommendations for {project_type} project",
                "details": {
                    "project_type": project_type,
                    "total_recommendations": len(recommendations),
                    "critical_count": len(critical),
                    "important_count": len(important),
                    "top_recommendations": [
                        {
                            "id": r.id,
                            "title": r.title,
                            "description": r.description,
                            "category": r.category,
                            "severity": r.severity,
                            "effort": r.effort,
                            "confidence": r.confidence,
                            "linked_gap_id": r.linked_gap_id,
                            "framework": r.frameworks[0] if r.frameworks else "any",
                            "source": r.source,
                            "implementation_guide": r.implementation_guide,
                            "references": r.references,
                            "rationale": r.rationale
                        }
                        for r in recommendations
                    ],
                    "categories_covered": list(set(r.category for r in recommendations)),
                    "linked_gaps": len([r for r in recommendations if r.linked_gap_id]),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            obs_id = self.dcp_manager.add_observation(observation, "best_practices_engine")
            logger.info(f"Wrote practice recommendations to DCP: {obs_id}")
            
        except Exception as e:
            logger.error(f"Failed to write recommendations to DCP: {e}")
    
    def get_practice_by_id(self, practice_id: str) -> Optional[PracticeRecommendation]:
        """Get a specific practice by ID."""
        # Search all sources
        if practice_id in self._industry_standards:
            return self._industry_standards[practice_id]
        if practice_id in self._framework_practices:
            return self._framework_practices[practice_id]
        if practice_id in self._community_practices:
            return self._community_practices[practice_id]
        return None
    
    def get_practices_for_capability(self, capability: str) -> List[PracticeRecommendation]:
        """Get all practices related to a specific capability."""
        practices = []
        all_practices = {
            **self._industry_standards,
            **self._framework_practices,
            **self._community_practices
        }
        
        for practice in all_practices.values():
            if practice.category == capability or capability in practice.category:
                practices.append(practice)
        
        return practices
    
    def export_recommendations(self,
                             recommendations: List[PracticeRecommendation],
                             format: str = "markdown") -> str:
        """Export recommendations in various formats."""
        if format == "markdown":
            output = ["# Best Practice Recommendations\n"]
            
            # Group by category
            by_category = {}
            for rec in recommendations:
                if rec.category not in by_category:
                    by_category[rec.category] = []
                by_category[rec.category].append(rec)
            
            for category, recs in by_category.items():
                output.append(f"\n## {category.replace('_', ' ').title()}\n")
                for rec in recs:
                    output.append(f"### {rec.title} ({rec.severity})\n")
                    output.append(f"{rec.description}\n")
                    if rec.rationale:
                        output.append(f"**Rationale**: {rec.rationale}\n")
                    if rec.implementation_guide:
                        output.append(f"**Implementation**: {rec.implementation_guide}\n")
                    if rec.references:
                        output.append("**References**:")
                        for ref in rec.references:
                            output.append(f"- {ref}")
                        output.append("")
                    output.append(f"**Effort**: {rec.effort} | **Confidence**: {rec.confidence:.0%}\n")
                    if rec.linked_gap_id:
                        output.append(f"**Linked Gap**: {rec.linked_gap_id}\n")
                    output.append("")
            
            return "\n".join(output)
        
        elif format == "json":
            return json.dumps(
                [rec.__dict__ for rec in recommendations],
                indent=2,
                default=str
            )
        
        else:
            raise ValueError(f"Unsupported format: {format}")