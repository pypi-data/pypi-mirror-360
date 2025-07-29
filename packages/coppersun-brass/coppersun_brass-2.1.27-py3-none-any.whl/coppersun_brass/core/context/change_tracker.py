"""DCP Change Tracking System with Agent Provenance"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class DCPChangeTracker:
    """Tracks all changes to DCP with full agent provenance"""
    
    def __init__(self, dcp_manager):
        self.dcp_manager = dcp_manager
        self.change_log_path = Path(dcp_manager.project_root) / "dcp_changes.json"
        self.change_log = self._load_changelog()
        
    def _load_changelog(self) -> List[Dict]:
        """Load existing changelog or create new"""
        if self.change_log_path.exists():
            try:
                with open(self.change_log_path, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def track_change(self, operation: str, field_path: str, 
                    old_value: Any, new_value: Any, 
                    agent_id: str, operation_id: Optional[str] = None):
        """Log changes with full agent provenance
        
        Args:
            operation: Type of operation (create|update|delete)
            field_path: Dot-separated path to changed field
            old_value: Previous value (None for create)
            new_value: New value (None for delete)
            agent_id: Agent making the change (watch|scout|claude|human)
            operation_id: Optional operation ID for grouping changes
        """
        change_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "field_path": field_path,
            "old_value": old_value,
            "new_value": new_value,
            "agent_id": agent_id,
            "operation_id": operation_id or str(uuid.uuid4()),
            "dcp_version": self.dcp_manager.get_current_version()
        }
        
        # Store per-agent for future rollback support
        self.change_log.append(change_entry)
        self._persist_changelog()
        
        return change_entry["operation_id"]
    
    def _persist_changelog(self):
        """Save changelog to disk"""
        # Keep only last 1000 changes to prevent unbounded growth
        if len(self.change_log) > 1000:
            self.change_log = self.change_log[-1000:]
        
        with open(self.change_log_path, 'w') as f:
            json.dump(self.change_log, f, indent=2)
    
    def get_changes_by_agent(self, agent_id: str, limit: int = 50) -> List[Dict]:
        """Get recent changes made by specific agent"""
        agent_changes = [c for c in self.change_log if c["agent_id"] == agent_id]
        return agent_changes[-limit:]
    
    def get_changes_by_operation(self, operation_id: str) -> List[Dict]:
        """Get all changes from a specific operation"""
        return [c for c in self.change_log if c["operation_id"] == operation_id]
    
    def get_field_history(self, field_path: str) -> List[Dict]:
        """Get complete history of changes to a specific field"""
        return [c for c in self.change_log if c["field_path"] == field_path]
    
    def generate_changelog_report(self, start_version: Optional[str] = None, 
                                 end_version: Optional[str] = None) -> str:
        """Generate human-readable changelog between versions"""
        changes = self.change_log
        
        if start_version:
            changes = [c for c in changes if c["dcp_version"] >= start_version]
        if end_version:
            changes = [c for c in changes if c["dcp_version"] <= end_version]
        
        if not changes:
            return "No changes found in specified range"
        
        report = f"# DCP Changelog\n\n"
        report += f"Period: {changes[0]['timestamp']} to {changes[-1]['timestamp']}\n"
        report += f"Total changes: {len(changes)}\n\n"
        
        # Group by agent
        by_agent = {}
        for change in changes:
            agent = change["agent_id"]
            if agent not in by_agent:
                by_agent[agent] = []
            by_agent[agent].append(change)
        
        for agent, agent_changes in by_agent.items():
            report += f"\n## {agent.title()} Agent ({len(agent_changes)} changes)\n"
            for c in agent_changes[-10:]:  # Show last 10 per agent
                op = c["operation"]
                field = c["field_path"]
                time = c["timestamp"].split("T")[1].split(".")[0]
                report += f"- [{time}] {op} {field}\n"
        
        return report
