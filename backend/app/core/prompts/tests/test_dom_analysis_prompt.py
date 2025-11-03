"""Tests for DOM analysis prompt builder."""
import pytest
from app.core.prompts.dom_analysis_prompt import (
    get_dom_analysis_prompt,
    sanitize_html_for_analysis,
    DOM_ANALYSIS_PROMPT_TEMPLATE
)


# Sample HTML fixtures
PRODUCT_CARD_HTML = """
<div class="product-card" data-product-id="12345" data-test-id="product-card">
    <img src="/product.jpg" alt="Product" class="product-image" data-test-id="product-image" />
    <div class="product-info">
        <h2 class="product-title" data-test-id="product-title">Vans Old Skool</h2>
        <p class="product-price" data-test-id="product-price">$65.00</p>
        <div class="product-actions">
            <button class="btn btn-primary" data-test-id="add-to-cart">Add to Cart</button>
            <button class="btn btn-secondary" data-test-id="wishlist-btn">♡</button>
        </div>
    </div>
</div>
"""

HERO_BANNER_HTML = """
<section class="hero-banner" data-test-id="hero-section">
    <div class="hero-content">
        <h1 class="hero-title" data-test-id="hero-title">New Collection</h1>
        <p class="hero-subtitle" data-test-id="hero-subtitle">Discover our latest styles</p>
        <a href="/shop" class="btn btn-cta" data-test-id="hero-cta-button">Shop Now</a>
    </div>
    <img src="/hero.jpg" alt="Hero" class="hero-image" data-test-id="hero-image" />
</section>
"""

FORM_HTML = """
<form class="checkout-form" data-test-id="checkout-form" action="/checkout" method="POST">
    <div class="form-group">
        <label for="email" data-test-id="email-label">Email</label>
        <input type="email" id="email" name="email" class="form-input" data-test-id="email-input" required />
    </div>
    <div class="form-group">
        <label for="password" data-test-id="password-label">Password</label>
        <input type="password" id="password" name="password" class="form-input" data-test-id="password-input" required />
    </div>
    <div class="form-actions">
        <button type="submit" class="btn btn-primary" data-test-id="submit-button">Submit</button>
        <button type="button" class="btn btn-secondary" data-test-id="cancel-button">Cancel</button>
    </div>
</form>
"""

HTML_WITH_SCRIPTS = """
<div class="container">
    <script>
        console.log("This should be removed");
        var x = 1;
    </script>
    <p class="content" data-test-id="content">This content should remain</p>
    <style>
        .container { color: red; }
    </style>
</div>
"""


class TestPromptFormatter:
    """Test prompt formatter function."""

    def test_prompt_formatter_basic(self):
        """Test formatter works with minimal HTML."""
        html = "<div>Test</div>"
        prompt = get_dom_analysis_prompt(html=html, page_type="PDP")
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "PDP" in prompt
        assert html in prompt
        assert "JSON" in prompt  # Should mention JSON output format

    def test_prompt_formatter_with_page_type(self):
        """Test that page_type is included in prompt."""
        html = "<div>Test</div>"
        prompt = get_dom_analysis_prompt(html=html, page_type="Cart")
        
        assert "Cart" in prompt or "CART" in prompt
        assert "Page Type" in prompt

    def test_prompt_formatter_with_brand_name(self):
        """Test that brand_name is included when provided."""
        html = "<div>Test</div>"
        prompt = get_dom_analysis_prompt(html=html, page_type="PDP", brand_name="VANS")
        
        assert "VANS" in prompt
        assert "Brand" in prompt

    def test_prompt_formatter_without_brand_name(self):
        """Test that prompt works without brand_name."""
        html = "<div>Test</div>"
        prompt = get_dom_analysis_prompt(html=html, page_type="PDP")
        
        # Should not raise error
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_prompt_formatter_with_product_card_html(self):
        """Test formatter with product card HTML."""
        prompt = get_dom_analysis_prompt(
            html=PRODUCT_CARD_HTML,
            page_type="PDP",
            brand_name="VANS"
        )
        
        assert "product-card" in prompt
        assert "data-product-id" in prompt
        assert "data-test-id" in prompt
        assert "PDP" in prompt or "pdp" in prompt
        assert "VANS" in prompt

    def test_prompt_formatter_empty_html_raises_error(self):
        """Test that empty HTML after sanitization raises ValueError."""
        with pytest.raises(ValueError, match="HTML content is empty"):
            get_dom_analysis_prompt(html="", page_type="PDP")
        
        # HTML with only whitespace/scripts should also raise error
        with pytest.raises(ValueError, match="HTML content is empty"):
            get_dom_analysis_prompt(html="   ", page_type="PDP")

    def test_prompt_includes_stability_scoring(self):
        """Test that prompt includes stability scoring guidelines."""
        prompt = get_dom_analysis_prompt(html="<div>Test</div>", page_type="PDP")
        
        assert "stability_score" in prompt
        assert "0.9-1.0" in prompt  # data-* attributes
        assert "data-*" in prompt.lower() or "data attribute" in prompt.lower()

    def test_prompt_includes_json_format(self):
        """Test that prompt clearly specifies JSON output format."""
        prompt = get_dom_analysis_prompt(html="<div>Test</div>", page_type="PDP")
        
        assert "JSON" in prompt
        assert "selectors" in prompt
        assert "relationships" in prompt
        assert "patterns" in prompt
        assert "recommendations" in prompt
        assert "warnings" in prompt


class TestHTMLSanitization:
    """Test HTML sanitization helper."""

    def test_html_sanitization_removes_scripts(self):
        """Test that script tags are removed."""
        html = HTML_WITH_SCRIPTS
        sanitized = sanitize_html_for_analysis(html)
        
        assert "<script>" not in sanitized
        assert "console.log" not in sanitized
        assert "var x" not in sanitized
        assert "This content should remain" in sanitized

    def test_html_sanitization_removes_styles(self):
        """Test that style tags are removed."""
        html = HTML_WITH_SCRIPTS
        sanitized = sanitize_html_for_analysis(html)
        
        assert "<style>" not in sanitized
        assert ".container { color: red; }" not in sanitized
        assert "data-test-id" in sanitized  # Should preserve attributes

    def test_html_sanitization_preserves_structure(self):
        """Test that HTML structure and attributes are preserved."""
        html = PRODUCT_CARD_HTML
        sanitized = sanitize_html_for_analysis(html)
        
        assert "data-product-id" in sanitized
        assert "data-test-id" in sanitized
        assert "class=" in sanitized
        assert "product-card" in sanitized
        assert "<div" in sanitized
        assert "<button" in sanitized

    def test_html_sanitization_preserves_data_attributes(self):
        """Test that data-* attributes are preserved (critical for selector extraction)."""
        html = '<button data-test-id="add-to-cart" data-product-id="123">Add</button>'
        sanitized = sanitize_html_for_analysis(html)
        
        assert "data-test-id" in sanitized
        assert "data-product-id" in sanitized
        assert "add-to-cart" in sanitized
        assert "123" in sanitized

    def test_html_sanitization_truncates_long_html(self):
        """Test that very long HTML is truncated to max_length."""
        # Create very long HTML
        long_html = "<div>" + "x" * 100000 + "</div>"
        sanitized = sanitize_html_for_analysis(long_html, max_length=1000)
        
        assert len(sanitized) <= 1000

    def test_html_sanitization_empty_string(self):
        """Test sanitization with empty string."""
        result = sanitize_html_for_analysis("")
        assert result == ""

    def test_html_sanitization_whitespace_only(self):
        """Test sanitization with whitespace only."""
        result = sanitize_html_for_analysis("   \n\t  ")
        # After sanitization, whitespace should be cleaned
        assert len(result.strip()) == 0 or result == ""

    def test_html_sanitization_removes_comments(self):
        """Test that HTML comments are removed."""
        html = '<div><!-- This is a comment --><p>Content</p></div>'
        sanitized = sanitize_html_for_analysis(html)
        
        assert "<!--" not in sanitized
        assert "comment" not in sanitized
        assert "Content" in sanitized

    def test_html_sanitization_custom_max_length(self):
        """Test that custom max_length parameter works."""
        html = "<div>" + "x" * 1000 + "</div>"
        sanitized = sanitize_html_for_analysis(html, max_length=100)
        
        assert len(sanitized) <= 100


class TestOutputFormatSpecification:
    """Test that output format is clearly specified in prompt."""

    def test_output_format_specification(self):
        """Test that JSON format is clearly specified in prompt."""
        prompt = get_dom_analysis_prompt(html="<div>Test</div>", page_type="PDP")
        
        # Check for key JSON structure elements
        assert '"selectors"' in prompt
        assert '"selector"' in prompt
        assert '"stability_score"' in prompt
        assert '"element_type"' in prompt
        assert '"relationships"' in prompt
        assert '"patterns"' in prompt
        assert '"recommendations"' in prompt
        assert '"warnings"' in prompt

    def test_prompt_emphasizes_json_only(self):
        """Test that prompt emphasizes JSON-only output."""
        prompt = get_dom_analysis_prompt(html="<div>Test</div>", page_type="PDP")
        
        # Should have strong language about JSON-only
        prompt_lower = prompt.lower()
        assert ("only" in prompt_lower and "json" in prompt_lower) or "json only" in prompt_lower
        assert "markdown" not in prompt_lower or "no markdown" in prompt_lower.lower()


class TestPromptExamples:
    """Test that prompt includes good examples."""

    def test_prompt_includes_selector_examples(self):
        """Test that prompt includes good vs bad selector examples."""
        prompt = get_dom_analysis_prompt(html="<div>Test</div>", page_type="PDP")
        
        # Should mention good selectors
        assert "data-test-id" in prompt or "data attribute" in prompt.lower()
        # Should mention bad selectors or stability issues
        assert "stability" in prompt.lower()

