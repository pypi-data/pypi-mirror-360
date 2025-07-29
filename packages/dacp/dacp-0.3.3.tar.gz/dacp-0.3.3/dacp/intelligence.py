"""
Intelligence provider integration for DACP.

This module provides a unified interface for calling different LLM providers
(OpenAI, Anthropic, Azure, Local) with comprehensive error handling and logging.
"""

import os
import logging
import time
from typing import Dict, Any, Union

logger = logging.getLogger("dacp.intelligence")


def invoke_intelligence(
    prompt: str, config: Dict[str, Any]
) -> Union[str, Dict[str, Any]]:
    """
    Invoke an intelligence provider with the given prompt and configuration.

    Args:
        prompt: The input prompt/message to send to the intelligence provider
        config: Configuration dictionary containing provider settings

    Returns:
        Response from the intelligence provider (string or dict)

    Raises:
        ValueError: If configuration is invalid
        Exception: If the intelligence call fails
    """
    start_time = time.time()

    engine = config.get("engine", "").lower()
    model = config.get("model", "unknown")

    logger.info(f"🧠 Invoking intelligence: engine='{engine}', model='{model}'")
    logger.debug(f"📋 Prompt: {prompt[:100]}...")

    try:
        # Validate configuration
        _validate_config(config)

        # Route to appropriate provider
        if engine in ["openai", "gpt"]:
            result = _invoke_openai(prompt, config)
        elif engine in ["anthropic", "claude"]:
            result = _invoke_anthropic(prompt, config)
        elif engine in ["azure", "azure_openai"]:
            result = _invoke_azure_openai(prompt, config)
        elif engine in ["local", "ollama"]:
            result = _invoke_local(prompt, config)
        else:
            available_engines = ["openai", "anthropic", "azure", "local"]
            raise ValueError(
                f"Unsupported engine: {engine}. "
                f"Available engines: {available_engines}"
            )

        duration = time.time() - start_time
        logger.info(f"✅ Intelligence call completed in {duration:.3f}s")
        logger.debug(f"📤 Response: {str(result)[:200]}...")

        return result

    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"❌ Intelligence call failed after {duration:.3f}s: "
            f"{type(e).__name__}: {e}"
        )
        raise


def _validate_config(config: Dict[str, Any]) -> None:
    """Validate intelligence configuration."""
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a dictionary")

    engine = config.get("engine")
    if not engine:
        raise ValueError("Engine must be specified in configuration")


def _invoke_openai(prompt: str, config: Dict[str, Any]) -> str:
    """Invoke OpenAI GPT models."""
    try:
        import openai
    except ImportError:
        raise ImportError("OpenAI package not installed. Run: pip install openai")

    # Get API key
    api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("❌ OpenAI API key not found")
        raise ValueError(
            "OpenAI API key not found in config or OPENAI_API_KEY "
            "environment variable"
        )

    # Configure client
    base_url = config.get("base_url")
    if base_url:
        client = openai.OpenAI(api_key=api_key, base_url=base_url)
    else:
        client = openai.OpenAI(api_key=api_key)

    # Prepare request
    model = config.get("model", "gpt-3.5-turbo")
    temperature = config.get("temperature", 0.7)
    max_tokens = config.get("max_tokens", 1000)

    logger.debug(
        f"🔧 OpenAI config: model={model}, temp={temperature}, "
        f"max_tokens={max_tokens}"
    )

    # Make API call
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    content = response.choices[0].message.content
    if content is None:
        raise ValueError("OpenAI returned empty response")

    return str(content)


def _invoke_anthropic(prompt: str, config: Dict[str, Any]) -> str:
    """Invoke Anthropic Claude models."""
    try:
        import anthropic
    except ImportError:
        raise ImportError("Anthropic package not installed. Run: pip install anthropic")

    # Get API key
    api_key = config.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("❌ Anthropic API key not found")
        raise ValueError(
            "Anthropic API key not found in config or ANTHROPIC_API_KEY "
            "environment variable"
        )

    # Configure client
    base_url = config.get("base_url")
    if base_url:
        client = anthropic.Anthropic(api_key=api_key, base_url=base_url)
    else:
        client = anthropic.Anthropic(api_key=api_key)

    # Prepare request
    model = config.get("model", "claude-3-haiku-20240307")
    temperature = config.get("temperature", 0.7)
    max_tokens = config.get("max_tokens", 1000)

    logger.debug(
        f"🔧 Anthropic config: model={model}, temp={temperature}, "
        f"max_tokens={max_tokens}"
    )

    # Make API call
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )

    # Get text from first content block
    content_block = response.content[0]
    if hasattr(content_block, "text"):
        return str(content_block.text)
    else:
        raise ValueError("Anthropic returned unexpected response format")


def _invoke_azure_openai(prompt: str, config: Dict[str, Any]) -> str:
    """Invoke Azure OpenAI models."""
    try:
        import openai
    except ImportError:
        raise ImportError("OpenAI package not installed. Run: pip install openai")

    # Get required Azure configuration
    api_key = config.get("api_key") or os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = config.get("endpoint") or os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version = config.get("api_version", "2023-12-01-preview")

    if not api_key:
        logger.error("❌ Azure OpenAI API key not found")
        raise ValueError(
            "Azure OpenAI API key not found in config or "
            "AZURE_OPENAI_API_KEY environment variable"
        )

    if not endpoint:
        logger.error("❌ Azure OpenAI endpoint not found")
        raise ValueError(
            "Azure OpenAI endpoint not found in config or "
            "AZURE_OPENAI_ENDPOINT environment variable"
        )

    # Configure Azure client
    client = openai.AzureOpenAI(
        api_key=api_key, azure_endpoint=endpoint, api_version=api_version
    )

    # Prepare request
    model = config.get("model", config.get("deployment_name", "gpt-35-turbo"))
    temperature = config.get("temperature", 0.7)
    max_tokens = config.get("max_tokens", 1000)

    logger.debug(
        f"🔧 Azure OpenAI config: model={model}, temp={temperature}, "
        f"max_tokens={max_tokens}"
    )

    # Make API call
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    content = response.choices[0].message.content
    if content is None:
        raise ValueError("Azure OpenAI returned empty response")

    return str(content)


def _invoke_local(prompt: str, config: Dict[str, Any]) -> str:
    """Invoke local LLM (e.g., Ollama)."""
    import requests

    base_url = config.get("base_url", "http://localhost:11434")
    model = config.get("model", "llama2")
    endpoint = config.get("endpoint", "/api/generate")

    url = f"{base_url.rstrip('/')}{endpoint}"

    logger.debug(f"🔧 Local config: url={url}, model={model}")

    # Prepare request payload
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": config.get("temperature", 0.7),
            "num_predict": config.get("max_tokens", 1000),
        },
    }

    try:
        response = requests.post(url, json=payload, timeout=config.get("timeout", 30))
        response.raise_for_status()

        result = response.json()

        # Handle different response formats and ensure string return
        if "response" in result:
            response_text = result["response"]
            return str(response_text) if response_text is not None else ""
        elif "content" in result:
            content_text = result["content"]
            return str(content_text) if content_text is not None else ""
        elif "text" in result:
            text_content = result["text"]
            return str(text_content) if text_content is not None else ""
        else:
            logger.warning("Unexpected response format from local LLM")
            return str(result)

    except requests.RequestException as e:
        logger.error(f"❌ Local LLM request failed: {e}")
        raise Exception(f"Local LLM request failed: {e}")
    except Exception as e:
        logger.error(f"❌ Local LLM call failed: {e}")
        raise


def _mask_sensitive_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Mask sensitive information in config for logging."""
    masked = config.copy()
    sensitive_keys = ["api_key", "password", "token", "secret"]

    for key in masked:
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            value = masked[key]
            if isinstance(value, str) and len(value) > 8:
                masked[key] = f"{value[:4]}...{value[-4:]}"
            else:
                masked[key] = "***"

    return masked
