"""
MCP Config Sync - Synchronize MCP server configurations across tools.

A Python package for synchronizing Model Context Protocol (MCP) server
configurations across different AI tools and applications.
"""

__version__ = "0.1.0"
__author__ = "Jon"
__email__ = "jon@zer0day.net"

from .apps import get_all_apps, get_app, get_app_names
from .sync import MCPServerSync

__all__ = ["MCPServerSync", "get_all_apps", "get_app_names", "get_app"]
