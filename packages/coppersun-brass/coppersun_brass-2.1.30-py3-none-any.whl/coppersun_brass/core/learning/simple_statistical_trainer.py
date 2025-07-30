"""
Simple Statistical Trainer - Pure Python Built-ins Only
======================================================

🩸 BLOOD OATH COMPLIANT: Uses ONLY Python standard library
✅ No numpy, no sklearn, no external dependencies
✅ Statistical learning with built-in statistics module
✅ Always works, zero installation problems

Replaces heavy ML dependencies with simple, effective statistical learning.
"""

import statistics
import json
import sqlite3
import math
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class SimpleLearningPattern:
    """A pattern learned from user feedback - pure Python dataclass."""
    pattern_type: str           # e.g., "sql_injection", "performance_issue"
    user_rating_average: float  # Average user rating (1-5)
    feedback_count: int         # Number of feedback instances
    confidence_multiplier: float # How much to adjust confidence (0.3 - 2.0)
    project_context: str        # Project type where this applies
    last_updated: str          # ISO timestamp
    success_rate: float        # Percentage of positive feedback

class SimpleStatisticalTrainer:
    """
    Statistical learning using only Python built-ins
    
    🩸 BLOOD OATH: Zero external dependencies beyond Python standard library
    ✅ Uses: statistics, json, sqlite3, dataclasses, math
    ❌ Never uses: numpy, sklearn, torch, onnxruntime
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize with SQLite storage (Python built-in)."""
        self.storage_path = storage_path or Path("learning_data.db")
        self.patterns = {}  # In-memory pattern cache
        self.feedback_history = []  # Feedback history
        
        # Initialize SQLite database
        self._init_database()
        
        # Load existing patterns
        self._load_patterns()
        
        logger.info("✅ Simple Statistical Trainer initialized with Python built-ins only")
    
    def _init_database(self):
        """Initialize SQLite database (Python built-in)."""
        with sqlite3.connect(self.storage_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_feedback (
                    id INTEGER PRIMARY KEY,
                    finding_id TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    user_rating INTEGER NOT NULL,
                    comment TEXT,
                    project_context TEXT,
                    timestamp TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learned_patterns (
                    pattern_type TEXT PRIMARY KEY,
                    pattern_data TEXT NOT NULL,
                    last_updated TEXT NOT NULL
                )
            """)
            
            conn.commit()
    
    def record_user_feedback(
        self, 
        finding_id: str, 
        pattern_type: str, 
        user_rating: int, 
        comment: str = "", 
        project_context: str = "general"
    ) -> bool:
        """
        Record user feedback using SQLite (Python built-in).
        
        Args:
            finding_id: Unique identifier for the finding
            pattern_type: Type of pattern (e.g., "sql_injection", "todo_bug")
            user_rating: User rating 1-5 (1=bad, 5=excellent)
            comment: Optional user comment
            project_context: Project type context
            
        Returns:
            Success boolean
        """
        try:
            timestamp = datetime.now().isoformat()
            
            # Store in SQLite
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute("""
                    INSERT INTO user_feedback 
                    (finding_id, pattern_type, user_rating, comment, project_context, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (finding_id, pattern_type, user_rating, comment, project_context, timestamp))
                conn.commit()
            
            # Update in-memory cache
            self.feedback_history.append({
                'finding_id': finding_id,
                'pattern_type': pattern_type,
                'user_rating': user_rating,
                'comment': comment,
                'project_context': project_context,
                'timestamp': timestamp
            })
            
            # Update learned patterns
            self._update_pattern_statistics(pattern_type, user_rating, project_context)
            
            logger.info(f"✅ Recorded feedback: {pattern_type} rated {user_rating}/5")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record feedback: {e}")
            return False
    
    def _update_pattern_statistics(self, pattern_type: str, user_rating: int, project_context: str):
        """Update pattern statistics using Python built-in statistics module."""
        
        # Get all feedback for this pattern type
        pattern_feedback = self._get_pattern_feedback(pattern_type, project_context)
        
        if len(pattern_feedback) < 1:
            return
        
        # Calculate statistics using built-in statistics module
        ratings = [fb['user_rating'] for fb in pattern_feedback]
        
        try:
            rating_average = statistics.mean(ratings)
            feedback_count = len(ratings)
            
            # Calculate success rate (ratings 4-5 are "success")
            successful_ratings = [r for r in ratings if r >= 4]
            success_rate = len(successful_ratings) / len(ratings) if ratings else 0.0
            
            # Calculate confidence multiplier using simple statistics
            # High average rating (4+) -> boost confidence
            # Low average rating (2-) -> reduce confidence  
            # Use exponential scaling based on rating and sample size
            
            if rating_average >= 4.0:
                # User loves these findings - boost confidence
                base_multiplier = 1.0 + (rating_average - 3.0) * 0.4  # Max 1.8x
            elif rating_average <= 2.0:
                # User dislikes these findings - reduce confidence
                base_multiplier = 0.3 + (rating_average - 1.0) * 0.35  # Min 0.3x
            else:
                # Neutral ratings - slight adjustment
                base_multiplier = 0.8 + (rating_average - 2.0) * 0.4
            
            # Apply sample size confidence (Wilson score concept, simplified)
            # More samples = more confident in the adjustment
            sample_confidence = min(1.0, math.log(feedback_count + 1) / math.log(10))
            confidence_multiplier = 1.0 + (base_multiplier - 1.0) * sample_confidence
            
            # Clamp to reasonable bounds
            confidence_multiplier = max(0.3, min(2.0, confidence_multiplier))
            
            # Create learned pattern
            pattern = SimpleLearningPattern(
                pattern_type=pattern_type,
                user_rating_average=rating_average,
                feedback_count=feedback_count,
                confidence_multiplier=confidence_multiplier,
                project_context=project_context,
                last_updated=datetime.now().isoformat(),
                success_rate=success_rate
            )
            
            # Store in memory and database
            pattern_key = f"{pattern_type}_{project_context}"
            self.patterns[pattern_key] = pattern
            self._save_pattern(pattern_key, pattern)
            
            logger.info(f"✅ Updated pattern {pattern_type}: {rating_average:.1f}★ -> {confidence_multiplier:.2f}x confidence")
            
        except statistics.StatisticsError as e:
            logger.warning(f"Statistics calculation failed: {e}")
    
    def _get_pattern_feedback(self, pattern_type: str, project_context: str) -> List[Dict]:
        """Get all feedback for a specific pattern type."""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                cursor = conn.execute("""
                    SELECT finding_id, pattern_type, user_rating, comment, project_context, timestamp
                    FROM user_feedback
                    WHERE pattern_type = ? AND project_context = ?
                    ORDER BY timestamp DESC
                """, (pattern_type, project_context))
                
                feedback = []
                for row in cursor.fetchall():
                    feedback.append({
                        'finding_id': row[0],
                        'pattern_type': row[1], 
                        'user_rating': row[2],
                        'comment': row[3],
                        'project_context': row[4],
                        'timestamp': row[5]
                    })
                
                return feedback
                
        except Exception as e:
            logger.error(f"Failed to get pattern feedback: {e}")
            return []
    
    def _save_pattern(self, pattern_key: str, pattern: SimpleLearningPattern):
        """Save learned pattern to SQLite."""
        try:
            pattern_json = json.dumps(asdict(pattern))
            
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO learned_patterns 
                    (pattern_type, pattern_data, last_updated)
                    VALUES (?, ?, ?)
                """, (pattern_key, pattern_json, pattern.last_updated))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to save pattern: {e}")
    
    def _load_patterns(self):
        """Load learned patterns from SQLite."""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                cursor = conn.execute("""
                    SELECT pattern_type, pattern_data 
                    FROM learned_patterns
                """)
                
                for row in cursor.fetchall():
                    pattern_key = row[0]
                    pattern_data = json.loads(row[1])
                    pattern = SimpleLearningPattern(**pattern_data)
                    self.patterns[pattern_key] = pattern
                
                logger.info(f"✅ Loaded {len(self.patterns)} learned patterns")
                
        except Exception as e:
            logger.warning(f"Failed to load patterns: {e}")
    
    def get_confidence_adjustment(self, pattern_type: str, project_context: str = "general") -> float:
        """
        Get confidence multiplier for a pattern type.
        
        Args:
            pattern_type: Type of pattern to check
            project_context: Project context
            
        Returns:
            Confidence multiplier (0.3 - 2.0)
        """
        pattern_key = f"{pattern_type}_{project_context}"
        
        if pattern_key in self.patterns:
            multiplier = self.patterns[pattern_key].confidence_multiplier
            logger.debug(f"Confidence adjustment for {pattern_type}: {multiplier:.2f}x")
            return multiplier
        
        # No learning data - return neutral
        return 1.0
    
    def get_learning_insights(self, min_feedback: int = 3) -> Dict[str, Any]:
        """
        Get insights about learned patterns using Python built-ins.
        
        Args:
            min_feedback: Minimum feedback count to include pattern
            
        Returns:
            Dictionary of insights
        """
        insights = {
            'total_patterns': len(self.patterns),
            'total_feedback': len(self.feedback_history),
            'high_confidence_patterns': [],
            'problematic_patterns': [],
            'statistics': {},
            'recommendations': []
        }
        
        # Analyze patterns with sufficient feedback
        valid_patterns = [
            p for p in self.patterns.values() 
            if p.feedback_count >= min_feedback
        ]
        
        if not valid_patterns:
            insights['recommendations'].append("Need more user feedback to generate insights")
            return insights
        
        # Calculate overall statistics using built-in statistics
        try:
            all_ratings = [p.user_rating_average for p in valid_patterns]
            all_multipliers = [p.confidence_multiplier for p in valid_patterns]
            
            insights['statistics'] = {
                'avg_user_rating': statistics.mean(all_ratings),
                'rating_stdev': statistics.stdev(all_ratings) if len(all_ratings) > 1 else 0,
                'avg_confidence_multiplier': statistics.mean(all_multipliers),
                'highly_rated_patterns': len([r for r in all_ratings if r >= 4.0]),
                'poorly_rated_patterns': len([r for r in all_ratings if r <= 2.0])
            }
            
            # Identify high-confidence patterns (users love these)
            for pattern in valid_patterns:
                if pattern.user_rating_average >= 4.0 and pattern.confidence_multiplier > 1.2:
                    insights['high_confidence_patterns'].append({
                        'pattern_type': pattern.pattern_type,
                        'rating': pattern.user_rating_average,
                        'multiplier': pattern.confidence_multiplier,
                        'feedback_count': pattern.feedback_count,
                        'success_rate': pattern.success_rate
                    })
            
            # Identify problematic patterns (users dislike these)
            for pattern in valid_patterns:
                if pattern.user_rating_average <= 2.5 and pattern.confidence_multiplier < 0.8:
                    insights['problematic_patterns'].append({
                        'pattern_type': pattern.pattern_type,
                        'rating': pattern.user_rating_average,
                        'multiplier': pattern.confidence_multiplier,
                        'feedback_count': pattern.feedback_count,
                        'success_rate': pattern.success_rate
                    })
            
            # Generate recommendations
            if insights['statistics']['avg_user_rating'] > 3.5:
                insights['recommendations'].append("Learning system is working well - high user satisfaction")
            else:
                insights['recommendations'].append("Consider adjusting analysis patterns - mixed user feedback")
            
            if len(insights['high_confidence_patterns']) > 0:
                insights['recommendations'].append(f"Found {len(insights['high_confidence_patterns'])} highly valued pattern types")
            
            if len(insights['problematic_patterns']) > 0:
                insights['recommendations'].append(f"Consider reducing {len(insights['problematic_patterns'])} problematic pattern types")
                
        except statistics.StatisticsError:
            insights['recommendations'].append("Insufficient data for statistical analysis")
        
        return insights
    
    def enhance_analysis_results(self, analysis_results: List[Any], project_context: str = "general") -> List[Any]:
        """
        Enhance analysis results with learned confidence adjustments.
        
        Args:
            analysis_results: Results from pure Python ML analysis
            project_context: Project context for learning
            
        Returns:
            Enhanced results with adjusted confidence scores
        """
        enhanced_results = []
        adjustments_applied = 0
        
        for result in analysis_results:
            # Create enhanced copy
            enhanced_result = result
            
            # Determine pattern type from result
            pattern_type = self._extract_pattern_type(result)
            
            if pattern_type:
                # Get confidence adjustment
                adjustment = self.get_confidence_adjustment(pattern_type, project_context)
                
                if adjustment != 1.0:
                    # Apply adjustment to confidence and priority
                    if hasattr(enhanced_result, 'confidence'):
                        enhanced_result.confidence *= adjustment
                        enhanced_result.confidence = max(0.1, min(1.0, enhanced_result.confidence))
                    
                    if hasattr(enhanced_result, 'priority_score'):
                        enhanced_result.priority_score *= adjustment
                        enhanced_result.priority_score = max(1, min(100, enhanced_result.priority_score))
                    
                    adjustments_applied += 1
            
            enhanced_results.append(enhanced_result)
        
        if adjustments_applied > 0:
            logger.info(f"✅ Applied learning adjustments to {adjustments_applied} findings")
        
        return enhanced_results
    
    def _extract_pattern_type(self, result: Any) -> Optional[str]:
        """Extract pattern type from analysis result."""
        # Try different ways to get pattern type
        if hasattr(result, 'todo_type'):
            return result.todo_type.lower()
        elif hasattr(result, 'classification'):
            return result.classification.lower()
        elif hasattr(result, 'finding_type'):
            return result.finding_type.lower()
        elif isinstance(result, dict):
            return result.get('type', result.get('category', 'unknown')).lower()
        else:
            return 'unknown'
    
    def get_training_status(self) -> Dict[str, Any]:
        """Get status of the learning system."""
        return {
            'enabled': True,
            'total_patterns': len(self.patterns),
            'total_feedback': len(self.feedback_history),
            'storage_path': str(self.storage_path),
            'dependencies': ['statistics', 'json', 'sqlite3', 'dataclasses', 'math'],
            'heavy_dependencies': [],  # None!
            'blood_oath_compliant': True,
            'last_updated': datetime.now().isoformat()
        }


# Example usage and testing
if __name__ == "__main__":
    # Demo of simple statistical learning
    trainer = SimpleStatisticalTrainer(Path("demo_learning.db"))
    
    # Simulate user feedback
    trainer.record_user_feedback("find_001", "sql_injection", 5, "Great catch!", "python_web")
    trainer.record_user_feedback("find_002", "sql_injection", 5, "Saved us from bug", "python_web") 
    trainer.record_user_feedback("find_003", "performance_issue", 2, "False positive", "python_web")
    trainer.record_user_feedback("find_004", "performance_issue", 1, "Not relevant", "python_web")
    
    # Get insights
    insights = trainer.get_learning_insights()
    print("📊 Learning Insights:")
    print(json.dumps(insights, indent=2))
    
    # Test confidence adjustments
    sql_adjustment = trainer.get_confidence_adjustment("sql_injection", "python_web")
    perf_adjustment = trainer.get_confidence_adjustment("performance_issue", "python_web")
    
    print(f"\n🎯 Confidence Adjustments:")
    print(f"SQL Injection: {sql_adjustment:.2f}x (users love these)")
    print(f"Performance Issues: {perf_adjustment:.2f}x (users dislike these)")