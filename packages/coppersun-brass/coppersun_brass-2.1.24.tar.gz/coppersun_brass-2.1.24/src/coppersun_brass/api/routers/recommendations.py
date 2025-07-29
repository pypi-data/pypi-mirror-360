"""
Recommendations API Router

General Staff G3 Role: Operations Recommendations Interface
Endpoints for getting AI-powered recommendations
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from coppersun_brass.api.auth import get_current_user
from coppersun_brass.agents.strategist import StrategistAgent
from coppersun_brass.core.context.dcp_manager import DCPManager

logger = logging.getLogger(__name__)

router = APIRouter()


class RecommendationRequest(BaseModel):
    """Request model for recommendations"""
    context_type: str = Field(..., description="Type of recommendation needed")
    project_path: Optional[str] = Field(None, description="Project path for context")
    urgency: str = Field("normal", description="Urgency level: low, normal, high")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Additional constraints")
    
    class Config:
        schema_extra = {
            "example": {
                "context_type": "next_task",
                "project_path": "/project",
                "urgency": "high",
                "constraints": {
                    "max_time_hours": 4,
                    "skills": ["python", "testing"]
                }
            }
        }


class Recommendation(BaseModel):
    """Single recommendation"""
    id: str
    title: str
    description: str
    priority: float
    confidence: float
    reasoning: str
    estimated_time_hours: Optional[float]
    prerequisites: List[str]
    tags: List[str]


class RecommendationResponse(BaseModel):
    """Response model for recommendations"""
    request_id: str
    context_type: str
    recommendations: List[Recommendation]
    generated_at: str
    ai_confidence: float
    
    class Config:
        schema_extra = {
            "example": {
                "request_id": "req_1234567890",
                "context_type": "next_task",
                "recommendations": [
                    {
                        "id": "rec_001",
                        "title": "Add unit tests for auth module",
                        "description": "Current test coverage is 45%, should be >80%",
                        "priority": 0.85,
                        "confidence": 0.92,
                        "reasoning": "Critical module with low test coverage",
                        "estimated_time_hours": 3.5,
                        "prerequisites": ["pytest", "mock"],
                        "tags": ["testing", "quality"]
                    }
                ],
                "generated_at": "2025-06-11T10:00:00Z",
                "ai_confidence": 0.88
            }
        }


@router.post("/",
            response_model=RecommendationResponse,
            summary="Get recommendations",
            description="Get AI-powered recommendations based on context")
async def get_recommendations(
    request: RecommendationRequest,
    auth: Dict = Depends(get_current_user)
) -> RecommendationResponse:
    """
    Get AI-powered recommendations
    
    Requires authentication with 'recommendations' scope.
    """
    # Check scope
    if 'recommendations' not in auth.get('scopes', []) and 'admin' not in auth.get('scopes', []):
        raise HTTPException(
            status_code=403,
            detail="Requires 'recommendations' scope"
        )
    
    try:
        # Initialize strategist
        strategist = StrategistAgent()
        
        # Build context
        context = {
            'type': request.context_type,
            'urgency': request.urgency,
            'user_id': auth['user_id']
        }
        
        if request.project_path:
            context['project_path'] = request.project_path
        
        if request.constraints:
            context.update(request.constraints)
        
        # Get recommendations
        raw_recommendations = await strategist.get_recommendations(context)
        
        # Convert to response format
        recommendations = []
        for i, rec in enumerate(raw_recommendations[:10]):  # Top 10
            recommendations.append(Recommendation(
                id=f"rec_{i+1:03d}",
                title=rec.get('title', 'Untitled'),
                description=rec.get('description', ''),
                priority=rec.get('priority', 0.5),
                confidence=rec.get('confidence', 0.5),
                reasoning=rec.get('reasoning', 'Based on project analysis'),
                estimated_time_hours=rec.get('estimated_hours'),
                prerequisites=rec.get('prerequisites', []),
                tags=rec.get('tags', [])
            ))
        
        # Calculate overall confidence
        if recommendations:
            ai_confidence = sum(r.confidence for r in recommendations) / len(recommendations)
        else:
            ai_confidence = 0.0
        
        # Log to DCP
        dcp_manager = DCPManager()
        dcp_manager.add_observation(
            'api_recommendations_generated',
            {
                'user_id': auth['user_id'],
                'context_type': request.context_type,
                'recommendation_count': len(recommendations),
                'ai_confidence': ai_confidence
            },
            source_agent='api',
            priority=65
        )
        
        return RecommendationResponse(
            request_id=f"req_{int(datetime.now().timestamp() * 1000)}",
            context_type=request.context_type,
            recommendations=recommendations,
            generated_at=datetime.utcnow().isoformat(),
            ai_confidence=ai_confidence
        )
        
    except Exception as e:
        logger.error(f"Failed to generate recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.post("/{recommendation_id}/feedback",
            summary="Submit feedback",
            description="Submit feedback on a recommendation")
async def submit_feedback(
    recommendation_id: str,
    feedback: Dict[str, Any],
    auth: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Submit feedback on a recommendation"""
    # Log feedback to DCP
    dcp_manager = DCPManager()
    dcp_manager.add_observation(
        'recommendation_feedback',
        {
            'user_id': auth['user_id'],
            'recommendation_id': recommendation_id,
            'feedback': feedback,
            'timestamp': datetime.utcnow().isoformat()
        },
        source_agent='api',
        priority=70
    )
    
    return {
        "status": "success",
        "message": "Feedback recorded",
        "recommendation_id": recommendation_id
    }


@router.get("/types",
           summary="Get recommendation types",
           description="Get available recommendation context types")
async def get_recommendation_types(
    auth: Dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get available recommendation types"""
    return [
        {
            "type": "next_task",
            "description": "Recommendations for next development task",
            "requires_project": True
        },
        {
            "type": "code_improvement",
            "description": "Code quality and refactoring recommendations",
            "requires_project": True
        },
        {
            "type": "architecture",
            "description": "Architecture and design recommendations",
            "requires_project": True
        },
        {
            "type": "testing",
            "description": "Testing strategy recommendations",
            "requires_project": True
        },
        {
            "type": "performance",
            "description": "Performance optimization recommendations",
            "requires_project": True
        },
        {
            "type": "security",
            "description": "Security improvement recommendations",
            "requires_project": True
        }
    ]