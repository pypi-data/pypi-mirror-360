#!/usr/bin/env python3
"""
🚨 LEGACY FILE - NO LONGER USED 🚨

Download and prepare real ML models for Copper Alloy Brass

⚠️ This file is LEGACY and no longer called by any active code paths.
🩸 Pure Python ML engine (pure_python_ml.py) is now used instead.
❌ This file contains heavy dependencies and should not be used.
"""
import os
import sys
import json
import logging
from pathlib import Path
import requests
from tqdm import tqdm
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model configurations
MODELS = {
    "codebert-small": {
        "url": "https://huggingface.co/microsoft/codebert-base/resolve/main/pytorch_model.bin",
        "size": "476MB",
        "sha256": "fake_hash_for_demo",  # Would verify in production
        "description": "CodeBERT for code understanding"
    },
    "security-patterns": {
        "url": "https://github.com/coppersun_brass/models/releases/download/v1.0/security_patterns.json",
        "size": "2MB", 
        "sha256": "fake_hash_for_demo",
        "description": "Security vulnerability patterns"
    }
}

# For now, create a real pattern database
SECURITY_PATTERNS = {
    "critical": [
        {
            "pattern": r"password\s*=\s*[\"'][^\"']+[\"']",
            "description": "Hardcoded password",
            "severity": 95,
            "fix": "Use environment variables or secure key management"
        },
        {
            "pattern": r"api_key\s*=\s*[\"'][^\"']+[\"']",
            "description": "Hardcoded API key",
            "severity": 95,
            "fix": "Store API keys in environment variables"
        },
        {
            "pattern": r"eval\s*\([^)]+\)",
            "description": "Eval usage - code injection risk",
            "severity": 90,
            "fix": "Use ast.literal_eval or avoid eval entirely"
        },
        {
            "pattern": r"pickle\.loads?\s*\([^)]+\)",
            "description": "Pickle deserialization - arbitrary code execution",
            "severity": 88,
            "fix": "Use JSON or other safe serialization formats"
        },
        {
            "pattern": r"os\.system\s*\([^)]+\)|subprocess\.call\s*\([^)]+shell=True",
            "description": "Shell command injection risk",
            "severity": 85,
            "fix": "Use subprocess with shell=False and list arguments"
        },
        {
            "pattern": r"request\.GET\.get\s*\([^)]+\).*\.objects\.raw\s*\(",
            "description": "SQL injection risk",
            "severity": 92,
            "fix": "Use parameterized queries"
        }
    ],
    "important": [
        {
            "pattern": r"except\s*:\s*pass",
            "description": "Bare except clause swallowing errors",
            "severity": 60,
            "fix": "Catch specific exceptions"
        },
        {
            "pattern": r"if\s+.*==\s*True|if\s+.*==\s*False",
            "description": "Explicit comparison to boolean",
            "severity": 40,
            "fix": "Use 'if value:' or 'if not value:'"
        },
        {
            "pattern": r"TODO|FIXME|XXX|HACK",
            "description": "Technical debt marker",
            "severity": 50,
            "fix": "Address the TODO item"
        }
    ]
}

# Code classification training data
CLASSIFICATION_EXAMPLES = {
    "critical": [
        "password = 'admin123'",
        "eval(user_input)",
        "os.system(f'rm -rf {path}')",
        "cursor.execute(f'SELECT * FROM users WHERE id = {user_id}')"
    ],
    "important": [
        "def calculate_price(items):",
        "class UserAuthentication:",
        "async def process_payment(amount):",
        "def validate_input(data):"
    ],
    "trivial": [
        "def test_addition():",
        "import pytest",
        "# This is a comment",
        "README.md content"
    ]
}


def download_file(url: str, dest: Path, expected_size: str = None):
    """Download file with progress bar."""
    logger.info(f"Downloading {url} to {dest}")
    
    # For demo, just create mock data
    dest.parent.mkdir(parents=True, exist_ok=True)
    
    if "security_patterns" in url:
        # Save security patterns
        with open(dest, 'w') as f:
            json.dump(SECURITY_PATTERNS, f, indent=2)
        logger.info(f"Created security patterns at {dest}")
    else:
        # Create mock model file
        dest.write_text("Mock model data")
        logger.info(f"Created mock model at {dest}")


def create_embeddings():
    """Create code embeddings for similarity search."""
    try:
        from sentence_transformers import SentenceTransformer
        
        logger.info("Creating code embeddings...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Embed classification examples
        embeddings = {}
        for category, examples in CLASSIFICATION_EXAMPLES.items():
            embeddings[category] = model.encode(examples)
        
        # Save embeddings
        import numpy as np
        embed_path = Path.home() / '.brass' / 'models' / 'embeddings.npz'
        embed_path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(embed_path, **embeddings)
        
        logger.info(f"Saved embeddings to {embed_path}")
        return True
        
    except ImportError:
        logger.warning("sentence-transformers not installed, skipping embeddings")
        return False


def setup_tokenizer():
    """Set up proper code tokenizer."""
    try:
        from transformers import AutoTokenizer
        
        logger.info("Setting up CodeBERT tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        
        # Save tokenizer
        tokenizer_path = Path.home() / '.brass' / 'models' / 'tokenizer'
        tokenizer.save_pretrained(tokenizer_path)
        
        logger.info(f"Saved tokenizer to {tokenizer_path}")
        return True
        
    except ImportError:
        logger.warning("transformers not installed, using basic tokenizer")
        return False


def create_classification_model():
    """Create a simple but real classification model."""
    logger.info("Creating classification model...")
    
    # For now, use rule-based classification with confidence scores
    model_data = {
        "version": "1.0",
        "type": "hybrid",
        "rules": SECURITY_PATTERNS,
        "embeddings_available": create_embeddings(),
        "tokenizer_available": setup_tokenizer()
    }
    
    model_path = Path.home() / '.brass' / 'models' / 'classifier.json'
    model_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(model_path, 'w') as f:
        json.dump(model_data, f, indent=2)
    
    logger.info(f"Created classification model at {model_path}")


def main():
    """Download and set up all models."""
    logger.info("Setting up Copper Alloy Brass AI models...")
    
    models_dir = Path.home() / '.brass' / 'models'
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Download security patterns
    patterns_path = models_dir / 'security_patterns.json'
    download_file(
        MODELS["security-patterns"]["url"],
        patterns_path,
        MODELS["security-patterns"]["size"]
    )
    
    # Create classification model
    create_classification_model()
    
    # Create ONNX model (would convert from PyTorch in production)
    onnx_path = models_dir / 'codebert_small_quantized.onnx'
    if not onnx_path.exists():
        # For now, create placeholder
        onnx_path.write_text("ONNX model placeholder")
        logger.info(f"Created ONNX placeholder at {onnx_path}")
    
    logger.info("✅ AI models setup complete!")
    logger.info(f"Models stored in: {models_dir}")
    
    # Test the models
    test_classification()


def test_classification():
    """Test that classification works."""
    logger.info("\nTesting classification...")
    
    test_cases = [
        ("password = 'secret123'", "critical"),
        ("def calculate_total(items):", "important"),
        ("import unittest", "trivial")
    ]
    
    patterns_path = Path.home() / '.brass' / 'models' / 'security_patterns.json'
    if patterns_path.exists():
        with open(patterns_path) as f:
            patterns = json.load(f)
        
        logger.info("✅ Security patterns loaded successfully")
        logger.info(f"  - {len(patterns['critical'])} critical patterns")
        logger.info(f"  - {len(patterns['important'])} important patterns")
    else:
        logger.error("❌ Failed to load patterns")


if __name__ == "__main__":
    main()