"""
MCP Application Registry

This module defines the supported MCP applications and their configuration file paths.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class MCPApp:
    """Represents an MCP-compatible application."""

    name: str
    display_name: str
    config_path: str
    description: str
    homepage: Optional[str] = None


# Registry of supported MCP applications
MCP_APPS: Dict[str, MCPApp] = {
    "amazonq": MCPApp(
        name="amazonq",
        display_name="Amazon Q",
        config_path="~/.aws/amazonq/mcp.json",
        description="Amazon Q AI assistant configuration",
        homepage="https://aws.amazon.com/q/",
    ),
    "cline": MCPApp(
        name="cline",
        display_name="Cline (VS Code)",
        config_path="~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json",
        description="Cline VS Code extension MCP settings",
        homepage="https://github.com/saoudrizwan/claude-dev",
    ),
    "claude-desktop": MCPApp(
        name="claude-desktop",
        display_name="Claude Desktop",
        config_path="~/Library/Application Support/Claude/claude_desktop_config.json",
        description="Anthropic Claude Desktop application",
        homepage="https://claude.ai/",
    ),
}


def get_app(app_name: str) -> Optional[MCPApp]:
    """
    Get an MCP app by name.

    Args:
        app_name: Name of the app to retrieve

    Returns:
        MCPApp instance if found, None otherwise
    """
    return MCP_APPS.get(app_name.lower())


def get_all_apps() -> Dict[str, MCPApp]:
    """
    Get all registered MCP apps.

    Returns:
        Dictionary of all MCP apps
    """
    return MCP_APPS.copy()


def get_app_names() -> List[str]:
    """
    Get list of all registered app names.

    Returns:
        List of app names
    """
    return list(MCP_APPS.keys())


def get_config_paths_for_apps(app_names: List[str]) -> List[str]:
    """
    Get configuration file paths for specified apps.

    Args:
        app_names: List of app names

    Returns:
        List of configuration file paths

    Raises:
        ValueError: If any app name is not found
    """
    paths = []
    for app_name in app_names:
        app = get_app(app_name)
        if app is None:
            raise ValueError(f"Unknown app: {app_name}")
        paths.append(app.config_path)
    return paths


def get_existing_apps() -> List[MCPApp]:
    """
    Get list of apps that have existing configuration files.

    Returns:
        List of MCPApp instances with existing config files
    """
    existing = []
    for app in MCP_APPS.values():
        config_path = Path(app.config_path).expanduser()
        if config_path.exists():
            existing.append(app)
    return existing


def validate_app_names(app_names: List[str]) -> List[str]:
    """
    Validate a list of app names and return any invalid ones.

    Args:
        app_names: List of app names to validate

    Returns:
        List of invalid app names (empty if all valid)
    """
    invalid = []
    for app_name in app_names:
        if app_name.lower() not in MCP_APPS:
            invalid.append(app_name)
    return invalid
