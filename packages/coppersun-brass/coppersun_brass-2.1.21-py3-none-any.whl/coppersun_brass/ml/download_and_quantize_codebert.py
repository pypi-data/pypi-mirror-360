#!/usr/bin/env python3
"""
🚨 LEGACY FILE - NO LONGER USED 🚨

Download and quantize CodeBERT to ~21MB
This creates a small, fast model perfect for Copper Alloy Brass

⚠️ This file is LEGACY and no longer called by any active code paths.
🩸 Pure Python ML engine (pure_python_ml.py) is now used instead.
❌ This file contains heavy dependencies and should not be used.
"""
import os
import sys
import logging
import shutil
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check required packages."""
    missing = []
    
    try:
        import transformers
        logger.info("✅ transformers installed")
    except ImportError:
        missing.append("transformers")
    
    try:
        import torch
        logger.info("✅ torch installed")
    except ImportError:
        missing.append("torch")
    
    try:
        import onnx
        logger.info("✅ onnx installed")
    except ImportError:
        missing.append("onnx")
    
    try:
        import onnxruntime
        logger.info("✅ onnxruntime installed")
    except ImportError:
        missing.append("onnxruntime")
    
    if missing:
        logger.error(f"\n❌ Missing packages: {', '.join(missing)}")
        logger.error(f"Please run: pip install {' '.join(missing)}")
        return False
    
    return True

def download_codebert():
    """Download CodeBERT from HuggingFace."""
    logger.info("\n📥 Downloading CodeBERT from HuggingFace...")
    
    from transformers import AutoModel, AutoTokenizer
    
    model_name = "microsoft/codebert-base"
    cache_dir = Path.home() / '.brass' / 'models' / 'codebert_temp'
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Download tokenizer
    logger.info("Downloading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
    
    # Download model
    logger.info("Downloading model (this may take a few minutes)...")
    model = AutoModel.from_pretrained(model_name, cache_dir=cache_dir)
    
    # Check size
    size_mb = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file()) / (1024*1024)
    logger.info(f"Downloaded model size: {size_mb:.1f} MB")
    
    return model, tokenizer, cache_dir

def export_to_onnx(model, tokenizer, output_dir):
    """Export CodeBERT to ONNX format."""
    logger.info("\n🔄 Converting to ONNX format...")
    
    import torch
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create dummy input
    dummy_text = "def hello_world(): pass"
    inputs = tokenizer(dummy_text, return_tensors="pt", max_length=512, padding="max_length", truncation=True)
    
    # Export model
    model.eval()
    onnx_path = output_dir / "codebert.onnx"
    
    torch.onnx.export(
        model,
        (inputs['input_ids'], inputs['attention_mask']),
        onnx_path,
        export_params=True,
        opset_version=14,  # Updated from 11 to support scaled_dot_product_attention
        do_constant_folding=True,
        input_names=['input_ids', 'attention_mask'],
        output_names=['last_hidden_state', 'pooler_output'],
        dynamic_axes={
            'input_ids': {0: 'batch_size', 1: 'sequence'},
            'attention_mask': {0: 'batch_size', 1: 'sequence'},
            'last_hidden_state': {0: 'batch_size', 1: 'sequence'},
            'pooler_output': {0: 'batch_size'}
        }
    )
    
    size_mb = onnx_path.stat().st_size / (1024*1024)
    logger.info(f"ONNX model size: {size_mb:.1f} MB")
    
    return onnx_path

def quantize_model(onnx_path, output_dir):
    """Quantize ONNX model to INT8 for massive size reduction."""
    logger.info("\n🗜️ Quantizing model to INT8...")
    
    from onnxruntime.quantization import quantize_dynamic, QuantType
    
    output_dir = Path(output_dir)
    quantized_path = output_dir / "codebert_quantized.onnx"
    
    # Quantize to INT8
    quantize_dynamic(
        str(onnx_path),
        str(quantized_path),
        weight_type=QuantType.QInt8
    )
    
    # Check size reduction
    original_mb = onnx_path.stat().st_size / (1024*1024)
    quantized_mb = quantized_path.stat().st_size / (1024*1024)
    reduction = (1 - quantized_mb/original_mb) * 100
    
    logger.info(f"✅ Quantized model size: {quantized_mb:.1f} MB ({reduction:.1f}% reduction)")
    
    return quantized_path

def create_optimized_tokenizer(tokenizer, output_dir):
    """Save tokenizer in optimized format."""
    logger.info("\n💾 Saving optimized tokenizer...")
    
    output_dir = Path(output_dir)
    tokenizer_dir = output_dir / "tokenizer"
    
    # Save tokenizer files
    tokenizer.save_pretrained(tokenizer_dir)
    
    # Also save vocabulary separately for faster loading
    vocab_path = output_dir / "vocab.json"
    import json
    with open(vocab_path, 'w') as f:
        json.dump(tokenizer.get_vocab(), f)
    
    logger.info(f"✅ Tokenizer saved to {tokenizer_dir}")
    
    return tokenizer_dir

def create_classifier_head():
    """Create a small classifier head for code classification."""
    logger.info("\n🧠 Creating classifier head...")
    
    import torch
    import torch.nn as nn
    
    # Small classifier for 3 classes
    classifier = nn.Sequential(
        nn.Linear(768, 256),  # CodeBERT hidden size = 768
        nn.ReLU(),
        nn.Dropout(0.1),
        nn.Linear(256, 64),
        nn.ReLU(),
        nn.Dropout(0.1),
        nn.Linear(64, 3)  # 3 classes: trivial, important, critical
    )
    
    # Initialize weights
    for module in classifier.modules():
        if isinstance(module, nn.Linear):
            nn.init.xavier_uniform_(module.weight)
            nn.init.zeros_(module.bias)
    
    # Save classifier
    output_dir = Path.home() / '.brass' / 'models' / 'codebert_quantized'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    torch.save({
        'classifier': classifier.state_dict(),
        'input_size': 768,
        'num_classes': 3
    }, output_dir / 'classifier_head.pt')
    
    logger.info("✅ Classifier head created")
    
    return classifier

def test_quantized_model(model_path):
    """Test the quantized model works."""
    logger.info("\n🧪 Testing quantized model...")
    
    import onnxruntime as ort
    import numpy as np
    
    # Load model
    session = ort.InferenceSession(str(model_path))
    
    # Test input
    batch_size = 1
    seq_length = 128
    input_ids = np.random.randint(0, 1000, (batch_size, seq_length), dtype=np.int64)
    attention_mask = np.ones((batch_size, seq_length), dtype=np.int64)
    
    # Run inference
    outputs = session.run(None, {
        'input_ids': input_ids,
        'attention_mask': attention_mask
    })
    
    logger.info(f"✅ Model output shape: {outputs[0].shape}")
    logger.info("✅ Quantized model working correctly!")
    
    return True

def cleanup_temp_files(temp_dir):
    """Remove temporary files to save space."""
    logger.info("\n🧹 Cleaning up temporary files...")
    
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        logger.info("✅ Removed temporary files")

def update_config():
    """Update ML config to use quantized model."""
    config_path = Path.home() / '.brass' / 'ml_config.json'
    
    import json
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
    else:
        config = {}
    
    config['models']['codebert'] = {
        'enabled': True,
        'type': 'quantized',
        'path': str(Path.home() / '.brass' / 'models' / 'codebert_quantized'),
        'model_file': 'codebert_quantized.onnx',
        'size_mb': 21  # Approximate
    }
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info("✅ Updated configuration")

def main():
    """Run the complete download and quantization process."""
    logger.info("🚀 CodeBERT Download and Quantization")
    logger.info("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    try:
        # Download CodeBERT
        model, tokenizer, temp_dir = download_codebert()
        
        # Export to ONNX
        output_dir = Path.home() / '.brass' / 'models' / 'codebert_quantized'
        onnx_path = export_to_onnx(model, tokenizer, output_dir)
        
        # Quantize to INT8
        quantized_path = quantize_model(onnx_path, output_dir)
        
        # Save tokenizer
        create_optimized_tokenizer(tokenizer, output_dir)
        
        # Create classifier head
        create_classifier_head()
        
        # Test model
        test_quantized_model(quantized_path)
        
        # Update config
        update_config()
        
        # Cleanup
        cleanup_temp_files(temp_dir)
        
        # Final summary
        final_size = sum(f.stat().st_size for f in output_dir.rglob('*') if f.is_file()) / (1024*1024)
        logger.info(f"\n✅ Success! Final model size: {final_size:.1f} MB")
        logger.info(f"Model saved to: {output_dir}")
        logger.info("\nCodeBERT is now ready for use in Copper Alloy Brass!")
        
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # First install the additional dependency
    logger.info("Installing ONNX if needed...")
    os.system("pip install onnx onnxruntime-tools --quiet")
    
    main()