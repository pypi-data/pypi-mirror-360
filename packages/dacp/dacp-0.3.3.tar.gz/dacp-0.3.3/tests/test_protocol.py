import pytest
import json
from dacp.protocol import (
    parse_agent_response,
    is_tool_request,
    get_tool_request,
    wrap_tool_result,
    is_final_response,
    get_final_response,
)


def test_parse_agent_response_dict():
    """Test parsing agent response that's already a dict."""
    response = {"tool_request": {"name": "test_tool", "args": {"param": "value"}}}
    result = parse_agent_response(response)
    assert result == response


def test_parse_agent_response_string():
    """Test parsing agent response that's a JSON string."""
    response_dict = {"tool_request": {"name": "test_tool", "args": {"param": "value"}}}
    response_string = json.dumps(response_dict)
    result = parse_agent_response(response_string)
    assert result == response_dict


def test_parse_agent_response_invalid_json():
    """Test parsing invalid JSON string."""
    with pytest.raises(ValueError, match="Malformed agent response"):
        parse_agent_response("invalid json")


def test_is_tool_request_true():
    """Test is_tool_request returns True for tool requests."""
    msg = {"tool_request": {"name": "test_tool", "args": {}}}
    assert is_tool_request(msg) is True


def test_is_tool_request_false():
    """Test is_tool_request returns False for non-tool requests."""
    msg = {"final_response": {"content": "Hello"}}
    assert is_tool_request(msg) is False


def test_get_tool_request():
    """Test getting tool request details."""
    msg = {"tool_request": {"name": "test_tool", "args": {"param": "value"}}}
    name, args = get_tool_request(msg)
    assert name == "test_tool"
    assert args == {"param": "value"}


def test_get_tool_request_no_args():
    """Test getting tool request with no args."""
    msg = {"tool_request": {"name": "test_tool"}}
    name, args = get_tool_request(msg)
    assert name == "test_tool"
    assert args == {}


def test_wrap_tool_result():
    """Test wrapping tool result."""
    result = {"output": "success"}
    wrapped = wrap_tool_result("test_tool", result)
    expected = {"tool_result": {"name": "test_tool", "result": result}}
    assert wrapped == expected


def test_is_final_response_true():
    """Test is_final_response returns True for final responses."""
    msg = {"final_response": {"content": "Hello"}}
    assert is_final_response(msg) is True


def test_is_final_response_false():
    """Test is_final_response returns False for non-final responses."""
    msg = {"tool_request": {"name": "test_tool", "args": {}}}
    assert is_final_response(msg) is False


def test_get_final_response():
    """Test getting final response content."""
    final_content = {"content": "Hello, world!"}
    msg = {"final_response": final_content}
    result = get_final_response(msg)
    assert result == final_content


def test_complex_agent_response():
    """Test parsing a complex agent response."""
    complex_response = {
        "tool_request": {
            "name": "weather_api",
            "args": {"location": "New York", "units": "celsius"},
        },
        "metadata": {"timestamp": "2024-01-01T00:00:00Z", "session_id": "abc123"},
    }

    # Test parsing
    parsed = parse_agent_response(complex_response)
    assert parsed == complex_response

    # Test tool request detection
    assert is_tool_request(parsed) is True

    # Test getting tool request
    name, args = get_tool_request(parsed)
    assert name == "weather_api"
    assert args == {"location": "New York", "units": "celsius"}

    # Test wrapping result
    tool_result = {"temperature": 20, "condition": "sunny"}
    wrapped = wrap_tool_result(name, tool_result)
    assert wrapped["tool_result"]["name"] == "weather_api"
    assert wrapped["tool_result"]["result"] == tool_result
