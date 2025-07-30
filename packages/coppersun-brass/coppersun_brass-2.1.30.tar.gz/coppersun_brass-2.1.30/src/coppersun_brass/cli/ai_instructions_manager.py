"""
AI Instructions Manager for Copper Sun Brass Pro - Manages AI instruction files.

This module handles detection, updating, and creation of AI instruction files
that ensure Claude Code (and other AI agents) remember to use Copper Sun Brass features.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import json
import re
from datetime import datetime

try:
    from .prepend_templates import PrependTemplateManager
except ImportError:
    from prepend_templates import PrependTemplateManager


class AIInstructionsManager:
    """Manages AI instruction files for persistent Copper Sun Brass configuration."""
    
    # Common AI instruction file names to search for
    AI_FILE_PATTERNS = [
        "AI_START_HERE.md",
        "AI_INSTRUCTIONS.md",
        "README_AI.md",
        "CLAUDE.md",
        ".ai/instructions.md",
        ".github/AI_GUIDE.md",
        "docs/AI_CONTEXT.md",
        "AI_AGENT_START_HERE.md",
        ".claude/instructions.md",
        "ASSISTANT_GUIDE.md"
    ]
    
    # Copper Sun Brass section markers
    BRASS_SECTION_START = "<!-- BRASS_SECTION_START -->"
    BRASS_SECTION_END = "<!-- BRASS_SECTION_END -->"
    
    def __init__(self, project_root: Path = Path.cwd()):
        self.project_root = project_root
        self.brass_dir = project_root / ".brass"
        self.config_file = self.brass_dir / "config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load Copper Sun Brass configuration."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"user_preferences": {}}
    
    def find_ai_instruction_files(self) -> List[Path]:
        """Find all AI instruction files in the project."""
        found_files = []
        
        # Search for exact matches
        for pattern in self.AI_FILE_PATTERNS:
            file_path = self.project_root / pattern
            if file_path.exists() and file_path.is_file():
                found_files.append(file_path)
        
        # Also search for files with AI/Claude in the name
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() == '.md':
                filename_lower = file_path.name.lower()
                if any(keyword in filename_lower for keyword in ['ai_', 'claude', 'assistant', 'llm']):
                    if file_path not in found_files:
                        # Check if it looks like an instruction file
                        if self._is_likely_ai_instruction_file(file_path):
                            found_files.append(file_path)
        
        return found_files
    
    def _is_likely_ai_instruction_file(self, file_path: Path) -> bool:
        """Check if a file is likely an AI instruction file based on content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1000).lower()  # Read first 1000 chars
            
            # Look for AI instruction keywords
            keywords = [
                'ai assistant', 'claude', 'gpt', 'instruction', 'guideline',
                'when you', 'you should', 'you must', 'always', 'never',
                'context', 'remember', 'important:', 'note:'
            ]
            
            keyword_count = sum(1 for keyword in keywords if keyword in content)
            return keyword_count >= 3  # At least 3 keywords
            
        except Exception:
            return False
    
    def create_brass_section(self) -> str:
        """Create the Copper Alloy Brass section for AI instruction files."""
        prefs = self.config.get("user_preferences", {})
        theme = prefs.get("visual_theme", "colorful")
        verbosity = prefs.get("verbosity", "balanced")
        
        # Use PrependTemplateManager to get dynamic examples
        prepend_manager = PrependTemplateManager()
        prepend_manager.config = self.config
        
        # Get example messages for different scenarios
        examples = []
        for msg_type, description in [
            ("initialization", "Starting work or responding to a query"),
            ("analysis", "Analyzing code or searching for patterns"),
            ("insight", "Found relevant pattern or insight from history"),
            ("task_complete", "Completed a task successfully"),
            ("warning", "Important issue or security concern detected")
        ]:
            example = prepend_manager.get_prepend_message(msg_type)
            examples.append(f"   - {example} ← {description}")
        
        # Get theme emojis for reference
        theme_emojis = prepend_manager.THEMES.get(theme, prepend_manager.THEMES["colorful"])
        
        section = f"""
{self.BRASS_SECTION_START}
## 🎺 Copper Sun Brass Pro Integration

**CRITICAL**: This project uses Copper Sun Brass Pro for persistent memory and enhanced insights.

### Response Protocol
**For EVERY response you write, you MUST:**

1. **Start with Copper Sun Brass indicator** using the {theme} theme:
{chr(10).join(examples)}

2. **Check Copper Sun Brass context** before responding:
   - Read `.brass/STATUS.md` for project state
   - Read `.brass/CONTEXT.md` for current work
   - Read `.brass/INSIGHTS.md` for recommendations
   - Read `.brass/HISTORY.md` for past decisions

3. **Update Copper Sun Brass** when appropriate:
   - Use `brass refresh` to update context
   - Reference insights in your responses
   - Maintain awareness across sessions

### Copper Sun Brass Configuration
- Visual Theme: **{theme}**
- Verbosity: **{verbosity}**
- Status: **Active** ✅

### Example Response Format
```
{theme_emojis['active']} Copper Sun Brass: Reviewing project history for similar patterns...

Based on Copper Sun Brass's analysis, I found that [specific insight from .brass files].
Here's my recommendation...
```

### Important Notes
- Copper Sun Brass provides persistent memory across Claude sessions
- Always check .brass/ files for context
- Copper Sun Brass only advises - you make the decisions
- Update context with `brass refresh` when needed

Remember: **Every response must start with a Copper Sun Brass indicator!**
{self.BRASS_SECTION_END}
"""
        return section
    
    def update_ai_instruction_file(self, file_path: Path) -> Tuple[bool, str]:
        """Update an AI instruction file with Copper Sun Brass section."""
        try:
            # Read current content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if Copper Alloy Brass section already exists
            if self.BRASS_SECTION_START in content:
                # Update existing section
                start_idx = content.find(self.BRASS_SECTION_START)
                end_idx = content.find(self.BRASS_SECTION_END) + len(self.BRASS_SECTION_END)
                
                if end_idx > start_idx:
                    # Replace existing section
                    new_content = (
                        content[:start_idx] +
                        self.create_brass_section() +
                        content[end_idx:]
                    )
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    return True, "Updated existing Copper Sun Brass section"
                else:
                    return False, "Malformed Copper Sun Brass section markers"
            else:
                # Add new section
                # Try to add after the first heading or at the beginning
                lines = content.split('\n')
                insert_index = 0
                
                # Find a good place to insert (after first heading)
                for i, line in enumerate(lines):
                    if line.strip().startswith('#') and i > 0:
                        insert_index = i + 1
                        break
                
                # Insert the section
                lines.insert(insert_index, self.create_brass_section())
                new_content = '\n'.join(lines)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                return True, "Added Copper Sun Brass section"
                
        except Exception as e:
            return False, f"Error updating file: {str(e)}"
    
    def create_default_ai_instructions(self) -> Path:
        """Create a default AI instructions file with Copper Sun Brass configuration."""
        # Ensure .brass directory exists
        self.brass_dir.mkdir(exist_ok=True)
        
        file_path = self.brass_dir / "AI_INSTRUCTIONS.md"
        
        content = f"""# AI Assistant Instructions

This file contains instructions for AI assistants (Claude, GPT, etc.) working on this project.

{self.create_brass_section()}

## Project Guidelines

### Code Style
- Follow existing patterns in the codebase
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and small

### Testing
- Write tests for new functionality
- Ensure existing tests pass
- Follow the project's testing conventions

### Documentation
- Update documentation when changing APIs
- Keep README files current
- Document complex algorithms

### Security
- Never commit secrets or API keys
- Review code for security implications
- Follow security best practices

## Remember
- Copper Alloy Brass is here to help maintain context across sessions
- Always start responses with Copper Alloy Brass indicators
- Check .brass/ files for project context
- You're building WITH Copper Alloy Brass, not FOR Copper Alloy Brass

---
*Last updated: {datetime.now().strftime('%Y-%m-%d')}*
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    def ensure_ai_instructions_exist(self) -> Tuple[Path, str]:
        """Ensure AI instructions exist, creating or updating as needed."""
        # First, look for existing AI instruction files
        existing_files = self.find_ai_instruction_files()
        
        if existing_files:
            # Update the first found file
            target_file = existing_files[0]
            success, message = self.update_ai_instruction_file(target_file)
            
            if success:
                return target_file, f"Updated existing file: {target_file.name}"
            else:
                # If update failed, create default
                new_file = self.create_default_ai_instructions()
                return new_file, f"Created new file due to update error: {message}"
        else:
            # No existing files, create default
            new_file = self.create_default_ai_instructions()
            return new_file, "Created new AI instructions file"
    
    def validate_brass_integration(self, file_path: Path) -> Dict[str, Any]:
        """Validate that an AI instruction file has proper Copper Alloy Brass integration."""
        result = {
            "has_brass_section": False,
            "has_correct_theme": False,
            "has_context_check": False,
            "has_indicator_examples": False,
            "issues": []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for Copper Alloy Brass section
            result["has_brass_section"] = self.BRASS_SECTION_START in content
            
            if result["has_brass_section"]:
                # Extract Copper Alloy Brass section
                start_idx = content.find(self.BRASS_SECTION_START)
                end_idx = content.find(self.BRASS_SECTION_END)
                
                if end_idx > start_idx:
                    section_content = content[start_idx:end_idx]
                    
                    # Check for theme
                    prefs = self.config.get("user_preferences", {})
                    current_theme = prefs.get("visual_theme", "colorful")
                    result["has_correct_theme"] = current_theme in section_content
                    
                    # Check for context file references
                    result["has_context_check"] = all(
                        filename in section_content 
                        for filename in ["STATUS.md", "CONTEXT.md", "INSIGHTS.md", "HISTORY.md"]
                    )
                    
                    # Check for indicator examples
                    result["has_indicator_examples"] = "Copper Alloy Brass:" in section_content
                    
                    # Identify issues
                    if not result["has_correct_theme"]:
                        result["issues"].append(f"Theme mismatch: expected '{current_theme}'")
                    
                    if not result["has_context_check"]:
                        result["issues"].append("Missing references to .brass/ context files")
                    
                    if not result["has_indicator_examples"]:
                        result["issues"].append("Missing Copper Alloy Brass indicator examples")
                else:
                    result["issues"].append("Malformed Copper Alloy Brass section markers")
            else:
                result["issues"].append("No Copper Alloy Brass section found")
            
        except Exception as e:
            result["issues"].append(f"Error reading file: {str(e)}")
        
        return result