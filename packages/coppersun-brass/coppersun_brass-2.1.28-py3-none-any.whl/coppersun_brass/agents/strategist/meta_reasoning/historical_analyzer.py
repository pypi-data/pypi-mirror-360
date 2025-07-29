"""
Historical Analysis Engine for Copper Alloy Brass Meta-Reasoning Layer
Main engine for DCP snapshot analysis, trend detection, and health scoring.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TrendDirection(Enum):
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


class HealthStatus(Enum):
    EXCELLENT = "excellent"  # 90-100
    GOOD = "good"           # 70-89
    WARNING = "warning"     # 50-69
    CRITICAL = "critical"   # 0-49


@dataclass
class TrendAnalysis:
    """Result of trend analysis"""
    direction: TrendDirection
    confidence: float  # 0-1
    rate_of_change: float
    anomalies: List[Dict[str, Any]]
    predictions: Dict[str, Any]
    timeframe_days: int
    metric_type: str


@dataclass
class HealthScore:
    """Project health scoring result"""
    overall_score: float  # 0-100
    status: HealthStatus
    components: Dict[str, float]
    recommendations: List[str]
    calculated_at: datetime
    confidence: float


@dataclass
class DriftAnalysis:
    """Architectural drift detection result"""
    drift_score: float  # 0-100, higher = more drift
    drift_indicators: List[str]
    significant_changes: List[Dict[str, Any]]
    recommendations: List[str]
    baseline_snapshot_id: str
    current_snapshot_id: str


class HistoricalAnalyzer:
    """
    Main historical analysis engine for Copper Alloy Brass meta-reasoning.
    Provides trend detection, health scoring, and drift analysis.
    """
    
    def __init__(self, dcp_manager, snapshot_manager, diff_engine):
        self.dcp_manager = dcp_manager
        self.snapshot_manager = snapshot_manager
        self.diff_engine = diff_engine
        self.logger = logging.getLogger(__name__)
        
        # Analysis configuration
        self.config = {
            'trend_confidence_threshold': 0.7,
            'health_weight_resolution': 0.25,
            'health_weight_priority': 0.20,
            'health_weight_effectiveness': 0.25,
            'health_weight_stability': 0.20,
            'health_weight_momentum': 0.10,
            'drift_threshold': 30.0,  # 0-100 scale
            'anomaly_threshold': 2.0,  # standard deviations
        }
    
    async def analyze_trends(self, project_id: str, timeframe_days: int = 30, 
                           metric_type: str = "all") -> Dict[str, TrendAnalysis]:
        """
        Analyze DCP trends over specified timeframe.
        
        Args:
            project_id: Project identifier
            timeframe_days: Analysis timeframe in days
            metric_type: Type of metrics to analyze ('all', 'priority', 'observations', 'health')
            
        Returns:
            Dictionary of trend analyses by metric type
        """
        try:
            self.logger.info(f"Starting trend analysis for project {project_id}, {timeframe_days} days")
            
            # Get snapshots for timeframe
            snapshots = await self.snapshot_manager.get_snapshots(
                project_id, 
                timeframe_days=timeframe_days
            )
            
            if len(snapshots) < 2:
                self.logger.warning(f"Insufficient snapshots for trend analysis: {len(snapshots)}")
                return {}
            
            trends = {}
            
            if metric_type in ["all", "priority"]:
                trends["priority"] = await self._analyze_priority_trends(snapshots)
                
            if metric_type in ["all", "observations"]:
                trends["observations"] = await self._analyze_observation_trends(snapshots)
                
            if metric_type in ["all", "health"]:
                trends["health"] = await self._analyze_health_trends(snapshots)
                
            if metric_type in ["all", "agent_effectiveness"]:
                trends["agent_effectiveness"] = await self._analyze_agent_trends(snapshots)
            
            self.logger.info(f"Completed trend analysis: {len(trends)} trend types")
            return trends
            
        except Exception as e:
            self.logger.error(f"Error in trend analysis: {e}")
            raise
    
    async def detect_drift(self, baseline_snapshot_id: str, 
                          current_snapshot_id: str) -> DriftAnalysis:
        """
        Detect architectural drift between two snapshots.
        
        Args:
            baseline_snapshot_id: Baseline snapshot ID
            current_snapshot_id: Current snapshot ID
            
        Returns:
            DriftAnalysis with drift score and indicators
        """
        try:
            self.logger.info(f"Detecting drift: {baseline_snapshot_id} -> {current_snapshot_id}")
            
            # Get snapshots
            baseline = await self.snapshot_manager.get_snapshot(baseline_snapshot_id)
            current = await self.snapshot_manager.get_snapshot(current_snapshot_id)
            
            if not baseline or not current:
                raise ValueError("One or both snapshots not found")
            
            # Generate comprehensive diff
            diff_result = self.diff_engine.compare_snapshots(
                baseline['snapshot_data'], 
                current['snapshot_data']
            )
            
            # Calculate drift score
            drift_score = self._calculate_drift_score(diff_result)
            
            # Identify drift indicators
            drift_indicators = self._identify_drift_indicators(diff_result, drift_score)
            
            # Extract significant changes
            significant_changes = self._extract_significant_changes(diff_result)
            
            # Generate recommendations
            recommendations = self._generate_drift_recommendations(drift_score, drift_indicators)
            
            drift_analysis = DriftAnalysis(
                drift_score=drift_score,
                drift_indicators=drift_indicators,
                significant_changes=significant_changes,
                recommendations=recommendations,
                baseline_snapshot_id=baseline_snapshot_id,
                current_snapshot_id=current_snapshot_id
            )
            
            self.logger.info(f"Drift analysis complete: score={drift_score:.1f}")
            return drift_analysis
            
        except Exception as e:
            self.logger.error(f"Error in drift detection: {e}")
            raise
    
    async def generate_health_score(self, project_id: str) -> HealthScore:
        """
        Generate comprehensive project health score.
        
        Args:
            project_id: Project identifier
            
        Returns:
            HealthScore with overall score and component breakdown
        """
        try:
            self.logger.info(f"Generating health score for project {project_id}")
            
            # Get recent snapshots for analysis
            recent_snapshots = await self.snapshot_manager.get_snapshots(
                project_id, 
                limit=10,
                timeframe_days=7
            )
            
            if not recent_snapshots:
                raise ValueError("No recent snapshots available for health analysis")
            
            current_dcp = recent_snapshots[0]['snapshot_data']
            
            # Calculate health components
            components = {}
            
            # Resolution rate (25% weight)
            components['resolution_rate'] = await self._calculate_resolution_rate(
                recent_snapshots
            )
            
            # Priority balance (20% weight)
            components['priority_balance'] = self._calculate_priority_balance(current_dcp)
            
            # Agent effectiveness (25% weight)
            components['agent_effectiveness'] = await self._calculate_agent_effectiveness(
                recent_snapshots
            )
            
            # Architectural stability (20% weight)
            components['architectural_stability'] = await self._calculate_stability_score(
                recent_snapshots
            )
            
            # Trend momentum (10% weight)
            components['trend_momentum'] = await self._calculate_momentum_score(
                project_id, recent_snapshots
            )
            
            # Calculate weighted overall score
            overall_score = (
                components['resolution_rate'] * self.config['health_weight_resolution'] +
                components['priority_balance'] * self.config['health_weight_priority'] +
                components['agent_effectiveness'] * self.config['health_weight_effectiveness'] +
                components['architectural_stability'] * self.config['health_weight_stability'] +
                components['trend_momentum'] * self.config['health_weight_momentum']
            )
            
            # Determine health status
            if overall_score >= 90:
                status = HealthStatus.EXCELLENT
            elif overall_score >= 70:
                status = HealthStatus.GOOD
            elif overall_score >= 50:
                status = HealthStatus.WARNING
            else:
                status = HealthStatus.CRITICAL
            
            # Generate recommendations
            recommendations = self._generate_health_recommendations(components, overall_score)
            
            # Calculate confidence based on data availability
            confidence = min(1.0, len(recent_snapshots) / 10.0)
            
            health_score = HealthScore(
                overall_score=overall_score,
                status=status,
                components=components,
                recommendations=recommendations,
                calculated_at=datetime.utcnow(),
                confidence=confidence
            )
            
            self.logger.info(f"Health score generated: {overall_score:.1f} ({status.value})")
            return health_score
            
        except Exception as e:
            self.logger.error(f"Error generating health score: {e}")
            raise
    
    # Private helper methods
    
    async def _analyze_priority_trends(self, snapshots: List[Dict]) -> TrendAnalysis:
        """Analyze priority trends across snapshots"""
        priority_data = []
        
        for snapshot in snapshots:
            dcp_data = snapshot['snapshot_data']
            observations = dcp_data.get('current_observations', [])
            
            if observations:
                avg_priority = sum(obs.get('priority', 0) for obs in observations) / len(observations)
                priority_data.append({
                    'timestamp': snapshot['created_at'],
                    'avg_priority': avg_priority,
                    'total_observations': len(observations)
                })
        
        return self._calculate_trend_metrics(priority_data, 'avg_priority', 'priority')
    
    async def _analyze_observation_trends(self, snapshots: List[Dict]) -> TrendAnalysis:
        """Analyze observation count and type trends"""
        obs_data = []
        
        for snapshot in snapshots:
            dcp_data = snapshot['snapshot_data']
            observations = dcp_data.get('current_observations', [])
            
            obs_data.append({
                'timestamp': snapshot['created_at'],
                'total_count': len(observations),
                'types': self._categorize_observations(observations)
            })
        
        return self._calculate_trend_metrics(obs_data, 'total_count', 'observations')
    
    async def _analyze_health_trends(self, snapshots: List[Dict]) -> TrendAnalysis:
        """Analyze health score trends over time"""
        health_data = []
        
        for snapshot in snapshots:
            # Calculate simplified health score for each snapshot
            health_score = await self._calculate_snapshot_health(snapshot)
            health_data.append({
                'timestamp': snapshot['created_at'],
                'health_score': health_score
            })
        
        return self._calculate_trend_metrics(health_data, 'health_score', 'health')
    
    async def _analyze_agent_trends(self, snapshots: List[Dict]) -> TrendAnalysis:
        """Analyze agent effectiveness trends"""
        agent_data = []
        
        for snapshot in snapshots:
            dcp_data = snapshot['snapshot_data']
            observations = dcp_data.get('current_observations', [])
            
            # Calculate agent effectiveness metrics
            effectiveness = self._calculate_agent_snapshot_effectiveness(observations)
            agent_data.append({
                'timestamp': snapshot['created_at'],
                'effectiveness': effectiveness
            })
        
        return self._calculate_trend_metrics(agent_data, 'effectiveness', 'agent_effectiveness')
    
    def _calculate_trend_metrics(self, data: List[Dict], metric_key: str, 
                                metric_type: str) -> TrendAnalysis:
        """Calculate trend metrics from time series data"""
        if len(data) < 2:
            return TrendAnalysis(
                direction=TrendDirection.STABLE,
                confidence=0.0,
                rate_of_change=0.0,
                anomalies=[],
                predictions={},
                timeframe_days=0,
                metric_type=metric_type
            )
        
        values = [item[metric_key] for item in data]
        
        # Calculate linear trend
        direction, rate_of_change, confidence = self._calculate_linear_trend(values)
        
        # Detect anomalies
        anomalies = self._detect_anomalies(data, metric_key)
        
        # Generate simple predictions
        predictions = self._generate_predictions(values, rate_of_change)
        
        # Calculate timeframe
        timeframe_days = (
            datetime.fromisoformat(data[-1]['timestamp'].replace('Z', '+00:00')) -
            datetime.fromisoformat(data[0]['timestamp'].replace('Z', '+00:00'))
        ).days
        
        return TrendAnalysis(
            direction=direction,
            confidence=confidence,
            rate_of_change=rate_of_change,
            anomalies=anomalies,
            predictions=predictions,
            timeframe_days=timeframe_days,
            metric_type=metric_type
        )
    
    def _calculate_linear_trend(self, values: List[float]) -> Tuple[TrendDirection, float, float]:
        """Calculate linear trend direction and confidence"""
        if len(values) < 2:
            return TrendDirection.STABLE, 0.0, 0.0
        
        # Simple linear regression
        n = len(values)
        x = list(range(n))
        y = values
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        # Calculate slope
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        # Determine direction
        if abs(slope) < 0.1:  # Threshold for stable
            direction = TrendDirection.STABLE
        elif slope > 0:
            direction = TrendDirection.INCREASING
        else:
            direction = TrendDirection.DECREASING
        
        # Calculate confidence based on R-squared
        y_mean = sum_y / n
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
        intercept = (sum_y - slope * sum_x) / n
        ss_res = sum((y[i] - (slope * x[i] + intercept)) ** 2 for i in range(n))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        confidence = max(0.0, min(1.0, r_squared))
        
        return direction, slope, confidence
    
    def _detect_anomalies(self, data: List[Dict], metric_key: str) -> List[Dict[str, Any]]:
        """Detect anomalies in time series data"""
        values = [item[metric_key] for item in data]
        
        if len(values) < 3:
            return []
        
        mean_val = sum(values) / len(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        anomalies = []
        threshold = self.config['anomaly_threshold'] * std_dev
        
        for i, item in enumerate(data):
            value = item[metric_key]
            if abs(value - mean_val) > threshold:
                anomalies.append({
                    'timestamp': item['timestamp'],
                    'value': value,
                    'deviation': abs(value - mean_val) / std_dev if std_dev > 0 else 0,
                    'type': 'spike' if value > mean_val else 'drop'
                })
        
        return anomalies
    
    def _generate_predictions(self, values: List[float], rate_of_change: float) -> Dict[str, Any]:
        """Generate simple predictions based on trend"""
        if not values:
            return {}
        
        current_value = values[-1]
        
        return {
            'next_value_estimate': current_value + rate_of_change,
            'confidence': 'low',  # Simple predictions have low confidence
            'trend_continuation': rate_of_change > 0.1 or rate_of_change < -0.1
        }
    
    def _calculate_drift_score(self, diff_result: Dict) -> float:
        """Calculate architectural drift score from diff result"""
        changes = diff_result.get('summary', {})
        total_changes = changes.get('total_changes', 0)
        significance_score = changes.get('significance_score', 0.0)
        
        # Normalize to 0-100 scale
        drift_score = min(100.0, (total_changes * 5) + (significance_score * 50))
        
        return drift_score
    
    def _identify_drift_indicators(self, diff_result: Dict, drift_score: float) -> List[str]:
        """Identify specific drift indicators"""
        indicators = []
        
        obs_changes = diff_result.get('observations', {})
        if len(obs_changes.get('added', [])) > 5:
            indicators.append("High observation creation rate")
        
        if len(obs_changes.get('priority_changes', [])) > 3:
            indicators.append("Significant priority shifts")
        
        if drift_score > self.config['drift_threshold']:
            indicators.append("Overall change volume exceeds threshold")
        
        return indicators
    
    def _extract_significant_changes(self, diff_result: Dict) -> List[Dict[str, Any]]:
        """Extract most significant changes from diff"""
        significant = []
        
        # High priority changes
        priority_changes = diff_result.get('observations', {}).get('priority_changes', [])
        for change in priority_changes:
            if abs(change.get('old_priority', 0) - change.get('new_priority', 0)) > 20:
                significant.append({
                    'type': 'priority_change',
                    'description': f"Priority changed from {change.get('old_priority')} to {change.get('new_priority')}",
                    'impact': 'high'
                })
        
        return significant[:10]  # Limit to top 10
    
    def _generate_drift_recommendations(self, drift_score: float, 
                                      drift_indicators: List[str]) -> List[str]:
        """Generate recommendations based on drift analysis"""
        recommendations = []
        
        if drift_score > 50:
            recommendations.append("Consider architectural review - high drift detected")
        
        if "High observation creation rate" in drift_indicators:
            recommendations.append("Review observation management - creation rate may indicate instability")
        
        if "Significant priority shifts" in drift_indicators:
            recommendations.append("Examine priority assignment logic - frequent changes may indicate unclear requirements")
        
        return recommendations
    
    async def _calculate_resolution_rate(self, snapshots: List[Dict]) -> float:
        """Calculate observation resolution rate"""
        if len(snapshots) < 2:
            return 50.0  # Default moderate score
        
        # Compare oldest and newest snapshots
        old_obs = set(obs['id'] for obs in snapshots[-1]['snapshot_data'].get('current_observations', []))
        new_obs = set(obs['id'] for obs in snapshots[0]['snapshot_data'].get('current_observations', []))
        
        resolved_count = len(old_obs - new_obs)
        total_old = len(old_obs)
        
        if total_old == 0:
            return 100.0
        
        resolution_rate = (resolved_count / total_old) * 100
        return min(100.0, resolution_rate)
    
    def _calculate_priority_balance(self, dcp_data: Dict) -> float:
        """Calculate priority distribution balance score"""
        observations = dcp_data.get('current_observations', [])
        
        if not observations:
            return 100.0
        
        priorities = [obs.get('priority', 0) for obs in observations]
        
        # Check for balanced distribution across priority ranges
        high_priority = sum(1 for p in priorities if p >= 80)
        medium_priority = sum(1 for p in priorities if 40 <= p < 80)
        low_priority = sum(1 for p in priorities if p < 40)
        
        total = len(priorities)
        if total == 0:
            return 100.0
        
        # Ideal distribution: 20% high, 60% medium, 20% low
        high_ratio = high_priority / total
        medium_ratio = medium_priority / total
        low_ratio = low_priority / total
        
        # Calculate deviation from ideal
        ideal_deviation = (
            abs(high_ratio - 0.2) +
            abs(medium_ratio - 0.6) +
            abs(low_ratio - 0.2)
        )
        
        balance_score = max(0.0, 100.0 - (ideal_deviation * 100))
        return balance_score
    
    async def _calculate_agent_effectiveness(self, snapshots: List[Dict]) -> float:
        """Calculate agent effectiveness score"""
        if not snapshots:
            return 50.0
        
        # Analyze agent annotations and effectiveness scores
        total_effectiveness = 0.0
        effectiveness_count = 0
        
        for snapshot in snapshots:
            recommendations = snapshot['snapshot_data'].get('strategic_recommendations', [])
            for rec in recommendations:
                if 'effectiveness_score' in rec:
                    total_effectiveness += rec['effectiveness_score']
                    effectiveness_count += 1
        
        if effectiveness_count == 0:
            return 50.0
        
        avg_effectiveness = total_effectiveness / effectiveness_count
        # Convert to 0-100 scale (assuming effectiveness scores are 0-10)
        return min(100.0, avg_effectiveness * 10)
    
    async def _calculate_stability_score(self, snapshots: List[Dict]) -> float:
        """Calculate architectural stability score"""
        if len(snapshots) < 2:
            return 100.0
        
        # Compare consecutive snapshots for stability
        stability_scores = []
        
        for i in range(len(snapshots) - 1):
            diff_result = self.diff_engine.compare_snapshots(
                snapshots[i+1]['snapshot_data'],
                snapshots[i]['snapshot_data']
            )
            
            change_count = diff_result.get('summary', {}).get('total_changes', 0)
            # Lower change count = higher stability
            snapshot_stability = max(0.0, 100.0 - (change_count * 5))
            stability_scores.append(snapshot_stability)
        
        return sum(stability_scores) / len(stability_scores) if stability_scores else 100.0
    
    async def _calculate_momentum_score(self, project_id: str, snapshots: List[Dict]) -> float:
        """Calculate trend momentum score"""
        try:
            trends = await self.analyze_trends(project_id, timeframe_days=7, metric_type="health")
            
            if 'health' in trends:
                trend = trends['health']
                if trend.direction == TrendDirection.INCREASING and trend.confidence > 0.5:
                    return 80.0
                elif trend.direction == TrendDirection.DECREASING and trend.confidence > 0.5:
                    return 20.0
                else:
                    return 50.0
            
            return 50.0
            
        except Exception:
            return 50.0  # Default if trend analysis fails
    
    def _generate_health_recommendations(self, components: Dict[str, float], 
                                       overall_score: float) -> List[str]:
        """Generate health improvement recommendations"""
        recommendations = []
        
        if components.get('resolution_rate', 0) < 50:
            recommendations.append("Focus on resolving existing observations - resolution rate is low")
        
        if components.get('priority_balance', 0) < 60:
            recommendations.append("Review priority assignments - distribution appears unbalanced")
        
        if components.get('agent_effectiveness', 0) < 70:
            recommendations.append("Examine agent performance - effectiveness scores suggest room for improvement")
        
        if components.get('architectural_stability', 0) < 80:
            recommendations.append("Consider stabilizing architecture - frequent changes detected")
        
        if overall_score < 70:
            recommendations.append("Overall project health needs attention - consider comprehensive review")
        
        return recommendations
    
    def _categorize_observations(self, observations: List[Dict]) -> Dict[str, int]:
        """Categorize observations by type"""
        categories = {}
        
        for obs in observations:
            obs_type = obs.get('type', 'unknown')
            categories[obs_type] = categories.get(obs_type, 0) + 1
        
        return categories
    
    async def _calculate_snapshot_health(self, snapshot: Dict) -> float:
        """Calculate simplified health score for a single snapshot"""
        dcp_data = snapshot['snapshot_data']
        observations = dcp_data.get('current_observations', [])
        
        if not observations:
            return 100.0
        
        # Simple health metrics
        high_priority_ratio = sum(1 for obs in observations if obs.get('priority', 0) >= 80) / len(observations)
        avg_priority = sum(obs.get('priority', 0) for obs in observations) / len(observations)
        
        # Higher high-priority ratio = lower health (more issues)
        health_score = 100.0 - (high_priority_ratio * 50) - (max(0, avg_priority - 50))
        
        return max(0.0, min(100.0, health_score))
    
    def _calculate_agent_snapshot_effectiveness(self, observations: List[Dict]) -> float:
        """Calculate agent effectiveness for a single snapshot"""
        if not observations:
            return 100.0
        
        # Look for effectiveness indicators in observations
        effectiveness_scores = []
        
        for obs in observations:
            # If observation has been addressed by agents, it's effective
            if obs.get('status') in ['resolved', 'in_progress']:
                effectiveness_scores.append(80.0)
            elif 'claude_annotation' in obs:
                effectiveness_scores.append(70.0)
            else:
                effectiveness_scores.append(40.0)
        
        return sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 50.0


# Export main class
__all__ = ['HistoricalAnalyzer', 'TrendAnalysis', 'HealthScore', 'DriftAnalysis']
