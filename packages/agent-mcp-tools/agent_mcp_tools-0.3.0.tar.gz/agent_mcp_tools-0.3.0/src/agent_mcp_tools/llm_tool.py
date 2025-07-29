"""LLM tool integration for Agent MCP Tools.

This module provides integration between LLM providers and MCP (Model Context Protocol),
allowing LLMs to use external tools via MCP servers. Currently supports OpenRouter API
but designed to be extensible to other providers.
"""

import json
import logging
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from .config import DEFAULT_MODEL, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE, load_mcp_config
from .mcp_client import MCPClientManager, ToolConverter

logger = logging.getLogger(__name__)

# Constants
API_REQUEST_TIMEOUT = 120.0

# In-memory store for conversations
_conversations: Dict[str, List[Dict[str, Any]]] = {}


class LLMProviderError(Exception):
    """Raised when there's an error with the LLM provider."""
    pass


class LLMClient:
    """Base class for LLM provider clients."""
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, Any]], 
        model: str,
        max_tokens: int,
        temperature: float,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Send a chat completion request to the LLM provider."""
        raise NotImplementedError("Subclasses must implement chat_completion")


class OpenRouterClient(LLMClient):
    """Handles communication with OpenRouter API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://localhost",
                            "X-Title": "Agent MCP Tools",
            "Content-Type": "application/json",
        }

    async def chat_completion(
        self, 
        messages: List[Dict[str, Any]], 
        model: str,
        max_tokens: int,
        temperature: float,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Send a chat completion request to OpenRouter."""
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=API_REQUEST_TIMEOUT,
            )

            if response.status_code != 200:
                raise LLMProviderError(f"OpenRouter API error: {response.status_code} - {response.text}")

            return response.json()


class AgentExecutor:
    """Executes agent requests with tool calling support."""

    def __init__(self, llm_client: LLMClient, mcp_manager: MCPClientManager):
        self.llm_client = llm_client
        self.mcp_manager = mcp_manager

    async def execute(
        self,
        prompt: str,
        system_prompt_template: str,
        conversation_id: str,
        close: bool = False,
        model: str = DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> str:
        """Execute an agent request."""
        messages = _conversations.get(conversation_id)

        if not messages:
            # New conversation
            formatted_prompt = system_prompt_template.format(prompt=prompt)
            messages = [{"role": "user", "content": formatted_prompt}]
            _conversations[conversation_id] = messages
        else:
            # Existing conversation
            messages.append({"role": "user", "content": prompt})

        # Get available tools
        mcp_tools = await self.mcp_manager.get_all_tools()
        openai_tools = ToolConverter.mcp_to_openai(mcp_tools) if mcp_tools else None

        while True:
            response_data = await self.llm_client.chat_completion(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                tools=openai_tools
            )

            if not response_data.get("choices"):
                return "No response content found"

            message = response_data["choices"][0]["message"]
            messages.append(message)

            # Handle tool calls
            if "tool_calls" in message and openai_tools:
                if await self._process_tool_calls(message["tool_calls"], messages):
                    continue  # Continue conversation loop

            # No tool calls or all processed, return final content
            final_content = message.get("content", "No content returned")

            if close:
                if conversation_id in _conversations:
                    del _conversations[conversation_id]
            
            return final_content

    async def _process_tool_calls(
        self, 
        tool_calls: List[Dict[str, Any]], 
        messages: List[Dict[str, Any]]
    ) -> bool:
        """Process tool calls and add results to messages."""
        has_tool_calls = False

        for tool_call in tool_calls:
            if tool_call["type"] != "function":
                continue

            has_tool_calls = True
            function_call = tool_call["function"]
            tool_name = function_call["name"]
            
            try:
                tool_args = json.loads(function_call["arguments"])
            except json.JSONDecodeError:
                tool_args = {}

            try:
                result = await self.mcp_manager.call_tool(tool_name, tool_args)
                content = result
            except Exception as e:
                content = f"Error calling MCP tool {tool_name}: {e}"
                logger.error(content)

            tool_result = {
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "name": tool_name,
                "content": content,
            }
            messages.append(tool_result)

        return has_tool_calls


class LLMClientFactory:
    """Factory for creating LLM clients based on configuration or environment."""
    
    @staticmethod
    def create_client() -> LLMClient:
        """Create an appropriate LLM client based on available configuration."""
        # For now, we only support OpenRouter, but this can be extended
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if api_key:
            return OpenRouterClient(api_key)
        
        # Future: Add support for other providers
        # if os.environ.get("ANTHROPIC_API_KEY"):
        #     return AnthropicClient(os.environ["ANTHROPIC_API_KEY"])
        # if os.environ.get("OPENAI_API_KEY"):
        #     return OpenAIClient(os.environ["OPENAI_API_KEY"])
        
        raise LLMProviderError(
            "No supported LLM provider API key found. "
            "Please set OPENROUTER_API_KEY environment variable."
        )


async def query_llm(
    prompt: str,
    system_prompt_file: Optional[Path] = None,
    mcp_config_file: Optional[Path] = None,
    conversation_id: Optional[str] = None,
    close_conversation: bool = False,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE
) -> str:
    """Query an LLM with optional MCP tools.
    
    Args:
        prompt: The user's prompt
        system_prompt_file: Path to file containing system prompt template
        mcp_config_file: Path to MCP configuration JSON file
        conversation_id: ID for multi-turn conversation. If None, a new one-off conversation is created.
        close_conversation: If True, closes the conversation and clears its history.
        model: Model to use
        max_tokens: Maximum tokens to generate
        temperature: Temperature for sampling
        
    Returns:
        The LLM's response
    """
    # Load system prompt template
    if system_prompt_file and system_prompt_file.exists():
        system_prompt_template = system_prompt_file.read_text(encoding="utf-8")
    else:
        system_prompt_template = "{prompt}"
    
    mcp_manager = MCPClientManager()
    
    close_after_exec = close_conversation
    if conversation_id is None:
        conversation_id = str(uuid.uuid4())
        close_after_exec = True

    try:
        # Connect to MCP servers if config provided
        if mcp_config_file and mcp_config_file.exists():
            mcp_servers = load_mcp_config(mcp_config_file)
            await mcp_manager.connect_to_servers(mcp_servers)
        
        # Create LLM client and execute
        llm_client = LLMClientFactory.create_client()
        executor = AgentExecutor(llm_client, mcp_manager)
        
        return await executor.execute(
            prompt=prompt,
            system_prompt_template=system_prompt_template,
            conversation_id=conversation_id,
            close=close_after_exec,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
    finally:
        await mcp_manager.cleanup()


# Export main functionality
__all__ = ["query_llm"]


if __name__ == "__main__":
    # Configure logging for standalone mode
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    # Run the server directly if this file is executed
    logger.info("Starting Agent MCP Tools server with streamable-http transport")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000) 