"""Code generation service using Claude AI."""
import json
import re
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from anthropic import Anthropic
from anthropic import APIError

from app.config import settings
from app.models.enums import RuleType

logger = logging.getLogger(__name__)


class CodeGeneratorService:
    """Service for generating safe JavaScript code using Claude AI."""
    
    def __init__(self):
        """Initialize Anthropic client with API key."""
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is not set in configuration")
        # Simple initialization - only api_key parameter
        # Do not pass any other parameters like proxies, timeout, etc.
        # The Anthropic SDK v0.34.2 doesn't accept those in __init__
        api_key = str(settings.ANTHROPIC_API_KEY).strip()
        self.client = Anthropic(api_key=api_key)
    
    async def generate_code(
        self,
        brand_context: Dict[str, Any],
        templates: List[Dict[str, Any]],
        selectors: List[Dict[str, Any]],
        rules: List[Dict[str, Any]],
        test_description: str
    ) -> Dict[str, Any]:
        """
        Generate safe code using Claude with brand-specific context.
        
        Args:
            brand_context: Dict with brand name, domain, etc.
            templates: List of template dicts with test_type, template_code, etc.
            selectors: List of selector dicts with selector, description, etc.
            rules: List of rule dicts with rule_type, rule_content, etc.
            test_description: User's description of what the test should do
            
        Returns:
            {
                "generated_code": str,
                "confidence_score": float,
                "implementation_notes": str,
                "testing_checklist": str
            }
        """
        try:
            # Build comprehensive prompt
            prompt = self._build_prompt(
                brand_context, templates, selectors, rules, test_description
            )
            
            # Call Claude API (run in thread pool since it's blocking)
            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-sonnet-4-20250514",
                max_tokens=8192,  # Increased for complex code generation
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract usage data from Claude API response
            prompt_tokens = getattr(response.usage, 'input_tokens', 0) if hasattr(response, 'usage') else 0
            completion_tokens = getattr(response.usage, 'output_tokens', 0) if hasattr(response, 'usage') else 0
            total_tokens = prompt_tokens + completion_tokens
            
            # Check stop_reason to detect truncation
            stop_reason = getattr(response, 'stop_reason', None)
            if stop_reason == "max_tokens":
                logger.warning(f"Code generation hit token limit (max_tokens={8192}). Output may be truncated.")
            elif stop_reason:
                logger.info(f"Response stop_reason: {stop_reason}")
            
            # Log response details
            logger.info(f"Generated code response - stop_reason: {stop_reason}, completion_tokens: {completion_tokens}/{8192}")
            
            # Parse response
            parsed_response = self._parse_claude_response(response)
            
            generated_code = parsed_response.get("generated_code", "")
            
            # Log generated code length for debugging
            logger.info(f"Generated code length: {len(generated_code)} characters")
            
            # Check for truncation
            is_truncated = self._is_code_truncated(generated_code)
            if is_truncated:
                logger.warning("Generated code appears truncated - may be incomplete")
                if stop_reason == "max_tokens":
                    logger.warning("Truncation detected due to token limit - consider increasing max_tokens further")
            
            # Replace placeholders in generated code if global template was used
            global_template = brand_context.get("code_template", {}).get("global_template")
            if global_template:
                logger.info("Global template detected - replacing placeholders in generated code")
                generated_code = self._replace_placeholders(
                    generated_code, test_description, brand_context
                )
                logger.info("Placeholder replacement completed")
                
                # Re-check truncation after placeholder replacement (placeholders might cause issues)
                is_truncated = self._is_code_truncated(generated_code) or is_truncated
                if is_truncated:
                    logger.warning("Generated code appears truncated after placeholder replacement")
            
            implementation_notes = parsed_response.get("implementation_notes", "Generated by Claude")
            testing_checklist = parsed_response.get("testing_checklist", "Review code manually")
            
            # Validate generated code
            validation_results = self._validate_code(
                generated_code, rules, selectors
            )
            
            # Calculate confidence score and breakdown
            confidence_result = self._calculate_confidence(
                generated_code, templates, validation_results
            )
            confidence_score = confidence_result["confidence_score"]
            confidence_breakdown = confidence_result["confidence_breakdown"]
            
            return {
                "generated_code": generated_code,
                "confidence_score": confidence_score,
                "confidence_breakdown": confidence_breakdown,
                "implementation_notes": implementation_notes,
                "testing_checklist": testing_checklist,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "is_truncated": is_truncated,
                "stop_reason": stop_reason
            }
            
        except APIError as e:
            logger.error(f"Claude API error: {str(e)}")
            raise Exception(f"Failed to generate code: {str(e)}")
        except Exception as e:
            logger.error(f"Code generation error: {str(e)}")
            raise Exception(f"Code generation failed: {str(e)}")
    
    def _build_prompt(
        self,
        brand_context: Dict[str, Any],
        templates: List[Dict[str, Any]],
        selectors: List[Dict[str, Any]],
        rules: List[Dict[str, Any]],
        test_description: str
    ) -> str:
        """Build comprehensive prompt for Claude."""
        brand_name = brand_context.get("name", "Unknown")
        brand_domain = brand_context.get("domain", "")
        brand_code_template = brand_context.get("code_template", {})
        global_template = brand_code_template.get("global_template")
        
        # Build selectors section
        selectors_text = "Available DOM Selectors:\n"
        if selectors:
            for selector in selectors:
                selector_str = selector.get("selector", "")
                desc = selector.get("description", "")
                selectors_text += f"- {selector_str}"
                if desc:
                    selectors_text += f" ({desc})"
                selectors_text += "\n"
        else:
            selectors_text += "- No selectors available for this page type\n"
        
        # Build rules section
        forbidden_patterns = [
            r["rule_content"] for r in rules 
            if r.get("rule_type") == RuleType.FORBIDDEN_PATTERN.value
        ]
        required_patterns = [
            r["rule_content"] for r in rules 
            if r.get("rule_type") == RuleType.REQUIRED_PATTERN.value
        ]
        
        rules_text = "Code Rules:\n"
        if forbidden_patterns:
            rules_text += "FORBIDDEN Patterns (DO NOT USE):\n"
            for pattern in forbidden_patterns:
                rules_text += f"- {pattern}\n"
        if required_patterns:
            rules_text += "REQUIRED Patterns:\n"
            for pattern in required_patterns:
                rules_text += f"- {pattern}\n"
        if not forbidden_patterns and not required_patterns:
            rules_text += "- No specific rules defined\n"
        
        # Build template section - prioritize global template if available
        template_text = ""
        if global_template:
            # Extract features from test description
            features = self._extract_features(test_description)
            features_text = "\n".join([f" * - {f}" for f in features])
            
            # Build global template section with placeholders shown
            template_text = "GLOBAL TEMPLATE (Company-wide Structure - MUST FOLLOW EXACTLY):\n"
            template_text += "```javascript\n"
            template_text += global_template
            template_text += "\n```\n\n"
            template_text += "CRITICAL INSTRUCTIONS FOR GLOBAL TEMPLATE:\n"
            template_text += "1. Follow the EXACT structure of the global template above\n"
            template_text += "2. Keep ALL section dividers (// ===...===)\n"
            template_text += "3. Keep ALL configuration variables (CONFIG object)\n"
            template_text += "4. Keep ALL logging utilities and LOG_PREFIX constant\n"
            template_text += "5. Keep the utils.waitForElement() wrapper\n"
            template_text += "6. Keep ALL error handling try/catch blocks\n"
            template_text += "7. Replace placeholders: {test_id}, {summary}, {version}, {date}, {features}\n"
            template_text += "8. Place your page-specific code ONLY in the 'PAGE-SPECIFIC CODE GOES HERE' section\n"
            template_text += "9. Use LOG_PREFIX constant for all console.log statements\n"
            template_text += "10. Use the log() utility function instead of direct console.log\n\n"
            
            # Add page template as reference for page-specific logic
            if templates:
                page_template = templates[0]
                template_text += f"PAGE TEMPLATE (Reference for page-specific logic patterns):\n"
                template_text += f"Test Type: {page_template.get('test_type', 'unknown')}\n"
                template_text += f"```javascript\n{page_template.get('template_code', '')}\n```\n\n"
                template_text += "Use the page template above as a REFERENCE for:\n"
                template_text += "- How to structure page-specific DOM queries\n"
                template_text += "- How to handle element validation\n"
                template_text += "- How to structure the logic within the main execution section\n"
        else:
            # No global template - use page template as before
            template_text = "Template Example:\n"
            if templates:
                template = templates[0]  # Use first template
                template_text += f"Test Type: {template.get('test_type', 'unknown')}\n"
                template_text += f"Template Code:\n```javascript\n{template.get('template_code', '')}\n```\n"
            else:
                template_text += "No template available - generate safe JavaScript following best practices\n"
        
        # Build prompt
        if global_template:
            prompt = f"""You are a JavaScript code generator for A/B testing. Generate safe, production-ready JavaScript code for the {brand_name} brand ({brand_domain}).

{selectors_text}

{rules_text}

{template_text}

Test Description:
{test_description}

Requirements:
1. Follow the EXACT structure of the global template - do not modify sections, dividers, or utility functions
2. Replace all placeholders ({{test_id}}, {{summary}}, {{version}}, {{date}}, {{features}}) with appropriate values
3. Generate safe JavaScript code that does NOT use: eval(), innerHTML, document.write(), or any forbidden patterns
4. Use only the available DOM selectors listed above
5. Place page-specific logic ONLY in the designated "PAGE-SPECIFIC CODE GOES HERE" section
6. Use the log() utility function with LOG_PREFIX for all logging
7. Maintain all error handling, configuration, and structure from the global template
8. Ensure the code is production-ready and follows JavaScript best practices

Placeholder Values to Use:
- {{test_id}}: Generate a test ID like "TE-XXX" or use a descriptive identifier
- {{summary}}: Create a brief summary based on the test description
- {{version}}: Use "1.0"
- {{date}}: Use current date in format "YYYY-MM-DD"
- {{features}}: Extract key features from the test description

CRITICAL OUTPUT FORMAT:
You must return ONLY the raw JavaScript code.
Do NOT wrap it in JSON with fields like "generated_code" or "implementation_notes".
Do NOT include markdown code blocks (```javascript or ```).
Do NOT include any explanatory text, JSON, or metadata.

Your entire response should be executable JavaScript that starts with comments and ends with the closing brace.
The code should be ready to copy/paste directly into Optimizely.

Example of correct format:
'use strict';
// Test code starts here
(function() {{
  // code
}})();

Example of WRONG format (do not do this):
{{
  "generated_code": "...",
  "notes": "..."
}}
"""
        else:
            # Original prompt without global template
            prompt = f"""You are a JavaScript code generator for A/B testing. Generate safe, production-ready JavaScript code for the {brand_name} brand ({brand_domain}).

{selectors_text}

{rules_text}

{template_text}

Test Description:
{test_description}

Requirements:
1. Generate safe JavaScript code that does NOT use: eval(), innerHTML, document.write(), or any forbidden patterns
2. Use only the available DOM selectors listed above
3. Follow the template structure and patterns shown
4. Ensure the code is production-ready and follows JavaScript best practices
5. Include comments explaining key logic

CRITICAL OUTPUT FORMAT:
You must return ONLY the raw JavaScript code.
Do NOT wrap it in JSON with fields like "generated_code" or "implementation_notes".
Do NOT include markdown code blocks (```javascript or ```).
Do NOT include any explanatory text, JSON, or metadata.

Your entire response should be executable JavaScript that starts with comments and ends with the closing brace.
The code should be ready to copy/paste directly into Optimizely.

Example of correct format:
'use strict';
// Test code starts here
(function() {{
  // code
}})();

Example of WRONG format (do not do this):
{{
  "generated_code": "...",
  "notes": "..."
}}
"""
        
        return prompt
    
    def _extract_features(self, test_description: str) -> List[str]:
        """Extract key features from test description."""
        features = []
        # Simple extraction - look for action verbs and key phrases
        description_lower = test_description.lower()
        
        # Common feature keywords
        feature_keywords = [
            "change", "modify", "update", "add", "remove", "highlight",
            "display", "show", "hide", "enable", "disable", "validate",
            "track", "measure", "improve", "enhance"
        ]
        
        # Split description into sentences/clauses
        sentences = re.split(r'[.,;!?]\s+', test_description)
        for sentence in sentences:
            sentence = sentence.strip()
            if any(keyword in sentence.lower() for keyword in feature_keywords):
                if len(sentence) > 10:  # Filter out very short fragments
                    features.append(sentence[:100])  # Limit length
        
        # If no features extracted, create from description
        if not features:
            # Break description into logical parts
            if " and " in description_lower:
                parts = test_description.split(" and ")
                features = [p.strip() for p in parts if len(p.strip()) > 10]
            elif "," in test_description:
                parts = test_description.split(",")
                features = [p.strip() for p in parts if len(p.strip()) > 10]
            else:
                features = [test_description[:100]]
        
        return features[:5]  # Limit to 5 features
    
    def _replace_placeholders(
        self,
        code: str,
        test_description: str,
        brand_context: Dict[str, Any]
    ) -> str:
        """Replace placeholders in generated code."""
        # Generate placeholder values
        logger.info("Generating test ID...")
        test_id = self._generate_test_id(test_description)
        logger.info(f"Generated test ID: {test_id}")
        
        summary = self._generate_summary(test_description)
        version = "1.0"
        date = datetime.now().strftime("%Y-%m-%d")
        features = self._extract_features(test_description)
        features_text = "\n".join([f" * - {f}" for f in features])
        
        # Replace placeholders
        replacements = {
            "{test_id}": test_id,
            "{summary}": summary,
            "{version}": version,
            "{date}": date,
            "{features}": features_text if features_text else " * - Test implementation"
        }
        
        for placeholder, value in replacements.items():
            code = code.replace(placeholder, value)
        
        return code
    
    def _generate_test_id(self, test_description: str) -> str:
        """Generate a test ID from description."""
        # Extract first meaningful words or use a generic ID
        words = test_description.split()[:3]
        if words:
            # Create ID like "TE-CHECKOUT-BUTTON" or similar
            acronym = "".join([w[0].upper() for w in words if len(w) > 2])[:5]
            return f"TE-{acronym}" if acronym else "TE-TEST"
        return "TE-TEST"
    
    def _generate_summary(self, test_description: str) -> str:
        """Generate a summary from test description."""
        # Clean up and limit length
        summary = test_description.strip()
        if len(summary) > 150:
            summary = summary[:147] + "..."
        return summary
    
    def _parse_claude_response(self, response: Any) -> Dict[str, Any]:
        """
        Parse Claude API response, handling raw JavaScript (preferred) or JSON (fallback).
        
        Claude should return raw JavaScript code, but we also handle JSON-wrapped responses
        for backwards compatibility and robustness.
        """
        # Extract text from Claude response
        content = response.content
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
        
        original_text = text
        text = text.strip()
        
        # First, check if response is JSON-wrapped (fallback case)
        # Look for JSON structure with "generated_code" field
        if '"generated_code"' in text or "'generated_code'" in text or (text.startswith('{') and '"generated_code"' in text):
            logger.info("Detected JSON-wrapped response, extracting code from JSON")
            try:
                # Strip markdown code block markers if present
                if text.startswith("```json"):
                    text = text[7:]
                elif text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
                
                parsed = json.loads(text)
                if isinstance(parsed, dict) and "generated_code" in parsed:
                    return {
                        "generated_code": parsed.get("generated_code", ""),
                        "implementation_notes": parsed.get("implementation_notes", "Generated by Claude"),
                        "testing_checklist": parsed.get("testing_checklist", "Review code manually")
                    }
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON, attempting to extract code from JSON string")
                # Try regex extraction as fallback
                try:
                    # Match "generated_code": "..." or 'generated_code': '...'
                    match = re.search(
                        r'["\']generated_code["\']\s*:\s*["\']((?:[^"\'\\]|\\.|\\n|\\t)*)["\']',
                        original_text,
                        re.DOTALL
                    )
                    if match:
                        code = match.group(1)
                        # Unescape JSON string
                        code = code.replace('\\n', '\n')
                        code = code.replace('\\t', '\t')
                        code = code.replace('\\"', '"')
                        code = code.replace("\\'", "'")
                        code = code.replace('\\\\', '\\')
                        logger.info("Extracted code from JSON wrapper using regex")
                        return {
                            "generated_code": code,
                            "implementation_notes": "Generated by Claude",
                            "testing_checklist": "Review code manually"
                        }
                except Exception as e:
                    logger.warning(f"Failed to extract code from JSON: {e}")
        
        # Assume raw JavaScript (preferred case)
        # Strip markdown code block markers if present
        if text.startswith("```javascript"):
            text = text[13:]  # Remove ```javascript
        elif text.startswith("```js"):
            text = text[5:]  # Remove ```js
        elif text.startswith("```"):
            text = text[3:]  # Remove ```
        if text.endswith("```"):
            text = text[:-3]  # Remove trailing ```
        text = text.strip()
        
        # If text is empty or doesn't look like code, try fallback extraction
        if not text or (not any(keyword in text for keyword in ['function', 'const', 'let', 'var', 'document.', 'window.', '(', ')'])):
            logger.warning("Response doesn't look like JavaScript, attempting fallback parsing")
            # Try to extract code from markdown blocks
            js_match = re.search(r'```(?:javascript|js)?\s*\n(.*?)```', original_text, re.DOTALL)
            if js_match:
                text = js_match.group(1).strip()
            else:
                # Use original text as fallback
                text = original_text.strip()
        
        # Return raw JavaScript code (preferred format)
        return {
            "generated_code": text,
            "implementation_notes": "Generated by Claude",
            "testing_checklist": "Review code manually - verify all functionality"
        }
    
    def _validate_code(
        self,
        code: str,
        rules: List[Dict[str, Any]],
        selectors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate generated code against rules and selectors.
        
        Returns:
            {
                "rule_violations": List[str],
                "invalid_selectors": List[str],
                "is_valid": bool
            }
        """
        rule_violations = []
        invalid_selectors = []
        
        # Check forbidden patterns
        forbidden_patterns = [
            r["rule_content"] for r in rules 
            if r.get("rule_type") == RuleType.FORBIDDEN_PATTERN.value
        ]
        
        for pattern in forbidden_patterns:
            # Simple substring match for now (could be enhanced with regex)
            if pattern.lower() in code.lower():
                rule_violations.append(f"Found forbidden pattern: {pattern}")
        
        # Extract selectors used in code
        # Look for common selector patterns: querySelector, getElementById, etc.
        selector_patterns = [
            r'querySelector\(["\']([^"\']+)["\']\)',
            r'querySelectorAll\(["\']([^"\']+)["\']\)',
            r'getElementById\(["\']([^"\']+)["\']\)',
            r'\.classList\[["\']([^"\']+)["\']\]',
        ]
        
        used_selectors = set()
        for pattern in selector_patterns:
            matches = re.findall(pattern, code)
            used_selectors.update(matches)
        
        # Also look for direct selector usage like .class-name or #id-name
        direct_selectors = re.findall(r'["\']([.#][\w-]+)["\']', code)
        used_selectors.update(direct_selectors)
        
        # Validate against available selectors
        available_selectors = {s.get("selector", "") for s in selectors}
        for used in used_selectors:
            # Normalize selector (remove quotes, whitespace)
            normalized = used.strip().strip('"\'')
            if normalized and normalized not in available_selectors:
                # Check if it's a partial match (e.g., ".button" might match ".checkout-button")
                is_partial_match = any(
                    normalized in avail or avail in normalized 
                    for avail in available_selectors
                )
                if not is_partial_match:
                    invalid_selectors.append(normalized)
        
        return {
            "rule_violations": rule_violations,
            "invalid_selectors": invalid_selectors,
            "is_valid": len(rule_violations) == 0 and len(invalid_selectors) == 0
        }
    
    def _calculate_recommendation(
        self,
        score: float,
        is_valid: bool,
        rule_violations: List[str],
        invalid_selectors: List[str]
    ) -> str:
        """
        Calculate recommendation based on confidence score and validation results.
        
        Returns:
            "safe_to_use": score >= 0.8 AND is_valid AND no violations
            "review_carefully": score >= 0.6 OR has warnings
            "needs_fixes": score < 0.6 OR has violations OR invalid selectors
        """
        has_violations = len(rule_violations) > 0 or len(invalid_selectors) > 0
        
        if score >= 0.8 and is_valid and not has_violations:
            return "safe_to_use"
        elif score >= 0.6:
            return "review_carefully"
        else:
            return "needs_fixes"
    
    def _get_validation_status(
        self,
        is_valid: bool,
        rule_violations: List[str]
    ) -> str:
        """
        Determine validation status based on validation results.
        
        Returns:
            "passed": is_valid == True AND no violations
            "failed": is_valid == False OR has violations
            "warning": is_valid == True BUT has issues
        """
        has_violations = len(rule_violations) > 0
        
        if is_valid and not has_violations:
            return "passed"
        elif not is_valid or has_violations:
            return "failed"
        else:
            return "warning"
    
    def _calculate_confidence(
        self,
        code: str,
        templates: List[Dict[str, Any]],
        validation_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate confidence score and breakdown for generated code.
        
        Scoring:
        - Template adherence: 30%
        - Rule compliance: 40%
        - Selector validation: 30%
        
        Returns:
            Dict with "confidence_score" (float) and "confidence_breakdown" (dict)
        """
        template_score = 0.0
        rule_score = 0.0
        selector_score = 0.0
        
        # Template adherence (30%)
        if templates:
            template = templates[0]
            template_code = template.get("template_code", "").lower()
            # Check if generated code uses similar patterns
            # Simple heuristic: check for common function patterns
            template_functions = set(re.findall(r'\bfunction\s+(\w+)', template_code))
            code_functions = set(re.findall(r'\bfunction\s+(\w+)', code.lower()))
            
            if template_functions:
                overlap = len(template_functions & code_functions) / len(template_functions)
                template_score = overlap * 0.3
            else:
                # If no functions, check for similar structure
                if 'querySelector' in template_code and 'querySelector' in code.lower():
                    template_score = 0.2
                elif template_code and code:
                    # Basic similarity check
                    template_keywords = set(template_code.split())
                    code_keywords = set(code.lower().split())
                    common = template_keywords & code_keywords
                    if template_keywords:
                        template_score = (len(common) / len(template_keywords)) * 0.3
        else:
            template_score = 0.1  # Low score if no template
        
        # Rule compliance (40%)
        if validation_results["is_valid"]:
            rule_score = 0.4
        else:
            violations = len(validation_results["rule_violations"])
            # Penalize based on number of violations
            rule_score = max(0.0, 0.4 - (violations * 0.1))
        
        # Selector validation (30%)
        invalid_selectors = len(validation_results["invalid_selectors"])
        if invalid_selectors == 0:
            selector_score = 0.3
        else:
            # Penalize for invalid selectors
            selector_score = max(0.0, 0.3 - (invalid_selectors * 0.05))
        
        total_score = template_score + rule_score + selector_score
        
        # Ensure score is between 0 and 1
        confidence_score = min(1.0, max(0.0, total_score))
        
        # Get validation status and recommendation
        rule_violations = validation_results.get("rule_violations", [])
        invalid_selectors_list = validation_results.get("invalid_selectors", [])
        is_valid = validation_results.get("is_valid", False)
        
        validation_status = self._get_validation_status(is_valid, rule_violations)
        recommendation = self._calculate_recommendation(
            confidence_score, is_valid, rule_violations, invalid_selectors_list
        )
        
        # Build breakdown dict
        breakdown = {
            "overall_score": confidence_score,
            "template_score": template_score,
            "rule_score": rule_score,
            "selector_score": selector_score,
            "rule_violations": rule_violations,
            "invalid_selectors": invalid_selectors_list,
            "is_valid": is_valid,
            "validation_status": validation_status,
            "recommendation": recommendation
        }
        
        return {
            "confidence_score": confidence_score,
            "confidence_breakdown": breakdown
        }
    
    def _is_code_truncated(self, code: str) -> bool:
        """
        Detect if generated code appears truncated.
        
        Signs of truncation:
        - Doesn't end with closing brace or semicolon
        - Has unclosed function/observer/try-catch blocks
        - Ends mid-line
        - Stop reason was max_tokens
        
        Args:
            code: Generated code string to check
            
        Returns:
            True if code appears truncated, False otherwise
        """
        if not code or not code.strip():
            return False
        
        code_stripped = code.strip()
        
        # Check if ends properly
        valid_endings = ['}', '});', '};', ');', ';']
        ends_properly = any(code_stripped.endswith(ending) for ending in valid_endings)
        
        if not ends_properly:
            # Check if it ends mid-statement (not at line boundary)
            last_line = code_stripped.split('\n')[-1] if '\n' in code_stripped else code_stripped
            # If last line doesn't end with semicolon, brace, or proper closing, likely truncated
            if last_line and not any(last_line.rstrip().endswith(ending) for ending in ['}', ';', ');', '});', '};']):
                return True
        
        # Check for unclosed blocks (simple heuristic)
        open_braces = code.count('{')
        close_braces = code.count('}')
        
        if open_braces != close_braces:
            return True
        
        # Check for unclosed parentheses
        open_parens = code.count('(')
        close_parens = code.count(')')
        
        if open_parens != close_parens:
            return True
        
        # Check for common incomplete patterns
        incomplete_patterns = [
            r'Observer\.observe\([^)]*$',  # observer.observe( without closing
            r'addEventListener\([^)]*$',    # addEventListener( without closing
            r'\.then\([^)]*$',              # .then( without closing
            r'function\s+\w+\([^)]*$',     # function declaration without closing
            r'const\s+\w+\s*=\s*[^;{]+$',  # const assignment incomplete
        ]
        
        last_lines = code_stripped.split('\n')[-3:] if len(code_stripped.split('\n')) >= 3 else [code_stripped]
        for pattern in incomplete_patterns:
            for line in last_lines:
                if re.search(pattern, line):
                    return True
        
        return False

