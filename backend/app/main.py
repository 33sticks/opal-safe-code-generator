"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.api.v1.router import router as v1_router
from app.core.exceptions import (
    NotFoundException,
    ConflictException,
    not_found_exception_handler,
    conflict_exception_handler,
    integrity_error_handler,
)

app = FastAPI(
    title="Opal Safe Code Generator API",
    description="Admin dashboard API for managing brand-specific code generation rules",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(NotFoundException, not_found_exception_handler)
app.add_exception_handler(ConflictException, conflict_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)

# Include API router
app.include_router(v1_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}
