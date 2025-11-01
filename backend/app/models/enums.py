"""Enum definitions for all model fields."""
from enum import Enum


class BrandStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class TestType(str, Enum):
    PDP = "pdp"
    CART = "cart"
    CHECKOUT = "checkout"
    HOME = "home"
    CATEGORY = "category"


class PageType(str, Enum):
    PDP = "pdp"
    CART = "cart"
    CHECKOUT = "checkout"
    HOME = "home"
    CATEGORY = "category"
    SEARCH = "search"


class RuleType(str, Enum):
    FORBIDDEN_PATTERN = "forbidden_pattern"
    REQUIRED_PATTERN = "required_pattern"
    MAX_LENGTH = "max_length"
    MIN_LENGTH = "min_length"


class ValidationStatus(str, Enum):
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"


class DeploymentStatus(str, Enum):
    PENDING = "pending"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class SelectorStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class ConversationStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class CodeStatus(str, Enum):
    GENERATED = "generated"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEPLOYED = "deployed"


class BrandRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    BRAND_ADMIN = "brand_admin"
    BRAND_USER = "brand_user"


class NotificationType(str, Enum):
    CODE_APPROVED = "code_approved"
    CODE_REJECTED = "code_rejected"
    CODE_UNDER_REVIEW = "code_under_review"
    CODE_NEEDS_REVIEW = "code_needs_review"
