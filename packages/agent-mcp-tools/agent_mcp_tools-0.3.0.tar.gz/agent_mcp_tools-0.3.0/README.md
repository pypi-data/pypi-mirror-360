# Agent MCP Tools

[![PyPI version](https://badge.fury.io/py/agent-mcp-tools.svg)](https://badge.fury.io/py/agent-mcp-tools)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Agent MCP Tools** is both a Model Context Protocol (MCP) server and client, allowing building multi-agent system by tool use.

## Quick Start

### 1. Installation

```bash
pipx install agent-mcp-tools
```

### 2. Configuration

Set your OpenRouter API key. Get one from the [OpenRouter website](https://openrouter.ai/keys).

```bash
export OPENROUTER_API_KEY="your_openrouter_api_key"
```

### 3. Command-Line Usage

**Basic Query:**
```bash
agent-mcp-tools query "What is the capital of France?"
```

**Query with Tools:**
Provide an MCP config file to give the LLM access to tools.
```bash
# Create a tool config file (e.g., mcp.json)
agent-mcp-tools query "List files in the /tmp directory" --mcp-config mcp.json
```

**Run as an MCP Server:**
Expose `agent-mcp-tools` itself as a MCP tool for other agents.
```bash
agent-mcp-tools http --tool-name "web_search" --tool-description "Search the web and returns the summarized contents."
```

## MCP Configuration

To use tools, create an `mcp.json` file that defines your MCP servers. Agent MCP Tools is compatible with the [MCP specification](https://mcp.ai) used by Cursor and other tools.

**Example `mcp.json`:**
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp/"],
      "env": {}
    },
    "http-transport-mcp": {
      "url": "http://localhost:3000/mcp"
    }
  }
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
