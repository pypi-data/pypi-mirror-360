"""
DACP Orchestrator - Agent management and message routing.

This module provides the core orchestrator functionality for managing agents
and routing messages between them.
"""

import logging
import time
from typing import Dict, Any, List, Optional

from .tools import execute_tool

logger = logging.getLogger("dacp.orchestrator")


class Agent:
    """
    Base agent class that all DACP agents should inherit from.

    This provides the standard interface for agent communication.
    """

    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming messages.

        Args:
            message: Message dictionary containing task and parameters

        Returns:
            Response dictionary with either 'response', 'tool_request', or 'error'
        """
        raise NotImplementedError("Agents must implement handle_message method")


class Orchestrator:
    """
    Central orchestrator for managing agents and routing messages.

    The orchestrator handles agent registration, message routing, tool execution,
    and conversation history management.
    """

    def __init__(self, session_id: Optional[str] = None):
        """Initialize orchestrator with optional session ID."""
        self.agents: Dict[str, Agent] = {}
        self.session_id = session_id or f"session_{int(time.time())}"
        self.conversation_history: List[Dict[str, Any]] = []

        logger.info(f"🎭 Orchestrator initialized with session ID: {self.session_id}")

    def register_agent(self, name: str, agent: Agent) -> None:
        """
        Register an agent with the orchestrator.

        Args:
            name: Unique name for the agent
            agent: Agent instance implementing the Agent interface
        """
        if not isinstance(agent, Agent):
            raise ValueError("Agent must inherit from dacp.Agent base class")

        self.agents[name] = agent
        logger.info(
            f"✅ Agent '{name}' registered successfully "
            f"(type: {type(agent).__name__})"
        )
        logger.debug(f"📊 Total registered agents: {len(self.agents)}")

    def unregister_agent(self, name: str) -> bool:
        """
        Unregister an agent from the orchestrator.

        Args:
            name: Name of the agent to unregister

        Returns:
            True if agent was unregistered, False if not found
        """
        if name in self.agents:
            del self.agents[name]
            logger.info(f"🗑️  Agent '{name}' unregistered successfully")
            logger.debug(f"📊 Remaining agents: {len(self.agents)}")
            return True
        else:
            logger.warning(f"⚠️  Agent '{name}' not found for unregistration")
            return False

    def list_agents(self) -> List[str]:
        """Get list of registered agent names."""
        return list(self.agents.keys())

    def send_message(self, agent_name: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to a specific agent.

        Args:
            agent_name: Name of the target agent
            message: Message dictionary to send

        Returns:
            Response from the agent after processing
        """
        start_time = time.time()

        logger.info(f"📨 Sending message to agent '{agent_name}'")
        logger.debug(f"📋 Message content: {message}")

        if agent_name not in self.agents:
            error_msg = f"Agent '{agent_name}' not found"
            logger.error(f"❌ {error_msg}")
            return {"error": error_msg}

        agent = self.agents[agent_name]

        try:
            logger.debug(f"🔄 Calling handle_message on agent '{agent_name}'")

            # Call the agent's message handler
            response = agent.handle_message(message)

            # Handle Pydantic models by converting to dict
            if hasattr(response, 'model_dump'):
                logger.debug(f"📊 Converting Pydantic model to dict: {type(response).__name__}")
                response = response.model_dump()
            elif not isinstance(response, dict):
                logger.debug(f"📊 Converting response to dict: {type(response)}")
                if hasattr(response, '__dict__'):
                    response = response.__dict__
                else:
                    response = {"result": str(response)}

            duration = time.time() - start_time
            logger.info(f"✅ Agent '{agent_name}' responded in {duration:.3f}s")
            logger.debug(f"📤 Agent response: {response}")

            # Check if agent requested tool execution
            if isinstance(response, dict) and "tool_request" in response:
                logger.info(f"🔧 Agent '{agent_name}' requested tool execution")
                response = self._handle_tool_request(
                    agent_name, response["tool_request"]
                )

            # Log the conversation
            self._log_conversation(agent_name, message, response, duration)

            return response

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Error in agent '{agent_name}': {type(e).__name__}: {e}"
            logger.error(f"❌ {error_msg}")
            logger.debug("💥 Exception details", exc_info=True)

            error_response = {"error": error_msg}
            self._log_conversation(agent_name, message, error_response, duration)

            return error_response

    def broadcast_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to all registered agents.

        Args:
            message: Message dictionary to broadcast

        Returns:
            Dictionary mapping agent names to their responses
        """
        logger.info(f"📢 Broadcasting message to {len(self.agents)} agents")
        logger.debug(f"📋 Broadcast message: {message}")

        responses = {}
        start_time = time.time()

        for agent_name in self.agents:
            logger.debug(f"📨 Broadcasting to agent '{agent_name}'")
            responses[agent_name] = self.send_message(agent_name, message)

        duration = time.time() - start_time
        logger.info(
            f"✅ Broadcast completed in {duration:.3f}s "
            f"({len(responses)} responses)"
        )

        return responses

    def _handle_tool_request(
        self, agent_name: str, tool_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle tool execution request from an agent.

        Args:
            agent_name: Name of the requesting agent
            tool_request: Tool request dictionary with 'name' and 'args'

        Returns:
            Tool execution result
        """
        tool_name = tool_request.get("name")
        tool_args = tool_request.get("args", {})

        if not tool_name:
            return {"error": "Tool name is required"}

        logger.info(f"🛠️  Executing tool: '{tool_name}' with args: {tool_args}")

        start_time = time.time()

        try:
            result = execute_tool(tool_name, tool_args)
            duration = time.time() - start_time

            logger.info(
                f"✅ Tool '{tool_name}' executed successfully in {duration:.3f}s"
            )
            logger.debug(f"🔧 Tool result: {result}")

            return {"tool_result": {"name": tool_name, "result": result}}

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Tool '{tool_name}' failed: {type(e).__name__}: {e}"
            logger.error(f"❌ {error_msg}")

            return {"error": error_msg}

    def _log_conversation(
        self,
        agent_name: str,
        message: Dict[str, Any],
        response: Dict[str, Any],
        duration: float,
    ) -> None:
        """Log conversation entry to history."""
        logger.debug("💾 Logging conversation entry")

        entry = {
            "timestamp": time.time(),
            "session_id": self.session_id,
            "agent": agent_name,
            "agent_name": agent_name,
            "message": message,
            "response": response,
            "duration": duration,
        }

        self.conversation_history.append(entry)

        # Keep history manageable (last 1000 entries)
        if len(self.conversation_history) > 1000:
            self.conversation_history = self.conversation_history[-1000:]
            logger.debug("🗂️  Conversation history trimmed to 1000 entries")

    def get_conversation_history(
        self, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history.

        Args:
            limit: Maximum number of entries to return (None for all)

        Returns:
            List of conversation entries
        """
        if limit is None:
            return self.conversation_history.copy()
        else:
            return self.conversation_history[-limit:].copy()

    def clear_conversation_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()
        logger.info("🗑️  Conversation history cleared")

    def get_session_metadata(self) -> Dict[str, Any]:
        """Get session metadata and statistics."""
        return {
            "session_id": self.session_id,
            "registered_agents": len(self.agents),
            "agent_names": list(self.agents.keys()),
            "conversation_entries": len(self.conversation_history),
            "start_time": (
                self.conversation_history[0]["timestamp"]
                if self.conversation_history
                else None
            ),
            "last_activity": (
                self.conversation_history[-1]["timestamp"]
                if self.conversation_history
                else None
            ),
        }
