import json
from typing import Dict, Any, Union, Tuple, cast


def parse_agent_response(response: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parse the agent/LLM response (as string or dict) and return a dict.
    """
    if isinstance(response, dict):
        return response
    try:
        return cast(Dict[str, Any], json.loads(response))
    except Exception as e:
        raise ValueError(f"Malformed agent response: {e}")


def is_tool_request(msg: Dict[str, Any]) -> bool:
    return "tool_request" in msg


def get_tool_request(msg: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    req = msg["tool_request"]
    return req["name"], req.get("args", {})


def wrap_tool_result(name: str, result: Dict[str, Any]) -> Dict[str, Any]:
    return {"tool_result": {"name": name, "result": result}}


def is_final_response(msg: Dict[str, Any]) -> bool:
    return "final_response" in msg


def get_final_response(msg: Dict[str, Any]) -> Dict[str, Any]:
    return cast(Dict[str, Any], msg["final_response"])
