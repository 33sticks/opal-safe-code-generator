"""Brand templates API endpoints."""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status

from app.schemas.brand_template import TemplateSummary
from app.services.brand_template_service import BrandTemplateService

router = APIRouter()

# Initialize service (loads templates on import)
template_service = BrandTemplateService()


@router.get("/", response_model=List[TemplateSummary], status_code=status.HTTP_200_OK)
async def list_templates():
    """
    Get list of all available brand templates.
    
    Returns:
        List of template summaries with name, description, and platform.
    """
    templates = template_service.get_available_templates()
    return templates


@router.get("/{template_name}", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def get_template(template_name: str):
    """
    Get full template details by name.
    
    Args:
        template_name: Name of the template (case-insensitive).
    
    Returns:
        Full template JSON object.
    
    Raises:
        HTTPException: 404 if template not found.
    """
    try:
        template = template_service.get_template_by_name(template_name)
        return template
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

