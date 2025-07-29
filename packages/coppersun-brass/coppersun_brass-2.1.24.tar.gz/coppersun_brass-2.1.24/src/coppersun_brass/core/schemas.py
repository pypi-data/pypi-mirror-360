"""
Core data schemas for Copper Alloy Brass agents
Standardized output formats for all agents
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

@dataclass
class Finding:
    """Represents an issue found during analysis"""
    type: str  # "security", "performance", "bug", "improvement", "warning"
    severity: str  # "critical", "high", "medium", "low"
    location: str  # file path, line number, or function name
    description: str
    evidence: List[str] = field(default_factory=list)
    confidence: float = 1.0

@dataclass
class Recommendation:
    """Represents an actionable recommendation"""
    priority: str  # "high", "medium", "low"
    action: str
    rationale: str
    estimated_effort: str  # "low", "medium", "high"
    category: str = "general"

@dataclass
class ProjectContext:
    """Context information about the project being analyzed"""
    name: str
    path: str
    total_files: int
    changed_files: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ReportMetadata:
    """Metadata about the analysis process"""
    agent_name: str
    processing_time: float
    tokens_used: Optional[int] = None
    model_used: str = "unknown"
    version: str = "1.0"

@dataclass
class AgentReport:
    """Standardized report format for all Copper Alloy Brass agents"""
    agent_name: str
    timestamp: datetime
    project_context: ProjectContext
    findings: List[Finding] = field(default_factory=list)
    recommendations: List[Recommendation] = field(default_factory=list)
    metadata: Optional[ReportMetadata] = None
    raw_data: Optional[Dict] = None
    
    def to_google_docs_format(self) -> str:
        """Format compatible with existing Google Docs integration"""
        content = "BRASS ANALYSIS REPORT\n"
        content += "=" * 50 + "\n\n"
        content += f"Project: {self.project_context.name}\n"
        content += f"Timestamp: {self.timestamp.isoformat()}\n"
        content += f"Total Files: {self.project_context.total_files}\n\n"
        
        if self.findings:
            content += "🏥 HEALTH CHECK\n"
            content += "-" * 20 + "\n"
            for finding in self.findings:
                content += f"  • {finding.description}\n"
            content += "\n"
        
        if self.recommendations:
            content += "🎯 NEXT ACTIONS\n"
            content += "-" * 20 + "\n"
            for i, rec in enumerate(self.recommendations, 1):
                content += f"{i}. {rec.action}\n"
        
        return content