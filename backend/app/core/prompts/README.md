# DOM Analysis Prompt Documentation

## Overview

This module contains the prompt template and utilities for analyzing HTML snippets and extracting structured data about DOM selectors. The analysis is performed by Claude API and returns information about selector stability, relationships, patterns, and recommendations.

## Purpose

During user onboarding, admins paste HTML snippets from their website (product cards, hero banners, forms, etc.). This prompt instructs Claude to analyze the HTML and suggest:

- Stable CSS selectors for key elements
- Parent-child-sibling relationships between elements
- Element stability scores (how likely a selector will break)
- Common patterns and recommendations

This analysis will populate the selector database with high-quality, relationship-aware selectors that can be used for safe code generation.

## File Structure

- `dom_analysis_prompt.py` - Main prompt template and utility functions
- `tests/test_dom_analysis_prompt.py` - Test fixtures and test cases

## Design Decisions

### Why JSON-Only Output Format?

The prompt explicitly requires JSON-only output (no markdown, no code blocks, no explanations) for several reasons:

1. **Parsing Reliability**: JSON is easily parseable and validated programmatically
2. **Consistency**: Ensures Claude always returns data in the same structure
3. **Integration**: The parsed JSON will be directly used to populate the database
4. **Error Prevention**: Reduces the chance of parsing errors from markdown formatting

The prompt uses strong, emphatic language about JSON-only output to minimize cases where Claude wraps the response in markdown code blocks.

### Stability Scoring Rationale

Stability scores indicate how likely a CSS selector will remain valid over time. The scoring system is based on:

1. **data-* attributes (0.9-1.0)**: Highest stability
   - These are explicitly added for testing/automation
   - Less likely to change during redesigns
   - Examples: `data-test-id`, `data-product-id`, `data-tracking-id`

2. **Semantic IDs (0.8-0.9)**: High stability
   - Unique, meaningful IDs that serve functional purposes
   - Less likely to change unless functionality changes
   - Examples: `#product-price-12345`, `#checkout-button`

3. **Unique, Descriptive Classes (0.6-0.8)**: Medium-high stability
   - Classes that are semantically meaningful
   - May change during redesigns but less frequently
   - Examples: `.product-card`, `.add-to-cart-button`

4. **Generic/Utility Classes (0.3-0.6)**: Low-medium stability
   - Utility classes from frameworks (Tailwind, Bootstrap)
   - Frequently changed during styling updates
   - Examples: `.flex`, `.btn-primary`, `.container`

5. **Deeply Nested Selectors**: Lower scores
   - Fragile structure that breaks easily
   - Reduces stability by 0.1-0.2 per nesting level
   - Example: `div > div > div > button` (very fragile)

6. **Tag-Only Selectors (0.1-0.3)**: Very low stability
   - Selects all elements of a type
   - No uniqueness guarantee
   - Examples: `button`, `div`, `p`

### Relationship Detection Approach

The prompt instructs Claude to identify meaningful relationships, not just every nested element:

**Parent-Child Relationships**:
- Only include when the parent provides meaningful context
- Example: A product card container and its price/button children
- Not: Every nested div relationship

**Sibling Relationships**:
- Elements that are functionally related
- Example: Add to cart button and wishlist button (both actions on a product)
- Example: Product title and price (both display product info)

**Containers**:
- Structural elements that organize content
- Useful for iteration (e.g., all product cards in a grid)
- Example: `div.product-card` containing multiple product items

The goal is to capture relationships that are useful for automation, not to map every DOM node.

## Usage

### Basic Usage

```python
from app.core.prompts.dom_analysis_prompt import get_dom_analysis_prompt

html = """
<div class="product-card" data-product-id="123">
    <button data-test-id="add-to-cart">Add to Cart</button>
</div>
"""

prompt = get_dom_analysis_prompt(
    html=html,
    page_type="PDP",
    brand_name="VANS"
)

# Use prompt with Claude API
response = claude_client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": prompt}]
)
```

### HTML Sanitization

The `sanitize_html_for_analysis()` function automatically:
- Removes `<script>` tags and content
- Removes `<style>` tags and content
- Removes HTML comments
- Limits length to prevent token overflow (default: 50,000 chars)
- Preserves HTML structure and all attributes (especially data-* attributes)

```python
from app.core.prompts.dom_analysis_prompt import sanitize_html_for_analysis

dirty_html = """
<script>console.log("test");</script>
<div data-test-id="content">Hello</div>
<style>.container { color: red; }</style>
"""

clean_html = sanitize_html_for_analysis(dirty_html)
# Result: <div data-test-id="content">Hello</div>
```

## Output Format

The prompt specifies a JSON structure:

```json
{
  "selectors": [
    {
      "selector": "button[data-test-id='add-to-cart']",
      "description": "Add to cart button on PDP",
      "stability_score": 0.95,
      "element_type": "interactive",
      "parent": "div.product-actions",
      "children": [],
      "siblings": ["button.wishlist-btn", "span.price"]
    }
  ],
  "relationships": {
    "containers": ["div.product-card", "section.hero-banner"],
    "interactive": ["button[data-test-id='add-to-cart']"],
    "content": ["h1.product-title", "p.product-description"]
  },
  "patterns": [
    "Product cards use consistent structure with data-product-id attribute"
  ],
  "recommendations": [
    "Use data-test-id attributes for most stable selectors"
  ],
  "warnings": [
    "Class names use Tailwind - may change frequently"
  ]
}
```

## Integration Points

This prompt will be used in **Task 3.2** to create a service that:
1. Accepts HTML from admin users during onboarding
2. Calls Claude API with this prompt
3. Parses the JSON response
4. Stores selectors and relationships in the database
5. Populates the `dom_selectors` table with high-quality selectors

## Iterating on the Prompt

If the prompt needs improvement:

1. **Test with Real HTML**: Use actual HTML from target websites
2. **Review Output Quality**: Check if stability scores are accurate
3. **Check Relationship Detection**: Verify parent/child/sibling detection is meaningful
4. **Validate JSON Parsing**: Ensure responses are always valid JSON
5. **Update Examples**: Add more examples if Claude misunderstands requirements

### Common Issues and Fixes

**Issue**: Claude returns markdown-wrapped JSON
- **Fix**: Strengthen the "JSON-only" language in the prompt

**Issue**: Stability scores are too high/low
- **Fix**: Adjust scoring thresholds or add more examples

**Issue**: Too many or too few relationships detected
- **Fix**: Clarify what constitutes a "meaningful" relationship

**Issue**: Missing data-* attributes in analysis
- **Fix**: Emphasize data attributes in the prompt instructions

## Testing

Run tests with:

```bash
pytest backend/app/core/prompts/tests/test_dom_analysis_prompt.py
```

Test coverage includes:
- Prompt formatter functionality
- HTML sanitization (scripts, styles, comments)
- Output format specification
- Edge cases (empty HTML, very long HTML)

## Dependencies

- No external HTML parsing libraries required
- Uses regex-based sanitization (no BeautifulSoup dependency)
- Compatible with existing Anthropic SDK

