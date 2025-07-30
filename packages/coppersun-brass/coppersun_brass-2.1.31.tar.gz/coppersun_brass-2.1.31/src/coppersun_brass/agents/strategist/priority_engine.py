# coppersun_brass/agents/strategist/priority_engine.py
"""
Priority scoring engine for Copper Alloy Brass observations
Implements algorithmic ranking based on impact, urgency, and context
"""

import math
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class PriorityEngine:
    """
    Calculates priority scores for observations using multiple weighted factors
    Score range: 0-100 (higher = more urgent/important)
    """
    
    # Type-based base scores
    TYPE_SCORES = {
        'security': 95,
        'critical_bug': 90,
        'performance': 75,
        'bug': 70,
        'todo_item': 60,
        'fixme_item': 65,
        'test_coverage': 55,
        'documentation': 40,
        'code_quality': 50,
        'implementation_gap': 65,
        'research_needed': 70,
        'optimization': 45,
        'file_change': 30,
        'unknown': 50
    }
    
    # Keyword impact multipliers
    URGENCY_KEYWORDS = {
        'critical': 1.3,
        'urgent': 1.2,
        'blocking': 1.25,
        'broken': 1.2,
        'failing': 1.15,
        'error': 1.1,
        'warning': 1.05,
        'todo': 1.0,
        'nice-to-have': 0.8,
        'optional': 0.7
    }
    
    # Location-based multipliers
    LOCATION_MULTIPLIERS = {
        'core': 1.2,
        'main': 1.15,
        'index': 1.1,
        'config': 1.05,
        'test': 0.9,
        'docs': 0.8,
        'example': 0.7
    }
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.decay_hours = self.config.get('time_decay_hours', 168)  # 1 week
        self.max_score = self.config.get('max_score', 100)
        self.min_score = self.config.get('min_score', 0)
        
        # Custom type scores from config
        self.type_scores = {**self.TYPE_SCORES, **self.config.get('type_scores', {})}
        
        logger.debug(f"Priority engine initialized with {len(self.type_scores)} type mappings")
    
    def calculate_priority(self, observation: Dict) -> int:
        """
        Calculate priority score for an observation
        
        Args:
            observation: Observation dictionary with type, summary, created_at, etc.
            
        Returns:
            Priority score (0-100, integer)
        """
        try:
            # Start with base type score
            obs_type = observation.get('type', 'unknown')
            base_score = self.type_scores.get(obs_type, self.TYPE_SCORES['unknown'])
            
            # Apply multipliers
            multipliers = self._calculate_multipliers(observation)
            final_score = base_score * multipliers['total']
            
            # Apply time decay
            time_factor = self._calculate_time_decay(observation)
            final_score *= time_factor
            
            # Clamp to valid range
            final_score = max(self.min_score, min(self.max_score, final_score))
            
            # Store calculation details for rationale
            observation['_priority_calculation'] = {
                'base_score': base_score,
                'multipliers': multipliers,
                'time_factor': time_factor,
                'final_score': final_score
            }
            
            return int(round(final_score))
            
        except Exception as e:
            logger.warning(f"Priority calculation failed for observation {observation.get('id', 'unknown')}: {e}")
            return 50  # Default middle priority
    
    def get_rationale(self, observation: Dict) -> str:
        """
        Generate human-readable rationale for priority score
        
        Args:
            observation: Observation with priority calculation details
            
        Returns:
            String explaining priority assignment
        """
        calc = observation.get('_priority_calculation', {})
        if not calc:
            return "Priority calculated using default scoring"
        
        parts = []
        
        # Base score explanation
        obs_type = observation.get('type', 'unknown')
        base_score = calc.get('base_score', 50)
        parts.append(f"Type '{obs_type}' base score: {base_score}")
        
        # Multiplier explanations
        multipliers = calc.get('multipliers', {})
        if multipliers.get('urgency', 1.0) != 1.0:
            parts.append(f"Urgency modifier: {multipliers['urgency']:.2f}")
        if multipliers.get('location', 1.0) != 1.0:
            parts.append(f"Location modifier: {multipliers['location']:.2f}")
        if multipliers.get('length', 1.0) != 1.0:
            parts.append(f"Content modifier: {multipliers['length']:.2f}")
        
        # Time factor
        time_factor = calc.get('time_factor', 1.0)
        if time_factor < 0.95:
            age_days = self._get_observation_age_days(observation)
            parts.append(f"Age decay ({age_days:.1f} days): {time_factor:.2f}")
        
        # Final score
        final_score = calc.get('final_score', 50)
        parts.append(f"Final: {final_score:.0f}")
        
        return " | ".join(parts)
    
    def _calculate_multipliers(self, observation: Dict) -> Dict[str, float]:
        """Calculate all priority multipliers"""
        urgency_mult = self._calculate_urgency_multiplier(observation)
        location_mult = self._calculate_location_multiplier(observation)
        length_mult = self._calculate_length_multiplier(observation)
        
        total_mult = urgency_mult * location_mult * length_mult
        
        return {
            'urgency': urgency_mult,
            'location': location_mult,
            'length': length_mult,
            'total': total_mult
        }
    
    def _calculate_urgency_multiplier(self, observation: Dict) -> float:
        """Calculate urgency multiplier based on keywords"""
        summary = observation.get('summary', '').lower()
        multiplier = 1.0
        
        for keyword, mult in self.URGENCY_KEYWORDS.items():
            if keyword in summary:
                multiplier = max(multiplier, mult)  # Use highest matching multiplier
        
        return multiplier
    
    def _calculate_location_multiplier(self, observation: Dict) -> float:
        """Calculate location-based multiplier"""
        summary = observation.get('summary', '').lower()
        multiplier = 1.0
        
        for location, mult in self.LOCATION_MULTIPLIERS.items():
            if location in summary:
                multiplier = max(multiplier, mult)
        
        return multiplier
    
    def _calculate_length_multiplier(self, observation: Dict) -> float:
        """Calculate multiplier based on summary length and detail"""
        summary = observation.get('summary', '')
        
        # Longer, more detailed summaries suggest more investigation
        length = len(summary)
        if length > 200:
            return 1.1
        elif length > 100:
            return 1.05
        elif length < 30:
            return 0.95
        
        return 1.0
    
    def _calculate_time_decay(self, observation: Dict) -> float:
        """
        Calculate time-based decay factor for aging observations
        
        Args:
            observation: Observation dict with 'created_at' timestamp
            
        Returns:
            Decay factor between 0.1 and 1.0 (newer = higher)
        """
        age_hours = self._get_observation_age_hours(observation)
        
        if age_hours <= 0:
            return 1.0
        
        # Exponential decay over configured time period
        decay_rate = math.log(0.5) / self.decay_hours  # Half-life = decay_hours
        decay_factor = math.exp(decay_rate * age_hours)
        
        # Don't decay below 0.1 (10% of original priority)
        return max(0.1, decay_factor)
    
    def _get_observation_age_hours(self, observation: Dict) -> float:
        """
        Get observation age in hours from created_at timestamp
        
        Args:
            observation: Observation dict with 'created_at' field
            
        Returns:
            Age in hours (0.0 if timestamp missing or invalid)
        """
        created_str = observation.get('created_at')
        if not created_str:
            return 0.0
        
        try:
            created_dt = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
            age = datetime.now(timezone.utc) - created_dt
            return age.total_seconds() / 3600
        except (ValueError, TypeError):
            return 0.0
    
    def _get_observation_age_days(self, observation: Dict) -> float:
        """Get observation age in days"""
        return self._get_observation_age_hours(observation) / 24
    
    def get_priority_distribution(self, observations: List[Dict]) -> Dict[str, int]:
        """
        Analyze priority distribution across observations
        
        Args:
            observations: List of observations
            
        Returns:
            Dict with priority range counts
        """
        ranges = {
            'critical': 0,    # 90-100
            'high': 0,        # 70-89
            'medium': 0,      # 40-69
            'low': 0          # 0-39
        }
        
        for obs in observations:
            priority = obs.get('calculated_priority', obs.get('priority', 50))
            
            if priority >= 90:
                ranges['critical'] += 1
            elif priority >= 70:
                ranges['high'] += 1
            elif priority >= 40:
                ranges['medium'] += 1
            else:
                ranges['low'] += 1
        
        return ranges
    
    def get_status(self) -> Dict[str, any]:
        """Get priority engine status"""
        return {
            'type_mappings': len(self.type_scores),
            'decay_hours': self.decay_hours,
            'score_range': f"{self.min_score}-{self.max_score}",
            'config': self.config
        }