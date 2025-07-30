#!/usr/bin/env python3
"""
Demo script to show Copper Alloy Brass context generation on the actual project.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from context_manager import ContextManager

def demo_context_generation():
    """Demonstrate context generation on the Copper Alloy Brass project itself."""
    print("🧠 Copper Alloy Brass Context Generation Demo")
    print("=" * 60)
    
    # Initialize context manager for the Copper Alloy Brass project (go up two levels)
    project_root = Path(__file__).parent.parent.parent
    context_manager = ContextManager(project_root)
    
    # Create a temporary .brass directory for demo
    demo_dir = project_root / ".brass_demo"
    context_manager.brass_dir = demo_dir
    
    # Update file paths
    context_manager.status_file = demo_dir / "STATUS.md"
    context_manager.context_file = demo_dir / "CONTEXT.md"
    context_manager.insights_file = demo_dir / "INSIGHTS.md"
    context_manager.history_file = demo_dir / "HISTORY.md"
    
    print(f"\n📁 Analyzing project at: {project_root}")
    print(f"📂 Generating demo files in: {demo_dir}")
    
    # Generate all context files
    print("\n⚡ Generating context files...")
    
    context_manager.update_status()
    print("✅ Generated STATUS.md")
    
    context_manager.update_context("Copper Alloy Brass Pro v1.0 - Building persistent memory for AI agents")
    print("✅ Generated CONTEXT.md")
    
    context_manager.generate_insights()
    print("✅ Generated INSIGHTS.md")
    
    context_manager.add_to_history(
        "Context generation system completed",
        {
            "component": "ContextManager",
            "purpose": "Generate meaningful .brass/ files",
            "roadmap_task": "Day 11-12 context file generation"
        }
    )
    print("✅ Generated HISTORY.md")
    
    # Display generated content
    print("\n" + "=" * 60)
    print("📄 GENERATED CONTENT PREVIEW")
    print("=" * 60)
    
    for filename in ["STATUS.md", "CONTEXT.md", "INSIGHTS.md", "HISTORY.md"]:
        filepath = demo_dir / filename
        if filepath.exists():
            print(f"\n### {filename}")
            print("-" * 40)
            with open(filepath, 'r') as f:
                content = f.read()
                # Show content (truncate if too long)
                if len(content) > 800:
                    print(content[:800] + "\n\n... (truncated for display)")
                else:
                    print(content)
    
    print("\n" + "=" * 60)
    print("✅ Demo completed! Check .brass_demo/ for full files")
    print("\nThese files demonstrate how Copper Alloy Brass analyzes your project:")
    print("- STATUS.md: Project statistics and current state")
    print("- CONTEXT.md: Key directories and technology stack")
    print("- INSIGHTS.md: Patterns, security checks, and suggestions")
    print("- HISTORY.md: Timeline of important events")
    

if __name__ == "__main__":
    demo_context_generation()