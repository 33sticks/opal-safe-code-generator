"""Chat prompt builder for Claude API."""
from typing import List, Dict, Any
from app.models.enums import TestType, PageType


def build_chat_prompt(
    conversation_history: List[Dict[str, str]],
    brand_name: str,
    brand_domain: str,
    test_types: List[str],
    page_types: List[str]
) -> str:
    """
    Build system prompt for Claude chat interface.
    
    Args:
        conversation_history: List of message dicts with 'role' and 'content'
        brand_name: Brand name for context
        brand_domain: Brand domain for context
        test_types: Available test types
        page_types: Available page types
        
    Returns:
        System prompt string for Claude
    """
    # Build available options text
    test_types_text = ", ".join([t.upper() for t in test_types])
    page_types_text = ", ".join([p.upper() for p in page_types])
    
    system_prompt = f"""You are a helpful A/B testing code generation assistant for {brand_name} ({brand_domain}).

Your job is to gather information from the user to generate safe, production-ready test code.

Available test types: {test_types_text}
Available page types: {page_types_text}

CONVERSATION RULES:
1. Ask ONE question at a time (don't overwhelm user)
2. Be friendly and conversational
3. Suggest options when helpful (e.g., "Is this for PDP, Cart, or Checkout?")
4. When you have enough info, confirm before generating

REQUIRED INFO FOR CODE GENERATION:
- Page type (PDP, Cart, Checkout, etc.)
- Element to modify (be specific)
- What change to make (color, text, visibility, position, etc.)
- Desired outcome

SELECTOR SEARCH GUIDANCE:
When extracting element descriptions from user requests:
1. Extract key elements they want to modify (buttons, images, text, links, etc.)
2. The system uses semantic matching to find selectors - it understands:
   - Element types (image, button, text, container)
   - Synonyms and related terms (e.g., "product image" matches "picture" selector)
   - Context keywords (e.g., "sibling", "child", "parent" for relationships)
3. When multiple selectors match, the system will present options to the user
4. When no exact match is found, the system will show available selectors for that page type
5. Only ask for HTML paste if truly no relevant selectors exist

ELEMENT DESCRIPTION TIPS:
- Be specific: "product image" is better than "image"
- Include context: "add to cart button" is better than "button"
- Use natural language: "product title" or "price" work well
- The system will match semantically, so "image" will find "picture" selectors

When you have all required info, respond with JSON:
{{
    "message": "Perfect! I have everything I need. Let me generate the code...",
    "ready_to_generate": true,
    "extracted_params": {{
        "page_type": "checkout",
        "test_type": "checkout",
        "element_description": "checkout button",
        "change_description": "change color to red"
    }}
}}

If you need more info, respond with JSON:
{{
    "message": "What color would you like the button to be?",
    "ready_to_generate": false
}}

IMPORTANT: Always return valid JSON. Do not include markdown code blocks or backticks."""

    return system_prompt


def build_conversation_messages(
    conversation_history: List[Dict[str, str]],
    user_message: str
) -> List[Dict[str, str]]:
    """
    Build message list for Claude API from conversation history.
    
    Args:
        conversation_history: List of previous messages with 'role' and 'content'
        user_message: Current user message
        
    Returns:
        List of message dicts formatted for Claude API
    """
    messages = []
    
    # Add conversation history
    for msg in conversation_history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Add current user message
    messages.append({
        "role": "user",
        "content": user_message
    })
    
    return messages

