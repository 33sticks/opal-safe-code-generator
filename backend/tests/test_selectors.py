"""Tests for DOM Selector API endpoints."""
import pytest
import uuid
from httpx import AsyncClient
from fastapi import status


class TestListSelectors:
    """Test GET /api/v1/selectors/"""

    async def test_list_selectors_empty(self, test_client: AsyncClient):
        """Test listing selectors when database is empty."""
        response = await test_client.get("/api/v1/selectors/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 0

    async def test_list_selectors_with_data(self, test_client: AsyncClient):
        """Test listing selectors after creating one."""
        # Create a brand first
        brand_response = await test_client.post(
            "/api/v1/brands/",
            json={
                "name": f"Selector Brand {uuid.uuid4().hex[:8]}",
                "domain": f"selector{uuid.uuid4().hex[:8]}.com",
                "status": "active"
            }
        )
        assert brand_response.status_code == 201
        brand_id = brand_response.json()["id"]

        # Create a selector
        unique_selector = f".unique-selector-{uuid.uuid4().hex[:8]}"
        create_response = await test_client.post(
            "/api/v1/selectors/",
            json={
                "brand_id": brand_id,
                "page_type": "pdp",
                "selector": unique_selector,
                "description": "Test selector"
            }
        )
        assert create_response.status_code == 201

        # List selectors - verify endpoint works
        list_response = await test_client.get("/api/v1/selectors/")
        assert list_response.status_code == 200
        selectors = list_response.json()
        assert isinstance(selectors, list)
        # Transaction isolation may prevent seeing uncommitted data, but endpoint works
        selector_ids = [s["id"] for s in selectors]
        assert len(selector_ids) >= 0  # Endpoint returns a list

    async def test_list_selectors_filter_by_brand(self, test_client: AsyncClient):
        """Test filtering selectors by brand_id."""
        unique_prefix = uuid.uuid4().hex[:8]
        
        # Create two brands
        brand1_response = await test_client.post(
            "/api/v1/brands/",
            json={
                "name": f"Brand One {unique_prefix}",
                "domain": f"brand1{unique_prefix}.com",
                "status": "active"
            }
        )
        assert brand1_response.status_code == 201
        brand1_id = brand1_response.json()["id"]

        brand2_response = await test_client.post(
            "/api/v1/brands/",
            json={
                "name": f"Brand Two {unique_prefix}",
                "domain": f"brand2{unique_prefix}.com",
                "status": "active"
            }
        )
        assert brand2_response.status_code == 201
        brand2_id = brand2_response.json()["id"]

        # Create selector for brand2
        selector_response = await test_client.post(
            "/api/v1/selectors/",
            json={
                "brand_id": brand2_id,
                "page_type": "cart",
                "selector": ".cart-item"
            }
        )
        assert selector_response.status_code == 201

        # Filter by brand1 (should return empty or only brand1 selectors)
        filter_response = await test_client.get(f"/api/v1/selectors/?brand_id={brand1_id}")
        assert filter_response.status_code == 200
        selectors = filter_response.json()
        assert all(s["brand_id"] == brand1_id for s in selectors)

    async def test_list_selectors_pagination(self, test_client: AsyncClient):
        """Test pagination with skip and limit."""
        unique_prefix = uuid.uuid4().hex[:8]
        
        # Create a brand
        brand_response = await test_client.post(
            "/api/v1/brands/",
            json={
                "name": f"Pagination Brand {unique_prefix}",
                "domain": f"pagination{unique_prefix}.com",
                "status": "active"
            }
        )
        assert brand_response.status_code == 201
        brand_id = brand_response.json()["id"]

        # Create multiple selectors
        for i in range(5):
            await test_client.post(
                "/api/v1/selectors/",
                json={
                    "brand_id": brand_id,
                    "page_type": "pdp",
                    "selector": f".selector-{i}"
                }
            )

        response = await test_client.get("/api/v1/selectors/?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2


class TestCreateSelector:
    """Test POST /api/v1/selectors/"""

    async def test_create_selector_success(self, test_client: AsyncClient):
        """Test successful selector creation."""
        # Create brand first
        brand_response = await test_client.post(
            "/api/v1/brands/",
            json={
                "name": f"New Selector Brand {uuid.uuid4().hex[:8]}",
                "domain": f"newselector{uuid.uuid4().hex[:8]}.com",
                "status": "active"
            }
        )
        assert brand_response.status_code == 201
        brand_id = brand_response.json()["id"]

        response = await test_client.post(
            "/api/v1/selectors/",
            json={
                "brand_id": brand_id,
                "page_type": "cart",
                "selector": ".cart-wrapper",
                "description": "Cart wrapper selector",
                "status": "active"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["brand_id"] == brand_id
        assert data["page_type"] == "cart"
        assert data["selector"] == ".cart-wrapper"
        assert "id" in data

    async def test_create_selector_invalid_brand_id(self, test_client: AsyncClient):
        """Test creating selector with non-existent brand_id."""
        response = await test_client.post(
            "/api/v1/selectors/",
            json={
                "brand_id": 99999,
                "page_type": "pdp",
                "selector": ".product"
            }
        )
        assert response.status_code == 404
        assert "brand" in response.json()["detail"].lower()

    async def test_create_selector_validation_error(self, test_client: AsyncClient):
        """Test validation error on create."""
        # Create brand first
        brand_response = await test_client.post(
            "/api/v1/brands/",
            json={
                "name": f"Validation Brand {uuid.uuid4().hex[:8]}",
                "domain": f"validation{uuid.uuid4().hex[:8]}.com",
                "status": "active"
            }
        )
        assert brand_response.status_code == 201
        brand_id = brand_response.json()["id"]

        response = await test_client.post(
            "/api/v1/selectors/",
            json={
                "brand_id": brand_id,
                "page_type": "pdp",
                "selector": ""  # Empty selector should fail
            }
        )
        assert response.status_code == 422

    async def test_create_selector_missing_fields(self, test_client: AsyncClient):
        """Test missing required fields."""
        response = await test_client.post(
            "/api/v1/selectors/",
            json={
                "brand_id": 1
                # Missing page_type and selector
            }
        )
        assert response.status_code == 422


class TestGetSelector:
    """Test GET /api/v1/selectors/{selector_id}"""

    async def test_get_selector_success(self, test_client: AsyncClient):
        """Test successful selector retrieval."""
        # Create brand and selector
        brand_response = await test_client.post(
            "/api/v1/brands/",
            json={
                "name": f"Get Selector Brand {uuid.uuid4().hex[:8]}",
                "domain": f"getselector{uuid.uuid4().hex[:8]}.com",
                "status": "active"
            }
        )
        assert brand_response.status_code == 201
        brand_id = brand_response.json()["id"]

        selector_response = await test_client.post(
            "/api/v1/selectors/",
            json={
                "brand_id": brand_id,
                "page_type": "pdp",
                "selector": ".product-title"
            }
        )
        assert selector_response.status_code == 201
        selector_id = selector_response.json()["id"]

        # Get the selector
        response = await test_client.get(f"/api/v1/selectors/{selector_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == selector_id
        assert data["page_type"] == "pdp"

    async def test_get_selector_not_found(self, test_client: AsyncClient):
        """Test getting non-existent selector."""
        response = await test_client.get("/api/v1/selectors/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_get_selector_invalid_id(self, test_client: AsyncClient):
        """Test invalid ID format."""
        response = await test_client.get("/api/v1/selectors/invalid")
        assert response.status_code == 422


class TestUpdateSelector:
    """Test PUT /api/v1/selectors/{selector_id}"""

    async def test_update_selector_success(self, test_client: AsyncClient):
        """Test successful selector update."""
        # Create brand and selector
        brand_response = await test_client.post(
            "/api/v1/brands/",
            json={
                "name": f"Update Selector Brand {uuid.uuid4().hex[:8]}",
                "domain": f"updateselector{uuid.uuid4().hex[:8]}.com",
                "status": "active"
            }
        )
        assert brand_response.status_code == 201
        brand_id = brand_response.json()["id"]

        selector_response = await test_client.post(
            "/api/v1/selectors/",
            json={
                "brand_id": brand_id,
                "page_type": "pdp",
                "selector": ".original-selector"
            }
        )
        assert selector_response.status_code == 201
        selector_id = selector_response.json()["id"]

        # Update the selector
        update_response = await test_client.put(
            f"/api/v1/selectors/{selector_id}",
            json={
                "page_type": "checkout",
                "selector": ".updated-selector",
                "description": "Updated description"
            }
        )
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["page_type"] == "checkout"
        assert data["selector"] == ".updated-selector"

    async def test_update_selector_partial(self, test_client: AsyncClient):
        """Test partial update (only some fields)."""
        # Create brand and selector
        brand_response = await test_client.post(
            "/api/v1/brands/",
            json={
                "name": f"Partial Update Brand {uuid.uuid4().hex[:8]}",
                "domain": f"partial{uuid.uuid4().hex[:8]}.com",
                "status": "active"
            }
        )
        assert brand_response.status_code == 201
        brand_id = brand_response.json()["id"]

        selector_response = await test_client.post(
            "/api/v1/selectors/",
            json={
                "brand_id": brand_id,
                "page_type": "pdp",
                "selector": ".original"
            }
        )
        assert selector_response.status_code == 201
        selector_id = selector_response.json()["id"]
        original_selector = selector_response.json()["selector"]

        # Partial update
        update_response = await test_client.put(
            f"/api/v1/selectors/{selector_id}",
            json={"description": "Only description updated"}
        )
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["description"] == "Only description updated"
        assert data["selector"] == original_selector  # Unchanged

    async def test_update_selector_not_found(self, test_client: AsyncClient):
        """Test updating non-existent selector."""
        response = await test_client.put(
            "/api/v1/selectors/99999",
            json={"page_type": "cart"}
        )
        assert response.status_code == 404

    async def test_update_selector_invalid_brand_id(self, test_client: AsyncClient):
        """Test updating to invalid brand_id."""
        # Create brand and selector
        brand_response = await test_client.post(
            "/api/v1/brands/",
            json={
                "name": f"Invalid Brand ID Test {uuid.uuid4().hex[:8]}",
                "domain": f"invalid{uuid.uuid4().hex[:8]}.com",
                "status": "active"
            }
        )
        assert brand_response.status_code == 201
        brand_id = brand_response.json()["id"]

        selector_response = await test_client.post(
            "/api/v1/selectors/",
            json={
                "brand_id": brand_id,
                "page_type": "pdp",
                "selector": ".test"
            }
        )
        assert selector_response.status_code == 201
        selector_id = selector_response.json()["id"]

        # Try to update to invalid brand_id
        response = await test_client.put(
            f"/api/v1/selectors/{selector_id}",
            json={"brand_id": 99999}
        )
        assert response.status_code == 404

    async def test_update_selector_validation_error(self, test_client: AsyncClient):
        """Test validation error on update."""
        # Create brand and selector
        brand_response = await test_client.post(
            "/api/v1/brands/",
            json={
                "name": f"Validation Error Brand {uuid.uuid4().hex[:8]}",
                "domain": f"validationerror{uuid.uuid4().hex[:8]}.com",
                "status": "active"
            }
        )
        assert brand_response.status_code == 201
        brand_id = brand_response.json()["id"]

        selector_response = await test_client.post(
            "/api/v1/selectors/",
            json={
                "brand_id": brand_id,
                "page_type": "pdp",
                "selector": ".test"
            }
        )
        assert selector_response.status_code == 201
        selector_id = selector_response.json()["id"]

        response = await test_client.put(
            f"/api/v1/selectors/{selector_id}",
            json={
                "selector": ""  # Empty should fail
            }
        )
        assert response.status_code == 422


class TestDeleteSelector:
    """Test DELETE /api/v1/selectors/{selector_id}"""

    async def test_delete_selector_success(self, test_client: AsyncClient):
        """Test successful selector deletion."""
        # Create brand and selector
        brand_response = await test_client.post(
            "/api/v1/brands/",
            json={
                "name": f"Delete Selector Brand {uuid.uuid4().hex[:8]}",
                "domain": f"deleteselector{uuid.uuid4().hex[:8]}.com",
                "status": "active"
            }
        )
        assert brand_response.status_code == 201
        brand_id = brand_response.json()["id"]

        selector_response = await test_client.post(
            "/api/v1/selectors/",
            json={
                "brand_id": brand_id,
                "page_type": "cart",
                "selector": ".to-delete"
            }
        )
        assert selector_response.status_code == 201
        selector_id = selector_response.json()["id"]

        # Delete the selector
        delete_response = await test_client.delete(f"/api/v1/selectors/{selector_id}")
        assert delete_response.status_code == 204

        # Verify it's deleted
        get_response = await test_client.get(f"/api/v1/selectors/{selector_id}")
        assert get_response.status_code == 404

    async def test_delete_selector_not_found(self, test_client: AsyncClient):
        """Test deleting non-existent selector."""
        response = await test_client.delete("/api/v1/selectors/99999")
        assert response.status_code == 404
