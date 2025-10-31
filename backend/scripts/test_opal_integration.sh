#!/bin/bash
# Manual testing script for Opal integration endpoints
# Usage: ./scripts/test_opal_integration.sh

set -e

BASE_URL="http://localhost:8000"
DISCOVERY_URL="${BASE_URL}/api/v1/opal/discovery"
GENERATE_CODE_URL="${BASE_URL}/api/v1/opal/generate-code"

echo "=========================================="
echo "Opal Integration Testing Script"
echo "=========================================="
echo ""

echo "1. Testing Discovery Endpoint"
echo "----------------------------"
echo "GET ${DISCOVERY_URL}"
echo ""

if command -v jq &> /dev/null; then
    curl -s "${DISCOVERY_URL}" | jq '.'
else
    curl -s "${DISCOVERY_URL}" | python3 -m json.tool
fi

echo ""
echo ""

echo "2. Testing Generate Code Endpoint"
echo "--------------------------------"
echo "POST ${GENERATE_CODE_URL}"
echo ""

# Test with VANS brand (should exist if seed data is loaded)
echo "Testing with VANS brand..."
echo ""

if command -v jq &> /dev/null; then
    curl -X POST "${GENERATE_CODE_URL}" \
        -H "Content-Type: application/json" \
        -d '{
            "parameters": {
                "brand_name": "VANS",
                "test_type": "checkout",
                "test_description": "Change checkout button color to red and add urgency text"
            }
        }' | jq '.'
else
    curl -X POST "${GENERATE_CODE_URL}" \
        -H "Content-Type: application/json" \
        -d '{
            "parameters": {
                "brand_name": "VANS",
                "test_type": "checkout",
                "test_description": "Change checkout button color to red and add urgency text"
            }
        }' | python3 -m json.tool
fi

echo ""
echo ""

echo "3. Testing with Different Test Type"
echo "-----------------------------------"
echo "Testing with PDP test type..."
echo ""

if command -v jq &> /dev/null; then
    curl -X POST "${GENERATE_CODE_URL}" \
        -H "Content-Type: application/json" \
        -d '{
            "parameters": {
                "brand_name": "VANS",
                "test_type": "pdp",
                "test_description": "Highlight product title with yellow background"
            }
        }' | jq '.'
else
    curl -X POST "${GENERATE_CODE_URL}" \
        -H "Content-Type: application/json" \
        -d '{
            "parameters": {
                "brand_name": "VANS",
                "test_type": "pdp",
                "test_description": "Highlight product title with yellow background"
            }
        }' | python3 -m json.tool
fi

echo ""
echo ""

echo "4. Testing Error Cases"
echo "---------------------"
echo "Testing with non-existent brand..."
echo ""

if command -v jq &> /dev/null; then
    curl -X POST "${GENERATE_CODE_URL}" \
        -H "Content-Type: application/json" \
        -d '{
            "parameters": {
                "brand_name": "NonExistentBrand",
                "test_type": "checkout",
                "test_description": "Test description"
            }
        }' | jq '.'
else
    curl -X POST "${GENERATE_CODE_URL}" \
        -H "Content-Type: application/json" \
        -d '{
            "parameters": {
                "brand_name": "NonExistentBrand",
                "test_type": "checkout",
                "test_description": "Test description"
            }
        }' | python3 -m json.tool
fi

echo ""
echo ""

echo "5. Testing Missing Parameters"
echo "----------------------------"
echo "Testing without brand_name..."
echo ""

if command -v jq &> /dev/null; then
    curl -X POST "${GENERATE_CODE_URL}" \
        -H "Content-Type: application/json" \
        -d '{
            "parameters": {
                "test_type": "checkout",
                "test_description": "Test description"
            }
        }' | jq '.'
else
    curl -X POST "${GENERATE_CODE_URL}" \
        -H "Content-Type: application/json" \
        -d '{
            "parameters": {
                "test_type": "checkout",
                "test_description": "Test description"
            }
        }' | python3 -m json.tool
fi

echo ""
echo "=========================================="
echo "Testing Complete"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "1. Verify generated code appears in admin dashboard at http://localhost:5173"
echo "2. Check database for new generated_code entries"
echo "3. Review generated code for quality and safety"
echo ""
echo "To verify in database:"
echo "  psql -d opal_safe_code -c 'SELECT id, brand_id, confidence_score, created_at FROM generated_code ORDER BY created_at DESC LIMIT 5;'"
echo ""

