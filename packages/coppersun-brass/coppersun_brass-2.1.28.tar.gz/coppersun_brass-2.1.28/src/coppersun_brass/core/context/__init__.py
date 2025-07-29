"""
Copper Alloy Brass Context Protocol (DCP) Module
Core infrastructure for AI-first project coordination
Enhanced with ChatGPT recommendations for safety and feedback loops
"""

from .schemas import (
    DCPSchemaValidator, 
    DCPValidationError, 
    DCP_SCHEMA, 
    create_dcp_template
)

from .dcp_manager import (
    DCPManager, 
    DCPUpdateResult
)

__version__ = "1.0.0"  # Production release
__author__ = "Copper Alloy Brass"

# Export main public interface
__all__ = [
    # Core classes
    'DCPManager',
    'DCPSchemaValidator',
    
    # Result types
    'DCPUpdateResult',
    'DCPValidationError',
    
    # Utilities
    'create_dcp_template',
    'DCP_SCHEMA'
]

# Default configuration
DEFAULT_DCP_FILENAME = "coppersun_brass.context.json"
DEFAULT_BACKUP_DIR = "dcp_versions"

def quick_validate(dcp_path: str) -> bool:
    """
    Quick validation of DCP file
    
    Args:
        dcp_path: Path to DCP file
        
    Returns:
        True if valid, False otherwise
    """
    try:
        import os
        from pathlib import Path
        
        manager = DCPManager(str(Path(dcp_path).parent))
        dcp_data = manager.read_dcp(validate=True)
        return True
    except Exception:
        return False

def create_project_dcp(project_root: str, project_id: str, project_summary: str = "") -> 'DCPUpdateResult':
    """
    Convenience function to create new DCP for a project
    
    Args:
        project_root: Root directory for the project
        project_id: Unique project identifier
        project_summary: Brief project description
        
    Returns:
        DCPUpdateResult with creation status
    """
    manager = DCPManager(project_root)
    return manager.create_new_dcp(project_id, project_summary)

def get_project_info(project_root: str) -> dict:
    """
    Get project DCP information
    
    Args:
        project_root: Root directory for the project
        
    Returns:
        Dictionary with project DCP info
    """
    manager = DCPManager(project_root)
    return manager.get_dcp_info()

def annotate_recommendation(project_root: str, rec_index: int, annotation: str, 
                          effectiveness_score: float = None) -> 'DCPUpdateResult':
    """
    Convenience function for Claude to annotate recommendations
    
    Args:
        project_root: Root directory for the project
        rec_index: Index of recommendation to annotate
        annotation: Claude's annotation text
        effectiveness_score: Optional effectiveness score (0-10)
        
    Returns:
        DCPUpdateResult with annotation status
    """
    try:
        manager = DCPManager(project_root)
        dcp_data = manager.read_dcp(validate=True)
        
        recommendations = dcp_data.get('strategic_recommendations', [])
        if rec_index >= len(recommendations):
            return DCPUpdateResult(
                success=False,
                message=f"Invalid recommendation index: {rec_index}"
            )
        
        # Update recommendation with Claude annotation
        from datetime import datetime
        recommendations[rec_index]['claude_annotation'] = annotation
        recommendations[rec_index]['last_updated'] = datetime.utcnow().isoformat() + "Z"
        recommendations[rec_index]['last_used_by'] = "claude"
        
        if effectiveness_score is not None and 0 <= effectiveness_score <= 10:
            recommendations[rec_index]['effectiveness_score'] = effectiveness_score
        
        return manager.update_dcp_section('strategic_recommendations', recommendations, 
                                        editor="claude", allow_protected=True)
        
    except Exception as e:
        return DCPUpdateResult(success=False, message=str(e))