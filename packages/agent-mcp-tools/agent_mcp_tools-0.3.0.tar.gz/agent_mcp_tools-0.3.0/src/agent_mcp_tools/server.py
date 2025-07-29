from pathlib import Path
from typing import Optional

from fastmcp import FastMCP
from .llm_tool import query_llm
from .config import cli_config

mcp = FastMCP(name="Agent MCP Tools Server")

async def query(
    prompt: str,
    conversation_id: Optional[str] = None,
    close_conversation: bool = False,
) -> str:
    """
    Query an LLM with a prompt and optional settings.

    Args:
        prompt: The user's prompt to the LLM.
        conversation_id: ID of an ongoing conversation.
        close_conversation: If true, closes the conversation.
    """
    return await query_llm(
        prompt=prompt,
        system_prompt_file=cli_config.system_prompt_file,
        mcp_config_file=cli_config.mcp_config_file,
        conversation_id=conversation_id,
        close_conversation=close_conversation,
        model=cli_config.model,
        max_tokens=cli_config.max_tokens,
        temperature=cli_config.temperature,
    ) 