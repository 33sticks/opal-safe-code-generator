"""Temporary admin endpoints for database setup."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.models import Brand, Template, DOMSelector, CodeRule
from datetime import datetime

router = APIRouter()

@router.post("/seed")
async def seed_database(db: AsyncSession = Depends(get_db)):
    """Seed the database with initial VANS and Timberland data."""
    
    try:
        # Check if brands already exist
        from sqlalchemy import select
        result = await db.execute(select(Brand))
        existing_brands = result.scalars().all()
        
        if existing_brands:
            return {
                "message": "Database already seeded",
                "brands": [b.name for b in existing_brands]
            }
        
        # Create VANS brand with global template
        vans = Brand(
            name="VANS",
            domain="vans.com",
            status="active",
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
        
        # Create Timberland brand
        timberland = Brand(
            name="Timberland",
            domain="timberland.com",
            status="active",
            config={"theme": "outdoor", "region": "US", "currency": "USD"}
        )
        db.add(timberland)
        await db.flush()
        
        # Create PDP template for VANS
        pdp_template = Template(
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
        db.add(pdp_template)
        
        # Create selectors for VANS PDP
        selectors = [
            DOMSelector(
                brand_id=vans.id,
                page_type="pdp",
                selector="button[data-test-id='vf-button']",
                description="Add to Cart button - main CTA on product page",
                status="active"
            ),
            DOMSelector(
                brand_id=vans.id,
                page_type="pdp",
                selector="span.center.text-center.i-flex",
                description="Button text span inside Add to Cart button",
                status="active"
            )
        ]
        
        for selector in selectors:
            db.add(selector)
        
        # Create code rules for VANS
        rules = [
            CodeRule(
                brand_id=vans.id,
                rule_type="forbidden_pattern",
                rule_content="eval(",
                priority=10
            ),
            CodeRule(
                brand_id=vans.id,
                rule_type="forbidden_pattern",
                rule_content=".innerHTML",
                priority=10
            ),
            CodeRule(
                brand_id=vans.id,
                rule_type="forbidden_pattern",
                rule_content="document.write",
                priority=10
            ),
            CodeRule(
                brand_id=vans.id,
                rule_type="required_pattern",
                rule_content="'use strict';",
                priority=5
            ),
            CodeRule(
                brand_id=vans.id,
                rule_type="required_pattern",
                rule_content="try {",
                priority=5
            ),
            CodeRule(
                brand_id=vans.id,
                rule_type="required_pattern",
                rule_content="log(",
                priority=3
            ),
            CodeRule(
                brand_id=vans.id,
                rule_type="forbidden_pattern",
                rule_content="document.body.innerHTML",
                priority=10
            )
        ]
        
        for rule in rules:
            db.add(rule)
        
        await db.commit()
        
        return {
            "message": "Database seeded successfully",
            "brands": ["VANS", "Timberland"],
            "vans_data": {
                "templates": 1,
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
