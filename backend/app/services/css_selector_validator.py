"""CSS Selector validation and extraction service."""
import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def is_valid_css_selector(selector: str) -> bool:
    """
    Validate if a string is valid CSS selector syntax.
    
    Args:
        selector: CSS selector string to validate
        
    Returns:
        True if selector is valid CSS, False otherwise.
    """
    if not selector or not selector.strip():
        return False
    
    selector = selector.strip()
    
    # Basic validation: selector should start with valid characters
    # Valid starts: tag name, ., #, [, :, *, etc.
    if not re.match(r'^[.#\[:\w*]', selector):
        return False
    
    # Check for balanced brackets (for attribute selectors)
    if selector.count('[') != selector.count(']'):
        return False
    
    # Check for balanced parentheses (for pseudo-classes/functions)
    if selector.count('(') != selector.count(')'):
        return False
    
    # Check for balanced quotes (within attribute selectors)
    # This is a simplified check - quotes should be balanced
    single_quotes = selector.count("'")
    double_quotes = selector.count('"')
    # Allow balanced quotes or no quotes
    if single_quotes % 2 != 0 or double_quotes % 2 != 0:
        return False
    
    # Basic pattern validation
    # Allow: tag, .class, #id, [attr], [attr=value], pseudo-classes, combinators
    valid_pattern = re.compile(
        r'^([.#]?[\w-]+|\[[\w-]+(?:[*^$|~]?=["\'][^\'\"]*["\']?)?\]|:[\w-]+(?:\([^\)]*\))?|[\s>+~,])+$',
        re.IGNORECASE
    )
    
    # More lenient check - just ensure it doesn't contain obviously invalid patterns
    # Allow common CSS selector characters
    invalid_chars = re.search(r'[<>{};]', selector)
    if invalid_chars:
        return False
    
    return True


def extract_css_selectors_from_message(message: str) -> List[str]:
    """
    Extract all potential CSS selectors from user message.
    
    Looks for:
    - Attribute selectors: [data-test-id='product-name'], [class*='product']
    - ID selectors: #product-name
    - Class selectors: .product-title
    - Tag selectors with attributes: h1[data-test-id='name']
    - Quoted selectors: "[data-test-id='product-name']" or '[data-test-id="product-name"]'
    
    Args:
        message: User message text
        
    Returns:
        List of extracted selectors, ordered by confidence (most specific first).
    """
    if not message:
        return []
    
    selectors = []
    
    # Pattern 1: Quoted attribute selectors
    # Matches: "[data-test-id='product-name']" or '[data-test-id="product-name"]'
    quoted_attr_pattern = r'["\'](\[[\w-]+(?:[*^$|~]?=["\'][^\'\"]*["\']?)?\])["\']'
    quoted_matches = re.findall(quoted_attr_pattern, message)
    selectors.extend(quoted_matches)
    
    # Pattern 2: Quoted ID/class selectors
    # Matches: "#product-name" or ".product-title"
    quoted_id_class_pattern = r'["\']([.#][\w-]+)["\']'
    quoted_id_class_matches = re.findall(quoted_id_class_pattern, message)
    selectors.extend(quoted_id_class_matches)
    
    # Pattern 3: Attribute selectors in brackets (not quoted)
    # Matches: [data-test-id='product-name'], [class*='product'], [id="test"]
    attr_pattern = r'\[[\w-]+(?:[*^$|~]?=["\'][^\'\"]*["\']?)?\]'
    attr_matches = re.findall(attr_pattern, message)
    # Filter out matches that were already captured in quoted patterns
    for match in attr_matches:
        # Check if this match is part of a quoted string
        match_start = message.find(match)
        if match_start >= 0:
            # Check context around the match
            before = message[max(0, match_start - 1):match_start]
            after_start = match_start + len(match)
            after = message[after_start:min(len(message), after_start + 1)]
            # If surrounded by quotes, skip (already captured)
            if not ((before == '"' or before == "'") and (after == '"' or after == "'")):
                selectors.append(match)
    
    # Pattern 4: ID selectors (not quoted)
    # Matches: #product-name (standalone, not part of another word)
    id_pattern = r'(?:^|\s)(#[a-zA-Z][\w-]*)(?:\s|$|[^a-zA-Z0-9_-])'
    id_matches = re.findall(id_pattern, message)
    selectors.extend(id_matches)
    
    # Pattern 5: Class selectors (not quoted)
    # Matches: .product-title (standalone, not part of another word)
    class_pattern = r'(?:^|\s)(\.[a-zA-Z][\w-]*)(?:\s|$|[^a-zA-Z0-9_-])'
    class_matches = re.findall(class_pattern, message)
    selectors.extend(class_matches)
    
    # Pattern 6: Compound selectors (tag + attribute)
    # Matches: h1[data-test-id='name'], div.product-title
    compound_pattern = r'[\w-]+(?:\[[\w-]+(?:[*^$|~]?=["\'][^\'\"]*["\']?)?\]|[.#][\w-]+)'
    compound_matches = re.findall(compound_pattern, message)
    selectors.extend(compound_matches)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_selectors = []
    for selector in selectors:
        if selector not in seen:
            seen.add(selector)
            unique_selectors.append(selector.strip())
    
    # Sort by specificity (most specific first)
    # Priority: compound > attribute > id/class
    def selector_priority(s: str) -> int:
        if '[' in s and (s.startswith('.') or s.startswith('#') or re.match(r'^\w', s)):
            return 3  # Compound selector (highest priority)
        elif '[' in s:
            return 2  # Attribute selector
        elif s.startswith('#') or s.startswith('.'):
            return 1  # ID/Class selector
        return 0
    
    unique_selectors.sort(key=selector_priority, reverse=True)
    
    # Validate each selector
    validated_selectors = [s for s in unique_selectors if is_valid_css_selector(s)]
    
    logger.debug(f"Extracted {len(validated_selectors)} CSS selectors from message: {validated_selectors}")
    
    return validated_selectors


def validate_selector_syntax(selector: str) -> Dict[str, Any]:
    """
    Validate selector and return detailed validation result.
    
    Args:
        selector: CSS selector string to validate
        
    Returns:
        {
            "is_valid": bool,
            "selector_type": str,  # "id", "class", "attribute", "compound", etc.
            "normalized": str,     # Cleaned/normalized selector
            "error": Optional[str] # Error message if invalid
        }
    """
    if not selector:
        return {
            "is_valid": False,
            "selector_type": "unknown",
            "normalized": "",
            "error": "Selector is empty"
        }
    
    normalized = selector.strip()
    
    # Determine selector type
    selector_type = "unknown"
    if normalized.startswith('#'):
        selector_type = "id"
    elif normalized.startswith('.'):
        selector_type = "class"
    elif normalized.startswith('['):
        selector_type = "attribute"
    elif '[' in normalized or (normalized.count('.') > 0 and not normalized.startswith('.')) or (normalized.count('#') > 0 and not normalized.startswith('#')):
        selector_type = "compound"
    elif re.match(r'^[a-zA-Z]', normalized):
        selector_type = "tag"
    
    # Validate syntax
    is_valid = is_valid_css_selector(normalized)
    
    result = {
        "is_valid": is_valid,
        "selector_type": selector_type,
        "normalized": normalized,
        "error": None
    }
    
    if not is_valid:
        result["error"] = f"Invalid CSS selector syntax: {normalized}"
    
    return result

