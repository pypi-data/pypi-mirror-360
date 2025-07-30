"""
Pure Python ML + Simple Learning Integration
===========================================

🩸 BLOOD OATH COMPLIANT: Connects our pure Python ML engine with 
simple statistical learning using ONLY Python built-ins.

This bridges our static pure Python ML analysis with dynamic user feedback learning.
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from coppersun_brass.ml.pure_python_ml import PurePythonMLEngine, MLAnalysisResult
from coppersun_brass.core.learning.simple_statistical_trainer import SimpleStatisticalTrainer

logger = logging.getLogger(__name__)

class LearningEnhancedMLEngine:
    """
    Pure Python ML Engine enhanced with simple statistical learning.
    
    🩸 BLOOD OATH: Uses only Python built-ins for learning
    ✅ Combines static ML analysis with dynamic user feedback
    ✅ Zero additional dependencies beyond our existing system
    """
    
    def __init__(self, learning_storage_path: Optional[Path] = None):
        """Initialize enhanced ML engine with learning capability."""
        
        # Initialize core pure Python ML engine
        self.ml_engine = PurePythonMLEngine()
        
        # Initialize simple statistical learning
        self.learning_trainer = SimpleStatisticalTrainer(learning_storage_path)
        
        # Track learning statistics
        self.analysis_count = 0
        self.learning_adjustments_count = 0
        
        logger.info("✅ Learning-Enhanced ML Engine initialized")
    
    def analyze_code_with_learning(
        self, 
        code_text: str, 
        file_path: str, 
        project_context: str = "general"
    ) -> List[MLAnalysisResult]:
        """
        Analyze code with both pure Python ML and learning enhancements.
        
        Args:
            code_text: Source code to analyze
            file_path: Path to the file being analyzed
            project_context: Project type context for learning
            
        Returns:
            Analysis results enhanced with learning
        """
        # Get base analysis from pure Python ML
        base_results = self.ml_engine.analyze_code(code_text, file_path)
        
        # Apply learning enhancements
        enhanced_results = self.learning_trainer.enhance_analysis_results(
            base_results, 
            project_context
        )
        
        self.analysis_count += 1
        
        logger.info(f"✅ Enhanced analysis: {len(enhanced_results)} findings for {file_path}")
        return enhanced_results
    
    def record_user_feedback(
        self,
        finding_id: str,
        pattern_type: str, 
        user_rating: int,
        comment: str = "",
        project_context: str = "general"
    ) -> bool:
        """
        Record user feedback to improve future analysis.
        
        Args:
            finding_id: Unique identifier for the finding
            pattern_type: Type of pattern (extracted from analysis result)
            user_rating: User rating 1-5 (1=bad, 5=excellent)
            comment: Optional user comment
            project_context: Project context
            
        Returns:
            Success boolean
        """
        success = self.learning_trainer.record_user_feedback(
            finding_id=finding_id,
            pattern_type=pattern_type,
            user_rating=user_rating,
            comment=comment,
            project_context=project_context
        )
        
        if success:
            logger.info(f"✅ Recorded feedback: {pattern_type} rated {user_rating}/5")
        
        return success
    
    def record_feedback_from_result(
        self,
        result: MLAnalysisResult,
        user_rating: int,
        comment: str = "",
        project_context: str = "general"
    ) -> bool:
        """
        Convenience method to record feedback directly from an analysis result.
        
        Args:
            result: The MLAnalysisResult the user is rating
            user_rating: User rating 1-5
            comment: Optional comment
            project_context: Project context
            
        Returns:
            Success boolean
        """
        # Create unique finding ID
        finding_id = f"{result.todo_type}_{result.classification}_{hash(result.confidence)}"
        
        # Extract pattern type
        pattern_type = f"{result.todo_type}_{result.classification}"
        
        return self.record_user_feedback(
            finding_id=finding_id,
            pattern_type=pattern_type,
            user_rating=user_rating,
            comment=comment,
            project_context=project_context
        )
    
    def get_learning_insights(self, min_feedback: int = 3) -> Dict[str, Any]:
        """Get insights about the learning system performance."""
        insights = self.learning_trainer.get_learning_insights(min_feedback)
        
        # Add ML engine statistics
        insights['ml_engine_stats'] = {
            'total_analyses': self.analysis_count,
            'learning_adjustments': self.learning_adjustments_count,
            'pure_python_ml_enabled': self.ml_engine.enabled,
            'learning_patterns_count': len(self.learning_trainer.patterns)
        }
        
        return insights
    
    def get_confidence_adjustment(self, pattern_type: str, project_context: str = "general") -> float:
        """Get confidence multiplier for a pattern type."""
        return self.learning_trainer.get_confidence_adjustment(pattern_type, project_context)
    
    def simulate_user_feedback_session(self, code_samples: List[str]) -> Dict[str, Any]:
        """
        Simulate a user feedback session for testing.
        
        Args:
            code_samples: List of code samples to analyze
            
        Returns:
            Session results
        """
        session_results = {
            'analyses_performed': 0,
            'feedback_recorded': 0,
            'patterns_discovered': [],
            'sample_adjustments': {}
        }
        
        for i, code_sample in enumerate(code_samples):
            # Analyze code
            results = self.analyze_code_with_learning(
                code_sample, 
                f"test_file_{i}.py",
                "python_test"
            )
            
            session_results['analyses_performed'] += 1
            
            # Simulate user feedback (random for demo)
            import random
            for result in results:
                # Simulate realistic user ratings
                if "security" in result.classification.lower() or "injection" in result.todo_type.lower():
                    # Security findings usually rated highly
                    rating = random.choice([4, 5, 5, 5])
                elif "performance" in result.classification.lower():
                    # Performance findings are mixed
                    rating = random.choice([2, 3, 3, 4])
                else:
                    # General findings are average
                    rating = random.choice([2, 3, 3, 4])
                
                # Record feedback
                success = self.record_feedback_from_result(
                    result, 
                    rating, 
                    f"Simulated feedback {rating}/5",
                    "python_test"
                )
                
                if success:
                    session_results['feedback_recorded'] += 1
                    
                    pattern_type = f"{result.todo_type}_{result.classification}"
                    if pattern_type not in session_results['patterns_discovered']:
                        session_results['patterns_discovered'].append(pattern_type)
                    
                    # Track confidence adjustments
                    adjustment = self.get_confidence_adjustment(pattern_type, "python_test")
                    session_results['sample_adjustments'][pattern_type] = adjustment
        
        return session_results
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the learning-enhanced ML system."""
        return {
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
            'learning_trainer_status': self.learning_trainer.get_training_status(),
            'integration_stats': {
                'total_analyses': self.analysis_count,
                'learning_adjustments': self.learning_adjustments_count
            },
            'dependencies': {
                'pure_python_ml': ['json', 'math', 're', 'hashlib', 'pathlib'],
                'simple_learning': ['statistics', 'json', 'sqlite3', 'dataclasses', 'math'],
                'heavy_dependencies': [],  # None!
                'blood_oath_compliant': True
            }
        }

# Demo and testing
if __name__ == "__main__":
    import json
    
    print("🎺 Testing Learning-Enhanced ML Engine")
    print("=" * 50)
    
    # Initialize system
    enhanced_ml = LearningEnhancedMLEngine(Path("demo_enhanced_ml.db"))
    
    # Test code samples
    test_code_samples = [
        """
        # TODO: Fix SQL injection vulnerability here
        query = f"SELECT * FROM users WHERE id = {user_id}"
        cursor.execute(query)
        """,
        
        """
        # FIXME: Performance issue - nested loops
        for i in range(1000):
            for j in range(1000):
                # TODO: Optimize this expensive operation
                result = calculate_complex_operation(i, j)
        """,
        
        """
        # NOTE: Security review needed
        password = "admin123"  # TODO: Use environment variable
        if user_input == password:
            grant_admin_access()
        """
    ]
    
    # Run simulation
    print("🧪 Running feedback simulation...")
    session_results = enhanced_ml.simulate_user_feedback_session(test_code_samples)
    
    print(f"📊 Session Results:")
    print(json.dumps(session_results, indent=2))
    
    print("\n🎯 Learning Insights:")
    insights = enhanced_ml.get_learning_insights()
    print(json.dumps(insights, indent=2))
    
    print("\n⚙️  System Status:")
    status = enhanced_ml.get_status()
    print(json.dumps(status, indent=2))
    
    print("\n✅ Demo completed successfully!")
    print("🩸 Blood Oath Status: COMPLIANT - Zero external dependencies!")