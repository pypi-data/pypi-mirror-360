"""
Copper Alloy Brass Context Protocol (DCP) Schema Definitions and Validation
Provides JSON schema validation for coppersun_brass.context.json files
"""

import json
from typing import Dict, Any, List, Optional, Union
from jsonschema import validate, ValidationError, Draft7Validator
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Complete DCP JSON Schema based on v0.6 specification
DCP_SCHEMA = {
    "type": "object",
    "properties": {
        "meta": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "minLength": 1},
                "generated_at": {"type": "string", "format": "date-time"},
                "version": {"type": "string", "pattern": "^dcp-\\d+\\.\\d+$"},
                "audience": {"type": "string", "enum": ["AI"]},
                "brass_role": {"type": "string", "enum": ["general_staff"]},
                "token_budget_hint": {"type": "integer", "minimum": 1000}
            },
            "required": ["project_id", "generated_at", "version", "audience", "brass_role"],
            "additionalProperties": False
        },
        "doctrine": {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "minLength": 10}
            },
            "required": ["summary"],
            "additionalProperties": False
        },
        "project_awareness": {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "minLength": 10},
                "language": {"type": "string", "minLength": 1},
                "framework": {"type": "string", "minLength": 1},
                "components_of_interest": {
                    "type": "array",
                    "items": {"type": "string", "minLength": 1},
                    "uniqueItems": True
                }
            },
            "required": ["summary"],
            "additionalProperties": True
        },
        "current_observations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "type": {"type": "string", "enum": ["code_health", "implementation_gap", "test_coverage", "security", "performance", "architecture", "code_entity", "code_issue", "code_metrics", "file_analysis", "persistent_issue", "pattern_match"]},
                    "priority": {"type": "integer", "minimum": 0, "maximum": 100},
                    "summary": {"type": "string", "minLength": 10},
                    "subtype": {"type": "string"},
                    "location": {"type": "object"},
                    "complexity": {"type": "integer"},
                    "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                    "fingerprint": {"type": "string"},
                    "metadata": {"type": "object"}
                },
                "required": ["id", "type", "priority", "summary"],
                "additionalProperties": True
            }
        },
        "strategic_recommendations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "priority": {"type": "integer", "minimum": 0, "maximum": 100},
                    "summary": {"type": "string", "minLength": 10},
                    "tone": {"type": "string", "enum": ["strategic suggestion", "engineering best practice", "test coverage suggestion", "security warning", "performance optimization"]},
                    "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "declined"], "default": "pending"},
                    "rationale": {"type": "string"},
                    "last_updated": {"type": "string", "format": "date-time"},
                    "last_used_by": {"type": "string"},
                    "claude_annotation": {"type": "string"},
                    "effectiveness_score": {"type": "number", "minimum": 0, "maximum": 10}
                },
                "required": ["priority", "summary", "tone"],
                "additionalProperties": False
            }
        },
        "ai_context_stabilization": {
            "type": "object",
            "properties": {
                "rationale": {"type": "string", "minLength": 20},
                "recommended_artifacts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "file": {"type": "string", "minLength": 1},
                            "purpose": {"type": "string", "minLength": 10},
                            "status": {"type": "string", "enum": ["not_found", "partial", "complete", "low_density"]}
                        },
                        "required": ["file", "purpose", "status"],
                        "additionalProperties": False
                    }
                },
                "execution_guidance": {"type": "string", "minLength": 10}
            },
            "required": ["rationale", "recommended_artifacts", "execution_guidance"],
            "additionalProperties": False
        }
    },
    "required": ["meta", "doctrine", "project_awareness", "current_observations", "strategic_recommendations", "ai_context_stabilization"],
    "additionalProperties": False
}

class DCPValidationError(Exception):
    """Raised when DCP validation fails"""
    def __init__(self, message: str, validation_errors: List[str] = None):
        super().__init__(message)
        self.validation_errors = validation_errors or []

class DCPSchemaValidator:
    """Validates DCP JSON structure and content"""
    
    def __init__(self):
        self.validator = Draft7Validator(DCP_SCHEMA)
        
    def validate_dcp(self, dcp_data: Dict[str, Any]) -> bool:
        """
        Validate DCP structure against schema
        
        Args:
            dcp_data: Dictionary containing DCP data
            
        Returns:
            True if valid
            
        Raises:
            DCPValidationError: If validation fails
        """
        try:
            # Basic schema validation
            validate(instance=dcp_data, schema=DCP_SCHEMA)
            
            # Additional business logic validation
            self._validate_business_rules(dcp_data)
            
            logger.info("DCP validation passed")
            return True
            
        except ValidationError as e:
            error_message = f"Schema validation failed: {e.message}"
            if e.absolute_path:
                error_message += f" at path: {' -> '.join(str(p) for p in e.absolute_path)}"
            raise DCPValidationError(error_message, [str(e)])
            
        except Exception as e:
            raise DCPValidationError(f"Validation error: {str(e)}")
    
    def _validate_business_rules(self, dcp_data: Dict[str, Any]) -> None:
        """Validate business logic rules beyond JSON schema"""
        
        # Validate datetime format
        try:
            datetime.fromisoformat(dcp_data["meta"]["generated_at"].replace('Z', '+00:00'))
        except ValueError:
            raise DCPValidationError("Invalid datetime format in meta.generated_at")
        
        # Validate unique observation IDs
        obs_ids = [obs["id"] for obs in dcp_data.get("current_observations", [])]
        if len(obs_ids) != len(set(obs_ids)):
            raise DCPValidationError("Duplicate observation IDs found")
        
        # Validate priority ranges make sense
        recommendations = dcp_data.get("strategic_recommendations", [])
        if recommendations:
            priorities = [rec["priority"] for rec in recommendations]
            if max(priorities) - min(priorities) < 10 and len(priorities) > 1:
                logger.warning("All recommendations have similar priorities - consider more spread")
    
    def get_validation_errors(self, dcp_data: Dict[str, Any]) -> List[str]:
        """
        Get all validation errors without raising exceptions
        
        Args:
            dcp_data: Dictionary containing DCP data
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        try:
            # Collect all schema validation errors
            for error in self.validator.iter_errors(dcp_data):
                error_msg = f"{error.message}"
                if error.absolute_path:
                    error_msg += f" at {' -> '.join(str(p) for p in error.absolute_path)}"
                errors.append(error_msg)
            
            # Business rule validation
            if not errors:  # Only check business rules if schema is valid
                try:
                    self._validate_business_rules(dcp_data)
                except DCPValidationError as e:
                    errors.extend(e.validation_errors or [str(e)])
                    
        except Exception as e:
            errors.append(f"Validation system error: {str(e)}")
        
        return errors
    
    def validate_partial_dcp(self, partial_data: Dict[str, Any], required_sections: List[str] = None) -> bool:
        """
        Validate partial DCP data (useful for incremental updates)
        
        Args:
            partial_data: Partial DCP data
            required_sections: Sections that must be present
            
        Returns:
            True if valid partial data
        """
        required_sections = required_sections or ["meta"]
        
        # Check required sections
        missing_sections = [section for section in required_sections if section not in partial_data]
        if missing_sections:
            raise DCPValidationError(f"Missing required sections: {missing_sections}")
        
        # Validate each present section against schema
        for section_name, section_data in partial_data.items():
            if section_name in DCP_SCHEMA["properties"]:
                section_schema = DCP_SCHEMA["properties"][section_name]
                try:
                    validate(instance=section_data, schema=section_schema)
                except ValidationError as e:
                    raise DCPValidationError(f"Invalid {section_name} section: {e.message}")
        
        return True

def create_dcp_template(project_id: str, project_summary: str = "") -> Dict[str, Any]:
    """
    Create a valid DCP template for a new project
    
    Args:
        project_id: Unique project identifier
        project_summary: Brief project description
        
    Returns:
        Valid DCP template dictionary
    """
    return {
        "meta": {
            "project_id": project_id,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "version": "dcp-0.6",
            "audience": "AI",
            "brass_role": "general_staff",
            "token_budget_hint": 10000
        },
        "doctrine": {
            "summary": "Copper Alloy Brass functions as a general staff. It does not command. It advises. Copper Alloy Brass exists for the AI, not the human. Its outputs are designed to enhance the AI's context, reasoning, and decision-making. Claude or GPT may accept, modify, or decline any recommendations based on their own understanding and judgment."
        },
        "project_awareness": {
            "summary": project_summary or "Project analysis pending",
            "language": "Unknown",
            "framework": "Unknown",
            "components_of_interest": []
        },
        "current_observations": [],
        "strategic_recommendations": [],
        "ai_context_stabilization": {
            "rationale": "Copper Alloy Brass recommends generating persistent project scaffolding that will support future context extraction and reasoning. These artifacts are not for human consumption — they exist to enable future AI systems (Copper Alloy Brass or Claude/GPT) to interpret project state, intent, and progression more accurately.",
            "recommended_artifacts": [
                {
                    "file": "README.md",
                    "purpose": "Summarize the project's scope and core functionality. This file will be scanned and ingested by Copper Alloy Brass in future analyses.",
                    "status": "not_found"
                },
                {
                    "file": "project_plan.md",
                    "purpose": "Outline current objectives, blockers, and target milestones. Copper Alloy Brass uses this to track alignment and detect planning drift.",
                    "status": "not_found"
                }
            ],
            "execution_guidance": "Claude may generate these artifacts proactively. Their purpose is to support future AI reasoning and continuity of understanding — not to explain to a human."
        }
    }

# Export main components
__all__ = ['DCPSchemaValidator', 'DCPValidationError', 'DCP_SCHEMA', 'create_dcp_template']