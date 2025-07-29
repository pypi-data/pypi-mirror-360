"""Configuration management for Agent MCP Tools.

This module handles loading MCP server configurations.
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Constants
DEFAULT_MODEL = "google/gemini-2.5-flash"
DEFAULT_MAX_TOKENS = 16384
DEFAULT_TEMPERATURE = 0.0


@dataclass
class CliConfig:
    """Holds CLI options."""
    system_prompt_file: Optional[Path] = None
    mcp_config_file: Optional[Path] = None
    model: str = DEFAULT_MODEL
    max_tokens: int = DEFAULT_MAX_TOKENS
    temperature: float = DEFAULT_TEMPERATURE
    tool_name: Optional[str] = None
    tool_description: Optional[str] = None

# Global instance of the config
cli_config = CliConfig()


@dataclass
class ServerConfig:
    """Configuration for an MCP server."""
    name: str
    command: Optional[str] = None
    args: List[str] = None
    env: Dict[str, str] = None
    url: Optional[str] = None

    def __post_init__(self):
        if self.args is None:
            self.args = []
        if self.env is None:
            self.env = {}

    @property
    def is_sse(self) -> bool:
        """Check if this is an SSE server configuration."""
        return self.url is not None

    @property
    def is_stdio(self) -> bool:
        """Check if this is a stdio server configuration."""
        return self.command is not None


class ConfigurationError(Exception):
    """Raised when there's an error in configuration."""
    pass


def load_mcp_config(config_path: Path) -> Dict[str, ServerConfig]:
    """Load MCP server configurations from JSON file.
    
    Args:
        config_path: Path to the MCP configuration JSON file
        
    Returns:
        Dictionary mapping server names to ServerConfig objects
        
    Raises:
        ConfigurationError: If the configuration file is invalid
    """
    try:
        with open(config_path, encoding="utf-8") as f:
            logger.info(f"Loading MCP configuration from {config_path}")
            data = json.load(f)
            
        servers = {}
        for name, config in data.get("mcpServers", {}).items():
            servers[name] = ServerConfig(
                name=name,
                command=config.get("command"),
                args=config.get("args", []),
                env=config.get("env", {}),
                url=config.get("url")
            )
        return servers
        
    except FileNotFoundError:
        raise ConfigurationError(f"MCP configuration file not found: {config_path}")
    except json.JSONDecodeError as e:
        raise ConfigurationError(f"Invalid JSON in MCP configuration file: {e}")
    except Exception as e:
        raise ConfigurationError(f"Error loading MCP configuration: {e}") 