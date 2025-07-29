"""
DCP Helper Functions for Learning Module

Helper functions to work with DCPManager in the learning module.
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def get_dcp_section(dcp_manager, section_path: str, default: Any = None) -> Any:
    """
    Get a section from DCP data.
    
    Args:
        dcp_manager: DCPManager instance
        section_path: Dot-separated path to section (e.g., 'learning.outcomes')
        default: Default value if section not found
        
    Returns:
        Section data or default value
    """
    try:
        dcp_data = dcp_manager.read_dcp()
        if not dcp_data:
            return default
            
        # Navigate through the path
        current = dcp_data
        for part in section_path.split('.'):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
                
        return current
    except Exception as e:
        logger.warning(f"Could not read DCP section {section_path}: {e}")
        return default


def update_dcp_section(dcp_manager, section_path: str, value: Any) -> bool:
    """
    Update a section in DCP data.
    
    Args:
        dcp_manager: DCPManager instance
        section_path: Dot-separated path to section (e.g., 'learning.outcomes')
        value: Value to set
        
    Returns:
        Success boolean
    """
    try:
        dcp_data = dcp_manager.read_dcp() or {}
        
        # Navigate through the path, creating dicts as needed
        parts = section_path.split('.')
        current = dcp_data
        
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                logger.warning(f"Cannot update {section_path}: {'.'.join(parts[:i+1])} is not a dict")
                return False
            current = current[part]
        
        # Set the final value
        current[parts[-1]] = value
        
        # Write back to DCP
        dcp_manager.write_dcp(dcp_data)
        return True
        
    except Exception as e:
        logger.error(f"Failed to update DCP section {section_path}: {e}")
        return False