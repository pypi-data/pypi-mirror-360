"""
Legacy LLM module - Provides backward compatibility for call_llm function.
Uses the new intelligence module under the hood.
"""

import os
from .intelligence import invoke_intelligence


def call_llm(prompt: str, model: str = "gpt-4") -> str:
    """
    Legacy function for calling LLMs.
    Maintained for backward compatibility.

    Args:
        prompt: The input prompt
        model: The model to use (defaults to gpt-4)

    Returns:
        Response from the LLM
    """
    # Create OpenAI config for backward compatibility
    config = {
        "engine": "openai",
        "model": model,
        "api_key": os.getenv("OPENAI_API_KEY"),
        "endpoint": "https://api.openai.com/v1",
        "temperature": 0.7,
        "max_tokens": 150,
    }

    result = invoke_intelligence(prompt, config)

    # Ensure we return a string for backward compatibility
    if isinstance(result, str):
        return result
    else:
        # If it's a dict (error response), convert to string
        return str(result.get("error", "Unknown error occurred"))
