"""
🚨 LEGACY FILE - NO LONGER USED 🚨

Model Trainer for Learning System

⚠️ This file is LEGACY and no longer called by any active code paths.
🩸 Pure Python ML engine (pure_python_ml.py) is now used instead.
❌ This file contains heavy dependencies and should not be used.

General Staff G7 Function: Training and Doctrine Development
Trains ML models based on collected feedback and outcomes
"""

import logging
import json
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
import hashlib
import shutil

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available - training will use fallback methods")

try:
    import onnx
    import onnxruntime as ort
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import FloatTensorType
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    logging.warning("ONNX not available - model export will be limited")

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, confusion_matrix
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn not available - using simple training")

from coppersun_brass.core.learning.models import (
    TaskOutcome, LearnedPattern, TaskStatus, init_db
)
from coppersun_brass.core.learning.pattern_extractor import PatternExtractor
from coppersun_brass.core.learning.privacy_manager import PrivacyManager
from coppersun_brass.core.context.dcp_manager import DCPManager
from coppersun_brass.config import BrassConfig
from .dcp_helpers import get_dcp_section, update_dcp_section

logger = logging.getLogger(__name__)


try:
    from torch.utils.data import Dataset
except ImportError:
    # Fallback for when torch is not available
    class Dataset:
        pass

class FeedbackDataset(Dataset):
    """PyTorch dataset for feedback data"""
    
    def __init__(self, features: np.ndarray, labels: np.ndarray):
        self.features = torch.FloatTensor(features)
        self.labels = torch.LongTensor(labels)
    
    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, idx):
        return self.features[idx], self.labels[idx]


class SimpleClassifier(nn.Module):
    """Simple neural network for classification"""
    
    def __init__(self, input_size: int, hidden_size: int = 64, num_classes: int = 5):
        super(SimpleClassifier, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.fc2 = nn.Linear(hidden_size, num_classes)
    
    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.fc2(out)
        return out


class ModelTrainer:
    """
    Trains ML models based on collected feedback and outcomes
    
    General Staff G7 Function: Training and Doctrine Development
    This component trains models that persist across sessions, enabling
    continuous improvement of Copper Alloy Brass's recommendations.
    """
    
    def __init__(
        self,
        dcp_path: Optional[str] = None,
        config: Optional[BrassConfig] = None,
        team_id: Optional[str] = None
    ):
        """
        Initialize model trainer with MANDATORY DCP integration
        
        Args:
            dcp_path: Path to DCP context file (mandatory per CLAUDE.md)
            config: Copper Alloy Brass configuration
            team_id: Team identifier for filtering
        """
        # DCP is MANDATORY - this is how the general staff coordinates
        self.dcp_manager = DCPManager(dcp_path)
        self.config = config or BrassConfig()
        self.team_id = team_id
        
        # Initialize components
        self.privacy_manager = PrivacyManager(dcp_path, team_id)
        self.pattern_extractor = PatternExtractor(dcp_path, team_id)
        self.engine, self.Session = init_db()
        
        # Training configuration
        self.min_samples_for_training = 50
        self.validation_split = 0.2
        self.max_epochs = 100
        self.early_stopping_patience = 10
        self.learning_rate = 0.001
        
        # Model paths
        self.model_dir = self.config.model_dir
        self.model_dir.mkdir(exist_ok=True, parents=True)
        
        # Load training history from DCP
        self._load_training_history_from_dcp()
    
    def check_training_readiness(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if we have enough data to train models
        
        Returns:
            Tuple of (ready_to_train, statistics)
        """
        session = self.Session()
        try:
            # Count outcomes
            total_outcomes = session.query(TaskOutcome).count()
            
            # Count outcomes with feedback
            feedback_outcomes = session.query(TaskOutcome).filter(
                TaskOutcome.user_feedback.isnot(None)
            ).count()
            
            # Count patterns
            pattern_count = session.query(LearnedPattern).count()
            
            # Get age of oldest outcome
            oldest_outcome = session.query(TaskOutcome).order_by(
                TaskOutcome.created_at
            ).first()
            
            if oldest_outcome:
                data_age_days = (datetime.utcnow() - oldest_outcome.created_at).days
            else:
                data_age_days = 0
            
            stats = {
                'total_outcomes': total_outcomes,
                'feedback_outcomes': feedback_outcomes,
                'pattern_count': pattern_count,
                'data_age_days': data_age_days,
                'ready_to_train': feedback_outcomes >= self.min_samples_for_training
            }
            
            logger.info(f"Training readiness check: {stats}")
            return stats['ready_to_train'], stats
            
        finally:
            session.close()
    
    def prepare_training_data(self) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Prepare data for model training
        
        Returns:
            Tuple of (features, labels, metadata)
        """
        session = self.Session()
        try:
            # Get outcomes with feedback
            outcomes = session.query(TaskOutcome).filter(
                TaskOutcome.user_feedback.isnot(None)
            ).all()
            
            features = []
            labels = []
            
            for outcome in outcomes:
                # Extract features from outcome
                feature_vec = self._extract_features(outcome)
                
                # Extract label from feedback
                label = self._extract_label(outcome)
                
                if feature_vec is not None and label is not None:
                    features.append(feature_vec)
                    labels.append(label)
            
            features = np.array(features)
            labels = np.array(labels)
            
            # Calculate class distribution
            unique_labels, counts = np.unique(labels, return_counts=True)
            class_distribution = dict(zip(unique_labels.tolist(), counts.tolist()))
            
            metadata = {
                'num_samples': len(labels),
                'num_features': features.shape[1] if len(features) > 0 else 0,
                'class_distribution': class_distribution,
                'feature_names': self._get_feature_names()
            }
            
            logger.info(f"Prepared {len(labels)} training samples with {metadata['num_features']} features")
            return features, labels, metadata
            
        finally:
            session.close()
    
    def _extract_features(self, outcome: TaskOutcome) -> Optional[np.ndarray]:
        """Extract feature vector from outcome"""
        features = []
        
        # Time-based features
        if outcome.time_taken and outcome.estimated_time:
            features.append(outcome.time_taken / outcome.estimated_time)  # Estimation accuracy
        else:
            features.append(1.0)
        
        # Status features
        features.append(1.0 if outcome.status == TaskStatus.COMPLETED else 0.0)
        features.append(1.0 if outcome.status == TaskStatus.FAILED else 0.0)
        
        # Context features (one-hot encoding)
        # Project type
        project_types = ['python', 'node', 'rust', 'unknown']
        for pt in project_types:
            features.append(1.0 if outcome.project_type == pt else 0.0)
        
        # Language
        languages = ['python', 'javascript', 'rust', 'unknown']
        for lang in languages:
            features.append(1.0 if outcome.language == lang else 0.0)
        
        # Codebase size (normalized)
        features.append(min(1.0, outcome.codebase_size / 10000) if outcome.codebase_size else 0.0)
        
        # Experiment variant
        features.append(1.0 if outcome.experiment_variant.value == 'test' else 0.0)
        
        return np.array(features)
    
    def _extract_label(self, outcome: TaskOutcome) -> Optional[int]:
        """Extract label from outcome feedback"""
        if not outcome.user_feedback:
            return None
        
        # Use rating as label (1-5) -> (0-4)
        rating = outcome.user_feedback.get('rating')
        if rating is not None:
            return max(0, min(4, rating - 1))
        
        # If no rating, infer from status
        if outcome.status == TaskStatus.COMPLETED:
            return 3  # Good (4/5)
        elif outcome.status == TaskStatus.FAILED:
            return 1  # Poor (2/5)
        else:
            return 2  # Neutral (3/5)
    
    def _get_feature_names(self) -> List[str]:
        """Get feature names for interpretability"""
        return [
            'estimation_accuracy',
            'is_completed',
            'is_failed',
            'project_python',
            'project_node',
            'project_rust',
            'project_unknown',
            'lang_python',
            'lang_javascript',
            'lang_rust',
            'lang_unknown',
            'codebase_size_norm',
            'is_test_variant'
        ]
    
    def train_models(self, force: bool = False) -> Dict[str, Any]:
        """
        Train ML models based on collected data
        
        Args:
            force: Force training even with limited data
            
        Returns:
            Training results dictionary
        """
        # Check readiness
        ready, stats = self.check_training_readiness()
        if not ready and not force:
            return {
                'success': False,
                'reason': 'Insufficient training data',
                'stats': stats
            }
        
        # Prepare data
        features, labels, data_metadata = self.prepare_training_data()
        
        if len(features) == 0:
            return {
                'success': False,
                'reason': 'No valid training samples found'
            }
        
        # Train models based on available libraries
        results = {
            'success': True,
            'models_trained': [],
            'data_metadata': data_metadata,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Try different training approaches
        if TORCH_AVAILABLE and len(features) >= 100:
            # Use PyTorch for larger datasets
            torch_results = self._train_pytorch_model(features, labels)
            results['models_trained'].append('pytorch')
            results['pytorch'] = torch_results
        
        if SKLEARN_AVAILABLE:
            # Use scikit-learn as fallback or primary
            sklearn_results = self._train_sklearn_model(features, labels)
            results['models_trained'].append('sklearn')
            results['sklearn'] = sklearn_results
        
        if not results['models_trained']:
            # Fallback to simple statistical model
            simple_results = self._train_simple_model(features, labels)
            results['models_trained'].append('simple')
            results['simple'] = simple_results
        
        # Extract patterns from outcomes
        patterns = self.pattern_extractor.extract_patterns()
        results['patterns_extracted'] = len(patterns)
        
        # Update DCP with training results
        self._persist_training_to_dcp(results)
        
        # Create model metadata
        self._create_model_metadata(results)
        
        logger.info(f"Training completed: {results['models_trained']}")
        return results
    
    def _train_pytorch_model(self, features: np.ndarray, labels: np.ndarray) -> Dict[str, Any]:
        """Train a PyTorch neural network model"""
        if not TORCH_AVAILABLE:
            return {'error': 'PyTorch not available'}
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            features, labels, test_size=self.validation_split, random_state=42
        )
        
        # Create datasets
        train_dataset = FeedbackDataset(X_train, y_train)
        val_dataset = FeedbackDataset(X_val, y_val)
        
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
        
        # Initialize model
        model = SimpleClassifier(
            input_size=features.shape[1],
            hidden_size=64,
            num_classes=5
        )
        
        # Loss and optimizer
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=self.learning_rate)
        
        # Training loop
        best_val_loss = float('inf')
        patience_counter = 0
        train_losses = []
        val_losses = []
        
        for epoch in range(self.max_epochs):
            # Training phase
            model.train()
            train_loss = 0.0
            for batch_features, batch_labels in train_loader:
                optimizer.zero_grad()
                outputs = model(batch_features)
                loss = criterion(outputs, batch_labels)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()
            
            # Validation phase
            model.eval()
            val_loss = 0.0
            correct = 0
            total = 0
            
            with torch.no_grad():
                for batch_features, batch_labels in val_loader:
                    outputs = model(batch_features)
                    loss = criterion(outputs, batch_labels)
                    val_loss += loss.item()
                    
                    _, predicted = torch.max(outputs.data, 1)
                    total += batch_labels.size(0)
                    correct += (predicted == batch_labels).sum().item()
            
            avg_train_loss = train_loss / len(train_loader)
            avg_val_loss = val_loss / len(val_loader)
            val_accuracy = correct / total
            
            train_losses.append(avg_train_loss)
            val_losses.append(avg_val_loss)
            
            # Early stopping
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                patience_counter = 0
                # Save best model
                torch.save(model.state_dict(), self.model_dir / 'pytorch_model.pth')
            else:
                patience_counter += 1
                if patience_counter >= self.early_stopping_patience:
                    logger.info(f"Early stopping at epoch {epoch}")
                    break
        
        # Export to ONNX if available
        if ONNX_AVAILABLE:
            model.eval()
            dummy_input = torch.randn(1, features.shape[1])
            torch.onnx.export(
                model, dummy_input,
                self.model_dir / 'classifier_pytorch.onnx',
                export_params=True,
                opset_version=13,
                do_constant_folding=True,
                input_names=['input'],
                output_names=['output'],
                dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
            )
        
        return {
            'final_val_loss': best_val_loss,
            'final_val_accuracy': val_accuracy,
            'epochs_trained': len(train_losses),
            'model_path': str(self.model_dir / 'pytorch_model.pth'),
            'onnx_exported': ONNX_AVAILABLE
        }
    
    def _train_sklearn_model(self, features: np.ndarray, labels: np.ndarray) -> Dict[str, Any]:
        """Train a scikit-learn model"""
        if not SKLEARN_AVAILABLE:
            return {'error': 'Scikit-learn not available'}
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            features, labels, test_size=self.validation_split, random_state=42
        )
        
        # Train Random Forest
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        train_score = model.score(X_train, y_train)
        val_score = model.score(X_val, y_val)
        
        # Get predictions for detailed metrics
        y_pred = model.predict(X_val)
        
        # Feature importance
        feature_importance = dict(zip(
            self._get_feature_names(),
            model.feature_importances_.tolist()
        ))
        
        # Save model
        import joblib
        model_path = self.model_dir / 'sklearn_model.joblib'
        joblib.dump(model, model_path)
        
        # Export to ONNX if available
        onnx_exported = False
        if ONNX_AVAILABLE:
            try:
                initial_type = [('float_input', FloatTensorType([None, features.shape[1]]))]
                onnx_model = convert_sklearn(model, initial_types=initial_type)
                
                onnx_path = self.model_dir / 'classifier_sklearn.onnx'
                with open(onnx_path, "wb") as f:
                    f.write(onnx_model.SerializeToString())
                onnx_exported = True
                
                # Update the main classifier.onnx that Copper Alloy Brass uses
                shutil.copy(onnx_path, self.model_dir / 'classifier.onnx')
                logger.info("Updated main classifier.onnx with new sklearn model")
            except Exception as e:
                logger.error(f"Failed to export sklearn model to ONNX: {e}")
        
        return {
            'train_accuracy': train_score,
            'val_accuracy': val_score,
            'feature_importance': feature_importance,
            'model_path': str(model_path),
            'onnx_exported': onnx_exported,
            'classification_report': classification_report(y_val, y_pred, output_dict=True)
        }
    
    def _train_simple_model(self, features: np.ndarray, labels: np.ndarray) -> Dict[str, Any]:
        """Train a simple statistical model as fallback"""
        # Calculate simple statistics for each feature and label combination
        stats = defaultdict(lambda: defaultdict(list))
        
        for feature_vec, label in zip(features, labels):
            for i, feature_val in enumerate(feature_vec):
                stats[label][i].append(feature_val)
        
        # Calculate means and stds
        model = {
            'type': 'simple_statistical',
            'label_stats': {}
        }
        
        for label, feature_stats in stats.items():
            model['label_stats'][int(label)] = {}
            for feature_idx, values in feature_stats.items():
                model['label_stats'][int(label)][int(feature_idx)] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values))
                }
        
        # Save model
        model_path = self.model_dir / 'simple_model.json'
        with open(model_path, 'w') as f:
            json.dump(model, f, indent=2)
        
        # Calculate simple accuracy (nearest neighbor approach)
        correct = 0
        for i, (feature_vec, true_label) in enumerate(zip(features, labels)):
            predicted_label = self._simple_predict(feature_vec, model)
            if predicted_label == true_label:
                correct += 1
        
        accuracy = correct / len(labels)
        
        return {
            'model_type': 'simple_statistical',
            'accuracy': accuracy,
            'model_path': str(model_path),
            'num_labels': len(model['label_stats'])
        }
    
    def _simple_predict(self, features: np.ndarray, model: Dict) -> int:
        """Make prediction with simple statistical model"""
        min_distance = float('inf')
        best_label = 2  # Default to neutral
        
        for label, feature_stats in model['label_stats'].items():
            distance = 0
            for i, feature_val in enumerate(features):
                if i in feature_stats:
                    mean = feature_stats[i]['mean']
                    std = feature_stats[i]['std'] + 1e-6  # Avoid division by zero
                    distance += abs(feature_val - mean) / std
            
            if distance < min_distance:
                min_distance = distance
                best_label = int(label)
        
        return best_label
    
    def update_models(self, backup: bool = True) -> Dict[str, Any]:
        """
        Update production models with newly trained ones
        
        Args:
            backup: Whether to backup existing models
            
        Returns:
            Update results
        """
        results = {
            'success': True,
            'models_updated': [],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Backup existing models if requested
        if backup:
            backup_dir = self.model_dir / f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            backup_dir.mkdir(exist_ok=True)
            
            for model_file in self.model_dir.glob('*.onnx'):
                shutil.copy(model_file, backup_dir / model_file.name)
            
            results['backup_dir'] = str(backup_dir)
        
        # Check for newly trained models
        updates = []
        
        # PyTorch model
        if (self.model_dir / 'classifier_pytorch.onnx').exists():
            updates.append({
                'source': 'classifier_pytorch.onnx',
                'target': 'classifier.onnx',
                'type': 'pytorch'
            })
        
        # Sklearn model
        if (self.model_dir / 'classifier_sklearn.onnx').exists():
            updates.append({
                'source': 'classifier_sklearn.onnx',
                'target': 'classifier.onnx',
                'type': 'sklearn'
            })
        
        # Apply updates
        for update in updates:
            source_path = self.model_dir / update['source']
            target_path = self.model_dir / update['target']
            
            try:
                shutil.copy(source_path, target_path)
                results['models_updated'].append(update['type'])
                logger.info(f"Updated {update['target']} with {update['type']} model")
            except Exception as e:
                logger.error(f"Failed to update model: {e}")
                results['success'] = False
                results['error'] = str(e)
        
        # Update model metadata
        self._update_model_metadata(results)
        
        # Notify DCP of model update
        self._notify_model_update_to_dcp(results)
        
        return results
    
    def _create_model_metadata(self, training_results: Dict[str, Any]) -> None:
        """Create metadata file for trained models"""
        metadata = {
            'version': datetime.utcnow().isoformat(),
            'team_id': self.team_id,
            'training_results': training_results,
            'model_files': {}
        }
        
        # List all model files
        for model_file in self.model_dir.glob('*'):
            if model_file.is_file():
                metadata['model_files'][model_file.name] = {
                    'size': model_file.stat().st_size,
                    'modified': datetime.fromtimestamp(model_file.stat().st_mtime).isoformat(),
                    'hash': self._calculate_file_hash(model_file)
                }
        
        # Save metadata
        metadata_path = self.model_dir / 'model_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _update_model_metadata(self, update_results: Dict[str, Any]) -> None:
        """Update model metadata after model update"""
        metadata_path = self.model_dir / 'model_metadata.json'
        
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {}
        
        metadata['last_update'] = update_results
        metadata['update_history'] = metadata.get('update_history', [])
        metadata['update_history'].append(update_results)
        
        # Keep only last 10 updates
        metadata['update_history'] = metadata['update_history'][-10:]
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def schedule_training(self, interval_hours: int = 24) -> Dict[str, Any]:
        """
        Schedule periodic model training
        
        Args:
            interval_hours: Hours between training runs
            
        Returns:
            Scheduling information
        """
        schedule_info = {
            'interval_hours': interval_hours,
            'next_training': datetime.utcnow() + timedelta(hours=interval_hours),
            'enabled': True
        }
        
        # Update DCP with schedule
        self.dcp_manager.update_section('learning.training_schedule', schedule_info)
        
        logger.info(f"Scheduled training every {interval_hours} hours")
        return schedule_info
    
    def _load_training_history_from_dcp(self) -> None:
        """Load training history from DCP"""
        try:
            learning_data = get_dcp_section(self.dcp_manager, 'learning', {})
            self.training_history = learning_data.get('training', {}).get('history', [])
            
            if self.training_history:
                logger.info(f"Loaded {len(self.training_history)} training records from DCP")
        except Exception as e:
            logger.warning(f"Could not load training history from DCP: {e}")
            self.training_history = []
    
    def _persist_training_to_dcp(self, results: Dict[str, Any]) -> None:
        """Persist training results to DCP"""
        # Add to history
        self.training_history.append(results)
        
        # Keep only recent history
        if len(self.training_history) > 20:
            self.training_history = self.training_history[-20:]
        
        # Update DCP
        self.dcp_manager.update_section('learning.training.history', self.training_history)
        
        # Add observation for significant training event
        self.dcp_manager.add_observation(
            'model_training_completed',
            {
                'models_trained': results.get('models_trained', []),
                'patterns_extracted': results.get('patterns_extracted', 0),
                'data_samples': results.get('data_metadata', {}).get('num_samples', 0),
                'team_id': self.team_id,
                'timestamp': results.get('timestamp')
            },
            source_agent='learning_system',
            priority=85  # High priority for training events
        )
        
        logger.info("Persisted training results to DCP")
    
    def _notify_model_update_to_dcp(self, results: Dict[str, Any]) -> None:
        """Notify DCP of model update"""
        self.dcp_manager.add_observation(
            'model_update_completed',
            {
                'models_updated': results.get('models_updated', []),
                'backup_created': 'backup_dir' in results,
                'success': results.get('success', False),
                'timestamp': results.get('timestamp')
            },
            source_agent='learning_system',
            priority=85  # High priority for model updates
        )

# Export main class
__all__ = ['ModelTrainer']