"""Opal custom tool API endpoints for code generation."""
import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field

from app.api.deps import get_db
from app.models.brand import Brand
from app.models.template import Template
from app.models.dom_selector import DOMSelector
from app.models.code_rule import CodeRule
from app.models.generated_code import GeneratedCode
from app.models.enums import TestType, PageType, SelectorStatus, ValidationStatus
from app.core.exceptions import NotFoundException
from app.services.code_generator import CodeGeneratorService

logger = logging.getLogger(__name__)

router = APIRouter()


class OpalGenerateCodeRequest(BaseModel):
    """Request model for Opal generate-code endpoint."""
    parameters: Dict[str, Any] = Field(..., description="Parameters wrapped by Opal")


@router.get("/discovery", status_code=status.HTTP_200_OK)
async def discovery(request: Request):
    """
    Opal discovery endpoint that returns tool manifest.
    
    Returns the tool definition that Opal uses to register this custom tool.
    """
    base_url = str(request.base_url).rstrip('/')
    
    return {
        "name": "Opal Safe Code Generator",
        "description": "Generate safe, brand-specific A/B test code using admin-curated knowledge and Claude AI",
        "functions": [
            {
                "name": "generate_code",
                "description": "Generate safe JavaScript code for A/B tests using brand-specific templates and selectors",
                "http_method": "POST",
                "endpoint": f"{base_url}/api/v1/opal/generate-code",
                "parameters": [
                    {
                        "name": "brand_name",
                        "type": "string",
                        "description": "Brand name (e.g., 'VANS', 'Timberland')",
                        "required": True
                    },
                    {
                        "name": "test_type",
                        "type": "string",
                        "description": "Type of test (pdp, cart, checkout)",
                        "required": True
                    },
                    {
                        "name": "test_description",
                        "type": "string",
                        "description": "What the test should do (e.g., 'Change checkout button color to red')",
                        "required": True
                    }
                ]
            }
        ]
    }


@router.post("/generate-code", status_code=status.HTTP_200_OK)
async def generate_code(
    request: OpalGenerateCodeRequest = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Opal execution endpoint for code generation.
    
    Receives request from Opal with wrapped parameters, queries database for
    brand context, generates code using Claude, and saves result.
    """
    try:
        # Extract parameters (Opal wraps them)
        params = request.parameters
        
        # Validate required parameters
        brand_name = params.get("brand_name")
        test_type = params.get("test_type")
        test_description = params.get("test_description")
        
        if not brand_name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="brand_name parameter is required"
            )
        if not test_type:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="test_type parameter is required"
            )
        if not test_description:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="test_description parameter is required"
            )
        
        # Validate and convert test_type to enum
        try:
            test_type_enum = TestType(test_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid test_type: {test_type}. Must be one of: {[t.value for t in TestType]}"
            )
        
        # Query brand by name (case-insensitive)
        brand_result = await db.execute(
            select(Brand).where(func.lower(Brand.name) == func.lower(brand_name))
        )
        brand = brand_result.scalar_one_or_none()
        
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand '{brand_name}' not found"
            )
        
        # Query templates filtered by brand_id and test_type
        templates_result = await db.execute(
            select(Template).where(
                Template.brand_id == brand.id,
                Template.test_type == test_type_enum,
                Template.is_active == True
            )
        )
        templates = templates_result.scalars().all()
        
        # Query selectors filtered by brand_id and page_type
        # Map test_type to page_type (they share the same enum values)
        page_type_enum = PageType(test_type.lower())
        selectors_result = await db.execute(
            select(DOMSelector).where(
                DOMSelector.brand_id == brand.id,
                DOMSelector.page_type == page_type_enum,
                DOMSelector.status == SelectorStatus.ACTIVE
            )
        )
        selectors = selectors_result.scalars().all()
        
        # Query code rules filtered by brand_id
        rules_result = await db.execute(
            select(CodeRule).where(CodeRule.brand_id == brand.id)
        )
        rules = rules_result.scalars().all()
        
        # Prepare data for code generator
        brand_context = {
            "name": brand.name,
            "domain": brand.domain,
            "id": brand.id,
            "config": brand.config or {}  # Include brand config (may contain global_template)
        }
        
        templates_data = [
            {
                "test_type": t.test_type.value,
                "template_code": t.template_code,
                "description": t.description
            }
            for t in templates
        ]
        
        selectors_data = [
            {
                "selector": s.selector,
                "description": s.description
            }
            for s in selectors
        ]
        
        rules_data = [
            {
                "rule_type": r.rule_type.value,
                "rule_content": r.rule_content,
                "priority": r.priority
            }
            for r in rules
        ]
        
        # Generate code using Claude
        code_generator = CodeGeneratorService()
        result = await code_generator.generate_code(
            brand_context=brand_context,
            templates=templates_data,
            selectors=selectors_data,
            rules=rules_data,
            test_description=test_description
        )
        
        # Save to database
        generated_code_record = GeneratedCode(
            brand_id=brand.id,
            request_data=params,
            generated_code=result["generated_code"],
            confidence_score=result["confidence_score"],
            validation_status=ValidationStatus.PENDING
        )
        
        db.add(generated_code_record)
        await db.commit()
        await db.refresh(generated_code_record)
        
        logger.info(f"Generated code for brand {brand.name}, test_type {test_type}, ID: {generated_code_record.id}")
        
        # Return formatted response
        return {
            "generated_code": result["generated_code"],
            "confidence_score": result["confidence_score"],
            "implementation_notes": result["implementation_notes"],
            "testing_checklist": result["testing_checklist"]
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Value error in generate_code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error generating code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate code: {str(e)}"
        )

