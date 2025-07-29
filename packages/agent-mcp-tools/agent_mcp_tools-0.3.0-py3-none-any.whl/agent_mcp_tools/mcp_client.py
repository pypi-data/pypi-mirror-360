"""MCP client management for Agent MCP Tools.

This module handles communication with MCP (Model Context Protocol) servers,
including connection management, tool discovery, and tool execution.
"""

import asyncio
import logging
import os
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional

from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.stdio import StdioServerParameters, stdio_client

from .config import ServerConfig

logger = logging.getLogger(__name__)

# Constants
DEFAULT_TIMEOUT = 10.0
TOOL_CALL_TIMEOUT = 600.0


class MCPConnectionError(Exception):
    """Raised when there's an error connecting to MCP server."""
    pass


class ToolConverter:
    """Converts between different tool formats."""

    @staticmethod
    def mcp_to_openai(mcp_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert MCP tool definitions to OpenAI-compatible format."""
        openai_tools = []
        
        for tool in mcp_tools:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.get("name", "unknown_tool"),
                    "description": tool.get("description", ""),
                    "parameters": {
                        "type": "object",
                        "properties": tool.get("inputSchema", {}).get("properties", {}),
                        "required": tool.get("inputSchema", {}).get("required", []),
                    },
                },
            }
            openai_tools.append(openai_tool)
        
        return openai_tools


class MCPClient:
    """Manages connection to a single MCP server."""

    def __init__(self, config: ServerConfig):
        self.config = config
        self.session: Optional[ClientSession] = None
        self.exit_stack: Optional[AsyncExitStack] = None
        self._tools_cache: Optional[List[Dict[str, Any]]] = None

    async def connect(self) -> bool:
        """Connect to the MCP server."""
        if self.session is not None:
            return True

        try:
            self.exit_stack = AsyncExitStack()
            
            if self.config.is_sse:
                await self._connect_sse()
            elif self.config.is_stdio:
                await self._connect_stdio()
            else:
                raise MCPConnectionError(f"Invalid server configuration for {self.config.name}")
            
            await asyncio.wait_for(self.session.initialize(), DEFAULT_TIMEOUT)
            logger.info(f"Connected to MCP server: {self.config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {self.config.name}: {e}")
            await self._cleanup()
            return False

    async def _connect_sse(self) -> None:
        """Connect using SSE transport."""
        sse_transport = await self.exit_stack.enter_async_context(
            sse_client(self.config.url)
        )
        read_stream, write_stream = sse_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )

    async def _connect_stdio(self) -> None:
        """Connect using stdio transport."""
        env_vars = os.environ.copy()
        env_vars.update(self.config.env)
        
        server_params = StdioServerParameters(
            command=self.config.command,
            args=self.config.args,
            env=env_vars,
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read_stream, write_stream = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )

    async def get_tools(self) -> List[Dict[str, Any]]:
        """Get tools from the server with caching."""
        if self._tools_cache is not None:
            return self._tools_cache

        if self.session is None:
            return []

        try:
            response = await asyncio.wait_for(self.session.list_tools(), DEFAULT_TIMEOUT)
            tools = self._process_tools_response(response)
            self._tools_cache = tools
            return tools
            
        except Exception as e:
            logger.error(f"Error fetching tools from {self.config.name}: {e}")
            return []

    def _process_tools_response(self, response) -> List[Dict[str, Any]]:
        """Process the tools response from MCP server."""
        tools = []
        
        if not response or not hasattr(response, 'tools'):
            return tools

        for tool in response.tools:
            tool_dict = {
                "name": tool.name,
                "description": tool.description or "",
                "inputSchema": self._extract_input_schema(tool),
            }
            tools.append(tool_dict)
        
        return tools

    def _extract_input_schema(self, tool) -> Dict[str, Any]:
        """Extract input schema from tool definition."""
        if not hasattr(tool, 'inputSchema'):
            return {}

        if isinstance(tool.inputSchema, dict):
            return tool.inputSchema

        # Convert from object to dict
        properties = getattr(tool.inputSchema, 'properties', {})
        required = getattr(tool.inputSchema, 'required', [])
        
        return {
            "properties": properties,
            "required": required,
        }

    async def call_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Call a tool on this server."""
        if self.session is None:
            raise MCPConnectionError(f"No connection to server {self.config.name}")

        try:
            result = await asyncio.wait_for(
                self.session.call_tool(tool_name, arguments=args), 
                TOOL_CALL_TIMEOUT
            )
            return self._extract_content(result)
            
        except Exception as e:
            logger.error(f"Error calling tool {tool_name} on {self.config.name}: {e}")
            raise

    def _extract_content(self, result) -> str:
        """Extract content from tool call result."""
        if not result:
            return "No content returned"

        if not hasattr(result, 'content'):
            return str(result)

        content = result.content

        if isinstance(content, list):
            content_items = []
            for item in content:
                if hasattr(item, 'text'):
                    content_items.append(item.text)
                elif hasattr(item, 'value'):
                    content_items.append(str(item.value))
                else:
                    content_items.append(str(item))
            return '\n'.join(content_items)

        if hasattr(content, 'text'):
            return content.text

        if hasattr(content, 'value'):
            return str(content.value)

        return str(content)

    async def disconnect(self) -> None:
        """Disconnect from the server."""
        await self._cleanup()

    async def _cleanup(self) -> None:
        """Clean up resources."""
        if self.exit_stack:
            try:
                await self.exit_stack.aclose()
            except Exception as e:
                logger.error(f"Error cleaning up {self.config.name}: {e}")
            finally:
                self.exit_stack = None
                self.session = None
                self._tools_cache = None


class MCPClientManager:
    """Manages multiple MCP client connections."""

    def __init__(self):
        self.clients: Dict[str, MCPClient] = {}

    async def connect_to_servers(self, server_configs: Dict[str, ServerConfig]) -> None:
        """Connect to multiple MCP servers."""
        for name, config in server_configs.items():
            client = MCPClient(config)
            if await client.connect():
                self.clients[name] = client

    async def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get tools from all connected servers."""
        all_tools = []
        
        for server_name, client in self.clients.items():
            tools = await client.get_tools()
            all_tools.extend(tools)
        
        return all_tools

    async def call_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Call a tool on the appropriate server."""
        for server_name, client in self.clients.items():
            tools = await client.get_tools()
            
            if any(tool.get("name") == tool_name for tool in tools):
                return await client.call_tool(tool_name, args)
        
        raise MCPConnectionError(f"Tool '{tool_name}' not found on any connected server")

    async def cleanup(self) -> None:
        """Disconnect from all servers."""
        for client in self.clients.values():
            await client.disconnect()
        self.clients.clear() 