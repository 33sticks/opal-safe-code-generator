"""SQLAlchemy models."""
from app.models.brand import Brand
from app.models.template import Template
from app.models.dom_selector import DOMSelector
from app.models.code_rule import CodeRule
from app.models.generated_code import GeneratedCode

__all__ = [
    "Brand",
    "Template",
    "DOMSelector",
    "CodeRule",
    "GeneratedCode",
]