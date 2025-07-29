import os
from contextlib import asynccontextmanager
from typing import Optional

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

from .prompts import pitwall_agent_prompt
from .memory import ConversationMemory


@asynccontextmanager
async def create_pitwall_agent(
    model: str = "anthropic/claude-3.7-sonnet",
    session_id: Optional[str] = None,
    memory: Optional[ConversationMemory] = None,
    multiviewer_url: str = "http://localhost:10101/graphql",
):
    """Create and manage a Pitwall agent instance with MCP server."""
    print(f"🏁 Starting local MVF1 MCP server (connecting to {multiviewer_url})...")

    try:
        # Use MCP server as context manager with MultiViewer URL
        mcp_args = ["mcp", "--url", multiviewer_url]
        async with MCPServerStdio("mvf1-cli", args=mcp_args, timeout=30) as mcp_server:
            print("✅ Local MVF1 MCP server started successfully!")

            # Create model
            api_key = os.environ.get("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY environment variable is required")

            model_instance = OpenAIModel(
                model,
                provider=OpenRouterProvider(api_key=api_key),
            )

            # Create agent with connected MCP server
            agent_instance = Agent(
                model_instance,
                mcp_servers=[mcp_server],
                system_prompt=pitwall_agent_prompt,
            )

            # Initialize memory if needed
            if memory is None:
                memory = ConversationMemory()

            # Load or create session
            if session_id:
                if not memory.load_session(session_id):
                    memory.create_session(model)
            elif not memory.has_active_session():
                memory.create_session(model)

            # Create a wrapper to make it compatible with PitwallAgent interface
            class ConnectedPitwallAgent:
                def __init__(self, agent, mcp_server, memory):
                    self._agent = agent
                    self._mcp_server = mcp_server
                    self._memory = memory
                    self.model_name = model

                async def execute_task(
                    self, query: str, max_turns: int = 3, user_input: bool = False
                ) -> str:
                    # Get message history for context
                    message_history = self._memory.get_message_history()

                    result = await self._agent.run(
                        query, message_history=message_history
                    )

                    # Update memory with the run result
                    self._memory.update_from_run_result(result)

                    return str(result.data)

                async def chat_turn(self, message: str) -> str:
                    # Get message history for context
                    message_history = self._memory.get_message_history()

                    result = await self._agent.run(
                        message, message_history=message_history
                    )

                    # Update memory with the run result
                    self._memory.update_from_run_result(result)

                    return str(result.data)

                async def get_available_tools(self) -> list:
                    tools = await self._mcp_server.list_tools()
                    return [
                        {"name": tool.name, "description": tool.description}
                        for tool in tools
                    ]

                def get_memory(self) -> ConversationMemory:
                    return self._memory

                async def cleanup(self):
                    pass  # Context manager handles cleanup

            yield ConnectedPitwallAgent(agent_instance, mcp_server, memory)

    except Exception as e:
        print(f"⚠️  Could not start local MCP server: {e}")
        print("🔄 Falling back to basic agent...")

        # Initialize memory if needed
        if memory is None:
            memory = ConversationMemory()

        # Load or create session
        if session_id:
            if not memory.load_session(session_id):
                memory.create_session(model)
        elif not memory.has_active_session():
            memory.create_session(model)

        # Fallback to basic agent
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")

        model_instance = OpenAIModel(
            model,
            provider=OpenRouterProvider(api_key=api_key),
        )

        agent_instance = Agent(model_instance, system_prompt=pitwall_agent_prompt)

        class BasicPitwallAgent:
            def __init__(self, agent, memory):
                self._agent = agent
                self._memory = memory
                self.model_name = model

            async def execute_task(
                self, query: str, max_turns: int = 3, user_input: bool = False
            ) -> str:
                # Get message history for context
                message_history = self._memory.get_message_history()

                result = await self._agent.run(query, message_history=message_history)

                # Update memory with the run result
                self._memory.update_from_run_result(result)

                return str(result.data)

            async def chat_turn(self, message: str) -> str:
                # Get message history for context
                message_history = self._memory.get_message_history()

                result = await self._agent.run(message, message_history=message_history)

                # Update memory with the run result
                self._memory.update_from_run_result(result)

                return str(result.data)

            async def get_available_tools(self) -> list:
                return [
                    {
                        "name": "general-analysis",
                        "description": "General motorsport knowledge "
                        "(no live tools available)",
                    }
                ]

            def get_memory(self) -> ConversationMemory:
                return self._memory

            async def cleanup(self):
                pass

        yield BasicPitwallAgent(agent_instance, memory)


async def quick_analysis(
    query: str,
    model: str = "anthropic/claude-3.7-sonnet",
    multiviewer_url: str = "http://localhost:10101/graphql",
) -> str:
    """Perform a quick analysis without persistent context."""
    async with create_pitwall_agent(model, multiviewer_url=multiviewer_url) as agent:
        return await agent.execute_task(query, max_turns=1)


# Keep the original global agent for backwards compatibility
python_server = MCPServerStdio("mvf1-cli", args=["mcp"])

# Global agent - only create if API key is available
api_key = os.environ.get("OPENROUTER_API_KEY")
model: Optional[OpenAIModel] = None
agent: Optional[Agent] = None

if api_key:
    model = OpenAIModel(
        "anthropic/claude-3.7-sonnet",
        provider=OpenRouterProvider(api_key=api_key),
    )
    agent = Agent(model, mcp_servers=[python_server])
