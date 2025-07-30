#!/usr/bin/env python3
"""
Test script for prepend message templates.
"""

import sys
from pathlib import Path
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from prepend_templates import PrependTemplateManager


def test_prepend_templates():
    """Test prepend template generation with different configurations."""
    print("🧪 Testing Prepend Message Templates")
    print("=" * 60)
    
    # Test with different configurations
    configs = [
        {"visual_theme": "colorful", "verbosity": "detailed"},
        {"visual_theme": "colorful", "verbosity": "balanced"},
        {"visual_theme": "colorful", "verbosity": "minimal"},
        {"visual_theme": "professional", "verbosity": "balanced"},
        {"visual_theme": "monochrome", "verbosity": "balanced"}
    ]
    
    for config in configs:
        print(f"\n📋 Configuration: Theme={config['visual_theme']}, Verbosity={config['verbosity']}")
        print("-" * 60)
        
        # Create a temporary config
        temp_config = {"user_preferences": config}
        manager = PrependTemplateManager()
        manager.config = temp_config
        
        # Test each message type
        for message_type in ["initialization", "analysis", "insight", "task_complete", "warning"]:
            message = manager.get_prepend_message(message_type)
            print(f"{message_type:15} → {message}")
        
        print()
    
    print("\n" + "=" * 60)
    print("📝 Testing Context-Aware Messages")
    print("=" * 60)
    
    # Test with context
    manager = PrependTemplateManager()
    manager.config = {"user_preferences": {"visual_theme": "colorful", "verbosity": "detailed"}}
    
    test_contexts = [
        ("analysis", {"file_name": "main.py", "line_count": 150}),
        ("insight", {"pattern_name": "Singleton", "file_name": "database.py"}),
        ("task_complete", {"function_name": "process_data", "line_count": 25}),
        ("warning", {"file_name": "config.py", "pattern_name": "hardcoded secret"})
    ]
    
    for msg_type, context in test_contexts:
        message = manager.format_with_context(msg_type, **context)
        print(f"\n{msg_type}:")
        print(f"  Context: {context}")
        print(f"  Message: {message}")
    
    print("\n" + "=" * 60)
    print("🤖 Testing Intent-Based Response Starters")
    print("=" * 60)
    
    manager.config = {"user_preferences": {"visual_theme": "colorful", "verbosity": "balanced"}}
    
    intents = ["question", "task", "review", "debug", "test", "fix", "explain", "optimize", "security"]
    
    for intent in intents:
        message = manager.get_response_starter(intent)
        print(f"{intent:12} → {message}")
    
    print("\n" + "=" * 60)
    print("📄 Testing Instruction Snippet Generation")
    print("=" * 60)
    
    snippet = manager.create_instruction_snippet()
    print(snippet)
    
    print("\n✅ Prepend template testing completed!")


def demo_all_themes():
    """Demonstrate all themes and their emojis."""
    print("\n\n🎨 All Theme Demonstrations")
    print("=" * 60)
    
    manager = PrependTemplateManager()
    
    for theme_name, theme_emojis in manager.THEMES.items():
        print(f"\n### {theme_name.title()} Theme")
        print("-" * 40)
        
        manager.config = {"user_preferences": {"visual_theme": theme_name, "verbosity": "balanced"}}
        
        # Show all emojis for this theme
        print("Emojis:")
        for emoji_type, emoji in theme_emojis.items():
            print(f"  {emoji_type:10} {emoji}")
        
        print("\nExample messages:")
        examples = manager.get_all_examples()
        for msg_type, example in list(examples.items())[:5]:  # Show first 5
            print(f"  {example}")
        

def test_custom_messages():
    """Test custom message functionality."""
    print("\n\n💬 Testing Custom Messages")
    print("=" * 60)
    
    manager = PrependTemplateManager()
    manager.config = {"user_preferences": {"visual_theme": "colorful", "verbosity": "balanced"}}
    
    custom_messages = [
        "Found 3 security vulnerabilities in authentication flow",
        "Optimized database queries - 50% performance improvement",
        "All 127 tests passing after refactoring",
        "Migration completed successfully - 5,432 records updated",
        "Code review complete - 12 suggestions added"
    ]
    
    for custom_msg in custom_messages:
        # Determine appropriate message type based on content
        if "security" in custom_msg.lower() or "vulnerabilit" in custom_msg.lower():
            msg_type = "warning"
        elif "complet" in custom_msg.lower() or "success" in custom_msg.lower():
            msg_type = "task_complete"
        elif "optimiz" in custom_msg.lower() or "improv" in custom_msg.lower():
            msg_type = "insight"
        elif "test" in custom_msg.lower():
            msg_type = "test"
        else:
            msg_type = "analysis"
        
        prepend = manager.get_prepend_message(msg_type, custom_message=custom_msg)
        print(f"\nCustom: {custom_msg}")
        print(f"Result: {prepend}")


if __name__ == "__main__":
    test_prepend_templates()
    demo_all_themes()
    test_custom_messages()