"""Seed data script for populating database with VANS and Timberland brands."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.database import Base
# Import all models to ensure relationships are resolved
from app.models import Brand, Template, DOMSelector, CodeRule, GeneratedCode
from app.models.enums import (
    BrandStatus, TestType, PageType, RuleType,
    SelectorStatus
)
from app.config import settings


async def seed_data():
    """Seed database with VANS and Timberland brand data."""
    # Create engine and session
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as session:
        async with session.begin():
            # VANS Brand with global template
            vans_brand = Brand(
                name="VANS",
                domain="vans.com",
                status=BrandStatus.ACTIVE,
                config={
                    "theme": "skate",
                    "region": "US",
                    "currency": "USD",
                    "global_template": """'use strict';

// ============================================================================
// TEST HEADER
// ============================================================================
/**
 * Test ID: {test_id}
 * Summary: {summary}
 * Version: {version}
 * Last Updated: {date}
 * 
 * Features:
 * {features}
 */

// ============================================================================
// CONFIGURATION
// ============================================================================
const CONFIG = {{
    LOG_LEVEL: 'INFO', // Options: DEBUG, INFO, WARN, ERROR, NONE
    // Add configurable thresholds/durations here
}};

// ============================================================================
// CONSTANTS
// ============================================================================
const LOG_PREFIX = '[{test_id}]';
const utils = window.optimizely && window.optimizely.get ? window.optimizely.get('utils') : null;

// ============================================================================
// LOGGING UTILITIES
// ============================================================================
function log(level, message, data) {{
    if (CONFIG.LOG_LEVEL === 'NONE') return;
    
    const levels = {{ DEBUG: 0, INFO: 1, WARN: 2, ERROR: 3 }};
    const currentLevel = levels[CONFIG.LOG_LEVEL] || 1;
    const messageLevel = levels[level] || 1;
    
    if (messageLevel >= currentLevel) {{
        const logMessage = `${{LOG_PREFIX}} [${{level}}] ${{message}}`;
        if (data) {{
            console.log(logMessage, data);
        }} else {{
            console.log(logMessage);
        }}
    }}
}}

// ============================================================================
// MAIN EXECUTION
// ============================================================================
if (!utils) {{
    log('ERROR', 'Optimizely utils not available');
}} else {{
    utils.waitForElement('body', 10000).then(function() {{
        try {{
            log('INFO', 'Test execution started');
            
            // ================================================================
            // PAGE-SPECIFIC CODE GOES HERE
            // ================================================================
            // Place your page-specific logic in this section
            // Use available DOM selectors from the selectors list
            // Follow the error handling pattern below
            
            
            
            // ================================================================
            // ERROR HANDLING
            // ================================================================
            log('INFO', 'Test execution completed successfully');
        }} catch (error) {{
            log('ERROR', 'Test execution failed', error);
        }}
    }}).catch(function(error) {{
        log('ERROR', 'Failed to wait for element', error);
    }});
}}"""
                }
            )
            session.add(vans_brand)
            await session.flush()
            
            # VANS Templates
            vans_templates = [
                Template(
                    brand_id=vans_brand.id,
                    test_type=TestType.PDP,
                    template_code="""'use strict';
// VANS Product Page Test Template
function testProductPage() {
    const productTitle = document.querySelector('.product-title');
    const productPrice = document.querySelector('.product-price');
    const addToCartBtn = document.querySelector('#add-to-cart-btn');
    
    if (!productTitle || !productPrice || !addToCartBtn) {
        throw new Error('Required PDP elements not found');
    }
    
    // Validate product information is displayed
    console.log('Product:', productTitle.textContent);
    console.log('Price:', productPrice.textContent);
    
    return {
        success: true,
        productTitle: productTitle.textContent,
        productPrice: productPrice.textContent
    };
}""",
                    description="VANS Product Detail Page test template",
                    version="1.0",
                    is_active=True
                ),
                Template(
                    brand_id=vans_brand.id,
                    test_type=TestType.CART,
                    template_code="""'use strict';
// VANS Cart Page Test Template
function testCartPage() {
    const cartItems = document.querySelectorAll('.cart-item');
    const cartTotal = document.querySelector('.cart-total');
    const checkoutBtn = document.querySelector('#checkout-button');
    
    if (cartItems.length === 0) {
        throw new Error('Cart is empty');
    }
    
    // Validate cart items and total
    const itemCount = cartItems.length;
    const total = cartTotal ? cartTotal.textContent : 'N/A';
    
    return {
        success: true,
        itemCount: itemCount,
        total: total
    };
}""",
                    description="VANS Cart Page test template",
                    version="1.0",
                    is_active=True
                ),
                Template(
                    brand_id=vans_brand.id,
                    test_type=TestType.CHECKOUT,
                    template_code="""'use strict';
// VANS Checkout Page Test Template
function testCheckoutPage() {
    const shippingForm = document.querySelector('#shipping-address-form');
    const paymentForm = document.querySelector('#payment-form');
    
    if (!shippingForm || !paymentForm) {
        throw new Error('Checkout forms not found');
    }
    
    // Validate forms are present and accessible
    return {
        success: true,
        shippingFormPresent: !!shippingForm,
        paymentFormPresent: !!paymentForm
    };
}""",
                    description="VANS Checkout Page test template",
                    version="1.0",
                    is_active=True
                )
            ]
            
            # VANS DOM Selectors (15 total)
            vans_selectors = [
                DOMSelector(brand_id=vans_brand.id, page_type=PageType.PDP, selector=".product-title", description="Product title on PDP", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=vans_brand.id, page_type=PageType.PDP, selector=".product-price", description="Product price display", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=vans_brand.id, page_type=PageType.PDP, selector="#add-to-cart-btn", description="Add to cart button", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=vans_brand.id, page_type=PageType.PDP, selector=".product-images img", description="Product image gallery", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=vans_brand.id, page_type=PageType.PDP, selector=".product-description", description="Product description text", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=vans_brand.id, page_type=PageType.PDP, selector=".size-selector", description="Size selection dropdown", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=vans_brand.id, page_type=PageType.CART, selector=".cart-item", description="Individual cart item container", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=vans_brand.id, page_type=PageType.CART, selector=".cart-total", description="Cart total price", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=vans_brand.id, page_type=PageType.CART, selector="#checkout-button", description="Proceed to checkout button", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=vans_brand.id, page_type=PageType.CART, selector=".remove-item-btn", description="Remove item from cart", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=vans_brand.id, page_type=PageType.CHECKOUT, selector="#shipping-address-form", description="Shipping address form", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=vans_brand.id, page_type=PageType.CHECKOUT, selector="#payment-form", description="Payment information form", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=vans_brand.id, page_type=PageType.HOME, selector=".hero-banner", description="Homepage hero banner", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=vans_brand.id, page_type=PageType.HOME, selector=".featured-products", description="Featured products section", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=vans_brand.id, page_type=PageType.CATEGORY, selector=".product-grid", description="Product grid on category page", status=SelectorStatus.ACTIVE),
            ]
            
            # VANS Code Rules (7 total)
            vans_rules = [
                CodeRule(brand_id=vans_brand.id, rule_type=RuleType.FORBIDDEN_PATTERN, rule_content="eval(", priority=1),
                CodeRule(brand_id=vans_brand.id, rule_type=RuleType.FORBIDDEN_PATTERN, rule_content="Function(", priority=1),
                CodeRule(brand_id=vans_brand.id, rule_type=RuleType.FORBIDDEN_PATTERN, rule_content=".innerHTML", priority=2),
                CodeRule(brand_id=vans_brand.id, rule_type=RuleType.FORBIDDEN_PATTERN, rule_content="document.write", priority=1),
                CodeRule(brand_id=vans_brand.id, rule_type=RuleType.FORBIDDEN_PATTERN, rule_content='setTimeout("', priority=2),
                CodeRule(brand_id=vans_brand.id, rule_type=RuleType.REQUIRED_PATTERN, rule_content='"use strict";', priority=3),
                CodeRule(brand_id=vans_brand.id, rule_type=RuleType.MAX_LENGTH, rule_content="5000", priority=2),
            ]
            
            # Add all VANS data
            session.add_all(vans_templates)
            session.add_all(vans_selectors)
            session.add_all(vans_rules)
            
            # Timberland Brand
            timberland_brand = Brand(
                name="Timberland",
                domain="timberland.com",
                status=BrandStatus.ACTIVE,
                config={"theme": "outdoor", "region": "US", "currency": "USD"}
            )
            session.add(timberland_brand)
            await session.flush()
            
            # Timberland Templates
            timberland_templates = [
                Template(
                    brand_id=timberland_brand.id,
                    test_type=TestType.PDP,
                    template_code="""'use strict';
// Timberland Product Page Test Template
function testProductPage() {
    const productHeader = document.querySelector('.timberland-product-header');
    const priceDisplay = document.querySelector('.tb-product-price');
    const addToCartBtn = document.querySelector('#tb-add-to-cart');
    
    if (!productHeader || !priceDisplay || !addToCartBtn) {
        throw new Error('Required PDP elements not found');
    }
    
    return {
        success: true,
        productHeader: productHeader.textContent,
        price: priceDisplay.textContent
    };
}""",
                    description="Timberland Product Detail Page test template",
                    version="1.0",
                    is_active=True
                ),
                Template(
                    brand_id=timberland_brand.id,
                    test_type=TestType.CART,
                    template_code="""'use strict';
// Timberland Cart Page Test Template
function testCartPage() {
    const cartItems = document.querySelectorAll('.tb-cart-item');
    const cartSummary = document.querySelector('.tb-cart-summary');
    
    if (cartItems.length === 0) {
        throw new Error('Cart is empty');
    }
    
    return {
        success: true,
        itemCount: cartItems.length,
        summary: cartSummary ? cartSummary.textContent : 'N/A'
    };
}""",
                    description="Timberland Cart Page test template",
                    version="1.0",
                    is_active=True
                ),
                Template(
                    brand_id=timberland_brand.id,
                    test_type=TestType.CHECKOUT,
                    template_code="""'use strict';
// Timberland Checkout Page Test Template
function testCheckoutPage() {
    const shippingSection = document.querySelector('.tb-shipping-section');
    const paymentSection = document.querySelector('.tb-payment-section');
    const orderReview = document.querySelector('.tb-order-review');
    
    if (!shippingSection || !paymentSection || !orderReview) {
        throw new Error('Required checkout sections not found');
    }
    
    return {
        success: true,
        allSectionsPresent: true
    };
}""",
                    description="Timberland Checkout Page test template",
                    version="1.0",
                    is_active=True
                )
            ]
            
            # Timberland DOM Selectors (15 total)
            timberland_selectors = [
                DOMSelector(brand_id=timberland_brand.id, page_type=PageType.PDP, selector=".timberland-product-header", description="Product header on PDP", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=timberland_brand.id, page_type=PageType.PDP, selector=".tb-product-price", description="Product price display", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=timberland_brand.id, page_type=PageType.PDP, selector="#tb-add-to-cart", description="Add to cart button", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=timberland_brand.id, page_type=PageType.PDP, selector=".tb-product-gallery img", description="Product image gallery", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=timberland_brand.id, page_type=PageType.PDP, selector=".tb-product-details", description="Product details section", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=timberland_brand.id, page_type=PageType.PDP, selector=".tb-size-chart", description="Size chart selector", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=timberland_brand.id, page_type=PageType.CART, selector=".tb-cart-item", description="Cart item container", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=timberland_brand.id, page_type=PageType.CART, selector=".tb-cart-summary", description="Cart summary section", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=timberland_brand.id, page_type=PageType.CART, selector="#tb-checkout-btn", description="Checkout button", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=timberland_brand.id, page_type=PageType.CART, selector=".tb-remove-item", description="Remove item button", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=timberland_brand.id, page_type=PageType.CHECKOUT, selector=".tb-shipping-section", description="Shipping information section", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=timberland_brand.id, page_type=PageType.CHECKOUT, selector=".tb-payment-section", description="Payment information section", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=timberland_brand.id, page_type=PageType.HOME, selector=".tb-hero-section", description="Homepage hero section", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=timberland_brand.id, page_type=PageType.HOME, selector=".tb-featured-collection", description="Featured collection section", status=SelectorStatus.ACTIVE),
                DOMSelector(brand_id=timberland_brand.id, page_type=PageType.CATEGORY, selector=".tb-product-list", description="Product list on category page", status=SelectorStatus.ACTIVE),
            ]
            
            # Timberland Code Rules (7 total)
            timberland_rules = [
                CodeRule(brand_id=timberland_brand.id, rule_type=RuleType.FORBIDDEN_PATTERN, rule_content="eval(", priority=1),
                CodeRule(brand_id=timberland_brand.id, rule_type=RuleType.FORBIDDEN_PATTERN, rule_content="Function(", priority=1),
                CodeRule(brand_id=timberland_brand.id, rule_type=RuleType.FORBIDDEN_PATTERN, rule_content=".innerHTML", priority=2),
                CodeRule(brand_id=timberland_brand.id, rule_type=RuleType.FORBIDDEN_PATTERN, rule_content="document.write", priority=1),
                CodeRule(brand_id=timberland_brand.id, rule_type=RuleType.FORBIDDEN_PATTERN, rule_content='setInterval("', priority=2),
                CodeRule(brand_id=timberland_brand.id, rule_type=RuleType.REQUIRED_PATTERN, rule_content='"use strict";', priority=3),
                CodeRule(brand_id=timberland_brand.id, rule_type=RuleType.MAX_LENGTH, rule_content="5000", priority=2),
            ]
            
            # Add all Timberland data
            session.add_all(timberland_templates)
            session.add_all(timberland_selectors)
            session.add_all(timberland_rules)
            
            await session.commit()
            print("✅ Seed data loaded successfully!")
            print(f"   - Created VANS brand with {len(vans_templates)} templates, {len(vans_selectors)} selectors, {len(vans_rules)} rules")
            print(f"   - Created Timberland brand with {len(timberland_templates)} templates, {len(timberland_selectors)} selectors, {len(timberland_rules)} rules")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_data())
