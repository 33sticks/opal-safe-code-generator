"""Tests for Opal API endpoints."""
import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient
from fastapi import status
from anthropic import APIError

from app.models.brand import Brand
from app.models.template import Template
from app.models.dom_selector import DOMSelector
from app.models.code_rule import CodeRule
from app.models.enums import TestType, PageType, RuleType, SelectorStatus
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class TestDiscoveryEndpoint:
    """Tests for GET /api/v1/opal/discovery"""

    async def test_discovery_returns_manifest(self, test_client: AsyncClient):
        """Test discovery endpoint returns valid Opal manifest."""
        response = await test_client.get("/api/v1/opal/discovery")
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "name" in data
        assert "description" in data
        assert "functions" in data
        assert isinstance(data["functions"], list)
        
        # Check function definition
        assert len(data["functions"]) > 0
        func = data["functions"][0]
        assert func["name"] == "generate_code"
        assert func["http_method"] == "POST"  # Important: uses http_method, not method
        assert func["endpoint"] == "/api/v1/opal/generate-code"
        assert "parameters" in func
        assert len(func["parameters"]) == 3
        
        # Check parameters
        param_names = [p["name"] for p in func["parameters"]]
        assert "brand_name" in param_names
        assert "test_type" in param_names
        assert "test_description" in param_names


class TestGenerateCodeEndpoint:
    """Tests for POST /api/v1/opal/generate-code"""

    async def test_generate_code_missing_brand(self, test_client: AsyncClient):
        """Test generate-code with missing brand_name."""
        response = await test_client.post(
            "/api/v1/opal/generate-code",
            json={
                "parameters": {
                    "test_type": "checkout",
                    "test_description": "Test description"
                }
            }
        )
        assert response.status_code == 422
        assert "brand_name" in response.json()["detail"].lower()

    async def test_generate_code_missing_test_type(self, test_client: AsyncClient):
        """Test generate-code with missing test_type."""
        response = await test_client.post(
            "/api/v1/opal/generate-code",
            json={
                "parameters": {
                    "brand_name": "VANS",
                    "test_description": "Test description"
                }
            }
        )
        assert response.status_code == 422
        assert "test_type" in response.json()["detail"].lower()

    async def test_generate_code_missing_description(self, test_client: AsyncClient):
        """Test generate-code with missing test_description."""
        response = await test_client.post(
            "/api/v1/opal/generate-code",
            json={
                "parameters": {
                    "brand_name": "VANS",
                    "test_type": "checkout"
                }
            }
        )
        assert response.status_code == 422
        assert "test_description" in response.json()["detail"].lower()

    async def test_generate_code_brand_not_found(self, test_client: AsyncClient):
        """Test generate-code with non-existent brand."""
        response = await test_client.post(
            "/api/v1/opal/generate-code",
            json={
                "parameters": {
                    "brand_name": "NonExistentBrand",
                    "test_type": "checkout",
                    "test_description": "Test description"
                }
            }
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_generate_code_invalid_test_type(self, test_client: AsyncClient, test_db: AsyncSession):
        """Test generate-code with invalid test_type."""
        # Create a brand first
        unique_name = f"Test Brand {uuid.uuid4().hex[:8]}"
        brand = Brand(
            name=unique_name,
            domain=f"test{uuid.uuid4().hex[:8]}.com",
            status="active"
        )
        test_db.add(brand)
        await test_db.commit()
        
        response = await test_client.post(
            "/api/v1/opal/generate-code",
            json={
                "parameters": {
                    "brand_name": unique_name,
                    "test_type": "invalid_type",
                    "test_description": "Test description"
                }
            }
        )
        assert response.status_code == 422
        assert "invalid test_type" in response.json()["detail"].lower()

    @patch('app.api.v1.opal.CodeGeneratorService')
    async def test_generate_code_success(
        self, 
        mock_service_class, 
        test_client: AsyncClient, 
        test_db: AsyncSession
    ):
        """Test successful code generation."""
        # Create test data
        unique_name = f"Test Brand {uuid.uuid4().hex[:8]}"
        brand = Brand(
            name=unique_name,
            domain=f"test{uuid.uuid4().hex[:8]}.com",
            status="active"
        )
        test_db.add(brand)
        await test_db.flush()
        
        template = Template(
            brand_id=brand.id,
            test_type=TestType.CHECKOUT,
            template_code="// Template code\nfunction test() { console.log('test'); }",
            is_active=True
        )
        test_db.add(template)
        
        selector = DOMSelector(
            brand_id=brand.id,
            page_type=PageType.CHECKOUT,
            selector=".checkout-button",
            description="Checkout button",
            status=SelectorStatus.ACTIVE
        )
        test_db.add(selector)
        
        rule = CodeRule(
            brand_id=brand.id,
            rule_type=RuleType.FORBIDDEN_PATTERN,
            rule_content="eval(",
            priority=1
        )
        test_db.add(rule)
        await test_db.commit()
        
        # Mock Claude service response
        mock_service = MagicMock()
        mock_service.generate_code = AsyncMock(return_value={
            "generated_code": "// Generated code\nconst button = document.querySelector('.checkout-button');",
            "confidence_score": 0.85,
            "implementation_notes": "- Use the .checkout-button selector\n- Follows brand guidelines",
            "testing_checklist": "- Verify button behavior\n- Test on mobile"
        })
        mock_service_class.return_value = mock_service
        
        # Make request
        response = await test_client.post(
            "/api/v1/opal/generate-code",
            json={
                "parameters": {
                    "brand_name": unique_name,
                    "test_type": "checkout",
                    "test_description": "Change checkout button color to red"
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "generated_code" in data
        assert "confidence_score" in data
        assert "implementation_notes" in data
        assert "testing_checklist" in data
        assert data["confidence_score"] == 0.85
        assert ".checkout-button" in data["generated_code"]

    @patch('app.api.v1.opal.CodeGeneratorService')
    async def test_generate_code_saves_to_database(
        self,
        mock_service_class,
        test_client: AsyncClient,
        test_db: AsyncSession
    ):
        """Test that generated code is saved to database."""
        # Create test data
        unique_name = f"Test Brand {uuid.uuid4().hex[:8]}"
        brand = Brand(
            name=unique_name,
            domain=f"test{uuid.uuid4().hex[:8]}.com",
            status="active"
        )
        test_db.add(brand)
        await test_db.flush()
        
        template = Template(
            brand_id=brand.id,
            test_type=TestType.CHECKOUT,
            template_code="// Template",
            is_active=True
        )
        test_db.add(template)
        await test_db.commit()
        
        # Mock Claude service
        mock_service = MagicMock()
        mock_service.generate_code = AsyncMock(return_value={
            "generated_code": "// Test code",
            "confidence_score": 0.9,
            "implementation_notes": "Notes",
            "testing_checklist": "Checklist"
        })
        mock_service_class.return_value = mock_service
        
        # Make request
        response = await test_client.post(
            "/api/v1/opal/generate-code",
            json={
                "parameters": {
                    "brand_name": unique_name,
                    "test_type": "checkout",
                    "test_description": "Test description"
                }
            }
        )
        
        assert response.status_code == 200
        
        # Verify code was saved to database
        from app.models.generated_code import GeneratedCode
        result = await test_db.execute(
            select(GeneratedCode).where(GeneratedCode.brand_id == brand.id)
        )
        saved_code = result.scalar_one_or_none()
        assert saved_code is not None
        assert saved_code.generated_code == "// Test code"
        assert saved_code.confidence_score == 0.9

    @patch('app.api.v1.opal.CodeGeneratorService')
    async def test_generate_code_case_insensitive_brand(
        self,
        mock_service_class,
        test_client: AsyncClient,
        test_db: AsyncSession
    ):
        """Test that brand lookup is case-insensitive."""
        unique_name = "TestBrand"
        brand = Brand(
            name=unique_name,
            domain="test.com",
            status="active"
        )
        test_db.add(brand)
        await test_db.flush()
        
        template = Template(
            brand_id=brand.id,
            test_type=TestType.CHECKOUT,
            template_code="// Template",
            is_active=True
        )
        test_db.add(template)
        await test_db.commit()
        
        # Mock Claude service
        mock_service = MagicMock()
        mock_service.generate_code = AsyncMock(return_value={
            "generated_code": "// Code",
            "confidence_score": 0.8,
            "implementation_notes": "Notes",
            "testing_checklist": "Checklist"
        })
        mock_service_class.return_value = mock_service
        
        # Make request with different case
        response = await test_client.post(
            "/api/v1/opal/generate-code",
            json={
                "parameters": {
                    "brand_name": "testbrand",  # lowercase
                    "test_type": "checkout",
                    "test_description": "Test"
                }
            }
        )
        
        assert response.status_code == 200

    @patch('app.api.v1.opal.CodeGeneratorService')
    async def test_generate_code_filters_templates_by_type(
        self,
        mock_service_class,
        test_client: AsyncClient,
        test_db: AsyncSession
    ):
        """Test that only templates matching test_type are used."""
        unique_name = f"Test Brand {uuid.uuid4().hex[:8]}"
        brand = Brand(
            name=unique_name,
            domain="test.com",
            status="active"
        )
        test_db.add(brand)
        await test_db.flush()
        
        # Create templates for different test types
        checkout_template = Template(
            brand_id=brand.id,
            test_type=TestType.CHECKOUT,
            template_code="// Checkout template",
            is_active=True
        )
        pdp_template = Template(
            brand_id=brand.id,
            test_type=TestType.PDP,
            template_code="// PDP template",
            is_active=True
        )
        test_db.add(checkout_template)
        test_db.add(pdp_template)
        await test_db.commit()
        
        # Mock Claude service to capture what was passed
        mock_service = MagicMock()
        call_args = {}
        
        async def mock_generate(*args, **kwargs):
            call_args['templates'] = kwargs.get('templates', [])
            return {
                "generated_code": "// Code",
                "confidence_score": 0.8,
                "implementation_notes": "Notes",
                "testing_checklist": "Checklist"
            }
        
        mock_service.generate_code = AsyncMock(side_effect=mock_generate)
        mock_service_class.return_value = mock_service
        
        # Request checkout test
        response = await test_client.post(
            "/api/v1/opal/generate-code",
            json={
                "parameters": {
                    "brand_name": unique_name,
                    "test_type": "checkout",
                    "test_description": "Test"
                }
            }
        )
        
        assert response.status_code == 200
        # Verify only checkout template was passed
        templates_passed = call_args.get('templates', [])
        assert len(templates_passed) == 1
        assert templates_passed[0]['test_type'] == 'checkout'

    @patch('app.api.v1.opal.CodeGeneratorService')
    async def test_generate_code_filters_selectors_by_page_type(
        self,
        mock_service_class,
        test_client: AsyncClient,
        test_db: AsyncSession
    ):
        """Test that only selectors matching page_type are used."""
        unique_name = f"Test Brand {uuid.uuid4().hex[:8]}"
        brand = Brand(
            name=unique_name,
            domain="test.com",
            status="active"
        )
        test_db.add(brand)
        await test_db.flush()
        
        # Create selectors for different page types
        checkout_selector = DOMSelector(
            brand_id=brand.id,
            page_type=PageType.CHECKOUT,
            selector=".checkout-button",
            status=SelectorStatus.ACTIVE
        )
        pdp_selector = DOMSelector(
            brand_id=brand.id,
            page_type=PageType.PDP,
            selector=".product-title",
            status=SelectorStatus.ACTIVE
        )
        test_db.add(checkout_selector)
        test_db.add(pdp_selector)
        
        template = Template(
            brand_id=brand.id,
            test_type=TestType.CHECKOUT,
            template_code="// Template",
            is_active=True
        )
        test_db.add(template)
        await test_db.commit()
        
        # Mock Claude service
        call_args = {}
        
        async def mock_generate(*args, **kwargs):
            call_args['selectors'] = kwargs.get('selectors', [])
            return {
                "generated_code": "// Code",
                "confidence_score": 0.8,
                "implementation_notes": "Notes",
                "testing_checklist": "Checklist"
            }
        
        mock_service = MagicMock()
        mock_service.generate_code = AsyncMock(side_effect=mock_generate)
        mock_service_class.return_value = mock_service
        
        # Request checkout test
        response = await test_client.post(
            "/api/v1/opal/generate-code",
            json={
                "parameters": {
                    "brand_name": unique_name,
                    "test_type": "checkout",
                    "test_description": "Test"
                }
            }
        )
        
        assert response.status_code == 200
        # Verify only checkout selector was passed
        selectors_passed = call_args.get('selectors', [])
        assert len(selectors_passed) == 1
        assert ".checkout-button" in selectors_passed[0]['selector']

    @patch('app.api.v1.opal.CodeGeneratorService')
    async def test_generate_code_claude_api_error(
        self,
        mock_service_class,
        test_client: AsyncClient,
        test_db: AsyncSession
    ):
        """Test error handling when Claude API fails."""
        unique_name = f"Test Brand {uuid.uuid4().hex[:8]}"
        brand = Brand(
            name=unique_name,
            domain="test.com",
            status="active"
        )
        test_db.add(brand)
        await test_db.flush()
        
        template = Template(
            brand_id=brand.id,
            test_type=TestType.CHECKOUT,
            template_code="// Template",
            is_active=True
        )
        test_db.add(template)
        await test_db.commit()
        
        # Mock Claude service to raise error
        mock_service = MagicMock()
        mock_service.generate_code = AsyncMock(side_effect=Exception("Claude API error"))
        mock_service_class.return_value = mock_service
        
        response = await test_client.post(
            "/api/v1/opal/generate-code",
            json={
                "parameters": {
                    "brand_name": unique_name,
                    "test_type": "checkout",
                    "test_description": "Test"
                }
            }
        )
        
        assert response.status_code == 500
        assert "failed" in response.json()["detail"].lower()

    async def test_generate_code_missing_api_key(
        self,
        test_client: AsyncClient,
        test_db: AsyncSession,
        monkeypatch
    ):
        """Test error when ANTHROPIC_API_KEY is missing."""
        # Remove API key from settings
        monkeypatch.setenv("ANTHROPIC_API_KEY", "")
        
        unique_name = f"Test Brand {uuid.uuid4().hex[:8]}"
        brand = Brand(
            name=unique_name,
            domain="test.com",
            status="active"
        )
        test_db.add(brand)
        await test_db.flush()
        
        template = Template(
            brand_id=brand.id,
            test_type=TestType.CHECKOUT,
            template_code="// Template",
            is_active=True
        )
        test_db.add(template)
        await test_db.commit()
        
        # Reload config to pick up missing API key
        from app.config import settings
        # This will fail when CodeGeneratorService tries to initialize
        # We need to patch it to catch the error
        with patch('app.api.v1.opal.CodeGeneratorService') as mock_service_class:
            mock_service_class.side_effect = ValueError("ANTHROPIC_API_KEY is not set")
            
            response = await test_client.post(
                "/api/v1/opal/generate-code",
                json={
                    "parameters": {
                        "brand_name": unique_name,
                        "test_type": "checkout",
                        "test_description": "Test"
                    }
                }
            )
            
            assert response.status_code == 500

