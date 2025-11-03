#!/bin/bash
# Opal Safe Code Generator - API Testing Script
# Usage: ./scripts/api_examples.sh
# Note: Ensure FastAPI server is running on http://localhost:8000

BASE_URL="http://localhost:8000/api/v1"

echo "========================================="
echo "Opal Safe Code Generator - API Testing"
echo "========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Store created IDs for later use
BRAND_ID=""
TEMPLATE_ID=""
SELECTOR_ID=""
RULE_ID=""
GENERATED_CODE_ID=""

echo -e "${BLUE}=== Testing Brands API ===${NC}"
echo ""

echo "1. GET /brands/ - List all brands"
curl -X GET "$BASE_URL/brands/" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

echo "2. POST /brands/ - Create a new brand"
BRAND_RESPONSE=$(curl -s -X POST "$BASE_URL/brands/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API Test Brand",
    "domain": "apitest.com",
    "status": "active",
    "code_template": {"test": true}
  }')
echo "$BRAND_RESPONSE"
BRAND_ID=$(echo "$BRAND_RESPONSE" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
echo "Created Brand ID: $BRAND_ID"
echo ""

echo "3. GET /brands/{id} - Get brand by ID"
curl -X GET "$BASE_URL/brands/$BRAND_ID" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

echo "4. PUT /brands/{id} - Update brand"
curl -X PUT "$BASE_URL/brands/$BRAND_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API Test Brand Updated",
    "domain": "apitest-updated.com"
  }' \
  -w "\nStatus: %{http_code}\n\n"

echo "5. GET /brands/ - List brands (pagination)"
curl -X GET "$BASE_URL/brands/?skip=0&limit=10" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

echo ""
echo -e "${BLUE}=== Testing Page Type Knowledge API ===${NC}"
echo ""

echo "6. GET /page-type-knowledge/ - List all page type knowledge"
curl -X GET "$BASE_URL/page-type-knowledge/" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

echo "7. POST /page-type-knowledge/ - Create a new page type knowledge entry"
TEMPLATE_RESPONSE=$(curl -s -X POST "$BASE_URL/page-type-knowledge/" \
  -H "Content-Type: application/json" \
  -d "{
    \"brand_id\": $BRAND_ID,
    \"test_type\": \"pdp\",
    \"template_code\": \"<div>API Test Knowledge</div>\",
    \"description\": \"Test page knowledge created via API\",
    \"version\": \"1.0\",
    \"is_active\": true
  }")
echo "$TEMPLATE_RESPONSE"
TEMPLATE_ID=$(echo "$TEMPLATE_RESPONSE" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
echo "Created Page Type Knowledge ID: $TEMPLATE_ID"
echo ""

echo "8. GET /page-type-knowledge/{id} - Get page type knowledge by ID"
curl -X GET "$BASE_URL/page-type-knowledge/$TEMPLATE_ID" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

echo "9. PUT /page-type-knowledge/{id} - Update page type knowledge"
curl -X PUT "$BASE_URL/page-type-knowledge/$TEMPLATE_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "template_code": "<div>Updated API Test Knowledge</div>",
    "description": "Updated description"
  }' \
  -w "\nStatus: %{http_code}\n\n"

echo "10. GET /page-type-knowledge/?brand_id={id} - Filter page type knowledge by brand"
curl -X GET "$BASE_URL/page-type-knowledge/?brand_id=$BRAND_ID" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

echo ""
echo -e "${BLUE}=== Testing DOM Selectors API ===${NC}"
echo ""

echo "11. GET /selectors/ - List all selectors"
curl -X GET "$BASE_URL/selectors/" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

echo "12. POST /selectors/ - Create a new selector"
SELECTOR_RESPONSE=$(curl -s -X POST "$BASE_URL/selectors/" \
  -H "Content-Type: application/json" \
  -d "{
    \"brand_id\": $BRAND_ID,
    \"page_type\": \"pdp\",
    \"selector\": \".api-test-selector\",
    \"description\": \"Test selector created via API\",
    \"status\": \"active\"
  }")
echo "$SELECTOR_RESPONSE"
SELECTOR_ID=$(echo "$SELECTOR_RESPONSE" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
echo "Created Selector ID: $SELECTOR_ID"
echo ""

echo "13. GET /selectors/{id} - Get selector by ID"
curl -X GET "$BASE_URL/selectors/$SELECTOR_ID" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

echo "14. PUT /selectors/{id} - Update selector"
curl -X PUT "$BASE_URL/selectors/$SELECTOR_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "selector": ".updated-api-test-selector",
    "description": "Updated selector description"
  }' \
  -w "\nStatus: %{http_code}\n\n"

echo "15. GET /selectors/?brand_id={id} - Filter selectors by brand"
curl -X GET "$BASE_URL/selectors/?brand_id=$BRAND_ID" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

echo ""
echo -e "${BLUE}=== Testing Code Rules API ===${NC}"
echo ""

echo "16. GET /rules/ - List all rules"
curl -X GET "$BASE_URL/rules/" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

echo "17. POST /rules/ - Create a new rule"
RULE_RESPONSE=$(curl -s -X POST "$BASE_URL/rules/" \
  -H "Content-Type: application/json" \
  -d "{
    \"brand_id\": $BRAND_ID,
    \"rule_type\": \"forbidden_pattern\",
    \"rule_content\": \"eval(\",
    \"priority\": 5
  }")
echo "$RULE_RESPONSE"
RULE_ID=$(echo "$RULE_RESPONSE" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
echo "Created Rule ID: $RULE_ID"
echo ""

echo "18. GET /rules/{id} - Get rule by ID"
curl -X GET "$BASE_URL/rules/$RULE_ID" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

echo "19. PUT /rules/{id} - Update rule"
curl -X PUT "$BASE_URL/rules/$RULE_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "rule_content": "document.write(",
    "priority": 8
  }' \
  -w "\nStatus: %{http_code}\n\n"

echo "20. GET /rules/?brand_id={id} - Filter rules by brand"
curl -X GET "$BASE_URL/rules/?brand_id=$BRAND_ID" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

echo ""
echo -e "${BLUE}=== Testing Generated Code API (Read-Only) ===${NC}"
echo ""

echo "21. GET /generated-code/ - List all generated code"
curl -X GET "$BASE_URL/generated-code/" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

echo "22. GET /generated-code/?brand_id={id} - Filter generated code by brand"
curl -X GET "$BASE_URL/generated-code/?brand_id=$BRAND_ID" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

# Try to get a generated code record if any exist (from seed data)
echo "23. GET /generated-code/{id} - Get generated code by ID (if exists)"
# Using ID 1 as example (may not exist)
curl -X GET "$BASE_URL/generated-code/1" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

echo ""
echo -e "${BLUE}=== Testing Error Cases ===${NC}"
echo ""

echo "24. GET /brands/{id} - Non-existent brand (404)"
curl -X GET "$BASE_URL/brands/99999" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

echo "25. POST /brands/ - Duplicate name (409)"
curl -X POST "$BASE_URL/brands/" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"API Test Brand Updated\",
    \"domain\": \"duplicate.com\"
  }" \
  -w "\nStatus: %{http_code}\n\n"

echo "26. POST /page-type-knowledge/ - Invalid brand_id (404)"
curl -X POST "$BASE_URL/page-type-knowledge/" \
  -H "Content-Type: application/json" \
  -d '{
    "brand_id": 99999,
    "test_type": "pdp",
    "template_code": "<div>Test</div>"
  }' \
  -w "\nStatus: %{http_code}\n\n"

echo "27. POST /brands/ - Validation error (422)"
curl -X POST "$BASE_URL/brands/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "",
    "domain": "test.com"
  }' \
  -w "\nStatus: %{http_code}\n\n"

echo ""
echo -e "${BLUE}=== Cleanup - Delete Created Resources ===${NC}"
echo ""

echo "28. DELETE /rules/{id}"
curl -X DELETE "$BASE_URL/rules/$RULE_ID" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

echo "29. DELETE /selectors/{id}"
curl -X DELETE "$BASE_URL/selectors/$SELECTOR_ID" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

echo "30. DELETE /page-type-knowledge/{id}"
curl -X DELETE "$BASE_URL/page-type-knowledge/$TEMPLATE_ID" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

echo "31. DELETE /brands/{id}"
curl -X DELETE "$BASE_URL/brands/$BRAND_ID" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

echo ""
echo -e "${GREEN}=== API Testing Complete ===${NC}"
echo ""

