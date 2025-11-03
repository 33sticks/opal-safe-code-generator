"""Tests for relationship-based DOM navigation in code generation."""
import pytest
import uuid
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brand import Brand
from app.models.dom_selector import DOMSelector
from app.models.enums import BrandStatus, PageType, SelectorStatus
from app.services.code_generator import CodeGeneratorService


class TestRelationshipNavigation:
    """Test relationship navigation in generated code."""
    
    @pytest.fixture
    def test_brand(self, test_db: AsyncSession):
        """Create a test brand."""
        unique_name = f"Relationship Test Brand {uuid.uuid4().hex[:8]}"
        brand = Brand(
            name=unique_name,
            domain=f"reltest{uuid.uuid4().hex[:8]}.com",
            status=BrandStatus.ACTIVE
        )
        test_db.add(brand)
        return brand
    
    @pytest.fixture
    def selector_with_sibling(self, test_db: AsyncSession, test_brand):
        """Create a selector with sibling relationship."""
        selector = DOMSelector(
            brand_id=test_brand.id,
            page_type=PageType.HOME,
            selector="button[data-test-id='add-to-cart']",
            description="Add to cart button",
            status=SelectorStatus.ACTIVE,
            relationships={
                "element_type": "interactive",
                "parent": "div.product-card",
                "siblings": ["picture[data-test-id='base-picture']"]
            }
        )
        test_db.add(selector)
        return selector
    
    @pytest.fixture
    def selector_with_child(self, test_db: AsyncSession, test_brand):
        """Create a selector with child relationship."""
        selector = DOMSelector(
            brand_id=test_brand.id,
            page_type=PageType.HOME,
            selector="div.product-card",
            description="Product card container",
            status=SelectorStatus.ACTIVE,
            relationships={
                "element_type": "container",
                "children": ["h3.product-title", "span.price", "button[data-test-id='add-to-cart']"]
            }
        )
        test_db.add(selector)
        return selector
    
    @pytest.fixture
    def selector_no_relationships(self, test_db: AsyncSession, test_brand):
        """Create a selector without relationships."""
        selector = DOMSelector(
            brand_id=test_brand.id,
            page_type=PageType.PDP,
            selector="button.checkout",
            description="Checkout button",
            status=SelectorStatus.ACTIVE,
            relationships=None
        )
        test_db.add(selector)
        return selector
    
    @pytest.fixture
    def selector_empty_relationships(self, test_db: AsyncSession, test_brand):
        """Create a selector with empty relationships dict."""
        selector = DOMSelector(
            brand_id=test_brand.id,
            page_type=PageType.PDP,
            selector="button.submit",
            description="Submit button",
            status=SelectorStatus.ACTIVE,
            relationships={}
        )
        test_db.add(selector)
        return selector
    
    @patch('app.services.code_generator.Anthropic')
    async def test_sibling_navigation(
        self,
        mock_anthropic_class,
        test_db: AsyncSession,
        test_brand,
        selector_with_sibling
    ):
        """Test that code uses parent-then-sibling pattern when targeting sibling."""
        await test_db.flush()
        
        # Mock Claude API response
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_content_block = MagicMock()
        # Generate code that should use parent-then-sibling pattern
        mock_code = """
const button = document.querySelector('button[data-test-id="add-to-cart"]');
const container = button.closest('div.product-card');
const picture = container.querySelector('picture[data-test-id="base-picture"]');
const badge = document.createElement('span');
badge.className = 'badge';
badge.textContent = 'NEW';
picture.parentElement.appendChild(badge);
"""
        mock_response_dict = {
            "generated_code": mock_code,
            "confidence_score": 0.9,
            "implementation_notes": "Uses sibling navigation",
            "testing_checklist": "Test badge appears"
        }
        mock_content_block.text = str(mock_response_dict)
        mock_message.content = [mock_content_block]
        mock_client.messages.create = AsyncMock(return_value=mock_message)
        mock_anthropic_class.return_value = mock_client
        
        # Create code generator service
        service = CodeGeneratorService()
        
        # Prepare data
        brand_context = {
            "name": test_brand.name,
            "domain": test_brand.domain,
            "id": test_brand.id,
            "code_template": {}
        }
        
        selectors_data = [{
            "selector": selector_with_sibling.selector,
            "description": selector_with_sibling.description,
            "relationships": selector_with_sibling.relationships
        }]
        
        # Generate code
        result = await service.generate_code(
            brand_context=brand_context,
            templates=[],
            selectors=selectors_data,
            rules=[],
            test_description="Add badge to product image"
        )
        
        # Verify code was generated
        assert "generated_code" in result
        generated_code = result["generated_code"]
        
        # Verify correct navigation pattern: parent-then-sibling
        assert "closest('div.product-card')" in generated_code or "closest(\"div.product-card\")" in generated_code
        assert "querySelector('picture" in generated_code or "querySelector(\"picture" in generated_code
        
        # Verify incorrect pattern is NOT used: closest() for sibling directly
        # Should NOT have: button.closest('picture[...]')
        assert "button.closest('picture" not in generated_code
        assert "button.closest(\"picture" not in generated_code
    
    @patch('app.services.code_generator.Anthropic')
    async def test_child_navigation(
        self,
        mock_anthropic_class,
        test_db: AsyncSession,
        test_brand,
        selector_with_child
    ):
        """Test that code queries within parent element for children."""
        await test_db.flush()
        
        # Mock Claude API response
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_content_block = MagicMock()
        # Generate code that should query children within parent
        mock_code = """
const productCard = document.querySelector('div.product-card');
const title = productCard.querySelector('h3.product-title');
if (title) {
    title.style.color = 'red';
}
"""
        mock_response_dict = {
            "generated_code": mock_code,
            "confidence_score": 0.85,
            "implementation_notes": "Uses child navigation",
            "testing_checklist": "Test title color changes"
        }
        mock_content_block.text = str(mock_response_dict)
        mock_message.content = [mock_content_block]
        mock_client.messages.create = AsyncMock(return_value=mock_response_dict)
        mock_anthropic_class.return_value = mock_client
        
        # Create code generator service
        service = CodeGeneratorService()
        
        # Prepare data
        brand_context = {
            "name": test_brand.name,
            "domain": test_brand.domain,
            "id": test_brand.id,
            "code_template": {}
        }
        
        selectors_data = [{
            "selector": selector_with_child.selector,
            "description": selector_with_child.description,
            "relationships": selector_with_child.relationships
        }]
        
        # Generate code
        result = await service.generate_code(
            brand_context=brand_context,
            templates=[],
            selectors=selectors_data,
            rules=[],
            test_description="Change product title color"
        )
        
        # Verify code was generated
        assert "generated_code" in result
        generated_code = result["generated_code"]
        
        # Verify child navigation pattern: query within parent
        assert "querySelector('div.product-card')" in generated_code or "querySelector(\"div.product-card\")" in generated_code
        assert "querySelector('h3.product-title')" in generated_code or "querySelector(\"h3.product-title\")" in generated_code
    
    @patch('app.services.code_generator.Anthropic')
    async def test_no_relationship_fallback(
        self,
        mock_anthropic_class,
        test_db: AsyncSession,
        test_brand,
        selector_no_relationships
    ):
        """Test that code works without relationships."""
        await test_db.flush()
        
        # Mock Claude API response
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_content_block = MagicMock()
        # Generate code without relationships
        mock_code = """
const button = document.querySelector('button.checkout');
if (button) {
    button.style.backgroundColor = 'red';
}
"""
        mock_response_dict = {
            "generated_code": mock_code,
            "confidence_score": 0.8,
            "implementation_notes": "Standard selector usage",
            "testing_checklist": "Test button color changes"
        }
        mock_content_block.text = str(mock_response_dict)
        mock_message.content = [mock_content_block]
        mock_client.messages.create = AsyncMock(return_value=mock_response_dict)
        mock_anthropic_class.return_value = mock_client
        
        # Create code generator service
        service = CodeGeneratorService()
        
        # Prepare data
        brand_context = {
            "name": test_brand.name,
            "domain": test_brand.domain,
            "id": test_brand.id,
            "code_template": {}
        }
        
        selectors_data = [{
            "selector": selector_no_relationships.selector,
            "description": selector_no_relationships.description,
            "relationships": None  # No relationships
        }]
        
        # Generate code
        result = await service.generate_code(
            brand_context=brand_context,
            templates=[],
            selectors=selectors_data,
            rules=[],
            test_description="Change checkout button color"
        )
        
        # Verify code was generated
        assert "generated_code" in result
        generated_code = result["generated_code"]
        
        # Verify standard selector usage (no relationship navigation)
        assert "querySelector('button.checkout')" in generated_code or "querySelector(\"button.checkout\")" in generated_code
        
        # Should not use relationship navigation patterns
        assert "closest(" not in generated_code.lower()
    
    @patch('app.services.code_generator.Anthropic')
    async def test_selector_with_empty_relationships(
        self,
        mock_anthropic_class,
        test_db: AsyncSession,
        test_brand,
        selector_empty_relationships
    ):
        """Test that code handles empty relationships gracefully (backward compatibility)."""
        await test_db.flush()
        
        # Mock Claude API response
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_content_block = MagicMock()
        # Generate code with empty relationships
        mock_code = """
const button = document.querySelector('button.submit');
if (button) {
    button.disabled = false;
}
"""
        mock_response_dict = {
            "generated_code": mock_code,
            "confidence_score": 0.75,
            "implementation_notes": "Handles empty relationships",
            "testing_checklist": "Test button is enabled"
        }
        mock_content_block.text = str(mock_response_dict)
        mock_message.content = [mock_content_block]
        mock_client.messages.create = AsyncMock(return_value=mock_response_dict)
        mock_anthropic_class.return_value = mock_client
        
        # Create code generator service
        service = CodeGeneratorService()
        
        # Prepare data with empty relationships dict
        brand_context = {
            "name": test_brand.name,
            "domain": test_brand.domain,
            "id": test_brand.id,
            "code_template": {}
        }
        
        selectors_data = [{
            "selector": selector_empty_relationships.selector,
            "description": selector_empty_relationships.description,
            "relationships": {}  # Empty dict
        }]
        
        # Generate code - should not raise error
        result = await service.generate_code(
            brand_context=brand_context,
            templates=[],
            selectors=selectors_data,
            rules=[],
            test_description="Enable submit button"
        )
        
        # Verify code was generated successfully
        assert "generated_code" in result
        generated_code = result["generated_code"]
        
        # Verify standard selector usage (empty relationships handled gracefully)
        assert "querySelector('button.submit')" in generated_code or "querySelector(\"button.submit\")" in generated_code

