"""
🚨 LEGACY FILE - NO LONGER USED 🚨

Real CodeBERT Integration - Actually uses CodeBERT for code understanding

⚠️ This file is LEGACY and no longer called by any active code paths.
🩸 Pure Python ML engine (pure_python_ml.py) is now used instead.
❌ This file contains heavy dependencies and should not be used.
"""
import os
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import json

logger = logging.getLogger(__name__)

# Check for required libraries
try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logger.error("transformers not installed! Install with: pip install transformers torch")

try:
    import onnxruntime as ort
    HAS_ONNX = True
except ImportError:
    HAS_ONNX = False


class CodeBERTClassifier:
    """Real CodeBERT implementation for code classification.
    
    This actually uses Microsoft's CodeBERT model for understanding code.
    """
    
    def __init__(self, model_dir: Path):
        """Initialize with real CodeBERT model."""
        self.model_dir = Path(model_dir)
        self.model = None
        self.tokenizer = None
        self.device = 'cpu'
        
        if HAS_TRANSFORMERS:
            self._load_codebert()
        else:
            logger.error("Cannot use CodeBERT without transformers library")
    
    def _load_codebert(self):
        """Load the actual CodeBERT model from HuggingFace."""
        try:
            logger.info("Loading real CodeBERT model...")
            
            # Use the actual CodeBERT model
            model_name = "microsoft/codebert-base"
            
            # Check if we have cached model
            cache_dir = self.model_dir / "codebert_cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=cache_dir
            )
            
            self.model = AutoModel.from_pretrained(
                model_name,
                cache_dir=cache_dir
            )
            
            # Set to eval mode
            self.model.eval()
            
            # Use GPU if available
            if torch.cuda.is_available():
                self.device = 'cuda'
                self.model = self.model.to(self.device)
                logger.info("Using GPU for CodeBERT")
            
            logger.info(f"✅ Loaded real CodeBERT model: {model_name}")
            
            # Load or create classification head
            self._load_classification_head()
            
        except Exception as e:
            logger.error(f"Failed to load CodeBERT: {e}")
            logger.info("Run: pip install transformers torch")
            self.model = None
    
    def _load_classification_head(self):
        """Load fine-tuned classification head for security detection."""
        classifier_path = self.model_dir / "codebert_classifier.pt"
        
        if classifier_path.exists():
            # Load fine-tuned classifier
            logger.info("Loading fine-tuned classifier...")
            checkpoint = torch.load(classifier_path, map_location=self.device)
            self.classifier = checkpoint['classifier']
        else:
            # Create simple classifier
            logger.info("Creating new classification head...")
            self.classifier = torch.nn.Sequential(
                torch.nn.Linear(768, 256),  # CodeBERT hidden size = 768
                torch.nn.ReLU(),
                torch.nn.Dropout(0.1),
                torch.nn.Linear(256, 3)  # 3 classes: critical, important, trivial
            )
            
            if self.device == 'cuda':
                self.classifier = self.classifier.to(self.device)
    
    def classify_code(self, code: str, file_path: str = "") -> Tuple[str, float, Dict]:
        """Classify code using real CodeBERT model.
        
        Returns:
            (category, confidence, features)
        """
        if not self.model or not self.tokenizer:
            return self._fallback_classify(code, file_path)
        
        try:
            # Tokenize code
            inputs = self.tokenizer(
                code,
                truncation=True,
                max_length=512,
                padding='max_length',
                return_tensors='pt'
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get CodeBERT embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state
                
                # Pool embeddings (mean pooling)
                attention_mask = inputs['attention_mask']
                mask_expanded = attention_mask.unsqueeze(-1).expand(embeddings.size()).float()
                sum_embeddings = torch.sum(embeddings * mask_expanded, 1)
                sum_mask = torch.clamp(mask_expanded.sum(1), min=1e-9)
                pooled = sum_embeddings / sum_mask
                
                # Classify
                logits = self.classifier(pooled)
                probs = torch.softmax(logits, dim=-1)
                
                # Get prediction
                pred_idx = torch.argmax(probs, dim=-1).item()
                confidence = probs[0][pred_idx].item()
            
            categories = ['trivial', 'important', 'critical']
            category = categories[pred_idx]
            
            # Extract features for explanation
            features = {
                'code_length': len(code),
                'has_password': 'password' in code.lower(),
                'has_eval': 'eval(' in code,
                'has_sql': any(sql in code.lower() for sql in ['select', 'insert', 'update', 'delete']),
                'confidence_scores': {
                    'trivial': probs[0][0].item(),
                    'important': probs[0][1].item(),
                    'critical': probs[0][2].item()
                }
            }
            
            return category, confidence, features
            
        except Exception as e:
            logger.error(f"CodeBERT classification failed: {e}")
            return self._fallback_classify(code, file_path)
    
    def _fallback_classify(self, code: str, file_path: str) -> Tuple[str, float, Dict]:
        """Fallback when CodeBERT not available."""
        # Use the pattern-based approach
        features = {'fallback': True}
        
        if any(risk in code.lower() for risk in ['password=', 'api_key=', 'secret=']):
            return 'critical', 0.9, features
        elif 'test' in file_path.lower():
            return 'trivial', 0.8, features
        else:
            return 'important', 0.6, features
    
    def export_to_onnx(self, output_path: Optional[Path] = None):
        """Export model to ONNX for production deployment."""
        if not self.model:
            logger.error("No model loaded to export")
            return
        
        output_path = output_path or self.model_dir / "codebert_security.onnx"
        
        logger.info(f"Exporting CodeBERT to ONNX: {output_path}")
        
        # Create dummy input
        dummy_input = self.tokenizer(
            "def example(): pass",
            return_tensors='pt',
            max_length=512,
            padding='max_length'
        )
        
        # Export to ONNX
        torch.onnx.export(
            self.model,
            (dummy_input['input_ids'], dummy_input['attention_mask']),
            output_path,
            export_params=True,
            opset_version=11,
            input_names=['input_ids', 'attention_mask'],
            output_names=['embeddings'],
            dynamic_axes={
                'input_ids': {0: 'batch_size'},
                'attention_mask': {0: 'batch_size'}
            }
        )
        
        logger.info(f"✅ Exported to {output_path}")
        
        # Quantize for smaller size
        if HAS_ONNX:
            self._quantize_onnx(output_path)
    
    def _quantize_onnx(self, model_path: Path):
        """Quantize ONNX model to INT8 for 4x size reduction."""
        try:
            from onnxruntime.quantization import quantize_dynamic, QuantType
            
            quantized_path = model_path.with_suffix('.quantized.onnx')
            
            quantize_dynamic(
                str(model_path),
                str(quantized_path),
                weight_type=QuantType.QInt8
            )
            
            # Check size reduction
            original_size = model_path.stat().st_size / (1024 * 1024)
            quantized_size = quantized_path.stat().st_size / (1024 * 1024)
            
            logger.info(f"✅ Quantized model: {original_size:.1f}MB → {quantized_size:.1f}MB")
            
        except Exception as e:
            logger.error(f"Quantization failed: {e}")


def download_and_setup_codebert():
    """Download and set up CodeBERT for Copper Alloy Brass."""
    logger.info("Setting up real CodeBERT integration...")
    
    model_dir = Path.home() / '.brass' / 'models'
    classifier = CodeBERTClassifier(model_dir)
    
    if classifier.model:
        # Test classification
        test_code = "password = 'admin123'"
        category, confidence, features = classifier.classify_code(test_code)
        logger.info(f"Test classification: {category} ({confidence:.2%})")
        
        # Export to ONNX
        classifier.export_to_onnx()
        
        return True
    
    return False


if __name__ == "__main__":
    success = download_and_setup_codebert()
    if success:
        print("✅ CodeBERT setup complete!")
    else:
        print("❌ CodeBERT setup failed - install dependencies")