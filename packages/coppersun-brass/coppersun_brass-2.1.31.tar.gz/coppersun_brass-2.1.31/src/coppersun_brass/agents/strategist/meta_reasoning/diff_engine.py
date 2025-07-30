"""
DCP Diff Engine for Copper Alloy Brass Historical Analysis
Advanced diffing algorithms for comparing DCP snapshots and detecting changes.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    MOVED = "moved"
    PRIORITY_CHANGED = "priority_changed"


class SignificanceLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ChangeRecord:
    """Record of a specific change between snapshots"""
    change_type: ChangeType
    significance: SignificanceLevel
    path: str
    old_value: Any
    new_value: Any
    context: Dict[str, Any]
    impact_score: float  # 0-100


@dataclass
class DiffSummary:
    """Summary of differences between snapshots"""
    total_changes: int
    significance_score: float  # 0-100
    drift_indicators: List[str]
    change_distribution: Dict[str, int]
    impact_areas: List[str]


@dataclass
class DiffResult:
    """Complete diff result between two DCP snapshots"""
    summary: DiffSummary
    observations: Dict[str, List[ChangeRecord]]
    recommendations: Dict[str, List[ChangeRecord]]
    metadata: Dict[str, List[ChangeRecord]]
    analysis_timestamp: datetime
    baseline_id: Optional[str]
    current_id: Optional[str]


class DiffEngine:
    """
    Advanced diffing engine for DCP snapshot comparisons.
    Provides detailed change detection, significance scoring, and drift analysis.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Diffing configuration
        self.config = {
            'priority_change_threshold': 10,  # Minimum change to be significant
            'significance_weights': {
                'priority_change': 2.0,
                'observation_added': 1.5,
                'observation_removed': 1.8,
                'recommendation_modified': 1.2,
                'metadata_change': 0.5
            },
            'drift_thresholds': {
                'low': 10,
                'medium': 25,
                'high': 50,
                'critical': 75
            }
        }
    
    def compare_snapshots(self, baseline_dcp: Dict, current_dcp: Dict,
                         baseline_id: Optional[str] = None,
                         current_id: Optional[str] = None) -> DiffResult:
        """
        Generate comprehensive diff between two DCP snapshots.
        
        Args:
            baseline_dcp: Earlier DCP snapshot data
            current_dcp: Later DCP snapshot data
            baseline_id: Optional baseline snapshot ID
            current_id: Optional current snapshot ID
            
        Returns:
            Complete DiffResult with all changes and analysis
        """
        try:
            self.logger.info("Starting comprehensive DCP snapshot comparison")
            
            # Initialize change tracking
            all_changes = []
            
            # Compare observations
            obs_changes = self.analyze_observation_changes(
                baseline_dcp.get('current_observations', []),
                current_dcp.get('current_observations', [])
            )
            all_changes.extend(obs_changes['all_changes'])
            
            # Compare recommendations
            rec_changes = self.analyze_recommendation_changes(
                baseline_dcp.get('strategic_recommendations', []),
                current_dcp.get('strategic_recommendations', [])
            )
            all_changes.extend(rec_changes['all_changes'])
            
            # Compare metadata
            meta_changes = self.analyze_metadata_changes(
                baseline_dcp.get('meta', {}),
                current_dcp.get('meta', {})
            )
            all_changes.extend(meta_changes['all_changes'])
            
            # Generate summary
            summary = self._generate_diff_summary(all_changes)
            
            # Create comprehensive result
            diff_result = DiffResult(
                summary=summary,
                observations=obs_changes,
                recommendations=rec_changes,
                metadata=meta_changes,
                analysis_timestamp=datetime.utcnow(),
                baseline_id=baseline_id,
                current_id=current_id
            )
            
            self.logger.info(f"Diff analysis complete: {summary.total_changes} changes, "
                           f"significance={summary.significance_score:.1f}")
            
            return diff_result
            
        except Exception as e:
            self.logger.error(f"Error in snapshot comparison: {e}")
            raise
    
    def analyze_observation_changes(self, old_observations: List[Dict], 
                                  new_observations: List[Dict]) -> Dict[str, Any]:
        """
        Analyze changes in observations between snapshots.
        
        Args:
            old_observations: Observations from baseline snapshot
            new_observations: Observations from current snapshot
            
        Returns:
            Dictionary with categorized observation changes
        """
        try:
            # Create ID-based lookups
            old_obs_map = {obs['id']: obs for obs in old_observations}
            new_obs_map = {obs['id']: obs for obs in new_observations}
            
            old_ids = set(old_obs_map.keys())
            new_ids = set(new_obs_map.keys())
            
            changes = {
                'added': [],
                'removed': [],
                'modified': [],
                'priority_changes': [],
                'all_changes': []
            }
            
            # Find added observations
            added_ids = new_ids - old_ids
            for obs_id in added_ids:
                obs = new_obs_map[obs_id]
                change = ChangeRecord(
                    change_type=ChangeType.ADDED,
                    significance=self._calculate_add_significance(obs),
                    path=f"observations.{obs_id}",
                    old_value=None,
                    new_value=obs,
                    context={'observation_type': obs.get('type', 'unknown')},
                    impact_score=self._calculate_impact_score(ChangeType.ADDED, obs)
                )
                changes['added'].append(change)
                changes['all_changes'].append(change)
            
            # Find removed observations
            removed_ids = old_ids - new_ids
            for obs_id in removed_ids:
                obs = old_obs_map[obs_id]
                change = ChangeRecord(
                    change_type=ChangeType.REMOVED,
                    significance=self._calculate_remove_significance(obs),
                    path=f"observations.{obs_id}",
                    old_value=obs,
                    new_value=None,
                    context={'observation_type': obs.get('type', 'unknown')},
                    impact_score=self._calculate_impact_score(ChangeType.REMOVED, obs)
                )
                changes['removed'].append(change)
                changes['all_changes'].append(change)
            
            # Find modified observations
            common_ids = old_ids & new_ids
            for obs_id in common_ids:
                old_obs = old_obs_map[obs_id]
                new_obs = new_obs_map[obs_id]
                
                obs_changes = self._compare_observations(old_obs, new_obs, obs_id)
                changes['modified'].extend(obs_changes)
                changes['all_changes'].extend(obs_changes)
                
                # Check for priority changes specifically
                old_priority = old_obs.get('priority', 0)
                new_priority = new_obs.get('priority', 0)
                
                if abs(old_priority - new_priority) >= self.config['priority_change_threshold']:
                    priority_change = ChangeRecord(
                        change_type=ChangeType.PRIORITY_CHANGED,
                        significance=self._calculate_priority_change_significance(old_priority, new_priority),
                        path=f"observations.{obs_id}.priority",
                        old_value=old_priority,
                        new_value=new_priority,
                        context={
                            'observation_type': old_obs.get('type', 'unknown'),
                            'priority_delta': new_priority - old_priority
                        },
                        impact_score=self._calculate_priority_impact_score(old_priority, new_priority)
                    )
                    changes['priority_changes'].append(priority_change)
                    changes['all_changes'].append(priority_change)
            
            self.logger.info(f"Observation analysis: {len(changes['added'])} added, "
                           f"{len(changes['removed'])} removed, {len(changes['modified'])} modified")
            
            return changes
            
        except Exception as e:
            self.logger.error(f"Error analyzing observation changes: {e}")
            raise
    
    def analyze_recommendation_changes(self, old_recommendations: List[Dict],
                                     new_recommendations: List[Dict]) -> Dict[str, Any]:
        """
        Analyze changes in strategic recommendations.
        
        Args:
            old_recommendations: Recommendations from baseline snapshot
            new_recommendations: Recommendations from current snapshot
            
        Returns:
            Dictionary with categorized recommendation changes
        """
        try:
            changes = {
                'added': [],
                'removed': [],
                'modified': [],
                'all_changes': []
            }
            
            # Use content-based comparison for recommendations (no guaranteed IDs)
            old_hashes = {self._hash_recommendation(rec): rec for rec in old_recommendations}
            new_hashes = {self._hash_recommendation(rec): rec for rec in new_recommendations}
            
            old_hash_set = set(old_hashes.keys())
            new_hash_set = set(new_hashes.keys())
            
            # Find added recommendations
            added_hashes = new_hash_set - old_hash_set
            for rec_hash in added_hashes:
                rec = new_hashes[rec_hash]
                change = ChangeRecord(
                    change_type=ChangeType.ADDED,
                    significance=self._calculate_recommendation_significance(rec),
                    path=f"recommendations.{rec_hash[:8]}",
                    old_value=None,
                    new_value=rec,
                    context={'recommendation_type': 'strategic'},
                    impact_score=rec.get('priority', 50)
                )
                changes['added'].append(change)
                changes['all_changes'].append(change)
            
            # Find removed recommendations
            removed_hashes = old_hash_set - new_hash_set
            for rec_hash in removed_hashes:
                rec = old_hashes[rec_hash]
                change = ChangeRecord(
                    change_type=ChangeType.REMOVED,
                    significance=self._calculate_recommendation_significance(rec),
                    path=f"recommendations.{rec_hash[:8]}",
                    old_value=rec,
                    new_value=None,
                    context={'recommendation_type': 'strategic'},
                    impact_score=rec.get('priority', 50)
                )
                changes['removed'].append(change)
                changes['all_changes'].append(change)
            
            # For recommendations, we focus on additions/removals rather than modifications
            # since they typically change completely rather than incrementally
            
            self.logger.info(f"Recommendation analysis: {len(changes['added'])} added, "
                           f"{len(changes['removed'])} removed")
            
            return changes
            
        except Exception as e:
            self.logger.error(f"Error analyzing recommendation changes: {e}")
            raise
    
    def analyze_metadata_changes(self, old_metadata: Dict, new_metadata: Dict) -> Dict[str, Any]:
        """
        Analyze changes in DCP metadata.
        
        Args:
            old_metadata: Metadata from baseline snapshot
            new_metadata: Metadata from current snapshot
            
        Returns:
            Dictionary with metadata changes
        """
        try:
            changes = {
                'modified': [],
                'all_changes': []
            }
            
            # Compare specific metadata fields
            important_fields = ['version', 'generated_at', 'token_budget_hint']
            
            for field in important_fields:
                old_value = old_metadata.get(field)
                new_value = new_metadata.get(field)
                
                if old_value != new_value:
                    change = ChangeRecord(
                        change_type=ChangeType.MODIFIED,
                        significance=self._calculate_metadata_significance(field, old_value, new_value),
                        path=f"meta.{field}",
                        old_value=old_value,
                        new_value=new_value,
                        context={'metadata_field': field},
                        impact_score=self._calculate_metadata_impact_score(field)
                    )
                    changes['modified'].append(change)
                    changes['all_changes'].append(change)
            
            return changes
            
        except Exception as e:
            self.logger.error(f"Error analyzing metadata changes: {e}")
            raise
    
    def detect_priority_shifts(self, old_priorities: List[int], 
                             new_priorities: List[int]) -> Dict[str, Any]:
        """
        Detect significant priority distribution changes.
        
        Args:
            old_priorities: Priority values from baseline
            new_priorities: Priority values from current
            
        Returns:
            Priority shift analysis
        """
        try:
            if not old_priorities or not new_priorities:
                return {'shifts': [], 'summary': 'insufficient_data'}
            
            # Calculate priority distribution statistics
            old_stats = self._calculate_priority_stats(old_priorities)
            new_stats = self._calculate_priority_stats(new_priorities)
            
            shifts = []
            
            # Check for mean shift
            mean_shift = new_stats['mean'] - old_stats['mean']
            if abs(mean_shift) > 10:
                shifts.append({
                    'type': 'mean_shift',
                    'magnitude': mean_shift,
                    'direction': 'increase' if mean_shift > 0 else 'decrease',
                    'significance': 'high' if abs(mean_shift) > 20 else 'medium'
                })
            
            # Check for distribution changes
            old_high = old_stats['high_priority_ratio']
            new_high = new_stats['high_priority_ratio']
            high_ratio_change = new_high - old_high
            
            if abs(high_ratio_change) > 0.2:  # 20% change in high priority ratio
                shifts.append({
                    'type': 'distribution_shift',
                    'category': 'high_priority',
                    'change': high_ratio_change,
                    'significance': 'high' if abs(high_ratio_change) > 0.3 else 'medium'
                })
            
            return {
                'shifts': shifts,
                'old_stats': old_stats,
                'new_stats': new_stats,
                'summary': 'significant_shifts' if shifts else 'stable'
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting priority shifts: {e}")
            return {'shifts': [], 'summary': 'error'}
    
    # Private helper methods
    
    def _compare_observations(self, old_obs: Dict, new_obs: Dict, obs_id: str) -> List[ChangeRecord]:
        """Compare individual observation fields for changes"""
        changes = []
        
        # Fields to compare (excluding priority, handled separately)
        compare_fields = ['summary', 'type', 'status', 'claude_annotation', 'effectiveness_score']
        
        for field in compare_fields:
            old_value = old_obs.get(field)
            new_value = new_obs.get(field)
            
            if old_value != new_value:
                change = ChangeRecord(
                    change_type=ChangeType.MODIFIED,
                    significance=self._calculate_field_change_significance(field, old_value, new_value),
                    path=f"observations.{obs_id}.{field}",
                    old_value=old_value,
                    new_value=new_value,
                    context={'field': field, 'observation_id': obs_id},
                    impact_score=self._calculate_field_impact_score(field, old_value, new_value)
                )
                changes.append(change)
        
        return changes
    
    def _hash_recommendation(self, recommendation: Dict) -> str:
        """Generate hash for recommendation content comparison"""
        # Use summary and priority for hash (stable fields)
        content = f"{recommendation.get('summary', '')}{recommendation.get('priority', 0)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _calculate_add_significance(self, observation: Dict) -> SignificanceLevel:
        """Calculate significance level for added observation"""
        priority = observation.get('priority', 0)
        obs_type = observation.get('type', '')
        
        if priority >= 90 or obs_type in ['security', 'critical']:
            return SignificanceLevel.CRITICAL
        elif priority >= 70:
            return SignificanceLevel.HIGH
        elif priority >= 40:
            return SignificanceLevel.MEDIUM
        else:
            return SignificanceLevel.LOW
    
    def _calculate_remove_significance(self, observation: Dict) -> SignificanceLevel:
        """Calculate significance level for removed observation"""
        # Removal is generally more significant than addition
        priority = observation.get('priority', 0)
        
        if priority >= 80:
            return SignificanceLevel.CRITICAL
        elif priority >= 60:
            return SignificanceLevel.HIGH
        elif priority >= 30:
            return SignificanceLevel.MEDIUM
        else:
            return SignificanceLevel.LOW
    
    def _calculate_priority_change_significance(self, old_priority: int, 
                                              new_priority: int) -> SignificanceLevel:
        """Calculate significance of priority change"""
        delta = abs(new_priority - old_priority)
        
        if delta >= 40:
            return SignificanceLevel.CRITICAL
        elif delta >= 25:
            return SignificanceLevel.HIGH
        elif delta >= 15:
            return SignificanceLevel.MEDIUM
        else:
            return SignificanceLevel.LOW
    
    def _calculate_recommendation_significance(self, recommendation: Dict) -> SignificanceLevel:
        """Calculate significance of recommendation change"""
        priority = recommendation.get('priority', 0)
        
        if priority >= 90:
            return SignificanceLevel.CRITICAL
        elif priority >= 70:
            return SignificanceLevel.HIGH
        elif priority >= 50:
            return SignificanceLevel.MEDIUM
        else:
            return SignificanceLevel.LOW
    
    def _calculate_metadata_significance(self, field: str, old_value: Any, 
                                       new_value: Any) -> SignificanceLevel:
        """Calculate significance of metadata change"""
        if field == 'version':
            return SignificanceLevel.MEDIUM
        elif field == 'token_budget_hint':
            return SignificanceLevel.LOW
        else:
            return SignificanceLevel.LOW
    
    def _calculate_field_change_significance(self, field: str, old_value: Any, 
                                           new_value: Any) -> SignificanceLevel:
        """Calculate significance of specific field change"""
        if field == 'status':
            return SignificanceLevel.HIGH  # Status changes are important
        elif field == 'claude_annotation':
            return SignificanceLevel.MEDIUM  # Annotations are moderately important
        elif field == 'effectiveness_score':
            return SignificanceLevel.MEDIUM
        else:
            return SignificanceLevel.LOW
    
    def _calculate_impact_score(self, change_type: ChangeType, observation: Dict) -> float:
        """Calculate impact score for observation change"""
        base_score = observation.get('priority', 50)
        
        # Apply change type modifiers
        modifiers = {
            ChangeType.ADDED: 1.0,
            ChangeType.REMOVED: 1.2,  # Removals have higher impact
            ChangeType.MODIFIED: 0.8,
            ChangeType.PRIORITY_CHANGED: 1.1
        }
        
        return min(100.0, base_score * modifiers.get(change_type, 1.0))
    
    def _calculate_priority_impact_score(self, old_priority: int, new_priority: int) -> float:
        """Calculate impact score for priority change"""
        delta = abs(new_priority - old_priority)
        max_priority = max(old_priority, new_priority)
        
        # Higher priority changes have more impact
        return min(100.0, delta * 2 + max_priority * 0.5)
    
    def _calculate_field_impact_score(self, field: str, old_value: Any, new_value: Any) -> float:
        """Calculate impact score for field change"""
        field_weights = {
            'status': 80.0,
            'summary': 60.0,
            'type': 70.0,
            'claude_annotation': 50.0,
            'effectiveness_score': 40.0
        }
        
        return field_weights.get(field, 30.0)
    
    def _calculate_metadata_impact_score(self, field: str) -> float:
        """Calculate impact score for metadata change"""
        field_scores = {
            'version': 40.0,
            'token_budget_hint': 20.0,
            'generated_at': 10.0
        }
        
        return field_scores.get(field, 15.0)
    
    def _generate_diff_summary(self, all_changes: List[ChangeRecord]) -> DiffSummary:
        """Generate comprehensive diff summary"""
        if not all_changes:
            return DiffSummary(
                total_changes=0,
                significance_score=0.0,
                drift_indicators=[],
                change_distribution={},
                impact_areas=[]
            )
        
        # Calculate significance score
        total_impact = sum(change.impact_score for change in all_changes)
        avg_impact = total_impact / len(all_changes)
        significance_score = min(100.0, avg_impact)
        
        # Count change types
        change_distribution = {}
        for change in all_changes:
            change_type = change.change_type.value
            change_distribution[change_type] = change_distribution.get(change_type, 0) + 1
        
        # Identify drift indicators
        drift_indicators = self._identify_drift_indicators_from_changes(all_changes)
        
        # Identify impact areas
        impact_areas = self._identify_impact_areas(all_changes)
        
        return DiffSummary(
            total_changes=len(all_changes),
            significance_score=significance_score,
            drift_indicators=drift_indicators,
            change_distribution=change_distribution,
            impact_areas=impact_areas
        )
    
    def _identify_drift_indicators_from_changes(self, changes: List[ChangeRecord]) -> List[str]:
        """Identify architectural drift indicators from changes"""
        indicators = []
        
        # High volume of changes
        if len(changes) > 20:
            indicators.append("High change volume detected")
        
        # Many priority changes
        priority_changes = [c for c in changes if c.change_type == ChangeType.PRIORITY_CHANGED]
        if len(priority_changes) > 5:
            indicators.append("Frequent priority adjustments")
        
        # Critical significance changes
        critical_changes = [c for c in changes if c.significance == SignificanceLevel.CRITICAL]
        if len(critical_changes) > 2:
            indicators.append("Multiple critical changes")
        
        # High impact score average
        avg_impact = sum(c.impact_score for c in changes) / len(changes)
        if avg_impact > 70:
            indicators.append("High average impact score")
        
        return indicators
    
    def _identify_impact_areas(self, changes: List[ChangeRecord]) -> List[str]:
        """Identify areas most impacted by changes"""
        area_scores = {}
        
        for change in changes:
            # Extract area from path (e.g., "observations.123.priority" -> "observations")
            area = change.path.split('.')[0]
            area_scores[area] = area_scores.get(area, 0) + change.impact_score
        
        # Sort by total impact score
        sorted_areas = sorted(area_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top 3 impact areas
        return [area for area, score in sorted_areas[:3]]
    
    def _calculate_priority_stats(self, priorities: List[int]) -> Dict[str, float]:
        """Calculate priority distribution statistics"""
        if not priorities:
            return {'mean': 0, 'std': 0, 'high_priority_ratio': 0}
        
        mean_priority = sum(priorities) / len(priorities)
        variance = sum((p - mean_priority) ** 2 for p in priorities) / len(priorities)
        std_priority = variance ** 0.5
        
        high_priority_count = sum(1 for p in priorities if p >= 80)
        high_priority_ratio = high_priority_count / len(priorities)
        
        return {
            'mean': mean_priority,
            'std': std_priority,
            'high_priority_ratio': high_priority_ratio,
            'min': min(priorities),
            'max': max(priorities),
            'count': len(priorities)
        }


# Export main classes
__all__ = ['DiffEngine', 'DiffResult', 'ChangeRecord', 'DiffSummary', 'ChangeType', 'SignificanceLevel']