#!/usr/bin/env python3
"""
🚨 LEGACY FILE - NO LONGER USED 🚨

Set up ML models for Copper Alloy Brass - creates working tokenizer and ONNX model

⚠️ This file is LEGACY and no longer called by any active code paths.
🩸 Pure Python ML engine (pure_python_ml.py) is now used instead.
❌ This file contains heavy dependencies and should not be used.

Note: This creates basic models with random weights. For better performance,
use setup_pretrained_models.py which creates models pre-trained on code patterns.
"""
import os
import json
import logging
from pathlib import Path
import numpy as np
import torch
import onnx
from onnx import helper, TensorProto
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Whitespace

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tokenizer(model_dir: Path):
    """Create a working BPE tokenizer for code."""
    tokenizer_path = model_dir / "code_tokenizer.json"
    
    if tokenizer_path.exists():
        logger.info(f"Tokenizer already exists at {tokenizer_path}")
        return
    
    logger.info("Creating BPE tokenizer...")
    
    # Create tokenizer
    tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
    tokenizer.pre_tokenizer = Whitespace()
    
    # Training samples
    code_samples = [
        "def function(param1, param2):",
        "import numpy as np",
        "class MyClass(BaseClass):",
        "if __name__ == '__main__':",
        "for i in range(10):",
        "while True:",
        "try: something() except Exception as e:",
        "return result",
        "self.attribute = value",
        "# TODO: implement this",
        "# FIXME: bug here",
        "password = 'secret123'",
        "api_key = 'sk-1234567890'",
        "eval(user_input)",
        "exec(command)",
        "pickle.load(file)",
        "os.system(cmd)",
        "subprocess.call(shell=True)",
        "__import__('os').system",
        "except: pass",
    ]
    
    # Train tokenizer
    trainer = BpeTrainer(
        vocab_size=1000,
        special_tokens=["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"]
    )
    
    tokenizer.train_from_iterator(code_samples, trainer)
    
    # Save tokenizer
    tokenizer.save(str(tokenizer_path))
    logger.info(f"✅ Created tokenizer at {tokenizer_path}")


def create_onnx_model(model_dir: Path):
    """Create a simple ONNX classification model."""
    onnx_path = model_dir / "classifier.onnx"
    
    if onnx_path.exists() and onnx_path.stat().st_size > 100:
        logger.info(f"ONNX model already exists at {onnx_path}")
        return
    
    logger.info("Creating ONNX model...")
    
    # Create a simple 3-class classifier
    # Input: 128 tokens (int64)
    # Output: 3 classes (float32)
    
    # Define input
    input_tensor = helper.make_tensor_value_info(
        'input_ids', TensorProto.INT64, [1, 128]
    )
    
    # Define output
    output_tensor = helper.make_tensor_value_info(
        'output', TensorProto.FLOAT, [1, 3]
    )
    
    # Create embedding layer (simplified)
    embedding_weight = helper.make_tensor(
        'embedding_weight',
        TensorProto.FLOAT,
        [1000, 64],  # vocab_size x embedding_dim
        np.random.randn(1000, 64).astype(np.float32).flatten()
    )
    
    # Create classifier weight
    classifier_weight = helper.make_tensor(
        'classifier_weight',
        TensorProto.FLOAT,
        [64, 3],  # embedding_dim x num_classes
        np.random.randn(64, 3).astype(np.float32).flatten()
    )
    
    # Create bias
    classifier_bias = helper.make_tensor(
        'classifier_bias',
        TensorProto.FLOAT,
        [3],
        np.zeros(3).astype(np.float32)
    )
    
    # Build graph
    gather_node = helper.make_node(
        'Gather',
        inputs=['embedding_weight', 'input_ids'],
        outputs=['embeddings'],
        axis=0
    )
    
    reduce_mean_node = helper.make_node(
        'ReduceMean',
        inputs=['embeddings'],
        outputs=['pooled'],
        axes=[1],
        keepdims=0
    )
    
    matmul_node = helper.make_node(
        'MatMul',
        inputs=['pooled', 'classifier_weight'],
        outputs=['logits']
    )
    
    add_node = helper.make_node(
        'Add',
        inputs=['logits', 'classifier_bias'],
        outputs=['output']
    )
    
    # Create graph
    graph_def = helper.make_graph(
        [gather_node, reduce_mean_node, matmul_node, add_node],
        'classifier',
        [input_tensor],
        [output_tensor],
        [embedding_weight, classifier_weight, classifier_bias]
    )
    
    # Create model with compatible IR version
    model_def = helper.make_model(graph_def, producer_name='coppersun_brass', opset_imports=[helper.make_opsetid("", 14)])
    model_def.ir_version = 7  # Use IR version 7 for compatibility
    
    # Save model
    onnx.save(model_def, str(onnx_path))
    logger.info(f"✅ Created ONNX model at {onnx_path}")


def main():
    """Set up all ML models."""
    # Model directory
    model_dir = Path.home() / '.brass' / 'models'
    model_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Setting up ML models for Copper Alloy Brass...")
    
    # Create tokenizer
    create_tokenizer(model_dir)
    
    # Create ONNX model
    create_onnx_model(model_dir)
    
    # Verify setup
    tokenizer_path = model_dir / "code_tokenizer.json"
    onnx_path = model_dir / "classifier.onnx"
    
    if tokenizer_path.exists() and onnx_path.exists():
        logger.info("✅ ML models set up successfully!")
        
        # Test tokenizer
        try:
            tokenizer = Tokenizer.from_file(str(tokenizer_path))
            test_text = "def hello_world():"
            encoded = tokenizer.encode(test_text)
            logger.info(f"✅ Tokenizer test passed: '{test_text}' → {len(encoded.ids)} tokens")
        except Exception as e:
            logger.error(f"Tokenizer test failed: {e}")
        
        # Test ONNX model
        try:
            import onnxruntime as ort
            session = ort.InferenceSession(str(onnx_path))
            test_input = np.zeros((1, 128), dtype=np.int64)
            outputs = session.run(None, {'input_ids': test_input})
            logger.info(f"✅ ONNX model test passed: output shape = {outputs[0].shape}")
        except Exception as e:
            logger.error(f"ONNX model test failed: {e}")
    else:
        logger.error("Failed to create all required models")


if __name__ == "__main__":
    main()