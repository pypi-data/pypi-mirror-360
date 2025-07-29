"""
🚨 LEGACY FILE - NO LONGER USED 🚨

Pre-trained Model Adapter for Copper Alloy Brass

⚠️ This file is LEGACY and no longer called by any active code paths.
🩸 Pure Python ML engine (pure_python_ml.py) is now used instead.
❌ This file contains heavy dependencies and should not be used.

Provides privacy-preserving integration with pre-trained models
to enhance Copper Alloy Brass's capabilities from day one.
"""

import logging
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib

try:
    import torch
    import torch.nn as nn
    from transformers import AutoModel, AutoTokenizer
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available - limited pre-trained support")

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

logger = logging.getLogger(__name__)


class PrivacyPreservingEncoder:
    """
    Encodes code into privacy-safe representations using pre-trained models.
    Never stores or outputs actual code.
    """
    
    def __init__(self, model_path: Path, max_length: int = 128):
        """
        Initialize encoder with pre-trained model.
        
        Args:
            model_path: Path to pre-trained model
            max_length: Maximum sequence length
        """
        self.model_path = Path(model_path)
        self.max_length = max_length
        self.model = None
        self.tokenizer = None
        self.onnx_session = None
        
        self._load_model()
    
    def _load_model(self) -> None:
        """Load model in order of preference: ONNX > PyTorch."""
        onnx_path = self.model_path / 'model.onnx'
        
        if ONNX_AVAILABLE and onnx_path.exists():
            # Prefer ONNX for faster inference
            self.onnx_session = ort.InferenceSession(str(onnx_path))
            logger.info(f"Loaded ONNX model from {onnx_path}")
        elif TORCH_AVAILABLE:
            # Fall back to PyTorch
            self.model = AutoModel.from_pretrained(self.model_path)
            self.model.eval()
            logger.info(f"Loaded PyTorch model from {self.model_path}")
        else:
            logger.warning("No suitable model runtime available")
        
        # Load tokenizer
        if TORCH_AVAILABLE:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
    
    def encode_to_privacy_safe_features(self, code_snippet: str) -> Dict[str, Any]:
        """
        Encode code into privacy-preserving features.
        
        Returns statistical features, never the actual code.
        """
        if not self.tokenizer:
            return self._fallback_features(code_snippet)
        
        # Tokenize
        inputs = self.tokenizer(
            code_snippet,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt' if TORCH_AVAILABLE else None
        )
        
        # Get embeddings
        if self.onnx_session:
            embeddings = self._run_onnx_inference(inputs)
        elif self.model:
            embeddings = self._run_torch_inference(inputs)
        else:
            embeddings = None
        
        # Extract privacy-safe features
        features = {
            'embedding_stats': self._compute_embedding_stats(embeddings),
            'token_stats': self._compute_token_stats(inputs),
            'structural_features': self._extract_structural_features(code_snippet),
            'pattern_hash': self._compute_pattern_hash(code_snippet)
        }
        
        return features
    
    def _run_onnx_inference(self, inputs: Dict[str, Any]) -> np.ndarray:
        """Run ONNX inference."""
        ort_inputs = {
            'input_ids': inputs['input_ids'].numpy(),
            'attention_mask': inputs['attention_mask'].numpy()
        }
        outputs = self.onnx_session.run(None, ort_inputs)
        return outputs[0]
    
    def _run_torch_inference(self, inputs: Dict[str, Any]) -> np.ndarray:
        """Run PyTorch inference."""
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use pooler output or mean of last hidden states
            if hasattr(outputs, 'pooler_output'):
                embeddings = outputs.pooler_output
            else:
                embeddings = outputs.last_hidden_state.mean(dim=1)
            return embeddings.numpy()
    
    def _compute_embedding_stats(self, embeddings: Optional[np.ndarray]) -> Dict[str, float]:
        """Compute statistical features from embeddings."""
        if embeddings is None:
            return {}
        
        return {
            'mean': float(np.mean(embeddings)),
            'std': float(np.std(embeddings)),
            'norm': float(np.linalg.norm(embeddings)),
            'max': float(np.max(embeddings)),
            'min': float(np.min(embeddings))
        }
    
    def _compute_token_stats(self, inputs: Dict[str, Any]) -> Dict[str, int]:
        """Compute token-level statistics."""
        if 'input_ids' not in inputs:
            return {}
        
        token_ids = inputs['input_ids'].flatten()
        unique_tokens = len(set(token_ids.tolist()))
        
        return {
            'num_tokens': len(token_ids),
            'unique_tokens': unique_tokens,
            'token_diversity': unique_tokens / len(token_ids) if len(token_ids) > 0 else 0
        }
    
    def _extract_structural_features(self, code: str) -> Dict[str, int]:
        """Extract structural features without storing code."""
        lines = code.split('\n')
        
        return {
            'num_lines': len(lines),
            'max_line_length': max(len(line) for line in lines) if lines else 0,
            'avg_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0,
            'num_functions': code.count('def ') + code.count('function '),
            'num_classes': code.count('class '),
            'complexity_estimate': self._estimate_complexity(code)
        }
    
    def _estimate_complexity(self, code: str) -> int:
        """Estimate cyclomatic complexity without parsing."""
        # Simple heuristic based on control flow keywords
        complexity = 1
        control_flow = ['if ', 'elif ', 'else:', 'for ', 'while ', 'except:', 'case ']
        
        for keyword in control_flow:
            complexity += code.count(keyword)
        
        return complexity
    
    def _compute_pattern_hash(self, code: str) -> str:
        """Compute hash of structural pattern, not content."""
        # Extract pattern without literals
        pattern_elements = []
        
        # Simple pattern extraction (would be more sophisticated in production)
        tokens = code.split()
        for token in tokens:
            if token in ['def', 'class', 'if', 'for', 'while', 'return', 'import']:
                pattern_elements.append(token)
            elif token.startswith(('(', ')', '{', '}', '[', ']')):
                pattern_elements.append('BRACKET')
        
        pattern_str = ' '.join(pattern_elements)
        return hashlib.md5(pattern_str.encode()).hexdigest()[:16]
    
    def _fallback_features(self, code: str) -> Dict[str, Any]:
        """Fallback feature extraction without models."""
        return {
            'structural_features': self._extract_structural_features(code),
            'pattern_hash': self._compute_pattern_hash(code)
        }


class PretrainedPatternMatcher:
    """
    Matches code against pre-trained patterns in a privacy-preserving way.
    """
    
    def __init__(self, pattern_db_path: Path):
        """
        Initialize pattern matcher.
        
        Args:
            pattern_db_path: Path to pattern database
        """
        self.pattern_db_path = Path(pattern_db_path)
        self.patterns = self._load_patterns()
        self.pattern_index = self._load_pattern_index()
    
    def _load_patterns(self) -> List[Dict[str, Any]]:
        """Load pattern database."""
        if self.pattern_db_path.exists():
            with open(self.pattern_db_path, 'r') as f:
                return json.load(f)
        return []
    
    def _load_pattern_index(self) -> Dict[str, Any]:
        """Load pattern index for fast lookup."""
        index_path = self.pattern_db_path.parent / 'pattern_index.json'
        if index_path.exists():
            with open(index_path, 'r') as f:
                return json.load(f)
        return {}
    
    def match_patterns(self, features: Dict[str, Any], language: str = 'python') -> List[Dict[str, Any]]:
        """
        Match features against known patterns.
        
        Returns matches with confidence scores.
        """
        matches = []
        
        # Get relevant patterns for language
        language_patterns = self.pattern_index.get('by_language', {}).get(language, [])
        all_patterns = self.pattern_index.get('by_language', {}).get('all', [])
        
        relevant_pattern_ids = set(language_patterns + all_patterns)
        
        for pattern in self.patterns:
            if pattern['pattern_id'] not in relevant_pattern_ids:
                continue
            
            # Calculate match confidence
            confidence = self._calculate_match_confidence(features, pattern)
            
            if confidence > 0.5:  # Threshold
                matches.append({
                    'pattern_id': pattern['pattern_id'],
                    'category': pattern['category'],
                    'severity': pattern['severity'],
                    'confidence': confidence,
                    'indicators': pattern.get('indicators', [])
                })
        
        # Sort by confidence
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        
        return matches[:10]  # Top 10 matches
    
    def _calculate_match_confidence(self, features: Dict[str, Any], pattern: Dict[str, Any]) -> float:
        """Calculate confidence score for pattern match."""
        confidence = 0.0
        weights = {
            'complexity_match': 0.3,
            'structural_match': 0.3,
            'indicator_match': 0.4
        }
        
        # Complexity matching
        if 'structural_features' in features:
            complexity = features['structural_features'].get('complexity_estimate', 0)
            # Simple heuristic: higher complexity for security patterns
            if pattern['category'] == 'security' and complexity > 5:
                confidence += weights['complexity_match']
            elif pattern['category'] == 'code_smells' and complexity < 3:
                confidence += weights['complexity_match']
        
        # Structural matching (simplified)
        if pattern.get('indicators'):
            # In production, this would be more sophisticated
            confidence += weights['indicator_match'] * 0.7
        
        return min(confidence, 1.0)


class PretrainedKnowledgeAdapter:
    """
    Adapts pre-trained knowledge to Copper Alloy Brass's learning system.
    """
    
    def __init__(self, model_dir: Path):
        """
        Initialize knowledge adapter.
        
        Args:
            model_dir: Directory containing models and patterns
        """
        self.model_dir = Path(model_dir)
        self.encoder = None
        self.pattern_matcher = None
        
        self._initialize_components()
    
    def _initialize_components(self) -> None:
        """Initialize encoder and pattern matcher."""
        # Find available model
        for model_key in ['codebert-small', 'codet5-small', 'unixcoder-base']:
            model_path = self.model_dir / model_key
            if model_path.exists():
                self.encoder = PrivacyPreservingEncoder(model_path)
                logger.info(f"Initialized encoder with {model_key}")
                break
        
        # Initialize pattern matcher
        pattern_db_path = self.model_dir / 'pattern_db.json'
        if pattern_db_path.exists():
            self.pattern_matcher = PretrainedPatternMatcher(pattern_db_path)
            logger.info("Initialized pattern matcher")
    
    def analyze_code_privacy_safe(self, code_snippet: str, language: str = 'python') -> Dict[str, Any]:
        """
        Analyze code using pre-trained knowledge.
        
        Returns only privacy-safe insights, never the code itself.
        """
        analysis = {
            'timestamp': datetime.utcnow().isoformat(),
            'language': language,
            'insights': {}
        }
        
        # Extract features
        if self.encoder:
            features = self.encoder.encode_to_privacy_safe_features(code_snippet)
            analysis['features'] = features
            
            # Match patterns
            if self.pattern_matcher:
                matches = self.pattern_matcher.match_patterns(features, language)
                analysis['pattern_matches'] = matches
                
                # Aggregate insights
                if matches:
                    analysis['insights'] = {
                        'quality_score': self._calculate_quality_score(matches),
                        'top_issues': self._get_top_issues(matches),
                        'recommendations': self._generate_recommendations(matches)
                    }
        
        return analysis
    
    def _calculate_quality_score(self, matches: List[Dict[str, Any]]) -> float:
        """Calculate overall code quality score."""
        if not matches:
            return 1.0
        
        # Weight by severity
        severity_weights = {
            'CRITICAL': 1.0,
            'HIGH': 0.7,
            'MAJOR': 0.7,
            'MEDIUM': 0.4,
            'MINOR': 0.2,
            'LOW': 0.1
        }
        
        total_penalty = 0.0
        for match in matches:
            severity = match.get('severity', 'MEDIUM')
            confidence = match.get('confidence', 0.5)
            weight = severity_weights.get(severity, 0.3)
            
            total_penalty += weight * confidence
        
        # Convert to 0-1 score
        score = max(0.0, 1.0 - (total_penalty / 10.0))
        
        return score
    
    def _get_top_issues(self, matches: List[Dict[str, Any]]) -> List[str]:
        """Get top issues from matches."""
        issues = []
        
        for match in matches[:5]:  # Top 5
            issue = f"{match['category']}: Pattern {match['pattern_id']} " \
                   f"(severity: {match['severity']}, confidence: {match['confidence']:.2f})"
            issues.append(issue)
        
        return issues
    
    def _generate_recommendations(self, matches: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Category-based recommendations
        categories = set(match['category'] for match in matches)
        
        if 'security' in categories:
            recommendations.append("Review security patterns and validate input handling")
        
        if 'code_smells' in categories:
            recommendations.append("Consider refactoring to improve code maintainability")
        
        if 'performance' in categories:
            recommendations.append("Profile code to identify performance bottlenecks")
        
        return recommendations[:3]  # Top 3 recommendations
    
    def get_bootstrap_status(self) -> Dict[str, Any]:
        """Get status of pre-trained components."""
        status = {
            'encoder_available': self.encoder is not None,
            'pattern_matcher_available': self.pattern_matcher is not None,
            'pattern_count': len(self.pattern_matcher.patterns) if self.pattern_matcher else 0,
            'models_available': []
        }
        
        # Check available models
        for model_key in ['codebert-small', 'codet5-small', 'unixcoder-base']:
            if (self.model_dir / model_key).exists():
                status['models_available'].append(model_key)
        
        return status


# Export main classes
__all__ = ['PrivacyPreservingEncoder', 'PretrainedPatternMatcher', 'PretrainedKnowledgeAdapter']