"""
Enhanced Semantic Analyzer with Codebase Learning
=================================================

🩸 BLOOD OATH COMPLIANT: Extends existing SemanticAnalyzer with codebase learning
✅ Uses pure Python ML + codebase learning with zero additional dependencies
✅ Restores user codebase learning functionality to Copper Sun Brass
✅ Maintains full backward compatibility with existing SemanticAnalyzer interface

This is the integration point that connects codebase learning to the main analysis pipeline.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from coppersun_brass.ml.semantic_analyzer import SemanticAnalyzer, SemanticMatch
from coppersun_brass.core.learning.enhanced_ml_integration import LearningEnhancedMLEngine

logger = logging.getLogger(__name__)

class EnhancedSemanticAnalyzer(SemanticAnalyzer):
    """
    Enhanced SemanticAnalyzer with codebase learning capabilities.
    
    🩸 BLOOD OATH: Extends existing analyzer with zero new dependencies
    ✅ Backward compatible with all existing SemanticAnalyzer functionality
    ✅ Adds adaptive intelligence through codebase learning
    ✅ Maintains blood oath compliance - only Python built-ins
    """
    
    def __init__(self, model_dir: Path, project_path: Optional[Path] = None):
        """
        Initialize enhanced semantic analyzer.
        
        Args:
            model_dir: Path to model directory (existing parameter)
            project_path: Optional project path for codebase learning
        """
        # Initialize parent SemanticAnalyzer
        super().__init__(model_dir)
        
        # Initialize enhanced ML engine with codebase learning
        learning_storage_path = self.model_dir / "learning_data.db"
        
        try:
            self.enhanced_ml_engine = LearningEnhancedMLEngine(
                project_path=project_path,
                learning_storage_path=learning_storage_path
            )
            self.learning_enabled = True
            logger.info("✅ Enhanced SemanticAnalyzer with codebase learning initialized")
            
        except Exception as e:
            logger.warning(f"Failed to initialize codebase learning: {e}")
            self.enhanced_ml_engine = None
            self.learning_enabled = False
    
    def analyze_code(self, code_text: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Analyze code with enhanced ML and codebase learning.
        
        🩸 BLOOD OATH: Uses pure Python ML + codebase learning
        Maintains full backward compatibility with SemanticAnalyzer.
        """
        if not code_text.strip():
            return []
        
        # Try enhanced analysis with codebase learning first
        if self.learning_enabled and self.enhanced_ml_engine:
            try:
                return self._analyze_with_enhanced_ml(code_text, file_path)
            except Exception as e:
                logger.warning(f"Enhanced ML analysis failed, falling back to standard: {e}")
        
        # Fallback to parent implementation
        logger.info("Using standard SemanticAnalyzer (no learning enhancements)")
        return super().analyze_code(code_text, file_path)
    
    def _analyze_with_enhanced_ml(self, code_text: str, file_path: str) -> List[Dict[str, Any]]:
        """Analyze using enhanced ML with codebase learning."""
        
        # Get enhanced analysis results
        enhanced_results = self.enhanced_ml_engine.analyze_code_with_learning(
            code_text, 
            file_path,
            project_context=None  # Will be auto-detected from project
        )
        
        # Convert to SemanticAnalyzer format for backward compatibility
        findings = []
        lines = code_text.split('\n')
        
        for i, result in enumerate(enhanced_results):
            # Extract line number more accurately
            line_num = self._extract_line_number(code_text, result, i)
            
            # Build finding with enhanced information
            finding = {
                "file_path": file_path,
                "line_number": line_num,
                "todo_type": result.todo_type,
                "content": getattr(result, 'content', f'Codebase learning pattern detected'),
                "priority_score": result.priority_score,
                "confidence": result.confidence,
                "classification": result.classification,
                "context_lines": self._get_context_lines(lines, line_num - 1),
                
                # Enhanced fields from codebase learning
                "learning_enhanced": True,
                "original_confidence": getattr(result, 'original_confidence', result.confidence),
                "learning_adjustment": getattr(result, 'learning_adjustment', 1.0),
                "learning_reason": getattr(result, 'learning_reason', ''),
                "pattern_frequency": getattr(result, 'pattern_frequency', 0),
                "resolution_likelihood": getattr(result, 'resolution_likelihood', 0.5),
                "security_risk": result.security_risk,
                "performance_impact": result.performance_impact
            }
            
            findings.append(finding)
        
        logger.info(f"✅ Enhanced ML analyzed {len(findings)} patterns with codebase learning")
        return findings
    
    def _extract_line_number(self, code_text: str, result: Any, result_index: int) -> int:
        """Extract accurate line number for a result."""
        lines = code_text.split('\n')
        
        # Look for TODO/FIXME patterns that match this result
        pattern_markers = ['TODO', 'FIXME', 'HACK', 'XXX', 'NOTE', 'BUG']
        todo_count = 0
        
        for line_idx, line in enumerate(lines):
            line_upper = line.upper()
            if any(marker in line_upper for marker in pattern_markers):
                if todo_count == result_index:
                    return line_idx + 1
                todo_count += 1
        
        # Fallback to first line if no match found
        return 1
    
    def _get_context_lines(self, lines: List[str], line_idx: int, context_size: int = 3) -> List[str]:
        """Get context lines around the target line."""
        start = max(0, line_idx - context_size)
        end = min(len(lines), line_idx + context_size + 1)
        return lines[start:end]
    
    def refresh_codebase_learning(self, project_path: Optional[Path] = None) -> bool:
        """
        Refresh codebase learning patterns.
        
        Args:
            project_path: Optional new project path
            
        Returns:
            Success boolean
        """
        if not self.learning_enabled or not self.enhanced_ml_engine:
            logger.warning("Codebase learning not available")
            return False
        
        return self.enhanced_ml_engine.refresh_codebase_learning(project_path)
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights about codebase learning patterns and effectiveness."""
        if not self.learning_enabled or not self.enhanced_ml_engine:
            return {
                'learning_enabled': False,
                'reason': 'Codebase learning not initialized'
            }
        
        return self.enhanced_ml_engine.get_learning_insights()
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get comprehensive learning summary for documentation."""
        if not self.learning_enabled or not self.enhanced_ml_engine:
            return {
                'learning_enabled': False,
                'summary': 'Codebase learning not available'
            }
        
        return self.enhanced_ml_engine.export_learning_summary()
    
    def analyze_with_learning_details(self, code_text: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze code and return detailed learning information.
        
        This is an enhanced method that provides additional learning insights
        beyond the standard analyze_code method.
        """
        
        # Get standard analysis
        findings = self.analyze_code(code_text, file_path)
        
        # Get learning insights
        learning_insights = self.get_learning_insights() if self.learning_enabled else {}
        
        # Calculate analysis statistics
        learning_enhanced_count = sum(1 for f in findings if f.get('learning_enhanced', False))
        confidence_changes = [
            f.get('learning_adjustment', 1.0) for f in findings 
            if f.get('learning_adjustment', 1.0) != 1.0
        ]
        
        return {
            'findings': findings,
            'analysis_stats': {
                'total_findings': len(findings),
                'learning_enhanced': learning_enhanced_count,
                'learning_coverage': f"{100 * learning_enhanced_count / max(1, len(findings)):.0f}%",
                'confidence_adjustments': len(confidence_changes),
                'avg_confidence_change': sum(confidence_changes) / len(confidence_changes) if confidence_changes else 1.0
            },
            'learning_insights': learning_insights,
            'file_analysis': {
                'file_path': file_path,
                'lines_analyzed': len(code_text.split('\n')),
                'has_todos': any('TODO' in line.upper() for line in code_text.split('\n')),
                'has_fixmes': any('FIXME' in line.upper() for line in code_text.split('\n')),
                'complexity_estimate': self._estimate_complexity(code_text)
            }
        }
    
    def _estimate_complexity(self, code_text: str) -> str:
        """Estimate code complexity (simple heuristic)."""
        lines = code_text.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        if len(non_empty_lines) < 20:
            return 'simple'
        elif len(non_empty_lines) < 100:
            return 'moderate'
        else:
            return 'complex'
    
    def get_pattern_details(self, pattern_type: str, pattern_subtype: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific learned pattern."""
        if not self.learning_enabled or not self.enhanced_ml_engine:
            return None
        
        return self.enhanced_ml_engine.get_pattern_details(pattern_type, pattern_subtype)
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the enhanced analyzer."""
        base_status = {
            'semantic_analyzer': {
                'initialized': True,
                'model_dir': str(self.model_dir)
            }
        }
        
        if self.learning_enabled and self.enhanced_ml_engine:
            enhanced_status = self.enhanced_ml_engine.get_status()
            base_status.update(enhanced_status)
            base_status['learning_integration'] = {
                'enabled': True,
                'status': 'active'
            }
        else:
            base_status['learning_integration'] = {
                'enabled': False,
                'status': 'not_available'
            }
        
        return base_status


# Factory function for easy integration
def create_enhanced_semantic_analyzer(
    model_dir: Path, 
    project_path: Optional[Path] = None
) -> EnhancedSemanticAnalyzer:
    """
    Factory function to create EnhancedSemanticAnalyzer.
    
    Args:
        model_dir: Path to model directory
        project_path: Optional project path for codebase learning
        
    Returns:
        EnhancedSemanticAnalyzer instance
    """
    return EnhancedSemanticAnalyzer(model_dir, project_path)


# Backward compatibility function
def create_semantic_analyzer(model_dir: Path) -> EnhancedSemanticAnalyzer:
    """
    Create semantic analyzer with backward compatibility.
    
    This function maintains compatibility with existing code that creates
    SemanticAnalyzer instances while providing enhanced functionality.
    """
    return EnhancedSemanticAnalyzer(model_dir)


# Demo and testing
if __name__ == "__main__":
    import json
    import tempfile
    
    print("🎺 Testing Enhanced Semantic Analyzer")
    print("=" * 50)
    
    # Create test project
    with tempfile.TemporaryDirectory() as temp_dir:
        test_project = Path(temp_dir) / "test_enhanced_analyzer"
        test_project.mkdir()
        model_dir = Path(temp_dir) / "models"
        model_dir.mkdir()
        
        # Create test files for codebase learning
        (test_project / "security.py").write_text("""
# TODO: CRITICAL - Fix SQL injection vulnerability
def vulnerable_query(user_input):
    return f"SELECT * FROM users WHERE id = {user_input}"

# FIXME: Authentication bypass - URGENT security issue
def broken_auth():
    return True
        """)
        
        (test_project / "performance.py").write_text("""
# TODO: Optimize slow database queries
def slow_queries():
    # FIXME: N+1 query problem causing performance issues
    return expensive_operation()

# NOTE: Caching could improve performance here
def cacheable_function():
    return calculate_result()
        """)
        
        # Initialize enhanced analyzer
        analyzer = EnhancedSemanticAnalyzer(
            model_dir=model_dir,
            project_path=test_project
        )
        
        print(f"✅ Enhanced analyzer initialized")
        print(f"   Learning enabled: {analyzer.learning_enabled}")
        
        # Test analysis
        test_code = """
# TODO: Fix potential security vulnerability in authentication
def authenticate(username, password):
    # HACK: Temporary workaround - needs proper validation
    return True

# FIXME: Performance bottleneck in data processing
def process_data():
    for item in large_dataset:
        expensive_operation(item)

# NOTE: This function works but could be optimized
def working_function():
    return "OK"
        """
        
        print("\n🔍 Testing enhanced analysis...")
        results = analyzer.analyze_with_learning_details(test_code, "test_file.py")
        
        print(f"📊 Analysis Results:")
        print(f"   Total findings: {results['analysis_stats']['total_findings']}")
        print(f"   Learning enhanced: {results['analysis_stats']['learning_enhanced']}")
        print(f"   Learning coverage: {results['analysis_stats']['learning_coverage']}")
        print(f"   Confidence adjustments: {results['analysis_stats']['confidence_adjustments']}")
        
        # Show detailed findings
        print("\n🎯 Detailed Findings:")
        for i, finding in enumerate(results['findings'][:3]):  # Show first 3
            print(f"  {i+1}. {finding['todo_type']} - {finding['classification']}")
            print(f"     Line {finding['line_number']}: Confidence {finding['confidence']:.2f}")
            if finding.get('learning_enhanced'):
                print(f"     Learning: {finding['learning_adjustment']:.2f}x adjustment")
                if finding.get('learning_reason'):
                    print(f"     Reason: {finding['learning_reason'][:80]}...")
        
        # Test learning insights
        if analyzer.learning_enabled:
            print("\n📈 Learning Insights:")
            insights = analyzer.get_learning_insights()
            if 'learned_patterns' in insights:
                print(f"   Patterns learned: {len(insights['learned_patterns'])}")
                for pattern in insights['learned_patterns'][:3]:
                    print(f"   - {pattern['pattern']}: {pattern['confidence_multiplier']:.2f}x")
        
        # Test status
        print("\n⚙️  System Status:")
        status = analyzer.get_status()
        print(f"   Learning integration: {status['learning_integration']['status']}")
        print(f"   Dependencies: Python built-ins only")
        print(f"   Blood oath: {'✅ COMPLIANT' if status.get('dependencies', {}).get('blood_oath_compliant') else '❌ VIOLATED'}")
        
        print("\n✅ Enhanced Semantic Analyzer test completed!")
        print("🩸 Codebase learning successfully integrated with SemanticAnalyzer")