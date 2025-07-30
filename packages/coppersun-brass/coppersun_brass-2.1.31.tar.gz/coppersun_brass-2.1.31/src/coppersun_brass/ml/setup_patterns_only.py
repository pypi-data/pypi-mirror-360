#!/usr/bin/env python3
"""
Setup Copper Sun Brass with pattern-based ML (no large dependencies required)
This gives you working ML classification without downloading CodeBERT
"""
import os
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_patterns():
    """Set up pattern-based classification."""
    logger.info("🔍 Setting up pattern-based ML...")
    
    models_dir = Path.home() / '.brass' / 'models'
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Enhanced security patterns
    patterns = {
        "critical": [
            {"pattern": r"password\s*=\s*[\"'][^\"']+[\"']", "severity": 95, "description": "Hardcoded password"},
            {"pattern": r"api_key\s*=\s*[\"'][^\"']+[\"']", "severity": 95, "description": "Hardcoded API key"},
            {"pattern": r"secret\s*=\s*[\"'][^\"']+[\"']", "severity": 94, "description": "Hardcoded secret"},
            {"pattern": r"private_key\s*=\s*[\"'][^\"']+[\"']", "severity": 96, "description": "Hardcoded private key"},
            {"pattern": r"eval\s*\([^)]+\)", "severity": 90, "description": "Eval usage - code injection risk"},
            {"pattern": r"exec\s*\([^)]+\)", "severity": 90, "description": "Exec usage - code injection risk"},
            {"pattern": r"pickle\.loads?\s*\([^)]+\)", "severity": 88, "description": "Pickle deserialization"},
            {"pattern": r"os\.system\s*\([^)]+\)", "severity": 85, "description": "Shell command execution"},
            {"pattern": r"subprocess\.\w+\s*\([^)]+shell\s*=\s*True", "severity": 85, "description": "Shell=True risk"},
            {"pattern": r"SELECT.*FROM.*WHERE.*[\+\%]", "severity": 92, "description": "Possible SQL injection"},
            {"pattern": r"__import__\s*\(", "severity": 80, "description": "Dynamic import risk"}
        ],
        "important": [
            {"pattern": r"TODO|FIXME|XXX|HACK", "severity": 50, "description": "Technical debt marker"},
            {"pattern": r"except\s*:\s*pass", "severity": 60, "description": "Bare except clause"},
            {"pattern": r"if\s+.*==\s*True|if\s+.*==\s*False", "severity": 40, "description": "Explicit bool comparison"},
            {"pattern": r"print\s*\(.*password|print\s*\(.*secret", "severity": 70, "description": "Sensitive data logging"},
            {"pattern": r"# type:\s*ignore", "severity": 45, "description": "Type checking disabled"},
            {"pattern": r"assert\s+", "severity": 55, "description": "Assert in production code"}
        ]
    }
    
    # Save patterns
    patterns_path = models_dir / 'security_patterns.json'
    with open(patterns_path, 'w') as f:
        json.dump(patterns, f, indent=2)
    
    logger.info(f"✅ Saved {len(patterns['critical'])} critical patterns")
    logger.info(f"✅ Saved {len(patterns['important'])} important patterns")
    
    return True

def test_claude_env():
    """Test if Claude API key is available."""
    logger.info("\n🔑 Checking Claude API key...")
    
    # Check .env file
    env_path = Path.cwd() / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.startswith('ANTHROPIC_API_KEY='):
                    logger.info("✅ Found API key in .env file")
                    return True
    
    # Check environment
    if os.getenv('ANTHROPIC_API_KEY'):
        logger.info("✅ Found API key in environment")
        return True
    
    logger.warning("⚠️  No Claude API key found - will work without Claude validation")
    return False

def create_config():
    """Create ML configuration."""
    logger.info("\n📝 Creating configuration...")
    
    config = {
        'models': {
            'patterns': {
                'enabled': True,
                'path': str(Path.home() / '.brass' / 'models' / 'security_patterns.json')
            },
            'pure_python_ml': {
                'enabled': True,
                'note': 'Pure Python ML engine - always available, zero dependencies'
            }
        },
        'claude_api': {
            'enabled': test_claude_env(),
            'model': 'claude-3-haiku-20240307',
            'note': 'Will use if API key found'
        },
        'filtering': {
            'quick_filter_threshold': 0.9,
            'pattern_confidence_threshold': 0.7
        }
    }
    
    config_path = Path.home() / '.brass' / 'ml_config.json'
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"✅ Configuration saved to {config_path}")
    return True

def test_patterns():
    """Test pattern matching."""
    logger.info("\n🧪 Testing pattern detection...")
    
    test_cases = [
        ("password = 'admin123'", "critical"),
        ("eval(user_input)", "critical"),
        ("TODO: fix this later", "important"),
        ("def hello(): pass", "normal")
    ]
    
    patterns_path = Path.home() / '.brass' / 'models' / 'security_patterns.json'
    with open(patterns_path) as f:
        patterns = json.load(f)
    
    import re
    
    for code, expected in test_cases:
        found = False
        for category in ['critical', 'important']:
            for pattern_info in patterns.get(category, []):
                if re.search(pattern_info['pattern'], code, re.IGNORECASE):
                    logger.info(f"✅ '{code[:30]}...' detected as {category}")
                    found = True
                    break
            if found:
                break
        
        if not found:
            logger.info(f"ℹ️  '{code[:30]}...' classified as normal")

def main():
    """Run setup."""
    logger.info("🚀 Copper Sun Brass Pattern-Based ML Setup")
    logger.info("=" * 50)
    
    # Create directories
    models_dir = Path.home() / '.brass' / 'models'
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup components
    setup_patterns()
    create_config()
    test_patterns()
    
    logger.info("\n✅ Setup Complete!")
    logger.info("\nCopper Sun Brass will use:")
    logger.info("- Pattern-based detection (works now!)")
    
    if test_claude_env():
        logger.info("- Claude API for validation (API key found)")
    else:
        logger.info("- No Claude API (add ANTHROPIC_API_KEY to .env)")
    
    logger.info("\nTo add full ML capabilities later:")
    logger.info("1. pip install transformers torch sentence-transformers")
    logger.info("2. python coppersun_brass/ml/setup_real_ml.py")
    
    logger.info("\nYou can start using Copper Sun Brass now!")
    logger.info("1. brass init")
    logger.info("2. brass analyze")

if __name__ == "__main__":
    main()