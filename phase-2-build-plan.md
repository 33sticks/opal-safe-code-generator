# Phase 2 Build Plan: Backend API Implementation
## Opal Safe Code Generator - Sprint 1, Phase 2

**Duration:** Days 3-4  
**Status:** Ready for Implementation  
**Prerequisites:** Phase 1 Complete ✅

---

## Overview

Phase 2 focuses on implementing the complete REST API for all 5 entities with full CRUD operations, comprehensive error handling, and thorough testing. This phase will deliver production-ready API endpoints that the frontend can consume.

---

## Day 3: API Endpoints Implementation

### 3.1 Core Infrastructure Setup

#### 3.1.1 Database Dependencies (`backend/app/api/deps.py`)
**Purpose:** Centralize database session dependency injection

**Implementation:**
- Create `get_db()` dependency function that yields `AsyncSession`
- Re-export from `app.database` or create wrapper for API layer separation
- Ensure proper session cleanup on request completion

**Code Structure:**
```python
from typing import AsyncGenerator
from app.database import AsyncSession, AsyncSessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

---

#### 3.1.2 Custom Exception Handlers (`backend/app/core/exceptions.py`)
**Purpose:** Standardized error handling across all endpoints

**Implementation:**
- Create custom exception classes:
  - `NotFoundException` - For 404 errors
  - `ValidationException` - For validation errors (422)
  - `ConflictException` - For duplicate/conflict errors (409)
- Create global exception handler in main.py:
  - SQLAlchemy IntegrityError → 409 Conflict
  - Pydantic ValidationError → 422 Unprocessable Entity
  - SQLAlchemy NoResultFound → 404 Not Found
  - Generic Exception → 500 Internal Server Error

**Exception Classes:**
```python
class NotFoundException(Exception):
    def __init__(self, resource: str, id: int):
        self.resource = resource
        self.id = id
        self.message = f"{resource} with id {id} not found"

class ConflictException(Exception):
    def __init__(self, message: str):
        self.message = message
```

**Handler Pattern:**
- Return JSON error responses with consistent structure:
  ```json
  {
    "detail": "Error message",
    "status_code": 404
  }
  ```

---

### 3.2 Entity API Endpoints

For each of the 5 entities (Brands, Templates, DOM Selectors, Code Rules, Generated Code), implement:

#### Standard Endpoint Pattern:
1. **GET /{entity}/** - List all (200 OK)
   - Query parameters: `skip`, `limit` for pagination
   - Return: List[EntityResponse]

2. **POST /{entity}/** - Create (201 Created)
   - Request body: EntityCreate schema
   - Validation: Check foreign key constraints (e.g., brand_id exists)
   - Return: EntityResponse

3. **GET /{entity}/{id}** - Get by ID (200 OK / 404 Not Found)
   - Path parameter: `id: int`
   - Return: EntityResponse or raise NotFoundException

4. **PUT /{entity}/{id}** - Update (200 OK / 404 Not Found)
   - Path parameter: `id: int`
   - Request body: EntityUpdate schema
   - Return: EntityResponse or raise NotFoundException

5. **DELETE /{entity}/{id}** - Delete (204 No Content / 404 Not Found)
   - Path parameter: `id: int`
   - Cascade delete handled by SQLAlchemy relationships
   - Return: No content or raise NotFoundException

---

#### 3.2.1 Brands API (`backend/app/api/v1/brands.py`)

**Endpoints:**
- `GET /api/v1/brands/` - List all brands
- `POST /api/v1/brands/` - Create brand
- `GET /api/v1/brands/{brand_id}` - Get brand by ID
- `PUT /api/v1/brands/{brand_id}` - Update brand
- `DELETE /api/v1/brands/{brand_id}` - Delete brand

**Business Logic:**
- Check for duplicate brand name on create/update
- Validate domain format (basic validation)
- Handle cascade deletes (templates, selectors, rules, generated_code)

**Dependencies:**
- `get_db` from `app.api.deps`
- `Brand` model, `BrandCreate`, `BrandUpdate`, `BrandResponse` schemas

---

#### 3.2.2 Templates API (`backend/app/api/v1/templates.py`)

**Endpoints:**
- `GET /api/v1/templates/` - List all templates (optional: filter by brand_id)
- `POST /api/v1/templates/` - Create template
- `GET /api/v1/templates/{template_id}` - Get template by ID
- `PUT /api/v1/templates/{template_id}` - Update template
- `DELETE /api/v1/templates/{template_id}` - Delete template

**Business Logic:**
- Validate `brand_id` exists before create/update
- Optional query param: `?brand_id={id}` for filtering list

**Dependencies:**
- `get_db` from `app.api.deps`
- `Template` model, `TemplateCreate`, `TemplateUpdate`, `TemplateResponse` schemas
- Verify brand exists (query Brand model)

---

#### 3.2.3 DOM Selectors API (`backend/app/api/v1/selectors.py`)

**Endpoints:**
- `GET /api/v1/selectors/` - List all selectors (optional: filter by brand_id)
- `POST /api/v1/selectors/` - Create selector
- `GET /api/v1/selectors/{selector_id}` - Get selector by ID
- `PUT /api/v1/selectors/{selector_id}` - Update selector
- `DELETE /api/v1/selectors/{selector_id}` - Delete selector

**Business Logic:**
- Validate `brand_id` exists before create/update
- Optional query param: `?brand_id={id}` for filtering list

**Dependencies:**
- `get_db` from `app.api.deps`
- `DOMSelector` model, `DOMSelectorCreate`, `DOMSelectorUpdate`, `DOMSelectorResponse` schemas
- Verify brand exists (query Brand model)

---

#### 3.2.4 Code Rules API (`backend/app/api/v1/rules.py`)

**Endpoints:**
- `GET /api/v1/rules/` - List all rules (optional: filter by brand_id)
- `POST /api/v1/rules/` - Create rule
- `GET /api/v1/rules/{rule_id}` - Get rule by ID
- `PUT /api/v1/rules/{rule_id}` - Update rule
- `DELETE /api/v1/rules/{rule_id}` - Delete rule

**Business Logic:**
- Validate `brand_id` exists before create/update
- Optional query param: `?brand_id={id}` for filtering list

**Dependencies:**
- `get_db` from `app.api.deps`
- `CodeRule` model, `CodeRuleCreate`, `CodeRuleUpdate`, `CodeRuleResponse` schemas
- Verify brand exists (query Brand model)

---

#### 3.2.5 Generated Code API (`backend/app/api/v1/generated_code.py`)

**Endpoints:**
- `GET /api/v1/generated-code/` - List all generated code (optional: filter by brand_id)
- `POST /api/v1/generated-code/` - Create generated code record
- `GET /api/v1/generated-code/{code_id}` - Get by ID
- `PUT /api/v1/generated-code/{code_id}` - Update generated code
- `DELETE /api/v1/generated-code/{code_id}` - Delete generated code

**Business Logic:**
- Validate `brand_id` exists before create/update
- Optional query param: `?brand_id={id}` for filtering list

**Dependencies:**
- `get_db` from `app.api.deps`
- `GeneratedCode` model, `GeneratedCodeCreate`, `GeneratedCodeUpdate`, `GeneratedCodeResponse` schemas
- Verify brand exists (query Brand model)

---

### 3.3 API Router Configuration

#### 3.3.1 Main V1 Router (`backend/app/api/v1/router.py`)
**Purpose:** Aggregate all entity routers under `/api/v1` prefix

**Implementation:**
- Import all entity routers
- Create main `router` (FastAPI APIRouter)
- Include all entity routers with appropriate prefixes:
  - `brands.router` → `/brands`
  - `templates.router` → `/templates`
  - `selectors.router` → `/selectors`
  - `rules.router` → `/rules`
  - `generated_code.router` → `/generated-code`

**Structure:**
```python
from fastapi import APIRouter
from app.api.v1 import brands, templates, selectors, rules, generated_code

router = APIRouter()

router.include_router(brands.router, prefix="/brands", tags=["brands"])
router.include_router(templates.router, prefix="/templates", tags=["templates"])
# ... etc
```

---

#### 3.3.2 Update Main Application (`backend/app/main.py`)
**Purpose:** Register API router and exception handlers

**Changes:**
1. Import exception handlers from `app.core.exceptions`
2. Add global exception handlers:
   - `NotFoundException` → 404
   - `ConflictException` → 409
   - `IntegrityError` → 409
   - `ValidationError` → 422
   - Generic `Exception` → 500
3. Uncomment and include v1 router:
   ```python
   from app.api.v1.router import router as v1_router
   app.include_router(v1_router, prefix="/api/v1")
   ```

---

### 3.4 Directory Structure (Day 3 Deliverables)

```
backend/app/
├── api/
│   ├── __init__.py
│   ├── deps.py                    # NEW: Database dependency
│   └── v1/
│       ├── __init__.py
│       ├── router.py              # NEW: Main v1 router
│       ├── brands.py              # NEW: Brand endpoints
│       ├── templates.py           # NEW: Template endpoints
│       ├── selectors.py           # NEW: DOM Selector endpoints
│       ├── rules.py               # NEW: Code Rule endpoints
│       └── generated_code.py     # NEW: Generated Code endpoints
├── core/
│   ├── __init__.py
│   └── exceptions.py              # NEW: Custom exceptions & handlers
└── main.py                        # UPDATE: Include router & handlers
```

---

## Day 4: Testing & Manual Testing Scripts

### 4.1 Test Infrastructure

#### 4.1.1 Test Configuration (`backend/tests/conftest.py`)
**Purpose:** Shared pytest fixtures for all tests

**Fixtures to Create:**

1. **Test Database Setup:**
   - `event_loop` - Async event loop fixture
   - `test_db_engine` - Create test database engine (opal_safe_code_test)
   - `test_db_session` - Create test database session
   - `test_db` - Yield test session, rollback after each test
   - `test_client` - FastAPI TestClient with test database override

2. **Database Cleanup:**
   - Use `async_sessionmaker` with test engine
   - Create all tables before tests (`Base.metadata.create_all`)
   - Drop all tables after test session
   - Rollback transaction after each test

3. **Seed Data Fixtures:**
   - `test_brand` - Create a test brand for use in tests
   - `test_template` - Create a test template
   - `test_selector` - Create a test selector
   - `test_rule` - Create a test rule
   - `test_generated_code` - Create test generated code

**Configuration:**
- Test database: `opal_safe_code_test`
- Override `get_db` dependency to use test session
- Use pytest-asyncio for async test support

---

### 4.2 Entity Test Suites

Each test file should have **15-20 test cases** covering:

1. **List Endpoints:**
   - Test empty list (0 results)
   - Test list with data (multiple items)
   - Test pagination (skip/limit)
   - Test filtering (brand_id where applicable)

2. **Create Endpoints:**
   - Test successful creation (201)
   - Test with valid data
   - Test validation errors (422)
   - Test foreign key validation (invalid brand_id)
   - Test duplicate constraints (where applicable)

3. **Get by ID Endpoints:**
   - Test successful retrieval (200)
   - Test not found (404)
   - Test invalid ID format (422)

4. **Update Endpoints:**
   - Test successful update (200)
   - Test partial update (only some fields)
   - Test not found (404)
   - Test validation errors (422)
   - Test foreign key validation

5. **Delete Endpoints:**
   - Test successful deletion (204)
   - Test not found (404)
   - Test cascade deletes (where applicable)

**Target:** 80+ total test cases across all 5 entities

---

#### 4.2.1 Brands Tests (`backend/tests/test_brands.py`)
**Test Cases (15-17):**
- List brands (empty, with data, pagination)
- Create brand (success, validation errors, duplicate name)
- Get brand by ID (success, not found)
- Update brand (success, partial, not found, validation)
- Delete brand (success, not found, cascade delete)

---

#### 4.2.2 Templates Tests (`backend/tests/test_templates.py`)
**Test Cases (17-20):**
- List templates (empty, with data, filter by brand_id, pagination)
- Create template (success, invalid brand_id, validation errors)
- Get template by ID (success, not found)
- Update template (success, partial, invalid brand_id, not found, validation)
- Delete template (success, not found)

---

#### 4.2.3 DOM Selectors Tests (`backend/tests/test_selectors.py`)
**Test Cases (17-20):**
- List selectors (empty, with data, filter by brand_id, pagination)
- Create selector (success, invalid brand_id, validation errors)
- Get selector by ID (success, not found)
- Update selector (success, partial, invalid brand_id, not found, validation)
- Delete selector (success, not found)

---

#### 4.2.4 Code Rules Tests (`backend/tests/test_rules.py`)
**Test Cases (17-20):**
- List rules (empty, with data, filter by brand_id, pagination)
- Create rule (success, invalid brand_id, validation errors)
- Get rule by ID (success, not found)
- Update rule (success, partial, invalid brand_id, not found, validation)
- Delete rule (success, not found)

---

#### 4.2.5 Generated Code Tests (`backend/tests/test_generated_code.py`)
**Test Cases (17-20):**
- List generated code (empty, with data, filter by brand_id, pagination)
- Create generated code (success, invalid brand_id, validation errors)
- Get generated code by ID (success, not found)
- Update generated code (success, partial, invalid brand_id, not found, validation)
- Delete generated code (success, not found)

---

### 4.3 Manual Testing Script

#### 4.3.1 cURL Script (`backend/scripts/api_examples.sh`)
**Purpose:** Manual API testing with cURL commands

**Content:**
- All CRUD operations for each entity
- Example requests with proper JSON formatting
- Expected responses documented
- Comments explaining each request
- Use `http://localhost:8000` as base URL

**Script Structure:**
```bash
#!/bin/bash
# Opal Safe Code Generator - API Testing Script
# Usage: ./scripts/api_examples.sh

BASE_URL="http://localhost:8000/api/v1"

echo "=== Testing Brands API ==="
# GET /brands/
curl -X GET "$BASE_URL/brands/" -H "Content-Type: application/json"

# POST /brands/
curl -X POST "$BASE_URL/brands/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Brand", "domain": "test.com", ...}'

# ... etc for all endpoints
```

**Coverage:**
- All 5 entities
- All 5 CRUD operations per entity
- Success cases with example data
- Error cases (invalid IDs, validation errors)

---

## Technical Requirements

### HTTP Status Codes
- `200 OK` - Successful GET, PUT requests
- `201 Created` - Successful POST requests
- `204 No Content` - Successful DELETE requests
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation errors
- `409 Conflict` - Duplicate/constraint violations
- `500 Internal Server Error` - Server errors

### Error Response Format
```json
{
  "detail": "Error message here",
  "status_code": 404
}
```

### Code Standards
- **Async/Await:** All database operations must be async
- **Type Hints:** Full type annotations on all functions
- **Docstrings:** All endpoints must have docstrings
- **Validation:** Use Pydantic schemas for request/response validation
- **Error Handling:** Consistent error handling via exception handlers

### Database Operations
- Use `AsyncSession` for all queries
- Use `await session.execute()` for queries
- Use `await session.commit()` for mutations
- Use `await session.refresh()` to reload entities after creation
- Handle `NoResultFound` from SQLAlchemy

### Testing Standards
- All tests must be async (`async def test_...`)
- Use `pytest.mark.asyncio` where needed (if not using auto mode)
- Each test should be independent (database rollback)
- Use fixtures for common test data
- Assert both status codes and response bodies

---

## Implementation Checklist

### Day 3 Tasks
- [ ] Create `backend/app/api/deps.py` with `get_db()`
- [ ] Create `backend/app/core/exceptions.py` with custom exceptions
- [ ] Create `backend/app/core/__init__.py`
- [ ] Create `backend/app/api/__init__.py`
- [ ] Create `backend/app/api/v1/__init__.py`
- [ ] Create `backend/app/api/v1/router.py` (main router)
- [ ] Create `backend/app/api/v1/brands.py` (all 5 endpoints)
- [ ] Create `backend/app/api/v1/templates.py` (all 5 endpoints)
- [ ] Create `backend/app/api/v1/selectors.py` (all 5 endpoints)
- [ ] Create `backend/app/api/v1/rules.py` (all 5 endpoints)
- [ ] Create `backend/app/api/v1/generated_code.py` (all 5 endpoints)
- [ ] Update `backend/app/main.py` with router and exception handlers
- [ ] Test endpoints manually with FastAPI docs (`/docs`)

### Day 4 Tasks
- [ ] Create `backend/tests/conftest.py` with all fixtures
- [ ] Create `backend/tests/test_brands.py` (15-17 tests)
- [ ] Create `backend/tests/test_templates.py` (17-20 tests)
- [ ] Create `backend/tests/test_selectors.py` (17-20 tests)
- [ ] Create `backend/tests/test_rules.py` (17-20 tests)
- [ ] Create `backend/tests/test_generated_code.py` (17-20 tests)
- [ ] Create `backend/scripts/api_examples.sh` (cURL script)
- [ ] Run full test suite: `pytest -v`
- [ ] Verify 80+ tests pass
- [ ] Test cURL script manually

---

## Verification Steps

### After Day 3 Implementation:
1. Start FastAPI server: `uvicorn app.main:app --reload`
2. Visit `http://localhost:8000/docs` to verify all endpoints appear
3. Test each endpoint manually in Swagger UI
4. Verify proper status codes
5. Verify error handling works correctly

### After Day 4 Implementation:
1. Run test suite: `pytest -v --tb=short`
2. Verify all tests pass (80+ tests)
3. Check test coverage: `pytest --cov=app --cov-report=term-missing`
4. Run cURL script: `bash backend/scripts/api_examples.sh`
5. Verify all endpoints respond correctly
6. Check database after tests (should be clean due to rollback)

### Final Verification:
1. All 25 endpoints (5 entities × 5 operations) functional
2. All tests passing (80+ tests)
3. Error handling consistent across all endpoints
4. Swagger documentation complete and accurate
5. cURL script covers all endpoints

---

## Success Criteria

✅ **Day 3 Complete When:**
- All 25 API endpoints implemented and functional
- Proper HTTP status codes for all operations
- Error handling works consistently
- Swagger docs show all endpoints correctly
- Manual testing in `/docs` succeeds

✅ **Day 4 Complete When:**
- 80+ tests written and passing
- Test coverage > 80% for API endpoints
- All tests use async patterns correctly
- Database rollback working (no test pollution)
- cURL script covers all endpoints
- Ready for Phase 3 (Frontend Integration)

---

## Notes

- Follow FastAPI best practices for dependency injection
- Use SQLAlchemy's `select()` for queries (not `query()`)
- Ensure proper relationship loading when needed
- Consider eager loading for nested relationships if required
- All date/timestamp fields handled automatically by SQLAlchemy
- JSON fields (config) handled as Python dicts

---

**End of Phase 2 Build Plan**

