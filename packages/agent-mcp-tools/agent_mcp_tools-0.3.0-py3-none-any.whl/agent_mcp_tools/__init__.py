"""Agent MCP Tools - LLM agent framework using Model Context Protocol for multi-agent systems.

This package provides tools for integrating LLMs from various providers (currently OpenRouter)
with MCP (Model Context Protocol) servers, allowing recursive tool usage in LLM conversations.
"""

__version__ = "0.2.0"

# Import main components for easier access
from .llm_tool import query_llm

__all__ = ["query_llm"]
