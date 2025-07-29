import pytest
from unittest.mock import patch
import os
from dacp.llm import call_llm


@patch("dacp.llm.invoke_intelligence")
def test_call_llm_success(mock_invoke_intelligence):
    """Test successful LLM call."""
    mock_invoke_intelligence.return_value = "Hello, world!"

    result = call_llm("Test prompt")

    assert result == "Hello, world!"

    # Verify invoke_intelligence was called with correct config
    mock_invoke_intelligence.assert_called_once()
    call_args = mock_invoke_intelligence.call_args
    assert call_args[0][0] == "Test prompt"  # First arg is prompt
    config = call_args[0][1]  # Second arg is config
    assert config["engine"] == "openai"
    assert config["model"] == "gpt-4"


@patch("dacp.llm.invoke_intelligence")
def test_call_llm_custom_model(mock_invoke_intelligence):
    """Test LLM call with custom model."""
    mock_invoke_intelligence.return_value = "Custom model response"

    result = call_llm("Test prompt", model="gpt-3.5-turbo")

    assert result == "Custom model response"

    # Verify custom model was used
    call_args = mock_invoke_intelligence.call_args
    config = call_args[0][1]
    assert config["model"] == "gpt-3.5-turbo"


@patch("dacp.llm.invoke_intelligence")
def test_call_llm_api_error(mock_invoke_intelligence):
    """Test LLM call with API error."""
    mock_invoke_intelligence.side_effect = Exception("API Error")

    with pytest.raises(Exception):
        call_llm("Test prompt")


@patch("dacp.llm.invoke_intelligence")
def test_call_llm_error_response(mock_invoke_intelligence):
    """Test LLM call that returns error dict."""
    mock_invoke_intelligence.return_value = {"error": "API key not found"}

    result = call_llm("Test prompt")

    assert result == "API key not found"


@patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-123"})
@patch("dacp.llm.invoke_intelligence")
def test_call_llm_environment_variable(mock_invoke_intelligence):
    """Test that the function uses the OPENAI_API_KEY environment variable."""
    mock_invoke_intelligence.return_value = "Test response"

    call_llm("Test prompt")

    # Verify the API key was passed in config
    call_args = mock_invoke_intelligence.call_args
    config = call_args[0][1]
    assert config["api_key"] == "test-api-key-123"


@patch("dacp.llm.invoke_intelligence")
def test_call_llm_default_parameters(mock_invoke_intelligence):
    """Test that default parameters are used correctly."""
    mock_invoke_intelligence.return_value = "Default response"

    call_llm("Test prompt")

    # Verify default parameters
    call_args = mock_invoke_intelligence.call_args
    config = call_args[0][1]
    assert config["model"] == "gpt-4"
    assert config["temperature"] == 0.7
    assert config["max_tokens"] == 150
    assert config["engine"] == "openai"
