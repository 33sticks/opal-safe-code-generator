"""Selector validation service for checking element selectors before code generation."""
import re
import logging
from typing import List, Dict, Optional, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func

from app.models.dom_selector import DOMSelector
from app.models.enums import PageType, SelectorStatus
from app.services.css_selector_validator import (
    extract_css_selectors_from_message,
    validate_selector_syntax
)

logger = logging.getLogger(__name__)


class SelectorMatch:
    """Represents a matched selector with confidence score."""
    def __init__(self, selector: DOMSelector, confidence: float, match_type: str):
        self.selector = selector
        self.confidence = confidence
        self.match_type = match_type  # 'exact', 'keyword', 'partial'


async def check_selector_in_database(
    db: AsyncSession,
    selector: str,
    brand_id: int,
    page_type: PageType
) -> Optional[DOMSelector]:
    """
    Check if a CSS selector exists in the database for the given brand and page type.
    
    Args:
        db: Database session
        selector: CSS selector string
        brand_id: Brand ID
        page_type: Page type enum
        
    Returns:
        DOMSelector if found, None otherwise
    """
    result = await db.execute(
        select(DOMSelector).where(
            DOMSelector.brand_id == brand_id,
            DOMSelector.page_type == page_type,
            DOMSelector.selector == selector.strip(),
            DOMSelector.status == SelectorStatus.ACTIVE
        )
    )
    return result.scalar_one_or_none()


async def validate_element_selector(
    db: AsyncSession,
    element_description: str,
    page_type: PageType,
    brand_id: int,
    user_message: Optional[str] = None,
    conversation_context: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Validate if an element description has matching selectors in the database.
    
    First checks for CSS selectors in the user message, then falls back to fuzzy matching.
    
    Args:
        db: Database session
        element_description: Description of the element user wants to modify
        page_type: Page type enum (PDP, CART, etc.)
        brand_id: Brand ID
        user_message: Optional user message to extract CSS selectors from
        conversation_context: Optional list of recent conversation messages for context
        
    Returns:
        {
            "status": str,  # "found_in_db", "valid_but_not_in_db", "multiple_matches", "not_found"
            "is_valid": bool,
            "selector": Optional[str],  # The selector found/validated
            "source": Optional[str],  # "database" or "user_provided"
            "requires_review": bool,
            "matches": List[SelectorMatch],
            "message": Optional[str]
        }
    """
    if not element_description or not element_description.strip():
        return {
            "status": "not_found",
            "is_valid": True,  # Allow if no element specified (generic request)
            "selector": None,
            "source": None,
            "requires_review": False,
            "matches": [],
            "message": None
        }
    
    # PRIORITY 1: Check for CSS selectors in user message (EXPLICIT USER INPUT)
    # This takes precedence over number choices and fuzzy matches
    # If user provides "use selector 3, but actually use #different-selector",
    # the explicit selector wins
    if user_message:
        css_selectors = extract_css_selectors_from_message(user_message)
        
        if css_selectors:
            # Try each extracted selector (they're ordered by confidence)
            for selector in css_selectors:
                validation = validate_selector_syntax(selector)
                
                if validation["is_valid"]:
                    # Valid CSS selector found - check database
                    db_match = await check_selector_in_database(
                        db, selector, brand_id, page_type
                    )
                    
                    if db_match:
                        # Selector exists in database
                        logger.info(f"CSS selector found in database: {selector}")
                        return {
                            "status": "found_in_db",
                            "is_valid": True,
                            "selector": selector,
                            "source": "database",
                            "requires_review": False,
                            "matches": [SelectorMatch(db_match, 1.0, "exact")],
                            "message": None
                        }
                    else:
                        # Valid CSS selector but not in database - use it, flag for review
                        logger.info(f"Valid CSS selector provided but not in database: {selector}")
                        return {
                            "status": "valid_but_not_in_db",
                            "is_valid": True,
                            "selector": selector,
                            "source": "user_provided",
                            "requires_review": True,
                            "matches": [],
                            "message": f"Using selector '{selector}' (not in database, will be flagged for admin review)"
                        }
    
    # PRIORITY 2: Check if user is responding to a multiple choice question (by number)
    # Only check this if no explicit CSS selector was found
    if user_message and conversation_context:
        # Check if last assistant message was asking for a choice
        if conversation_context:
            # Look for previous "multiple selectors found" message
            last_assistant_msg = None
            for msg in reversed(conversation_context[-5:]):  # Check last 5 messages
                if "found multiple selectors" in msg.lower() or "which selector should i use" in msg.lower():
                    last_assistant_msg = msg
                    break
            
            if last_assistant_msg:
                # User might be responding to a choice - check for number selection
                choice_num = extract_selector_choice_from_message(user_message)
                
                if choice_num:
                    # Extract the selector from the previous message's options
                    selected_selector = extract_selector_from_choice_message(last_assistant_msg, choice_num)
                    
                    if selected_selector:
                        # Validate the selected selector
                        validation = validate_selector_syntax(selected_selector)
                        if validation["is_valid"]:
                            # Check if it's in database
                            db_match = await check_selector_in_database(
                                db, selected_selector, brand_id, page_type
                            )
                            
                            if db_match:
                                logger.info(f"User selected selector #{choice_num}: {selected_selector}")
                                return {
                                    "status": "found_in_db",
                                    "is_valid": True,
                                    "selector": selected_selector,
                                    "source": "database",
                                    "requires_review": False,
                                    "matches": [SelectorMatch(db_match, 1.0, "exact")],
                                    "message": None
                                }
                    
                    # If we got a choice number but couldn't extract selector, 
                    # still check if the number is valid by looking at the matches format
                    # We'll need the matches to validate the choice, so continue to fuzzy matching
    
    # PRIORITY 3: Fall back to fuzzy matching if no valid CSS selector found and no number choice
    # Normalize element description
    element_desc = element_description.strip().lower()
    
    # Query selectors for this brand and page type
    base_query = select(DOMSelector).where(
        DOMSelector.brand_id == brand_id,
        DOMSelector.page_type == page_type,
        DOMSelector.status == SelectorStatus.ACTIVE
    )
    
    # Get all selectors first
    result = await db.execute(base_query)
    all_selectors = result.scalars().all()
    
    if not all_selectors:
        # No selectors exist for this page type
        return {
            "status": "not_found",
            "is_valid": False,
            "selector": None,
            "source": None,
            "requires_review": False,
            "matches": [],
            "message": _format_no_selectors_message(element_description, page_type)
        }
    
    # Perform fuzzy matching
    matches = _find_matching_selectors(element_desc, all_selectors)
    
    # Check if user is selecting from fuzzy matches by number
    if user_message and len(matches) > 1:
        choice_num = extract_selector_choice_from_message(user_message)
        if choice_num:
            # Validate choice number is within range
            if 1 <= choice_num <= len(matches):
                selected_match = matches[choice_num - 1]  # Convert to 0-indexed
                logger.info(f"User selected fuzzy match #{choice_num}: {selected_match.selector.selector}")
                return {
                    "status": "found_in_db",
                    "is_valid": True,
                    "selector": selected_match.selector.selector,
                    "source": "database",
                    "requires_review": False,
                    "matches": [selected_match],
                    "message": None
                }
            else:
                # Invalid choice number
                return {
                    "status": "invalid_choice",
                    "is_valid": False,
                    "selector": None,
                    "source": None,
                    "requires_review": False,
                    "matches": matches,
                    "message": f"I only found {len(matches)} selectors. Please choose 1, 2, or {len(matches)}."
                }
    
    if not matches:
        # No matches found
        return {
            "status": "not_found",
            "is_valid": False,
            "selector": None,
            "source": None,
            "requires_review": False,
            "matches": [],
            "message": _format_selector_not_found_message(element_description, page_type)
        }
    
    if len(matches) == 1:
        # Single match - valid
        return {
            "status": "found_in_db",
            "is_valid": True,
            "selector": matches[0].selector.selector,
            "source": "database",
            "requires_review": False,
            "matches": matches,
            "message": None
        }
    
    # Multiple matches - need user to choose
    return {
        "status": "multiple_matches",
        "is_valid": False,
        "selector": None,
        "source": None,
        "requires_review": False,
        "matches": matches,
        "message": _format_multiple_matches_message(element_description, matches)
    }


def _find_matching_selectors(
    element_desc: str,
    selectors: List[DOMSelector]
) -> List[SelectorMatch]:
    """
    Find matching selectors using fuzzy matching.
    
    Returns list of SelectorMatch objects sorted by confidence (highest first).
    """
    matches = []
    element_keywords = _extract_keywords(element_desc)
    
    for selector in selectors:
        selector_desc = (selector.description or "").strip().lower()
        
        if not selector_desc:
            continue
        
        # Check exact match
        if selector_desc == element_desc:
            matches.append(SelectorMatch(selector, 1.0, "exact"))
            continue
        
        # Check if element_desc is contained in selector description
        if element_desc in selector_desc:
            confidence = len(element_desc) / len(selector_desc) if selector_desc else 0
            matches.append(SelectorMatch(selector, min(confidence, 0.9), "partial"))
            continue
        
        # Check keyword overlap
        selector_keywords = _extract_keywords(selector_desc)
        keyword_overlap = _calculate_keyword_overlap(element_keywords, selector_keywords)
        
        if keyword_overlap > 0.3:  # Threshold for keyword match
            matches.append(SelectorMatch(selector, keyword_overlap, "keyword"))
    
    # Sort by confidence (highest first)
    matches.sort(key=lambda x: x.confidence, reverse=True)
    
    # Return top matches (limit to 5)
    return matches[:5]


def _extract_keywords(text: str) -> List[str]:
    """Extract meaningful keywords from text, filtering out common stop words."""
    # Common stop words to filter
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "are", "was", "were", "be",
        "been", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "must", "can", "this", "that",
        "these", "those", "on", "off", "up", "down", "out", "over", "under"
    }
    
    # Split by non-word characters and filter
    words = re.findall(r'\b\w+\b', text.lower())
    keywords = [w for w in words if len(w) > 2 and w not in stop_words]
    
    return keywords


def _calculate_keyword_overlap(keywords1: List[str], keywords2: List[str]) -> float:
    """Calculate overlap score between two keyword lists."""
    if not keywords1 or not keywords2:
        return 0.0
    
    set1 = set(keywords1)
    set2 = set(keywords2)
    
    intersection = set1 & set2
    union = set1 | set2
    
    if not union:
        return 0.0
    
    # Jaccard similarity
    jaccard = len(intersection) / len(union)
    
    # Also factor in how many keywords matched vs total
    keyword_match_ratio = len(intersection) / len(keywords1) if keywords1 else 0
    
    # Combined score
    return (jaccard * 0.6) + (keyword_match_ratio * 0.4)


def _format_selector_not_found_message(element_description: str, page_type: PageType) -> str:
    """Format helpful message when selector is not found."""
    page_type_upper = page_type.value.upper()
    
    return f"""I'm unable to find a selector for "{element_description}" on the {page_type_upper} page.

To help me generate accurate code, please:
1. Open the {page_type_upper} page in your browser
2. Right-click on the {element_description}
3. Select "Inspect" or "Inspect Element"
4. Copy the CSS selector or the relevant HTML

Then paste it here, and I'll generate the code with the correct selector.

Alternatively, if you know the CSS selector, you can provide it directly (e.g., ".product-title" or "#product-name")."""


def _format_no_selectors_message(element_description: str, page_type: PageType) -> str:
    """Format message when no selectors exist for the page type."""
    page_type_upper = page_type.value.upper()
    
    return f"""No selectors are configured for the {page_type_upper} page yet.

To help me generate accurate code, please:
1. Open the {page_type_upper} page in your browser
2. Right-click on the {element_description}
3. Select "Inspect" or "Inspect Element"
4. Copy the CSS selector or the relevant HTML

Then paste it here, and I'll generate the code with the correct selector.

Alternatively, if you know the CSS selector, you can provide it directly (e.g., ".product-title" or "#product-name")."""


def extract_selector_choice_from_message(message: str) -> Optional[int]:
    """
    Extract selector choice number from user message.
    
    Patterns to match:
    - "use selector 3"
    - "use option 2"
    - "number 1"
    - "use 2"
    - "selector 3"
    - Just "3" (if in context of choosing)
    
    Args:
        message: User message text
        
    Returns:
        Choice number (1-indexed) or None
    """
    if not message:
        return None
    
    message_lower = message.lower().strip()
    
    # Pattern 1: "use selector/option X"
    match = re.search(r'use\s+(?:selector|option)\s+(\d+)', message_lower)
    if match:
        return int(match.group(1))
    
    # Pattern 2: "selector/option X"
    match = re.search(r'(?:selector|option)\s+(\d+)', message_lower)
    if match:
        return int(match.group(1))
    
    # Pattern 3: "number X" or "use X"
    match = re.search(r'(?:number|use)\s+(\d+)', message_lower)
    if match:
        return int(match.group(1))
    
    # Pattern 4: Just a number (be careful - only if short message)
    if re.match(r'^\d+$', message_lower.strip()) and len(message_lower.strip()) <= 2:
        return int(message_lower.strip())
    
    return None


def extract_selector_from_choice_message(message: str, choice_num: int) -> Optional[str]:
    """
    Extract selector from a numbered choice message.
    
    Looks for patterns like:
    "1. description (selector: .selector)"
    "1. selector-value"
    
    Args:
        message: Message containing numbered options
        choice_num: The choice number (1-indexed)
        
    Returns:
        Selector string if found, None otherwise
    """
    if not message:
        return None
    
    # Look for the line starting with the choice number
    lines = message.split('\n')
    for line in lines:
        # Match: "N. ... (selector: ...)" - prioritize selector in parentheses
        # Pattern matches: "1. description (selector: .selector)"
        pattern1 = rf'^{choice_num}\.\s+.*?\(selector:\s*([^\)]+)\)'
        match1 = re.search(pattern1, line, re.IGNORECASE)
        if match1:
            selector = match1.group(1).strip()
            if selector:
                return selector
        
        # Match: "N. selector-value" - fallback if no parentheses
        # Only match if line is relatively short (likely just a selector)
        pattern2 = rf'^{choice_num}\.\s+([^\s\)]+)(?:\s|$)'
        match2 = re.search(pattern2, line, re.IGNORECASE)
        if match2 and len(line.strip()) < 100:  # Short line likely just selector
            selector = match2.group(1).strip()
            if selector and not selector.startswith('('):  # Don't match if starts with (
                return selector
    
    return None


def _format_multiple_matches_message(element_description: str, matches: List[SelectorMatch]) -> str:
    """Format message when multiple selectors match."""
    selector_list = []
    for i, match in enumerate(matches[:5], 1):  # Limit to 5 matches
        desc = match.selector.description or match.selector.selector
        selector_list.append(f"{i}. {desc} (selector: {match.selector.selector})")
    
    selector_text = "\n".join(selector_list)
    
    return f"""I found multiple selectors that might match "{element_description}":

{selector_text}

Which selector should I use? You can either:
- Specify the number (e.g., "use selector 1")
- Provide the exact selector value (e.g., "{matches[0].selector.selector}")
- Or provide a more specific description of the element"""


def extract_user_provided_selector(
    message: str,
    conversation_context: Optional[List[str]] = None
) -> Optional[str]:
    """
    Extract CSS selector from user message if provided directly.
    
    Looks for patterns like:
    - ".product-title"
    - "#product-name"
    - "[data-testid='product']"
    - "selector: .product-title"
    - "id is 'product-name'" → #product-name
    - "class is 'product-title'" → .product-title
    - "it's product-name" (in ID context) → #product-name
    - Bare names: "product-name" → tries #product-name and .product-name
    
    Args:
        message: User message text
        conversation_context: Optional list of previous messages for context
    
    Returns:
        Selector string if found, None otherwise
    """
    message_lower = message.lower()
    
    # Check conversation context for ID/class keywords
    has_id_context = False
    has_class_context = False
    
    if conversation_context:
        context_text = " ".join(conversation_context).lower()
        # Look for ID-related keywords
        id_keywords = ["id", "identifier", "element id", "h1 id", "div id"]
        has_id_context = any(keyword in context_text for keyword in id_keywords)
        
        # Look for class-related keywords
        class_keywords = ["class", "css class", "element class", "class name"]
        has_class_context = any(keyword in context_text for keyword in class_keywords)
    
    # Pattern 1: Direct CSS selectors with . or #
    direct_patterns = [
        r'["\']([.#][\w-]+(?:[\w\s-]*)?)["\']',  # Quoted selector: ".class" or "#id"
        r'(?:selector|css|selector)[:\s]+["\']?([.#][\w-]+(?:[\w\s-]*)?)["\']?',  # "selector: .class"
        r'(?:selector|css|selector)[:\s]+([.#][\w-]+)',  # "selector: .class" without quotes
        r'\b([.#][\w-]+)\b',  # Standalone selector: .class or #id
    ]
    
    for pattern in direct_patterns:
        matches = re.findall(pattern, message, re.IGNORECASE)
        if matches:
            selector = matches[0].strip().strip('"\'')
            if re.match(r'^[.#\[][\w\s\-\[\]="\']+$', selector):
                return selector
    
    # Pattern 2: Natural language ID references
    # Matches: "id is 'product-name'", "id='product-name'", "id: product-name", "the id product-name"
    id_patterns = [
        r'id\s*(?:is|=|:)\s*["\']?([a-zA-Z0-9_-]+)["\']?',  # "id is 'product-name'" or "id='product-name'"
        r'the\s+id\s+(["\']?[a-zA-Z0-9_-]+["\']?)',  # "the id product-name"
        r'id\s+["\']?([a-zA-Z0-9_-]+)["\']?',  # "id product-name"
        r'h1\s+id\s*(?:is|=|:)\s*["\']?([a-zA-Z0-9_-]+)["\']?',  # "h1 id is 'product-name'"
    ]
    
    for pattern in id_patterns:
        matches = re.findall(pattern, message_lower)
        if matches:
            selector_name = matches[0].strip().strip('"\'')
            # Validate it looks like a valid identifier
            if re.match(r'^[a-zA-Z0-9_-]+$', selector_name):
                return f"#{selector_name}"
    
    # Pattern 3: Natural language class references
    # Matches: "class is 'product-title'", "class='product-title'", "the class product-title"
    class_patterns = [
        r'class\s*(?:is|=|:)\s*["\']?([a-zA-Z0-9_-]+)["\']?',  # "class is 'product-title'"
        r'the\s+class\s+(["\']?[a-zA-Z0-9_-]+["\']?)',  # "the class product-title"
        r'class\s+["\']?([a-zA-Z0-9_-]+)["\']?',  # "class product-title"
        r'css\s+class\s*(?:is|=|:)\s*["\']?([a-zA-Z0-9_-]+)["\']?',  # "css class is 'title'"
    ]
    
    for pattern in class_patterns:
        matches = re.findall(pattern, message_lower)
        if matches:
            selector_name = matches[0].strip().strip('"\'')
            if re.match(r'^[a-zA-Z0-9_-]+$', selector_name):
                return f".{selector_name}"
    
    # Pattern 4: "it's X" or "it is X" (after ID/class context)
    # Only match if we have context about ID or class
    if has_id_context or "id" in message_lower:
        its_pattern = r"(?:it'?s?|it\s+is)\s+['\"]?([a-zA-Z0-9_-]+)['\"]?"
        matches = re.findall(its_pattern, message_lower)
        if matches:
            selector_name = matches[0].strip().strip('"\'')
            if re.match(r'^[a-zA-Z0-9_-]+$', selector_name):
                return f"#{selector_name}"
    
    if has_class_context or ("class" in message_lower and "id" not in message_lower):
        its_pattern = r"(?:it'?s?|it\s+is)\s+['\"]?([a-zA-Z0-9_-]+)['\"]?"
        matches = re.findall(its_pattern, message_lower)
        if matches:
            selector_name = matches[0].strip().strip('"\'')
            if re.match(r'^[a-zA-Z0-9_-]+$', selector_name):
                return f".{selector_name}"
    
    # Pattern 5: Bare selector names (no prefix)
    # Try as ID first if we have ID context, otherwise try both
    bare_name_pattern = r'\b([a-zA-Z][a-zA-Z0-9_-]{2,})\b'
    # Avoid matching common words
    common_words = {
        "the", "and", "for", "with", "that", "this", "product", "page", "element",
        "button", "text", "name", "title", "price", "cart", "checkout", "home"
    }
    
    matches = re.findall(bare_name_pattern, message)
    if matches:
        # Filter out common words and look for selector-like names
        potential_selectors = [
            m for m in matches 
            if m.lower() not in common_words 
            and '-' in m or '_' in m or m.isalnum()
        ]
        
        if potential_selectors:
            # If we have ID context, try ID first
            if has_id_context:
                return f"#{potential_selectors[0]}"
            # If we have class context, try class first
            elif has_class_context:
                return f".{potential_selectors[0]}"
            # Otherwise, we'll return the first one and let validation try both
            # The caller should handle trying both # and . prefixes
            return potential_selectors[0]
    
    # Pattern 6: Attribute selectors [attr=value]
    attr_pattern = r'\[[\w-]+(?:=["\'][^"\']+["\'])?\]'
    attr_matches = re.findall(attr_pattern, message)
    if attr_matches:
        return attr_matches[0]
    
    return None


def extract_element_description_from_message(message: str) -> Optional[str]:
    """
    Extract element description from user message as fallback if Claude doesn't extract it.
    
    Looks for common patterns like:
    - "change [element] to [value]"
    - "modify [element]"
    - "[element] on [page]"
    
    Returns:
        Element description if found, None otherwise
    """
    message_lower = message.lower()
    
    # Common element keywords to look for
    element_keywords = [
        "button", "link", "text", "title", "heading", "image", "form", "input",
        "field", "label", "menu", "nav", "header", "footer", "cart", "checkout",
        "product", "name", "price", "description", "quantity", "add to cart",
        "buy now", "checkout", "submit", "search", "filter", "sort"
    ]
    
    # Pattern: "change [element]" or "modify [element]"
    change_pattern = r'(?:change|modify|update|edit|adjust)\s+([^.,!?]+?)(?:\s+to|\s+on|[,\.!?]|$)'
    match = re.search(change_pattern, message_lower)
    if match:
        element_phrase = match.group(1).strip()
        # Check if it contains element keywords
        if any(keyword in element_phrase for keyword in element_keywords):
            return element_phrase
    
    # Pattern: "on [page]" followed by element or before element
    page_pattern = r'([^.,!?]+?)\s+on\s+(?:pdp|cart|checkout|home|category|search)'
    match = re.search(page_pattern, message_lower)
    if match:
        element_phrase = match.group(1).strip()
        if any(keyword in element_phrase for keyword in element_keywords):
            return element_phrase
    
    # Pattern: "[element] on [page]"
    reverse_pattern = r'(?:pdp|cart|checkout|home|category|search)\s+([^.,!?]+?)(?:[,\.!?]|$)'
    match = re.search(reverse_pattern, message_lower)
    if match:
        element_phrase = match.group(1).strip()
        if any(keyword in element_phrase for keyword in element_keywords):
            return element_phrase
    
    # Try to extract noun phrases that might be elements
    # Look for common patterns like "product name", "checkout button", etc.
    for keyword in element_keywords:
        # Pattern: "[modifier] [keyword]" or "[keyword] [modifier]"
        pattern1 = rf'\b(\w+\s+{keyword}|{keyword}\s+\w+)\b'
        match = re.search(pattern1, message_lower)
        if match:
            element_phrase = match.group(0).strip()
            # Limit length to avoid capturing too much
            if len(element_phrase) < 50:
                return element_phrase
    
    return None


async def try_both_selector_prefixes(
    db: AsyncSession,
    bare_selector_name: str,
    page_type: PageType,
    brand_id: int
) -> Optional[str]:
    """
    Try both # (ID) and . (class) prefixes for a bare selector name.
    
    Args:
        db: Database session
        bare_selector_name: Selector name without prefix (e.g., "product-name")
        page_type: Page type enum
        brand_id: Brand ID
        
    Returns:
        Valid selector string (#prefix or .prefix) if found in DB, None otherwise
    """
    id_selector = f"#{bare_selector_name}"
    class_selector = f".{bare_selector_name}"
    
    # Check both selectors in database
    result = await db.execute(
        select(DOMSelector).where(
            DOMSelector.brand_id == brand_id,
            DOMSelector.page_type == page_type,
            DOMSelector.status == SelectorStatus.ACTIVE,
            DOMSelector.selector.in_([id_selector, class_selector])
        )
    )
    matching_selector = result.scalar_one_or_none()
    
    if matching_selector:
        return matching_selector.selector
    
    # If neither found in DB, prefer ID selector as default
    # (ID is more specific and commonly used)
    return id_selector


async def validate_user_provided_selector(
    db: AsyncSession,
    selector: str,
    page_type: PageType,
    brand_id: int
) -> Tuple[bool, Optional[str]]:
    """
    Validate if a user-provided selector exists in the database.
    
    Args:
        db: Database session
        selector: CSS selector string from user
        page_type: Page type enum
        brand_id: Brand ID
        
    Returns:
        (is_valid: bool, error_message: Optional[str])
    """
    if not selector:
        return False, "Please provide a valid CSS selector."
    
    # Normalize selector
    selector_normalized = selector.strip()
    
    # Basic format validation
    if not re.match(r'^[.#\[][\w\s\-\[\]="\']+$', selector_normalized):
        return False, f"Invalid CSS selector format: {selector_normalized}. Please use a valid selector (e.g., '.class-name' or '#id-name')."
    
    # Check if selector exists in database
    result = await db.execute(
        select(DOMSelector).where(
            DOMSelector.brand_id == brand_id,
            DOMSelector.page_type == page_type,
            DOMSelector.selector == selector_normalized,
            DOMSelector.status == SelectorStatus.ACTIVE
        )
    )
    existing_selector = result.scalar_one_or_none()
    
    if existing_selector:
        return True, None
    else:
        # Selector not in database - suggest adding it or ask for confirmation
        return False, f"""The selector "{selector_normalized}" is not in the database for this page type.

Would you like me to:
1. Generate code using this selector anyway (not recommended - selector may be incorrect)
2. Add this selector to the database first
3. Check if you meant a different selector"""
