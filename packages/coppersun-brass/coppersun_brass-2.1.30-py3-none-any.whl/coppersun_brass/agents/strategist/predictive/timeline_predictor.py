"""
Copper Alloy Brass Timeline Predictor - Project timeline forecasting and milestone risk assessment
Implements velocity analysis, bottleneck prediction, and milestone completion probability
"""

import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from statistics import mean, stdev
import asyncio

from ..meta_reasoning.historical_analyzer import HistoricalAnalyzer
from .prediction_config import PredictionConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VelocityMetrics:
    """Velocity analysis results"""
    current_velocity: float  # observations resolved per day
    average_velocity: float  # historical average
    velocity_trend: str  # 'increasing', 'decreasing', 'stable'
    velocity_change_rate: float  # percentage change
    confidence: float  # confidence in analysis
    trend_strength: float  # strength of trend
    data_points: int  # number of data points used

@dataclass
class MilestoneRisk:
    """Milestone risk assessment"""
    milestone_name: str
    target_date: datetime
    completion_probability: float
    days_remaining: int
    required_velocity: float
    current_velocity: float
    risk_level: str  # 'low', 'medium', 'high'
    confidence: float
    reasoning: str
    recommended_actions: List[str]

@dataclass
class BottleneckPrediction:
    """Bottleneck prediction results"""
    bottleneck_type: str
    predicted_occurrence: datetime
    probability: float
    impact_severity: str  # 'low', 'medium', 'high'
    affected_areas: List[str]
    confidence: float
    reasoning: str
    preventive_actions: List[str]
    early_warning_indicators: List[str]

class TimelinePredictor:
    """
    Timeline forecasting and milestone risk assessment for Copper Alloy Brass projects
    
    Analyzes historical observation resolution patterns to predict:
    - Project velocity trends and changes
    - Milestone completion probability 
    - Resource bottlenecks and capacity issues
    - Timeline optimization recommendations
    """
    
    def __init__(self, historical_analyzer: HistoricalAnalyzer, config: PredictionConfig):
        """
        Initialize timeline predictor
        
        Args:
            historical_analyzer: For accessing historical trend data
            config: Prediction configuration and thresholds
        """
        self.historical_analyzer = historical_analyzer
        self.config = config
        
        # Analysis parameters
        self.velocity_window_days = config.velocity_analysis_window_days
        self.trend_detection_sensitivity = config.trend_detection_sensitivity
        self.confidence_threshold = config.minimum_confidence_threshold
        
        # Cache for performance
        self._velocity_cache = {}
        self._cache_timestamp = None
        self._cache_ttl_minutes = 10
        
        logger.info("TimelinePredictor initialized")
    
    async def analyze_velocity_trends(self) -> Optional[Dict]:
        """
        Analyze project velocity trends and changes
        
        Returns:
            Dictionary with velocity analysis including trends and confidence
        """
        try:
            # Check cache first
            if self._is_cache_valid('velocity'):
                return self._velocity_cache.get('velocity_analysis')
            
            logger.info("Analyzing velocity trends")
            
            # Get historical snapshots for velocity calculation
            snapshots = await self.historical_analyzer.get_dcp_snapshots(
                limit=self.velocity_window_days * 2  # Ensure enough data
            )
            
            if len(snapshots) < 3:
                logger.warning("Insufficient historical data for velocity analysis")
                return None
            
            # Calculate velocity metrics
            velocity_metrics = await self._calculate_velocity_metrics(snapshots)
            
            if not velocity_metrics:
                return None
            
            # Generate velocity analysis
            analysis = {
                'current_velocity': velocity_metrics.current_velocity,
                'average_velocity': velocity_metrics.average_velocity,
                'trend_direction': velocity_metrics.velocity_trend,
                'velocity_change_rate': velocity_metrics.velocity_change_rate,
                'confidence': velocity_metrics.confidence,
                'reasoning': self._generate_velocity_reasoning(velocity_metrics),
                'recommendations': self._generate_velocity_recommendations(velocity_metrics),
                'data_quality': {
                    'data_points': velocity_metrics.data_points,
                    'trend_strength': velocity_metrics.trend_strength,
                    'analysis_window_days': self.velocity_window_days
                }
            }
            
            # Cache results
            self._velocity_cache['velocity_analysis'] = analysis
            self._cache_timestamp = datetime.utcnow()
            
            logger.info(f"Velocity analysis completed: {velocity_metrics.current_velocity:.1f} obs/day, trend: {velocity_metrics.velocity_trend}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze velocity trends: {e}")
            return None
    
    async def _calculate_velocity_metrics(self, snapshots: List[Dict]) -> Optional[VelocityMetrics]:
        """Calculate velocity metrics from DCP snapshots"""
        try:
            if len(snapshots) < 2:
                return None
            
            # Sort snapshots by timestamp
            sorted_snapshots = sorted(snapshots, key=lambda x: x['created_at'])
            
            # Calculate daily velocities
            daily_velocities = []
            for i in range(1, len(sorted_snapshots)):
                prev_snapshot = sorted_snapshots[i-1]
                curr_snapshot = sorted_snapshots[i]
                
                # Calculate time difference
                prev_time = datetime.fromisoformat(prev_snapshot['created_at'].replace('Z', '+00:00'))
                curr_time = datetime.fromisoformat(curr_snapshot['created_at'].replace('Z', '+00:00'))
                time_diff_days = (curr_time - prev_time).total_seconds() / 86400
                
                if time_diff_days <= 0:
                    continue
                
                # Calculate observation changes (resolved observations)
                prev_obs_count = len(prev_snapshot.get('observations', []))
                curr_obs_count = len(curr_snapshot.get('observations', []))
                
                # Estimate resolved observations (simplified heuristic)
                # In practice, this would track observation lifecycle states
                resolved_count = max(0, prev_obs_count - curr_obs_count + 
                                   self._estimate_new_observations(prev_snapshot, curr_snapshot))
                
                velocity = resolved_count / time_diff_days
                daily_velocities.append(velocity)
            
            if not daily_velocities:
                return None
            
            # Calculate velocity statistics
            current_velocity = daily_velocities[-1] if daily_velocities else 0.0
            average_velocity = mean(daily_velocities)
            
            # Determine trend
            trend_direction, trend_strength = self._analyze_velocity_trend(daily_velocities)
            
            # Calculate velocity change rate
            if len(daily_velocities) >= 2:
                recent_avg = mean(daily_velocities[-3:]) if len(daily_velocities) >= 3 else daily_velocities[-1]
                older_avg = mean(daily_velocities[:-3]) if len(daily_velocities) >= 6 else average_velocity
                velocity_change_rate = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0.0
            else:
                velocity_change_rate = 0.0
            
            # Calculate confidence based on data quality
            confidence = self._calculate_velocity_confidence(daily_velocities, trend_strength)
            
            return VelocityMetrics(
                current_velocity=current_velocity,
                average_velocity=average_velocity,
                velocity_trend=trend_direction,
                velocity_change_rate=velocity_change_rate,
                confidence=confidence,
                trend_strength=trend_strength,
                data_points=len(daily_velocities)
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate velocity metrics: {e}")
            return None
    
    def _estimate_new_observations(self, prev_snapshot: Dict, curr_snapshot: Dict) -> int:
        """Estimate new observations added between snapshots"""
        try:
            # Simplified heuristic - in practice would track observation IDs
            # Estimate based on priority distribution changes
            prev_priorities = [obs.get('priority', 50) for obs in prev_snapshot.get('observations', [])]
            curr_priorities = [obs.get('priority', 50) for obs in curr_snapshot.get('observations', [])]
            
            # If new high-priority observations, estimate some were added
            high_priority_prev = len([p for p in prev_priorities if p >= 80])
            high_priority_curr = len([p for p in curr_priorities if p >= 80])
            
            return max(0, high_priority_curr - high_priority_prev)
            
        except Exception as e:
            logger.error(f"Failed to estimate new observations: {e}")
            return 0
    
    def _analyze_velocity_trend(self, velocities: List[float]) -> Tuple[str, float]:
        """Analyze velocity trend direction and strength"""
        try:
            if len(velocities) < 3:
                return 'stable', 0.0
            
            # Use linear regression to detect trend
            n = len(velocities)
            x_values = list(range(n))
            
            # Calculate slope
            x_mean = mean(x_values)
            y_mean = mean(velocities)
            
            numerator = sum((x_values[i] - x_mean) * (velocities[i] - y_mean) for i in range(n))
            denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
            
            if denominator == 0:
                return 'stable', 0.0
            
            slope = numerator / denominator
            
            # Calculate correlation coefficient for trend strength
            if len(velocities) > 1:
                velocity_std = stdev(velocities) if len(velocities) > 1 else 0.0
                if velocity_std > 0:
                    correlation = abs(slope * math.sqrt(denominator) / (velocity_std * math.sqrt(n)))
                    trend_strength = min(1.0, correlation)
                else:
                    trend_strength = 0.0
            else:
                trend_strength = 0.0
            
            # Determine trend direction based on slope and sensitivity
            threshold = self.trend_detection_sensitivity
            if slope > threshold:
                return 'increasing', trend_strength
            elif slope < -threshold:
                return 'decreasing', trend_strength
            else:
                return 'stable', trend_strength
                
        except Exception as e:
            logger.error(f"Failed to analyze velocity trend: {e}")
            return 'stable', 0.0
    
    def _calculate_velocity_confidence(self, velocities: List[float], trend_strength: float) -> float:
        """Calculate confidence in velocity analysis"""
        try:
            if not velocities:
                return 0.0
            
            # Base confidence on data quality factors
            data_points_factor = min(1.0, len(velocities) / 10)  # Improve with more data points
            
            # Consistency factor (lower variance = higher confidence)
            if len(velocities) > 1:
                velocity_std = stdev(velocities)
                velocity_mean = mean(velocities)
                consistency_factor = 1.0 - min(1.0, velocity_std / (velocity_mean + 0.1))
            else:
                consistency_factor = 0.5
            
            # Trend strength factor
            trend_factor = trend_strength
            
            # Combined confidence score
            confidence = (data_points_factor * 0.4 + consistency_factor * 0.4 + trend_factor * 0.2)
            
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            logger.error(f"Failed to calculate velocity confidence: {e}")
            return 0.0
    
    def _generate_velocity_reasoning(self, metrics: VelocityMetrics) -> str:
        """Generate human-readable reasoning for velocity analysis"""
        try:
            reasoning_parts = []
            
            # Current velocity context
            if metrics.current_velocity > metrics.average_velocity * 1.1:
                reasoning_parts.append(f"Current velocity ({metrics.current_velocity:.1f} obs/day) is above historical average ({metrics.average_velocity:.1f})")
            elif metrics.current_velocity < metrics.average_velocity * 0.9:
                reasoning_parts.append(f"Current velocity ({metrics.current_velocity:.1f} obs/day) is below historical average ({metrics.average_velocity:.1f})")
            else:
                reasoning_parts.append(f"Current velocity ({metrics.current_velocity:.1f} obs/day) is consistent with historical average")
            
            # Trend context
            if metrics.velocity_trend == 'increasing':
                reasoning_parts.append(f"Velocity trend is increasing by {abs(metrics.velocity_change_rate):.1f}%")
            elif metrics.velocity_trend == 'decreasing':
                reasoning_parts.append(f"Velocity trend is decreasing by {abs(metrics.velocity_change_rate):.1f}%")
            else:
                reasoning_parts.append("Velocity trend is stable with minimal variation")
            
            # Data quality context
            if metrics.data_points < 5:
                reasoning_parts.append("Analysis based on limited historical data")
            elif metrics.confidence < 0.6:
                reasoning_parts.append("Analysis confidence is moderate due to velocity variation")
            else:
                reasoning_parts.append("Analysis confidence is high based on consistent data")
            
            return ". ".join(reasoning_parts) + "."
            
        except Exception as e:
            logger.error(f"Failed to generate velocity reasoning: {e}")
            return "Velocity analysis completed with standard parameters."
    
    def _generate_velocity_recommendations(self, metrics: VelocityMetrics) -> List[str]:
        """Generate actionable recommendations based on velocity analysis"""
        try:
            recommendations = []
            
            # Velocity-specific recommendations
            if metrics.velocity_trend == 'decreasing' and metrics.velocity_change_rate < -10:
                recommendations.extend([
                    "Investigate potential blockers causing velocity decline",
                    "Consider increasing agent focus on high-priority observations",
                    "Review resource allocation and agent effectiveness"
                ])
            elif metrics.velocity_trend == 'increasing':
                recommendations.extend([
                    "Maintain current approach to sustain positive velocity trend",
                    "Consider scaling successful practices to other areas"
                ])
            
            # Low velocity recommendations
            if metrics.current_velocity < metrics.average_velocity * 0.7:
                recommendations.extend([
                    "Analyze observation complexity and resolution barriers",
                    "Consider breaking down high-priority observations into smaller tasks"
                ])
            
            # High velocity recommendations
            if metrics.current_velocity > metrics.average_velocity * 1.3:
                recommendations.extend([
                    "Monitor for quality vs. speed trade-offs",
                    "Ensure sustainable pace to prevent burnout"
                ])
            
            # Data quality recommendations
            if metrics.confidence < 0.6:
                recommendations.append("Collect more historical data to improve prediction accuracy")
            
            return recommendations if recommendations else ["Continue monitoring velocity trends"]
            
        except Exception as e:
            logger.error(f"Failed to generate velocity recommendations: {e}")
            return ["Monitor velocity trends and adjust as needed"]
    
    async def assess_milestone_risks(self, target_dates: Optional[List[datetime]] = None) -> List[Dict]:
        """
        Assess milestone completion risks based on current velocity
        
        Args:
            target_dates: Optional list of milestone dates to assess
            
        Returns:
            List of milestone risk assessments
        """
        try:
            logger.info("Assessing milestone risks")
            
            # Get current velocity analysis
            velocity_analysis = await self.analyze_velocity_trends()
            if not velocity_analysis:
                logger.warning("Cannot assess milestone risks without velocity data")
                return []
            
            current_velocity = velocity_analysis['current_velocity']
            
            # Use default milestone dates if none provided
            if not target_dates:
                target_dates = self._generate_default_milestone_dates()
            
            milestone_risks = []
            
            for target_date in target_dates:
                risk_assessment = await self._assess_single_milestone(
                    target_date, current_velocity, velocity_analysis
                )
                if risk_assessment:
                    milestone_risks.append(risk_assessment)
            
            logger.info(f"Assessed {len(milestone_risks)} milestone risks")
            return milestone_risks
            
        except Exception as e:
            logger.error(f"Failed to assess milestone risks: {e}")
            return []
    
    def _generate_default_milestone_dates(self) -> List[datetime]:
        """Generate default milestone dates for assessment"""
        try:
            now = datetime.utcnow()
            return [
                now + timedelta(days=7),   # 1 week
                now + timedelta(days=21),  # 3 weeks  
                now + timedelta(days=42),  # 6 weeks
            ]
        except Exception as e:
            logger.error(f"Failed to generate default milestone dates: {e}")
            return []
    
    async def _assess_single_milestone(self, target_date: datetime, 
                                     current_velocity: float, 
                                     velocity_analysis: Dict) -> Optional[Dict]:
        """Assess risk for a single milestone"""
        try:
            now = datetime.utcnow()
            days_remaining = (target_date - now).days
            
            if days_remaining <= 0:
                return None  # Milestone is in the past
            
            # Get current observation count (simplified estimation)
            snapshots = await self.historical_analyzer.get_dcp_snapshots(limit=1)
            if not snapshots:
                return None
            
            current_obs_count = len(snapshots[0].get('observations', []))
            
            # Estimate required velocity to complete all observations
            required_velocity = current_obs_count / days_remaining if days_remaining > 0 else float('inf')
            
            # Calculate completion probability
            velocity_ratio = current_velocity / required_velocity if required_velocity > 0 else 1.0
            
            # Apply confidence and trend adjustments
            confidence_adjustment = velocity_analysis['confidence']
            trend_adjustment = self._get_trend_adjustment(velocity_analysis['trend_direction'])
            
            completion_probability = min(1.0, velocity_ratio * confidence_adjustment * trend_adjustment)
            
            # Determine risk level
            risk_level = self._determine_risk_level(completion_probability)
            
            # Generate reasoning and recommendations
            reasoning = self._generate_milestone_reasoning(
                completion_probability, days_remaining, current_velocity, required_velocity
            )
            
            recommendations = self._generate_milestone_recommendations(
                completion_probability, risk_level, days_remaining
            )
            
            return {
                'target_date': target_date,
                'completion_probability': completion_probability,
                'days_remaining': days_remaining,
                'required_velocity': required_velocity,
                'current_velocity': current_velocity,
                'risk_level': risk_level,
                'confidence': velocity_analysis['confidence'],
                'reasoning': reasoning,
                'recommended_actions': recommendations
            }
            
        except Exception as e:
            logger.error(f"Failed to assess single milestone: {e}")
            return None
    
    def _get_trend_adjustment(self, trend_direction: str) -> float:
        """Get trend adjustment factor for milestone probability"""
        trend_adjustments = {
            'increasing': 1.1,
            'stable': 1.0,
            'decreasing': 0.9
        }
        return trend_adjustments.get(trend_direction, 1.0)
    
    def _determine_risk_level(self, completion_probability: float) -> str:
        """Determine risk level based on completion probability"""
        if completion_probability >= 0.8:
            return 'low'
        elif completion_probability >= 0.6:
            return 'medium'
        else:
            return 'high'
    
    def _generate_milestone_reasoning(self, probability: float, days_remaining: int,
                                    current_velocity: float, required_velocity: float) -> str:
        """Generate reasoning for milestone assessment"""
        try:
            reasoning_parts = []
            
            reasoning_parts.append(f"Based on current velocity of {current_velocity:.1f} observations/day")
            reasoning_parts.append(f"Required velocity is {required_velocity:.1f} observations/day for {days_remaining} days")
            
            if probability >= 0.8:
                reasoning_parts.append("Current pace is sufficient for milestone completion")
            elif probability >= 0.6:
                reasoning_parts.append("Current pace may meet milestone with focused effort")
            else:
                reasoning_parts.append("Current pace is insufficient for milestone completion")
            
            return ". ".join(reasoning_parts) + "."
            
        except Exception as e:
            logger.error(f"Failed to generate milestone reasoning: {e}")
            return "Milestone assessment based on current velocity trends."
    
    def _generate_milestone_recommendations(self, probability: float, 
                                          risk_level: str, days_remaining: int) -> List[str]:
        """Generate recommendations for milestone completion"""
        try:
            recommendations = []
            
            if risk_level == 'high':
                recommendations.extend([
                    "Prioritize critical observations for immediate resolution",
                    "Consider scope reduction or timeline extension",
                    "Increase agent focus and resource allocation"
                ])
            elif risk_level == 'medium':
                recommendations.extend([
                    "Monitor progress closely and adjust priorities",
                    "Focus on high-impact observations",
                    "Consider preventive measures for potential delays"
                ])
            else:  # low risk
                recommendations.extend([
                    "Maintain current pace and monitor for changes",
                    "Consider optimizing for quality over speed"
                ])
            
            if days_remaining <= 7:
                recommendations.append("Daily progress reviews recommended due to short timeline")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate milestone recommendations: {e}")
            return ["Monitor milestone progress and adjust as needed"]
    
    async def predict_bottlenecks(self, horizon_days: int = 21) -> List[Dict]:
        """
        Predict potential bottlenecks and capacity issues
        
        Args:
            horizon_days: Prediction horizon in days
            
        Returns:
            List of bottleneck predictions
        """
        try:
            logger.info(f"Predicting bottlenecks for {horizon_days} day horizon")
            
            # Get historical data for bottleneck analysis
            snapshots = await self.historical_analyzer.get_dcp_snapshots(limit=horizon_days)
            if len(snapshots) < 3:
                logger.warning("Insufficient data for bottleneck prediction")
                return []
            
            bottlenecks = []
            
            # Analyze priority inflation patterns
            priority_bottleneck = await self._analyze_priority_inflation(snapshots, horizon_days)
            if priority_bottleneck:
                bottlenecks.append(priority_bottleneck)
            
            # Analyze observation accumulation patterns
            accumulation_bottleneck = await self._analyze_observation_accumulation(snapshots, horizon_days)
            if accumulation_bottleneck:
                bottlenecks.append(accumulation_bottleneck)
            
            logger.info(f"Predicted {len(bottlenecks)} potential bottlenecks")
            return bottlenecks
            
        except Exception as e:
            logger.error(f"Failed to predict bottlenecks: {e}")
            return []
    
    async def _analyze_priority_inflation(self, snapshots: List[Dict], horizon_days: int) -> Optional[Dict]:
        """Analyze priority inflation patterns for bottleneck prediction"""
        try:
            # Calculate priority trends over time
            priority_trends = []
            
            for snapshot in snapshots:
                observations = snapshot.get('observations', [])
                if observations:
                    avg_priority = mean([obs.get('priority', 50) for obs in observations])
                    high_priority_count = len([obs for obs in observations if obs.get('priority', 50) >= 80])
                    priority_trends.append({
                        'timestamp': snapshot['created_at'],
                        'avg_priority': avg_priority,
                        'high_priority_count': high_priority_count
                    })
            
            if len(priority_trends) < 2:
                return None
            
            # Detect priority inflation trend
            recent_avg = mean([trend['avg_priority'] for trend in priority_trends[-3:]])
            older_avg = mean([trend['avg_priority'] for trend in priority_trends[:-3]]) if len(priority_trends) > 3 else recent_avg
            
            inflation_rate = (recent_avg - older_avg) / older_avg * 100 if older_avg > 0 else 0
            
            # Predict bottleneck if significant inflation detected
            if inflation_rate > self.config.priority_inflation_threshold:
                predicted_occurrence = datetime.utcnow() + timedelta(days=horizon_days // 2)
                
                return {
                    'bottleneck_type': 'priority_inflation',
                    'predicted_occurrence': predicted_occurrence,
                    'probability': min(0.9, inflation_rate / 20),  # Scale probability
                    'impact_severity': 'medium' if inflation_rate < 15 else 'high',
                    'affected_areas': ['task_prioritization', 'resource_allocation'],
                    'confidence': 0.7,
                    'reasoning': f"Priority inflation detected at {inflation_rate:.1f}% rate, indicating potential priority conflicts",
                    'preventive_actions': [
                        "Review and normalize observation priorities",
                        "Implement priority governance process",
                        "Focus on resolving high-priority observations"
                    ],
                    'early_warning_indicators': [
                        "Average priority exceeding historical norms",
                        "Increasing number of high-priority observations",
                        "Priority conflicts between observations"
                    ]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to analyze priority inflation: {e}")
            return None
    
    async def _analyze_observation_accumulation(self, snapshots: List[Dict], horizon_days: int) -> Optional[Dict]:
        """Analyze observation accumulation for bottleneck prediction"""
        try:
            # Calculate observation count trends
            obs_counts = []
            
            for snapshot in snapshots:
                observations = snapshot.get('observations', [])
                obs_counts.append({
                    'timestamp': snapshot['created_at'],
                    'total_count': len(observations),
                    'high_priority_count': len([obs for obs in observations if obs.get('priority', 50) >= 80])
                })
            
            if len(obs_counts) < 2:
                return None
            
            # Calculate accumulation rate
            recent_counts = [count['total_count'] for count in obs_counts[-3:]]
            older_counts = [count['total_count'] for count in obs_counts[:-3]] if len(obs_counts) > 3 else recent_counts
            
            recent_avg = mean(recent_counts)
            older_avg = mean(older_counts)
            
            accumulation_rate = (recent_avg - older_avg) / len(obs_counts) if len(obs_counts) > 0 else 0
            
            # Predict bottleneck if observations are accumulating faster than resolution
            if accumulation_rate > self.config.observation_accumulation_threshold:
                predicted_occurrence = datetime.utcnow() + timedelta(days=int(recent_avg / abs(accumulation_rate)))
                
                return {
                    'bottleneck_type': 'observation_accumulation',
                    'predicted_occurrence': predicted_occurrence,
                    'probability': min(0.8, accumulation_rate / 5),
                    'impact_severity': 'medium' if accumulation_rate < 3 else 'high',
                    'affected_areas': ['agent_capacity', 'observation_resolution'],
                    'confidence': 0.6,
                    'reasoning': f"Observations accumulating at {accumulation_rate:.1f} per period, exceeding resolution capacity",
                    'preventive_actions': [
                        "Increase agent scanning and resolution frequency",
                        "Focus on completing existing observations",
                        "Consider observation prioritization and filtering"
                    ],
                    'early_warning_indicators': [
                        "Increasing observation count over time",
                        "Slower observation resolution rates",
                        "Agent capacity utilization approaching limits"
                    ]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to analyze observation accumulation: {e}")
            return None
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache is valid for given key"""
        try:
            if not self._cache_timestamp:
                return False
            
            time_since_cache = datetime.utcnow() - self._cache_timestamp
            return time_since_cache.total_seconds() < (self._cache_ttl_minutes * 60)
            
        except Exception as e:
            logger.error(f"Failed to check cache validity: {e}")
            return False
    
    def clear_cache(self):
        """Clear prediction cache"""
        self._velocity_cache.clear()
        self._cache_timestamp = None
        logger.info("Timeline predictor cache cleared")
