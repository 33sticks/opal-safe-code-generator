"""Main API router for v1."""
from fastapi import APIRouter
from app.api.v1 import brands, templates, selectors, rules, generated_code, opal

router = APIRouter()

router.include_router(brands.router, prefix="/brands", tags=["brands"])
router.include_router(templates.router, prefix="/templates", tags=["templates"])
router.include_router(selectors.router, prefix="/selectors", tags=["selectors"])
router.include_router(rules.router, prefix="/rules", tags=["rules"])
router.include_router(generated_code.router, prefix="/generated-code", tags=["generated-code"])
router.include_router(opal.router, prefix="/opal", tags=["opal"])

