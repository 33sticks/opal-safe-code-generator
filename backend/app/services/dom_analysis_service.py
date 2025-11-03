"""DOM Analysis service using Claude API."""
import json
import re
import logging
import time
from typing import Optional
from anthropic import AsyncAnthropic
from anthropic import APIError

from app.config import settings
from app.core.prompts.dom_analysis_prompt import get_dom_analysis_prompt
from app.schemas.dom_analysis import DomAnalysisResult

logger = logging.getLogger(__name__)


class DomAnalysisService:
    """Service for analyzing HTML and extracting DOM selector information using Claude API."""
    
    def __init__(self):
        """Initialize Anthropic client with API key."""
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is not set in configuration")
        
        api_key = str(settings.ANTHROPIC_API_KEY).strip()
        self.client = AsyncAnthropic(api_key=api_key)
        logger.info("DomAnalysisService initialized")
    
    async def analyze_html(
        self,
        html: str,
        page_type: str,
        brand_name: str = ""
    ) -> DomAnalysisResult:
        """
        Analyze HTML and return structured selector data.
        
        Args:
            html: HTML snippet to analyze
            page_type: Type of page (PDP, Cart, Home, etc.)
            brand_name: Optional brand name for context
            
        Returns:
            DomAnalysisResult with selectors, relationships, patterns
            
        Raises:
            ValueError: If HTML is invalid or response malformed
            Exception: If API call fails
        """
        start_time = time.time()
        
        # Validate input
        if not html or not html.strip():
            raise ValueError("HTML content is empty or invalid")
        
        if not page_type or not page_type.strip():
            raise ValueError("page_type is required")
        
        logger.info(f"Starting DOM analysis for page_type: {page_type}, brand: {brand_name or 'N/A'}")
        logger.debug(f"HTML size: {len(html)} characters")
        
        try:
            # Format prompt using template
            prompt = get_dom_analysis_prompt(
                html=html,
                page_type=page_type,
                brand_name=brand_name
            )
            
            logger.debug(f"Prompt length: {len(prompt)} characters")
            
            # Call Claude API
            logger.debug("Calling Claude API...")
            api_start_time = time.time()
            
            message = await self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            api_duration = time.time() - api_start_time
            logger.info(f"Claude API call completed in {api_duration:.2f} seconds")
            
            # Extract text from response
            response_text = self._extract_response_text(message)
            logger.debug(f"Response text length: {len(response_text)} characters")
            
            # Parse JSON (handle markdown code blocks if present)
            parsed_data = self._parse_json_response(response_text)
            
            # Validate response structure
            self._validate_response_structure(parsed_data)
            
            # Validate and create Pydantic model
            result = DomAnalysisResult(**parsed_data)
            
            total_duration = time.time() - start_time
            logger.info(
                f"DOM analysis completed successfully in {total_duration:.2f} seconds. "
                f"Found {len(result.selectors)} selectors, {len(result.patterns)} patterns"
            )
            
            return result
            
        except APIError as e:
            logger.error(f"Claude API error: {str(e)}")
            raise Exception(f"Failed to analyze HTML: {str(e)}")
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            raise ValueError(f"Failed to parse Claude API response as JSON: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during DOM analysis: {str(e)}")
            raise Exception(f"DOM analysis failed: {str(e)}")
    
    def _extract_response_text(self, message) -> str:
        """
        Extract text content from Claude API response.
        
        Args:
            message: Claude API message response
            
        Returns:
            Extracted text content as string
        """
        content = message.content
        if isinstance(content, list):
            # Handle list of content blocks
            text = ""
            for block in content:
                if hasattr(block, 'text'):
                    text += block.text
                elif isinstance(block, str):
                    text += block
        elif hasattr(content, 'text'):
            text = content.text
        elif isinstance(content, str):
            text = content
        else:
            text = str(content)
        
        return text.strip()
    
    def _parse_json_response(self, response_text: str) -> dict:
        """
        Parse JSON from Claude API response, handling markdown code blocks.
        
        Args:
            response_text: Raw text response from Claude API
            
        Returns:
            Parsed JSON as dictionary
            
        Raises:
            ValueError: If JSON is malformed or cannot be parsed
        """
        if not response_text:
            raise ValueError("Response text is empty")
        
        # Strip markdown code blocks if present
        text = response_text.strip()
        had_markdown = False
        
        # Remove leading markdown code block markers
        if text.startswith("```json"):
            text = text[7:]
            had_markdown = True
            logger.debug("Detected ```json markdown block, stripping...")
        elif text.startswith("```"):
            text = text[3:]
            had_markdown = True
            logger.debug("Detected ``` markdown block, stripping...")
        
        # Remove trailing markdown code block markers
        if text.endswith("```"):
            text = text[:-3]
            had_markdown = True
        
        text = text.strip()
        
        if had_markdown:
            logger.warning("Response contained markdown code blocks, stripping...")
        
        # Parse JSON
        try:
            parsed = json.loads(text)
            if not isinstance(parsed, dict):
                raise ValueError("Parsed JSON is not a dictionary")
            
            logger.debug("JSON parsed successfully")
            return parsed
            
        except json.JSONDecodeError as e:
            # Try to extract JSON from text if it's embedded
            logger.warning("Direct JSON parsing failed, attempting to extract JSON from text...")
            
            # Try to find JSON object in the text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group(0))
                    logger.info("Successfully extracted JSON from embedded text")
                    return parsed
                except json.JSONDecodeError:
                    pass
            
            # If all parsing attempts fail, raise with helpful error
            raise ValueError(
                f"Failed to parse response as JSON. "
                f"Response may be malformed. Error: {str(e)}"
            )
    
    def _validate_response_structure(self, data: dict) -> None:
        """
        Validate that response contains required fields.
        
        Args:
            data: Parsed JSON data
            
        Raises:
            ValueError: If required fields are missing
        """
        required_fields = ["selectors", "relationships", "patterns", "recommendations"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise ValueError(
                f"Response missing required fields: {', '.join(missing_fields)}"
            )
        
        # Validate relationships structure
        if not isinstance(data.get("relationships"), dict):
            raise ValueError("'relationships' must be a dictionary")
        
        relationships = data["relationships"]
        expected_rel_fields = ["containers", "interactive", "content"]
        missing_rel_fields = [
            field for field in expected_rel_fields 
            if field not in relationships
        ]
        
        if missing_rel_fields:
            logger.warning(
                f"Response missing optional relationship fields: {', '.join(missing_rel_fields)}. "
                f"Using empty lists as defaults."
            )
            for field in missing_rel_fields:
                relationships[field] = []
        
        # Validate selectors is a list
        if not isinstance(data.get("selectors"), list):
            raise ValueError("'selectors' must be a list")
        
        # Validate patterns and recommendations are lists
        for field in ["patterns", "recommendations"]:
            if field in data and not isinstance(data[field], list):
                raise ValueError(f"'{field}' must be a list")
        
        # Validate warnings (optional, but should be list if present)
        if "warnings" in data and not isinstance(data["warnings"], list):
            logger.warning("'warnings' field is not a list, converting to empty list")
            data["warnings"] = []

