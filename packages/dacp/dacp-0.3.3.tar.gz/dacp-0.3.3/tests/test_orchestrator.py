"""
Tests for the orchestrator module.
"""

import unittest

from dacp.orchestrator import Orchestrator, Agent


class TestAgent(Agent):
    """Test agent implementation."""

    def handle_message(self, message):
        if message.get("task") == "greet":
            return {"response": f"Hello {message.get('name', 'World')}!"}
        elif message.get("task") == "error":
            raise Exception("Test error")
        elif message.get("task") == "tool_request":
            return {
                "tool_request": {
                    "name": "file_writer",
                    "args": {"path": "./test.txt", "content": "test"},
                }
            }
        else:
            return {"error": "Unknown task"}


class TestOrchestrator(unittest.TestCase):
    """Test the Orchestrator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.orchestrator = Orchestrator()
        self.agent = TestAgent()

    def test_register_agent(self):
        """Test agent registration."""
        self.orchestrator.register_agent("test_agent", self.agent)
        self.assertIn("test_agent", self.orchestrator.agents)
        self.assertEqual(self.orchestrator.agents["test_agent"], self.agent)

    def test_register_invalid_agent(self):
        """Test registering invalid agent raises error."""
        with self.assertRaises(ValueError):
            self.orchestrator.register_agent("invalid", "not_an_agent")

    def test_unregister_agent(self):
        """Test agent unregistration."""
        self.orchestrator.register_agent("test_agent", self.agent)
        result = self.orchestrator.unregister_agent("test_agent")
        self.assertTrue(result)
        self.assertNotIn("test_agent", self.orchestrator.agents)

    def test_unregister_nonexistent_agent(self):
        """Test unregistering nonexistent agent returns False."""
        result = self.orchestrator.unregister_agent("nonexistent")
        self.assertFalse(result)

    def test_send_message_success(self):
        """Test successful message sending."""
        self.orchestrator.register_agent("test_agent", self.agent)

        response = self.orchestrator.send_message(
            "test_agent", {"task": "greet", "name": "Alice"}
        )

        self.assertEqual(response, {"response": "Hello Alice!"})

    def test_send_message_agent_not_found(self):
        """Test sending message to nonexistent agent."""
        response = self.orchestrator.send_message("nonexistent", {"task": "greet"})

        self.assertEqual(response, {"error": "Agent 'nonexistent' not found"})

    def test_send_message_agent_error(self):
        """Test agent error handling."""
        self.orchestrator.register_agent("test_agent", self.agent)

        response = self.orchestrator.send_message("test_agent", {"task": "error"})

        self.assertIn("error", response)

    def test_list_agents(self):
        """Test listing agents."""
        self.orchestrator.register_agent("agent1", self.agent)
        self.orchestrator.register_agent("agent2", TestAgent())

        agents = self.orchestrator.list_agents()
        self.assertEqual(set(agents), {"agent1", "agent2"})

    def test_broadcast_message(self):
        """Test broadcasting message to all agents."""
        agent1 = TestAgent()
        agent2 = TestAgent()

        self.orchestrator.register_agent("agent1", agent1)
        self.orchestrator.register_agent("agent2", agent2)

        responses = self.orchestrator.broadcast_message(
            {"task": "greet", "name": "World"}
        )

        self.assertEqual(len(responses), 2)
        self.assertEqual(responses["agent1"], {"response": "Hello World!"})
        self.assertEqual(responses["agent2"], {"response": "Hello World!"})


if __name__ == "__main__":
    unittest.main()
