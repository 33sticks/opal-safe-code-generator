"""DOM Analysis prompt builder for Claude API."""
import re


# Main prompt template
DOM_ANALYSIS_PROMPT_TEMPLATE = """You are an expert HTML/CSS analyzer specializing in identifying stable, maintainable CSS selectors for web automation and testing.

Your task is to analyze the provided HTML snippet and extract structured information about DOM selectors, their relationships, stability scores, and patterns.

CONTEXT:
- Page Type: {page_type}
{brand_context}

HTML TO ANALYZE:
{html}

ANALYSIS REQUIREMENTS:

1. IDENTIFY KEY ELEMENTS:
   - Interactive elements: buttons, links, form inputs, checkboxes, radio buttons
   - Content elements: headings, paragraphs, text spans, images, videos
   - Container/structural elements: divs, sections, articles that organize content
   - Data attributes: elements with data-test-id, data-tracking-id, data-product-id, etc.

2. FOR EACH ELEMENT, PROVIDE:
   - selector: The most stable CSS selector that uniquely identifies this element
   - description: What the element does or represents (human-readable)
   - stability_score: A float between 0.0 and 1.0 indicating how likely this selector will remain stable
   - element_type: One of "interactive", "content", "container", or "data"
   - parent: CSS selector for the parent element (if relevant and meaningful)
   - children: List of CSS selectors for direct child elements (if any)
   - siblings: List of CSS selectors for related sibling elements (if any)

3. STABILITY SCORING GUIDELINES:
   - data-* attributes (data-test-id, data-product-id, etc.): 0.9-1.0 (highest stability)
   - Semantic IDs (unique, meaningful IDs): 0.8-0.9 (high stability)
   - Unique, descriptive classes: 0.6-0.8 (medium-high stability)
   - Generic or utility classes (e.g., Tailwind classes): 0.3-0.6 (low-medium stability)
   - Deeply nested selectors (e.g., div > div > div > button): Lower scores (reduce by 0.1-0.2 per level)
   - Tag-only selectors (e.g., button, div): 0.1-0.3 (very low stability)

4. RELATIONSHIP DETECTION:
   - Identify parent-child relationships where the parent provides meaningful context
   - Identify sibling relationships where elements are related (e.g., product card and its price/button)
   - Only include relationships that are meaningful for automation (not every nested element)

5. COMMON PATTERNS:
   - Identify repeated structures (e.g., "Product cards in a grid", "Form fields in a container")
   - Note consistent patterns in selector naming (e.g., "All interactive elements have data-test-id")
   - Identify structural patterns that could be used for iteration

6. RECOMMENDATIONS:
   - Best practices for this page type
   - Suggestions for improving selector stability
   - Recommendations for automation-friendly selectors

7. WARNINGS:
   - Potential gotchas or unstable selectors
   - Elements that might change frequently
   - Selectors that rely on fragile patterns

SELECTOR QUALITY EXAMPLES:

GOOD SELECTORS:
- button[data-test-id="add-to-cart"] (stability: 0.95) - Uses data attribute
- #product-price-12345 (stability: 0.85) - Unique semantic ID
- .product-card[data-product-id] (stability: 0.9) - Combines class with data attribute

BAD SELECTORS:
- button.btn-primary (stability: 0.4) - Generic classes, likely to change
- div > div > div > button (stability: 0.2) - Deeply nested, fragile structure
- .flex.items-center.gap-2 (stability: 0.3) - Utility classes from Tailwind/CSS frameworks

OUTPUT FORMAT:

CRITICAL: You MUST return ONLY valid JSON. No markdown code blocks, no backticks, no explanations outside the JSON structure. The response must be parseable JSON.

Required JSON structure:
{{
  "selectors": [
    {{
      "selector": "button[data-test-id='add-to-cart']",
      "description": "Add to cart button on PDP",
      "stability_score": 0.95,
      "element_type": "interactive",
      "parent": "div.product-actions",
      "children": [],
      "siblings": ["button.wishlist-btn", "span.price"]
    }}
  ],
  "relationships": {{
    "containers": ["div.product-card", "section.hero-banner"],
    "interactive": ["button[data-test-id='add-to-cart']", "a.product-link"],
    "content": ["h1.product-title", "p.product-description", "img.product-image"]
  }},
  "patterns": [
    "Product cards use consistent structure with data-product-id attribute",
    "All interactive elements have data-test-id attributes for testing"
  ],
  "recommendations": [
    "Use data-test-id attributes for most stable selectors",
    "Product card container repeats - good for iteration over multiple products",
    "Consider adding data attributes to elements that currently rely on classes"
  ],
  "warnings": [
    "Class names use Tailwind utility classes - may change frequently during redesigns",
    "Some buttons lack unique identifiers and rely on class combinations"
  ]
}}

IMPORTANT REMINDERS:
- Return ONLY valid JSON - no markdown, no code blocks, no explanations
- Test selectors mentally: would they select unique elements?
- Prioritize data-* attributes and semantic IDs over classes
- Include meaningful relationships, not every nested element
- Be specific in descriptions (what does the element do, not just what it is)
- Provide actionable recommendations and warnings
"""


def sanitize_html_for_analysis(html: str, max_length: int = 50000) -> str:
    """
    Clean HTML for analysis by removing script/style tags and limiting length.
    
    Args:
        html: Raw HTML string to sanitize
        max_length: Maximum length of HTML to preserve (default: 50000)
        
    Returns:
        Sanitized HTML string with scripts/styles removed and length limited
    """
    if not html:
        return ""
    
    # Remove script tags and their content
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove style tags and their content
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove comments
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    
    # Clean up extra whitespace but preserve structure
    html = re.sub(r'\s+', ' ', html)
    html = re.sub(r'>\s+<', '><', html)
    
    # Limit length if needed
    if len(html) > max_length:
        # Try to truncate at a tag boundary
        truncated = html[:max_length]
        last_tag_close = truncated.rfind('>')
        if last_tag_close > max_length * 0.9:  # If we're close to a tag boundary
            html = truncated[:last_tag_close + 1]
        else:
            html = truncated
            # Add closing tags for common elements if needed (simple heuristic)
            if html.count('<div') > html.count('</div'):
                html += '</div>'
            if html.count('<section') > html.count('</section'):
                html += '</section>'
    
    return html.strip()


def get_dom_analysis_prompt(
    html: str,
    page_type: str,
    brand_name: str = ""
) -> str:
    """
    Format the DOM analysis prompt with provided context.
    
    Args:
        html: HTML snippet to analyze
        page_type: Type of page (PDP, Cart, Home, etc.)
        brand_name: Brand name for context (optional)
        
    Returns:
        Formatted prompt string ready for Claude API
    """
    # Sanitize HTML first
    sanitized_html = sanitize_html_for_analysis(html)
    
    if not sanitized_html:
        raise ValueError("HTML content is empty or invalid after sanitization")
    
    # Format the prompt template
    brand_context = f"- Brand: {brand_name}" if brand_name else ""
    prompt = DOM_ANALYSIS_PROMPT_TEMPLATE.format(
        html=sanitized_html,
        page_type=page_type.upper() if page_type else "UNKNOWN",
        brand_context=brand_context
    )
    
    return prompt

