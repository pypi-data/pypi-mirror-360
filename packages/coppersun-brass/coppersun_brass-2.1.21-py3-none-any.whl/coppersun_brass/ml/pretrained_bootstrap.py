"""
🚨 LEGACY FILE - NO LONGER USED 🚨

Pre-trained Model Bootstrap for Copper Alloy Brass

⚠️ This file is LEGACY and no longer called by any active code paths.
🩸 Pure Python ML engine (pure_python_ml.py) is now used instead.
❌ This file contains heavy dependencies and should not be used.

This module provides privacy-preserving initialization of Copper Alloy Brass
with pre-trained models and pattern databases.
"""

import logging
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
import urllib.request
import zipfile
import tarfile
from datetime import datetime

try:
    import torch
    import transformers
    from transformers import AutoModel, AutoTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers not available - limited pre-trained support")

try:
    import onnx
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

logger = logging.getLogger(__name__)


class PretrainedBootstrap:
    """
    Bootstrap Copper Alloy Brass with pre-trained models and patterns
    while maintaining privacy-first principles.
    """
    
    # Lightweight models suitable for local deployment
    RECOMMENDED_MODELS = {
        'codebert-small': {
            'name': 'microsoft/codebert-base',
            'size_mb': 420,
            'description': 'General code understanding',
            'cpu_friendly': True
        },
        'codet5-small': {
            'name': 'Salesforce/codet5-small',
            'size_mb': 220,
            'description': 'Code generation and analysis',
            'cpu_friendly': True
        },
        'unixcoder-base': {
            'name': 'microsoft/unixcoder-base',
            'size_mb': 500,
            'description': 'Multi-language code understanding',
            'cpu_friendly': True
        }
    }
    
    # Privacy-safe pattern databases
    PATTERN_DATABASES = {
        'sonarqube': {
            'url': 'https://rules.sonarsource.com/api/rules',
            'size_mb': 50,
            'description': '3000+ code quality rules',
            'privacy_safe': True
        },
        'cwe-patterns': {
            'url': 'https://cwe.mitre.org/data/xml/cwec_latest.xml.zip',
            'size_mb': 35,
            'description': 'Common weakness patterns',
            'privacy_safe': True
        },
        'design-patterns': {
            'url': 'https://github.com/kamranahmedse/design-patterns-for-humans',
            'size_mb': 10,
            'description': 'Common design patterns',
            'privacy_safe': True
        }
    }
    
    def __init__(self, model_dir: Path, cache_dir: Optional[Path] = None):
        """
        Initialize bootstrap system.
        
        Args:
            model_dir: Directory to store models
            cache_dir: Cache directory for downloads
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True, parents=True)
        
        self.cache_dir = cache_dir or (self.model_dir / 'cache')
        self.cache_dir.mkdir(exist_ok=True)
        
        self.pattern_db_path = self.model_dir / 'pattern_db.json'
        self.bootstrap_log_path = self.model_dir / 'bootstrap_log.json'
    
    def check_existing_bootstrap(self) -> Dict[str, Any]:
        """Check if bootstrap has already been performed."""
        if self.bootstrap_log_path.exists():
            with open(self.bootstrap_log_path, 'r') as f:
                return json.load(f)
        return {}
    
    def download_lightweight_model(self, model_key: str = 'codebert-small') -> bool:
        """
        Download a lightweight pre-trained model.
        
        Args:
            model_key: Key from RECOMMENDED_MODELS
            
        Returns:
            Success boolean
        """
        if not TRANSFORMERS_AVAILABLE:
            logger.error("Transformers library not available")
            return False
        
        if model_key not in self.RECOMMENDED_MODELS:
            logger.error(f"Unknown model: {model_key}")
            return False
        
        model_info = self.RECOMMENDED_MODELS[model_key]
        model_name = model_info['name']
        
        try:
            logger.info(f"Downloading {model_name} (~{model_info['size_mb']}MB)...")
            
            # Download model and tokenizer
            model = AutoModel.from_pretrained(
                model_name,
                cache_dir=self.cache_dir
            )
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=self.cache_dir
            )
            
            # Save to local directory
            local_model_path = self.model_dir / model_key
            local_model_path.mkdir(exist_ok=True)
            
            model.save_pretrained(local_model_path)
            tokenizer.save_pretrained(local_model_path)
            
            # Convert to ONNX if possible
            if ONNX_AVAILABLE:
                self._convert_to_onnx(model, tokenizer, local_model_path)
            
            logger.info(f"Successfully downloaded {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            return False
    
    def _convert_to_onnx(self, model, tokenizer, output_dir: Path) -> bool:
        """Convert model to ONNX format for faster inference."""
        try:
            # Create dummy input
            dummy_input = tokenizer(
                "def hello_world(): pass",
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=128
            )
            
            # Export to ONNX
            onnx_path = output_dir / 'model.onnx'
            torch.onnx.export(
                model,
                (dummy_input['input_ids'], dummy_input['attention_mask']),
                onnx_path,
                export_params=True,
                opset_version=13,
                do_constant_folding=True,
                input_names=['input_ids', 'attention_mask'],
                output_names=['output'],
                dynamic_axes={
                    'input_ids': {0: 'batch_size', 1: 'sequence'},
                    'attention_mask': {0: 'batch_size', 1: 'sequence'},
                    'output': {0: 'batch_size'}
                }
            )
            
            logger.info(f"Converted to ONNX: {onnx_path}")
            return True
            
        except Exception as e:
            logger.warning(f"ONNX conversion failed: {e}")
            return False
    
    def download_pattern_database(self, db_key: str) -> Dict[str, Any]:
        """
        Download privacy-safe pattern database.
        
        Args:
            db_key: Key from PATTERN_DATABASES
            
        Returns:
            Extracted patterns
        """
        if db_key not in self.PATTERN_DATABASES:
            logger.error(f"Unknown database: {db_key}")
            return {}
        
        db_info = self.PATTERN_DATABASES[db_key]
        
        # For this example, we'll create synthetic patterns
        # In production, this would download and parse real databases
        patterns = self._generate_synthetic_patterns(db_key)
        
        return patterns
    
    def _generate_synthetic_patterns(self, db_key: str) -> Dict[str, Any]:
        """Generate synthetic patterns for demonstration."""
        patterns = {
            'sonarqube': {
                'code_smells': [
                    {
                        'id': 'S1125',
                        'name': 'Boolean literals should not be redundant',
                        'severity': 'MINOR',
                        'pattern': 'if (condition == true)',
                        'fix': 'if (condition)',
                        'languages': ['java', 'javascript', 'python']
                    },
                    {
                        'id': 'S1172',
                        'name': 'Unused function parameters should be removed',
                        'severity': 'MAJOR',
                        'pattern': 'function foo(unused_param)',
                        'languages': ['javascript', 'typescript', 'python']
                    }
                ],
                'security': [
                    {
                        'id': 'S2068',
                        'name': 'Credentials should not be hard-coded',
                        'severity': 'CRITICAL',
                        'pattern': 'password = "hardcoded"',
                        'languages': ['all']
                    }
                ]
            },
            'cwe-patterns': {
                'weaknesses': [
                    {
                        'cwe_id': 'CWE-79',
                        'name': 'Cross-site Scripting',
                        'pattern_indicators': ['innerHTML', 'document.write', 'eval'],
                        'severity': 'HIGH'
                    },
                    {
                        'cwe_id': 'CWE-89',
                        'name': 'SQL Injection',
                        'pattern_indicators': ['string concatenation', 'dynamic query'],
                        'severity': 'CRITICAL'
                    }
                ]
            },
            'design-patterns': {
                'patterns': [
                    {
                        'name': 'Singleton',
                        'indicators': ['getInstance', 'private constructor', 'static instance'],
                        'category': 'creational'
                    },
                    {
                        'name': 'Observer',
                        'indicators': ['subscribe', 'notify', 'listeners'],
                        'category': 'behavioral'
                    }
                ]
            }
        }
        
        return patterns.get(db_key, {})
    
    def extract_privacy_safe_patterns(self, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract patterns in a privacy-preserving format.
        
        Never stores actual code, only abstract patterns.
        """
        safe_patterns = []
        
        for category, items in patterns.items():
            for item in items:
                if isinstance(item, dict):
                    # Extract only metadata, never actual code
                    safe_pattern = {
                        'category': category,
                        'pattern_id': item.get('id') or item.get('name'),
                        'severity': item.get('severity', 'MEDIUM'),
                        'languages': item.get('languages', ['all']),
                        'indicators': self._extract_indicators(item),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    safe_patterns.append(safe_pattern)
        
        return safe_patterns
    
    def _extract_indicators(self, pattern: Dict[str, Any]) -> List[str]:
        """Extract abstract indicators without code."""
        indicators = []
        
        # Look for various indicator fields
        for field in ['pattern_indicators', 'indicators', 'pattern']:
            if field in pattern:
                value = pattern[field]
                if isinstance(value, list):
                    indicators.extend(value)
                elif isinstance(value, str):
                    # Extract keywords, not code
                    keywords = [w for w in value.split() if len(w) > 3 and not w.startswith('"')]
                    indicators.extend(keywords)
        
        return list(set(indicators))  # Unique indicators only
    
    def generate_synthetic_training_data(self, num_samples: int = 1000) -> List[Dict[str, Any]]:
        """
        Generate synthetic training data based on patterns.
        
        This provides training examples without using real code.
        """
        import random
        
        training_data = []
        
        # Load existing patterns
        if self.pattern_db_path.exists():
            with open(self.pattern_db_path, 'r') as f:
                patterns = json.load(f)
        else:
            patterns = []
        
        # Generate synthetic examples
        for i in range(num_samples):
            pattern = random.choice(patterns) if patterns else {}
            
            example = {
                'id': f'synthetic_{i}',
                'features': {
                    'has_pattern': random.random() > 0.5,
                    'pattern_confidence': random.random(),
                    'code_complexity': random.randint(1, 10),
                    'line_count': random.randint(10, 500),
                    'language': random.choice(['python', 'javascript', 'java'])
                },
                'label': pattern.get('severity', random.choice(['LOW', 'MEDIUM', 'HIGH'])),
                'synthetic': True
            }
            
            training_data.append(example)
        
        return training_data
    
    def bootstrap(self, lightweight: bool = True) -> Dict[str, Any]:
        """
        Perform complete bootstrap process.
        
        Args:
            lightweight: Use only lightweight models
            
        Returns:
            Bootstrap results
        """
        logger.info("Starting Copper Alloy Brass bootstrap process...")
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'models_downloaded': [],
            'patterns_extracted': 0,
            'synthetic_data_generated': 0,
            'errors': []
        }
        
        # Check existing bootstrap
        existing = self.check_existing_bootstrap()
        if existing:
            logger.info(f"Found existing bootstrap from {existing.get('timestamp')}")
        
        # 1. Download lightweight models
        if lightweight:
            models_to_download = ['codebert-small']
        else:
            models_to_download = list(self.RECOMMENDED_MODELS.keys())
        
        for model_key in models_to_download:
            if self.download_lightweight_model(model_key):
                results['models_downloaded'].append(model_key)
            else:
                results['errors'].append(f"Failed to download {model_key}")
        
        # 2. Download pattern databases
        all_patterns = []
        for db_key in self.PATTERN_DATABASES:
            logger.info(f"Processing {db_key} patterns...")
            patterns = self.download_pattern_database(db_key)
            safe_patterns = self.extract_privacy_safe_patterns(patterns)
            all_patterns.extend(safe_patterns)
        
        # Save patterns
        if all_patterns:
            with open(self.pattern_db_path, 'w') as f:
                json.dump(all_patterns, f, indent=2)
            results['patterns_extracted'] = len(all_patterns)
            logger.info(f"Saved {len(all_patterns)} privacy-safe patterns")
        
        # 3. Generate synthetic training data
        synthetic_data = self.generate_synthetic_training_data(1000)
        synthetic_path = self.model_dir / 'synthetic_training.json'
        with open(synthetic_path, 'w') as f:
            json.dump(synthetic_data, f)
        results['synthetic_data_generated'] = len(synthetic_data)
        
        # 4. Create pattern index for fast lookup
        self._create_pattern_index(all_patterns)
        
        # Save bootstrap log
        with open(self.bootstrap_log_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Bootstrap complete: {len(results['models_downloaded'])} models, "
                   f"{results['patterns_extracted']} patterns")
        
        return results
    
    def _create_pattern_index(self, patterns: List[Dict[str, Any]]) -> None:
        """Create searchable index of patterns."""
        index = {
            'by_severity': {},
            'by_language': {},
            'by_category': {}
        }
        
        for pattern in patterns:
            # Index by severity
            severity = pattern.get('severity', 'UNKNOWN')
            if severity not in index['by_severity']:
                index['by_severity'][severity] = []
            index['by_severity'][severity].append(pattern['pattern_id'])
            
            # Index by language
            for lang in pattern.get('languages', ['all']):
                if lang not in index['by_language']:
                    index['by_language'][lang] = []
                index['by_language'][lang].append(pattern['pattern_id'])
            
            # Index by category
            category = pattern.get('category', 'general')
            if category not in index['by_category']:
                index['by_category'][category] = []
            index['by_category'][category].append(pattern['pattern_id'])
        
        # Save index
        index_path = self.model_dir / 'pattern_index.json'
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)
    
    def get_model_for_task(self, task: str) -> Optional[str]:
        """
        Get recommended pre-trained model for a specific task.
        
        Args:
            task: Task type (code_understanding, bug_detection, etc.)
            
        Returns:
            Model path if available
        """
        task_model_mapping = {
            'code_understanding': 'codebert-small',
            'code_generation': 'codet5-small',
            'multi_language': 'unixcoder-base'
        }
        
        model_key = task_model_mapping.get(task)
        if model_key:
            model_path = self.model_dir / model_key
            if model_path.exists():
                return str(model_path)
        
        return None


# Export main class
__all__ = ['PretrainedBootstrap']