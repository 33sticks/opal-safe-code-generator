"""Temporary admin endpoints for database setup."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db
from app.models import Brand, PageTypeKnowledge, DOMSelector, CodeRule, User
from app.models.enums import UserRole, BrandStatus
from datetime import datetime

router = APIRouter()

@router.post("/seed")
async def seed_database(db: AsyncSession = Depends(get_db)):
    """Seed the database with initial VANS and Timberland data. Idempotent - creates missing data only."""
    
    try:
        # Check if brands already exist
        result = await db.execute(select(Brand))
        existing_brands = result.scalars().all()
        
        brands_seeded = False
        if existing_brands:
            brands_seeded = True
            vans_brand = next((b for b in existing_brands if b.name == "VANS"), None)
            timberland_brand = next((b for b in existing_brands if b.name == "Timberland"), None)
        else:
            brands_seeded = False
            vans_brand = None
            timberland_brand = None
        
        # Create VANS brand if it doesn't exist
        if not vans_brand:
            vans = Brand(
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
const CONFIG = {
    LOG_LEVEL: 'INFO', // Options: DEBUG, INFO, WARN, ERROR, NONE
};

// ============================================================================
// CONSTANTS
// ============================================================================
const LOG_PREFIX = '[{test_id}]';
const utils = window.optimizely && window.optimizely.get ? window.optimizely.get('utils') : null;

// ============================================================================
// LOGGING UTILITIES
// ============================================================================
function log(level, message, data) {
    if (CONFIG.LOG_LEVEL === 'NONE') return;
    
    const levels = { DEBUG: 0, INFO: 1, WARN: 2, ERROR: 3 };
    const currentLevel = levels[CONFIG.LOG_LEVEL] || 1;
    const messageLevel = levels[level] || 1;
    
    if (messageLevel >= currentLevel) {
        const logMessage = `${LOG_PREFIX} [${level}] ${message}`;
        if (data) {
            console.log(logMessage, data);
        } else {
            console.log(logMessage);
        }
    }
}

// ============================================================================
// MAIN EXECUTION
// ============================================================================
if (!utils) {
    log('ERROR', 'Optimizely utils not available');
} else {
    utils.waitForElement('body', 10000).then(function() {
        try {
            log('INFO', 'Test execution started');
            
            // ================================================================
            // PAGE-SPECIFIC CODE GOES HERE
            // ================================================================
            
            log('INFO', 'Test execution completed successfully');
        } catch (error) {
            log('ERROR', 'Test execution failed', error);
        }
    }).catch(function(error) {
        log('ERROR', 'Failed to wait for element', error);
    });
}"""
            }
            )
            db.add(vans)
            await db.flush()
            vans_brand = vans
        else:
            vans = vans_brand
        
        # Create Timberland brand if it doesn't exist
        if not timberland_brand:
            timberland = Brand(
                name="Timberland",
                domain="timberland.com",
                status=BrandStatus.ACTIVE,
                config={"theme": "outdoor", "region": "US", "currency": "USD"}
            )
            db.add(timberland)
            await db.flush()
            timberland_brand = timberland
        else:
            timberland = timberland_brand
        
        # Create PDP page type knowledge for VANS if it doesn't exist
        existing_knowledge = await db.execute(
            select(PageTypeKnowledge).where(PageTypeKnowledge.brand_id == vans.id, PageTypeKnowledge.test_type == "pdp")
        )
        if not existing_knowledge.scalar_one_or_none():
            pdp_knowledge = PageTypeKnowledge(
                brand_id=vans.id,
                test_type="pdp",
                template_code="""'use strict';

const utils = window.optimizely.get("utils");

utils.waitForElement("button[data-test-id='vf-button']", 10000).then(function(addToCartButton) {
    log('INFO', 'Add to Cart button found');
    
    const textSpan = addToCartButton.querySelector('span.center.text-center.i-flex');
    
    if (!textSpan) {
        log('WARN', 'Text span not found in button');
        return;
    }
    
    if (!textSpan.dataset.originalText) {
        textSpan.dataset.originalText = textSpan.innerText || textSpan.textContent;
    }
    
    log('INFO', 'Button modification complete');
    
}).catch(function(error) {
    log('ERROR', 'Add to Cart button not found', error);
});""",
                description="PDP Add to Cart button modification pattern",
                version="1.0",
                is_active=True
            )
            db.add(pdp_knowledge)
        
        # Create selectors for VANS PDP if they don't exist
        selector_data = [
            {"selector": "button[data-test-id='vf-button']", "description": "Add to Cart button - main CTA on product page"},
            {"selector": "span.center.text-center.i-flex", "description": "Button text span inside Add to Cart button"}
        ]
        
        for sel_data in selector_data:
            existing_sel = await db.execute(
                select(DOMSelector).where(
                    DOMSelector.brand_id == vans.id,
                    DOMSelector.selector == sel_data["selector"]
                )
            )
            if not existing_sel.scalar_one_or_none():
                selector = DOMSelector(
                    brand_id=vans.id,
                    page_type="pdp",
                    selector=sel_data["selector"],
                    description=sel_data["description"],
                    status="active"
                )
                db.add(selector)
        
        # Create code rules for VANS if they don't exist
        rules_data = [
            {"rule_type": "forbidden_pattern", "rule_content": "eval(", "priority": 10},
            {"rule_type": "forbidden_pattern", "rule_content": ".innerHTML", "priority": 10},
            {"rule_type": "forbidden_pattern", "rule_content": "document.write", "priority": 10},
            {"rule_type": "required_pattern", "rule_content": "'use strict';", "priority": 5},
            {"rule_type": "required_pattern", "rule_content": "try {", "priority": 5},
            {"rule_type": "required_pattern", "rule_content": "log(", "priority": 3},
            {"rule_type": "forbidden_pattern", "rule_content": "document.body.innerHTML", "priority": 10}
        ]
        
        for rule_data in rules_data:
            existing_rule = await db.execute(
                select(CodeRule).where(
                    CodeRule.brand_id == vans.id,
                    CodeRule.rule_type == rule_data["rule_type"],
                    CodeRule.rule_content == rule_data["rule_content"]
                )
            )
            if not existing_rule.scalar_one_or_none():
                rule = CodeRule(
                    brand_id=vans.id,
                    **rule_data
                )
                db.add(rule)
        
        # Always check and create users if they don't exist
        admin_result = await db.execute(
            select(User).where(User.email == "admin@opalsafecode.com")
        )
        admin_user = admin_result.scalar_one_or_none()
        
        admin_created = False
        if not admin_user:
            admin_user = User(
                email="admin@opalsafecode.com",
                name="Admin User",
                role=UserRole.ADMIN,
                brand_id=None
            )
            admin_user.set_password("changeme123")
            db.add(admin_user)
            admin_created = True
        
        user_result = await db.execute(
            select(User).where(User.email == "user@vans.com")
        )
        user_user = user_result.scalar_one_or_none()
        
        user_created = False
        if not user_user:
            user_user = User(
                email="user@vans.com",
                name="VANS User",
                role=UserRole.USER,
                brand_id=vans.id
            )
            user_user.set_password("changeme123")
            db.add(user_user)
            user_created = True
        
        await db.commit()
        
        message = "Database seeded successfully" if not brands_seeded else "Database check completed - missing data created"
        
        return {
            "message": message,
            "brands": ["VANS", "Timberland"],
            "brands_already_existed": brands_seeded,
            "users_created": {
                "admin": admin_created,
                "user": user_created
            },
            "vans_data": {
                "page_type_knowledge": 1,
                "selectors": 2,
                "rules": 7
            }
        }
        
    except Exception as e:
        await db.rollback()
        raise Exception(f"Seed failed: {str(e)}")


@router.post("/migrate")
async def run_migrations():
    """Run database migrations. TEMPORARY - for setup only."""
    try:
        import subprocess
        import os
        
        # Get the backend directory
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        # Run alembic upgrade head
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return {
                "message": "Migrations completed successfully",
                "output": result.stdout
            }
        else:
            return {
                "message": "Migration failed",
                "error": result.stderr,
                "returncode": result.returncode
            }
            
    except Exception as e:
        raise Exception(f"Migration failed: {str(e)}")
