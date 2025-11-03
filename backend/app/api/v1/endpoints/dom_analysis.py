"""DOM Analysis API endpoints."""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.core.auth import get_current_user_dependency
from app.models.user import User
from app.models.brand import Brand
from app.schemas.dom_analysis import DomAnalysisRequest, DomAnalysisResult
from app.services.dom_analysis_service import DomAnalysisService

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize service
dom_analysis_service = DomAnalysisService()


@router.post("/", response_model=DomAnalysisResult, status_code=status.HTTP_200_OK)
async def analyze_dom(
    request: DomAnalysisRequest,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze HTML and return AI-generated selector suggestions with relationships.
    
    This endpoint is used during brand onboarding when admins paste HTML snippets.
    
    Args:
        request: Request body containing HTML, page_type, and optional brand_id
        current_user: Authenticated user (from dependency)
        db: Database session
        
    Returns:
        DomAnalysisResult with selectors, relationships, patterns, and recommendations
        
    Raises:
        HTTPException: 
            - 400 for invalid HTML or missing required fields
            - 404 if brand_id provided but brand not found
            - 500 for API/parsing errors
    """
    try:
        # Get brand name if brand_id is provided
        brand_name = ""
        if request.brand_id:
            brand_result = await db.execute(
                select(Brand).where(Brand.id == request.brand_id)
            )
            brand = brand_result.scalar_one_or_none()
            
            if not brand:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Brand with id {request.brand_id} not found"
                )
            
            brand_name = brand.name
            logger.info(f"DOM analysis for brand: {brand_name} (id: {request.brand_id})")
        
        # Call service to analyze HTML
        logger.info(f"Starting DOM analysis for page_type: {request.page_type}")
        result = await dom_analysis_service.analyze_html(
            html=request.html,
            page_type=request.page_type,
            brand_name=brand_name
        )
        
        logger.info(
            f"DOM analysis completed successfully. "
            f"Found {len(result.selectors)} selectors, {len(result.patterns)} patterns"
        )
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except ValueError as e:
        # Invalid HTML or validation errors
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # API/parsing errors or other unexpected errors
        logger.error(f"DOM analysis error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze HTML: {str(e)}"
        )

