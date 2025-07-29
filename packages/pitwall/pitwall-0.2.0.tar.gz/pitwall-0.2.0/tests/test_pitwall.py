"""
Tests for Pitwall agent - The agentic AI companion to MultiViewer.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import os

from pitwall.pitwall import create_pitwall_agent, quick_analysis


class TestPitwallAgent:
    """Test the Pitwall agent functionality."""

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"})
    @patch("pitwall.pitwall.MCPServerStdio")
    @patch("pitwall.pitwall.OpenAIModel")
    @patch("pitwall.pitwall.Agent")
    async def test_create_pitwall_agent_success(self, mock_agent, mock_model, mock_mcp):
        """Test successful agent creation with MCP server."""
        # Mock MCP server
        mock_mcp_instance = AsyncMock()
        mock_mcp.return_value.__aenter__ = AsyncMock(return_value=mock_mcp_instance)
        mock_mcp.return_value.__aexit__ = AsyncMock(return_value=None)

        # Mock model
        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        # Mock agent
        mock_agent_instance = MagicMock()
        mock_agent.return_value = mock_agent_instance

        # Mock tools for get_available_tools
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.description = "Test tool description"
        mock_tools = [mock_tool]
        mock_mcp_instance.list_tools = AsyncMock(return_value=mock_tools)

        async with create_pitwall_agent("test-model") as agent:
            assert agent is not None
            assert agent.model_name == "test-model"

            # Test get_available_tools
            tools = await agent.get_available_tools()
            assert len(tools) == 1
            assert tools[0]["name"] == "test_tool"
            assert tools[0]["description"] == "Test tool description"

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"})
    @patch("pitwall.pitwall.MCPServerStdio")
    @patch("pitwall.pitwall.OpenAIModel")
    @patch("pitwall.pitwall.Agent")
    async def test_create_pitwall_agent_mcp_failure(
        self, mock_agent, mock_model, mock_mcp
    ):
        """Test agent creation when MCP server fails (fallback mode)."""
        # Mock MCP server to raise exception
        mock_mcp.return_value.__aenter__ = AsyncMock(
            side_effect=Exception("MCP connection failed")
        )

        # Mock model for fallback
        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        # Mock agent for fallback
        mock_agent_instance = MagicMock()
        mock_agent.return_value = mock_agent_instance

        async with create_pitwall_agent("test-model") as agent:
            assert agent is not None
            assert agent.model_name == "test-model"

            # Test get_available_tools in fallback mode
            tools = await agent.get_available_tools()
            assert len(tools) == 1
            assert tools[0]["name"] == "general-analysis"

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"})
    @patch("pitwall.pitwall.MCPServerStdio")
    @patch("pitwall.pitwall.OpenAIModel")
    @patch("pitwall.pitwall.Agent")
    async def test_agent_execute_task(self, mock_agent, mock_model, mock_mcp):
        """Test agent task execution."""
        # Setup mocks
        mock_mcp_instance = AsyncMock()
        mock_mcp.return_value.__aenter__ = AsyncMock(return_value=mock_mcp_instance)
        mock_mcp.return_value.__aexit__ = AsyncMock(return_value=None)

        mock_model.return_value = MagicMock()

        # Mock agent run result
        mock_result = MagicMock()
        mock_result.data = "Test result"
        mock_agent_instance = MagicMock()
        mock_agent_instance.run = AsyncMock(return_value=mock_result)
        mock_agent.return_value = mock_agent_instance

        async with create_pitwall_agent("test-model") as agent:
            result = await agent.execute_task("test query")
            assert result == "Test result"
            mock_agent_instance.run.assert_called_once_with(
                "test query", message_history=[]
            )

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"})
    @patch("pitwall.pitwall.MCPServerStdio")
    @patch("pitwall.pitwall.OpenAIModel")
    @patch("pitwall.pitwall.Agent")
    async def test_agent_chat_turn(self, mock_agent, mock_model, mock_mcp):
        """Test agent chat turn."""
        # Setup mocks
        mock_mcp_instance = AsyncMock()
        mock_mcp.return_value.__aenter__ = AsyncMock(return_value=mock_mcp_instance)
        mock_mcp.return_value.__aexit__ = AsyncMock(return_value=None)

        mock_model.return_value = MagicMock()

        # Mock agent run result
        mock_result = MagicMock()
        mock_result.data = "Chat response"
        mock_agent_instance = MagicMock()
        mock_agent_instance.run = AsyncMock(return_value=mock_result)
        mock_agent.return_value = mock_agent_instance

        async with create_pitwall_agent("test-model") as agent:
            response = await agent.chat_turn("Hello")
            assert response == "Chat response"
            mock_agent_instance.run.assert_called_once_with("Hello", message_history=[])

    @pytest.mark.asyncio
    @patch("pitwall.pitwall.create_pitwall_agent")
    async def test_quick_analysis(self, mock_create_agent):
        """Test quick analysis function."""
        # Mock agent
        mock_agent = AsyncMock()
        mock_agent.execute_task = AsyncMock(return_value="Quick analysis result")

        # Mock context manager
        mock_create_agent.return_value.__aenter__ = AsyncMock(return_value=mock_agent)
        mock_create_agent.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await quick_analysis("test query", "test-model")
        assert result == "Quick analysis result"
        mock_agent.execute_task.assert_called_once_with("test query", max_turns=1)

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"})
    @patch("pitwall.pitwall.OpenRouterProvider")
    @patch("pitwall.pitwall.MCPServerStdio")
    @patch("pitwall.pitwall.OpenAIModel")
    @patch("pitwall.pitwall.Agent")
    async def test_agent_with_api_key(
        self, mock_agent, mock_model, mock_mcp, mock_provider
    ):
        """Test agent creation with API key from environment."""
        mock_mcp_instance = AsyncMock()
        mock_mcp.return_value.__aenter__ = AsyncMock(return_value=mock_mcp_instance)
        mock_mcp.return_value.__aexit__ = AsyncMock(return_value=None)

        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance
        mock_agent.return_value = MagicMock()
        mock_provider_instance = MagicMock()
        mock_provider.return_value = mock_provider_instance

        async with create_pitwall_agent("test-model"):
            # Verify OpenRouterProvider was called with the API key
            mock_provider.assert_called_with(api_key="test-key")
            # Verify OpenAIModel was called with the model and provider
            mock_model.assert_called_with("test-model", provider=mock_provider_instance)


class TestPitwallAgentMethods:
    """Test specific agent wrapper methods."""

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"})
    @patch("pitwall.pitwall.MCPServerStdio")
    @patch("pitwall.pitwall.OpenAIModel")
    @patch("pitwall.pitwall.Agent")
    async def test_connected_agent_cleanup(self, mock_agent, mock_model, mock_mcp):
        """Test that connected agent cleanup doesn't raise errors."""
        mock_mcp_instance = AsyncMock()
        mock_mcp.return_value.__aenter__ = AsyncMock(return_value=mock_mcp_instance)
        mock_mcp.return_value.__aexit__ = AsyncMock(return_value=None)

        mock_model.return_value = MagicMock()
        mock_agent.return_value = MagicMock()

        async with create_pitwall_agent("test-model") as agent:
            # This should not raise any exceptions
            await agent.cleanup()

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"})
    @patch("pitwall.pitwall.MCPServerStdio")
    @patch("pitwall.pitwall.OpenAIModel")
    @patch("pitwall.pitwall.Agent")
    async def test_basic_agent_cleanup(self, mock_agent, mock_model, mock_mcp):
        """Test that basic agent (fallback) cleanup doesn't raise errors."""
        # Force fallback mode by making MCP fail
        mock_mcp.return_value.__aenter__ = AsyncMock(
            side_effect=Exception("MCP failed")
        )

        mock_model.return_value = MagicMock()
        mock_agent.return_value = MagicMock()

        async with create_pitwall_agent("test-model") as agent:
            # This should not raise any exceptions
            await agent.cleanup()


class TestSystemPrompts:
    """Test system prompts are set correctly."""

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"})
    @patch("pitwall.pitwall.MCPServerStdio")
    @patch("pitwall.pitwall.OpenAIModel")
    @patch("pitwall.pitwall.Agent")
    async def test_connected_agent_system_prompt(
        self, mock_agent, mock_model, mock_mcp
    ):
        """Test that connected agent has the correct system prompt."""
        mock_mcp_instance = AsyncMock()
        mock_mcp.return_value.__aenter__ = AsyncMock(return_value=mock_mcp_instance)
        mock_mcp.return_value.__aexit__ = AsyncMock(return_value=None)

        mock_model.return_value = MagicMock()
        mock_agent.return_value = MagicMock()

        async with create_pitwall_agent("test-model"):
            # Verify Agent was called with the correct system prompt
            mock_agent.assert_called_once()
            call_args = mock_agent.call_args[1]
            system_prompt = call_args["system_prompt"]
            assert "Pitwall" in system_prompt
            assert "agentic AI companion to MultiViewer" in system_prompt
            assert "MultiViewer" in system_prompt

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"})
    @patch("pitwall.pitwall.MCPServerStdio")
    @patch("pitwall.pitwall.OpenAIModel")
    @patch("pitwall.pitwall.Agent")
    async def test_fallback_agent_system_prompt(self, mock_agent, mock_model, mock_mcp):
        """Test that fallback agent has the correct system prompt."""
        # Force fallback mode
        mock_mcp.return_value.__aenter__ = AsyncMock(
            side_effect=Exception("MCP failed")
        )

        mock_model.return_value = MagicMock()
        mock_agent.return_value = MagicMock()

        async with create_pitwall_agent("test-model"):
            # Agent should be called once for fallback
            # (connected attempt fails before creating agent)
            assert mock_agent.call_count == 1

            # Check fallback system prompt
            fallback_call = mock_agent.call_args_list[0]
            system_prompt = fallback_call[1]["system_prompt"]
            assert "Pitwall" in system_prompt
            assert "agentic AI companion to MultiViewer" in system_prompt
