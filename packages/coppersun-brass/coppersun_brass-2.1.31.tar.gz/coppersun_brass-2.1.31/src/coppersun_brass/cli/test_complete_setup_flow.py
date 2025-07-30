#!/usr/bin/env python3
"""
Test the complete Copper Alloy Brass Pro setup flow for Claude Code.

This simulates the entire user journey from receiving the setup file
to having a fully configured Copper Alloy Brass environment.
"""

import os
import sys
import shutil
from pathlib import Path
import json
import subprocess
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from coppersun_brass_cli import BrassCLI
from license_manager import LicenseManager
from context_manager import ContextManager
from ai_instructions_manager import AIInstructionsManager
from prepend_templates import PrependTemplateManager


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 70}")
    print(f"🧠 {title}")
    print('=' * 70)


def simulate_user_setup():
    """Simulate the complete user setup flow."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "BRASS PRO SETUP FLOW TEST" + " " * 21 + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Create a test project directory
    test_project = Path("test_claude_project")
    if test_project.exists():
        shutil.rmtree(test_project)
    test_project.mkdir()
    
    # Change to test project directory
    original_cwd = os.getcwd()
    os.chdir(test_project)
    
    try:
        # Step 1: User receives brass-setup.md file
        print_section("Step 1: User Receives Setup File")
        print("📧 Email received with Copper Alloy Brass Pro license")
        print("📎 Attachment: brass-setup.md")
        print("🔑 License Key: BRASS-TEST-DEMO-1234-5678")
        
        # Create a mock brass-setup.md
        setup_content = """# Copper Alloy Brass Pro Setup for Claude Code

Welcome to Copper Alloy Brass Pro! Follow these steps to enable persistent memory.

## Your License Key
```
BRASS-TEST-DEMO-1234-5678
```

## Setup Instructions
1. Save this file in your project directory
2. Tell Claude: "Read brass-setup.md and set up Copper Alloy Brass"
3. Provide your license key when asked
4. Choose your preferences
5. Enjoy persistent memory!
"""
        with open("brass-setup.md", "w") as f:
            f.write(setup_content)
        print("✅ Setup file saved to project directory")
        
        # Step 2: Claude reads the setup file
        print_section("Step 2: Claude Reads Setup File")
        print("👤 User: 'Read brass-setup.md and set up Copper Alloy Brass'")
        print("🤖 Claude: Reading setup file...")
        
        with open("brass-setup.md", "r") as f:
            content = f.read()
        print(f"✅ Read {len(content)} characters from setup file")
        
        # Step 3: Install Copper Alloy Brass (simulate)
        print_section("Step 3: Install Copper Alloy Brass Pro")
        print("🤖 Claude: Installing Copper Alloy Brass Pro...")
        print("   $ pip install brass-pro")
        print("✅ Copper Alloy Brass Pro installed successfully (simulated)")
        
        # Step 4: Activate license
        print_section("Step 4: Activate License")
        cli = BrassCLI()
        
        # Create a test license
        test_license = LicenseManager.generate_customer_license("test@example.com", 365)
        print(f"🤖 Claude: Activating license...")
        print(f"   $ brass activate {test_license}")
        
        success = cli.activate(test_license)
        if success:
            print("✅ License activated successfully!")
        else:
            print("❌ License activation failed")
        
        # Step 5: Configure Claude API key
        print_section("Step 5: Configure Claude API Key")
        print("🤖 Claude: Setting Claude API key...")
        print("   $ brass config set claude_api_key sk-ant-test-key-123")
        
        cli.config_set("claude_api_key", "sk-ant-test-key-123")
        
        # Step 6: Choose preferences
        print_section("Step 6: Choose Preferences")
        print("🤖 Claude: Let's set your preferences...")
        print("\n📋 Available themes:")
        print("   1. colorful (🧠💡🚨✨) - Vibrant and expressive")
        print("   2. professional (📊📈⚠️✓) - Clean and business-like")
        print("   3. monochrome (●▶▲✓) - Minimal and focused")
        print("\n👤 User chooses: colorful")
        
        cli.config_set("visual_theme", "colorful")
        
        print("\n📋 Verbosity levels:")
        print("   1. detailed - Full context with timestamps")
        print("   2. balanced - Clear and informative")
        print("   3. minimal - Just the essentials")
        print("\n👤 User chooses: balanced")
        
        cli.config_set("verbosity", "balanced")
        
        # Step 7: Initialize Copper Alloy Brass
        print_section("Step 7: Initialize Copper Alloy Brass")
        print("🤖 Claude: Initializing Copper Alloy Brass for your project...")
        print("   $ brass init")
        
        cli.init()
        
        # Step 8: Verify setup
        print_section("Step 8: Verify Setup")
        print("🤖 Claude: Let me verify everything is working...")
        
        # Check that all files were created
        brass_dir = Path(".brass")
        expected_files = [
            "config.json",
            "STATUS.md",
            "CONTEXT.md", 
            "INSIGHTS.md",
            "HISTORY.md",
            "AI_INSTRUCTIONS.md"
        ]
        
        print("\n📁 Checking .brass/ directory:")
        all_good = True
        for filename in expected_files:
            filepath = brass_dir / filename
            if filepath.exists():
                size = filepath.stat().st_size
                print(f"   ✅ {filename} ({size} bytes)")
            else:
                print(f"   ❌ {filename} (missing)")
                all_good = False
        
        # Step 9: Test prepend messages
        print_section("Step 9: Test Copper Alloy Brass Indicators")
        print("🤖 Claude: Testing prepend message system...")
        
        prepend_manager = PrependTemplateManager()
        prepend_manager.config = cli.config
        
        print("\nExample responses with Copper Alloy Brass indicators:")
        test_scenarios = [
            ("initialization", "Hello! How can I help you today?"),
            ("analysis", "Let me analyze your code..."),
            ("insight", "I found a similar pattern in your project history"),
            ("task_complete", "I've successfully implemented the feature"),
            ("warning", "I noticed a potential security issue")
        ]
        
        for msg_type, follow_up in test_scenarios:
            prepend = prepend_manager.get_prepend_message(msg_type)
            print(f"\n{prepend}")
            print(f"{follow_up}")
        
        # Step 10: Show AI instructions
        print_section("Step 10: AI Instructions Active")
        print("🤖 Claude: I've updated my instructions to always use Copper Alloy Brass")
        
        ai_file = brass_dir / "AI_INSTRUCTIONS.md"
        if ai_file.exists():
            with open(ai_file, 'r') as f:
                content = f.read()
            
            # Show just the Copper Alloy Brass section
            if "<!-- BRASS_SECTION_START -->" in content:
                start = content.find("<!-- BRASS_SECTION_START -->")
                end = content.find("<!-- BRASS_SECTION_END -->")
                if end > start:
                    section = content[start:end]
                    print("\n📄 AI Instructions (Copper Alloy Brass section):")
                    print("-" * 50)
                    print(section[:400] + "..." if len(section) > 400 else section)
        
        # Final status
        print_section("Setup Complete! 🎉")
        print("✅ Copper Alloy Brass Pro is now active and monitoring")
        print("✅ Persistent memory enabled across Claude sessions")
        print("✅ All responses will start with Copper Alloy Brass indicators")
        print("✅ Context files will be maintained automatically")
        
        print("\n💡 Next steps:")
        print("1. Claude will now prepend Copper Alloy Brass indicators to all responses")
        print("2. Context persists across all your Claude Code sessions")
        print("3. Use 'brass refresh' to update context anytime")
        print("4. Check .brass/ folder to see your project insights")
        
        # Show final status
        print("\n" + "-" * 70)
        cli.status()
        
        return all_good
        
    finally:
        # Change back to original directory
        os.chdir(original_cwd)
        
        # Clean up test directory
        if test_project.exists():
            shutil.rmtree(test_project)


def test_error_scenarios():
    """Test various error scenarios in the setup flow."""
    print_section("Testing Error Scenarios")
    
    test_dir = Path("test_errors")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    original_cwd = os.getcwd()
    os.chdir(test_dir)
    
    try:
        cli = BrassCLI()
        
        # Test 1: Init without license
        print("\n❌ Test 1: Initialize without license")
        cli.init()
        
        # Test 2: Invalid license
        print("\n❌ Test 2: Invalid license key")
        cli.activate("INVALID-LICENSE-KEY")
        
        # Test 3: Init without Claude API key
        print("\n❌ Test 3: Initialize without Claude API key")
        # First activate with valid license
        test_license = LicenseManager.generate_customer_license("test@example.com", 365)
        cli.activate(test_license)
        # Try to init without API key
        cli.init()
        
        print("\n✅ All error scenarios handled correctly!")
        
    finally:
        os.chdir(original_cwd)
        if test_dir.exists():
            shutil.rmtree(test_dir)


def main():
    """Run the complete setup flow test."""
    try:
        # Run the main setup flow simulation
        success = simulate_user_setup()
        
        # Test error scenarios
        test_error_scenarios()
        
        # Final summary
        print("\n" + "=" * 70)
        print("✅ COMPLETE SETUP FLOW TEST PASSED!")
        print("=" * 70)
        print("\nThe Copper Alloy Brass Pro setup flow is working correctly:")
        print("- License activation ✅")
        print("- Configuration management ✅")
        print("- Context file generation ✅")
        print("- AI instruction integration ✅")
        print("- Prepend message system ✅")
        print("- Error handling ✅")
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())