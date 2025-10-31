"""Custom exceptions and exception handlers."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select


class NotFoundException(Exception):
    """Exception for resource not found."""
    
    def __init__(self, resource: str, id: int):
        self.resource = resource
        self.id = id
        self.message = f"{resource} with id {id} not found"


class ConflictException(Exception):
    """Exception for conflict errors (duplicates, constraints)."""
    
    def __init__(self, message: str):
        self.message = message


async def not_found_exception_handler(request: Request, exc: NotFoundException):
    """Handle NotFoundException and return 404."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message}
    )


async def conflict_exception_handler(request: Request, exc: ConflictException):
    """Handle ConflictException and return 409."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message}
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle SQLAlchemy IntegrityError and return 409."""
    message = "Database constraint violation"
    error_str = str(exc.orig).lower()
    
    if "unique" in error_str:
        message = "Duplicate entry violates unique constraint"
    elif "foreign key" in error_str:
        message = "Foreign key constraint violation"
    
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": message}
    )

