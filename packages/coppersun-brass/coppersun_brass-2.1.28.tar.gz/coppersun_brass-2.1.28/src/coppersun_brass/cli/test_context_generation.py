#!/usr/bin/env python3
"""
Test script to demonstrate Copper Alloy Brass context file generation.
"""

import os
import sys
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from context_manager import ContextManager
from coppersun_brass_cli import BrassCLI

def test_context_generation():
    """Test the context file generation system."""
    print("🧪 Testing Copper Alloy Brass Context Generation")
    print("=" * 50)
    
    # Create a test project directory
    test_dir = Path("test_project")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    # Create some test files to analyze
    (test_dir / "README.md").write_text("# Test Project\n\nA test project for Copper Alloy Brass.")
    (test_dir / "main.py").write_text("def main():\n    print('Hello Copper Alloy Brass!')\n")
    (test_dir / "test_main.py").write_text("def test_main():\n    assert True\n")
    
    # Create a src directory
    src_dir = test_dir / "src"
    src_dir.mkdir()
    (src_dir / "utils.py").write_text("def helper():\n    return 42\n")
    
    # Change to test directory
    original_cwd = os.getcwd()
    os.chdir(test_dir)
    
    try:
        # Initialize context manager
        context_manager = ContextManager()
        
        # Create .brass directory
        brass_dir = Path(".brass")
        brass_dir.mkdir(exist_ok=True)
        
        print("\n📁 Generating context files...")
        
        # Generate all context files
        context_manager.update_status()
        print("✅ Generated STATUS.md")
        
        context_manager.update_context("Testing context generation system")
        print("✅ Generated CONTEXT.md")
        
        context_manager.generate_insights()
        print("✅ Generated INSIGHTS.md")
        
        context_manager.add_to_history("Test project created", {"purpose": "Context generation testing"})
        print("✅ Generated HISTORY.md")
        
        # Display generated files
        print("\n📄 Generated Files:")
        print("-" * 50)
        
        for filename in ["STATUS.md", "CONTEXT.md", "INSIGHTS.md", "HISTORY.md"]:
            filepath = brass_dir / filename
            if filepath.exists():
                print(f"\n### {filename}")
                print("-" * 30)
                with open(filepath, 'r') as f:
                    content = f.read()
                    # Show first 500 chars
                    if len(content) > 500:
                        print(content[:500] + "\n... (truncated)")
                    else:
                        print(content)
        
        print("\n✅ Context generation test completed successfully!")
        
    finally:
        # Change back to original directory
        os.chdir(original_cwd)
        
        # Clean up test directory
        if test_dir.exists():
            shutil.rmtree(test_dir)


def test_cli_init():
    """Test the CLI initialization with context generation."""
    print("\n\n🧪 Testing Copper Alloy Brass CLI Initialization")
    print("=" * 50)
    
    # Create a test project directory
    test_dir = Path("test_cli_project")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    # Create some project files
    (test_dir / "app.py").write_text("# Main application\nprint('Copper Alloy Brass Test')\n")
    (test_dir / ".gitignore").write_text("*.pyc\n__pycache__/\n.env\n")
    
    # Change to test directory
    original_cwd = os.getcwd()
    os.chdir(test_dir)
    
    try:
        # Create a mock CLI instance
        cli = BrassCLI()
        
        # Set up a test configuration (simulate activation)
        cli.config["user_preferences"]["license_key"] = "TEST-1234-5678-9012"
        cli.config["user_preferences"]["claude_api_key"] = "sk-ant-test-key"
        cli.config["user_preferences"]["visual_theme"] = "colorful"
        cli.config["user_preferences"]["verbosity"] = "balanced"
        cli._save_config()
        
        # Initialize Copper Alloy Brass
        print("\n🚀 Initializing Copper Alloy Brass...")
        cli.init()
        
        # Check generated files
        brass_dir = Path(".brass")
        if brass_dir.exists():
            print("\n✅ .brass directory created")
            
            # List all files
            print("\n📁 Generated files:")
            for file in brass_dir.iterdir():
                print(f"  - {file.name} ({file.stat().st_size} bytes)")
        
        # Test refresh command
        print("\n🔄 Testing refresh command...")
        cli.refresh()
        
        print("\n✅ CLI initialization test completed successfully!")
        
    finally:
        # Change back to original directory
        os.chdir(original_cwd)
        
        # Clean up test directory
        if test_dir.exists():
            shutil.rmtree(test_dir)


if __name__ == "__main__":
    test_context_generation()
    test_cli_init()