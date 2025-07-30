"""
Copper Alloy Brass Prediction Engine - Core orchestration hub for predictive intelligence
Implements async prediction coordination with confidence scoring and validation
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from ..meta_reasoning.historical_analyzer import HistoricalAnalyzer
from ....core.context.dcp_manager import DCPManager
# from ....core.event_bus import EventBus  # EventBus removed - using DCP coordination
from .prediction_config import PredictionConfig
from .timeline_predictor import TimelinePredictor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictionType(Enum):
    """Types of predictions supported by the engine"""
    TIMELINE = "timeline"
    RESOURCE = "resource" 
    RISK = "risk"
    PATTERN = "pattern"

class PredictionStatus(Enum):
    """Status of prediction lifecycle"""
    PENDING = "pending"
    GENERATED = "generated"
    VALIDATED = "validated"
    EXPIRED = "expired"

@dataclass
class Prediction:
    """Core prediction data structure with validation support"""
    id: str
    type: PredictionType
    prediction: str
    confidence: float  # 0.0 to 1.0
    reasoning: str
    recommended_actions: List[str]
    target_date: Optional[datetime] = None
    created_at: datetime = None
    status: PredictionStatus = PredictionStatus.PENDING
    validation_result: Optional[Dict] = None
    source_data: Optional[Dict] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if isinstance(self.type, str):
            self.type = PredictionType(self.type)
        if isinstance(self.status, str):
            self.status = PredictionStatus(self.status)
            
    def to_dict(self) -> Dict:
        """Convert prediction to dictionary for DCP storage"""
        data = asdict(self)
        data['type'] = self.type.value
        data['status'] = self.status.value
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.target_date:
            data['target_date'] = self.target_date.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Prediction':
        """Create prediction from dictionary"""
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        if 'target_date' in data and data['target_date'] and isinstance(data['target_date'], str):
            data['target_date'] = datetime.fromisoformat(data['target_date'].replace('Z', '+00:00'))
        return cls(**data)

class PredictionEngine:
    """
    Core prediction orchestration engine for Copper Alloy Brass Strategist Agent
    
    Coordinates multiple prediction modules with async processing,
    confidence scoring, and validation tracking. Integrates with
    existing DCP and event bus infrastructure.
    """
    
    def __init__(self, 
                 historical_analyzer: HistoricalAnalyzer,
                 dcp_manager: DCPManager, 
                 event_bus: Optional[Any] = None,  # EventBus phased out
                 config: Optional[PredictionConfig] = None):
        """
        Initialize prediction engine with required dependencies
        
        Args:
            historical_analyzer: For accessing historical trend data
            dcp_manager: For DCP storage and retrieval
            event_bus: For prediction event coordination (optional, being phased out)
            config: Prediction configuration (uses default if None)
        """
        self.historical_analyzer = historical_analyzer
        self.dcp_manager = dcp_manager
        self.event_bus = event_bus  # Optional - being phased out
        self.config = config or PredictionConfig()
        
        # Initialize prediction modules based on config
        self.timeline_predictor = None
        self.pattern_matcher = None
        self.resource_optimizer = None
        
        # Initialize prediction storage
        self._active_predictions: Dict[str, Prediction] = {}
        self._prediction_cache: Dict[str, Any] = {}
        self._last_prediction_cycle = None
        
        # Performance metrics
        self._cycle_count = 0
        self._total_predictions = 0
        self._validation_accuracy = {}
        
        logger.info("PredictionEngine initialized with configuration")
    
    async def initialize(self):
        """Initialize prediction modules based on configuration"""
        try:
            # Initialize timeline predictor (high priority per GPT review)
            if self.config.timeline_prediction_enabled:
                self.timeline_predictor = TimelinePredictor(
                    self.historical_analyzer,
                    self.config
                )
                logger.info("Timeline predictor initialized")
            
            # Pattern matcher and resource optimizer to be added in future sprints
            if self.config.pattern_matching_enabled:
                logger.info("Pattern matching will be available in future sprint")
                
            if self.config.resource_optimization_enabled:
                logger.info("Resource optimization will be available in future sprint")
                
            # Subscribe to relevant events
            await self._subscribe_to_events()
            
        except Exception as e:
            logger.error(f"Failed to initialize prediction engine: {e}")
            raise
    
    async def _subscribe_to_events(self):
        """Subscribe to event bus for prediction triggers"""
        try:
            # Subscribe to events if event bus available
            if self.event_bus:
                # Subscribe to DCP update events for prediction triggers
                await self.event_bus.subscribe(
                    'dcp.updated',
                    self._handle_dcp_update
                )
                
                # Subscribe to strategist orchestration events
                await self.event_bus.subscribe(
                    'strategist.orchestration_complete',
                    self._handle_orchestration_cycle
                )
            
            logger.info("Prediction engine subscribed to events")
            
        except Exception as e:
            logger.error(f"Failed to subscribe to events: {e}")
    
    async def _handle_dcp_update(self, event_data: Dict):
        """Handle DCP update events for prediction triggers"""
        try:
            # Check if significant changes warrant new predictions
            if self._should_trigger_predictions(event_data):
                await self.generate_predictions_async()
                
        except Exception as e:
            logger.error(f"Error handling DCP update for predictions: {e}")
    
    async def _handle_orchestration_cycle(self, event_data: Dict):
        """Handle strategist orchestration cycle completion"""
        try:
            self._cycle_count += 1
            
            # Generate predictions every N cycles (configurable)
            if self._cycle_count % self.config.prediction_frequency == 0:
                logger.info(f"Triggering prediction cycle at orchestration {self._cycle_count}")
                await self.generate_predictions_async()
                
        except Exception as e:
            logger.error(f"Error handling orchestration cycle for predictions: {e}")
    
    def _should_trigger_predictions(self, event_data: Dict) -> bool:
        """Determine if DCP changes warrant new predictions"""
        try:
            # Check if enough time has passed since last prediction
            if self._last_prediction_cycle:
                time_since_last = datetime.utcnow() - self._last_prediction_cycle
                if time_since_last < timedelta(minutes=self.config.min_prediction_interval_minutes):
                    return False
            
            # Check for significant observation changes
            change_data = event_data.get('changes', {})
            new_observations = change_data.get('new_observations', 0)
            priority_changes = change_data.get('priority_changes', 0)
            
            # Trigger if significant changes detected
            threshold = self.config.change_threshold_for_predictions
            return new_observations >= threshold or priority_changes >= threshold
            
        except Exception as e:
            logger.error(f"Error determining prediction trigger: {e}")
            return False
    
    async def generate_predictions_async(self) -> List[Prediction]:
        """
        Generate predictions asynchronously across all enabled modules
        
        Returns:
            List of generated predictions with confidence scores
        """
        try:
            logger.info("Starting async prediction generation cycle")
            self._last_prediction_cycle = datetime.utcnow()
            
            # Collect prediction tasks based on enabled modules
            prediction_tasks = []
            
            # Timeline predictions (high priority)
            if self.timeline_predictor and self.config.timeline_prediction_enabled:
                prediction_tasks.append(
                    self._generate_timeline_predictions()
                )
            
            # Future: Pattern and resource prediction tasks
            # These will be added in subsequent sprints
            
            # Execute all prediction tasks concurrently
            if not prediction_tasks:
                logger.warning("No prediction modules enabled")
                return []
            
            prediction_results = await asyncio.gather(
                *prediction_tasks,
                return_exceptions=True
            )
            
            # Collect successful predictions
            all_predictions = []
            for result in prediction_results:
                if isinstance(result, Exception):
                    logger.error(f"Prediction task failed: {result}")
                else:
                    all_predictions.extend(result)
            
            # Store predictions and emit events
            await self._store_predictions(all_predictions)
            await self._emit_prediction_events(all_predictions)
            
            self._total_predictions += len(all_predictions)
            logger.info(f"Generated {len(all_predictions)} predictions successfully")
            
            return all_predictions
            
        except Exception as e:
            logger.error(f"Failed to generate predictions: {e}")
            return []
    
    async def _generate_timeline_predictions(self) -> List[Prediction]:
        """Generate timeline-specific predictions"""
        try:
            if not self.timeline_predictor:
                return []
            
            predictions = []
            
            # Generate velocity analysis prediction
            velocity_analysis = await self.timeline_predictor.analyze_velocity_trends()
            if velocity_analysis:
                predictions.append(self._create_velocity_prediction(velocity_analysis))
            
            # Generate milestone risk predictions
            milestone_risks = await self.timeline_predictor.assess_milestone_risks()
            for risk in milestone_risks:
                predictions.append(self._create_milestone_prediction(risk))
            
            # Generate bottleneck predictions
            bottlenecks = await self.timeline_predictor.predict_bottlenecks()
            for bottleneck in bottlenecks:
                predictions.append(self._create_bottleneck_prediction(bottleneck))
            
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to generate timeline predictions: {e}")
            return []
    
    def _create_velocity_prediction(self, velocity_analysis: Dict) -> Prediction:
        """Create prediction from velocity analysis"""
        return Prediction(
            id=str(uuid.uuid4()),
            type=PredictionType.TIMELINE,
            prediction=f"Project velocity is {velocity_analysis['trend_direction']} at {velocity_analysis['current_velocity']:.1f} observations/day",
            confidence=velocity_analysis['confidence'],
            reasoning=velocity_analysis['reasoning'],
            recommended_actions=velocity_analysis['recommendations'],
            source_data=velocity_analysis
        )
    
    def _create_milestone_prediction(self, risk_data: Dict) -> Prediction:
        """Create prediction from milestone risk analysis"""
        return Prediction(
            id=str(uuid.uuid4()),
            type=PredictionType.TIMELINE,
            prediction=f"Milestone completion probability: {risk_data['completion_probability']:.0%}",
            confidence=risk_data['confidence'],
            reasoning=risk_data['reasoning'],
            recommended_actions=risk_data['recommended_actions'],
            target_date=risk_data.get('target_date'),
            source_data=risk_data
        )
    
    def _create_bottleneck_prediction(self, bottleneck_data: Dict) -> Prediction:
        """Create prediction from bottleneck analysis"""
        return Prediction(
            id=str(uuid.uuid4()),
            type=PredictionType.RISK,
            prediction=f"Potential bottleneck detected: {bottleneck_data['bottleneck_type']}",
            confidence=bottleneck_data['confidence'],
            reasoning=bottleneck_data['reasoning'],
            recommended_actions=bottleneck_data['preventive_actions'],
            target_date=bottleneck_data.get('predicted_occurrence'),
            source_data=bottleneck_data
        )
    
    async def _store_predictions(self, predictions: List[Prediction]):
        """Store predictions in DCP and active predictions cache"""
        try:
            if not predictions:
                return
            
            # Store in active predictions cache
            for prediction in predictions:
                self._active_predictions[prediction.id] = prediction
            
            # Update DCP with predictions
            await self._update_dcp_with_predictions(predictions)
            
            logger.info(f"Stored {len(predictions)} predictions")
            
        except Exception as e:
            logger.error(f"Failed to store predictions: {e}")
    
    async def _update_dcp_with_predictions(self, predictions: List[Prediction]):
        """Update DCP with new predictions"""
        try:
            # Get current DCP
            dcp_data = await self.dcp_manager.read_dcp()
            
            # Initialize predictive intelligence section if needed
            if 'predictive_intelligence' not in dcp_data:
                dcp_data['predictive_intelligence'] = {
                    'timeline_predictions': [],
                    'resource_predictions': [],
                    'risk_predictions': [],
                    'meta': {
                        'last_prediction_cycle': datetime.utcnow().isoformat(),
                        'total_predictions_generated': 0
                    }
                }
            
            # Add new predictions by type
            for prediction in predictions:
                prediction_dict = prediction.to_dict()
                
                if prediction.type == PredictionType.TIMELINE:
                    dcp_data['predictive_intelligence']['timeline_predictions'].append(prediction_dict)
                elif prediction.type == PredictionType.RISK:
                    dcp_data['predictive_intelligence']['risk_predictions'].append(prediction_dict)
                elif prediction.type == PredictionType.RESOURCE:
                    dcp_data['predictive_intelligence']['resource_predictions'].append(prediction_dict)
            
            # Update metadata
            dcp_data['predictive_intelligence']['meta']['last_prediction_cycle'] = datetime.utcnow().isoformat()
            dcp_data['predictive_intelligence']['meta']['total_predictions_generated'] = self._total_predictions
            
            # Prune old predictions to prevent DCP bloat
            await self._prune_old_predictions(dcp_data['predictive_intelligence'])
            
            # Save updated DCP
            await self.dcp_manager.update_dcp(dcp_data, source_agent="prediction_engine")
            
        except Exception as e:
            logger.error(f"Failed to update DCP with predictions: {e}")
    
    async def _prune_old_predictions(self, predictive_data: Dict):
        """Remove old predictions to prevent DCP bloat"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.config.prediction_retention_days)
            
            for prediction_type in ['timeline_predictions', 'resource_predictions', 'risk_predictions']:
                if prediction_type in predictive_data:
                    # Filter out old predictions
                    predictions = predictive_data[prediction_type]
                    filtered_predictions = []
                    
                    for pred in predictions:
                        created_at = datetime.fromisoformat(pred['created_at'].replace('Z', '+00:00'))
                        if created_at > cutoff_date:
                            filtered_predictions.append(pred)
                    
                    predictive_data[prediction_type] = filtered_predictions
                    
        except Exception as e:
            logger.error(f"Failed to prune old predictions: {e}")
    
    async def _emit_prediction_events(self, predictions: List[Prediction]):
        """Emit events for new predictions"""
        try:
            if self.event_bus:
                for prediction in predictions:
                    await self.event_bus.emit(
                        'strategist.prediction_generated',
                        {
                            'prediction_id': prediction.id,
                            'type': prediction.type.value,
                            'confidence': prediction.confidence,
                            'prediction': prediction.prediction
                        }
                    )
            
            # Emit summary event
            if self.event_bus:
                await self.event_bus.emit(
                    'strategist.prediction_cycle_complete',
                    {
                        'predictions_generated': len(predictions),
                        'cycle_timestamp': datetime.utcnow().isoformat(),
                        'cycle_count': self._cycle_count
                    }
                )
            
        except Exception as e:
            logger.error(f"Failed to emit prediction events: {e}")
    
    async def get_active_predictions(self, 
                                   prediction_type: Optional[PredictionType] = None,
                                   min_confidence: float = 0.0) -> List[Prediction]:
        """
        Get active predictions with optional filtering
        
        Args:
            prediction_type: Filter by prediction type
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of filtered predictions
        """
        try:
            predictions = list(self._active_predictions.values())
            
            # Apply filters
            if prediction_type:
                predictions = [p for p in predictions if p.type == prediction_type]
            
            if min_confidence > 0.0:
                predictions = [p for p in predictions if p.confidence >= min_confidence]
            
            # Sort by confidence descending
            predictions.sort(key=lambda p: p.confidence, reverse=True)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to get active predictions: {e}")
            return []
    
    async def validate_prediction(self, prediction_id: str, actual_outcome: Dict) -> bool:
        """
        Validate a prediction against actual outcome
        
        Args:
            prediction_id: ID of prediction to validate
            actual_outcome: Actual outcome data for validation
            
        Returns:
            True if validation successful, False otherwise
        """
        try:
            if prediction_id not in self._active_predictions:
                logger.warning(f"Prediction {prediction_id} not found for validation")
                return False
            
            prediction = self._active_predictions[prediction_id]
            
            # Perform validation logic (simplified for initial implementation)
            validation_result = {
                'actual_outcome': actual_outcome,
                'validated_at': datetime.utcnow().isoformat(),
                'accuracy_score': self._calculate_accuracy(prediction, actual_outcome)
            }
            
            # Update prediction with validation result
            prediction.validation_result = validation_result
            prediction.status = PredictionStatus.VALIDATED
            
            # Update accuracy metrics
            pred_type = prediction.type.value
            if pred_type not in self._validation_accuracy:
                self._validation_accuracy[pred_type] = []
            
            self._validation_accuracy[pred_type].append(validation_result['accuracy_score'])
            
            # Emit validation event
            if self.event_bus:
                await self.event_bus.emit(
                    'strategist.prediction_validated',
                    {
                        'prediction_id': prediction_id,
                        'accuracy_score': validation_result['accuracy_score'],
                        'prediction_type': pred_type
                    }
                )
            
            logger.info(f"Validated prediction {prediction_id} with accuracy {validation_result['accuracy_score']:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate prediction {prediction_id}: {e}")
            return False
    
    def _calculate_accuracy(self, prediction: Prediction, actual_outcome: Dict) -> float:
        """Calculate accuracy score for prediction validation"""
        try:
            # Simplified accuracy calculation for initial implementation
            # More sophisticated logic will be added based on prediction type
            
            if prediction.type == PredictionType.TIMELINE:
                # For timeline predictions, compare predicted vs actual completion
                predicted_success = prediction.confidence > 0.7
                actual_success = actual_outcome.get('milestone_met', False)
                return 1.0 if predicted_success == actual_success else 0.0
            
            # Default accuracy calculation
            return 0.5
            
        except Exception as e:
            logger.error(f"Failed to calculate accuracy: {e}")
            return 0.0
    
    def get_performance_metrics(self) -> Dict:
        """Get prediction engine performance metrics"""
        try:
            metrics = {
                'total_predictions_generated': self._total_predictions,
                'total_cycles': self._cycle_count,
                'active_predictions': len(self._active_predictions),
                'last_prediction_cycle': self._last_prediction_cycle.isoformat() if self._last_prediction_cycle else None,
                'accuracy_by_type': {}
            }
            
            # Calculate accuracy metrics by type
            for pred_type, scores in self._validation_accuracy.items():
                if scores:
                    metrics['accuracy_by_type'][pred_type] = {
                        'average_accuracy': sum(scores) / len(scores),
                        'sample_size': len(scores)
                    }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {}
    
    async def cleanup(self):
        """Cleanup prediction engine resources"""
        try:
            # Clear caches
            self._active_predictions.clear()
            self._prediction_cache.clear()
            
            # Unsubscribe from events
            if self.event_bus:
                await self.event_bus.unsubscribe('dcp.updated')
                await self.event_bus.unsubscribe('strategist.orchestration_complete')
            
            logger.info("Prediction engine cleanup completed")
            
        except Exception as e:
            logger.error(f"Failed to cleanup prediction engine: {e}")
