#!/usr/bin/env python3
"""
Test the integrated AI instructions with prepend templates.
"""

import sys
from pathlib import Path
import json
import shutil

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ai_instructions_manager import AIInstructionsManager
from prepend_templates import PrependTemplateManager


def test_integrated_system():
    """Test the integration of AI instructions with prepend templates."""
    print("🧠 Testing Integrated Copper Alloy Brass System")
    print("=" * 60)
    
    # Test with different configurations
    configs = [
        {"visual_theme": "colorful", "verbosity": "balanced"},
        {"visual_theme": "professional", "verbosity": "detailed"},
        {"visual_theme": "monochrome", "verbosity": "minimal"}
    ]
    
    for config in configs:
        print(f"\n📋 Configuration: Theme={config['visual_theme']}, Verbosity={config['verbosity']}")
        print("-" * 60)
        
        # Create test directory
        test_dir = Path(f"test_integration_{config['visual_theme']}")
        if test_dir.exists():
            shutil.rmtree(test_dir)
        test_dir.mkdir()
        
        try:
            # Set up managers with config
            ai_manager = AIInstructionsManager(test_dir)
            ai_manager.config = {"user_preferences": config}
            
            # Generate Copper Alloy Brass section
            section = ai_manager.create_brass_section()
            
            # Display first 800 characters of the section
            print("\nGenerated Copper Alloy Brass Section Preview:")
            print("~" * 40)
            if len(section) > 800:
                print(section[:800] + "\n...(truncated)")
            else:
                print(section)
            
            # Test prepend examples
            prepend_manager = PrependTemplateManager()
            prepend_manager.config = {"user_preferences": config}
            
            print("\nSample Prepend Messages:")
            for msg_type in ["initialization", "insight", "warning"]:
                msg = prepend_manager.get_prepend_message(msg_type)
                print(f"  {msg}")
                
        finally:
            # Clean up
            if test_dir.exists():
                shutil.rmtree(test_dir)
    
    print("\n" + "=" * 60)
    print("✅ Integrated system test completed!")


def test_full_ai_instruction_file():
    """Test creation of a complete AI instruction file."""
    print("\n\n📄 Testing Full AI Instruction File Generation")
    print("=" * 60)
    
    test_dir = Path("test_full_instructions")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    try:
        # Create manager with specific config
        ai_manager = AIInstructionsManager(test_dir)
        ai_manager.config = {
            "user_preferences": {
                "visual_theme": "colorful",
                "verbosity": "balanced",
                "user_name": "TestUser"
            }
        }
        
        # Create default AI instructions
        file_path = ai_manager.create_default_ai_instructions()
        print(f"\n✅ Created file: {file_path.name}")
        
        # Read and display the file
        with open(file_path, 'r') as f:
            content = f.read()
        
        print("\nFile Content:")
        print("~" * 60)
        print(content)
        
        # Validate the file
        validation = ai_manager.validate_brass_integration(file_path)
        print("\n✅ Validation Results:")
        for key, value in validation.items():
            if key != "issues":
                print(f"  - {key}: {value}")
        
        if validation["issues"]:
            print("  - Issues found:")
            for issue in validation["issues"]:
                print(f"    • {issue}")
        else:
            print("  - No issues found!")
            
    finally:
        # Clean up
        if test_dir.exists():
            shutil.rmtree(test_dir)
    
    print("\n✅ Full instruction file test completed!")


def demo_real_world_scenario():
    """Demonstrate a real-world usage scenario."""
    print("\n\n🌟 Real-World Scenario Demo")
    print("=" * 60)
    print("Simulating: User asks Claude to fix a bug")
    print("-" * 60)
    
    # Set up configuration
    config = {"user_preferences": {"visual_theme": "colorful", "verbosity": "balanced"}}
    prepend_manager = PrependTemplateManager()
    prepend_manager.config = config
    
    # Simulate different stages of the response
    stages = [
        ("context_check", None, "Claude checks Copper Alloy Brass context first"),
        ("analysis", None, "Claude analyzes the code"),
        ("insight", "Found similar bug fixed in commit abc123 last week", "Claude finds relevant history"),
        ("task_start", None, "Claude begins fixing the bug"),
        ("task_complete", "Bug fixed - null pointer check added to line 47", "Claude completes the fix")
    ]
    
    print("\nClaude's response flow:\n")
    
    for msg_type, custom_msg, description in stages:
        prepend = prepend_manager.get_prepend_message(msg_type, custom_message=custom_msg)
        print(f"{prepend}")
        print(f"└─ {description}")
        print()
    
    print("✅ Demo completed!")


if __name__ == "__main__":
    test_integrated_system()
    test_full_ai_instruction_file()
    demo_real_world_scenario()