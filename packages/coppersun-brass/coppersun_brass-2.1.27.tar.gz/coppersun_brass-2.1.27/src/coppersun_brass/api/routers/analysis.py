"""
Analysis API Router

General Staff G2 Role: Intelligence Analysis Interface
Endpoints for code analysis operations
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

from coppersun_brass.api.auth import get_current_user, get_api_key_info
from coppersun_brass.agents.scout import ScoutAgent
from coppersun_brass.core.context.dcp_manager import DCPManager
from coppersun_brass.core.security import validate_path, validate_string, InputValidationError

logger = logging.getLogger(__name__)

router = APIRouter()


class AnalysisRequest(BaseModel):
    """Request model for analysis"""
    path: str = Field(..., description="Path to analyze (file or directory)")
    recursive: bool = Field(True, description="Analyze subdirectories")
    file_types: Optional[List[str]] = Field(None, description="Filter by file extensions")
    max_files: Optional[int] = Field(1000, description="Maximum files to analyze")
    
    class Config:
        schema_extra = {
            "example": {
                "path": "/project/src",
                "recursive": True,
                "file_types": [".py", ".js"],
                "max_files": 500
            }
        }


class AnalysisResponse(BaseModel):
    """Response model for analysis"""
    request_id: str
    status: str
    path: str
    files_analyzed: int
    issues_found: int
    patterns_detected: int
    duration_ms: float
    summary: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "request_id": "req_1234567890",
                "status": "completed",
                "path": "/project/src",
                "files_analyzed": 150,
                "issues_found": 23,
                "patterns_detected": 5,
                "duration_ms": 2345.67,
                "summary": {
                    "high_priority": 3,
                    "medium_priority": 12,
                    "low_priority": 8
                }
            }
        }


@router.post("/", 
            response_model=AnalysisResponse,
            summary="Analyze code",
            description="Perform comprehensive code analysis on specified path")
async def analyze_code(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    auth: Dict = Depends(get_current_user)
) -> AnalysisResponse:
    """
    Analyze code at specified path
    
    Requires authentication with 'analyze' scope.
    """
    # Check scope
    if 'analyze' not in auth.get('scopes', []) and 'admin' not in auth.get('scopes', []):
        raise HTTPException(
            status_code=403,
            detail="Requires 'analyze' scope"
        )
    
    # Validate and sanitize path
    try:
        target_path = validate_path(request.path, must_exist=True, allow_outside_project=False)
    except InputValidationError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid path: {str(e)}"
        )
    
    # Initialize Scout agent
    scout = ScoutAgent()
    
    try:
        # Perform analysis
        import time
        start_time = time.time()
        
        findings = await scout.analyze_path(
            target_path,
            recursive=request.recursive,
            file_types=request.file_types,
            max_files=request.max_files
        )
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Summarize findings
        summary = _summarize_findings(findings)
        
        # Log to DCP
        dcp_manager = DCPManager()
        dcp_manager.add_observation(
            'api_analysis_completed',
            {
                'user_id': auth['user_id'],
                'path': request.path,
                'files_analyzed': summary['files_analyzed'],
                'issues_found': summary['issues_found'],
                'duration_ms': duration_ms
            },
            source_agent='api',
            priority=65
        )
        
        return AnalysisResponse(
            request_id=f"req_{int(time.time() * 1000)}",
            status="completed",
            path=request.path,
            files_analyzed=summary['files_analyzed'],
            issues_found=summary['issues_found'],
            patterns_detected=summary['patterns_detected'],
            duration_ms=duration_ms,
            summary=summary['priority_breakdown']
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/status/{request_id}",
           summary="Get analysis status",
           description="Check status of ongoing analysis")
async def get_analysis_status(
    request_id: str,
    auth: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get status of analysis request"""
    # TODO: Implement async analysis tracking
    return {
        "request_id": request_id,
        "status": "completed",
        "message": "Analysis tracking not yet implemented"
    }


@router.get("/history",
           summary="Get analysis history",
           description="Get history of previous analyses")
async def get_analysis_history(
    limit: int = 10,
    offset: int = 0,
    auth: Dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get user's analysis history"""
    # Get from DCP
    dcp_manager = DCPManager()
    
    # Filter observations by user
    observations = dcp_manager.get_observations(
        filters={'type': 'api_analysis_completed'}
    )
    
    # Filter by user
    user_analyses = [
        obs for obs in observations
        if obs.get('data', {}).get('user_id') == auth['user_id']
    ]
    
    # Sort by timestamp
    user_analyses.sort(
        key=lambda x: x.get('timestamp', ''),
        reverse=True
    )
    
    # Apply pagination
    paginated = user_analyses[offset:offset + limit]
    
    return paginated


def _summarize_findings(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Summarize analysis findings"""
    summary = {
        'files_analyzed': len(findings),
        'issues_found': 0,
        'patterns_detected': 0,
        'priority_breakdown': {
            'high': 0,
            'medium': 0,
            'low': 0
        }
    }
    
    for finding in findings:
        issues = finding.get('issues', [])
        summary['issues_found'] += len(issues)
        
        patterns = finding.get('patterns', [])
        summary['patterns_detected'] += len(patterns)
        
        # Count by priority
        for issue in issues:
            priority = issue.get('priority', 'low')
            if priority in summary['priority_breakdown']:
                summary['priority_breakdown'][priority] += 1
    
    return summary