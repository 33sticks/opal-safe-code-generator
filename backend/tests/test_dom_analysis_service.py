"""Tests for DOM Analysis Service."""
import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from anthropic import APIError

from app.services.dom_analysis_service import DomAnalysisService
from app.schemas.dom_analysis import DomAnalysisResult, DomSelector, DomRelationships


# Sample HTML for testing
SAMPLE_HTML = """
<div class="product-card" data-product-id="123">
    <h1 class="product-title">Test Product</h1>
    <button data-test-id="add-to-cart">Add to Cart</button>
    <span class="price">$99.99</span>
</div>
"""

# Sample valid JSON response
SAMPLE_JSON_RESPONSE = {
    "selectors": [
        {
            "selector": "button[data-test-id='add-to-cart']",
            "description": "Add to cart button on PDP",
            "stability_score": 0.95,
            "element_type": "interactive",
            "parent": "div.product-card",
            "children": [],
            "siblings": ["span.price"]
        },
        {
            "selector": "h1.product-title",
            "description": "Product title heading",
            "stability_score": 0.7,
            "element_type": "content",
            "parent": "div.product-card",
            "children": [],
            "siblings": []
        }
    ],
    "relationships": {
        "containers": ["div.product-card"],
        "interactive": ["button[data-test-id='add-to-cart']"],
        "content": ["h1.product-title", "span.price"]
    },
    "patterns": [
        "Product cards use consistent structure with data-product-id attribute",
        "All interactive elements have data-test-id attributes"
    ],
    "recommendations": [
        "Use data-test-id attributes for most stable selectors",
        "Product card container repeats - good for iteration"
    ],
    "warnings": [
        "Class names use utility classes - may change during redesigns"
    ]
}


class TestDomAnalysisService:
    """Tests for DomAnalysisService."""
    
    @pytest.fixture
    def mock_anthropic_client(self):
        """Create a mock AsyncAnthropic client."""
        with patch('app.services.dom_analysis_service.AsyncAnthropic') as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            yield mock_client
    
    @pytest.fixture
    def service(self, mock_anthropic_client):
        """Create service instance with mocked client."""
        with patch('app.services.dom_analysis_service.settings') as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = "test-api-key"
            service = DomAnalysisService()
            return service
    
    async def test_analyze_html_success(self, service, mock_anthropic_client):
        """Test successful HTML analysis with valid JSON response."""
        # Mock the API response
        mock_message = MagicMock()
        mock_content_block = MagicMock()
        mock_content_block.text = json.dumps(SAMPLE_JSON_RESPONSE)
        mock_message.content = [mock_content_block]
        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_message)
        
        # Call the service
        result = await service.analyze_html(
            html=SAMPLE_HTML,
            page_type="PDP",
            brand_name="TestBrand"
        )
        
        # Verify result
        assert isinstance(result, DomAnalysisResult)
        assert len(result.selectors) == 2
        assert result.selectors[0].selector == "button[data-test-id='add-to-cart']"
        assert result.selectors[0].stability_score == 0.95
        assert len(result.patterns) == 2
        assert len(result.recommendations) == 2
        assert len(result.warnings) == 1
        
        # Verify API was called correctly
        mock_anthropic_client.messages.create.assert_called_once()
        call_args = mock_anthropic_client.messages.create.call_args
        assert call_args.kwargs["model"] == "claude-sonnet-4-20250514"
        assert call_args.kwargs["max_tokens"] == 4000
        assert len(call_args.kwargs["messages"]) == 1
        assert call_args.kwargs["messages"][0]["role"] == "user"
        assert "PDP" in call_args.kwargs["messages"][0]["content"]
        assert "TestBrand" in call_args.kwargs["messages"][0]["content"]
    
    async def test_analyze_html_with_markdown_blocks(self, service, mock_anthropic_client):
        """Test handling of JSON wrapped in markdown code blocks."""
        # Mock response with markdown code blocks
        json_with_markdown = f"```json\n{json.dumps(SAMPLE_JSON_RESPONSE)}\n```"
        
        mock_message = MagicMock()
        mock_content_block = MagicMock()
        mock_content_block.text = json_with_markdown
        mock_message.content = [mock_content_block]
        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_message)
        
        result = await service.analyze_html(
            html=SAMPLE_HTML,
            page_type="PDP"
        )
        
        assert isinstance(result, DomAnalysisResult)
        assert len(result.selectors) == 2
        
        # Test with ``` blocks (no json)
        json_with_backticks = f"```\n{json.dumps(SAMPLE_JSON_RESPONSE)}\n```"
        mock_content_block.text = json_with_backticks
        mock_message.content = [mock_content_block]
        
        result2 = await service.analyze_html(
            html=SAMPLE_HTML,
            page_type="PDP"
        )
        
        assert isinstance(result2, DomAnalysisResult)
        assert len(result2.selectors) == 2
    
    async def test_analyze_html_malformed_json(self, service, mock_anthropic_client):
        """Test handling of malformed JSON gracefully."""
        # Mock response with invalid JSON
        mock_message = MagicMock()
        mock_content_block = MagicMock()
        mock_content_block.text = "{ invalid json }"
        mock_message.content = [mock_content_block]
        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_message)
        
        with pytest.raises(ValueError) as exc_info:
            await service.analyze_html(
                html=SAMPLE_HTML,
                page_type="PDP"
            )
        
        assert "parse" in str(exc_info.value).lower() or "json" in str(exc_info.value).lower()
    
    async def test_analyze_html_missing_fields(self, service, mock_anthropic_client):
        """Test validation of required fields in response."""
        # Mock response missing required fields
        incomplete_response = {
            "selectors": [],
            # Missing relationships, patterns, recommendations
        }
        
        mock_message = MagicMock()
        mock_content_block = MagicMock()
        mock_content_block.text = json.dumps(incomplete_response)
        mock_message.content = [mock_content_block]
        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_message)
        
        with pytest.raises(ValueError) as exc_info:
            await service.analyze_html(
                html=SAMPLE_HTML,
                page_type="PDP"
            )
        
        # Should raise ValidationError from Pydantic or ValueError from validation
        error_msg = str(exc_info.value).lower()
        assert "relationships" in error_msg or "missing" in error_msg or "required" in error_msg
    
    async def test_analyze_html_api_error(self, service, mock_anthropic_client):
        """Test handling of API errors."""
        # Mock API error - create a simple APIError instance
        # APIError requires message, request, and optional body
        from httpx import Request
        request = Request("POST", "https://api.anthropic.com/v1/messages")
        api_error = APIError(message="Rate limit exceeded", request=request, body=None)
        mock_anthropic_client.messages.create = AsyncMock(side_effect=api_error)
        
        with pytest.raises(Exception) as exc_info:
            await service.analyze_html(
                html=SAMPLE_HTML,
                page_type="PDP"
            )
        
        assert "analyze" in str(exc_info.value).lower() or "failed" in str(exc_info.value).lower()
    
    async def test_analyze_html_empty_html(self, service):
        """Test rejection of empty HTML input."""
        with pytest.raises(ValueError) as exc_info:
            await service.analyze_html(
                html="",
                page_type="PDP"
            )
        
        assert "empty" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()
        
        # Test with whitespace only
        with pytest.raises(ValueError):
            await service.analyze_html(
                html="   ",
                page_type="PDP"
            )
    
    async def test_analyze_html_empty_page_type(self, service):
        """Test rejection of empty page_type."""
        with pytest.raises(ValueError) as exc_info:
            await service.analyze_html(
                html=SAMPLE_HTML,
                page_type=""
            )
        
        assert "page_type" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()
    
    def test_init_without_api_key(self):
        """Test that service raises error if API key is missing."""
        with patch('app.services.dom_analysis_service.settings') as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = None
            
            with pytest.raises(ValueError) as exc_info:
                DomAnalysisService()
            
            assert "api_key" in str(exc_info.value).lower() or "not set" in str(exc_info.value).lower()
    
    async def test_analyze_html_with_minimal_response(self, service, mock_anthropic_client):
        """Test handling of minimal valid response."""
        minimal_response = {
            "selectors": [],
            "relationships": {
                "containers": [],
                "interactive": [],
                "content": []
            },
            "patterns": [],
            "recommendations": []
        }
        
        mock_message = MagicMock()
        mock_content_block = MagicMock()
        mock_content_block.text = json.dumps(minimal_response)
        mock_message.content = [mock_content_block]
        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_message)
        
        result = await service.analyze_html(
            html=SAMPLE_HTML,
            page_type="PDP"
        )
        
        assert isinstance(result, DomAnalysisResult)
        assert len(result.selectors) == 0
        assert len(result.patterns) == 0
        assert len(result.warnings) == 0  # Should default to empty list
    
    async def test_analyze_html_with_string_content(self, service, mock_anthropic_client):
        """Test handling of string content in response."""
        mock_message = MagicMock()
        # Simulate string content (not a list)
        mock_message.content = json.dumps(SAMPLE_JSON_RESPONSE)
        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_message)
        
        result = await service.analyze_html(
            html=SAMPLE_HTML,
            page_type="PDP"
        )
        
        assert isinstance(result, DomAnalysisResult)
        assert len(result.selectors) == 2
    
    async def test_analyze_html_with_invalid_relationships_structure(self, service, mock_anthropic_client):
        """Test handling of invalid relationships structure."""
        invalid_response = {
            "selectors": [],
            "relationships": "not a dict",  # Should be dict
            "patterns": [],
            "recommendations": []
        }
        
        mock_message = MagicMock()
        mock_content_block = MagicMock()
        mock_content_block.text = json.dumps(invalid_response)
        mock_message.content = [mock_content_block]
        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_message)
        
        with pytest.raises(ValueError) as exc_info:
            await service.analyze_html(
                html=SAMPLE_HTML,
                page_type="PDP"
            )
        
        assert "relationships" in str(exc_info.value).lower() or "dictionary" in str(exc_info.value).lower()
    
    async def test_analyze_html_with_missing_relationship_fields(self, service, mock_anthropic_client):
        """Test handling of missing optional relationship fields."""
        response_missing_rel_fields = {
            "selectors": [],
            "relationships": {
                "containers": []
                # Missing interactive and content - should use defaults
            },
            "patterns": [],
            "recommendations": []
        }
        
        mock_message = MagicMock()
        mock_content_block = MagicMock()
        mock_content_block.text = json.dumps(response_missing_rel_fields)
        mock_message.content = [mock_content_block]
        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_message)
        
        # Should not raise error, but log warning
        result = await service.analyze_html(
            html=SAMPLE_HTML,
            page_type="PDP"
        )
        
        assert isinstance(result, DomAnalysisResult)
        # Pydantic will use defaults for missing fields
    
    async def test_analyze_html_with_json_embedded_in_text(self, service, mock_anthropic_client):
        """Test extraction of JSON from text that contains other content."""
        text_with_json = f"""
        Here is some explanation text.
        {json.dumps(SAMPLE_JSON_RESPONSE)}
        More text after.
        """
        
        mock_message = MagicMock()
        mock_content_block = MagicMock()
        mock_content_block.text = text_with_json
        mock_message.content = [mock_content_block]
        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_message)
        
        # Should attempt to extract JSON
        result = await service.analyze_html(
            html=SAMPLE_HTML,
            page_type="PDP"
        )
        
        assert isinstance(result, DomAnalysisResult)
        assert len(result.selectors) == 2
    
    async def test_analyze_html_with_invalid_stability_score(self, service, mock_anthropic_client):
        """Test validation of stability_score range."""
        invalid_response = {
            "selectors": [
                {
                    "selector": "button.test",
                    "description": "Test button",
                    "stability_score": 1.5,  # Invalid: > 1.0
                    "element_type": "interactive",
                    "parent": None,
                    "children": [],
                    "siblings": []
                }
            ],
            "relationships": {
                "containers": [],
                "interactive": [],
                "content": []
            },
            "patterns": [],
            "recommendations": []
        }
        
        mock_message = MagicMock()
        mock_content_block = MagicMock()
        mock_content_block.text = json.dumps(invalid_response)
        mock_message.content = [mock_content_block]
        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_message)
        
        # Pydantic should raise ValidationError
        with pytest.raises(Exception):  # Could be ValidationError or ValueError
            await service.analyze_html(
                html=SAMPLE_HTML,
                page_type="PDP"
            )

