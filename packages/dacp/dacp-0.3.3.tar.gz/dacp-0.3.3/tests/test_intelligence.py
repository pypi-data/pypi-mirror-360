"""
Tests for the intelligence module.
"""

import unittest
from unittest.mock import patch

from dacp.intelligence import invoke_intelligence


class TestInvokeIntelligence(unittest.TestCase):
    """Test the main invoke_intelligence function."""

    def test_missing_engine_raises_error(self):
        """Test that missing engine raises ValueError."""
        config = {"model": "gpt-4"}
        with self.assertRaises(ValueError, msg="Engine must be specified"):
            invoke_intelligence("test prompt", config)

    def test_unsupported_engine_raises_error(self):
        """Test that unsupported engine raises ValueError."""
        config = {"engine": "unsupported_engine"}
        with self.assertRaises(ValueError, msg="Unsupported engine"):
            invoke_intelligence("test prompt", config)

    @patch("dacp.intelligence._invoke_openai")
    def test_openai_engine_calls_correct_function(self, mock_openai):
        """Test that OpenAI engine calls the correct function."""
        mock_openai.return_value = "OpenAI response"
        config = {"engine": "openai", "model": "gpt-4"}

        result = invoke_intelligence("test prompt", config)

        self.assertEqual(result, "OpenAI response")
        mock_openai.assert_called_once_with("test prompt", config)

    @patch("dacp.intelligence._invoke_anthropic")
    def test_anthropic_engine_calls_correct_function(self, mock_anthropic):
        """Test that Anthropic engine calls the correct function."""
        mock_anthropic.return_value = "Anthropic response"
        config = {"engine": "anthropic", "model": "claude-3-haiku-20240307"}

        result = invoke_intelligence("test prompt", config)

        self.assertEqual(result, "Anthropic response")
        mock_anthropic.assert_called_once_with("test prompt", config)

    @patch("dacp.intelligence._invoke_azure_openai")
    def test_azure_engine_calls_correct_function(self, mock_azure):
        """Test that Azure engine calls the correct function."""
        mock_azure.return_value = "Azure response"
        config = {"engine": "azure", "model": "gpt-4"}

        result = invoke_intelligence("test prompt", config)

        self.assertEqual(result, "Azure response")
        mock_azure.assert_called_once_with("test prompt", config)

    @patch("dacp.intelligence._invoke_local")
    def test_local_engine_calls_correct_function(self, mock_local):
        """Test that local engine calls the correct function."""
        mock_local.return_value = "Local response"
        config = {"engine": "local", "model": "llama2"}

        result = invoke_intelligence("test prompt", config)

        self.assertEqual(result, "Local response")
        mock_local.assert_called_once_with("test prompt", config)


if __name__ == "__main__":
    unittest.main()
