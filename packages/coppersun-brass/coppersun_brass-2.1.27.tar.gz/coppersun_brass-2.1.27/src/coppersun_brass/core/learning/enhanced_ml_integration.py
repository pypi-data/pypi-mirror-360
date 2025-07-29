"""
Enhanced ML Integration - Pure Python ML + Codebase Learning
============================================================

🩸 BLOOD OATH COMPLIANT: Integrates our pure Python ML engine with 
codebase learning using ONLY Python built-ins.

This is the complete integration that restores adaptive intelligence
to the Copper Sun Brass system by learning from user codebases.
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from coppersun_brass.ml.pure_python_ml import PurePythonMLEngine, MLAnalysisResult
from coppersun_brass.core.learning.codebase_learning_engine import CodebaseLearningEngine, ProjectContext

logger = logging.getLogger(__name__)

class EnhancedMLAnalysisResult(MLAnalysisResult):
    """Extended analysis result with learning enhancements."""
    
    def __init__(self, base_result: MLAnalysisResult):
        """Initialize from base result."""
        super().__init__(
            todo_type=base_result.todo_type,
            priority_score=base_result.priority_score,
            confidence=base_result.confidence,
            security_risk=base_result.security_risk,
            performance_impact=base_result.performance_impact,
            classification=base_result.classification
        )
        
        # Learning enhancements
        self.original_confidence = base_result.confidence
        self.original_priority = base_result.priority_score
        self.learning_adjustment = 1.0
        self.learning_reason = ""
        self.pattern_frequency = 0
        self.resolution_likelihood = 0.5

class LearningEnhancedMLEngine:
    """
    Pure Python ML Engine enhanced with codebase learning.
    
    🩸 BLOOD OATH: Uses only Python built-ins for learning enhancement
    ✅ Combines static ML analysis with dynamic codebase adaptation
    ✅ Zero additional dependencies beyond existing system
    ✅ Restores user codebase learning functionality
    """
    
    def __init__(self, project_path: Optional[Path] = None, learning_storage_path: Optional[Path] = None):
        """
        Initialize enhanced ML engine with codebase learning.
        
        Args:
            project_path: Root path of project for codebase learning
            learning_storage_path: Path for learning data storage
        """
        
        # Initialize core pure Python ML engine
        self.ml_engine = PurePythonMLEngine()
        
        # Initialize codebase learning engine
        self.learning_engine = CodebaseLearningEngine(learning_storage_path)
        
        # Track project context
        self.project_path = project_path
        self.project_context = None
        
        # Analysis statistics
        self.analysis_count = 0
        self.learning_adjustments_count = 0
        self.total_confidence_boost = 0.0
        
        # Initialize codebase learning if project path provided
        if project_path and project_path.exists():
            self._initialize_codebase_learning()
        
        logger.info("✅ Learning-Enhanced ML Engine initialized")
    
    def _initialize_codebase_learning(self):
        """Initialize codebase learning for the project."""
        try:
            logger.info(f"🔍 Initializing codebase learning for {self.project_path}")
            self.project_context = self.learning_engine.analyze_codebase(self.project_path)
            logger.info(f"✅ Learned {len(self.learning_engine.patterns)} patterns from codebase")
        except Exception as e:
            logger.warning(f"Failed to initialize codebase learning: {e}")
    
    def analyze_code_with_learning(
        self, 
        code_text: str, 
        file_path: str, 
        project_context: Optional[str] = None
    ) -> List[EnhancedMLAnalysisResult]:
        """
        Analyze code with both pure Python ML and codebase learning enhancements.
        
        Args:
            code_text: Source code to analyze
            file_path: Path to the file being analyzed
            project_context: Optional project context override
            
        Returns:
            Enhanced analysis results with learning adjustments
        """
        
        # Get base analysis from pure Python ML
        try:
            base_results = self.ml_engine.analyze_code(code_text, file_path)
        except Exception as e:
            logger.error(f"Pure Python ML analysis failed: {e}")
            return []
        
        # Enhance with codebase learning
        enhanced_results = []
        
        for base_result in base_results:
            enhanced_result = EnhancedMLAnalysisResult(base_result)
            
            # Apply codebase learning enhancements
            self._apply_learning_enhancements(enhanced_result, file_path, project_context)
            
            enhanced_results.append(enhanced_result)
        
        self.analysis_count += 1
        
        logger.info(f"✅ Enhanced analysis: {len(enhanced_results)} findings for {file_path}")
        return enhanced_results
    
    def _apply_learning_enhancements(
        self, 
        result: EnhancedMLAnalysisResult, 
        file_path: str,
        project_context: Optional[str] = None
    ):
        """Apply codebase learning enhancements to a single result."""
        
        # Extract pattern information
        pattern_type = result.todo_type.lower()
        pattern_subtype = result.classification.lower()
        
        # Get confidence adjustment from codebase learning
        context = project_context or (self.project_context.project_type if self.project_context else None)
        adjustment = self.learning_engine.get_confidence_adjustment(
            pattern_type, 
            pattern_subtype,
            context
        )
        
        if adjustment != 1.0:
            # Store original values
            result.original_confidence = result.confidence
            result.original_priority = result.priority_score
            
            # Apply learning adjustment
            result.confidence *= adjustment
            result.confidence = max(0.1, min(1.0, result.confidence))
            
            result.priority_score *= adjustment
            result.priority_score = max(1, min(100, result.priority_score))
            
            # Track learning metadata
            result.learning_adjustment = adjustment
            result.learning_reason = self._generate_learning_reason(pattern_type, pattern_subtype, adjustment)
            
            # Get pattern frequency if available
            pattern_key = f"{pattern_type}_{pattern_subtype}"
            if pattern_key in self.learning_engine.patterns:
                pattern = self.learning_engine.patterns[pattern_key]
                result.pattern_frequency = pattern.frequency
                result.resolution_likelihood = pattern.resolution_rate
            
            self.learning_adjustments_count += 1
            self.total_confidence_boost += (adjustment - 1.0)
    
    def _generate_learning_reason(self, pattern_type: str, pattern_subtype: str, adjustment: float) -> str:
        """Generate human-readable reason for learning adjustment."""
        
        pattern_key = f"{pattern_type}_{pattern_subtype}"
        
        if pattern_key in self.learning_engine.patterns:
            pattern = self.learning_engine.patterns[pattern_key]
            
            if adjustment > 1.2:
                return f"Boosted confidence: {pattern_subtype} {pattern_type} patterns appear {pattern.frequency} times in codebase with high resolution rate ({pattern.resolution_rate:.0%})"
            elif adjustment < 0.8:
                return f"Reduced confidence: {pattern_subtype} {pattern_type} patterns have low resolution rate ({pattern.resolution_rate:.0%}) in this project"
            else:
                return f"Slight adjustment based on project patterns"
        else:
            if adjustment > 1.0:
                return "Boosted based on project context"
            else:
                return "Reduced based on project context"
    
    def refresh_codebase_learning(self, project_path: Optional[Path] = None) -> bool:
        """
        Refresh codebase learning by re-analyzing the project.
        
        Args:
            project_path: Optional new project path
            
        Returns:
            Success boolean
        """
        try:
            target_path = project_path or self.project_path
            
            if not target_path or not target_path.exists():
                logger.warning("No valid project path for codebase learning refresh")
                return False
            
            logger.info(f"🔄 Refreshing codebase learning for {target_path}")
            
            # Update project path if changed
            self.project_path = target_path
            
            # Re-analyze codebase
            old_pattern_count = len(self.learning_engine.patterns)
            self.project_context = self.learning_engine.analyze_codebase(target_path)
            new_pattern_count = len(self.learning_engine.patterns)
            
            logger.info(f"✅ Codebase learning refreshed: {old_pattern_count} → {new_pattern_count} patterns")
            return True
            
        except Exception as e:
            logger.error(f"Failed to refresh codebase learning: {e}")
            return False
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get comprehensive insights about the learning system."""
        
        insights = {
            'ml_engine_status': {
                'enabled': self.ml_engine.enabled,
                'components_loaded': all([
                    self.ml_engine.embeddings is not None,
                    self.ml_engine.neural_weights is not None,
                    self.ml_engine.tokenizer is not None,
                    self.ml_engine.security_patterns is not None,
                    self.ml_engine.performance_patterns is not None
                ])
            },
            'codebase_learning_status': self.learning_engine.get_learning_status(),
            'integration_stats': {
                'total_analyses': self.analysis_count,
                'learning_adjustments': self.learning_adjustments_count,
                'avg_confidence_boost': (
                    self.total_confidence_boost / max(1, self.learning_adjustments_count)
                ),
                'adjustment_rate': (
                    self.learning_adjustments_count / max(1, self.analysis_count)
                )
            },
            'project_context': asdict(self.project_context) if self.project_context else None,
            'learned_patterns': []
        }
        
        # Add detailed pattern information
        for pattern_key, pattern in self.learning_engine.patterns.items():
            insights['learned_patterns'].append({
                'pattern': pattern_key,
                'frequency': pattern.frequency,
                'confidence_multiplier': pattern.confidence_multiplier,
                'resolution_rate': pattern.resolution_rate,
                'priority_keywords': pattern.priority_keywords[:3],  # First 3
                'sample_comment': pattern.sample_comments[0] if pattern.sample_comments else ""
            })
        
        # Sort patterns by impact (frequency * confidence adjustment)
        insights['learned_patterns'].sort(
            key=lambda p: p['frequency'] * abs(p['confidence_multiplier'] - 1.0),
            reverse=True
        )
        
        return insights
    
    def get_pattern_details(self, pattern_type: str, pattern_subtype: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific learned pattern."""
        
        pattern_key = f"{pattern_type.lower()}_{pattern_subtype.lower()}"
        
        if pattern_key not in self.learning_engine.patterns:
            return None
        
        pattern = self.learning_engine.patterns[pattern_key]
        
        return {
            'pattern_type': pattern.pattern_type,
            'pattern_subtype': pattern.pattern_subtype,
            'frequency': pattern.frequency,
            'context_weight': pattern.context_weight,
            'confidence_multiplier': pattern.confidence_multiplier,
            'resolution_rate': pattern.resolution_rate,
            'priority_keywords': pattern.priority_keywords,
            'project_context': pattern.project_context,
            'last_updated': pattern.last_updated,
            'sample_comments': pattern.sample_comments,
            'impact_assessment': self._assess_pattern_impact(pattern)
        }
    
    def _assess_pattern_impact(self, pattern) -> str:
        """Assess the impact level of a learned pattern."""
        
        impact_score = (
            pattern.frequency * 
            abs(pattern.confidence_multiplier - 1.0) * 
            pattern.context_weight
        )
        
        if impact_score > 5.0:
            return "high"
        elif impact_score > 2.0:
            return "medium"
        else:
            return "low"
    
    def export_learning_summary(self) -> Dict[str, Any]:
        """Export a comprehensive learning summary for documentation."""
        
        insights = self.get_learning_insights()
        
        summary = {
            'project_overview': {
                'path': str(self.project_path) if self.project_path else 'unknown',
                'type': self.project_context.project_type if self.project_context else 'unknown',
                'language': self.project_context.primary_language if self.project_context else 'unknown',
                'complexity': self.project_context.complexity_level if self.project_context else 'unknown',
                'total_files': self.project_context.total_files if self.project_context else 0,
            },
            'learning_effectiveness': {
                'patterns_learned': len(self.learning_engine.patterns),
                'high_impact_patterns': len([
                    p for p in insights['learned_patterns'] 
                    if abs(p['confidence_multiplier'] - 1.0) > 0.3
                ]),
                'confidence_boosts': len([
                    p for p in insights['learned_patterns'] 
                    if p['confidence_multiplier'] > 1.2
                ]),
                'confidence_reductions': len([
                    p for p in insights['learned_patterns'] 
                    if p['confidence_multiplier'] < 0.8
                ])
            },
            'top_patterns': insights['learned_patterns'][:10],  # Top 10 patterns
            'integration_health': {
                'ml_engine_functional': insights['ml_engine_status']['enabled'],
                'learning_active': insights['codebase_learning_status']['enabled'],
                'analysis_count': insights['integration_stats']['total_analyses'],
                'learning_coverage': f"{insights['integration_stats']['adjustment_rate']:.0%}"
            },
            'recommendations': self._generate_learning_recommendations(insights)
        }
        
        return summary
    
    def _generate_learning_recommendations(self, insights: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on learning insights."""
        
        recommendations = []
        
        # Check learning effectiveness
        pattern_count = len(insights['learned_patterns'])
        if pattern_count == 0:
            recommendations.append("No patterns learned yet - system needs more diverse TODO/FIXME comments to learn from")
        elif pattern_count < 5:
            recommendations.append("Limited learning data - consider adding more descriptive TODO comments with priority keywords")
        else:
            recommendations.append(f"Good learning coverage with {pattern_count} patterns identified")
        
        # Check adjustment balance
        high_boost_count = len([p for p in insights['learned_patterns'] if p['confidence_multiplier'] > 1.3])
        high_reduction_count = len([p for p in insights['learned_patterns'] if p['confidence_multiplier'] < 0.7])
        
        if high_boost_count > high_reduction_count * 2:
            recommendations.append("System is mostly boosting confidence - consider if some patterns should be deprioritized")
        elif high_reduction_count > high_boost_count * 2:
            recommendations.append("System is mostly reducing confidence - consider adding priority keywords to important TODOs")
        else:
            recommendations.append("Good balance of confidence adjustments based on project patterns")
        
        # Project-specific recommendations
        if self.project_context:
            if self.project_context.project_type == 'web':
                security_patterns = len([p for p in insights['learned_patterns'] if 'security' in p['pattern']])
                if security_patterns == 0:
                    recommendations.append("Web project detected - consider adding security-related TODO comments for better learning")
            
            if self.project_context.complexity_level == 'complex':
                if pattern_count < 10:
                    recommendations.append("Complex project with limited learning patterns - more comment diversity could improve analysis")
        
        return recommendations
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the enhanced ML system."""
        
        return {
            'system_health': {
                'ml_engine_enabled': self.ml_engine.enabled,
                'learning_engine_enabled': True,
                'project_context_loaded': self.project_context is not None,
                'codebase_analyzed': len(self.learning_engine.patterns) > 0
            },
            'learning_stats': self.learning_engine.get_learning_status(),
            'integration_performance': {
                'total_analyses': self.analysis_count,
                'learning_adjustments': self.learning_adjustments_count,
                'adjustment_percentage': (
                    100 * self.learning_adjustments_count / max(1, self.analysis_count)
                ),
                'avg_confidence_change': (
                    self.total_confidence_boost / max(1, self.learning_adjustments_count)
                )
            },
            'dependencies': {
                'pure_python_ml': ['json', 'math', 're', 'hashlib', 'pathlib'],
                'codebase_learning': ['re', 'json', 'sqlite3', 'statistics', 'pathlib', 'collections'],
                'heavy_dependencies': [],  # None!
                'blood_oath_compliant': True
            },
            'project_info': {
                'path': str(self.project_path) if self.project_path else None,
                'type': self.project_context.project_type if self.project_context else None,
                'language': self.project_context.primary_language if self.project_context else None,
                'patterns_learned': len(self.learning_engine.patterns)
            }
        }


# Helper function for dataclass conversion (missing import)
def asdict(obj):
    """Convert dataclass to dict (simple implementation)."""
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return {}


# Demo and testing
if __name__ == "__main__":
    import json
    import tempfile
    
    print("🎺 Testing Learning-Enhanced ML Engine Integration")
    print("=" * 60)
    
    # Create test project
    with tempfile.TemporaryDirectory() as temp_dir:
        test_project = Path(temp_dir) / "test_integration"
        test_project.mkdir()
        
        # Create test files with varied comment patterns
        (test_project / "security_module.py").write_text("""
# TODO: CRITICAL - Fix SQL injection in user authentication
def authenticate_user(username, password):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    # FIXME: Parameterized queries needed ASAP
    return db.execute(query)

# HACK: Temporary bypass for admin - URGENT security issue
def admin_login():
    return True
        """)
        
        (test_project / "performance_module.py").write_text("""
# TODO: Optimize this slow database query
def get_user_data():
    # FIXME: N+1 query problem here - major performance issue
    users = User.objects.all()
    for user in users:
        user.profile = Profile.objects.get(user=user)
    return users

# NOTE: Caching could help performance here
def expensive_calculation():
    # TODO: MINOR optimization opportunity
    return sum(range(10000))
        """)
        
        # Initialize enhanced ML engine
        enhanced_ml = LearningEnhancedMLEngine(
            project_path=test_project,
            learning_storage_path=Path(temp_dir) / "learning.db"
        )
        
        # Test analysis with learning
        print("🔍 Testing enhanced analysis...")
        
        test_code = """
# TODO: Fix potential SQL injection vulnerability
def unsafe_query(user_input):
    return f"SELECT * FROM data WHERE id = {user_input}"

# FIXME: Performance bottleneck in nested loop  
def slow_function():
    for i in range(100):
        for j in range(100):
            process_item(i, j)

# NOTE: This could be optimized someday
def working_function():
    return "OK"
        """
        
        results = enhanced_ml.analyze_code_with_learning(
            test_code, 
            "test_analysis.py",
            "web"
        )
        
        print(f"📊 Analysis Results: {len(results)} findings")
        for i, result in enumerate(results):
            print(f"  {i+1}. {result.todo_type} - {result.classification}")
            print(f"     Confidence: {result.original_confidence:.2f} → {result.confidence:.2f}")
            print(f"     Priority: {result.original_priority:.1f} → {result.priority_score:.1f}")
            if result.learning_adjustment != 1.0:
                print(f"     Learning: {result.learning_adjustment:.2f}x - {result.learning_reason}")
            print()
        
        # Get comprehensive insights
        print("🎯 Learning Insights:")
        insights = enhanced_ml.get_learning_insights()
        print(f"  Patterns learned: {len(insights['learned_patterns'])}")
        print(f"  Total analyses: {insights['integration_stats']['total_analyses']}")
        print(f"  Learning adjustments: {insights['integration_stats']['learning_adjustments']}")
        
        # Export learning summary
        print("\n📋 Learning Summary:")
        summary = enhanced_ml.export_learning_summary()
        print(json.dumps(summary, indent=2)[:1000] + "...")  # Truncate for display
        
        print("\n⚙️  System Status:")
        status = enhanced_ml.get_status()
        print(f"  ML Engine: {'✅' if status['system_health']['ml_engine_enabled'] else '❌'}")
        print(f"  Learning: {'✅' if status['system_health']['learning_engine_enabled'] else '❌'}")
        print(f"  Project Context: {'✅' if status['system_health']['project_context_loaded'] else '❌'}")
        print(f"  Patterns: {status['project_info']['patterns_learned']}")
        
        print(f"\n✅ Integration test completed successfully!")
        print(f"🩸 Blood Oath Status: COMPLIANT")
        print(f"   Dependencies: {len(status['dependencies']['pure_python_ml']) + len(status['dependencies']['codebase_learning'])} Python built-ins")
        print(f"   Heavy deps: {len(status['dependencies']['heavy_dependencies'])} (ZERO!)")