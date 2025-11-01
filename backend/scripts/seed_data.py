"""Seed data script for populating database with VANS and Timberland brands."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from app.database import Base
# Import all models to ensure relationships are resolved
from app.models import Brand, Template, DOMSelector, CodeRule, GeneratedCode, User
from app.models.enums import (
    BrandStatus, TestType, PageType, RuleType,
    SelectorStatus, UserRole, BrandRole
)
from app.config import settings


async def seed_data():
    """Seed database with VANS and Timberland brand data."""
    # Transform DATABASE_URL to use asyncpg driver (same as database.py)
    database_url = settings.DATABASE_URL
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    
    # Create engine and session
    engine = create_async_engine(database_url, echo=False)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as session:
        # Check if VANS brand exists
        vans_result = await session.execute(
            select(Brand).where(Brand.name == "VANS")
        )
        vans_brand = vans_result.scalar_one_or_none()
        
        if not vans_brand:
            # Create VANS Brand with global template
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
            print("✅ Created VANS brand")
        else:
            print("ℹ️  VANS brand already exists")
            
        # VANS Templates - check and create if missing
        vans_templates_data = [
            {
                "test_type": TestType.PDP,
                "template_code": """'use strict';
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
                "description": "VANS Product Detail Page test template",
                "version": "1.0",
                "is_active": True
            },
            {
                "test_type": TestType.CART,
                "template_code": """'use strict';
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
                "description": "VANS Cart Page test template",
                "version": "1.0",
                "is_active": True
            },
            {
                "test_type": TestType.CHECKOUT,
                "template_code": """'use strict';
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
                "description": "VANS Checkout Page test template",
                "version": "1.0",
                "is_active": True
            }
        ]
        
        vans_templates_created = 0
        for template_data in vans_templates_data:
            existing = await session.execute(
                select(Template).where(
                    Template.brand_id == vans_brand.id,
                    Template.test_type == template_data["test_type"]
                )
            )
            if not existing.scalar_one_or_none():
                template = Template(
                    brand_id=vans_brand.id,
                    **template_data
                )
                session.add(template)
                vans_templates_created += 1
        
        # VANS DOM Selectors - check and create if missing
        vans_selectors_data = [
            {"page_type": PageType.PDP, "selector": ".product-title", "description": "Product title on PDP"},
            {"page_type": PageType.PDP, "selector": ".product-price", "description": "Product price display"},
            {"page_type": PageType.PDP, "selector": "#add-to-cart-btn", "description": "Add to cart button"},
            {"page_type": PageType.PDP, "selector": ".product-images img", "description": "Product image gallery"},
            {"page_type": PageType.PDP, "selector": ".product-description", "description": "Product description text"},
            {"page_type": PageType.PDP, "selector": ".size-selector", "description": "Size selection dropdown"},
            {"page_type": PageType.CART, "selector": ".cart-item", "description": "Individual cart item container"},
            {"page_type": PageType.CART, "selector": ".cart-total", "description": "Cart total price"},
            {"page_type": PageType.CART, "selector": "#checkout-button", "description": "Proceed to checkout button"},
            {"page_type": PageType.CART, "selector": ".remove-item-btn", "description": "Remove item from cart"},
            {"page_type": PageType.CHECKOUT, "selector": "#shipping-address-form", "description": "Shipping address form"},
            {"page_type": PageType.CHECKOUT, "selector": "#payment-form", "description": "Payment information form"},
            {"page_type": PageType.HOME, "selector": ".hero-banner", "description": "Homepage hero banner"},
            {"page_type": PageType.HOME, "selector": ".featured-products", "description": "Featured products section"},
            {"page_type": PageType.CATEGORY, "selector": ".product-grid", "description": "Product grid on category page"},
        ]
        
        vans_selectors_created = 0
        for selector_data in vans_selectors_data:
            existing = await session.execute(
                select(DOMSelector).where(
                    DOMSelector.brand_id == vans_brand.id,
                    DOMSelector.selector == selector_data["selector"]
                )
            )
            if not existing.scalar_one_or_none():
                selector = DOMSelector(
                    brand_id=vans_brand.id,
                    status=SelectorStatus.ACTIVE,
                    **selector_data
                )
                session.add(selector)
                vans_selectors_created += 1
        
        # VANS Code Rules - check and create if missing
        vans_rules_data = [
            {"rule_type": RuleType.FORBIDDEN_PATTERN, "rule_content": "eval(", "priority": 1},
            {"rule_type": RuleType.FORBIDDEN_PATTERN, "rule_content": "Function(", "priority": 1},
            {"rule_type": RuleType.FORBIDDEN_PATTERN, "rule_content": ".innerHTML", "priority": 2},
            {"rule_type": RuleType.FORBIDDEN_PATTERN, "rule_content": "document.write", "priority": 1},
            {"rule_type": RuleType.FORBIDDEN_PATTERN, "rule_content": 'setTimeout("', "priority": 2},
            {"rule_type": RuleType.REQUIRED_PATTERN, "rule_content": '"use strict";', "priority": 3},
            {"rule_type": RuleType.MAX_LENGTH, "rule_content": "5000", "priority": 2},
        ]
        
        vans_rules_created = 0
        for rule_data in vans_rules_data:
            existing = await session.execute(
                select(CodeRule).where(
                    CodeRule.brand_id == vans_brand.id,
                    CodeRule.rule_type == rule_data["rule_type"],
                    CodeRule.rule_content == rule_data["rule_content"]
                )
            )
            if not existing.scalar_one_or_none():
                rule = CodeRule(
                    brand_id=vans_brand.id,
                    **rule_data
                )
                session.add(rule)
                vans_rules_created += 1
            
        # Check if Timberland brand exists
        timberland_result = await session.execute(
            select(Brand).where(Brand.name == "Timberland")
        )
        timberland_brand = timberland_result.scalar_one_or_none()
        
        if not timberland_brand:
            # Create Timberland Brand
            timberland_brand = Brand(
                name="Timberland",
                domain="timberland.com",
                status=BrandStatus.ACTIVE,
                config={"theme": "outdoor", "region": "US", "currency": "USD"}
            )
            session.add(timberland_brand)
            await session.flush()
            print("✅ Created Timberland brand")
        else:
            print("ℹ️  Timberland brand already exists")
            
        # Timberland Templates - check and create if missing
        timberland_templates_data = [
            {
                "test_type": TestType.PDP,
                "template_code": """'use strict';
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
                "description": "Timberland Product Detail Page test template",
                "version": "1.0",
                "is_active": True
            },
            {
                "test_type": TestType.CART,
                "template_code": """'use strict';
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
                "description": "Timberland Cart Page test template",
                "version": "1.0",
                "is_active": True
            },
            {
                "test_type": TestType.CHECKOUT,
                "template_code": """'use strict';
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
                "description": "Timberland Checkout Page test template",
                "version": "1.0",
                "is_active": True
            }
        ]
        
        timberland_templates_created = 0
        for template_data in timberland_templates_data:
            existing = await session.execute(
                select(Template).where(
                    Template.brand_id == timberland_brand.id,
                    Template.test_type == template_data["test_type"]
                )
            )
            if not existing.scalar_one_or_none():
                template = Template(
                    brand_id=timberland_brand.id,
                    **template_data
                )
                session.add(template)
                timberland_templates_created += 1
        
        # Timberland DOM Selectors - check and create if missing
        timberland_selectors_data = [
            {"page_type": PageType.PDP, "selector": ".timberland-product-header", "description": "Product header on PDP"},
            {"page_type": PageType.PDP, "selector": ".tb-product-price", "description": "Product price display"},
            {"page_type": PageType.PDP, "selector": "#tb-add-to-cart", "description": "Add to cart button"},
            {"page_type": PageType.PDP, "selector": ".tb-product-gallery img", "description": "Product image gallery"},
            {"page_type": PageType.PDP, "selector": ".tb-product-details", "description": "Product details section"},
            {"page_type": PageType.PDP, "selector": ".tb-size-chart", "description": "Size chart selector"},
            {"page_type": PageType.CART, "selector": ".tb-cart-item", "description": "Cart item container"},
            {"page_type": PageType.CART, "selector": ".tb-cart-summary", "description": "Cart summary section"},
            {"page_type": PageType.CART, "selector": "#tb-checkout-btn", "description": "Checkout button"},
            {"page_type": PageType.CART, "selector": ".tb-remove-item", "description": "Remove item button"},
            {"page_type": PageType.CHECKOUT, "selector": ".tb-shipping-section", "description": "Shipping information section"},
            {"page_type": PageType.CHECKOUT, "selector": ".tb-payment-section", "description": "Payment information section"},
            {"page_type": PageType.HOME, "selector": ".tb-hero-section", "description": "Homepage hero section"},
            {"page_type": PageType.HOME, "selector": ".tb-featured-collection", "description": "Featured collection section"},
            {"page_type": PageType.CATEGORY, "selector": ".tb-product-list", "description": "Product list on category page"},
        ]
        
        timberland_selectors_created = 0
        for selector_data in timberland_selectors_data:
            existing = await session.execute(
                select(DOMSelector).where(
                    DOMSelector.brand_id == timberland_brand.id,
                    DOMSelector.selector == selector_data["selector"]
                )
            )
            if not existing.scalar_one_or_none():
                selector = DOMSelector(
                    brand_id=timberland_brand.id,
                    status=SelectorStatus.ACTIVE,
                    **selector_data
                )
                session.add(selector)
                timberland_selectors_created += 1
        
        # Timberland Code Rules - check and create if missing
        timberland_rules_data = [
            {"rule_type": RuleType.FORBIDDEN_PATTERN, "rule_content": "eval(", "priority": 1},
            {"rule_type": RuleType.FORBIDDEN_PATTERN, "rule_content": "Function(", "priority": 1},
            {"rule_type": RuleType.FORBIDDEN_PATTERN, "rule_content": ".innerHTML", "priority": 2},
            {"rule_type": RuleType.FORBIDDEN_PATTERN, "rule_content": "document.write", "priority": 1},
            {"rule_type": RuleType.FORBIDDEN_PATTERN, "rule_content": 'setInterval("', "priority": 2},
            {"rule_type": RuleType.REQUIRED_PATTERN, "rule_content": '"use strict";', "priority": 3},
            {"rule_type": RuleType.MAX_LENGTH, "rule_content": "5000", "priority": 2},
        ]
        
        timberland_rules_created = 0
        for rule_data in timberland_rules_data:
            existing = await session.execute(
                select(CodeRule).where(
                    CodeRule.brand_id == timberland_brand.id,
                    CodeRule.rule_type == rule_data["rule_type"],
                    CodeRule.rule_content == rule_data["rule_content"]
                )
            )
            if not existing.scalar_one_or_none():
                rule = CodeRule(
                    brand_id=timberland_brand.id,
                    **rule_data
                )
                session.add(rule)
                timberland_rules_created += 1
            
        # Create default users - check if they exist
        admin_result = await session.execute(
            select(User).where(User.email == "admin@opalsafecode.com")
        )
        admin_user = admin_result.scalar_one_or_none()
        
        if not admin_user:
            admin_user = User(
                email="admin@opalsafecode.com",
                name="Super Admin",
                role=UserRole.ADMIN,
                brand_id=None,
                brand_role=BrandRole.SUPER_ADMIN.value
            )
            admin_user.set_password("changeme123")
            session.add(admin_user)
            print("✅ Created super admin user: admin@opalsafecode.com / changeme123")
        else:
            # Update existing admin to super_admin
            admin_user.brand_role = BrandRole.SUPER_ADMIN.value
            admin_user.name = "Super Admin"
            print("✅ Updated admin user to super_admin: admin@opalsafecode.com")
        
        # Create VANS brand admin
        vans_admin_result = await session.execute(
            select(User).where(User.email == "admin@vans.com")
        )
        vans_admin_user = vans_admin_result.scalar_one_or_none()
        
        if not vans_admin_user:
            vans_admin_user = User(
                email="admin@vans.com",
                name="VANS Admin",
                role=UserRole.ADMIN,
                brand_id=vans_brand.id,
                brand_role=BrandRole.BRAND_ADMIN.value
            )
            vans_admin_user.set_password("changeme123")
            session.add(vans_admin_user)
            print("✅ Created VANS brand admin: admin@vans.com / changeme123")
        else:
            # Update existing to brand_admin
            vans_admin_user.brand_role = BrandRole.BRAND_ADMIN.value
            print("✅ Updated VANS admin to brand_admin: admin@vans.com")
        
        user_result = await session.execute(
            select(User).where(User.email == "user@vans.com")
        )
        user_user = user_result.scalar_one_or_none()
        
        if not user_user:
            user_user = User(
                email="user@vans.com",
                name="VANS User",
                role=UserRole.USER,
                brand_id=vans_brand.id,
                brand_role=BrandRole.BRAND_USER.value
            )
            user_user.set_password("changeme123")
            session.add(user_user)
            print("✅ Created VANS user: user@vans.com / changeme123")
        else:
            # Update existing user to brand_user
            user_user.brand_role = BrandRole.BRAND_USER.value
            print("✅ Updated VANS user to brand_user: user@vans.com")
        
        await session.commit()
        print("\n✅ Seed data loaded successfully!")
        print(f"   - VANS: {vans_templates_created} templates, {vans_selectors_created} selectors, {vans_rules_created} rules created")
        print(f"   - Timberland: {timberland_templates_created} templates, {timberland_selectors_created} selectors, {timberland_rules_created} rules created")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_data())
