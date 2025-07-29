"""
Prepend Message Templates for Copper Sun Brass Pro.

This module manages the prepend message templates that ensure Claude Code
starts every response with a Copper Sun Brass indicator.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json
import random
from datetime import datetime


class PrependTemplateManager:
    """Manages prepend message templates for Copper Sun Brass responses."""
    
    # Visual themes with their emojis
    THEMES = {
        "colorful": {
            "active": "🎺",
            "insight": "💡",
            "alert": "🚨",
            "success": "✨",
            "check": "✅",
            "search": "🔍",
            "build": "🔨",
            "test": "🧪",
            "docs": "📚"
        },
        "professional": {
            "active": "📊",
            "insight": "📈",
            "alert": "⚠️",
            "success": "✓",
            "check": "✓",
            "search": "🔎",
            "build": "⚙️",
            "test": "🔬",
            "docs": "📄"
        },
        "monochrome": {
            "active": "●",
            "insight": "▶",
            "alert": "▲",
            "success": "✓",
            "check": "✓",
            "search": "○",
            "build": "□",
            "test": "◆",
            "docs": "▪"
        }
    }
    
    # Verbosity templates
    VERBOSITY_FORMATS = {
        "detailed": "{emoji} Copper Sun Brass: {action} | Context: {context} | Time: {time}",
        "balanced": "{emoji} Copper Sun Brass: {message}",
        "minimal": "{emoji} Copper Sun Brass{suffix}"
    }
    
    # Message types and their templates
    MESSAGE_TYPES = {
        "initialization": {
            "actions": ["Initializing", "Starting up", "Activating"],
            "contexts": ["project analysis", "memory systems", "intelligence gathering"],
            "messages": ["Ready to assist with development", "Context loaded and monitoring", "Active and analyzing your project"],
            "suffixes": [" active", " ready", " online"]
        },
        "analysis": {
            "actions": ["Analyzing", "Scanning", "Examining"],
            "contexts": ["code patterns", "project structure", "dependencies"],
            "messages": ["Analyzing your codebase for insights", "Scanning project for patterns", "Examining code structure"],
            "suffixes": [" analyzing...", " scanning...", " processing..."]
        },
        "insight": {
            "actions": ["Found", "Discovered", "Identified"],
            "contexts": ["relevant pattern", "optimization opportunity", "best practice"],
            "messages": ["Found relevant pattern from project history", "Discovered insight from previous sessions", "Identified pattern matching your query"],
            "suffixes": [" insight found", " pattern detected", " match found"]
        },
        "task_start": {
            "actions": ["Starting", "Beginning", "Initiating"],
            "contexts": ["implementation", "task execution", "requested operation"],
            "messages": ["Starting work on your request", "Beginning implementation", "Initiating task execution"],
            "suffixes": [" working...", " implementing...", " executing..."]
        },
        "task_complete": {
            "actions": ["Completed", "Finished", "Done"],
            "contexts": ["task execution", "implementation", "requested changes"],
            "messages": ["Task completed successfully", "Implementation finished", "Changes applied successfully"],
            "suffixes": [" complete", " done", " finished"]
        },
        "warning": {
            "actions": ["Warning", "Caution", "Alert"],
            "contexts": ["potential issue", "security concern", "performance impact"],
            "messages": ["Potential issue detected", "Security consideration identified", "Performance impact possible"],
            "suffixes": [" warning", " alert", " caution"]
        },
        "error": {
            "actions": ["Error", "Issue", "Problem"],
            "contexts": ["execution failure", "validation error", "unexpected state"],
            "messages": ["Encountered an issue", "Error detected during execution", "Problem identified"],
            "suffixes": [" error", " issue", " problem"]
        },
        "suggestion": {
            "actions": ["Suggesting", "Recommending", "Proposing"],
            "contexts": ["improvement", "optimization", "best practice"],
            "messages": ["Based on analysis, recommending approach", "Suggesting optimization based on patterns", "Proposing improvement from insights"],
            "suffixes": [" suggestion", " recommendation", " proposal"]
        },
        "context_check": {
            "actions": ["Checking", "Reading", "Loading"],
            "contexts": ["project context", "previous sessions", "Copper Sun Brass history"],
            "messages": ["Checking project context and history", "Loading insights from previous sessions", "Reading Copper Sun Brass context files"],
            "suffixes": [" checking...", " loading...", " reading..."]
        },
        "test": {
            "actions": ["Testing", "Validating", "Verifying"],
            "contexts": ["implementation", "functionality", "integration"],
            "messages": ["Running tests on implementation", "Validating changes", "Verifying functionality"],
            "suffixes": [" testing...", " validating...", " verifying..."]
        }
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the prepend template manager."""
        self.config_path = config_path or Path(".brass/config.json")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load Copper Sun Brass configuration."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default configuration
        return {
            "user_preferences": {
                "visual_theme": "colorful",
                "verbosity": "balanced"
            }
        }
    
    def get_prepend_message(self, message_type: str = "initialization", 
                          custom_message: Optional[str] = None) -> str:
        """
        Generate a prepend message based on configuration and message type.
        
        Args:
            message_type: Type of message (initialization, analysis, insight, etc.)
            custom_message: Optional custom message to use
            
        Returns:
            Formatted prepend message
        """
        prefs = self.config.get("user_preferences", {})
        theme = prefs.get("visual_theme", "colorful")
        verbosity = prefs.get("verbosity", "balanced")
        
        # Get theme emojis
        theme_emojis = self.THEMES.get(theme, self.THEMES["colorful"])
        
        # Select appropriate emoji for message type
        emoji_map = {
            "initialization": "active",
            "analysis": "search",
            "insight": "insight",
            "task_start": "build",
            "task_complete": "success",
            "warning": "alert",
            "error": "alert",
            "suggestion": "insight",
            "context_check": "search",
            "test": "test"
        }
        
        emoji_key = emoji_map.get(message_type, "active")
        emoji = theme_emojis[emoji_key]
        
        # Get message templates
        templates = self.MESSAGE_TYPES.get(message_type, self.MESSAGE_TYPES["initialization"])
        
        # Generate message based on verbosity
        if verbosity == "detailed":
            action = random.choice(templates["actions"])
            context = random.choice(templates["contexts"])
            time = datetime.now().strftime("%H:%M:%S")
            message = self.VERBOSITY_FORMATS["detailed"].format(
                emoji=emoji,
                action=action,
                context=context,
                time=time
            )
        elif verbosity == "balanced":
            if custom_message:
                message_text = custom_message
            else:
                message_text = random.choice(templates["messages"])
            message = self.VERBOSITY_FORMATS["balanced"].format(
                emoji=emoji,
                message=message_text
            )
        else:  # minimal
            suffix = random.choice(templates["suffixes"])
            message = self.VERBOSITY_FORMATS["minimal"].format(
                emoji=emoji,
                suffix=suffix
            )
        
        return message
    
    def get_all_examples(self) -> Dict[str, str]:
        """Get examples of all message types with current configuration."""
        examples = {}
        for message_type in self.MESSAGE_TYPES.keys():
            examples[message_type] = self.get_prepend_message(message_type)
        return examples
    
    def format_with_context(self, message_type: str, **kwargs) -> str:
        """
        Format a prepend message with specific context.
        
        Args:
            message_type: Type of message
            **kwargs: Context-specific values (file_name, line_count, etc.)
            
        Returns:
            Formatted prepend message with context
        """
        base_message = self.get_prepend_message(message_type)
        
        # Add context if verbosity is detailed or balanced
        prefs = self.config.get("user_preferences", {})
        verbosity = prefs.get("verbosity", "balanced")
        
        if verbosity != "minimal" and kwargs:
            # Format additional context
            context_parts = []
            if "file_name" in kwargs:
                context_parts.append(f"File: {kwargs['file_name']}")
            if "line_count" in kwargs:
                context_parts.append(f"Lines: {kwargs['line_count']}")
            if "function_name" in kwargs:
                context_parts.append(f"Function: {kwargs['function_name']}")
            if "pattern_name" in kwargs:
                context_parts.append(f"Pattern: {kwargs['pattern_name']}")
            
            if context_parts and verbosity == "detailed":
                base_message += f" [{', '.join(context_parts)}]"
        
        return base_message
    
    def get_response_starter(self, detected_intent: Optional[str] = None) -> str:
        """
        Get an appropriate response starter based on detected user intent.
        
        Args:
            detected_intent: Detected intent (question, task, review, etc.)
            
        Returns:
            Appropriate prepend message
        """
        intent_map = {
            "question": "analysis",
            "task": "task_start",
            "review": "analysis",
            "debug": "analysis",
            "test": "test",
            "fix": "task_start",
            "explain": "context_check",
            "optimize": "analysis",
            "security": "analysis",
            "complete": "task_complete",
            "error": "error",
            "warning": "warning"
        }
        
        message_type = intent_map.get(detected_intent, "initialization")
        return self.get_prepend_message(message_type)
    
    def create_instruction_snippet(self) -> str:
        """
        Create an instruction snippet for AI files about prepend messages.
        
        Returns:
            Formatted instruction text
        """
        prefs = self.config.get("user_preferences", {})
        theme = prefs.get("visual_theme", "colorful")
        verbosity = prefs.get("verbosity", "balanced")
        
        examples = []
        for msg_type in ["initialization", "analysis", "insight", "task_complete"]:
            examples.append(f"   - {self.get_prepend_message(msg_type)}")
        
        snippet = f"""### Copper Sun Brass Response Format
Always start your responses with a Copper Sun Brass indicator using the {theme} theme:

Examples:
{chr(10).join(examples)}

Current settings:
- Theme: {theme}
- Verbosity: {verbosity}

The indicator should match the context of your response."""
        
        return snippet