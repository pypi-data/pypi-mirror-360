#!/usr/bin/env python3
"""
Test script for AI Instructions Manager functionality.
"""

import os
import sys
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ai_instructions_manager import AIInstructionsManager

def test_ai_instructions():
    """Test AI instruction file detection and updates."""
    print("🧪 Testing AI Instructions Manager")
    print("=" * 60)
    
    # Test on the actual Copper Alloy Brass project
    project_root = Path(__file__).parent.parent.parent
    ai_manager = AIInstructionsManager(project_root)
    
    print(f"\n📁 Searching for AI instruction files in: {project_root}")
    
    # Find existing AI instruction files
    found_files = ai_manager.find_ai_instruction_files()
    
    if found_files:
        print(f"\n✅ Found {len(found_files)} AI instruction file(s):")
        for file in found_files:
            print(f"  - {file.relative_to(project_root)}")
            
            # Validate each file
            validation = ai_manager.validate_brass_integration(file)
            print(f"    Validation:")
            print(f"      - Has Copper Alloy Brass section: {validation['has_brass_section']}")
            print(f"      - Has correct theme: {validation['has_correct_theme']}")
            print(f"      - Has context check: {validation['has_context_check']}")
            print(f"      - Has indicators: {validation['has_indicator_examples']}")
            
            if validation['issues']:
                print(f"      - Issues: {', '.join(validation['issues'])}")
    else:
        print("\n❌ No AI instruction files found")
    
    # Test creating Copper Alloy Brass section
    print("\n" + "-" * 60)
    print("📝 Testing Copper Alloy Brass section generation:")
    print("-" * 60)
    
    section = ai_manager.create_brass_section()
    print(section[:500] + "..." if len(section) > 500 else section)
    
    # Test creating a new file in a temporary location
    print("\n" + "-" * 60)
    print("📄 Testing file creation:")
    print("-" * 60)
    
    test_dir = Path("test_ai_instructions")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    try:
        # Change manager to test directory
        test_manager = AIInstructionsManager(test_dir)
        
        # Create default instructions
        new_file = test_manager.create_default_ai_instructions()
        print(f"✅ Created: {new_file.relative_to(test_dir)}")
        
        # Validate the created file
        validation = test_manager.validate_brass_integration(new_file)
        print(f"\nValidation of new file:")
        print(f"  - Has Copper Alloy Brass section: {validation['has_brass_section']}")
        print(f"  - Has correct theme: {validation['has_correct_theme']}")
        print(f"  - Has context check: {validation['has_context_check']}")
        print(f"  - All checks passed: {not validation['issues']}")
        
    finally:
        # Clean up
        if test_dir.exists():
            shutil.rmtree(test_dir)
    
    print("\n✅ AI Instructions Manager test completed!")


def test_update_existing_file():
    """Test updating an existing AI instruction file."""
    print("\n\n🧪 Testing Update of Existing File")
    print("=" * 60)
    
    test_dir = Path("test_update_ai")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    try:
        # Create a test AI instruction file
        test_file = test_dir / "CLAUDE.md"
        test_content = """# Claude Instructions

This is a test file for Claude.

## Guidelines

1. Follow the code style
2. Write tests
3. Be helpful

## Notes

Remember to check the documentation.
"""
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        print(f"📄 Created test file: {test_file.name}")
        print("Original content preview:")
        print("-" * 40)
        print(test_content[:200] + "..." if len(test_content) > 200 else test_content)
        
        # Update the file
        test_manager = AIInstructionsManager(test_dir)
        success, message = test_manager.update_ai_instruction_file(test_file)
        
        print(f"\n🔄 Update result: {message}")
        print(f"Success: {success}")
        
        if success:
            # Show updated content
            with open(test_file, 'r') as f:
                updated_content = f.read()
            
            print("\nUpdated content preview:")
            print("-" * 40)
            print(updated_content[:600] + "..." if len(updated_content) > 600 else updated_content)
            
            # Validate
            validation = test_manager.validate_brass_integration(test_file)
            print(f"\n✅ Validation passed: {not validation['issues']}")
        
    finally:
        # Clean up
        if test_dir.exists():
            shutil.rmtree(test_dir)
    
    print("\n✅ Update test completed!")


if __name__ == "__main__":
    test_ai_instructions()
    test_update_existing_file()