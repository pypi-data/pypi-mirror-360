"""
DACP Tools - Built-in tool implementations.

This module provides the core tool functionality including tool registry,
execution, and built-in tools like file_writer.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Callable

logger = logging.getLogger("dacp.tools")

# Global tool registry
TOOL_REGISTRY: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}


def register_tool(name: str, func: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
    """
    Register a tool function.

    Args:
        name: Name of the tool
        func: Function that takes args dict and returns result dict
    """
    TOOL_REGISTRY[name] = func
    logger.info(f"🔧 Tool '{name}' registered")


def execute_tool(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool by name with given arguments.

    Args:
        name: Name of the tool to execute
        args: Arguments to pass to the tool

    Returns:
        Tool execution result

    Raises:
        ValueError: If tool is not found
    """
    if name not in TOOL_REGISTRY:
        available_tools = list(TOOL_REGISTRY.keys())
        logger.error(
            f"❌ Tool '{name}' not found. " f"Available tools: {available_tools}"
        )
        raise ValueError(f"Tool '{name}' not found. Available tools: {available_tools}")

    logger.debug(f"🛠️  Executing tool '{name}' with args: {args}")

    try:
        result = TOOL_REGISTRY[name](args)
        logger.debug(f"✅ Tool '{name}' completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Tool '{name}' failed: {type(e).__name__}: {e}")
        raise


def file_writer(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Write content to a file, creating directories as needed.

    Args:
        args: Dictionary containing 'path' and 'content'

    Returns:
        Success status and file information
    """
    path = args.get("path")
    content = args.get("content", "")

    if not path:
        raise ValueError("file_writer requires 'path' argument")

    try:
        # Create parent directories if they don't exist
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write content to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"✅ File written successfully: {path}")

        return {
            "success": True,
            "path": str(file_path),
            "message": f"Successfully wrote {len(content)} characters to {path}",
        }

    except Exception as e:
        logger.error(f"❌ Failed to write file {path}: {e}")
        return {
            "success": False,
            "path": path,
            "error": str(e),
        }


# Register built-in tools
register_tool("file_writer", file_writer)
