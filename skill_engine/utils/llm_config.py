"""
LLM Configuration utility module.

Provides centralized detection and management of available LLM providers
and their configurations from environment variables.
"""

import os
from typing import Tuple
from loguru import logger


def get_available_llm_config() -> Tuple[str, str, str]:
    """
    Detect available LLM provider and model from environment.
    
    Checks for API keys in this order:
    1. OPENAI_API_KEY (with optional OPENAI_MODEL_NAME)
    2. ANTHROPIC_API_KEY (with optional ANTHROPIC_MODEL_NAME)
    
    Returns:
        Tuple of (provider, model_name, api_key)
        
    Raises:
        ValueError: If no API key is configured
        
    Examples:
        >>> provider, model, api_key = get_available_llm_config()
        >>> print(f"Using {provider}: {model}")
        Using anthropic: claude-3-5-sonnet-20241022
    """
    # Check for OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        model = os.getenv("OPENAI_MODEL_NAME", "gpt-4")
        logger.info(f"Using OpenAI provider with model: {model}")
        return "openai", model, openai_api_key
    
    # Check for Anthropic
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_api_key:
        model = os.getenv("ANTHROPIC_MODEL_NAME", "claude-3-5-sonnet-20241022")
        logger.info(f"Using Anthropic provider with model: {model}")
        return "anthropic", model, anthropic_api_key
    
    # No API keys found
    error_message = (
        "No LLM API key found in environment variables.\n"
        "Please set one of the following:\n"
        "  - OPENAI_API_KEY (with optional OPENAI_MODEL_NAME)\n"
        "  - ANTHROPIC_API_KEY (with optional ANTHROPIC_MODEL_NAME)\n"
        "\nExample .env file:\n"
        "  ANTHROPIC_API_KEY=sk-ant-...\n"
        "  ANTHROPIC_MODEL_NAME=claude-3-5-sonnet-20241022"
    )
    logger.error(error_message)
    raise ValueError(error_message)


def get_llm_display_name(provider: str, model: str) -> str:
    """
    Get a human-readable display name for the LLM configuration.
    
    Args:
        provider: LLM provider name ("openai" or "anthropic")
        model: Model name
        
    Returns:
        Formatted display string
        
    Examples:
        >>> get_llm_display_name("openai", "gpt-4")
        'OpenAI GPT-4'
        >>> get_llm_display_name("anthropic", "claude-3-5-sonnet-20241022")
        'Anthropic Claude 3.5 Sonnet'
    """
    provider_display = {
        "openai": "OpenAI",
        "anthropic": "Anthropic"
    }.get(provider.lower(), provider)
    
    return f"{provider_display} - {model}"