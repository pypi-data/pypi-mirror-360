"""
Patterns API Router

General Staff G2 Role: Pattern Intelligence Interface
Endpoints for accessing learned patterns
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from coppersun_brass.api.auth import get_current_user
from coppersun_brass.core.learning.codebase_learning_coordinator import CodebaseLearningCoordinator
from coppersun_brass.core.context.dcp_manager import DCPManager

logger = logging.getLogger(__name__)

router = APIRouter()


class Pattern(BaseModel):
    """Pattern model"""
    id: str
    name: str
    type: str
    description: str
    confidence: float
    success_rate: float
    sample_size: int
    context: Dict[str, Any]
    last_updated: str
    
    class Config:
        schema_extra = {
            "example": {
                "id": "pattern_001",
                "name": "Python test file pattern",
                "type": "file_structure",
                "description": "Test files follow test_*.py naming convention",
                "confidence": 0.95,
                "success_rate": 0.92,
                "sample_size": 150,
                "context": {"language": "python", "project_type": "library"},
                "last_updated": "2025-06-11T10:00:00Z"
            }
        }


class PatternResponse(BaseModel):
    """Response for pattern queries"""
    patterns: List[Pattern]
    total: int
    offset: int
    limit: int
    filters_applied: Dict[str, Any]


@router.get("/",
           response_model=PatternResponse,
           summary="Get patterns",
           description="Get learned patterns with optional filtering")
async def get_patterns(
    pattern_type: Optional[str] = Query(None, description="Filter by pattern type"),
    min_confidence: float = Query(0.6, description="Minimum confidence threshold"),
    language: Optional[str] = Query(None, description="Filter by language"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    offset: int = Query(0, ge=0, description="Result offset"),
    auth: Dict = Depends(get_current_user)
) -> PatternResponse:
    """
    Get learned patterns
    
    Requires authentication with 'patterns' scope.
    """
    # Check scope
    if 'patterns' not in auth.get('scopes', []) and 'admin' not in auth.get('scopes', []):
        raise HTTPException(
            status_code=403,
            detail="Requires 'patterns' scope"
        )
    
    try:
        # Initialize pure Python learning coordinator
        coordinator = CodebaseLearningCoordinator(dcp_path=None)
        
        # Build context filter
        context_filter = {}
        if language:
            context_filter['language'] = language
        
        # Get patterns from pure Python learning system
        learning_status = coordinator.get_learning_status()
        all_patterns = learning_status.get('patterns_learned', [])
        
        # Apply additional filters
        filtered_patterns = []
        for pattern in all_patterns:
            # Type filter
            if pattern_type and pattern.pattern_type != pattern_type:
                continue
            
            # Confidence filter
            if pattern.confidence < min_confidence:
                continue
                
            filtered_patterns.append(pattern)
        
        # Sort by confidence
        filtered_patterns.sort(key=lambda p: p.confidence, reverse=True)
        
        # Apply pagination
        total = len(filtered_patterns)
        paginated = filtered_patterns[offset:offset + limit]
        
        # Convert to response format
        patterns = []
        for p in paginated:
            patterns.append(Pattern(
                id=p.id,
                name=p.pattern_name,
                type=p.pattern_type,
                description=p.description or '',
                confidence=p.confidence,
                success_rate=p.success_rate,
                sample_size=p.sample_size,
                context=p.context_dimensions or {},
                last_updated=p.last_updated.isoformat() if p.last_updated else ''
            ))
        
        return PatternResponse(
            patterns=patterns,
            total=total,
            offset=offset,
            limit=limit,
            filters_applied={
                'pattern_type': pattern_type,
                'min_confidence': min_confidence,
                'language': language
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get patterns: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get patterns: {str(e)}"
        )


@router.get("/types",
           summary="Get pattern types",
           description="Get available pattern types")
async def get_pattern_types(
    auth: Dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get available pattern types"""
    return [
        {
            "type": "task_success",
            "description": "Patterns related to task completion success rates",
            "example": "Python tasks have 85% success rate"
        },
        {
            "type": "time_estimation",
            "description": "Patterns in time estimation accuracy",
            "example": "Frontend tasks typically take 1.5x estimated time"
        },
        {
            "type": "failure_risk",
            "description": "Patterns indicating high failure risk",
            "example": "Complex database migrations have 40% failure rate"
        },
        {
            "type": "file_structure",
            "description": "Patterns in project file organization",
            "example": "Test files follow test_*.py convention"
        },
        {
            "type": "code_quality",
            "description": "Patterns in code quality metrics",
            "example": "Files over 500 lines have higher bug density"
        }
    ]


@router.get("/{pattern_id}",
           response_model=Pattern,
           summary="Get pattern details",
           description="Get detailed information about a specific pattern")
async def get_pattern_details(
    pattern_id: str,
    auth: Dict = Depends(get_current_user)
) -> Pattern:
    """Get detailed pattern information"""
    # TODO: Implement pattern lookup by ID
    # For now, return example
    return Pattern(
        id=pattern_id,
        name="Example Pattern",
        type="task_success",
        description="This is an example pattern",
        confidence=0.85,
        success_rate=0.90,
        sample_size=100,
        context={"language": "python"},
        last_updated=datetime.utcnow().isoformat()
    )


@router.post("/extract",
            summary="Extract new patterns",
            description="Trigger pattern extraction from recent data")
async def extract_patterns(
    lookback_days: int = Query(90, description="Days to analyze"),
    min_samples: int = Query(5, description="Minimum samples required"),
    auth: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Trigger pattern extraction
    
    Requires 'admin' scope.
    """
    # Check admin scope
    if 'admin' not in auth.get('scopes', []):
        raise HTTPException(
            status_code=403,
            detail="Requires 'admin' scope"
        )
    
    try:
        # Initialize pure Python learning coordinator
        coordinator = CodebaseLearningCoordinator(dcp_path=None)
        
        # Extract patterns using pure Python learning system
        import time
        start_time = time.time()
        
        # Run learning cycle to extract new patterns
        learning_result = await coordinator.run_learning_cycle(force=True)
        new_patterns = learning_result.get('phases', {}).get('codebase_analysis', {}).get('patterns_learned', 0)
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Log to DCP
        dcp_manager = DCPManager()
        dcp_manager.add_observation(
            'api_pattern_extraction',
            {
                'user_id': auth['user_id'],
                'lookback_days': lookback_days,
                'min_samples': min_samples,
                'patterns_extracted': len(new_patterns),
                'duration_ms': duration_ms
            },
            source_agent='api',
            priority=70
        )
        
        return {
            "status": "success",
            "patterns_extracted": len(new_patterns),
            "duration_ms": duration_ms,
            "message": f"Extracted {len(new_patterns)} new patterns"
        }
        
    except Exception as e:
        logger.error(f"Pattern extraction failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Pattern extraction failed: {str(e)}"
        )