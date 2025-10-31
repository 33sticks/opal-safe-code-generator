# Phase 2 Implementation Clarifications

## 1. Test Database Strategy ✅

**Confirmed Approach:**

- **Database:** Separate PostgreSQL test database (`opal_safe_code_test`)
- **Engine:** Async PostgreSQL engine using `asyncpg` driver
- **Connection:** `postgresql+asyncpg://postgres:postgres@localhost:5432/opal_safe_code_test`
- **Transaction Strategy:** Rollback after each test (NOT commit)
- **NOT using:** SQLite in-memory database

**Implementation Details:**

```python
# backend/tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base
from app.config import settings

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/opal_safe_code_test"

@pytest.fixture(scope="function")
async def test_db():
    """Create test database session with transaction rollback."""
    # Create test engine
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
    )
    
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    TestSessionLocal = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    # Create session
    async with TestSessionLocal() as session:
        # Begin a transaction
        async with session.begin():
            yield session
            # Rollback transaction after test
            await session.rollback()
    
    # Drop all tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await test_engine.dispose()
```

**Key Points:**
- Uses the same PostgreSQL instance as development (different database name)
- Transaction rollback ensures test isolation (no data pollution)
- Tables created/dropped per test run (or session-scoped for performance)
- Requires test database to exist: `CREATE DATABASE opal_safe_code_test;`

---

## 2. Error Response Format ✅

**Standardized JSON Structure:**

All errors will follow FastAPI's default format with consistent structure:

```json
{
  "detail": "Error message here"
}
```

**Status Code Examples:**

### 404 Not Found
```json
{
  "detail": "Brand with id 999 not found"
}
```
**HTTP Status:** 404

---

### 422 Unprocessable Entity (Validation Error)
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "name"],
      "msg": "Field required",
      "input": {}
    },
    {
      "type": "string_type",
      "loc": ["body", "domain"],
      "msg": "Input should be a valid string",
      "input": null
    }
  ]
}
```
**HTTP Status:** 422

---

### 409 Conflict (Duplicate/Constraint Violation)
```json
{
  "detail": "Brand with name 'VANS' already exists"
}
```
**HTTP Status:** 409

---

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```
**HTTP Status:** 500

---

**Implementation in `app/core/exceptions.py`:**

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, NoResultFound
from app.core.exceptions import NotFoundException, ConflictException

async def not_found_exception_handler(request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message}
    )

async def conflict_exception_handler(request: Request, exc: ConflictException):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message}
    )

async def integrity_error_handler(request: Request, exc: IntegrityError):
    # Extract meaningful message from IntegrityError
    message = "Database constraint violation"
    if "unique" in str(exc.orig).lower():
        message = "Duplicate entry violates unique constraint"
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": message}
    )

# FastAPI's default validation error handler already returns 422 with proper format
# No need to override unless customizing
```

**Note:** FastAPI automatically handles Pydantic validation errors and returns the detailed format shown above for 422 errors.

---

## 3. Generated Code Endpoints ⚠️

**Recommendation: Read-Only Implementation (GET only)**

Since `generated_code` is read-only in the MVP, I recommend implementing **only GET endpoints**:

- ✅ `GET /api/v1/generated-code/` - List all generated code
- ✅ `GET /api/v1/generated-code/{code_id}` - Get by ID
- ❌ `POST /api/v1/generated-code/` - **SKIP** (read-only)
- ❌ `PUT /api/v1/generated-code/{code_id}` - **SKIP** (read-only)
- ❌ `DELETE /api/v1/generated-code/{code_id}` - **SKIP** (read-only)

**Benefits:**
- Aligns with MVP requirements (read-only)
- Simpler implementation
- Clearer API contract
- Can add write operations later if needed

**Alternative:** If you prefer consistency and future-proofing, I can implement full CRUD, but mark POST/PUT/DELETE as "reserved for future use" or return 405 Method Not Allowed.

**Please confirm your preference:**
1. **Option A:** GET only (recommended for MVP)
2. **Option B:** Full CRUD (for consistency/future-proofing)

---

## Updated Endpoint Count

**If Option A (GET only for generated_code):**
- Total endpoints: **22** (instead of 25)
- Brands: 5 endpoints
- Templates: 5 endpoints
- Selectors: 5 endpoints
- Rules: 5 endpoints
- Generated Code: 2 endpoints (GET list, GET by ID)

**If Option B (Full CRUD):**
- Total endpoints: **25** (as originally planned)

---

## Updated Test Count

**If Option A:**
- Generated Code tests: **8-10 tests** (instead of 17-20)
  - List tests (empty, with data, filter, pagination)
  - Get by ID tests (success, not found)
- **Total test target: 70+ tests** (instead of 80+)

**If Option B:**
- Generated Code tests: 17-20 tests (as originally planned)
- **Total test target: 80+ tests**

---

**Please approve Option A or Option B for generated_code endpoints.**

