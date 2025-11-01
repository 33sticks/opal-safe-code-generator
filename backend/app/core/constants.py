"""Application constants."""

# Claude Sonnet 4.5 Pricing (as of Jan 2025)
CLAUDE_SONNET_4_5_INPUT_COST_PER_MILLION = 3.0  # USD
CLAUDE_SONNET_4_5_OUTPUT_COST_PER_MILLION = 15.0  # USD


def calculate_llm_cost(input_tokens: int, output_tokens: int) -> float:
    """
    Calculate cost for Claude Sonnet 4.5 usage.
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
    
    Returns:
        Total cost in USD, rounded to 4 decimal places
    """
    input_cost = (input_tokens / 1_000_000) * CLAUDE_SONNET_4_5_INPUT_COST_PER_MILLION
    output_cost = (output_tokens / 1_000_000) * CLAUDE_SONNET_4_5_OUTPUT_COST_PER_MILLION
    return round(input_cost + output_cost, 4)

