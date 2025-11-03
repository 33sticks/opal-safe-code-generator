"""Real-world VANS test scenarios for selector matching and code generation."""
import pytest
import uuid
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brand import Brand
from app.models.dom_selector import DOMSelector
from app.models.enums import BrandStatus, PageType, SelectorStatus
from app.services.selector_validator import validate_element_selector
from app.services.code_generator import CodeGeneratorService


class TestVANSScenarios:
    """Test real-world VANS scenarios for selector matching."""
    
    @pytest.fixture
    def vans_brand(self, test_db: AsyncSession):
        """Create a VANS brand for testing."""
        brand = Brand(
            name="VANS",
            domain="vans.com",
            status=BrandStatus.ACTIVE
        )
        test_db.add(brand)
        return brand
    
    @pytest.fixture
    def vans_home_selectors(self, test_db: AsyncSession, vans_brand):
        """Create VANS HOME page selectors."""
        selectors = [
            DOMSelector(
                brand_id=vans_brand.id,
                page_type=PageType.HOME,
                selector="picture[data-test-id='base-picture']",
                description="Product image container",
                status=SelectorStatus.ACTIVE,
                relationships={
                    "element_type": "content",
                    "parent": "div.product-card",
                    "siblings": ["button[data-test-id='add-to-cart']"]
                }
            ),
            DOMSelector(
                brand_id=vans_brand.id,
                page_type=PageType.HOME,
                selector="button[data-test-id='add-to-cart']",
                description="Add to cart button",
                status=SelectorStatus.ACTIVE,
                relationships={
                    "element_type": "interactive",
                    "parent": "div.product-card",
                    "siblings": ["picture[data-test-id='base-picture']"]
                }
            ),
            DOMSelector(
                brand_id=vans_brand.id,
                page_type=PageType.HOME,
                selector="div.product-card",
                description="Product card container",
                status=SelectorStatus.ACTIVE,
                relationships={
                    "element_type": "container",
                    "children": ["picture[data-test-id='base-picture']", "button[data-test-id='add-to-cart']"]
                }
            )
        ]
        for selector in selectors:
            test_db.add(selector)
        return selectors
    
    @pytest.fixture
    def vans_pdp_selectors(self, test_db: AsyncSession, vans_brand):
        """Create VANS PDP page selectors."""
        selectors = [
            DOMSelector(
                brand_id=vans_brand.id,
                page_type=PageType.PDP,
                selector="button[data-test-id='add-to-cart']",
                description="Add to cart button on product page",
                status=SelectorStatus.ACTIVE,
                relationships={
                    "element_type": "interactive"
                }
            ),
            DOMSelector(
                brand_id=vans_brand.id,
                page_type=PageType.PDP,
                selector="span.price",
                description="Product price",
                status=SelectorStatus.ACTIVE,
                relationships={
                    "element_type": "content"
                }
            ),
            DOMSelector(
                brand_id=vans_brand.id,
                page_type=PageType.PDP,
                selector="div.product-price",
                description="Product price container",
                status=SelectorStatus.ACTIVE,
                relationships={
                    "element_type": "container"
                }
            )
        ]
        for selector in selectors:
            test_db.add(selector)
        return selectors
    
    async def test_badge_on_product_images(
        self,
        test_db: AsyncSession,
        vans_brand,
        vans_home_selectors
    ):
        """Test: 'Add NEW badge to product images in carousel' → Should find picture selector."""
        await test_db.flush()
        
        # Test selector matching
        result = await validate_element_selector(
            db=test_db,
            element_description="product images",
            page_type=PageType.HOME,
            brand_id=vans_brand.id,
            user_message="Add NEW badge to product images in carousel"
        )
        
        # Verify selector was found
        assert result["status"] == "found_in_db"
        assert result["is_valid"] is True
        assert result["selector"] == "picture[data-test-id='base-picture']"
        assert result["source"] == "database"
        
        # Verify it found the correct selector
        assert len(result["matches"]) > 0
        match = result["matches"][0]
        assert match.selector.selector == "picture[data-test-id='base-picture']"
        assert match.selector.description == "Product image container"
    
    async def test_change_add_to_cart_button_color(
        self,
        test_db: AsyncSession,
        vans_brand,
        vans_pdp_selectors
    ):
        """Test: 'Change add to cart button color on product page' → Should find button selector."""
        await test_db.flush()
        
        # Test selector matching
        result = await validate_element_selector(
            db=test_db,
            element_description="add to cart button",
            page_type=PageType.PDP,
            brand_id=vans_brand.id,
            user_message="Change add to cart button color on product page"
        )
        
        # Verify selector was found
        assert result["status"] == "found_in_db"
        assert result["is_valid"] is True
        assert result["selector"] == "button[data-test-id='add-to-cart']"
        assert result["source"] == "database"
        
        # Verify it found the correct selector
        assert len(result["matches"]) > 0
        match = result["matches"][0]
        assert match.selector.selector == "button[data-test-id='add-to-cart']"
        assert "cart" in match.selector.description.lower() or "add" in match.selector.description.lower()
    
    async def test_hide_price_for_sale_products(
        self,
        test_db: AsyncSession,
        vans_brand,
        vans_pdp_selectors
    ):
        """Test: 'Hide the price for products on sale' → Should find price-related selectors."""
        await test_db.flush()
        
        # Test selector matching
        result = await validate_element_selector(
            db=test_db,
            element_description="price",
            page_type=PageType.PDP,
            brand_id=vans_brand.id,
            user_message="Hide the price for products on sale"
        )
        
        # Verify selector was found (should match either span.price or div.product-price)
        assert result["status"] == "found_in_db"
        assert result["is_valid"] is True
        assert result["selector"] in ["span.price", "div.product-price"]
        assert result["source"] == "database"
        
        # Verify it found a price-related selector
        assert len(result["matches"]) > 0
        match = result["matches"][0]
        assert "price" in match.selector.selector.lower() or "price" in match.selector.description.lower()
    
    async def test_semantic_match_product_image(
        self,
        test_db: AsyncSession,
        vans_brand,
        vans_home_selectors
    ):
        """Test semantic matching: 'Change image border' → finds picture selector."""
        await test_db.flush()
        
        # Test with different phrasing
        result = await validate_element_selector(
            db=test_db,
            element_description="image border",
            page_type=PageType.HOME,
            brand_id=vans_brand.id,
            user_message="Change image border"
        )
        
        # Should find the picture selector through semantic matching
        assert result["status"] == "found_in_db"
        assert result["is_valid"] is True
        
        # Should match picture selector (even though description says "image border")
        match = result["matches"][0]
        assert "picture" in match.selector.selector.lower() or "image" in match.selector.description.lower()
    
    @patch('app.services.code_generator.Anthropic')
    async def test_code_generation_with_relationships(
        self,
        mock_anthropic_class,
        test_db: AsyncSession,
        vans_brand,
        vans_home_selectors
    ):
        """Test that code generation uses relationships appropriately."""
        await test_db.flush()
        
        # Mock Claude API response
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_content_block = MagicMock()
        # Generate code that should use sibling navigation
        mock_code = """
const button = document.querySelector('button[data-test-id="add-to-cart"]');
const container = button.closest('div.product-card');
const picture = container.querySelector('picture[data-test-id="base-picture"]');
const badge = document.createElement('span');
badge.className = 'badge';
badge.textContent = 'NEW';
picture.appendChild(badge);
"""
        mock_response_dict = {
            "generated_code": mock_code,
            "confidence_score": 0.9,
            "implementation_notes": "Uses sibling navigation via parent container",
            "testing_checklist": "Verify badge appears on product images"
        }
        mock_content_block.text = str(mock_response_dict)
        mock_message.content = [mock_content_block]
        mock_client.messages.create = AsyncMock(return_value=mock_message)
        mock_anthropic_class.return_value = mock_client
        
        # Create code generator service
        service = CodeGeneratorService()
        
        # Prepare data with relationships
        brand_context = {
            "name": vans_brand.name,
            "domain": vans_brand.domain,
            "id": vans_brand.id,
            "code_template": {}
        }
        
        selectors_data = [{
            "selector": s.selector,
            "description": s.description,
            "relationships": s.relationships
        } for s in vans_home_selectors]
        
        # Generate code
        result = await service.generate_code(
            brand_context=brand_context,
            templates=[],
            selectors=selectors_data,
            rules=[],
            test_description="Add NEW badge to product images in carousel"
        )
        
        # Verify code was generated
        assert "generated_code" in result
        generated_code = result["generated_code"]
        
        # Verify relationships were used (should navigate via parent container)
        assert "closest('div.product-card')" in generated_code or "closest(\"div.product-card\")" in generated_code
        assert "querySelector('picture" in generated_code or "querySelector(\"picture" in generated_code

