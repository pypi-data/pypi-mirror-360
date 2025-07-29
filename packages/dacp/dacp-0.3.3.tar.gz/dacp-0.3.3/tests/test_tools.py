import pytest
import tempfile
import os
from dacp.tools import register_tool, execute_tool, TOOL_REGISTRY, file_writer


def test_register_tool():
    """Test registering a tool."""

    def test_tool(args: dict) -> dict:
        param1 = args.get("param1", "")
        param2 = args.get("param2", 0)
        return {"result": f"Processed {param1} with {param2}"}

    register_tool("test_tool", test_tool)
    assert "test_tool" in TOOL_REGISTRY
    assert TOOL_REGISTRY["test_tool"] == test_tool


def test_execute_tool():
    """Test executing a registered tool."""

    def test_tool(args: dict) -> dict:
        param1 = args.get("param1", "")
        param2 = args.get("param2", 0)
        return {"result": f"Processed {param1} with {param2}"}

    register_tool("test_tool", test_tool)
    result = execute_tool("test_tool", {"param1": "hello", "param2": 42})
    assert result["result"] == "Processed hello with 42"


def test_execute_nonexistent_tool():
    """Test executing a tool that doesn't exist."""
    with pytest.raises(ValueError):
        execute_tool("nonexistent_tool", {})


def test_tool_with_no_args():
    """Test executing a tool with no arguments."""

    def no_args_tool(args: dict) -> dict:
        return {"result": "success"}

    register_tool("no_args_tool", no_args_tool)
    result = execute_tool("no_args_tool", {})
    assert result["result"] == "success"


def test_tool_with_optional_args():
    """Test executing a tool with optional arguments."""

    def optional_args_tool(args: dict) -> dict:
        required = args.get("required", "")
        optional = args.get("optional", "default")
        return {"result": f"{required}:{optional}"}

    register_tool("optional_args_tool", optional_args_tool)

    # Test with both args
    result = execute_tool(
        "optional_args_tool", {"required": "test", "optional": "custom"}
    )
    assert result["result"] == "test:custom"

    # Test with only required arg
    result = execute_tool("optional_args_tool", {"required": "test"})
    assert result["result"] == "test:default"


def test_file_writer_registered():
    """Test that file_writer is automatically registered."""
    assert "file_writer" in TOOL_REGISTRY
    assert TOOL_REGISTRY["file_writer"] == file_writer


def test_clear_tool_registry():
    """Test that we can clear and re-register tools."""

    def test_tool(args: dict) -> dict:
        return {"result": "test"}

    register_tool("test_tool", test_tool)
    assert "test_tool" in TOOL_REGISTRY

    # Clear registry
    TOOL_REGISTRY.clear()
    assert "test_tool" not in TOOL_REGISTRY

    # Re-register file_writer since it was cleared
    register_tool("file_writer", file_writer)


def test_file_writer_creates_parent_directories():
    """Test that file_writer creates parent directories automatically."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test writing to a nested directory that doesn't exist
        test_path = os.path.join(temp_dir, "nested", "subdir", "test.txt")
        content = "Hello, World!"

        result = file_writer({"path": test_path, "content": content})

        assert result["success"] is True
        assert result["path"] == test_path
        assert "Successfully wrote" in result["message"]

        # Verify the file was created with correct content
        assert os.path.exists(test_path)
        with open(test_path, "r", encoding="utf-8") as f:
            assert f.read() == content


def test_file_writer_existing_directory():
    """Test file_writer with existing directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_path = os.path.join(temp_dir, "test.txt")
        content = "Test content"

        result = file_writer({"path": test_path, "content": content})

        assert result["success"] is True
        assert os.path.exists(test_path)
        with open(test_path, "r", encoding="utf-8") as f:
            assert f.read() == content


def test_file_writer_permission_error():
    """Test file_writer handles permission errors gracefully."""
    # Try to write to a system directory that should be protected
    test_path = "/root/test.txt"
    content = "This should fail"

    result = file_writer({"path": test_path, "content": content})

    assert result["success"] is False
    assert "error" in result
    assert result["path"] == test_path


def test_file_writer_unicode_content():
    """Test file_writer handles unicode content properly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_path = os.path.join(temp_dir, "unicode_test.txt")
        content = "Hello, 世界! 🌍"

        result = file_writer({"path": test_path, "content": content})

        assert result["success"] is True
        with open(test_path, "r", encoding="utf-8") as f:
            assert f.read() == content
