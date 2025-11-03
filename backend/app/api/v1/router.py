"""Main API router for v1."""
from fastapi import APIRouter
from app.api.v1 import brands, page_type_knowledge, selectors, rules, generated_code, opal, admin
from app.api.v1.endpoints import auth, chat, notifications, my_requests, users, analytics, brand_templates, dom_analysis

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(brands.router, prefix="/brands", tags=["brands"])
router.include_router(page_type_knowledge.router, prefix="/page-type-knowledge", tags=["page-type-knowledge"])
router.include_router(selectors.router, prefix="/selectors", tags=["selectors"])
router.include_router(rules.router, prefix="/rules", tags=["rules"])
router.include_router(generated_code.router, prefix="/generated-code", tags=["generated-code"])
router.include_router(opal.router, prefix="/opal", tags=["opal"])
router.include_router(admin.router, prefix="/admin", tags=["admin"])
router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
router.include_router(my_requests.router, prefix="/my-requests", tags=["my-requests"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
router.include_router(brand_templates.router, prefix="/brand-templates", tags=["brand-templates"])
router.include_router(dom_analysis.router, prefix="/dom-analysis", tags=["dom-analysis"])
