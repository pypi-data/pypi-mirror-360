"""Agent permission system for DCP field access control"""

# Agent permission configuration
AGENT_PERMISSIONS = {
    "claude": {
        "can_edit": ["priority", "status", "claude_annotation", "effectiveness_score"],
        "can_create": [],
        "can_delete": []
    },
    "watch": {
        "can_edit": ["summary", "type"],
        "can_create": ["current_observations"],
        "can_delete": []
    },
    "scout": {
        "can_edit": ["priority", "summary"],
        "can_create": ["current_observations"],
        "can_delete": []
    },
    "human": {
        "can_edit": ["*"],  # Full access
        "can_create": ["*"],
        "can_delete": ["*"]
    }
}

def validate_agent_permission(agent_id, operation, field_path):
    """Check if agent has permission for operation
    
    Args:
        agent_id: Agent identifier (claude, watch, scout, human)
        operation: Operation type (edit, create, delete)
        field_path: Dot-separated path to field
        
    Returns:
        bool: True if permitted, False otherwise
    """
    permissions = AGENT_PERMISSIONS.get(agent_id, {})
    
    if operation == "edit":
        allowed_fields = permissions.get("can_edit", [])
    elif operation == "create":
        allowed_fields = permissions.get("can_create", [])
    elif operation == "delete":
        allowed_fields = permissions.get("can_delete", [])
    else:
        return False
    
    # Full access check
    if "*" in allowed_fields:
        return True
    
    # Check if any allowed field matches the path
    for allowed in allowed_fields:
        # Exact match or proper prefix with delimiter
        if field_path == allowed:
            return True
        # Check if it's a proper sub-field (not partial match)
        if field_path.startswith(allowed + "."):
            return True
            
    return False

def get_agent_permissions(agent_id):
    """Get all permissions for an agent"""
    return AGENT_PERMISSIONS.get(agent_id, {
        "can_edit": [],
        "can_create": [],
        "can_delete": []
    })
