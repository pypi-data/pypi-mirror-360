"""Command-line interface for Agent MCP Tools.

This module provides a CLI for interacting with LLMs through OpenRouter API
and MCP tools.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from enum import Enum
import json

import typer
from rich.console import Console
from rich.markdown import Markdown

from .llm_tool import query_llm
from .config import DEFAULT_MODEL, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE, cli_config
from .server import mcp, query as query_func

# Configure logging
logger = logging.getLogger(__name__)

app = typer.Typer()
console = Console()


class ThemeEnum(str, Enum):
    """Enum for available syntax highlighting themes."""
    default = "default"
    monokai = "monokai"
    solarized_light = "solarized-light"
    solarized_dark = "solarized-dark"
    github_dark = "github-dark"
    lightbulb = "lightbulb"


def verify_api_key() -> None:
    """Verify that the OpenRouter API key is set.
    
    Raises:
        SystemExit: If the API key is not set
    """
    if not os.environ.get("OPENROUTER_API_KEY"):
        typer.echo("Error: OPENROUTER_API_KEY environment variable not set")
        typer.echo("Please run: export OPENROUTER_API_KEY=your_key_here")
        sys.exit(1)


@app.command()
def query(
    prompt: str = typer.Argument(..., help="The prompt to send to the LLM"),
    system_prompt: Path = typer.Option(
        None,
        "--system-prompt", "-s",
        help="Path to file containing the system prompt template",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    mcp_config: Path = typer.Option(
        None,
        "--mcp-config", "-m",
        help="Path to MCP configuration JSON file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    model: str = typer.Option(
        DEFAULT_MODEL,
        "--model",
        help="Model to use for generation",
    ),
    max_tokens: int = typer.Option(
        DEFAULT_MAX_TOKENS,
        "--max-tokens",
        help="Maximum number of tokens to generate",
    ),
    temperature: float = typer.Option(
        DEFAULT_TEMPERATURE,
        "--temperature",
        help="Temperature for sampling (0.0 to 1.0)",
        min=0.0,
        max=2.0,
    ),
    theme: ThemeEnum = typer.Option(
        ThemeEnum.monokai,
        "--theme",
        "-t",
        help="Theme for syntax highlighting.",
        case_sensitive=False,
    ),
) -> None:
    """Query an LLM with optional MCP tools and custom system prompt.
    
    Args:
        prompt: The prompt text to send to the LLM
        system_prompt: Path to system prompt template file
        mcp_config: Path to MCP configuration JSON file
        model: Model to use
        max_tokens: Maximum tokens to generate
        temperature: Temperature for sampling
        theme: Theme for syntax highlighting
    """
    verify_api_key()
    
    # Show configuration
    typer.echo(f"Model: {model}")
    if system_prompt:
        typer.echo(f"System prompt: {system_prompt}")
    if mcp_config:
        typer.echo(f"MCP config: {mcp_config}")
    typer.echo(f"Max tokens: {max_tokens}")
    typer.echo(f"Temperature: {temperature}")
    typer.echo(f"Theme: {theme.value}")
    typer.echo("\nQuerying...\n")

    try:
        result = asyncio.run(query_llm(
            prompt=prompt,
            system_prompt_file=system_prompt,
            mcp_config_file=mcp_config,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        ))

        console.print("\nResponse:")
        console.print("=" * 50)
        try:
            data = json.loads(result)
            if 'result' in data and isinstance(data['result'], str):
                console.print(Markdown(data['result'], code_theme=theme.value))
            else:
                console.print_json(data=data)
        except (json.JSONDecodeError, TypeError):
            console.print(Markdown(result, code_theme=theme.value))
        console.print("=" * 50)
    except KeyboardInterrupt:
        typer.echo("\nOperation cancelled by user.")
    except Exception as e:
        typer.echo(f"\nError: {e}")
        if logger.isEnabledFor(logging.DEBUG):
            import traceback
            traceback.print_exc()


@app.command()
def stdio(
    system_prompt: Path = typer.Option(
        None,
        "--system-prompt",
        "-s",
        help="Path to file containing the system prompt template",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    mcp_config: Path = typer.Option(
        None,
        "--mcp-config",
        "-m",
        help="Path to MCP configuration JSON file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    model: str = typer.Option(
        DEFAULT_MODEL,
        "--model",
        help="Model to use for generation",
    ),
    max_tokens: int = typer.Option(
        DEFAULT_MAX_TOKENS,
        "--max-tokens",
        help="Maximum number of tokens to generate",
    ),
    temperature: float = typer.Option(
        DEFAULT_TEMPERATURE,
        "--temperature",
        help="Temperature for sampling (0.0 to 1.0)",
        min=0.0,
        max=2.0,
    ),
    tool_name: str = typer.Option(
        "query",
        "--tool-name",
        help="Name for the query tool",
    ),
    tool_description: str = typer.Option(
        "Query an LLM with a prompt and optional settings.",
        "--tool-description",
        help="Description for the query tool",
    ),
):
    """Run the Agent MCP Tools server with stdio transport."""
    cli_config.system_prompt_file = system_prompt
    cli_config.mcp_config_file = mcp_config
    cli_config.model = model
    cli_config.max_tokens = max_tokens
    cli_config.temperature = temperature
    cli_config.tool_name = tool_name
    cli_config.tool_description = tool_description

    # Register the tool with the specified name and description
    mcp.tool(name=cli_config.tool_name, description=cli_config.tool_description)(
        query_func
    )

    typer.echo("Starting Agent MCP Tools server with stdio transport...")
    mcp.run(transport="stdio")


@app.command()
def http(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind the server to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind the server to"),
    system_prompt: Path = typer.Option(
        None,
        "--system-prompt",
        "-s",
        help="Path to file containing the system prompt template",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    mcp_config: Path = typer.Option(
        None,
        "--mcp-config",
        "-m",
        help="Path to MCP configuration JSON file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    model: str = typer.Option(
        DEFAULT_MODEL,
        "--model",
        help="Model to use for generation",
    ),
    max_tokens: int = typer.Option(
        DEFAULT_MAX_TOKENS,
        "--max-tokens",
        help="Maximum number of tokens to generate",
    ),
    temperature: float = typer.Option(
        DEFAULT_TEMPERATURE,
        "--temperature",
        help="Temperature for sampling (0.0 to 1.0)",
        min=0.0,
        max=2.0,
    ),
    tool_name: str = typer.Option(
        "query",
        "--tool-name",
        help="Name for the query tool",
    ),
    tool_description: str = typer.Option(
        "Query an LLM with a prompt and optional settings.",
        "--tool-description",
        help="Description for the query tool",
    ),
):
    """Run the Agent MCP Tools server with HTTP transport."""
    cli_config.system_prompt_file = system_prompt
    cli_config.mcp_config_file = mcp_config
    cli_config.model = model
    cli_config.max_tokens = max_tokens
    cli_config.temperature = temperature
    cli_config.tool_name = tool_name
    cli_config.tool_description = tool_description

    # Register the tool with the specified name and description
    mcp.tool(name=cli_config.tool_name, description=cli_config.tool_description)(
        query_func
    )

    typer.echo(f"Starting Agent MCP Tools server with HTTP transport on {host}:{port}...")
    mcp.run(transport="http", host=host, port=port)


@app.command()
def examples() -> None:
    """Show example usage and configurations."""
    examples_text = """
# Agent MCP Tools Examples

### 1. Basic query (no MCP tools)
```bash
agent-mcp-tools query 'What is the capital of France?'
```

### 2. Query with system prompt
```bash
agent-mcp-tools query 'Write a Python function' --system-prompt examples/coder.md
```

### 3. Query with MCP tools
```bash
agent-mcp-tools query 'List files in /tmp' --mcp-config examples/mcp.json
```

### 4. Full configuration
```bash
agent-mcp-tools query 'Analyze this code' \\
    --system-prompt examples/coder.md \\
    --mcp-config examples/mcp.json \\
    --model google/gemini-2.5-pro-preview \\
    --max-tokens 4096 \\
    --temperature 0.0
```

### 5. Using environment variables
```bash
export OPENROUTER_API_KEY=your_key_here
agent-mcp-tools query 'Hello, world!'
```

### 6. Run as an MCP server (stdio)
```bash
agent-mcp-tools stdio
```

### 7. Run as an MCP server (http)
```bash
agent-mcp-tools http --host 0.0.0.0 --port 8080
```

Example files are available in the 'examples' directory.
"""
    console.print(Markdown(examples_text))


def main() -> None:
    """Entry point for the CLI application."""
    # Set up logging
    log_level = logging.DEBUG if os.environ.get("AGENT_MCP_TOOLS_DEBUG") else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    app()


if __name__ == "__main__":
    main()

