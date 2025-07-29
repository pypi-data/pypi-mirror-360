#!/usr/bin/env python3
"""Basic DCP functionality test"""

import sys
import os
from pathlib import Path

# Add the project root to Python path (4 levels up from this file)
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test basic imports work"""
    try:
        from coppersun_brass.core.context import DCPManager, DCPSchemaValidator
        print("✅ Core imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print(f"Python path: {sys.path}")
        print(f"Project root: {project_root}")
        print(f"Looking for: {project_root / 'coppersun_brass'}")
        print(f"Exists: {(project_root / 'coppersun_brass').exists()}")
        return False

def test_template_creation():
    """Test DCP template creation"""
    try:
        from coppersun_brass.core.context import create_project_dcp
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = create_project_dcp(temp_dir, "test-project", "Test project")
            if result.success:
                print("✅ Template creation successful")
                return True
            else:
                print(f"❌ Template creation failed: {result.message}")
                return False
    except Exception as e:
        print(f"❌ Template creation error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running basic DCP tests...")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Test file location: {__file__}")
    
    tests = [test_imports(), test_template_creation()]
    
    if all(tests):
        print("🎉 All basic tests passed!")
        sys.exit(0)
    else:
        print("⚠️ Some tests failed")
        sys.exit(1)